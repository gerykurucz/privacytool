"""Settings: defaults, validation, JSON + INI storage, live reload,
import/export. Shared by every interface (GUI, console, tests)."""

import json
import os
import sys
import threading
from configparser import ConfigParser

import build_secrets
import i18n
from core import log
from colorspec import parse_accents

# User-facing return strings live in the catalog like everything else
# (v8.40); log lines stay English, they are support evidence.
i18n.publish("en", {
    "st.import_fail": "Import failed: %r",
    "st.import_notfile": "Import failed: not a settings file.",
    "st.imported": "Imported %d setting(s)%s.",
    "st.imported_ignored": ", ignored: %s",
})

DEFAULT_CONFIG = {
    # v8.27 GUI restructure - removed settings (old config.json keys
    # are ignored on load, ini overrides for them are dropped):
    #   assist_enabled / start_paused : assistance is ALWAYS available
    #       and the engine ALWAYS starts paused (Launch is the gate).
    #   feedback / announce_snaps     : the voice-feedback feature is
    #       gone entirely - no spoken announcements, no powershell
    #       speech child process.
    #   entitlement_check_minutes     : the runtime subscription
    #       re-check cadence is a built-in constant (30 min), not a
    #       user setting.
    #   accent_color2 / accent_boost2 : "Accent colour(s)" already
    #       accepts an unlimited ";"-separated list - one accent field.
    #   key_radius / key_feedback / key_reload / key_quit : those
    #       hotkeys are gone (config reload happens on Apply; quitting
    #       happens through the window close button).
    #   play_mode / play_repeat       : playback style is stored PER
    #       RECORDING ("loop" flag in macros.json), not globally.
    #   macroN_repeat / _period_ms / _once / _block : a macro is one
    #       blocked trigger -> exactly one combo press.

    # 1 = classic: suppress mis-click, snap, auto-click.
    # 2 = guide: never eat clicks, move cursor after release.
    "mode": 2,

    # Search radius in logical pixels.
    "radius": 150,

    # ------------------------------------------------------------------
    # v8.49: NOTHING deployment-related lives here any more.
    #
    # The entitlement repo/branch, both Stripe payment links, the OAuth
    # client credentials, the presence webhook and the row-hash pepper
    # are BUILD CONSTANTS in build_secrets.py, not settings. They used to
    # be keys in this dict, which meant Config.save() wrote the payment
    # links and the repo into config.json next to the exe in clear text -
    # readable by anyone with the folder, attached to every support
    # request, and copied out by Export Config into a file users were
    # told to share.
    #
    # They were never settings in any meaningful sense: repointing the
    # entitlement repo gains nothing because the Ed25519 public key is a
    # pinned build constant, and there is no scenario where a user wants
    # a different payment link. SENSITIVE_KEYS below is enforced by
    # save() and export_to() as a second layer, so a future key cannot
    # reach the disk by accident either.
    #
    # Old config.json files carrying these keys load fine - the keys are
    # dropped (see _load) and the build constants are used instead.
    # ------------------------------------------------------------------

    # Interface theme: "light" or "dark". Toggle on the login screen or
    # in the app header; persisted like every other setting.
    "theme": "light",

    # After a successful snap, quick repeat clicks near the same place
    # may be treated as double-click assistance in classic mode.
    "watcher_seconds": 0.45,

    # If capture/scan stalls, pause assistance briefly.
    "stall_pause_seconds": 0.25,

    # Advanced image-analysis tuning.
    "contrast_threshold": 38,
    "min_contrast": 48,
    "min_area": 220,
    "max_area": 45000,
    "max_dim": 300,
    "on_target_dist": 10,

    # Detection adaptivity:
    # adaptive_threshold lets inherently dim regions (dark themes,
    # washed-out documents) lower their own ink bar; luminance_norm
    # scores edges relative to local brightness so dark-mode items rank
    # like their light-mode equivalents. Both default on; mid-grey
    # content behaves exactly as before.
    "adaptive_threshold": True,
    "luminance_norm": True,

    # Screen capture backend.
    # "auto"  = mss (GDI) first - it sees every ordinary window,
    #           including games and hardware-accelerated apps that
    #           Desktop Duplication cannot observe. (v8.52: auto used
    #           to prefer dxcam; stale/black frames in live tests were
    #           the result.)
    # "dxcam" = force Desktop Duplication - fastest grabs, but blind to
    #           some game/fullscreen swapchains; mss stays as fallback.
    # "mss"   / "wgc" = force GDI / Windows.Graphics.Capture.
    "capture_backend": "auto",

    # Click DELIVERY backend (v8.50). Opt-in secondary option:
    # "win32" (default) injects through SendInput - no driver, works
    # out of the box, and our own hooks recognise the events as
    # injected so assistance never feeds itself.
    # "interception" delivers clicks at the DRIVER level through the
    # Interception library (github.com/oblitum/Interception) for the
    # minority of games and Raw-Input apps that ignore synthetic
    # events. It needs interception.dll beside the app AND the signed
    # kernel driver installed (interception.exe install, then reboot).
    # If either is missing the app says so once and keeps working
    # through the standard Windows method - a half-installed setup can
    # never eat a click. Applies on restart.
    "input_backend": "win32",

    # Detected pieces whose bounding boxes are within this many pixels of
    # each other are merged into a single item. This rescues broken
    # outlines, icon + label pairs, and fragments that are individually
    # smaller than min_area. 0 disables merging.
    "merge_distance": 18,

    # Accent colour priority. "off", one colour ("r,g,b" 0-255, or a
    # preset name: red, orange, yellow, green, cyan, blue, purple, pink,
    # grey, white, black), or several separated by ";" - for example
    # "blue; red" or "60,120,220; 200,60,60". Items containing pixels
    # near ANY accent get a scoring boost proportional to how much of
    # the item matches, so "the one with more blue in it" wins ties.
    # This never excludes other items; it only breaks ties in your
    # favour.
    "accent_color": "off",
    "accent_tolerance": 26,

    # Smart colour matching (0-100). Above 0, near-miss shades of the
    # accent earn graded partial credit instead of scoring zero:
    # lighter/darker, washed-out or slightly hue-shifted variants are
    # preferred like the real colour (weaker, proportionally), and a
    # colour with the same brightness AND vividness but a different
    # hue still earns ~10-20% "looks related" credit. Ranking only -
    # accent_only exclusion and follow-memory learning still require a
    # real match. 0 = classic exact tolerance box.
    "accent_soft": 60,

    # Smart matcher engine, used while accent_soft > 0 (at 0 both use
    # the classic exact tolerance box):
    # "oklab" = perceptual matching (recommended). Colours are compared
    #   in OKLab, a perceptually uniform colour space: ranking follows
    #   how different colours actually LOOK. Fixes the classic scorer's
    #   hue false positives (a saturated green can no longer ride a
    #   blue accent's tolerance) and rescues anti-aliased accent-
    #   coloured glyph/icon edges on any background via a blend-line
    #   test. Also ~1.5-2x faster per scanned item.
    # "hsv" = the v8.13 weighted-HSV smart matcher (kept for A/B
    #   comparison in the field).
    "accent_matcher": "oklab",

    "accent_boost": 0.9,

    # Hard-excluded colours ("never clickable"). Same syntax as
    # accent_color (preset name, "r,g,b", ";" list). Items with a REAL
    # match (strict gate: >= 5% of pixels at similarity >= 0.55) are
    # dropped from assistance entirely - clicks on them pass straight
    # through to Windows, in both modes. Exclusion outranks every
    # accent boost; soft partial credit can never keep an excluded
    # item clickable. "off" disables.
    "exclude_color": "off",

    # Motion lead ("smart follower"): for MOVING items (scrolling
    # lists, video seek bars) the engine measures the chosen target's
    # speed and direction across consecutive scans and aims ahead by
    # this many milliseconds of that travel, so the click lands on the
    # item instead of where it was. The offset is capped (80 px), and
    # standing, slow or direction-changing histories get no lead at
    # all - stationary items behave exactly as before.
    "motion_predict": False,
    "motion_lead_ms": 50,

    # Watch the screen centre only: when true, every scan is anchored
    # at the middle of the virtual screen instead of under the cursor -
    # for fixed-position layouts (kiosks, TV guides, one app filling the
    # window) where the items never move. The search radius stays as set
    # on Advanced; a click far outside that area simply passes through
    # unassisted, like any empty space. Off = the classic cursor-anchored
    # behaviour, bit-for-bit.
    "watch_center_only": False,

    # "Keep the cursor on it" (centre-watch follow). Only ever acts while
    # watch_center_only is ON: after an item inside the watched square
    # was picked (a click that snapped to it, or resting the cursor on
    # it for ~0.3 s), the cursor stays parked on that item and chases it
    # while it moves - scroll planes, animated panels, moving targets.
    # It never fights the user: any held button or active follow-lock
    # pauses it, and it dies ~1 s after the item stops being sighted.
    # Combine with "Lead moving items" for smooth fast chasing.
    "center_follow": False,

    # Colour-stage scan budget in milliseconds (vision.scan_region).
    # Items whose colour could not be checked before this deadline fail
    # closed for accent_only/exclude_color and are reported in the log.
    # 350 ms is generous enough that a radius-400 busy screen finishes
    # scoring; lower it (min 60) if scans ever feel late on slow machines.
    "scan_budget_ms": 350,

    # 3D snap follower: track position AND scale with a Kalman filter
    # instead of the legacy linear fit. Outliers are rejected per scan
    # (one bad frame damps the step instead of blinding the track),
    # direction changes are followed through in two or three scans,
    # and a sudden scale jump restarts the track (different item, not
    # growth). Same gates, same cap - only the brains change. Needs
    # motion_predict on; off keeps the legacy engine bit-for-bit.
    "motion_3d": False,

    # Colour-exclusive targeting ("click the blue thing" mode). When
    # true, ONLY items containing the accent colour are eligible for
    # assistance; clicks where nothing matches pass through untouched
    # (mode 1 returns the suppressed click safely). Still cursor-
    # relative and click-driven: SnappyAI never clicks on its own.
    # Ignored with a warning while accent_color is off. Console
    # command "a" toggles this at runtime.
    "accent_only": False,

    # Auto-click ("click the buttons for me"): the ONLY feature that
    # acts without a user gesture - turning this switch ON is itself the
    # request (the mouse1 equivalent). The engine scans the middle of the
    # screen every auto_click_interval (default 100 ms) for the best item
    # and clicks it: with an accent colour set, only items carrying that
    # colour qualify; without one, the highest-contrast item in the centre
    # square qualifies, held to the stricter auto_click_min_contrast gate.
    #
    # SAFETY IS STRUCTURAL, not advisory:
    #   * colour-free mode clicks ONLY crisp, clearly drawn items (the
    #     min_contrast gate above), never blurry background noise;
    #   * exclude_color still wins: a colour on the never-click list
    #     removes the item from the scan entirely;
    #   * it never clicks inside Snappy AI's own windows;
    #   * it never clicks while PAUSED - Launch is still the only gate;
    #   * max clicks per session, a repeat guard on the same spot and a
    #     settle delay cap how fast it can act.
    "auto_click": False,

    # Seconds between automatic scans. The default is 100 ms: the loop
    # re-scans the centre square ten times a second and fires at the
    # first qualifying item (repeat guard + settle below still pace it).
    "auto_click_interval": 0.1,

    # Contrast gate for an auto-click target, on the same scale as
    # min_contrast. This is what makes colour-free auto-clicking safe:
    # with no accent colour set, ONLY items this crisp are eligible.
    # Raise it and only strong, crisp items qualify.
    "auto_click_min_contrast": 60,

    # Safety cap: automatic clicks per launched session. The engine stops
    # auto-clicking (and says so) once the cap is reached.
    "auto_click_max_clicks": 10,

    # How long the cursor rests on the target before the click lands, so a
    # hover/pressed state under the pointer is visible to the app first.
    "auto_click_settle_ms": 120,

    # Do not click the same spot again while it stays on screen - the
    # scan-after-click cooldown. Without it a button that does not change
    # on activation would be clicked over and over.
    "auto_click_repeat_px": 60,

    # Search radius around the centre of the screen, in logical pixels.
    "auto_click_radius": 200,

    # Follow memory ("colour following"): after a successful snap, the
    # item's colour and position are remembered for follow_seconds;
    # similar-looking or same-place items then get a scoring boost, so
    # repeated work on one control (a scrollbar thumb, a dialog button)
    # keeps snapping to it. Learned only from YOUR successful clicks,
    # decays over time, never clicks on its own. Console "f" toggles.
    "follow_enabled": False,
    "follow_boost": 1.0,
    "follow_seconds": 20,

    # Cursor glide: 0 = instant snap (default, lowest latency).
    # 40-120 animates the cursor move over that many milliseconds so you
    # can follow where it went. Moving the mouse physically aborts a
    # glide immediately; in classic mode your click is then delivered
    # wherever the cursor ended up, never swallowed.
    "glide_ms": 0,

    # Snap point offset, in logical pixels. The engine normally aims at
    # the middle of the item; these move that point - positive X goes
    # right, positive Y goes down (negative values go left/up). For a
    # control whose middle is dead (a split button, a slider track, an
    # icon whose clickable corner sits off-centre), dial the click onto
    # the live spot once instead of fighting every snap. Applies to
    # classic snaps, guide moves and auto-clicks alike.
    "snap_offset_x": 0,
    "snap_offset_y": 0,

    # Round-2 colour handling (see vision.py). All three default on:
    # they only ever make matching stricter about the RIGHT things
    # (lighting casts, shade states, speckle noise), never looser about
    # hues - a wrong hue still cannot win. Turn one off only to A/B a
    # misbehaving screen against the older behaviour.
    #
    # color_adapt: white-balance each item against its own background
    # before matching, so night light and theme casts stop shifting
    # your colour out of tolerance.
    "color_adapt": True,
    # accent_variants: also test brighter/dimmer copies of your colour,
    # so hover, pressed and dimmed states match without widening the
    # hue tolerance.
    "accent_variants": True,
    # accent_coherent: accent-coloured pixels must connect into a blob
    # to count - scattered dither/compression specks never qualify an
    # item, boost it, or exclude it.
    "accent_coherent": True,

    # v8.39: the product ships silent and sightless by design;
    # diagnostics live in the log bus instead.

    # Interface language (i18n.codes()). Switched live from the
    # Language button in the footer; persisted like every setting.
    "language": "en",

    # Input behaviour.
    # block_bound_keys = false (default): modifier-less bindings like
    # "1" or "v" work SYSTEM-WIDE through a pass-through keyboard hook:
    # the action fires in every app AND the key still reaches the
    # focused app, so typing is never blocked. Note: typing that key
    # mid-sentence also fires its action - that is the trade-off.
    # true: classic hotkey behaviour - single-key bindings fire
    # everywhere but swallow those keys while typing.
    "block_bound_keys": False,

    # Hold-to-follow: while the left button is held right after a snap
    # (or re-pressed on the remembered item), the cursor keeps following
    # that item's colour - stabilises drags like scrollbar thumbs.
    # Released automatically on button-up; never clicks on its own.
    "hold_follow": True,

    # Rapid-click snapping (LEFT button only). Off (default): while a
    # snap is still being processed, further left clicks pass straight
    # through to Windows - only the first click of a burst is assisted.
    # On: EVERY left click is assisted, so continuous clicking or
    # double-clicking constantly snaps to icons/colours instead of
    # leaking unassisted clicks (Mode 1; Mode 2 already assists every
    # click). Never affects the right button - it has its own
    # mouse2_action / mouse2_hold_action settings below.
    "rapid_click_snap": False,

    # Programmable RIGHT-button side action (the right button itself
    # ALWAYS keeps its normal Windows function - we only react
    # alongside, never suppress it):
    # 1 = clear the current follow task, 2 = follow the last snapped
    # item's colour, 3 = 2 s colour pick then follow it, 4 = nothing.
    # Timing: fires on button-DOWN while mouse2_hold_action is 4
    # (classic behaviour); once a hold action is configured, a short
    # press fires this on button-UP instead, so click and hold can be
    # told apart.
    "mouse2_action": 4,

    # Same choices as mouse2_action (1 = clear the current follow
    # task, 2 = follow the last snapped item's colour, 3 = 2 s colour
    # pick then follow it, 4 = nothing), but fired when the right
    # button is kept HELD for ~0.45 s instead of clicked. A press is
    # either a click or a hold, never both. 4 (default) = nothing -
    # with that, mouse2_action keeps its classic press-time behaviour
    # unchanged. The right button itself always keeps its normal
    # Windows function.
    "mouse2_hold_action": 4,

    # What the follow memory is allowed to learn:
    # "accent" = only items matching accent_color (a misclick that snaps
    #            to some other item does NOT poison the memory);
    # "any"    = every successful snap (old behaviour).
    # With accent_color off, "accent" behaves like "any".
    "follow_learn": "accent",

    # Key bindings. Format: "ctrl+alt+s", "f5", "space", "1", ...
    # Modifiers: ctrl, alt, shift, win. Applied on GUI save (Apply).
    # v8.27: the radius / feedback / reload / quit hotkeys are gone;
    # the remaining map is launch, pause, the two mode keys, the
    # recorder pair and the playback keys.
    "key_launch": "ctrl+l",
    "key_pause": "ctrl+p",
    "key_mode1": "1",
    "key_mode2": "2",
    "key_record": "ctrl+alt+r",
    "key_record_stop": "ctrl+alt+s",
    "key_play": "ctrl+alt+m",
    "key_play1": "ctrl+1",
    "key_play2": "ctrl+2",
    "key_play3": "ctrl+3",
    "key_play4": "ctrl+4",
    "key_play5": "ctrl+5",

    # Macros (GUI Macros tab, v8.27): five slots of TWO settings each -
    # trigger spec and the combo sent per press. One blocked trigger
    # press injects exactly one combo press while launched ("B means
    # Ctrl+C" - the focused app never sees the bare trigger); paused,
    # the keyboard is entirely yours. Empty trigger or action = off.
    "macro1_key": "",       "macro1_action": "",
    "macro2_key": "",       "macro2_action": "",
    "macro3_key": "",       "macro3_action": "",
    "macro4_key": "",       "macro4_action": "",
    "macro5_key": "",       "macro5_action": "",

    # Recording playback (v8.27) has no global transport settings:
    # each recording in macros.json carries its own "loop" flag
    # (play once / repeat until stopped), set in the Macros tab.

    "config_version": 8,
}

