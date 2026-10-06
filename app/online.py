"""Online sign-in + entitlement client, GitHub edition (v8.27).

Discord is the one and only sign-in method (product decision v8.23).

There is no backend server anywhere in this product:

  * **OAuth runs app-to-provider.** The browser does the authorization
    round trip and comes back to a loopback HTTP server on a fixed
    port (RFC 8252 native-app style); the app exchanges the code
    itself and keeps the provider tokens in session.json (DPAPI
    protected on Windows). PKCE (S256) is used wherever the provider
    supports it; the client secret ships in the exe, which is the
    standard, accepted reality for installed apps - it identifies the
    app, it is not a password.
  * **The subscription truth is a signed file in a PUBLIC GitHub
    repo.** A GitHub Action (private controller repo, cron every
    10 min, Stripe secret kept in repo secrets) rebuilds
    entitlements.json from Stripe events, Ed25519-signs it and
    force-pushes it. The app embeds only the PUBLIC key, fetches the
    file from raw.githubusercontent.com and verifies: unforgeable,
    token-free, CDN-fast, and GitHub is the only infrastructure.
  * Strict policy unchanged: no live, verified answer = no engine.

Everything degrades to OnlineError so the interfaces can show
"unreachable - retry" instead of a traceback.
"""

import base64
import concurrent.futures
import hashlib
import json
import os
import secrets
import sys
import threading
import time
import urllib.error
import urllib.parse
import re
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import build_secrets
import edsig
import i18n
from config import config_dir

# The few strings a user can see (sign-in cancel, licence statuses)
# live in the catalog like everything else (v8.40); everything logged
# stays English, it is support evidence.
i18n.publish("en", {
    "online.cancelled": "Discord authentication has been cancelled (or "
                        "failed). Please try again.",
    "ent.st.active": "active",
    "ent.st.trial": "trial",
    "ent.st.grant": "support grant",
    "ent.st.canceling": "active but cancelling",
    "ent.st.past_due": "PAYMENT FAILED",
    "ent.st.canceled": "ended",
    "ent.st.refunded": "refunded / charged back",
    "ent.st.unsubscribed": "no subscription",
    "ent.until": " until %s",
    "ent.plan": " (%s)",
    "ent.cancel_line": "active until %s - will NOT renew",
    "ent.past_due_line": "payment failed - fix the card in your Stripe "
                         "receipt e-mail; access returns when the "
                         "invoice pays",
    "ent.canceled_line": "subscription ended%s",
    "ent.refunded_line": "refunded / charged back - entitlement revoked",
    "ent.expired_line": "expired on %s - renew on Stripe",
})
from core import APP_VERSION, IS_WINDOWS, log

# ----------------------------------------------------------------------
# Deployment constants (v8.49)
#
# EVERYTHING below now comes from build_secrets.py. None of it is a
# setting, and none of it is in DEFAULT_CONFIG, so none of it can reach
# config.json or an Export Config file:
#
#   * the entitlement repo/branch - repointing it gains an attacker
#     nothing, because the Ed25519 PUBLIC key is pinned here too and a
#     file from any other repo simply fails verification;
#   * the Ed25519 public key - the trust anchor. Deliberately a build
#     constant and never a config key: when it was configurable, the
#     paywall could be bypassed with a self-signed file in your own
#     public repo (see entitlement_pubkey() below);
#   * both Stripe payment links;
#   * the Discord OAuth client id/secret;
#   * the presence webhook.
#
# A dev run (unfrozen) may override any of them through the environment
# - see build_secrets._ENV. A frozen build cannot: the override path is
# gated on `sys.frozen`, so a shipped exe cannot be repointed by setting
# a variable.
# ----------------------------------------------------------------------

ENTITLEMENT_PATH = "entitlements.json"

# A signed file older than this means the publisher pipeline is broken;
# treat it like an unreachable server (strict), not as "no subscription".
FRESHNESS_SECONDS = 6 * 3600

# Per-request dev override for the entitlement repo (--repo). Unfrozen
# only, and still gated by the pinned public key, so it cannot be used to
# substitute an entitlement file.
_DEV_REPO = ""


def set_dev_repo(value):
    """Point a DEV run at another entitlement repo (main.py --repo).

    Refused in a frozen build: a shipped exe must read the repo it was
    built with. Even when accepted it is not a security boundary - the
    file still has to verify against the pinned public key."""
    global _DEV_REPO
    if getattr(sys, "frozen", False):
        log("--repo ignored: this is a shipped build.")
        return False
    _DEV_REPO = str(value or "").strip().strip("/")
    return True


# Legacy names, kept as module attributes so existing references and any
# downstream tooling keep working. They are properties, not constants: the
# value is read from build_secrets on every access.
def _bs(name):
    return getattr(build_secrets, name)()


class _Lazy(object):
    """module attribute backed by a build_secrets accessor"""
    def __init__(self, fn):
        self._fn = fn

    def __str__(self):
        return self._fn()

    def __repr__(self):
        return self._fn()

    def __eq__(self, other):
        return self._fn() == other

    def __hash__(self):
        return hash(self._fn())

    def __add__(self, other):
        return self._fn() + other

    def __radd__(self, other):
        return other + self._fn()


DEFAULT_ENTITLEMENT_BRANCH = _Lazy(build_secrets.entitlement_branch)
DEFAULT_PAYMENT_LINK = _Lazy(build_secrets.stripe_monthly_link)
DEFAULT_TRIAL_LINK = _Lazy(build_secrets.stripe_trial_link)

LOOPBACK_HOST = "127.0.0.1"
LOOPBACK_PORT = 48321
LOOPBACK_PATH = "/oauth"

# Presence webhook (account-sharing detector): build_secrets, so it is not
# in config.json and not greppable in the source. See presence_webhook()
# for the security argument, and SHARED_CONFIRM_SNAPSHOTS for what happens
# when someone forges a beat anyway.

SESSION_FILE = "session.json"

# Account-sharing detector cadence. A BUILD-TIME CONSTANT on purpose: see
# presence_interval_seconds(). The publisher counts distinct live nonces
# inside a 5-minute window, so a 2-minute beat gives ~2 samples per
# machine - enough to tell "one machine" from "two" with one missed beat
# of slack, and short enough that a closed session frees the account fast.
PRESENCE_HEARTBEAT_MINUTES = 2

HTTP_TIMEOUT = 15.0
LOGIN_TIMEOUT = 300.0

def CANCELLED_MSG():
    return i18n.L("online.cancelled")

# ----------------------------------------------------------------------
# OAuth providers, direct from the app. pkce = provider supports the
# S256 proof-key flow; refresh = provider issues refresh tokens.
# Fill CLIENT_ID/CLIENT_SECRET before building (GITHUB-BACKEND.md §2).
# ----------------------------------------------------------------------

def _provider_table():
    """The OAuth provider table, assembled at call time.

    A function rather than a module dict so the credentials are read from
    build_secrets when they are needed instead of being bound into a
    module-level literal at import - which is what put the client secret
    in the .pyc and in every traceback that ever printed the table.
    """
    return {
        "discord": dict(
            label="Discord",
            auth="https://discord.com/oauth2/authorize",
            token="https://discord.com/api/oauth2/token",
            userinfo="https://discord.com/api/users/@me",
            # v8.49: PKCE (S256) is now attempted for Discord too. RFC 8252
            # section 8.1 recommends it for native apps precisely because
            # the client secret is extractable from the binary; the code
            # path was already fully implemented and simply never engaged.
            # login_with_provider retries WITHOUT the verifier if the token
            # endpoint rejects it, so enabling PKCE cannot brick sign-in.
            scope="identify email", pkce=True, refresh=True,
            client_id=build_secrets.discord_client_id(),
            client_secret=build_secrets.discord_client_secret(),
            identity=lambda u: (u.get("id"), u.get("email"),
                                u.get("username")),
        ),
    }


class _ProviderProxy(object):
    """Dict-like view over _provider_table(), so PROVIDER_TABLE[...] and
    `for k in PROVIDER_TABLE` keep working without materialising the
    credentials at import time."""

    def __getitem__(self, key):
        return _provider_table()[key]

    def get(self, key, default=None):
        return _provider_table().get(key, default)

    def __contains__(self, key):
        return key in _provider_table()

    def __iter__(self):
        return iter(_provider_table())

    def __len__(self):
        return len(_provider_table())

    def keys(self):
        return _provider_table().keys()

    def items(self):
        return _provider_table().items()

    def values(self):
        return _provider_table().values()


PROVIDER_TABLE = _ProviderProxy()

PROVIDERS = [(k, PROVIDER_TABLE[k]["label"]) for k in ("discord",)]

# Dev/test overrides for the provider credentials are handled inside
# build_secrets (SNAPPYAI_OAUTH_DISCORD_CLIENT_ID / _CLIENT_SECRET), and
# apply in an unfrozen run only. They used to be applied here, at import,
# by mutating PROVIDER_TABLE - which is why the secret had to be a module
# literal in the first place.


class OnlineError(Exception):
    """Network/path failure: no answer at all (or an untrusted one)."""


# ----------------------------------------------------------------------
# config helpers
# ----------------------------------------------------------------------

def entitlement_repo(cfg=None):
    """owner/repo of the PUBLIC repo holding signed entitlements.json.

    `cfg` is accepted and ignored, so every existing call site keeps
    working: this was a setting once, and it must not be one again. The
    only override is --repo in an unfrozen dev run (set_dev_repo)."""
    if _DEV_REPO:
        return _DEV_REPO
    return build_secrets.entitlement_repo()


def entitlement_branch(cfg=None):
    """Branch, sanitised: it is interpolated into a URL path, so a value
    carrying "/", "?" or "#" would reshape the request. Not a security
    boundary - the signature check still gates everything - but an
    unsanitised branch turns a typo into a confusing HTTP error."""
    raw = build_secrets.entitlement_branch() or "live"
    return _safe_url_segment(raw, "live")


