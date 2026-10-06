#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Snappy AI
=========

Accessibility click helper for people with low vision.

Entry point. The code lives in focused modules:

    core.py      app identity + logging bus
    config.py    settings: defaults, validation, storage, reload, import/export
    vision.py    screen analysis engine (+ follow memory)
    i18n.py      runtime localisation (live language switch)
    hotkeys.py   bindable hotkey specs and action ids
    win32rt.py   Windows runtime (ctypes, capture backends, feedback)
    online.py    sign-in + entitlement client (OAuth worker, Stripe)
    assist.py    mouse hook + click workers + start_app()
    console.py   classic text interface (--console)
    gui.py       default interface: sign-in + subscription gate + settings
    logo.py      embedded logo image

There is no server we operate in this product. Sign-in is a direct
OAuth round trip from the app (loopback redirect), and the subscription
truth is an Ed25519-signed entitlements.json hosted as a PUBLIC file in
a GitHub repo - GitHub's own APIs are the "backend": a private-repo
Action rebuilds the file from Stripe events, and the app fetches and
verifies it directly. No middleman server exists or runs. See
GITHUB-BACKEND.md.

Run:
    python main.py               GUI (online sign-in first)
    python main.py --console     classic text interface
"""

import os
import sys

from core import (APP_NAME, IS_WINDOWS, attach_log_file, log,
                  log_path)
from config import DEFAULT_CONFIG, Config


def attach_app_log():
    """Point the log bus at a capped file inside the app's own data dir.

    The shipped GUI is built --noconsole, so without this every
    diagnostic line dies on a stream that does not exist and a field
    problem cannot be reported with evidence. Returns the path, or None
    when the folder is not writable - the app carries on either way.

    Named differently from core.attach_log_file on purpose: sharing the
    name shadowed the import and turned the delegation below into
    unbounded self-recursion.
    """
    try:
        import online
        base = online.secure_dir()
    except Exception:
        base = None
    if not base:
        return None
    try:
        return attach_log_file(os.path.join(base, "logs", "snappyai.log"))
    except Exception:
        return None


def apply_cli_overrides(cfg, argv):
    # v8.27: --launch / --paused are gone (the engine ALWAYS starts
    # paused; Launch is the only gate) and so are --voice / --silent
    # (the voice-feedback feature was removed entirely).

    if "--mode1" in argv:
        cfg.set("mode", 1, save=False)

    if "--mode2" in argv:
        cfg.set("mode", 2, save=False)

    if "--bare-keys" in argv:
        # v8.4 called this bare_mode_keys; the live key since then is
        # block_bound_keys (setting the old name would do nothing).
        cfg.set("block_bound_keys", True, save=False)

    if "--accent-only" in argv:
        cfg.set("accent_only", True, save=False)

    if "--follow" in argv:
        cfg.set("follow_enabled", True, save=False)

    if "--auto-click" in argv:
        cfg.set("auto_click", True, save=False)

    if "--motion-3d" in argv:
        cfg.set("motion_3d", True, save=False)

    if "--no-adaptive" in argv:
        cfg.set("adaptive_threshold", False, save=False)

    if "--no-lumnorm" in argv:
        cfg.set("luminance_norm", False, save=False)

    for i, arg in enumerate(argv):
        if arg == "--repo" and i + 1 < len(argv):
            # v8.49: the entitlement repo is a build constant, not a
            # setting, so this goes to online.set_dev_repo() - which refuses
            # in a frozen build. It was never a security boundary either
            # way: the Ed25519 public key is pinned, so a substituted repo
            # still has to present a validly signed file.
            try:
                import online
                online.set_dev_repo(argv[i + 1])
            except Exception as exc:
                print("Ignored --repo (%r)" % (exc,))

        elif arg == "--radius" and i + 1 < len(argv):
            value = argv[i + 1].lower()

            if value in ("small", "medium", "large"):
                cfg.set("radius", {"small": 80, "medium": 150,
                                   "large": 250}[value], save=False)
            else:
                # any integer px value (clamped by _sanitize below)
                try:
                    cfg.set("radius", int(float(value)), save=False)
                except (ValueError, OverflowError):
                    print("Ignored invalid --radius %r" % (argv[i + 1],))

        elif arg == "--capture" and i + 1 < len(argv):
            value = argv[i + 1].lower()

            if value in ("auto", "dxcam", "mss", "wgc"):
                cfg.set("capture_backend", value, save=False)
            else:
                print("Ignored invalid --capture %r" % (argv[i + 1],))

        elif arg == "--merge" and i + 1 < len(argv):
            try:
                cfg.set("merge_distance", int(float(argv[i + 1])), save=False)
            except (ValueError, OverflowError):
                # OverflowError, not just ValueError: "1e999" parses as a
                # float fine and then int(inf) raises. --radius two branches
                # up already caught both; these two did not, so a malformed
                # --merge killed the app before a window opened. A bad CLI
                # value must warn and fall back, exactly like a bad value in
                # config.json (see config._coerce_value).
                print("Ignored invalid --merge %r" % (argv[i + 1],))

        elif arg == "--accent" and i + 1 < len(argv):
            cfg.set("accent_color", argv[i + 1].strip(), save=False)

        elif arg == "--glide" and i + 1 < len(argv):
            try:
                cfg.set("glide_ms", int(float(argv[i + 1])), save=False)
            except (ValueError, OverflowError):
                print("Ignored invalid --glide %r" % (argv[i + 1],))




_KNOWN_FLAGS = ("--mode1", "--mode2", "--bare-keys", "--accent-only",
                "--follow", "--auto-click", "--motion-3d", "--no-adaptive",
                "--no-lumnorm", "--console", "--reset-config", "--help",
                "--repo", "--radius", "--capture", "--merge", "--accent",
                "--glide")


def _announce(title, body, fatal=False):
    """Show a message the user can actually SEE.

    The shipping exe is built --noconsole, so `print` alone makes every
    diagnostic invisible in exactly the situation where it matters - a
    double-click that appears to do nothing. core.py says as much about the
    log bus; the same rule applies to start-up, which is where this lives.

    Tries a Tk dialog first (works in a windowed build), then a Windows
    message box via ctypes (works even when Tk itself is what broke), and
    only then falls back to print. Always logs as well, so there is a
    written record next to the log file."""
    text = "%s\n\n%s" % (title, body)
    try:
        log(text.replace("\n", " | "))
    except Exception:
        pass
    try:
        import tkinter
        from tkinter import messagebox
        root = tkinter.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        (messagebox.showerror if fatal else messagebox.showwarning)(
            APP_NAME, text)
        root.destroy()
        return
    except Exception:
        pass
    if IS_WINDOWS:
        try:
            import ctypes
            # MB_ICONERROR/MB_TOPMOST: a real dialog with no Tk involved
            ctypes.windll.user32.MessageBoxW(
                None, text, APP_NAME, 0x10 | 0x40000)
            return
        except Exception:
            pass
    print(text)


def _crash_guard(exc_type, exc, tb):
    """Last resort: never let the exe die without saying why.

    A --noconsole --onefile build that raises during start-up otherwise
    produces the single most unhelpful symptom in desktop software - a
    double-click, a brief disk churn while the bundle unpacks, and nothing.
    The traceback goes to a dialog AND to the log file, with the log path
    spelled out, so "it doesn't run" becomes a reportable sentence."""
    import traceback
    text = "".join(traceback.format_exception(exc_type, exc, tb))
    try:
        log("FATAL start-up error:\n" + text)
    except Exception:
        pass
    where = None
    try:
        where = log_path()
    except Exception:
        pass
    body = text.strip().splitlines()
    tail = "\n".join(body[-12:]) if len(body) > 12 else text.strip()
    _announce("%s could not start" % APP_NAME,
              "%s\n\n%s%s" % (
                  tail,
                  "Log file: %s" % where if where else
                  "No log file could be opened.",
                  ""),
              fatal=True)


def warn_unknown_flags(argv):
    """Say so when a flag does nothing.

    Silent acceptance is how "--radiuss 250" becomes a support thread about
    the radius setting not working."""
    for arg in argv[1:]:
        if arg.startswith("--") and arg not in _KNOWN_FLAGS:
            print("Ignored unknown option %r (try --help)." % (arg,))


def print_usage():
    print("")
    print("Snappy AI - accessibility click helper")
    print("")
    print("  (no option)        start the graphical interface")
    print("  --console          classic text interface")
    print("  --help             this text")
    print("")
    print("  --mode1 | --mode2  classic (suppress + snap) / guide (never eat a click)")
    print("  --radius N|small|medium|large   search distance in pixels")
    print("  --capture auto|dxcam|mss|wgc    screen-capture backend")
    print("  --merge N          merge detected pieces within N px")
    print("  --accent SPEC      preferred colour(s): blue, 60,120,220, or a ; list")
    print("  --glide MS         animate cursor moves over MS milliseconds")
    print("  --accent-only      assist only items carrying the accent colour")
    print("  --follow           remember and prefer the last snapped item")
    print("  --auto-click       click the accent colour without a gesture (capped)")
    print("  --motion-3d        lead moving targets with the position+scale tracker")
    print("  --no-adaptive      disable the adaptive ink threshold (A/B)")
    print("  --no-lumnorm       disable luminance normalisation (A/B)")
    print("  --bare-keys        bound single keys swallow the key while typing")
    print("  --reset-config     restore every setting to its default")
    print("")
    print("Settings live in config.json / config.ini next to the executable.")
    print("Deployment constants (entitlement repo, payment links, provider")
    print("credentials) are build-time and deliberately not settings.")
    print("")


def main():
    sys.excepthook = _crash_guard
    if "--help" in sys.argv or "-h" in sys.argv:
        print_usage()
        sys.exit(0)
    try:
        _run()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        sys.exit(0)
    except BaseException:
        # sys.excepthook does not fire for an exception that escapes the
        # main script in every embedding, so catch it here too.
        _crash_guard(*sys.exc_info())
        sys.exit(1)


def _run():
    attach_app_log()                # first: capture everything that follows
    cfg = Config()

    if "--reset-config" in sys.argv:
        cfg.values = dict(DEFAULT_CONFIG)
        cfg.save()
        print("Config reset to defaults: %s" % cfg.path)

    warn_unknown_flags(sys.argv)
    apply_cli_overrides(cfg, sys.argv)
    cfg.sanitize()    # clamp/validate CLI values exactly like file loads

    # Say what is wrong with the build BEFORE the sign-in window, so a
    # mis-packaged exe explains itself instead of failing later as
    # "auth server unreachable" twenty minutes into a support call.
    #
    # v8.49.1: two corrections to how this was first written.
    #
    #   * It announced itself with print(), which in a --noconsole build
    #     goes to a stream that does not exist - so the exe exited having
    #     told nobody anything, and the symptom was "double-click, nothing
    #     happens". _announce() shows a real dialog instead.
    #   * It treated EVERY readiness problem as fatal, so a build with
    #     test-mode Stripe links could not start at all. That is wrong:
    #     test-mode links are the normal state of a developer's exe. Only
    #     genuinely non-functional builds (no key to verify with, no client
    #     id to sign in with) refuse to start; the rest warn and continue.
    try:
        import online
        fatal, advisory = online.build_is_ready()
        for problem in advisory:
            log("BUILD: %s" % problem)
        if advisory and not fatal:
            # A dialog on every unfrozen run would be noise for the person
            # developing it - the log line is enough there. In a packaged
            # build the dialog is the only channel that exists.
            if getattr(sys, "frozen", False):
                _announce(
                    "This is not a release build",
                    "\n".join("- " + p for p in advisory)
                    + "\n\nThe app will start normally. Fix these before "
                      "distributing it.")
        if fatal:
            _announce("%s cannot start" % APP_NAME,
                      "This build is missing the constants it needs:\n\n"
                      + "\n".join("- " + p for p in fatal)
                      + "\n\nRe-package it with the production deployment "
                        "constants injected (see build_secrets.py).",
                      fatal=True)
            sys.exit(1)
    except SystemExit:
        raise
    except Exception as exc:
        log("build readiness check failed: %r" % (exc,))

    if not IS_WINDOWS:
        print("")
        print("Snappy AI active mouse assistance currently requires Windows.")
        print("")
        sys.exit(1)

    # Default interface: the GUI (login screen first). --console keeps
    # the classic text UI; it is the developer/debug path.
    use_gui = "--console" not in sys.argv
    if use_gui:
        try:
            import tkinter  # noqa: F401
        except ImportError:
            print("Tkinter unavailable - starting in console mode.")
            use_gui = False

    if use_gui:
        from gui import run_gui
        sys.exit(run_gui(cfg))
    from console import console_gate, windows_main
    identity = console_gate(cfg)
    if identity is None:
        sys.exit(1)
    sys.exit(windows_main(cfg, identity))


if __name__ == "__main__":
    main()