RADIUS_STEPS = [(80, "small"), (150, "medium"), (250, "large")]


def config_dir():
    """
    Store config next to the script if writable.
    Otherwise use AppData on Windows or home directory elsewhere.
    """
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    try:
        probe = os.path.join(base, ".snappyai_write_test")
        with open(probe, "w", encoding="utf-8") as fh:
            fh.write("x")
        os.remove(probe)
        return base
    except OSError:
        appdata = os.environ.get("APPDATA")
        if appdata:
            d = os.path.join(appdata, "SnappyAI")
        else:
            d = os.path.join(os.path.expanduser("~"), ".snappyai")
        try:
            os.makedirs(d, exist_ok=True)
        except OSError:
            pass
        return d


class SafeConfigReader:
    """
    Reads only safe accessibility keys from an optional config.ini.

    Example config.ini:

        [accessibility]
        mode = 1
        radius = 250
        accent_color = blue
    """

    def __init__(self, path):
        self.path = path

    def read_overrides(self):
        overrides = {}
        bad = []
        if not os.path.exists(self.path):
            return overrides

        parser = ConfigParser(strict=False)
        parser.optionxform = str

        try:
            parser.read(self.path, encoding="utf-8")
        except Exception:
            return overrides

        # v8.49: "DEFAULT" was listed here, but
        # ConfigParser.has_section("DEFAULT") is ALWAYS False - the defaults
        # pseudo-section is not a section in configparser's API - so that
        # entry was unreachable and a config.ini holding ONLY [DEFAULT] was
        # silently ignored. Defaults are now read explicitly, and they still
        # work as a fallback for the real sections (has_option/get already
        # consult them, which is why [accessibility] + [DEFAULT] appeared to
        # work while [DEFAULT] alone did not).
        sections = [s for s in ("accessibility", "snappyai")
                    if parser.has_section(s)]

        def _collect(section, has_option, getter):
            for key, default in DEFAULT_CONFIG.items():
                if key in build_secrets.SENSITIVE_KEYS:
                    continue        # never read from a file next to the exe
                if not has_option(key):
                    continue
                raw = getter(key)
                try:
                    overrides[key] = self._convert(raw, default)
                except Exception:
                    bad.append((section, key, raw))

        for section in sections:
            _collect(section,
                   lambda k, s=section: parser.has_option(s, k),
                   lambda k, s=section: parser.get(s, k))

        defaults = parser.defaults()
        if defaults:
            _collect("DEFAULT",
                     lambda k: k in defaults,
                     lambda k: defaults[k])

        for section, key, raw in bad:
            log("config.ini: ignored invalid %s in [%s]: %r"
                % (key, section, raw))

        return overrides

    @staticmethod
    def _convert(raw, default):
        raw = raw.strip()

        if isinstance(default, bool):
            return raw.lower() in ("1", "true", "yes", "on")

        if isinstance(default, int):
            # v8.67: round instead of truncate (150.7 -> 151, not 150)
            # and warn on a fractional hand edit instead of silently
            # misbehaving - the file's own philosophy.
            val = float(raw)
            rounded = int(round(val))
            if rounded != val:
                log("Config value %r is not an integer; rounded to "
                    "%d." % (raw, rounded))
            return rounded

        if isinstance(default, float):
            return float(raw)

        return raw