def _safe_url_segment(value, fallback):
    """One path segment of a raw.githubusercontent.com URL."""
    v = str(value or "").strip().strip("/")
    if not v:
        return fallback
    # a segment must not be able to walk out of the path or start a query
    for ch in ("/", "?", "#", "@", ".."):
        if ch in v:
            log("entitlement branch %r contains %r - using %r."
                % (value, ch, fallback))
            return fallback
    return v


def entitlement_pubkey(cfg=None):
    """The Ed25519 PUBLIC key this build verifies entitlements.json with.

    SECURITY: this is a BUILD CONSTANT (build_secrets) and is deliberately
    NOT read from config. It used to be an ordinary config key, which meant
    the trust anchor sat in a user-writable config.json next to the exe:
    generate your own keypair, self-sign your own entitlements.json, host
    it in any public repo, point `entitlement_repo` + `entitlement_pubkey`
    at it, and the app verifies your file with YOUR key and starts the
    engine having paid nothing. Pinning the key makes repointing the repo
    useless - an attacker's file simply fails verification.

    The only override is an environment variable in an UNFROZEN run, so
    you can still test against a staging publisher from source; that is
    handled inside build_secrets."""
    return build_secrets.entitlement_pubkey()


def entitlement_url(cfg=None):
    return "https://raw.githubusercontent.com/%s/%s/%s" % (
        entitlement_repo(cfg), entitlement_branch(cfg), ENTITLEMENT_PATH)


def payment_link(cfg=None, kind="monthly"):
    """kind = "monthly" (the subscription link) or "trial" (the one-time
    1.99 EUR link). Stripe cannot put a one-time price and a recurring
    price on one payment link, so the two live on separate products.

    Both come from build_secrets: they are not settings, and they must
    never land in config.json or an exported settings file. The gate
    ALWAYS shows the trial button, so an empty link is a build defect -
    which is why build_secrets.describe_readiness() reports it."""
    if kind == "trial":
        return build_secrets.stripe_trial_link()
    return build_secrets.stripe_monthly_link()


def build_is_ready():
    """(fatal, advisory) for this build's deployment constants.

    Checked once at start-up so a mis-packaged exe says what is wrong
    instead of failing later as "auth server unreachable" twenty minutes
    into a support call. The advisory case that matters most is test-mode
    Stripe: the link completes checkout, charges nothing, creates no
    entitlement row, and the gate then says "still none" forever with no
    explanation.

    Returns TWO lists, not one boolean - see build_secrets.describe_
    readiness(). Only `fatal` may stop the app; `advisory` must be shown
    and then allowed past, or a developer cannot build a test exe at all
    until production payment links exist."""
    return build_secrets.describe_readiness()


def configured(cfg=None):
    """True when the build carries the constants sign-in needs.

    No longer a question about the user's config: repo, pubkey and the
    provider client id are all build constants, so this is a build
    sanity check, not a settings check."""
    return bool(entitlement_repo(cfg) and entitlement_pubkey(cfg)
                and build_secrets.discord_client_id())


def _http(url, data=None, headers=None, timeout=HTTP_TIMEOUT,
          form=None):
    """(status, bytes). form = dict -> urlencoded POST."""
    hdrs = {"Accept": "application/json",
            "User-Agent": "SnappyAI/" + APP_VERSION}
    hdrs.update(headers or {})
    body = None
    if form is not None:
        body = urllib.parse.urlencode(
            {k: v for k, v in form.items() if v is not None}).encode()
        hdrs["Content-Type"] = "application/x-www-form-urlencoded"
    elif data is not None:
        body = data
    req = urllib.request.Request(url, data=body, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        try:
            return exc.code, exc.read()
        except Exception:
            return exc.code, b""
    except Exception as exc:
        raise OnlineError("%r" % (exc,))


def _json(status, body):
    try:
        return status, json.loads(body.decode("utf-8", "replace"))
    except ValueError:
        raise OnlineError("non-JSON answer (HTTP %d)" % status)


# ----------------------------------------------------------------------
# session.json: the provider tokens, DPAPI-protected where possible
# ----------------------------------------------------------------------

def _dpapi_protect(blob):
    if not IS_WINDOWS:
        return None
    try:
        import ctypes
        import ctypes.wintypes as wt

        class DATA_BLOB(ctypes.Structure):
            _fields_ = [("cbData", wt.DWORD),
                        ("pbData", ctypes.POINTER(ctypes.c_char))]

        inp = DATA_BLOB(len(blob),
                        ctypes.create_string_buffer(blob, len(blob)))
        out = DATA_BLOB()
        if not ctypes.windll.crypt32.CryptProtectData(
                ctypes.byref(inp), "SnappyAI session", None, None, None,
                0, ctypes.byref(out)):
            return None
        data = ctypes.string_at(out.pbData, out.cbData)
        ctypes.windll.kernel32.LocalFree(out.pbData)
        return data
    except Exception:
        return None


def _dpapi_unprotect(blob):
    if not IS_WINDOWS:
        return None
    try:
        import ctypes
        import ctypes.wintypes as wt

        class DATA_BLOB(ctypes.Structure):
            _fields_ = [("cbData", wt.DWORD),
                        ("pbData", ctypes.POINTER(ctypes.c_char))]

        inp = DATA_BLOB(len(blob),
                        ctypes.create_string_buffer(blob, len(blob)))
        out = DATA_BLOB()
        if not ctypes.windll.crypt32.CryptUnprotectData(
                ctypes.byref(inp), None, None, None, None, 0,
                ctypes.byref(out)):
            return None
        data = ctypes.string_at(out.pbData, out.cbData)
        ctypes.windll.kernel32.LocalFree(out.pbData)
        return data
    except Exception:
        return None


def secure_dir():
    """Where credential material lives: %LOCALAPPDATA%\\SnappyAI on
    Windows (per-machine, not roaming, not next to a shareable exe),
    $XDG_DATA_HOME/snappyai (~/.local/share/snappyai) elsewhere.
    Created on first use; falls back to config_dir() if unwritable."""
    if IS_WINDOWS:
        base = os.environ.get("LOCALAPPDATA")
        if base:
            cand = os.path.join(base, "SnappyAI")
        else:
            cand = os.path.join(os.path.expanduser("~"), "AppData",
                                "Local", "SnappyAI")
    else:
        base = os.environ.get("XDG_DATA_HOME")
        cand = os.path.join(base, "snappyai") if base else os.path.join(
            os.path.expanduser("~"), ".local", "share", "snappyai")
    try:
        os.makedirs(cand, exist_ok=True)
        probe = os.path.join(cand, ".write_test")
        with open(probe, "w") as fh:
            fh.write("x")
        os.remove(probe)
        return cand
    except OSError:
        return config_dir()


def _session_path():
    return os.path.join(secure_dir(), SESSION_FILE)


def load_session():
    """Decoded session dict or None. Never raises."""
    try:
        with open(_session_path(), "rb") as fh:
            wrap = json.loads(fh.read().decode("utf-8"))
    except (OSError, ValueError):
        return None
    try:
        raw = base64.b64decode(wrap.get("data", ""))
        if wrap.get("prot") == "dpapi":
            raw = _dpapi_unprotect(raw)
            if raw is None:
                return None          # other Windows user/profile
        sess = json.loads(raw.decode("utf-8"))
        return sess if isinstance(sess, dict) else None
    except Exception:
        return None


def save_session(sess):
    raw = json.dumps(sess).encode("utf-8")
    prot = "b64"
    blob = _dpapi_protect(raw)
    # never trust DPAPI blindly: a half-working protection (or a fake
    # win32 layer in the test harness) must fall back, not lose tokens
    if blob is not None and _dpapi_unprotect(blob) == raw:
        raw, prot = blob, "dpapi"
    else:
        if blob is not None:
            log("session.json: DPAPI round-trip failed - storing "
                "obfuscated, not encrypted.")
        else:
            log("session.json: DPAPI unavailable - storing obfuscated, "
                "not encrypted (same guarantee as a browser cookie).")
    try:
        with open(_session_path(), "wb") as fh:
            fh.write(json.dumps({"v": 2, "prot": prot,
                                 "data": base64.b64encode(raw).decode()})
                     .encode("utf-8"))
        return True
    except OSError as exc:
        log("session.json: could not save (%r)" % (exc,))
        return False


def clear_session():
    try:
        os.remove(_session_path())
    except OSError:
        pass


def identity_key(identity):
    return "%s:%s" % (str(identity.get("provider", "")).lower(),
                      str(identity.get("sub", "")))


def identity_label(identity):
    return (str(identity.get("email") or "").strip()
            or str(identity.get("name") or "").strip()
            or identity_key(identity))


# ----------------------------------------------------------------------
# OAuth, straight from the app
# ----------------------------------------------------------------------

AUTH_BROWSER_PROFILE = "authbrowser"

# --- how the dedicated sign-in window is started ---------------------
#
# The window has to be a process WE started: that is the only kind of
# window a program may remove, because browser policy forbids a page
# from closing a tab the operating system opened. Two engine quirks
# decide the exact flags, and both of them used to break sign-in:
#
#   * On Windows, firefox.exe is a *launcher*: "the launcher process
#     usually exits immediately after the browser process is confirmed
#     to have started" (Mozilla). Without --wait-for-browser the
#     process we started is gone within a second while the window lives
#     on elsewhere - which we read as "the user closed the window",
#     tearing the loopback listener down under a redirect that was
#     already on its way ("cannot connect to 127.0.0.1:48321").
#   * Both engines forward a URL to an already-running instance when
#     the profile directory is locked, then exit. So every attempt gets
#     a FRESH profile directory, and Firefox also gets -no-remote.
FAST_EXIT_SECONDS = 3.0       # a launch that dies this fast handed off
LAUNCH_FAIL_OPEN_AFTER = 1.0  # nothing alive: open the default browser
UNVERIFIED_OPEN_AFTER = 12.0  # cannot check: open it anyway, but later
CANCEL_GRACE_SECONDS = 2.0    # let an in-flight redirect land first
PROFILES_TO_KEEP = 2          # per-attempt profile dirs kept on disk


def _auth_profile_dir():
    return os.path.join(secure_dir(), AUTH_BROWSER_PROFILE)


_KNOWN_BROWSER_PATHS = (
    ("msedge", ("ProgramFiles(x86)", r"Microsoft\Edge\Application\msedge.exe"),
     ("ProgramFiles", r"Microsoft\Edge\Application\msedge.exe"),
     ("LocalAppData", r"Microsoft\Edge\Application\msedge.exe")),
    ("chrome", ("LocalAppData", r"Google\Chrome\Application\chrome.exe"),
     ("ProgramFiles", r"Google\Chrome\Application\chrome.exe"),
     ("ProgramFiles(x86)", r"Google\Chrome\Application\chrome.exe")),
    ("brave", ("LocalAppData", r"BraveSoftware\Brave-Browser\Application\brave.exe"),
     ("ProgramFiles", r"BraveSoftware\Brave-Browser\Application\brave.exe"),
     ("ProgramFiles(x86)", r"BraveSoftware\Brave-Browser\Application\brave.exe")),
    ("vivaldi", ("LocalAppData", r"Vivaldi\Application\vivaldi.exe"),
     ("ProgramFiles", r"Vivaldi\Application\vivaldi.exe"),
     ("ProgramFiles(x86)", r"Vivaldi\Application\vivaldi.exe")),
    ("firefox", ("ProgramFiles", r"Mozilla Firefox\firefox.exe"),
     ("ProgramFiles(x86)", r"Mozilla Firefox\firefox.exe"),
     ("LocalAppData", r"Mozilla\firefox\firefox.exe")),
)
_BROWSER_ORDER = ("msedge", "chrome", "brave", "vivaldi", "firefox")
_BROWSER_EXES = ("msedge.exe", "chrome.exe", "brave.exe", "vivaldi.exe",
                 "firefox.exe")

# ProgId prefix -> engine, for the default-browser fallback: only used
# when the ProgId names an engine we know, so a Chromium command line
# can never be handed to Firefox or the other way round.
_PROGID_KINDS = (("MSEdgeHTM", "msedge"), ("ChromeHTML", "chrome"),
                 ("BraveHTML", "brave"), ("Vivaldi", "vivaldi"),
                 ("FirefoxURL", "firefox"), ("FirefoxHTML", "firefox"))

# A fresh profile is an empty profile: without these the window would
# open with first-run/welcome chrome around our sign-in page, and (for
# Chromium, whose profile we force-kill) with a "didn't shut down
# correctly" offer to restore pages.
_FIREFOX_USER_JS = """\
user_pref("browser.aboutwelcome.enabled", false);
user_pref("browser.startup.homepage_override.mstone", "ignore");
user_pref("trailhead.firstrun.didSeeAboutWelcome", true);
user_pref("browser.sessionstore.resume_from_crash", false);
user_pref("toolkit.startup.max_resumed_crashes", -1);
user_pref("datareporting.policy.dataSubmissionPolicyBypassNotification", true);
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("app.update.auto", false);
"""


def _winreg_views():
    """(winreg, access masks to try) or (None, ()).

    A 32-bit process reading SOFTWARE\\Microsoft\\... is redirected to
    WOW6432Node, where Edge and Chrome are not registered - one way a
    machine that HAS Edge can still come up "no browser found". Asking
    for both views explicitly covers either build of this exe."""
    try:
        import winreg
    except Exception:
        return None, ()
    views = []
    for flag in (getattr(winreg, "KEY_WOW64_64KEY", 0x0100),
                 getattr(winreg, "KEY_WOW64_32KEY", 0x0200)):
        views.append(winreg.KEY_READ | flag)
    views.append(winreg.KEY_READ)
    return winreg, views


def _app_paths_browser(exe_name):
    """Install path registered under App Paths, any registry view."""
    winreg, views = _winreg_views()
    if winreg is None:
        return None
    sub = (r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\\"
           + exe_name)
    for view in views:
        for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                key = winreg.OpenKey(hive, sub, 0, view)
                val = winreg.QueryValue(key, None)
                winreg.CloseKey(key)
            except OSError:
                continue
            if val and os.path.exists(val):
                return val
    return None


def _exe_from_command(cmd):
    r"""'"C:\...\chrome.exe" --flag "%1"' -> 'C:\...\chrome.exe'"""
    cmd = (cmd or "").strip()
    if not cmd:
        return None
    if cmd.startswith('"'):
        end = cmd.find('"', 1)
        return cmd[1:end] if end > 1 else None
    idx = cmd.lower().find(".exe")
    return cmd[:idx + 4] if idx > 0 else None


def _default_browser_exe():
    """(kind, path) of the user's default browser, or None.

    Last resort on machines whose browser lives somewhere we did not
    hard-code: Windows records the default https handler ProgId, and
    that ProgId's shell\\open\\command carries the exe."""
    winreg, views = _winreg_views()
    if winreg is None:
        return None
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\Shell\Associations"
            r"\UrlAssociations\https\UserChoice", 0, winreg.KEY_READ)
        progid = str(winreg.QueryValueEx(key, "ProgId")[0])
        winreg.CloseKey(key)
    except OSError:
        return None
    kind = None
    for prefix, name in _PROGID_KINDS:
        if progid.lower().startswith(prefix.lower()):
            kind = name
            break
    if kind is None:
        return None
    for view in views:
        try:
            key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,
                                 progid + r"\shell\open\command", 0, view)
            cmd = winreg.QueryValue(key, "")
            winreg.CloseKey(key)
        except OSError:
            continue
        exe = _exe_from_command(cmd)
        if exe and os.path.exists(exe):
            return kind, exe
    return None


