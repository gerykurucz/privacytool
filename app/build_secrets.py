"""Deployment constants: links, keys and credentials.

WHY THIS MODULE EXISTS
----------------------
Until v8.49 the entitlement repo, both Stripe payment links, the Discord
OAuth client secret and the presence webhook lived in `config.py`'s
DEFAULT_CONFIG. Two consequences, both bad:

  * `Config.save()` dumps every value, so **config.json next to the exe
    carried the payment links and the repo in clear text** - readable by
    anyone with the folder, included in every "please send me your
    config" support exchange, and copied by Export Config into a file
    users were encouraged to share;
  * the source itself was greppable, so the webhook and the client
    secret were one `strings SnappyAI.exe` away.

None of these are settings. A user has no legitimate reason to point the
app at a different entitlement repo (the Ed25519 public key is pinned, so
repointing gains nothing) or to swap the payment links. So they are build
constants now, they are NOT in DEFAULT_CONFIG, and `Config.save()`
additionally refuses to write any key on SENSITIVE_KEYS as a second
layer - a future setting must be actively allowed to reach the disk.

HONEST THREAT MODEL
-------------------
The values below are obfuscated (XOR under a build key + base64), not
encrypted. `_KEY` ships in the exe, so a determined attacker with a
debugger recovers them; that is unavoidable for any client-side program
and is the same reality as a browser shipping its OAuth client id. What
this does buy:

  * nothing sensitive in config.json, ever - the file the app is most
    often asked to hand over is now clean;
  * nothing sensitive in Export Config output;
  * no plaintext credential in the source tree or in `strings` output,
    so casual scraping and accidental publication stop working;
  * one place to rotate, and a build-time injection path so the real
    production values never have to be committed at all.

BUILD-TIME INJECTION (preferred)
--------------------------------
Every constant can be supplied by the build environment instead of being
baked in, which is how a release SHOULD be produced - leave the encoded
placeholder empty and inject:

    SNAPPYAI_ENT_REPO, SNAPPYAI_ENT_BRANCH, SNAPPYAI_ENT_PUBKEY,
    SNAPPYAI_STRIPE_MONTHLY, SNAPPYAI_STRIPE_TRIAL,
    SNAPPYAI_OAUTH_DISCORD_CLIENT_ID, SNAPPYAI_OAUTH_DISCORD_CLIENT_SECRET,
    SNAPPYAI_PRESENCE_WEBHOOK, SNAPPYAI_ROW_PEPPER

Environment overrides apply in an UNFROZEN run only, exactly like the
existing dev overrides in online.py, so a user cannot repoint a shipped
exe by setting a variable.
"""

import base64
import hashlib
import os
import sys

# Build key for the obfuscation below. Not a secret: it is present in the
# shipped binary. Its job is to keep credentials out of the readable
# source and out of `strings`, not to resist a debugger.
_KEY = b"SnappyAI/build-secrets/v1"

# Encoded deployment constants. Decode with _get(); never read directly.
_BLOB = {
    "DISCORD_CLIENT_ID": "mVzqIJpPmEVQ4kbHjPhdEwNvEw==",
    "DISCORD_CLIENT_SEC": "0FqFddIc+AA0hkWXzfkBYEc9aGvR6yLEfHXHZbN2dlA=",
    "ENTITLEMENT_BRANCH": "xACpdg==",
    "ENTITLEMENT_PUBKEY": "4lqKf9of1F8uhwq51I4RV3lsHynUlVzQYDeaQqkkf1LuD5tmkRbUIiOYNc0=",
    "ENTITLEMENT_REPO": "zwytaskP0wUHrV+D1qgYV0o/Ti/Zzx3LeCzMTpt8aWs=",
    "PRESENCE_WEBHOOK": (
        "wB2rY9FAjl8AvgOT17sMCVAxSi3d0QCNeyXLS5F9dmuHWOomkUOTR1TmQseB+V0QAm4U"
        "OpP5EeU1Gf4apn13YPcgsHySK+0nDrASsYyZAGt+FW9kxuBekm8z+Wi6dFNP/xypWfFX"
        "0xcivSKS/vtaQmoIb1vVkR2PXg=="),
    "ROW_PEPPER": "",   # injected at build time; see row_pepper()
    "STRIPE_MONTHLY": "wB2rY9FAjl8Gogney70aTkM7CWHTzEbWaTPdfJtEbH3+De0r5U/gKVCGPcmIpA52em4X",
    "STRIPE_TRIAL": "wB2rY9FAjl8Gogney70aTkM7CWHTzEbWaTPdfM1xVC7HIehnkk3rRlzlKZbXgg52em4W",
}

# Environment variable that overrides each constant in an unfrozen run.
_ENV = {
    "ENTITLEMENT_REPO":   "SNAPPYAI_ENT_REPO",
    "ENTITLEMENT_BRANCH": "SNAPPYAI_ENT_BRANCH",
    "ENTITLEMENT_PUBKEY": "SNAPPYAI_ENT_PUBKEY",
    "STRIPE_MONTHLY":     "SNAPPYAI_STRIPE_MONTHLY",
    "STRIPE_TRIAL":       "SNAPPYAI_STRIPE_TRIAL",
    "DISCORD_CLIENT_ID":  "SNAPPYAI_OAUTH_DISCORD_CLIENT_ID",
    "DISCORD_CLIENT_SEC": "SNAPPYAI_OAUTH_DISCORD_CLIENT_SECRET",
    "PRESENCE_WEBHOOK":   "SNAPPYAI_PRESENCE_WEBHOOK",
    "ROW_PEPPER":         "SNAPPYAI_ROW_PEPPER",
}

