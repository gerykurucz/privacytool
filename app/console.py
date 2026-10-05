"""Classic console interface:  python main.py --console
Commands: s=status t=toggle h=help q=quit a=accent f=follow c=autoclick
          v=calibrate colour"""

import queue
import sys
import threading
import time

import online
from core import APP_NAME, log

from config import RADIUS_STEPS
from assist import start_app
from hotkeys import effective_mode_key
from vision import (_parse_accents, accent_soft_of, accent_matcher_of,
                    calibrate_accent)

def print_banner(app):
    cfg = app.cfg

    rad_value = cfg.get("radius")
    rad_label = dict(RADIUS_STEPS).get(rad_value, "custom")

    print("")
    print("=" * 70)
    print("   S N A P P Y   A I  -  accessibility click helper")
    print("=" * 70)
    print("   MODE        : %s" % ("1 classic" if cfg.get("mode") == 1 else "2 guide"))
    print("   Radius      : %s (%d px)" % (rad_label, app.radius_px()))
    print("   Capture     : %s" % cfg.get("capture_backend", "auto"))
    print("   Merge       : %d px" % int(cfg.get("merge_distance", 0) or 0))
    print("   Accent      : %s%s" % (
        cfg.get("accent_color") or "off",
        "  [ONLY - other items ignored]"
        if cfg.get("accent_only") else ""))
    glide = int(cfg.get("glide_ms", 0) or 0)
    print("   Glide       : %s" % ("%d ms" % glide if glide > 0
                                   else "off (instant)"))
    print("   Follow      : %s" % (
        "ON (%.1fx boost, %ds memory)"
        % (float(cfg.get("follow_boost", 1.0)),
           int(cfg.get("follow_seconds", 20)))
        if cfg.get("follow_enabled") else "OFF"))
    print("")
    print("   STATE       : %s" % ("LAUNCHED" if app.running else "PAUSED"))
    print("")
    print("   Mouse behaviour")
    print("     Mode 2 guide:")
    print("       Your clicks are never eaten.")
    print("       After release, cursor moves onto the nearest clear item.")
    print("")
    print("     Mode 1 classic:")
    print("       If you click near an item, the mis-click is suppressed,")
    print("       cursor snaps to the item, and SnappyAI clicks it for you.")
    print("")
    print("   SHIFT + click : no assist for that click.")
    print("")
    print("   Always-available keys (rebindable: config.ini or GUI)")
    print("     %-14s launch" % str(cfg.get("key_launch", "ctrl+l")).lower())
    print("     %-14s pause" % str(cfg.get("key_pause", "ctrl+p")).lower())
    print("     %-14s record macro (start)"
          % str(cfg.get("key_record", "ctrl+alt+r")).lower())
    print("     %-14s record macro (stop + save)"
          % str(cfg.get("key_record_stop", "ctrl+alt+s")).lower())
    print("     %-14s play recording (selected/newest)"
          % str(cfg.get("key_play", "ctrl+alt+m")).lower())
    print("     %-14s play recording slots 1-5"
          % (str(cfg.get("key_play1", "ctrl+1")).lower() + "..."))
    print("")
    print("   Mode keys%s" % (
        " - single-key binds BLOCK typing system-wide!"
        if cfg.get("block_bound_keys")
        else " (fire everywhere, keys still type)"))
    print("     %-14s mode 1 classic" % effective_mode_key(cfg, 1))
    print("     %-14s mode 2 guide" % effective_mode_key(cfg, 2))
    print("")
    print("   Console commands")
    print("     s=status t=toggle h=help q=quit a=accent f=follow "
          "c=autoclick v=calibrate")
    print("=" * 70)
    print("")

def print_status(app):
    cfg = app.cfg

    print("-" * 70)
    print(
        " STATUS   mode: %s | radius: %d px | state: %s"
        % (
            cfg.get("mode"),
            app.radius_px(),
            "LAUNCHED" if app.running else "PAUSED",
        )
    )
    print(
        "          assisted: %d   |   normal/passed: %d"
        % (app.snap_count, app.pass_count)
    )
    mem = app.follow
    mem_txt = "no memory yet"
    if mem.when > 0:
        age = int(time.perf_counter() - mem.when)
        mem_txt = "last snap %ds ago (%d total)" % (age, mem.hits)
    print(
        "          follow: %s  |  %s"
        % ("ON" if cfg.get("follow_enabled") else "OFF", mem_txt)
    )
    print("-" * 70)