def _find_auth_browser():
    """(kind, path) of a browser we may spawn with a DEDICATED profile.

    Discovery order: registry App Paths (both WOW64 views), well-known
    install locations including per-user installs, the user's default
    browser, then PATH. Chromium family first: a separate
    --user-data-dir always yields a separate process we can terminate
    cleanly, and --app gives a window with no tab strip left behind.
    """
    if not IS_WINDOWS:
        return None
    import shutil
    found = {}
    for exe in _BROWSER_EXES:
        val = _app_paths_browser(exe)
        if val:
            found.setdefault(exe.split(".")[0], val)
    for kind, *locs in _KNOWN_BROWSER_PATHS:
        if kind in found:
            continue
        for envvar, sub in locs:
            base = os.environ.get(envvar, "")
            if not base:
                continue
            cand = os.path.join(base, sub)
            if os.path.exists(cand):
                found[kind] = cand
                break
    for kind in _BROWSER_ORDER:
        if kind in found:
            return kind, found[kind]
    default = _default_browser_exe()
    if default:
        return default
    for kind in _BROWSER_ORDER:
        which = shutil.which(kind)
        if which:
            return kind, which
    return None


# ---------------------------------------------------------------------
# never let a child process put a console window on the customer's desk
# ---------------------------------------------------------------------
# The exe is built --noconsole, so it has NO console of its own. Every
# console-subsystem child it starts (taskkill.exe, cmd.exe, powershell)
# therefore gets a brand-new black window from Windows. Customers read
# that as malware, and it lands exactly when the sign-in tab closes, so
# it looks like the terminal closed their browser.
#
# Rule for this file: no child process is ever spawned except through
# _hidden_spawn_kwargs(), and a URL is only ever handed to ShellExecute
# (_open_url) - which is in-process and cannot create a console at all.
CREATE_NO_WINDOW = 0x08000000
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_DEFAULT_ERROR_MODE = 0x04000000
_SPAWN_FLAGS = (CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP
                | CREATE_DEFAULT_ERROR_MODE)
_NO_WINDOW_FLAGS = 0x00000001        # STARTF_USESHOWWINDOW
_SW_HIDE = 0


class _StartupInfo:
    """Stand-in for subprocess.STARTUPINFO (which only exists on
    Windows): same two attributes, so the kwargs this module builds are
    complete - and testable - on any platform."""
    __slots__ = ("dwFlags", "wShowWindow")

    def __init__(self):
        self.dwFlags = 0
        self.wShowWindow = 0


def _hidden_spawn_kwargs():
    """Popen kwargs that keep a HELPER child (taskkill, powershell, ...)
    off the screen.

    CREATE_NO_WINDOW covers console programs; the STARTUPINFO pair is a
    second layer for anything that is really a .cmd/.bat wrapper."""
    if not IS_WINDOWS:
        return {}
    try:
        import subprocess
        si = getattr(subprocess, "STARTUPINFO", _StartupInfo)()
        si.dwFlags |= _NO_WINDOW_FLAGS
        si.wShowWindow = _SW_HIDE
        return {"creationflags": _SPAWN_FLAGS, "startupinfo": si,
                "close_fds": True}
    except Exception:
        return {"creationflags": _SPAWN_FLAGS}


def _gui_spawn_flags():
    """creationflags for a child that is meant to SHOW a window.

    Deliberately no STARTUPINFO/SW_HIDE here: a browser reads nCmdShow
    from it, so hiding would risk opening the sign-in window invisibly.
    CREATE_NO_WINDOW is ignored by GUI-subsystem programs and only bites
    if the "browser" turns out to be a console wrapper."""
    if not IS_WINDOWS:
        return 0
    return CREATE_NO_WINDOW | CREATE_DEFAULT_ERROR_MODE