_ks = hashlib.sha256(_KEY).digest()
_cache = {}


def _decode(raw):
    data = base64.b64decode(raw)
    return bytes(c ^ _ks[i % len(_ks)]
                 for i, c in enumerate(data)).decode("utf-8")


def _get(name):
    """One deployment constant, from the build environment or the blob."""
    if name in _cache:
        return _cache[name]
    value = ""
    if not getattr(sys, "frozen", False):
        env = _ENV.get(name)
        if env:
            value = os.environ.get(env, "").strip()
    if not value:
        raw = _BLOB.get(name, "")
        if raw:
            try:
                value = _decode(raw)
            except Exception:
                value = ""
    _cache[name] = value
    return value


# ----------------------------------------------------------------------
# Public accessors. Import these; do not touch _BLOB.
# ----------------------------------------------------------------------

def entitlement_repo():
    """owner/repo of the PUBLIC repo holding signed entitlements.json."""
    return _get("ENTITLEMENT_REPO").strip().strip("/")


def entitlement_branch():
    return _get("ENTITLEMENT_BRANCH").strip() or "live"


def entitlement_pubkey():
    """Base64 Ed25519 PUBLIC key. The pinned trust anchor."""
    return _get("ENTITLEMENT_PUBKEY").strip()


def stripe_monthly_link():
    return _get("STRIPE_MONTHLY").strip()


def stripe_trial_link():
    return _get("STRIPE_TRIAL").strip()


def discord_client_id():
    return _get("DISCORD_CLIENT_ID").strip()


def discord_client_secret():
    return _get("DISCORD_CLIENT_SEC").strip()


def presence_webhook():
    return _get("PRESENCE_WEBHOOK").strip()


def row_pepper():
    """Pepper for the entitlement row hash (see online.row_hash).

    Empty means "legacy unsalted sha256 only". Set it at build time to
    stop the public entitlements.json from being an offline crack of the
    subscriber e-mail list."""
    return _get("ROW_PEPPER").strip()


def is_test_mode():
    """True when a Stripe payment link is still a test-mode link.

    A frozen build must never present a test-mode paywall as live: the
    checkout appears to succeed, no money moves, and no entitlement row
    is ever created, so the customer sees "still none" forever with no
    explanation. Callers turn this into a loud refusal instead."""
    links = stripe_monthly_link() + stripe_trial_link()
    return "buy.stripe.com/test_" in links or "/test/" in links


def describe_readiness():
    """(fatal, advisory) - what is wrong with this build's constants.

    Two severities, because they need different answers:

      FATAL     the app cannot do its job at all - there is no key to
                verify a subscription with, or no client id to sign in
                with. Starting would produce a window that can never let
                anyone in, so a frozen build refuses.
      ADVISORY  the app works, but this is not a shippable release - a
                test-mode Stripe link takes no real money, and a missing
                row pepper leaves the public entitlements file keyable by
                e-mail. A developer building a test exe MUST be allowed
                past these; before v8.49.1 they were treated as fatal,
                which meant no packaged build could start at all until
                production payment links existed.

    Both lists are meant to be SHOWN, not printed: the shipping exe is
    built --noconsole, where print() goes to a stream that does not
    exist (see main._announce)."""
    fatal = []
    advisory = []
    if not entitlement_pubkey():
        fatal.append("no Ed25519 public key - a subscription can never be "
                     "verified, so nobody could ever get past the gate")
    if not discord_client_id():
        fatal.append("no Discord OAuth client id - sign-in is impossible")
    if not entitlement_repo():
        fatal.append("no entitlement repo - there is nowhere to fetch the "
                     "signed subscription file from")
    if is_test_mode():
        advisory.append("the Stripe payment links are still in TEST mode - "
                        "checkout will complete, no money will move, and no "
                        "subscription will ever activate")
    if not row_pepper():
        advisory.append("no row-hash pepper - entitlement rows are keyed by "
                        "unsalted sha256(e-mail) in a PUBLIC file")
    if not presence_webhook():
        advisory.append("no presence webhook - account-sharing detection "
                        "is off")
    return fatal, advisory


def is_shippable():
    """True when this build has no fatal AND no advisory problems."""
    fatal, advisory = describe_readiness()
    return not fatal and not advisory


# Keys that must never be written to config.json or an export, even if a
# future change puts one into DEFAULT_CONFIG. config.py enforces this.
SENSITIVE_KEYS = frozenset((
    "entitlement_repo", "entitlement_branch", "entitlement_pubkey",
    "stripe_payment_link", "stripe_trial_link", "publish_dispatch_pat",
    "presence_webhook_url", "presence_heartbeat_minutes",
    "row_pepper", "client_secret", "client_id",
))