def print_help():
    print("-" * 70)
    print(" SNAPPYAI HELP")
    print("  - Start paused. Press Ctrl+L to launch assistance.")
    print("  - Press Ctrl+P to pause (rebindable). While paused,")
    print("    nothing is intercepted - macros and recorder included.")
    print("  - Ctrl+Alt+R starts the macro recorder: your keys are")
    print("    captured and still reach your apps; Ctrl+Alt+S saves")
    print("    into the library (GUI Macros tab: rename, per-recording")
    print("    repeat-until-stopped, export, import, delete).")
    print("  - Ctrl+Alt+M plays the selected (or newest) recording;")
    print("    Ctrl+1..Ctrl+5 play recordings #1..#5 by list position.")
    print("  - Hold SHIFT while clicking to bypass assistance once.")
    print("  - Mode 2 guide is safest: it never eats your clicks.")
    print("  - Mode 1 classic is stronger: it can suppress a mis-click and")
    print("    click the nearby item for you.")
    print("  - Settings reload from disk whenever you press Apply in")
    print("    the GUI (there is no reload hotkey anymore); quitting")
    print("    goes through the window's close button.")
    print("  - All hotkeys are rebindable (key_launch, key_pause, ...) in")
    print("    config.ini or the GUI's Hotkeys tab.")
    print("  - Single-key binds (1, 2, v ...) work in every app by")
    print("    default AND never block typing: the action fires and the")
    print("    key still reaches the focused app. block_bound_keys")
    print("    switches them to classic swallowing hotkeys.")
    print("  - follow_learn = accent: the follow memory only learns items")
    print("    matching accent_color, so a misclick that snapped elsewhere")
    print("    never retargets the memory away from your colour.")
    print("  - glide_ms animates cursor moves so you can follow them")
    print("    (0 = instant; moving your mouse cancels a glide).")
    print("  - accent_only (console 'a') restricts assistance to items")
    print("    containing your accent colour - 'click the blue thing' mode.")
    print("    Clicks where nothing matches pass through untouched.")
    print("  - follow memory (console 'f') remembers your last snapped item:")
    print("    for a few seconds, similar-looking or same-place items win")
    print("    ties - handy for scrollbars and repeated clicks on one")
    print("    control. It learns only from your own successful clicks.")
    print("  - auto-click (console 'c') clicks your colour by itself:")
    print("    the screen is scanned on its own and the best item in your")
    print("    accent colour is clicked, without you clicking anything.")
    print("    Needs accent_color set, never clicks while paused, and stops")
    print("    at its per-session limit.")
    print("  - calibrate (console 'v') measures your colour on THIS screen:")
    print("    point at the app you work in, press v, and it suggests the")
    print("    accent_soft value tuned to your display and lighting.")
    print("    Set it on the Handler tab ('Accept near-miss shades').")
    print("  - Detection adapts to your screen: dim regions lower their own")
    print("    ink bar (adaptive_threshold) and edges are scored relative to")
    print("    local brightness (luminance_norm), so dark themes work like")
    print("    light ones. Both default on; A/B test with the CLI flags")
    print("    --no-adaptive / --no-lumnorm.")
    print("  - Sign-in is online only (Discord, straight from the")
    print("    app); the Stripe")
    print("    subscription bound to that login is re-checked at every")
    print("    start - no reachable server, no engine.")
    print("  - exclude_color (Detection & Colours tab): items containing")
    print("    that colour are NEVER clickable - clicks on them pass")
    print("    straight through, in both modes. Exclusion outranks")
    print("    accent boosts.")
    print("  - motion_predict + motion_lead_ms (Detection & Colours):")
    print("    aim ahead of MOVING items (scrolling lists, video seek")
    print("    bars) by a measured speed+direction lead; standing")
    print("    items behave exactly as before.")
    print("  - motion_3d (Assistance tab): the same lead through a")
    print("    position-plus-size tracker - bad scans are ignored, turns")
    print("    are followed through, and a sudden size jump restarts the")
    print("    track. Same gates and cap; only the brains change.")
    print("  - Macros tab: five triggers that send a whole key combo")
    print("    instead of typing ('B means Ctrl+C'). One press = one")
    print("    combo press, and the trigger is always swallowed while")
    print("    launched, so D = Ctrl+D never leaks a bare D.")
    print("    Recorder: Ctrl+Alt+R capture, Ctrl+Alt+S stop and save,")
    print("    Ctrl+Alt+M play, Ctrl+1..5 play by list position. Each")
    print("    recording is named and carries its own playback style:")
    print("    play once, or repeat until stopped.")
    print("  - capture_backend, merge_distance, accent_color and friends can")
    print("    be tuned in config.ini / config.json; see the shipped example.")
    print("  - Settings are stored in config.json and optional config.ini.")
    print("-" * 70)