def _open_url(url):
    """Open a URL with NO child process at all where possible.

    `webbrowser.open()` is a last resort, not the first: on Windows it can
    end up running a registered handler through cmd.exe, and on a
    --noconsole exe that means a black terminal window flashing on the
    customer's screen. ShellExecute runs inside our own process."""
    url = str(url or "").strip()
    if not url:
        return False
    if IS_WINDOWS:
        # os.startfile IS ShellExecuteW("open") - in-process, no console,
        # and it honours the user's default browser.
        try:
            os.startfile(url)                 # noqa: S606 - Windows only
            return True
        except Exception:
            pass
        try:
            import ctypes
            shell32 = ctypes.windll.shell32
            shell32.ShellExecuteW.restype = ctypes.c_void_p
            shell32.ShellExecuteW.argtypes = [ctypes.c_void_p,
                                              ctypes.c_wchar_p,
                                              ctypes.c_wchar_p,
                                              ctypes.c_void_p,
                                              ctypes.c_wchar_p, ctypes.c_int]
            rc = shell32.ShellExecuteW(None, "open", url, None, None, 5)
            if isinstance(rc, int) and rc > 32:      # >32 == success
                return True
        except Exception:
            pass
    try:
        return bool(webbrowser.open(url))
    except Exception:
        return False


def _kill_browser_tree(proc):
    """Terminate the spawned browser AND its child processes; a bare
    Popen.terminate() can leave renderer/broker processes holding the
    window open.

    Pure Win32 first: walking the process tree and calling
    TerminateProcess is the same job `taskkill /PID n /T /F` does, minus
    the console window taskkill pops up on a --noconsole exe. taskkill
    stays only as a last resort, and hidden."""
    if proc is None:
        return
    if IS_WINDOWS:
        if _win32_kill_tree(proc.pid):
            log("Sign-in: window closed (process tree terminated in-process "
                "- no console window involved).")
            _reap(proc)
            return
        log("Sign-in: could not enumerate the process tree; falling back to "
            "a hidden taskkill.")
        try:
            import subprocess
            subprocess.run(
                ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                timeout=5, **_hidden_spawn_kwargs())
            _reap(proc)
            return
        except Exception:
            pass
    for stop in (proc.terminate, proc.kill):
        try:
            stop()
            proc.wait(timeout=2)
            return
        except Exception:
            continue


def _reap(proc):
    """Collect our own handle so the child is not left a zombie."""
    try:
        proc.wait(timeout=2)
    except Exception:
        pass


def _win32_kill_tree(root_pid):
    """True when the tree was terminated through kernel32 alone."""
    if not IS_WINDOWS:
        return False
    snap = _process_snapshot()
    if not snap:
        return False
    me = os.getpid()
    pids = [p for p in _process_tree(snap, root_pid) if p and p != me]
    if not pids:
        return False
    try:
        import ctypes
        from ctypes import wintypes
        k32 = ctypes.windll.kernel32
        k32.OpenProcess.restype = wintypes.HANDLE
        k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL,
                                    wintypes.DWORD]
        k32.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
        k32.CloseHandle.argtypes = [wintypes.HANDLE]
    except Exception:
        return False
    killed = False
    for pid in pids:                 # leaves first, root last (see _process_tree)
        try:
            handle = k32.OpenProcess(0x0001, False, int(pid))   # TERMINATE
            if not handle:
                continue
            try:
                if k32.TerminateProcess(handle, 1):
                    killed = True
            finally:
                k32.CloseHandle(handle)
        except Exception:
            continue
    return killed


def _process_snapshot():
    """{pid: (exe_name_lower, parent_pid)} for every process, or None.

    Toolhelp needs no admin rights, no WMI and no child process - which
    is the whole point: an external helper would flash a console window
    at the customer, a ctypes snapshot cannot. Also the source for
    _process_tree()."""
    if not IS_WINDOWS:
        return None
    try:
        import ctypes
        from ctypes import wintypes
    except Exception:
        return None

    class PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [("dwSize", wintypes.DWORD),
                    ("cntUsage", wintypes.DWORD),
                    ("th32ProcessID", wintypes.DWORD),
                    ("th32DefaultHeapID", ctypes.c_size_t),
                    ("th32ModuleID", wintypes.DWORD),
                    ("cntThreads", wintypes.DWORD),
                    ("th32ParentProcessID", wintypes.DWORD),
                    ("pcPriClassBase", ctypes.c_long),
                    ("szExeFile", ctypes.c_wchar * 260)]

    def _as_bool(value):
        # a real BOOL comes back as 1/0; anything else (a stubbed
        # ctypes layer, a driver that lied) means "unknown" - and
        # "unknown" must never turn into an endless walk
        return value is True or (isinstance(value, int) and value != 0)

    try:
        k32 = ctypes.windll.kernel32
        k32.CreateToolhelp32Snapshot.restype = ctypes.c_void_p
        k32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD,
                                                wintypes.DWORD]
        # Set here as well as in _win32_kill_tree: without argtypes a
        # c_void_p handle is marshalled as a 32-bit int, and which of the
        # two functions happened to run first decided whether this call was
        # correct. Order-dependent ctypes is a bug that only shows up on
        # one machine.
        k32.CloseHandle.argtypes = [wintypes.HANDLE]
        k32.CloseHandle.restype = wintypes.BOOL
        k32.Process32FirstW.restype = wintypes.BOOL
        k32.Process32FirstW.argtypes = [ctypes.c_void_p,
                                        ctypes.POINTER(PROCESSENTRY32W)]
        k32.Process32NextW.restype = wintypes.BOOL
        k32.Process32NextW.argtypes = [ctypes.c_void_p,
                                       ctypes.POINTER(PROCESSENTRY32W)]
        snap = k32.CreateToolhelp32Snapshot(0x2, 0)   # TH32CS_SNAPPROCESS
        if (not isinstance(snap, int) or not snap
                or snap in (0xFFFFFFFF, 0xFFFFFFFFFFFFFFFF)):
            return None        # INVALID_HANDLE_VALUE, either pointer size
        table = {}
        try:
            entry = PROCESSENTRY32W()
            entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)
            ok = _as_bool(k32.Process32FirstW(snap, ctypes.byref(entry)))
            walked = 0
            while ok and walked < 20000:
                walked += 1
                try:
                    table[int(entry.th32ProcessID)] = (
                        str(entry.szExeFile).lower(),
                        int(entry.th32ParentProcessID))
                except (TypeError, ValueError):
                    pass        # a stubbed ctypes layer: skip, never hang
                ok = _as_bool(k32.Process32NextW(snap, ctypes.byref(entry)))
        finally:
            k32.CloseHandle(snap)
        return table or None
    except Exception:
        return None


def _process_tree(snapshot, root_pid):
    """root_pid plus every descendant, deepest first.

    Children go before the parent so a browser that respawns its
    renderers cannot resurrect the window. A parent-PID cycle - possible,
    because Windows reuses PIDs - must not turn this into an endless
    walk, so the result is capped and the seen-set is authoritative."""
    try:
        root = int(root_pid)
    except (TypeError, ValueError):
        return []
    if not snapshot or root not in snapshot:
        return [root]
    order, seen, level = [], {root}, [root]
    while level and len(order) < 512:
        nxt = []
        for pid in level:
            for cand, entry in snapshot.items():
                if (entry[1] == pid and cand not in seen
                        and cand != pid and cand != root):
                    seen.add(cand)
                    nxt.append(cand)
                    order.append(cand)
        level = nxt
    order.reverse()          # deepest descendant first ...
    order.append(root)       # ... and the root window last
    return order


def _browser_pids(exe_path):
    """Set of PIDs currently running that browser exe, or None.

    Only consulted on the rare path where the process we started exits
    at once, to answer "did it leave a window behind?" - which decides
    between keep-waiting and open-the-default-browser."""
    snap = _process_snapshot()
    if not snap:
        return None
    # a Windows path may reach us with either separator (registry App
    # Paths uses \, a hand-written config may use /)
    want = str(exe_path or "").lower().replace("\\", "/").rsplit("/", 1)[-1]
    return {pid for pid, entry in snap.items() if entry[0] == want}


def _prune_profiles(root, keep):
    """Drop old per-attempt profile dirs. One a browser is still using
    refuses to delete - that is the correct outcome, not an error."""
    import shutil
    try:
        dirs = [os.path.join(root, n) for n in os.listdir(root)]
        dirs = [d for d in dirs if d != keep and os.path.isdir(d)]
        dirs.sort(key=lambda d: os.path.getmtime(d))
    except OSError:
        return
    for stale in dirs[:max(0, len(dirs) - PROFILES_TO_KEEP)]:
        shutil.rmtree(stale, ignore_errors=True)


def _fresh_profile_dir(kind):
    """A brand-new profile directory for this attempt.

    Sharing one directory is what makes a second browser forward its
    URL to the first (a locked profile means "already running", and the
    process we started then exits) - leaving the app waiting on a
    window it can neither watch nor close."""
    root = _auth_profile_dir()
    prof = os.path.join(root, "%s-%s" % (kind, secrets.token_hex(4)))
    try:
        os.makedirs(prof, exist_ok=True)
    except OSError:
        return os.path.join(root, kind)
    try:
        if kind == "firefox":
            with open(os.path.join(prof, "user.js"), "w",
                      encoding="utf-8") as fh:
                fh.write(_FIREFOX_USER_JS)
        else:
            default = os.path.join(prof, "Default")
            os.makedirs(default, exist_ok=True)
            with open(os.path.join(prof, "First Run"), "w") as fh:
                fh.write("")
            with open(os.path.join(default, "Preferences"), "w",
                      encoding="utf-8") as fh:
                json.dump({"profile": {"exit_type": "Normal",
                                       "exited_cleanly": True}}, fh)
    except OSError:
        pass
    _prune_profiles(root, prof)
    return prof


class _Launch:
    """The dedicated sign-in window we started."""
    __slots__ = ("proc", "label", "exe", "before")

    def __init__(self, proc, label, exe, before):
        self.proc = proc
        self.label = label
        self.exe = exe
        self.before = before      # browser PIDs that predate the launch