def _coerce_value(raw, default):
    """
    Validate and convert one config value against its default's type.

    Returns (ok, value). Bad values are rejected with a warning by the
    caller instead of crashing or silently keeping garbage - a hand-
    edited config file must never take the tool down.
    """
    try:
        if isinstance(default, bool):
            if isinstance(raw, bool):
                return True, raw
            if isinstance(raw, str):
                return True, raw.strip().lower() in ("1", "true", "yes", "on")
            if isinstance(raw, (int, float)):
                return True, bool(raw)
            return False, None

        if isinstance(default, int):
            if isinstance(raw, bool):
                return False, None
            if isinstance(raw, int):
                return True, raw
            if isinstance(raw, float):
                return True, int(raw)
            if isinstance(raw, str):
                return True, int(float(raw.strip()))
            return False, None

        if isinstance(default, float):
            if isinstance(raw, bool):
                return False, None
            if isinstance(raw, (int, float)):
                return True, float(raw)
            if isinstance(raw, str):
                return True, float(raw.strip())
            return False, None

        # String-valued keys (mode names, feedback, accent colour, ...).
        if isinstance(raw, str):
            return True, raw
        if isinstance(raw, (list, tuple)):
            # accent_color also accepts [r, g, b] from hand-edited JSON.
            return True, raw
        return False, None
    except (ValueError, TypeError, OverflowError):
        # OverflowError: hand-edited "1e999" -> float inf -> int() would
        # raise; a bad value must warn and fall back, never crash.
        return False, None