def _retry_prompt():
    try:
        ans = input("   Retry? [Y/n] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("")
        return False
    return ans not in ("n", "no", "q", "quit")


def _console_login(cfg):
    """Discord browser round trip. Returns the identity or None."""
    while True:
        print("")
        print("   Sign in with Discord (your browser opens; the tab")
        print("   returns to this app on its own).")
        try:
            identity, msg = online.login_with_provider(cfg, "discord")
        except online.OnlineError as exc:
            print("   Sign-in unreachable: %s" % exc)
            if not _retry_prompt():
                return None
            continue
        if identity:
            return identity
        print("   %s" % (msg or "No sign-in came back - try again."))


def _console_subscribe_loop(cfg, identity):
    """Subscription gate for the console. True = engine may start."""
    while True:
        try:
            identity, ent = online.me(cfg, fresh=True)
        except online.OnlineError as exc:
            print("   Auth server unreachable: %s" % exc)
            if not _retry_prompt():
                return False
            continue
        if identity is None:
            return False            # session vanished: sign in again
        print("   Status    : %s" % online.entitlement_summary(ent))
        if online.entitlement_active(ent) and not ent.get("shared"):
            return True
        if (ent or {}).get("shared"):
            print("")
            print("   This account is in use on ANOTHER computer right")
            print("   now. Snappy AI stays off while it is shared -")
            print("   close the other session, then re-check.")
            try:
                ans = input("   Enter re-checks, q quits: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("")
                return False
            if ans in ("q", "quit"):
                return False
            continue
        state = str((ent or {}).get("status", "unsubscribed"))
        print("")
        print("   Account   : %s" % online.identity_label(identity))
        print("   Subscrip. : %s - the engine stays off." % state)
        if state == "email_mismatch":
            print("   The payment was made with a different e-mail")
            print("   than your Discord account - subscribe again")
            print("   using the Discord e-mail shown above.")
        print("   Subscribe on Stripe (activation lands up to ~10 min")
        print("   after payment, or use 'I paid' in the GUI):")
        print("     monthly : %s"
              % online.subscribe_url(cfg, identity, "monthly"))
        if online.payment_link(cfg, "trial"):
            print("     trial   : %s"
                  % online.subscribe_url(cfg, identity, "trial"))
        try:
            ans = input("   Enter re-checks, q quits: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("")
            return False
        if ans in ("q", "quit"):
            return False


def console_gate(cfg):
    """
    Online sign-in + subscription gate for the console path (v8.22).

    Strict by design: the engine starts only with a live, positive
    answer from the signed entitlements file on GitHub - no live
    engine, not even the banner prints. Returns the identity label,
    or None when the session must not start.
    """
    print("")
    print("   %s - online sign-in" % APP_NAME)
    print("   (subscriptions are bound to your provider login)")
    while True:
        identity = None
        sess = online.load_session()
        if sess and sess.get("provider"):
            try:
                identity, ent = online.me(cfg, fresh=True)
            except online.OnlineError as exc:
                print("   Auth server unreachable: %s" % exc)
                if not _retry_prompt():
                    return None
                continue
            if identity is None:
                online.clear_session()
        if identity is None:
            identity = _console_login(cfg)
            if identity is None:
                return None
        else:
            if online.entitlement_active(ent) and not ent.get("shared"):
                return identity
        if not _console_subscribe_loop(cfg, identity):
            return None
        return identity


def windows_main(cfg, identity=None):
    app, hook_thread = start_app(cfg, identity)
    if app is None:
        return 1

    print_banner(app)

    if app.running:
        log("Ready. Assistance is LAUNCHED. Press Ctrl+P to pause.")
    else:
        log("Ready. Program is PAUSED. Press Ctrl+L to launch.")

    cmds = queue.Queue()

    def reader():
        try:
            for line in sys.stdin:
                cmds.put(line)
        except (OSError, ValueError):
            pass
        cmds.put(None)

    threading.Thread(target=reader, daemon=True).start()

    def shared_watch():
        """Netflix-style guard: if the signed file flags this identity
        as running in two places at once, pause and say why.

        Goes through online.row_shared(), so the confirmation window
        applies here too: the heartbeat endpoint is an open webhook, and a
        single sighting can be forged by anyone who knows the e-mail."""
        if not identity:
            return
        idh = online.row_hash(identity)
        legacy = online.row_hash_legacy(identity)
        while not app.stop.is_set():
            # fixed cadence (not a setting): this is sharing enforcement
            if app.stop.wait(max(1, online.presence_interval_seconds())):
                return
            try:
                rows, gen = online.fetch_entitlements(cfg)
            except online.OnlineError:
                continue
            # the publisher may still be keyed by the legacy hash
            key = idh if idh in rows else legacy
            shared = online.row_shared(rows, key, gen)
            if shared and app.running:
                app.toggle_running()
                log("ACCOUNT IN USE ELSEWHERE - assistance paused. "
                    "Snappy AI runs on one machine per account; close "
                    "the other session and launch again.")
            elif shared:
                log("ACCOUNT IN USE ELSEWHERE - staying paused.")

    threading.Thread(target=shared_watch, daemon=True,
                     name="shared-watch").start()

    try:
        while not app.stop.is_set():
            try:
                line = cmds.get(timeout=0.25)
            except queue.Empty:
                continue

            if line is None:
                break

            line = line.strip().lower()

            if not line:
                continue

            if line in ("q", "quit", "exit"):
                app.request_quit()
                break

            elif line in ("t", "toggle"):
                app.toggle_running()

            elif line in ("s", "status"):
                print_status(app)

            elif line in ("h", "help", "?"):
                print_help()

            elif line in ("a", "accent"):
                if not _parse_accents(cfg.get("accent_color")):
                    print("accent_color is off. Set it first (GUI Detection &")
                    print("Colours tab, or config.ini: accent_color = blue")
                    print("then press Apply in the GUI, and 'a' will work.")
                else:
                    new_state = not bool(cfg.get("accent_only"))
                    cfg.set("accent_only", new_state)
                    log("ACCENT-ONLY: %s (%s)"
                        % ("ON - only matching items are clickable"
                           if new_state
                           else "OFF - all items eligible",
                           cfg.get("accent_color")))

            elif line in ("f", "follow"):
                new_state = not bool(cfg.get("follow_enabled"))
                cfg.set("follow_enabled", new_state)
                log("FOLLOW MEMORY: %s (%.1fx boost for %ds after each snap)"
                    % ("ON" if new_state else "OFF",
                       float(cfg.get("follow_boost", 1.0)),
                       int(cfg.get("follow_seconds", 20))))

            elif line in ("c", "autoclick"):
                if not _parse_accents(cfg.get("accent_color")):
                    print("accent_color is off. Set it first (GUI Colors "
                          "tab, or config.ini: accent_color = blue), "
                          "then press Apply in the GUI.")
                    print("Auto-click needs a colour to aim at - without "
                          "one there is nothing safe to click.")
                else:
                    new_state = not bool(cfg.get("auto_click"))
                    cfg.set("auto_click", new_state)
                    if new_state:
                        app._auto_reset_session()
                    log("AUTO-CLICK: %s (clicks %s by itself every %.1fs, "
                        "limit %d per session)"
                        % ("ON" if new_state else "OFF",
                           cfg.get("accent_color"),
                           float(cfg.get("auto_click_interval", 2.0)),
                           int(cfg.get("auto_click_max_clicks", 10))))

            elif line in ("v", "calibrate"):
                accents = _parse_accents(cfg.get("accent_color"))
                if not accents:
                    print("accent_color is off - there is nothing to "
                          "calibrate. Set your colour first (GUI Colors "
                          "tab), point at the app you work in, and press "
                          "v again.")
                else:
                    # No prompt here: stdin belongs to the command
                    # reader thread, so this only reports - the value is
                    # applied on the Handler tab ('Accept near-miss
                    # shades') or in config.ini as accent_soft.
                    try:
                        from win32rt import get_cursor_pos
                        x, y = get_cursor_pos()
                        img, cx, cy, _o, _e = app.grab_around(
                            x, y, app.radius_px())
                    except Exception as exc:
                        print("Calibration capture failed: %r" % (exc,))
                        img = None
                    if img is None:
                        print("Calibration capture failed - nothing "
                              "grabbed around the cursor.")
                    else:
                        rep = calibrate_accent(
                            img, cx, cy, accents,
                            float(cfg.get("accent_tolerance", 26)),
                            accent_soft_of(cfg.values),
                            accent_matcher_of(cfg.values))
                        if rep is None:
                            print("Nothing measurable under the cursor.")
                        else:
                            print("Colour calibration (%d px sampled, "
                                  "unit %s):" % (rep["pixels"], rep["unit"]))
                            print("  median distance: %.2f   95th: %.2f"
                                  % (rep["p50"], rep["p95"]))
                            print("  strong matches now: %.0f%%"
                                  % (rep["strong_frac"] * 100.0))
                            print("  suggested accent_soft: %d (now %d)"
                                  % (rep["suggested_soft"],
                                     int(cfg.get("accent_soft", 60))))

            else:
                print("Unknown command '%s'. Type h for help, q to quit." % line)

    except KeyboardInterrupt:
        app.request_quit()

    hook_thread.join(timeout=2.0)

    print("")
    log(
        "Snappy AI stopped. Assisted %d clicks this session. Goodbye."
        % app.snap_count
    )

    return 0

# ------------------------------------------------------------------
# GUI (tkinter) - the default interface; --console keeps the old one
# ------------------------------------------------------------------