def _spawn_auth_browser(url):
    """_Launch, or None when no browser could be started.

    A window we own: dedicated profile (so it is a separate process we
    may terminate) and, on Chromium, --app (a popup-style window with no
    tab strip, so nothing is "left behind" to complain about)."""
    found = _find_auth_browser()
    if found is None:
        log("Sign-in: no spawnable browser found (registry App Paths, "
            "install folders and the default https handler were all "
            "empty).")
        return None
    kind, path = found
    before = _browser_pids(path)
    prof = _fresh_profile_dir(kind)
    try:
        import subprocess
        if kind == "firefox":
            args = [path,
                    "-no-remote",            # never forward to a running one
                    "-new-instance",
                    "--wait-for-browser",    # launcher lives as long as window
                    "-profile", prof,
                    "-new-window", url]
        else:
            args = [path, "--user-data-dir=" + prof, "--no-first-run",
                    "--no-default-browser-check", "--disable-sync",
                    "--disable-session-crashed-bubble",
                    "--hide-crash-restore-bubble", "--app=" + url]
        proc = subprocess.Popen(args, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                creationflags=_gui_spawn_flags())
        return _Launch(proc, "%s (%s)" % (kind, path), path, before)
    except Exception as exc:
        log("Sign-in: %s did not start (%r)." % (kind, exc))
        return None



def _redirect_uri():
    return "http://%s:%d%s" % (LOOPBACK_HOST, LOOPBACK_PORT, LOOPBACK_PATH)


def _exchange_code(provider, code, verifier=None):
    """Trade an authorization code for tokens.

    v8.49 PKCE: the verifier is sent when the provider advertises support,
    and if the token endpoint rejects the request the exchange is retried
    ONCE without it. That retry is what makes turning PKCE on safe - a
    provider that turns out not to accept a code_challenge for a
    confidential client costs one extra round trip during sign-in instead
    of a dead login flow, and the fallback is logged so the table can be
    corrected rather than silently relied on."""
    p = PROVIDER_TABLE[provider]

    def _post(use_verifier):
        return _json(*_http(p["token"], form={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": _redirect_uri(),
            "client_id": p["client_id"],
            "client_secret": p["client_secret"],
            "code_verifier": verifier if use_verifier else None,
        }, headers={"Accept": "application/json"}))

    status, tok = _post(bool(verifier))
    if verifier and (status != 200 or "access_token" not in tok):
        log("Sign-in: the token endpoint rejected the PKCE verifier "
            "(HTTP %d); retrying without it. If this repeats, set pkce=False "
            "for %r in the provider table." % (status, provider))
        status, tok = _post(False)
    if status != 200 or "access_token" not in tok:
        raise OnlineError("token exchange failed (HTTP %d)" % status)
    return tok


def _refresh(provider, refresh_token):
    p = PROVIDER_TABLE[provider]
    status, tok = _json(*_http(p["token"], form={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": p["client_id"],
        "client_secret": p["client_secret"],
    }, headers={"Accept": "application/json"}))
    if status != 200 or "access_token" not in tok:
        return None
    return tok


def _userinfo(provider, access_token):
    p = PROVIDER_TABLE[provider]
    status, user = _json(*_http(
        p["userinfo"], headers={"Authorization": "Bearer %s" % access_token,
                                "User-Agent": "SnappyAI/" + APP_VERSION}))
    if status != 200:
        return None
    sub, email, name = p["identity"](user)
    if not sub:
        return None
    return {"provider": provider, "sub": str(sub),
            "email": email or None, "name": name or None}


def _token_expiry(tok):
    try:
        return time.time() + float(tok.get("expires_in", 0)) - 60
    except (TypeError, ValueError):
        return 0.0


# ----------------------------------------------------------------------
# entitlements.json: fetch + verify
# ----------------------------------------------------------------------

def _canonical_bytes(doc):
    """The exact byte string the publisher signs.

    FORWARD COMPATIBILITY: canonicalise over EVERY key except `sig`, not
    over a hard-coded list. The builder signs `json.dumps(doc, ...)`
    before it adds `sig`, so "everything but sig" is by construction what
    it signed. The previous version enumerated ("v","generated_at",
    "cursor","rows"), which meant the first time anyone added a top-level
    field to the signed document (a `note`, a `schema`, a `min_version`)
    every client in the field would compute different bytes and reject a
    perfectly valid file - simultaneously, and unfixable remotely for
    already-shipped exes."""
    return json.dumps({k: v for k, v in doc.items() if k != "sig"},
                      sort_keys=True, separators=(",", ":")).encode("utf-8")


CACHE_BUCKET_SECONDS = 30