class Config:
    def __init__(self):
        self.lock = threading.Lock()
        self.dir = config_dir()
        self.path = os.path.join(self.dir, "config.json")
        self.ini_path = os.path.join(self.dir, "config.ini")
        self.values = dict(DEFAULT_CONFIG)
        self._load()

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                data = json.load(fh)

            if isinstance(data, dict):
                for key in DEFAULT_CONFIG:
                    if key in data:
                        ok, value = _coerce_value(data[key],
                                                  DEFAULT_CONFIG[key])
                        if ok:
                            self.values[key] = value
                        else:
                            log("config.json: ignored invalid %s = %r"
                                % (key, data[key]))

                # v8.49 and older carried the deployment constants as
                # settings. They are build constants now; drop whatever a
                # previous version left behind so an upgraded config.json
                # stops carrying payment links and the repo.
                stale = [k for k in build_secrets.SENSITIVE_KEYS
                         if k in data]
                if stale:
                    for k in stale:
                        self.values.pop(k, None)
                    log("config.json: removed %d deployment key(s) left by "
                        "an older version (%s); these now come from the "
                        "build, not from settings."
                        % (len(stale), ", ".join(sorted(stale))))
                    try:
                        self.save()
                    except Exception:
                        pass

                # v8.4 and older called this bare_mode_keys.
                if data.get("bare_mode_keys") in (True, "true", "1", 1):
                    self.values["block_bound_keys"] = True

                # v8.16 and older had a sixth combo-macro slot; v8.17
                # replaced it with the recording library (macros.json).
                if str(data.get("macro6_key") or "").strip() \
                        or str(data.get("macro6_action") or "").strip():
                    log("config: macro6 was removed in v8.17 (five combo "
                        "slots + recordings); its value was dropped - "
                        "re-create it as a recording or in slots 1-5.")

                try:
                    version = int(data.get("config_version", 1))
                except Exception:
                    version = 1

                if version < 8:
                    # v8.27: the old migrations used to force
                    # feedback/start_paused values - both keys are gone
                    # (feedback removed, start-paused is now the fixed
                    # behaviour), so migration is just the version bump.
                    self.values["config_version"] = 8
                    self.save()
        except (OSError, ValueError):
            pass

        try:
            overrides = SafeConfigReader(self.ini_path).read_overrides()
            if overrides:
                self.values.update(overrides)
        except Exception:
            pass

        self._sanitize()

    # Sane bounds for numeric settings, clamped with a warning instead of
    # crashing or silently misbehaving (idea from validated config
    # readers: bad numbers should never take the tool down).
    _RANGES = {
        "radius": (40, 400),
        # Detection gates had no bounds at all: a hand-edited
        # max_dim = -5 silently blinded the whole engine (every item
        # fails a negative cap), and similarly degenerate values
        # elsewhere. Same clamp-with-warning philosophy as the rest -
        # in-range configs behave bit-for-bit as before.
        "contrast_threshold": (1, 200),
        "min_contrast": (1, 200),
        "min_area": (1, 100000),
        "max_area": (100, 1000000),
        "max_dim": (10, 2000),
        "merge_distance": (0, 64),
        "accent_tolerance": (4, 90),
        "accent_soft": (0, 100),
        "accent_boost": (0.0, 3.0),
        "follow_boost": (0.0, 3.0),
        "follow_seconds": (1, 120),
        "glide_ms": (0, 500),
        "watcher_seconds": (0.0, 3.0),
        "stall_pause_seconds": (0.0, 3.0),
        "on_target_dist": (0, 100),
        "motion_lead_ms": (0, 300),
        # Colour-stage scan budget. The old hard-coded 120 ms deadline
        # cut the colour scoring short on busy screens ("Colour stage
        # cut short" log spam) so accent_only/exclude_color items failed
        # closed - visible especially with auto-click's wide multi-accent
        # lists and radius 400. Raising it only lets more items get
        # scored; clicks never wait longer than the scan actually takes.
        "scan_budget_ms": (60, 2000),
        # The snap offset is deliberately bounded: it re-aims the click
        # within the neighbourhood of the item, it must never be able to
        # send a click across the screen on its own.
        "snap_offset_x": (-200, 200),
        "snap_offset_y": (-200, 200),
        # Auto-click bounds. The floors/ceilings here are SAFETY limits,
        # not taste: the interval may now go down to 100 ms (the user's
        # requested cadence) but never below it, and an unbounded cap
        # would turn a misconfigured setup into runaway input.
        "auto_click_interval": (0.1, 60.0),
        "auto_click_min_contrast": (20, 150),
        "auto_click_max_clicks": (1, 200),
        "auto_click_settle_ms": (0, 2000),
        "auto_click_repeat_px": (0, 400),
        "auto_click_radius": (40, 600),
    }

    def sanitize(self):
        """Public name for _sanitize(): main.py and gui.py both call it
        from outside the class, and a leading underscore on the one
        validation entry point invited exactly that."""
        return self._sanitize()

    def _sanitize(self):
        for key, (lo, hi) in self._RANGES.items():
            try:
                value = self.values[key]
                clamped = type(lo)(min(hi, max(lo, value)))
                if clamped != value:
                    log("config: %s %r clamped to %r" % (key, value, clamped))
                self.values[key] = clamped
            except (KeyError, TypeError, ValueError):
                # Fall back to the default. Guarded: a _RANGES entry for a
                # key that is no longer in DEFAULT_CONFIG (a retired
                # setting) must not turn validation itself into a crash.
                if key in DEFAULT_CONFIG:
                    self.values[key] = DEFAULT_CONFIG[key]
                else:
                    self.values.pop(key, None)

        # String-valued keys with a fixed vocabulary: a typo must never
        # silently disable a feature (an unknown capture_backend used to
        # degrade to "always mss", an unknown accent_matcher to a guess).
        _CHOICES = {
            "accent_matcher": ("hsv", "oklab"),
            "capture_backend": ("auto", "dxcam", "mss", "wgc"),
            "input_backend": ("win32", "interception"),
        }
        for key, allowed in _CHOICES.items():
            raw = self.values.get(key, DEFAULT_CONFIG[key])
            value = str(raw).strip().lower() if raw is not None else ""
            if value not in allowed:
                log("config: %s %r unknown; using %r"
                    % (key, raw, DEFAULT_CONFIG[key]))
                value = DEFAULT_CONFIG[key]
            self.values[key] = value

        # accent_only / auto_click without an accent colour: the ENGINE
        # already degrades gracefully (scan_region forces the accent
        # gate off when no colour parses; the auto-click worker refuses
        # to arm and says why), so the stored values are left alone and
        # only a warning is logged. Forcing them off here would destroy
        # user intent - clearing the colour to try something, then
        # setting it back, must restore the previous behaviour without
        # re-flipping switches. No setting rewrites another setting.
        if self.values.get("accent_only") \
                and not parse_accents(self.values.get("accent_color")):
            log("config: accent_only is on but accent_color is off - "
                "it stays on and simply does nothing until a colour "
                "is set again.")

        if self.values.get("auto_click") \
                and not parse_accents(self.values.get("accent_color")):
            log("config: auto_click is on with no accent colour - it "
                "will click the highest-contrast item in the centre "
                "square instead (raise auto_click_min_contrast if it "
                "picks too eagerly).")

        if str(self.values.get("follow_learn", "accent")).lower() \
                not in ("accent", "any"):
            log("config: follow_learn %r invalid; using 'accent'"
                % (self.values.get("follow_learn"),))
            self.values["follow_learn"] = "accent"

        if str(self.values.get("theme", "light")).lower() \
                not in ("light", "dark"):
            self.values["theme"] = "light"

        # An unknown language code (hand-edited file, a locale removed
        # in a newer build) must fall back, never show raw keys.
        lang = str(self.values.get("language", "en")).strip().lower()
        self.values["language"] = lang if lang in i18n.codes() else "en"

        # Right-button click AND hold actions share one vocabulary.
        for key in ("mouse2_action", "mouse2_hold_action"):
            try:
                m2 = int(self.values.get(key, 4))
            except (TypeError, ValueError):
                m2 = 4
            if m2 not in (1, 2, 3, 4):
                log("config: %s %r invalid; using 4 (nothing)"
                    % (key, self.values.get(key)))
                m2 = 4
            self.values[key] = m2

    def export_to(self, path):
        """Write the current settings to a shareable JSON file.

        Export is the one path that puts this data somewhere the user
        will deliberately hand to another person, so it goes through the
        same SENSITIVE_KEYS filter as save() - an exported settings file
        must be safe to e-mail."""
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(self._public_values(), fh, indent=2)
            return True, i18n.L("st.exported", path)
        except OSError as exc:
            return False, i18n.L("st.export_fail", exc)

    def import_from(self, path):
        """
        Load settings from an exported JSON file. Every value is
        validated and coerced against the defaults; unknown or invalid
        keys are ignored with a warning. Changes stay in memory until
        the caller saves.
        """
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError) as exc:
            return False, i18n.L("st.import_fail", exc)

        if not isinstance(data, dict):
            return False, i18n.L("st.import_notfile")

        applied = 0
        skipped = []

        with self.lock:
            for key in DEFAULT_CONFIG:
                if key == "config_version" or key not in data:
                    continue
                if key in build_secrets.SENSITIVE_KEYS:
                    skipped.append(key)      # never re-imported from a file
                    continue
                ok, value = _coerce_value(data[key], DEFAULT_CONFIG[key])
                if ok:
                    self.values[key] = value
                    applied += 1
                else:
                    skipped.append(key)
            self._sanitize()

        if skipped:
            log("import: ignored invalid %s" % ", ".join(skipped))

        return True, i18n.L(
            "st.imported", applied,
            "" if not skipped else i18n.L(
                "st.imported_ignored", ", ".join(skipped)))

    def reload(self):
        """
        Re-read config.json and config.ini from disk while running.
        Runtime state (like mode switched via bare keys) is preserved
        only if it was saved; values from CLI flags are session-only and
        revert to what the files say.
        """
        with self.lock:
            self.values = dict(DEFAULT_CONFIG)
            self._load()

    def _public_values(self, values=None):
        """The settings that may be written to disk or exported.

        Deployment constants (build_secrets) are filtered out here as a
        second layer: they are no longer in DEFAULT_CONFIG, so nothing
        should ever put one into self.values - but save() and export_to()
        are the two ways data leaves the process, and a credential in
        either is exactly the leak this guard exists to make impossible.
        Anything stripped is logged once, because it means a caller set a
        key it should not have."""
        src = self.values if values is None else values
        out = {}
        dropped = []
        for key, value in src.items():
            if key in build_secrets.SENSITIVE_KEYS:
                dropped.append(key)
                continue
            out[key] = value
        if dropped and not self._leak_warned:
            type(self)._leak_warned = True
            log("config: refused to persist %s - deployment constants live "
                "in build_secrets.py, never in config.json."
                % ", ".join(sorted(dropped)))
        return out

    _leak_warned = False

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as fh:
                json.dump(self._public_values(), fh, indent=2)
        except OSError:
            pass

    def get(self, key, default=None):
        return self.values.get(key, default)

    def set(self, key, value, save=True):
        """Store one setting, clamped like a value read from disk.

        Clamping here (not only in _sanitize) closes a real hole: the
        console commands and the GUI pill switches all go through set()
        with save=True, so before this an out-of-range value reached
        config.json and the engine untouched until the next reload."""
        if key in build_secrets.SENSITIVE_KEYS:
            log("config.set(%r) ignored - that is a build constant, not a "
                "setting." % (key,))
            return
        with self.lock:
            bounds = self._RANGES.get(key)
            if bounds is not None:
                try:
                    lo, hi = bounds
                    value = type(lo)(min(hi, max(lo, value)))
                except (TypeError, ValueError):
                    pass                     # _sanitize() will fall back
            self.values[key] = value
            if save:
                self.save()

    def cycle(self, key, steps):
        current = self.get(key)
        values = [v for v, _ in steps]

        if current in values:
            idx = values.index(current)
        else:
            idx = -1

        idx = (idx + 1) % len(steps)
        value, label = steps[idx]
        self.set(key, value)
        return value, label