def fetch_entitlements(cfg, fresh=False):
    """Verified rows dict + generated_at, or OnlineError/(None).

    `fresh` controls CDN behaviour. raw.githubusercontent.com is
    CDN-served with a short max-age, and the whole capacity plan in
    GITHUB-BACKEND.md §7 assumes that caching. A unique `?ts=<epoch>` on
    EVERY request - which is what this used to do - gives every client a
    distinct cache key, so every poll is an origin miss: at 1 000 users
    the 2-minute presence poll alone is ~8 origin fetches/second for one
    ~1 KB static file. Background polls now share a 30-second bucket
    (plenty: the publisher only rewrites the file every ~10 minutes), and
    only a user who is actively waiting - "Re-check now", "I paid -
    activate now" - pays for a true cache bypass."""
    if not configured(cfg):
        raise OnlineError("entitlement_repo / entitlement_pubkey are "
                          "not configured (see GITHUB-BACKEND.md)")
    if fresh:
        qs = "?ts=%d" % int(time.time())
    else:
        qs = "?cb=%d" % (int(time.time()) // CACHE_BUCKET_SECONDS)
    status, body = _http(entitlement_url(cfg) + qs)
    if status == 404:
        raise OnlineError("entitlements.json not found in %s"
                          % entitlement_repo(cfg))
    if status != 200:
        raise OnlineError("GitHub raw answered HTTP %d" % status)
    try:
        doc = json.loads(body.decode("utf-8"))
    except ValueError:
        raise OnlineError("entitlements.json is not valid JSON")
    try:
        pub = base64.b64decode(entitlement_pubkey(cfg))
        sig = base64.b64decode(str(doc.get("sig", "")))
    except Exception:
        raise OnlineError("entitlement_pubkey / sig undecodable")
    if not edsig.verify(pub, _canonical_bytes(doc), sig):
        raise OnlineError("entitlements.json signature INVALID - "
                          "refusing an untrusted file")
    gen = int(doc.get("generated_at", 0) or 0)
    age = time.time() - gen
    if age > FRESHNESS_SECONDS:
        raise OnlineError(
            "entitlements.json is stale (published %s UTC, %d h %02d m ago; "
            "limit %d h) - the publisher pipeline is down. Run the "
            "'entitlements' workflow in the private controller repo "
            "(Actions -> entitlements -> Run workflow); see "
            "GITHUB-BACKEND.md section 12."
            % (time.strftime("%Y-%m-%d %H:%M", time.gmtime(gen)),
               int(age) // 3600, (int(age) % 3600) // 60,
               FRESHNESS_SECONDS // 3600))
    return doc.get("rows") or {}, gen


def _row_to_ent(row, now):
    if not isinstance(row, dict):
        return {"active": False, "status": "unsubscribed", "plan": None,
                "until": 0}
    until = float(row.get("until", 0) or 0)
    status = str(row.get("status", "unsubscribed"))
    active = until > now and status in ("trial", "active", "grant",
                                        "canceling")
    return {"active": active, "status": status,
            "plan": row.get("plan"), "until": until,
            "shared": bool(row.get("shared", False))}


IDENTITY_REFRESH_SECONDS = 6 * 3600


def me(cfg, fresh=False):
    """(identity, entitlement) with NO browser interaction.

    (None, None) when there is no usable local session (caller shows
    the sign-in window). Raises OnlineError when the signed entitlement
    file cannot be fetched or fails verification.

    The identity comes from the session cache and is only re-validated
    against the provider every IDENTITY_REFRESH_SECONDS. It used to call
    the provider's /users/@me on EVERY check, which meant:

      * the subscription gate polling every 30 s hit Discord's API every
        30 s per waiting user - and every Snappy AI install shares ONE
        baked-in client_id, so a few thousand users sitting on the gate
        is enough to trip Discord's rate limits;
      * a 429 (or any Discord blip) made _userinfo return None, me()
        returned (None, None), and the gate concluded "Session gone -
        sign in again" and closed itself - i.e. Discord being busy
        logged paying customers out;
      * every re-check paid a second round trip for data that cannot
        have changed since sign-in.

    A failed periodic re-validation now keeps the cached identity rather
    than ending the session: the entitlement file is the access control,
    and it is fetched from GitHub, not from Discord."""
    sess = load_session()
    if not sess or not sess.get("provider"):
        return None, None
    provider = sess["provider"]
    p = PROVIDER_TABLE.get(provider)
    if p is None:
        return None, None
    access = sess.get("access_token")
    if not access or time.time() > float(sess.get("expires_at", 0)):
        if not (p["refresh"] and sess.get("refresh_token")):
            return None, None        # needs a browser round trip
        tok = _refresh(provider, sess["refresh_token"])
        if tok is None:
            return None, None
        sess["access_token"] = tok["access_token"]
        sess["refresh_token"] = tok.get("refresh_token",
                                        sess.get("refresh_token"))
        sess["expires_at"] = _token_expiry(tok)
        save_session(sess)
        access = sess["access_token"]

    cached = sess.get("identity")
    cached_ok = (isinstance(cached, dict) and cached.get("sub")
                 and cached.get("provider") == provider)
    try:
        age = time.time() - float(sess.get("identity_at", 0) or 0)
    except (TypeError, ValueError):
        age = float("inf")
    need_refresh = not cached_ok or age > IDENTITY_REFRESH_SECONDS

    if need_refresh:
        # Independent fetches (provider vs GitHub raw): run them
        # concurrently so a genuine refresh still costs one round trip.
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            fut_id = pool.submit(_safe_userinfo, provider, access)
            fut_rows = pool.submit(fetch_entitlements, cfg, fresh)
            fresh_ident = fut_id.result()
            rows, _gen = fut_rows.result()
        if fresh_ident is not None:
            sess["identity"] = fresh_ident
            sess["identity_at"] = time.time()
            save_session(sess)
            cached = fresh_ident
        elif not cached_ok:
            # No cached fallback and the provider would not answer: this
            # is a network/provider problem, not a dead session.
            raise OnlineError("could not confirm the sign-in with %s "
                              "(no cached identity)" % provider)
        else:
            log("Identity re-validation failed - keeping the cached "
                "identity (the entitlement file is the access control).")
    else:
        rows, _gen = fetch_entitlements(cfg, fresh)

    row, _used = lookup_row(rows, cached)
    ent = _row_to_ent(row, time.time())
    # The `shared` flag passes through the confirmation window: a single
    # signed-file sighting is not acted on, because the heartbeat endpoint
    # is an open webhook and a beat can be forged by anyone who knows the
    # subscriber's e-mail. See _SharedGuard.
    idh = _used or row_hash(cached)
    ent["shared"] = row_shared(rows, idh, _gen)
    return cached, ent


def _safe_userinfo(provider, access_token):
    """_userinfo that degrades to None instead of raising, so a provider
    blip can never abort an entitlement check."""
    try:
        return _userinfo(provider, access_token)
    except OnlineError as exc:
        log("userinfo(%s) failed: %s" % (provider, exc))
        return None


def entitlement_active(ent, now=None):
    if not isinstance(ent, dict):
        return False
    if not ent.get("active"):
        return False
    try:
        until = float(ent.get("until", 0) or 0)
    except (TypeError, ValueError):
        return False
    now = now if now is not None else time.time()
    return until > now


def entitlement_key(identity):
    """The key an entitlement row lives under: the e-mail address.

    Stripe Payment Links silently ignore a client_reference_id URL
    parameter (proven against four real checkouts, round 7), but the
    paid e-mail always arrives inside the checkout session - so the
    publisher keys rows by a hash of the e-mail, and the app looks its
    Discord e-mail up there. The e-mail rule is structural: paying with
    any other address creates a row under THAT address, invisible to
    this login. Identities without a verified e-mail fall back to the
    provider id (and cannot subscribe until Discord provides one)."""
    email = str(identity.get("email") or "").strip().lower()
    return ("email:" + email) if email else identity_key(identity)


def _hash_key(key, pepper):
    return hashlib.sha256((pepper + key).encode("utf-8")).hexdigest()


def row_hash(identity):
    """The PRIMARY row hash for this identity (peppered when a pepper is
    built in). See row_hashes() for why the legacy form is still tried."""
    return _hash_key(entitlement_key(identity), build_secrets.row_pepper())


def row_hash_legacy(identity):
    """The pre-v8.49 hash: unsalted sha256 of the entitlement key.

    Kept for one reason - an already-published entitlements.json is keyed
    this way, and the publisher (a separate private repo) has to be
    updated in lockstep with the pepper. Looking up both means a client
    can ship before the publisher does, and vice versa, without anyone
    losing access mid-migration.

    WHY THE PEPPER EXISTS AT ALL: entitlements.json sits in a PUBLIC repo
    and is fetched without authentication. Unsalted sha256("email:" +
    address) over a low-entropy, heavily-enumerated input space is an
    offline cracking exercise on commodity hardware, so the file was
    effectively a published list of who pays for this product, with their
    status and renewal dates attached. That is personal data disclosed
    without a lawful basis. A build-time pepper raises the cost from
    "download a wordlist" to "extract the pepper from the binary and then
    still brute-force it" - not absolute, but a real change, and the
    honest ceiling for a client-side scheme."""
    return _hash_key(entitlement_key(identity), "")


def row_hashes(identity):
    """Every hash this identity could be filed under, primary first."""
    out = [row_hash(identity)]
    legacy = row_hash_legacy(identity)
    if legacy not in out:
        out.append(legacy)
    return out


def lookup_row(rows, identity):
    """(row, hash_used) for this identity, or (None, None).

    Tries the peppered hash first and falls back to the legacy unsalted
    one, so the client and the publisher can be migrated independently.
    A legacy match is logged once - that is the signal to rotate the
    publisher, and it should stop appearing when the migration is done."""
    if not isinstance(rows, dict):
        return None, None
    for h in row_hashes(identity):
        row = rows.get(h)
        if row is not None:
            if h == row_hash_legacy(identity) and build_secrets.row_pepper():
                log("Entitlement row matched the LEGACY unsalted hash - the "
                    "publisher has not been rotated to the peppered key yet.")
            return row, h
    return None, None


_STATUS_KEYS = {
    "active": "ent.st.active",
    "trial": "ent.st.trial",
    "grant": "ent.st.grant",
    "canceling": "ent.st.canceling",
    "past_due": "ent.st.past_due",
    "canceled": "ent.st.canceled",
    "refunded": "ent.st.refunded",
    "unsubscribed": "ent.st.unsubscribed",
}


def entitlement_summary(ent, now=None):
    """One human line covering every payment status we track."""
    if not isinstance(ent, dict) or not ent:
        return i18n.L(_STATUS_KEYS["unsubscribed"])
    now = time.time() if now is None else now
    st = str(ent.get("status", "unsubscribed"))
    until = float(ent.get("until") or 0)
    day = time.strftime("%Y-%m-%d", time.gmtime(until)) if until else ""
    plan = ent.get("plan") or ""
    if st in ("active", "trial", "grant") and until > now:
        # Don't render "trial (trial)" / "support grant (grant)": the plan
        # is only worth showing when it adds information to the status.
        label = i18n.L(_STATUS_KEYS[st])
        show_plan = plan and plan.lower() not in label.lower()
        return "%s%s%s" % (label,
                           i18n.L("ent.plan", plan) if show_plan else "",
                           i18n.L("ent.until", day) if day else "")
    if st == "canceling" and until > now:
        return i18n.L("ent.cancel_line", day)
    if st == "past_due":
        return i18n.L("ent.past_due_line")
    if st == "canceled":
        return i18n.L("ent.canceled_line", " on %s" % day if day else "")
    if st == "refunded":
        return i18n.L("ent.refunded_line")
    if until and until <= now:
        return i18n.L("ent.expired_line", day)
    return i18n.L(_STATUS_KEYS.get(st, "ent.st.unsubscribed"))


def subscribe_url(cfg, identity, kind="monthly"):
    """Payment link with the Discord e-mail prefilled (and locked in
    by the structural binding above). client_reference_id is kept as
    an audit hint only - the publisher no longer depends on it."""
    link = payment_link(cfg, kind)
    if not link:
        return ""
    sep = "&" if "?" in link else "?"
    email = str(identity.get("email") or "").strip().lower()
    out = "%s%sclient_reference_id=%s" % (
        link, sep, urllib.parse.quote(identity_key(identity), safe=""))
    if email:
        out += "&prefilled_email=%s" % urllib.parse.quote(email, safe="")
    return out


# Fine-grained PAT with Actions: write on the PRIVATE controller repo
# only. It can TRIGGER publisher runs, never read code, state or secrets.
#
# v8.49: this was the `publish_dispatch_pat` config key - a credential
# sitting in config.json in clear text, next to the payment links. It is a
# build constant now (SNAPPYAI_DISPATCH_PAT in an unfrozen run, encoded in
# the blob for a release). Empty = feature off, and "I paid - activate now"
# falls back to the cron cadence, which is the correct degradation.
DEFAULT_DISPATCH_PAT = ""


def dispatch_pat(cfg=None):
    """The Actions:write PAT, or "" when the feature is off."""
    import os as _os
    if not getattr(sys, "frozen", False):
        env = _os.environ.get("SNAPPYAI_DISPATCH_PAT", "").strip()
        if env:
            return env
    return DEFAULT_DISPATCH_PAT


def dispatch_publish(cfg=None):
    """Ask the publisher to run RIGHT NOW (repository_dispatch).
    Returns True when GitHub accepted the request."""
    pat = dispatch_pat(cfg)
    if not pat:
        return False
    repo = entitlement_repo(cfg)              # public repo = same owner
    owner = repo.split("/")[0] if "/" in repo else ""
    if not owner:
        return False
    url = ("https://api.github.com/repos/%s/snappyai-backend/actions/"
           "workflows/entitlements.yml/dispatches" % owner)
    body = json.dumps({"event_type": "publish"}).encode()
    try:
        status, _ = _http(url, data=body, timeout=10, headers={
            "Authorization": "Bearer %s" % pat,
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json"})
        return status in (200, 202, 204)
    except OnlineError:
        return False


# ----------------------------------------------------------------------
# Account-sharing detector, and why `shared` is no longer believed on the
# first sighting.
#
# The heartbeat endpoint is a Discord webhook URL baked into a distributed
# binary. Discord webhooks are bearer credentials: whoever holds the URL
# may post to it, and it cannot be made unforgeable from the client side.
# The payload is {identity_hash, nonce, timestamp}, and identity_hash is
# derivable by anyone who knows the subscriber's e-mail. So before v8.49
# any person could POST a second nonce for a victim's hash and the
# publisher would flag that account `shared` - pausing a PAYING customer's
# assistance remotely, repeatedly, at no cost, with no access to their
# machine. The old code treated one sighting as terminal.
#
# Two client-side changes take the attack apart:
#
#   1. CONFIRMATION WINDOW. `shared` only becomes effective after it has
#      been seen in SHARED_CONFIRM_SNAPSHOTS consecutive DISTINCT signed
#      file generations. The publisher rebuilds every ~10 minutes over a
#      5-minute liveness window, so a one-shot forged beat ages out before
#      it can ever be confirmed - while two genuinely live machines keep
#      re-appearing in every generation and are confirmed after
#      ~20 minutes. A sustained forgery still trips it; that is a much
#      higher bar, and unlike a single POST it leaves a rate-limitable
#      pattern in the channel.
#   2. THE WEBHOOK IS NO LONGER PLAINTEXT in the source or in config.json.
#
# The real fix is server-side and is recorded here so it is not lost: put
# an authenticated relay in front of the webhook (a Cloudflare Worker or
# small Function) that rate-limits per identity and only forwards beats
# carrying a valid per-install token. That is the only option which also
# stops channel spam, and it is the only one that makes `shared` safe to
# treat as authoritative again. Until it exists, `shared` is corroborated
# evidence, not proof.
# ----------------------------------------------------------------------

SHARED_CONFIRM_SNAPSHOTS = 2


class _SharedGuard(object):
    """Per-identity confirmation window for the `shared` flag."""

    def __init__(self):
        self._lock = threading.Lock()
        self._seen = {}       # idh -> {"gens": [gen, ...], "clean": int}

    def observe(self, idh, raw_shared, gen):
        """Record one signed-file observation; return the EFFECTIVE flag.

        `gen` is the file's `generated_at`, so consecutive polls inside one
        publisher generation cannot be counted as independent sightings -
        otherwise polling every 2 minutes would confirm a forgery in 4."""
        if not idh:
            return bool(raw_shared)
        with self._lock:
            st = self._seen.setdefault(idh, {"gens": [], "clean": 0})
            if not raw_shared:
                st["gens"] = []
                st["clean"] += 1
                return False
            if gen and gen not in st["gens"]:
                st["gens"].append(gen)
                st["gens"] = st["gens"][-SHARED_CONFIRM_SNAPSHOTS - 1:]
            st["clean"] = 0
            confirmed = len(st["gens"]) >= SHARED_CONFIRM_SNAPSHOTS
            if not confirmed and st["gens"]:
                log("Entitlement file reports this account as in use "
                    "elsewhere (generation %s). Not acting yet: a single "
                    "sighting can be a forged heartbeat, so this needs %d "
                    "consecutive signed generations."
                    % (gen, SHARED_CONFIRM_SNAPSHOTS))
            return confirmed

    def reset(self, idh=None):
        with self._lock:
            if idh is None:
                self._seen.clear()
            else:
                self._seen.pop(idh, None)


SHARED_GUARD = _SharedGuard()


def presence_webhook(cfg=None):
    """The channel heartbeats go to (build_secrets).

    SECURITY: not user-configurable, and not in config.json. It used to be
    overridable via `presence_webhook_url` in config.json/ini, which let
    anyone point their beats at a dead URL and silently opt out of
    account-sharing detection while keeping full access. The value itself
    is a build constant now, so it is neither readable from the settings
    file nor greppable in the source. Dev override is an environment
    variable in an UNFROZEN run only, handled in build_secrets."""
    return build_secrets.presence_webhook()


def row_shared(rows, idh, gen):
    """The EFFECTIVE `shared` flag for one identity in one signed file.

    Every consumer of the flag must go through here rather than reading
    `row["shared"]` directly, so the confirmation window applies uniformly
    to the gate, the runtime watcher and the console path."""
    row = rows.get(idh) if isinstance(rows, dict) else None
    raw = bool((row or {}).get("shared", False))
    return SHARED_GUARD.observe(idh, raw, gen)


def presence_interval_seconds(cfg=None):
    """Seconds between presence heartbeats while assistance is LAUNCHED.

    SECURITY: a build-time constant, not a setting. `presence_heartbeat_
    minutes` used to be an ordinary config key whose documented range
    included 0 ("feature off"), so one line in config.ini next to the exe
    stopped every heartbeat - the publisher then never saw a second live
    nonce and never set `shared`, defeating the one-subscription-one-
    machine rule entirely. The `cfg` argument is accepted and ignored so
    existing call sites keep working."""
    return PRESENCE_HEARTBEAT_MINUTES * 60


def post_presence(cfg, identity_hash, nonce, bye=False):
    """One heartbeat (or goodbye) to the Discord presence webhook.
    Best-effort by design: a failed beat just looks like a missed one,
    and the publisher's window logic tolerates gaps."""
    url = presence_webhook(cfg)
    if not url:
        return False
    payload = json.dumps({"k": identity_hash, "n": nonce,
                          "t": int(time.time()),
                          "bye": bool(bye), "v": 1})
    body = json.dumps({"content": payload,
                       "allowed_mentions": {"parse": []}}).encode()
    try:
        status, _ = _http(url, data=body, timeout=5,
                          headers={"Content-Type": "application/json"})
        return 200 <= status < 300
    except OnlineError:
        return False


_EMAIL_IN_URL = re.compile(r"(prefilled_email=)[^&]*")


def redact_url(url):
    """A payment URL with the subscriber's e-mail removed.

    The log file is the artefact users are asked to send when something
    goes wrong, and `subscribe_url` puts the Discord e-mail in the query
    string - so before v8.49 every "I paid" click wrote the customer's
    address into a file they were about to e-mail to support. The link is
    still useful evidence without it."""
    return _EMAIL_IN_URL.sub(r"\1<redacted>", str(url or ""))


def open_subscribe(cfg, identity, kind="monthly"):
    url = subscribe_url(cfg, identity, kind)
    log("Opening Stripe: %s" % redact_url(url))
    try:
        return _open_url(url)
    except Exception:
        return False


# ----------------------------------------------------------------------
# browser round trip (loopback), used when silent refresh is impossible
# ----------------------------------------------------------------------

PING_PATH = "/__snappy_ping"
PING_TOKEN = "snappyai-loopback"


class _Attempt:
    """One in-flight sign-in.

    The listener outlives the attempt (see _loopback_listener), so a
    redirect from an OLDER window - one the user left open after a
    cancel, or one the fallback below opened - must never be mistaken
    for this attempt's answer. The state parameter is the identity
    check; anything else gets a polite page and changes nothing."""
    __slots__ = ("state", "result", "done", "live")

    def __init__(self, state):
        self.state = state
        self.result = None
        self.done = threading.Event()
        self.live = True


_ATTEMPT = None
_ATTEMPT_LOCK = threading.Lock()


class _OAuthReturn(BaseHTTPRequestHandler):
    def _send(self, body, code=200, ctype="text/html; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(data)
        except OSError:
            pass

    def do_GET(self):
        parsed = urllib.parse.urlsplit(self.path)
        if parsed.path == PING_PATH:
            self._send(PING_TOKEN, ctype="text/plain; charset=utf-8")
            return
        if parsed.path != LOOPBACK_PATH:
            self._send(_PAGE_FAIL % _esc("wrong address"), code=404)
            return
        qs = urllib.parse.parse_qs(parsed.query)
        state = (qs.get("state") or [""])[0]
        with _ATTEMPT_LOCK:
            att = _ATTEMPT
            # v8.67: live/state checked INSIDE the lock - teardown
            # flips live=False under this same lock, so reading it
            # after release was a race that could treat a dying
            # attempt as current.
            if att is None or not att.live or state != att.state:
                att = None
        if att is None:
            # a window from an attempt we are no longer running, or a
            # local port scanner: answer, disturb nothing
            self._send(_PAGE_STALE)
            return
        code = (qs.get("code") or [""])[0]
        err = (qs.get("error_description") or qs.get("error") or [""])[0]
        if err:
            att.result = ("error", err, None)
            self._send(_PAGE_FAIL % _esc(err))
        elif not code:
            att.result = ("error", "the provider returned no code", None)
            self._send(_PAGE_FAIL % _esc("the provider returned no code"))
        else:
            att.result = ("ok", code, None)
            self._send(_PAGE_OK)
        att.done.set()          # release the waiter immediately

    def log_message(self, *args):
        pass


_CLOSE_SCRIPT = """<script>
/* The app has everything it needs the instant this page loads. A window
   WE started is removed by the app itself; this covers the fallback
   (the system browser), where a page may only close a window it opened
   - so it also blanks itself and titles the tab as a receipt rather
   than leaving an error behind. */
document.title = "\\u2713 Snappy AI";
try { window.close(); } catch (e) {}
setTimeout(function () {
  document.body.innerHTML = "";
  try { window.close(); } catch (e) {}
}, 700);
</script>"""

_PAGE_OK = ("""<html><head><title>\\u2713 Snappy AI</title></head>"""
            """<body style="font-family:Segoe UI,Arial,sans-serif;"""
            """background:#1e2026;color:#e9eaee;text-align:center;"""
            """padding-top:18vh"><h2>Snappy AI</h2>"""
            """<p>Signed in - returning to the app...</p>"""
            + _CLOSE_SCRIPT + """</body></html>""")

_PAGE_FAIL = ("""<html><head><title>Snappy AI</title></head>"""
              """<body style="font-family:Segoe UI,Arial,sans-serif;"""
              """background:#1e2026;color:#e9eaee;text-align:center;"""
              """padding-top:18vh"><h2>Snappy AI</h2>"""
              """<p>Sign-in failed: %s</p>"""
              """<p style="opacity:0.6">Close this window and try """
              """again in the app.</p></body></html>""")

_PAGE_STALE = ("""<html><head><title>Snappy AI</title></head>"""
               """<body style="font-family:Segoe UI,Arial,sans-serif;"""
               """background:#1e2026;color:#e9eaee;text-align:center;"""
               """padding-top:18vh"><h2>Snappy AI</h2>"""
               """<p>This sign-in window is no longer needed - the app """
               """stopped waiting for it.</p>"""
               """<p style="opacity:0.6">You can close it. To sign in, """
               """start again from the app.</p></body></html>""")


def _esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


_HTTPD = None
_HTTPD_LOCK = threading.Lock()


def _probe_listener():
    """True when the socket answering on the loopback port is OURS.

    http.server turns SO_REUSEADDR on, and on Windows that lets a second
    program bind a port that is already bound; without this check the
    provider's redirect could be served by somebody else while the app
    waits out its five minutes for an answer that never comes."""
    url = "http://%s:%d%s" % (LOOPBACK_HOST, LOOPBACK_PORT, PING_PATH)
    for _ in range(12):
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                body = resp.read(64).decode("utf-8", "replace")
            return body == PING_TOKEN
        except Exception:
            time.sleep(0.15)        # serve_forever may not be up yet
    return False


def _loopback_listener():
    """The one loopback listener, created on first sign-in and kept for
    the life of the process. Raises OnlineError with a readable reason.

    Deliberately never shut down between attempts. A browser window can
    outlive the attempt that opened it - Firefox's launcher hands the
    window to another process, a user can leave a window open after
    cancelling, the fallback can open a second one - and its redirect
    still has to reach something. "Cannot connect to 127.0.0.1:48321" is
    the one failure the user can do nothing about, so the port stays
    open and a late redirect gets a page that says it is no longer
    needed. Keeping one socket also makes retries immune to "port busy"
    from our own previous attempt."""
    global _HTTPD
    with _HTTPD_LOCK:
        if _HTTPD is not None:
            return _HTTPD
        httpd, last = None, None
        for _ in range(6):
            try:
                httpd = ThreadingHTTPServer((LOOPBACK_HOST, LOOPBACK_PORT),
                                            _OAuthReturn)
                break
            except OSError as exc:
                last = exc
                time.sleep(0.3)
        if httpd is None:
            raise OnlineError(
                "cannot listen on %s:%d (%r) - another program (or "
                "another Snappy AI) is using that port. Close it and "
                "try again." % (LOOPBACK_HOST, LOOPBACK_PORT, last))
        httpd.daemon_threads = True
        threading.Thread(target=httpd.serve_forever, daemon=True,
                         name="oauth-loopback").start()
        if not _probe_listener():
            try:
                httpd.shutdown()
                httpd.server_close()
            except Exception:
                pass
            raise OnlineError(
                "port %d is taken by another program, which answers "
                "instead of Snappy AI. Close that program (or the other "
                "Snappy AI) and try again." % LOOPBACK_PORT)
        _HTTPD = httpd
        log("Sign-in: loopback listener ready on http://%s:%d%s"
            % (LOOPBACK_HOST, LOOPBACK_PORT, LOOPBACK_PATH))
        return httpd


def close_loopback():
    """Release the singleton listener (tests, and a clean shutdown)."""
    global _HTTPD
    with _HTTPD_LOCK:
        httpd, _HTTPD = _HTTPD, None
    if httpd is None:
        return
    try:
        httpd.shutdown()
        httpd.server_close()
    except Exception:
        pass


def login_with_provider(cfg, provider, timeout=LOGIN_TIMEOUT,
                        opener=None):
    """One desktop OAuth round trip.

    Returns (identity, message): identity dict + "" on success, or
    (None, human-readable reason) on cancel/timeout/provider error.
    Raises OnlineError on token-exchange or userinfo failure."""
    p = PROVIDER_TABLE.get(provider)
    if p is None:
        raise OnlineError("unknown provider %r" % (provider,))
    if not p["client_id"]:
        raise OnlineError("provider %r has no client_id yet - paste the "
                          "OAuth app credentials into online.py "
                          "PROVIDER_TABLE (GITHUB-BACKEND.md §3), or set "
                          "SNAPPYAI_OAUTH_%s_CLIENT_ID/_SECRET for a dev "
                          "run without rebuilding"
                          % (provider, provider.upper()))
    if not configured(cfg):
        raise OnlineError("entitlement_repo / entitlement_pubkey are "
                          "not configured (see GITHUB-BACKEND.md)")

    _loopback_listener()        # readable OnlineError, never a traceback

    state = secrets.token_urlsafe(16)
    verifier = secrets.token_urlsafe(64) if p["pkce"] else None
    challenge = None
    if verifier:
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()

    global _ATTEMPT
    att = _Attempt(state)
    with _ATTEMPT_LOCK:
        _ATTEMPT = att

    q = {"client_id": p["client_id"], "redirect_uri": _redirect_uri(),
         "response_type": "code", "scope": p["scope"], "state": state}
    if challenge:
        q["code_challenge"] = challenge
        q["code_challenge_method"] = "S256"
    url = p["auth"] + "?" + urllib.parse.urlencode(q)

    launch = _spawn_auth_browser(url)
    if launch is not None:
        opened = True
        log("Sign-in: dedicated auto-closing sign-in window opened - "
            "%s." % launch.label)
    else:
        log("Sign-in: using your system browser instead (its tab must be "
            "closed by hand; browser policy forbids pages from closing "
            "OS-opened tabs).")
        try:
            opened = (opener or _open_url)(url)
        except Exception:
            opened = False
    if not opened:
        log("Could not open a browser automatically - open this URL "
            "by hand:\n    %s" % url)

    # A closed auth window is a cancellation, not a five-minute wait:
    # when we own the browser process, its exit releases the wait at
    # once and the sign-in button becomes clickable again with a
    # readable message. The catch is telling "user closed it" from
    # "the launcher exited and the window lives on in another process"
    # (Firefox on Windows, or a profile hand-off) - the difference
    # between those two decides whether the port stays open for a
    # redirect that is already on its way.
    started = time.time()
    cancel_event = threading.Event()
    handed_off = threading.Event()
    launch_failed = threading.Event()
    if launch is not None:
        def _watch():
            try:
                launch.proc.wait()
            except Exception:
                return
            lived = time.time() - started
            if lived >= FAST_EXIT_SECONDS:
                # a window that was really there, and is now closed
                time.sleep(CANCEL_GRACE_SECONDS)
                cancel_event.set()
                return
            alive = None
            for _ in range(2):
                now = _browser_pids(launch.exe)
                if now is not None:
                    if launch.before is not None:
                        # PIDs that appeared AFTER we spawned are ours;
                        # the user's pre-existing browser does not count.
                        alive = bool(now - launch.before)
                    else:
                        # The pre-spawn snapshot failed, so we cannot
                        # tell "our window handed off" from "the user's
                        # browser was already running". v8.67: do NOT
                        # trust a non-empty set (the old `bool(now)`
                        # credited any running browser as our hand-off);
                        # treat unknown parentage as no hand-off and let
                        # the default-browser fallback take over.
                        alive = False
                    if alive:
                        break
                time.sleep(0.3)
            if alive:
                handed_off.set()
                log("Sign-in: the process we started exited after %.1fs but "
                    "its window is alive in another process - still "
                    "listening on port %d." % (lived, LOOPBACK_PORT))
            elif alive is None:
                handed_off.set()
                log("Sign-in: that browser process exited after %.1fs and "
                    "we cannot enumerate processes to check its window - "
                    "still listening on port %d." % (lived, LOOPBACK_PORT))
            else:
                launch_failed.set()
                log("Sign-in: %s exited after %.1fs and left no window "
                    "behind." % (launch.label, lived))
        threading.Thread(target=_watch, daemon=True,
                         name="auth-browser-watch").start()

    deadline = started + timeout
    reopened = False
    while time.time() < deadline:
        if att.done.wait(0.2):
            break
        if cancel_event.is_set():
            break
        if not reopened and (launch_failed.is_set()
                             and time.time() - started
                             >= LAUNCH_FAIL_OPEN_AFTER):
            # The dedicated window never existed: make sure there IS one,
            # otherwise the user stares at nothing for five minutes.
            reopened = True
            log("Sign-in: opening the link in your default browser "
                "instead - the sign-in still ends here.")
            try:
                (opener or _open_url)(url)
            except Exception:
                pass
        if not reopened and handed_off.is_set() and time.time() - started \
                >= UNVERIFIED_OPEN_AFTER:
            # Handed off and we could not verify a window: give the user
            # one they can definitely see.
            reopened = True
            log("Sign-in: no window appeared - opening the link in your "
                "default browser; the sign-in still ends here.")
            try:
                (opener or _open_url)(url)
            except Exception:
                pass
    came = att.done.is_set()

    with _ATTEMPT_LOCK:
        att.live = False
        if _ATTEMPT is att:
            _ATTEMPT = None
    if launch is not None and not handed_off.is_set():
        # the window is ours: let the end page paint for a blink, then
        # remove it entirely (a timeout/cancel removes it too)
        if came:
            time.sleep(0.6)
        _kill_browser_tree(launch.proc)

    result = att.result
    if not came or result is None or result[0] != "ok":
        if result and result[0] == "error":
            msg = ("Discord authentication failed: %s - please try "
                   "again." % result[1])
        elif cancel_event.is_set():
            msg = CANCELLED_MSG()
        else:
            msg = ("Discord authentication timed out - please try "
                   "again.")
        log(msg)
        return None, msg

    code = result[1]
    tok = _exchange_code(provider, code, verifier)
    identity = _userinfo(provider, tok["access_token"])
    if identity is None:
        raise OnlineError("provider did not return an identity")
    save_session({
        "provider": provider,
        "access_token": tok["access_token"],
        "refresh_token": tok.get("refresh_token"),
        "expires_at": _token_expiry(tok) if tok.get("expires_in")
        else 0.0,
        "identity": identity,
        "identity_at": time.time(),   # me() re-validates on a timer now
    })
    # log the provider id, not the e-mail: identity_label() prefers the
    # address, and the log file is support evidence users are asked to
    # share (see redact_url).
    log("Signed in as %s (%s)." % (identity_key(identity), provider))
    return identity, ""
