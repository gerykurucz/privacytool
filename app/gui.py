"""Snappy AI - default graphical interface.

Flow: sign-in window (OAuth: Discord only, straight from the app)
-> subscription gate (Stripe entitlement, signed on GitHub) -> main
window. Visual contract:

  * rounded corners on every button (PIL-drawn PNG masks; plain flat
    buttons as fallback when Pillow is missing)
  * no focus rings, no press flash on any button
  * live light/dark switching in the SAME window: one shared palette
    dict + a tree-walk restyle (every widget carries a theme role)
  * the window title bar follows the theme too (DWM on Windows 10/11)
  * header: a card flush with the client-area top (v8.29) with the
    usual 10 px side gutters (v8.30) and a FIXED height (v8.31 made
    it 64 px, 20 px shorter than v8.30; v8.32 gave 10 px back for the
    raised identity stack) carrying a bigger logo plus a two-line
    stack - the title and a "build <version>" stamp in the seat the
    e-mail used to occupy (v8.34) - sitting 4 px above the logo's
    centring remainder (v8.33), with the mark keeping its exact seat,
    and the [theme switch] [Log Out] | [Pause] [Launch] cluster
  * status bar (v8.34): one row, two anchors. Left = the live counters
    ("Assisted N | passed N | theme: X"); right = "Registered to:
    <e-mail>    Status: <licence>", which is where the header's e-mail
    and licence lines moved to. Both in F_DESC on status_bg, and the
    right-hand line refreshes on every 30-minute entitlement re-check
  * custom tab bar (selected tab bigger), single-column settings,
    hover descriptions in one bar, Apply appears only when dirty
  * v8.38 tabs: eight of them, wrapping onto as many rows as the
    window width needs. v8.39 renamed and regrouped them: Colors
    (the two colour lists + Current RGB Value as full-width rows with
    their values on the RIGHT like every other tab - the lists as
    colour boxes, the RGB row as three channel-glow boxes - then the
    picker bottom-left with its controls on the right edge, v8.43),
    Handler (contrast + item-size
    gates + accent strictness), Experimental (every dropdown, derived
    from META's kinds), Help (read-only scrollable tuning guide)
  * v8.39 localisation: every visible string goes through i18n.L and
    re-registers a re-text closure, so the Language button (footer,
    beside Export Config) switches the whole interface live; the
    chooser lists native names with measured coverage and partial
    catalogs fall back key-by-key to English
  * v8.39: the Apply button lives in the description bar's row, flush
    right, opposite the text it commits - not in the footer beside the
    running/standby light
  * Assistance tab (v8.37): every on/off setting is a PILL SWITCH in
    the Light/Dark switch's own geometry - knob on the RIGHT and the
    track filled with the logo's red when the setting is on, knob left
    on the neutral track when it is off - with a small On/Off word
    beside it, because colour alone is not an accessible encoding in a
    product for low-vision users. The BooleanVar stays the single
    source of truth, so Apply/dirty/reload behave exactly as before
  * Macros tab (v8.46): TWO COLUMNS - the five key macros left, and
    BESIDE them the recordings in a compact five-row box (five is the
    library cap: Ctrl+1..5 play those positions). Every recording row
    carries its OWN "Repeat until stopped" pill switch (the column
    appears only once at least one recording exists), Rename / Export
    / Import / Delete sit side by side in the box's bottom-right
    corner, and clicking a row selects that recording for them and
    for the play shortcut. Recordings capture EVERYTHING the user
    does: every key, every mouse button and the cursor trail, and
    replay it exactly (tagged steps in macros.json, export marker 2,
    v1 keyboard-only files still import).
  * Reject window + shared-seat dialog (v8.47): CLEAN CARD surface.
    The blurred-logo backdrop (a 14 px GaussianBlur over the red
    snake) left saturated red blotches peeking out from behind the
    centred card and flat dead margins beside it - in the field the
    window sides read as dirty spots and texture. Both windows are
    now one flat themed card like every other window in the product,
    and the reject window re-fits its frame whenever its text
    changes (language switch while it is open included), so a tall
    translation can never clip the card.

The GUI never calls thread-bound Windows APIs directly: actions go to
the hook thread via PostThreadMessage.
"""

import colorsys
import io
import base64
import threading
import time

import numpy as np

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog, messagebox, simpledialog

import i18n
import logo
import online
import vision
try:
    import provider_logos
except ImportError:
    # older partial copy of the project: sign-in falls back to
    # text-only buttons instead of crashing at launch
    provider_logos = None
from assist import start_app
from config import DEFAULT_CONFIG, _coerce_value
from core import APP_NAME, log
try:
    # core.py newer than v8.23: the ring buffer and log file behind the
    # version stamp in the header. Nothing in the interface reads them -
    # they exist so a windowless build still records what happened.
    from core import APP_VERSION
except ImportError:          # older core.py next to a newer gui.py
    APP_VERSION = "?"
from hotkeys import MACRO_SLOTS, REC_PLAY_SLOTS
from win32rt import PostThreadMessage, WM_HOTKEY, get_cursor_pos, \
    virtual_screen

try:
    from win32rt import apply_window_theme
except ImportError:
    # Older win32rt.py next to a newer gui.py (partial file copy):
    # degrade gracefully instead of crashing at launch.
    def apply_window_theme(*_args, **_kw):
        pass
    log("win32rt.py is older than gui.py - title-bar theming disabled. "
        "Copy ALL project files, then rebuild.")

try:
    from PIL import Image as _PILImage
    from PIL import ImageDraw as _PILDraw
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False


def hex2rgb(value):
    value = str(value).lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


# ----------------------------------------------------------------------
# Live localisation (v8.39)
#
# Every widget that shows a translatable string registers a zero-arg
# closure here that re-applies its text from the current catalog; a
# language change runs the lot, so the window re-words itself without
# being rebuilt.  A closure returns False when its widget is gone, and
# apply_language() prunes it - logout/login loops must not accumulate
# dead callbacks.
# ----------------------------------------------------------------------

RETEXT = []


def R(fn):
    RETEXT.append(fn)
    return fn


def apply_language():
    """Re-word every registered widget in the live language."""
    dead = []
    for fn in list(RETEXT):
        try:
            if fn() is False:
                dead.append(fn)
        except tk.TclError:
            dead.append(fn)
    for fn in dead:
        try:
            RETEXT.remove(fn)
        except ValueError:
            pass


def _live(w):
    try:
        return bool(w.winfo_exists())
    except (tk.TclError, RuntimeError):
        return False


def label_key(key):
    """The catalog key a setting name lives under.

    Generated families (the five macro slots, the five play-slot
    hotkeys) share one PATTERN key each with a %d, so a locale adds
    three strings instead of fifteen and a sixth slot could never be
    untranslated."""
    if key.startswith("macro") and key.endswith("_key"):
        return "lbl.macro_key"
    if key.startswith("macro") and key.endswith("_action"):
        return "lbl.macro_action"
    if key.startswith("key_play") and key[len("key_play"):].isdigit():
        return "lbl.key_play_n"
    return "lbl." + key


def tr_label(key):
    """Setting name in the live language, META English as fallback."""
    lk = label_key(key)
    t = i18n.L(lk)
    if t == lk:
        return META[key][0]
    if "%d" in t:
        num = key[len("key_play"):] if lk == "lbl.key_play_n" \
            else key[len("macro"):-len("_action") if lk == "lbl.macro_action"
                     else -len("_key")] if lk != "lbl.key_play_n" else ""
        try:
            return t % int(num)
        except (TypeError, ValueError):
            return t
    return t


def desc_key(key):
    """Catalog key of a hover description; generated families share
    pattern keys exactly like label_key()."""
    if key.startswith("macro") and key.endswith(("_key", "_action")):
        return "desc.macro_" + ("key" if key.endswith("_key") else "action")
    if key.startswith("key_play") and key[len("key_play"):].isdigit():
        return "desc.key_play_n"
    return "desc." + key


def tr_desc(key):
    """Hover description; en is published from META at import (plus
    the three generated patterns below), other locales override."""
    dk = desc_key(key)
    t = i18n.L(dk)
    if dk == "desc.key_play_n" and "%d" in t:
        t = t % int(key[len("key_play"):])
    return t


# ----------------------------------------------------------------------
# Themes, fonts, metadata
# ----------------------------------------------------------------------

THEMES = {
    "light": dict(
        bg="#f4f5f7", card="#ffffff", text="#1b1b1b", muted="#5f6368",
        entry="#ffffff", entry_bd="#c8ccd0", accent="#c62828",
        green="#2e7d32", amber="#b26a00",
        tab_bg="#eceef1", desc_bg="#e8eaed", status_bg="#e8eaed",
        light_bg="#dfe2e6",
        # "switch_on" is the ON colour of the Assistance tab's pill
        # switches, and it is the logo's own red: #cc2f38 is the mean
        # colour of the snake's fully-opaque head/upper body in
        # LOGO_PNG_B64 (the mark runs #d53439 at the head down to
        # #9c2133 in the tail, so the vivid end is what reads as "the
        # Snappy AI red").  Kept as the literal sample in the light
        # theme, where it measures 5.2:1 against both the white card
        # and the white knob.
        switch_on="#cc2f38",
    ),
    "dark": dict(
        bg="#1e2026", card="#272a33", text="#e9eaee", muted="#a2a7b0",
        entry="#1b1d23", entry_bd="#3a3f4a", accent="#ef5350",
        green="#66bb6a", amber="#ffb74d",
        tab_bg="#17181d", desc_bg="#17181d", status_bg="#17181d",
        light_bg="#343845",
        # Same hue, brightened by the transform this palette already
        # applies to its other state colours (accent #c62828 ->
        # #ef5350, green #2e7d32 -> #66bb6a): the raw logo red only
        # reaches 2.75:1 on the dark card, this reaches 3.6:1, which
        # clears the 3:1 bar for a non-text control.
        switch_on="#e04a52",
    ),
}

# Pill-switch geometry, shared by the Light/Dark switch in the header
# and the on/off switches on the Assistance tab so the two read as one
# control family: a 46 x 22 track, a 16 px knob with a 3 px inset, and
# the knob ON THE RIGHT when the setting is on.
SW_W, SW_H = 46, 22
SW_KNOB, SW_PAD, SW_RADIUS = 16, 3, 11

F_BASE = ("Segoe UI", 11)
F_BOLD = ("Segoe UI", 11, "bold")
F_DESC = ("Segoe UI", 10)
F_H1 = ("Segoe UI", 19, "bold")
F_BTN = ("Segoe UI", 11, "bold")
F_BTN_BIG = ("Segoe UI", 13, "bold")
F_ENTRY = ("Segoe UI", 11)
F_TAB = ("Segoe UI", 12, "bold")
F_TAB_OFF = ("Segoe UI", 10)

# v8.31 header geometry.  The owner asked for a BIGGER logo, a card
# 20 px SHORTER than v8.30 (which was 84 px tall: the 52 px logo plus
# 16 px of logo padding above and below), and the three identity
# lines compacted beside the logo.  The card height is now a fixed
# constant - the contents are sized to live inside it, so the strip
# stopped being whatever the installed fonts happened to request.
# The logo grows 52 -> 60 px and the identity lines get their own
# tighter type ramp (title 15 bold, the e-mail and licence lines
# 9 pt, 1 px between them) so the whole block reads as one compact
# identity cluster next to the mark.
# v8.32: the owner field-tested v8.31, kept the logo size but gave
# the strip 10 of the 20 px back (64 -> 74, the main window growing
# with it) so the identity stack could move UP: the title now opens
# on the logo's top row - the snake's head - instead of riding
# centred, and the e-mail / licence lines hang off it with their
# 1 px gaps.  The mark itself keeps its exact seat (same left
# gutter, same vertical centring), so growing the strip never moves
# it sideways.
HEADER_H = 74
HEADER_LOGO_PX = 60
# v8.33: the identity stack rides 4 px HIGHER than the logo's centring
# remainder.  The owner's crop showed the third line (the licence
# status) running tight against the card's bottom edge; lifting the
# whole stack bought that room back without touching the mark.
# v8.34: that third line is gone - the e-mail and licence status moved
# to the status bar - so the stack is just the title and a build stamp
# and no longer risks clipping at all.  The raise is KEPT: it is the
# seat the owner signed off on, and the two-line stack reads better
# slightly high next to the centred 60 px mark than dead level with it.
HEADER_TEXT_RAISE = 4
# First row of the identity stack: the logo rides centred in the
# strip, so its top edge - the snake's head - is (HEADER_H -
# HEADER_LOGO_PX) // 2 px below the card top; the title box starts
# HEADER_TEXT_RAISE px above that row.  Clamped at 0 so a future
# shorter strip can never pack the title off the top of the card.
HEADER_TEXT_TOP = max(0, (HEADER_H - HEADER_LOGO_PX) // 2
                      - HEADER_TEXT_RAISE)
# v8.35: both header faces grew by 5 pt on the owner's ask - the title
# 15 -> 20 bold, the build stamp 9 -> 14.  Neither constant is used
# anywhere else in the file, so nothing outside the header card moves.
# v8.36: the build stamp came back down to 10 pt - at 14 it read as a
# second headline rather than a footnote to the title.  10 pt is also
# exactly F_DESC, the face the status bar and the hover descriptions
# use, so the small print now matches across the window.
F_HEAD_H1 = ("Segoe UI", 20, "bold")
F_HEAD_LINE = ("Segoe UI", 10)

# v8.36: optical left inset for the build stamp, in px.
#
# Both header labels are packed anchor="w" in the same frame, so their
# BOXES already start on the same pixel - the misalignment is in the
# glyphs.  A font's left side bearing scales with its em size, so the
# 20 pt bold "S" of "Snappy AI" starts a pixel or two further right than
# the 10 pt "b" of "build", and the smaller line reads as hanging out to
# the left.  Nudging the stamp right by this much lines the two up by
# eye.  This is the ONE number to tune if it still looks off on your
# display - it depends on the font's metrics and your DPI scale, neither
# of which can be measured without a real screen.
HEADER_BUILD_INDENT = 2

# How often a RUNNING instance re-asks the auth worker whether the
# subscription is still active (v8.27: a built-in constant - the
# user-facing "Subscription re-check" setting was removed).
ENTITLEMENT_CHECK_MINUTES = 30

META = {
    # v8.40: every label and description rewritten in plain user
    # language - no config keys, no engine jargon in a name.  Dropdowns
    # whose stored value is a code word are "map" kind: the display
    # string is human, the stored value stays the code the engine and
    # old config files expect.
    "block_bound_keys": ("Single-key shortcuts swallow the key",
                         "Off (default): a shortcut without Ctrl/Alt/"
                         "Shift - like 1 or V - works in every program "
                         "AND still types normally, so pressing it "
                         "mid-sentence also triggers its action. On: "
                         "the action still fires everywhere, but the "
                         "key no longer types while bound.",
                         "bool", None),
    "hold_follow": ("Keep following while the button is held",
                    "While you keep the left button pressed right "
                    "after a snap - or press again on the remembered "
                    "item - the cursor stays on that item's colour, "
                    "which steadies drags like scrollbar thumbs. "
                    "Presses anywhere else are never touched.",
                    "bool", None),
    "rapid_click_snap": ("Assist every click in a fast burst",
                         "Off (default): while one click is still "
                         "being handled, extra left clicks go straight "
                         "to Windows. On: every left click is assisted, "
                         "so double-clicking keeps snapping to items "
                         "instead of leaking plain clicks.",
                         "bool", None),
    "mouse2_action": ("Right-click extra action",
                      "What a short right-click ALSO does - the right "
                      "click itself always keeps its normal Windows "
                      "function. Default: nothing.",
                      "map", (("Do nothing", 4),
                              ("Clear the current follow task", 1),
                              ("Follow the last snapped colour", 2),
                              ("Pick the colour under the cursor, then "
                               "follow it", 3))),
    "mouse2_hold_action": ("Right-hold extra action",
                           "The same choices, fired when you HOLD the "
                           "right button for about half a second "
                           "instead of clicking it. A press is either "
                           "a click or a hold, never both. Default: "
                           "nothing.",
                           "map", (("Do nothing", 4),
                                   ("Clear the current follow task", 1),
                                   ("Follow the last snapped colour", 2),
                                   ("Pick the colour under the cursor, "
                                    "then follow it", 3))),
    "radius": ("How far from the cursor to look",
               "Search distance in pixels (40-400). Raise it when the "
               "item you want sits just out of reach; lower it when "
               "the wrong neighbour keeps winning.", "int", None),
    "on_target_dist": ("Already-on-item distance",
                       "If your click lands within this many pixels of "
                       "an item's centre, nothing moves - you hit it.",
                       "int", None),
    "glide_ms": ("Animate cursor moves",
                 "0 (default) jumps instantly - fastest. 40-120 glides "
                 "so you can watch the cursor travel; moving the mouse "
                 "yourself cancels the glide and keeps control.",
                 "int", None),
    "watcher_seconds": ("Double-click window",
                        "In classic mode, a second snap near the same "
                        "spot within this time becomes a double-click "
                        "on the item.", "float", None),
    # v8.43: kind "colors" - the row's value is a strip of COLOUR
    # BOXES (see make_row), not a typed "r,g,b; r,g,b" string.
    "accent_color": ("My colour(s)",
                     "The colour Snappy AI should prefer, shown as "
                     "colour boxes on the right. Pick a colour below "
                     "and press 'Add to preferred colours' to add it "
                     "- fifteen boxes at most; click a box to remove "
                     "that colour again. Items containing one of them "
                     "win ties. An empty list shows a crossed-out box "
                     "and disables the setting.",
                     "colors", None),
    "accent_only": ("Only assist my colour",
                    "Only items containing your colour can be "
                    "assisted; clicks anywhere else pass straight "
                    "through to Windows. Needs a colour in 'My "
                    "colour(s)' first - with none set this switch stays "
                    "on and simply does nothing, and the log says so "
                    "(your switch is never rewritten behind your "
                    "back).", "bool", None),
    "accent_tolerance": ("Colour match strictness",
                         "How close a colour must be to count as yours "
                         "(4-90). Lower = stricter.", "int", None),
    # v8.49: these two descriptions now state their DEPENDENCY on each
    # other. At 0 near-miss shades both engines collapse to the same exact
    # tolerance box, so the engine dropdown genuinely does nothing until
    # this is above 0 - which is documented in config.py but was invisible
    # here, and reads as a broken control to the person who set 0 and then
    # tried switching engines.
    "accent_soft": ("Accept near-miss shades",
                    "0-100: how much lighter, darker or washed-out "
                    "versions of your colour still count in its "
                    "favour. 0 = exact shades only, and at 0 the Colour "
                    "matching engine below makes no difference - raise "
                    "this first.", "int", None),
    "accent_matcher": ("Colour matching engine",
                       "How colours are compared. Perceptual ranks by "
                       "how colours actually look and is recommended; "
                       "Classic is the older engine, kept for "
                       "comparison. Only applies while 'Accept "
                       "near-miss shades' is above 0 - at 0 both use the "
                       "same exact colour box.",
                       "map", (("Perceptual - how colours look "
                                "(recommended)", "oklab"),
                               ("Classic - the older engine", "hsv"))),
    "accent_boost": ("Colour tie-break strength",
                     "How much your colour lifts an item's score "
                     "(0-3). Raise toward 1.5-2 when the wrong item "
                     "still wins.", "float", None),
    # v8.43: colour boxes here too - same widget as My colour(s).
    "exclude_color": ("Never-click colour(s)",
                      "Items containing these colours are never "
                      "assisted: clicks on them go straight to "
                      "Windows, in both modes. Shown as colour boxes "
                      "on the right - pick a colour below and press "
                      "'Add to refused colours' to add one (fifteen "
                      "at most), click a box to remove it. An empty "
                      "list shows a crossed-out box and disables the "
                      "setting.",
                      "colors", None),
    "motion_3d": ("Smarter following for moving items",
                   "Track moving items with position AND size instead of "
                   "a straight-line fit: single bad scans are ignored "
                   "instead of blinding the follower, turns are followed "
                   "through, and a sudden size jump restarts the track "
                   "(that means the scanner picked a different item). "
                   "Same speed gates and the same 80 px cap - only the "
                   "brains change. Runs on its own.",
                   "bool", None),
    "motion_predict": ("Lead moving items",
                       "For items that move while you click (scrolling "
                       "lists, video seek bars), aim slightly ahead so "
                       "the click lands on the item, not where it was. "
                       "Still items are unaffected.", "bool", None),
    "motion_lead_ms": ("How far ahead to aim",
                       "Milliseconds of travel to lead a moving item "
                       "(0-300): 40-80 suits slow scrolling, 100-150 a "
                       "fast seek bar. The lead is capped at 80 px and "
                       "switches off for slow or turning movement.",
                       "int", None),
    "follow_enabled": ("Remember the last clicked item",
                       "After a successful snap, similar-looking items "
                       "or items in the same place win ties for a "
                       "while - handy for scrollbars and repeated "
                       "clicks on one control.", "bool", None),
    "watch_center_only": ("Watch the screen centre only",
                          "For fixed layouts where the items never "
                          "move: assistance ignores where your cursor "
                          "is and always looks inside a square at the "
                          "middle of the screen - as wide as your "
                          "\"search distance\" setting (150 px by "
                          "default). Clicks outside that square pass "
                          "through completely untouched, like empty "
                          "space. Off (default): the usual cursor-"
                          "anchored search.",
                          "bool", None),
    "center_follow": ("Keep the cursor on it",
                      "Needs \"Watch the screen centre only\" on. Once "
                      "an item inside the watched square is picked - "
                      "by your click, or by resting the cursor on it - "
                      "the cursor stays parked on it and keeps following "
                      "it even while the item moves (a scrolling plane, "
                      "an animated panel). No colour needed: without "
                      "\"My colour(s)\" set it locks straight onto the "
                      "best high-contrast item; with a colour set it "
                      "waits for the brief dwell first. It never fights "
                      "you: holding any mouse button pauses it, and it "
                      "lets go about a second after the item "
                      "disappears. Turn on \"Lead moving items\" as "
                      "well for smooth fast chasing.",
                      "bool", None),
    "follow_learn": ("What the memory may learn",
                     "Only items in my colour: a misclick that snapped "
                     "somewhere else cannot retarget the memory. Every "
                     "successful snap: the old, trusting behaviour.",
                     "map", (("Only items in my colour", "accent"),
                             ("Every successful snap", "any"))),
    "follow_boost": ("Memory strength",
                     "How strongly the remembered item wins ties: "
                     "100% can double its score while fresh, 25% is a "
                     "light nudge.",
                     "map", (("25%", 0.25), ("50%", 0.5),
                             ("75%", 0.75), ("100%", 1.0))),
    "follow_seconds": ("How long to remember",
                       "Seconds the remembered item stays preferred "
                       "after your last successful snap (1-120).",
                       "int", None),
    "merge_distance": ("Glue nearby pieces together",
                       "Pieces closer than this many pixels (a broken "
                       "outline, an icon beside its label) become one "
                       "item. Two complete items are never glued, so "
                       "the cursor cannot land between buttons.",
                       "int", None),
    "key_launch": ("Shortcut: start assisting",
                   "Format: ctrl+l, f5, space, ctrl+alt+1 ... "
                   "Modifiers: ctrl, alt, shift, win. Applied on "
                   "Apply.", "str", None),
    "key_pause": ("Shortcut: pause",
                  "Your mouse and keyboard become entirely yours "
                  "again until you launch.", "str", None),
    "key_record": ("Shortcut: start a recording",
                   "Captures everything you do - every key, every "
                   "mouse click and every cursor move - while your "
                   "input still reaches your programs, until the stop "
                   "shortcut saves it into the Macros list. Arms only "
                   "while launched.", "str", None),
    "key_record_stop": ("Shortcut: stop and save the recording",
                        "Stops capturing, saves the sequence into the "
                        "Macros list, and halts a running playback.",
                        "str", None),
    "key_play": ("Shortcut: play the selected recording",
                 "Replays the recording selected in the Macros tab, or "
                 "the newest one when nothing is selected. Pressed on "
                 "a repeating recording, it stops it.", "str", None),
    "key_mode1": ("Shortcut: classic mode (up to 4 keys)",
                  "Comma-separated, e.g. '1, f1, ctrl+f1, v'. See the "
                  "Keybindings tab for what classic mode does.",
                  "str", None),
    "key_mode2": ("Shortcut: guide mode (up to 4 keys)",
                  "Comma-separated, e.g. '2, f2, ctrl+f2, b'. See the "
                  "Keybindings tab for what guide mode does.",
                  "str", None),
    "capture_backend": ("Screen capture engine",
                        "How the screen is photographed. Automatic "
                        "picks the fastest that works; Compatible "
                        "always works, including Remote Desktop and "
                        "virtual machines. Applies on restart.",
                        "map", (("Automatic - fastest with safe "
                                 "fallback", "auto"),
                                ("Desktop Duplication - fastest on most "
                                 "PCs", "dxcam"),
                                ("Compatible - always works (Remote "
                                 "Desktop, VMs)", "mss"),
                                ("Windows Graphics Capture - "
                                 "experimental", "wgc"))),
    # v8.50: click DELIVERY backend - the opt-in Interception option.
    # The dropdown shows availability in its own label; assist.py falls
    # back to win32 with a log line if the driver is missing, so an
    # unavailable choice can never eat a click.
    "input_backend": ("Click delivery method",
                      "How your assisted clicks reach the screen. "
                      "Standard works everywhere with nothing to "
                      "install and is what almost everyone should "
                      "keep. Driver level sends clicks through the "
                      "Interception kernel driver instead, for the "
                      "few games that ignore normal synthetic clicks "
                      "- it needs interception.dll next to Snappy AI "
                      "and the driver installed (run interception.exe "
                      "install as administrator, then reboot). If "
                      "either is missing, Snappy AI says so once and "
                      "keeps working the standard way. Applies on "
                      "restart.",
                      "map", (("Standard Windows method", "win32"),
                              ("Driver level (Interception) - for "
                               "games that ignore synthetic clicks",
                               "interception"))),
    # v8.49: the three detection knobs have a documented precedence that
    # was invisible here. "Auto-adjust for dim screens" may only LOWER the
    # bar, and it stands aside entirely once you raise either number above
    # its stock value - otherwise "raise it if it clicks the wrong thing"
    # would silently do nothing while the recommended default was on.
    "contrast_threshold": ("How faint an edge may be",
                           "Lower finds fainter items (and more "
                           "noise); higher needs crisper edges. Raising "
                           "this above 38 turns off the auto-adjust "
                           "below for this control - a value you set "
                           "deliberately is used exactly.",
                           "int", None),
    "min_contrast": ("Minimum edge strength",
                     "An item must be at least this crisp to be "
                     "clickable at all. Values below 28 count as 28: "
                     "a built-in quality floor keeps noise from "
                     "becoming clickable. Raising this above 48 turns "
                     "off the auto-adjust below for this control - your "
                     "number is then used exactly.", "int", None),
    "adaptive_threshold": ("Auto-adjust for dim screens",
                           "Dark themes and washed-out documents lower "
                           "their own detection bar automatically, so "
                           "faint items are still found. Recommended "
                           "on. It only ever LOWERS the bar, and it "
                           "stands aside when you have deliberately "
                           "raised either contrast control above its "
                           "stock value (38 / 48).", "bool", None),
    "luminance_norm": ("Judge edges by relative brightness",
                       "Edges are scored against how bright their "
                       "surroundings are, so dark-mode items rank like "
                       "light-mode ones. Recommended on.",
                       "bool", None),
    "min_area": ("Smallest item size",
                 "Smaller blobs are ignored as specks, unless they are "
                 "glued to a bigger item.", "int", None),
    "max_area": ("Largest item size",
                 "Bigger blobs are ignored - usually whole windows or "
                 "wallpaper, not clickable items.", "int", None),
    "max_dim": ("Largest item width or height",
                "Items wider or taller than this are ignored; items at "
                "a screen edge, like scrollbars, get double.",
                "int", None),
    "stall_pause_seconds": ("Pause after a hiccup",
                            "If a scan ever stalls, assistance pauses "
                            "this long and any held click is given "
                            "back to you.", "float", None),

    # v8.48: colour handling round 2. Three switches, all on by
    # default - each only ever makes matching stricter about the right
    # things (lighting, shade states, speckle), never looser about hues.
    "color_adapt": ("Adapt to screen lighting",
                    "Each item is white-balanced against its own "
                    "background before matching, so night light and "
                    "theme casts stop shifting your colour out of "
                    "tolerance. Turn off only to compare against the "
                    "unadapted matcher.",
                    "bool", None),
    "accent_variants": ("Catch bright and dim states of my colour",
                        "Brighter and dimmer copies of your colour match "
                        "too, so hover, pressed and dimmed states of a "
                        "control count without widening the hue "
                        "tolerance. Lightness only - a wrong hue can "
                        "never ride it.",
                        "bool", None),
    "accent_coherent": ("Ignore scattered colour specks",
                        "Your colour must form a connected blob to count "
                        "- scattered dither or compression specks never "
                        "qualify an item, boost it, or put it on the "
                        "never-click list.",
                        "bool", None),

    # v8.48: snap offset. The click point is normally the middle of the
    # item; these move it, in pixels (right and down are positive).
    "snap_offset_x": ("Click point: shift left / right",
                      "Moves the click point sideways from the middle of "
                      "the item (-200 to 200, negative goes left). For a "
                      "control whose middle is dead - a split button, a "
                      "slider track - dial the click onto the live spot "
                      "once instead of fighting every snap.",
                      "int", None),
    "snap_offset_y": ("Click point: shift up / down",
                      "Moves the click point vertically from the middle "
                      "of the item (-200 to 200, negative goes up). Same "
                      "idea as the sideways shift: land on the live part "
                      "of the control.",
                      "int", None),

    # v8.48: auto-click. The ONLY setting in the product that makes the
    # app act with no gesture from the user, so its label leads with the
    # consequence ("clicks on its own") rather than the mechanism.
    "auto_click": ("Click items by itself",
                   "Scans the screen centre on its own and clicks the "
                   "best item - no click from you needed; turning this "
                   "on IS the request. With 'My colour(s)' set it "
                   "clicks only items in your colour; without a colour "
                   "it clicks the highest-contrast item instead (raise "
                   "'How crisp an auto-click target must be' if it "
                   "picks too eagerly). Never while paused, never on "
                   "Snappy AI's own windows, never on a Never-click "
                   "colour, and it stops at the limit below. Press "
                   "Pause any time to take the mouse back.",
                   "bool", None),
    "auto_click_interval": ("Seconds between auto-clicks",
                            "How often the screen centre is re-checked "
                            "(0.1-60). The default 0.1 s = ten looks a "
                            "second, so a fresh item is clicked almost "
                            "as soon as it appears; the same-spot guard "
                            "and the pause-before-click keep it from "
                            "hammering one control. Raise it to 2-5 for "
                            "a calmer pace.",
                            "float", None),
    "auto_click_min_contrast": ("How crisp an auto-click target must be",
                                "On the same scale as 'Minimum edge "
                                "strength'. This gate matters MOST when "
                                "no colour is set: with colour-free "
                                "auto-clicking only items above this "
                                "crispness are eligible. Start at the "
                                "default and raise it if it clicks the "
                                "wrong thing.",
                                "int", None),
    "auto_click_max_clicks": ("Auto-click limit per session",
                              "How many times it may click on its own "
                              "after you launch (1-200). When it reaches "
                              "the limit it stops and tells you, so a "
                              "wrong setup cannot run away.",
                              "int", None),
    "auto_click_settle_ms": ("Pause before an auto-click lands",
                             "The cursor rests on the target this long "
                             "(0-2000 ms) before the click, so the "
                             "program sees the highlight first. 120 suits "
                             "most windows.", "int", None),
    "auto_click_repeat_px": ("Stop re-clicking the same spot",
                             "After an auto-click, a target within this "
                             "many pixels is left alone (0-400). Without "
                             "it a button that stays on screen would be "
                             "clicked again and again.", "int", None),
    "auto_click_radius": ("How far from the middle to look",
                          "Auto-clicking searches around the centre of "
                          "the screen (40-600 px). Raise it for a busy "
                          "window; lower it so it only ever sees the one "
                          "control in the middle.", "int", None),
}

# Macro slots: the number of combo-macro triggers and recording play
# keys comes from hotkeys.py (five each since v8.17), so descriptions
# can never be generated for slots the engine does not have.
for _i in range(1, MACRO_SLOTS + 1):
    META["macro%d_key" % _i] = (
        "Macro %d: press this key" % _i,
        "The key that MEANS the macro instead of typing: 'b', 'f7', "
        "'ctrl+b' ... While launched, pressing it sends the combo "
        "beside it exactly once and the key itself never reaches your "
        "programs. Paused, it types normally. Empty = macro off.",
        "str", None)
    META["macro%d_action" % _i] = (
        "Macro %d: sends this instead" % _i,
        "The key combo pressed for you on each trigger press (one "
        "press = one combo press): 'ctrl+c', 'ctrl+shift+s', 'space', "
        "'f5' ... Empty = macro off.",
        "str", None)

for _i in range(1, REC_PLAY_SLOTS + 1):
    META["key_play%d" % _i] = (
        "Shortcut: play recording #%d" % _i,
        "Replays recording #%d of the numbered list in the Macros tab, "
        "by its position in the list. If the list is shorter than "
        "that, nothing happens." % _i,
        "str", None)

# Tab layout - settings live on tabs BY OPTION CATEGORY (v8.38):
#   Assistance          = every ON/OFF switch that changes BEHAVIOUR
#   Colors              = the two colour lists + the Current RGB
#                         Value row as full-width rows, values on the
#                         right like every other tab (the lists as
#                         colour boxes, the RGB row as three channel-
#                         glow boxes), then the picker bottom-left
#                         with its controls on the right edge (v8.43;
#                         "Detection & Colours" before v8.39)
#   Handler             = the contrast gates, the item-size gates and
#                         the accent-matching strictness (v8.38 as
#                         "Color Handling", renamed in v8.39)
#   Hotkeys             = every bindable key
#   Macros              = macro slots + the recording library (custom UI)
#   Advanced            = every remaining value option (geometry,
#                         timing, size gates, right-button actions)
#   Experimental        = every DROPDOWN (choice) setting: engine
#                         selection, kept apart because each has a
#                         tested default and the alternatives exist
#                         for A/B comparison or special hardware
#   Help                = read-only tuning guide (scrollable)
# (mode/theme/entitlement keys stay off the tabs: mode switches with
# its hotkeys, theme with the header switch, the rest are deployment.)
TAB_ASSIST = ["block_bound_keys", "hold_follow", "rapid_click_snap",
              "follow_enabled", "motion_predict", "motion_3d",
              "watch_center_only",
              "center_follow",
              "accent_only",
              "adaptive_threshold", "luminance_norm",
              "color_adapt", "accent_variants", "accent_coherent",
              "auto_click",
              "auto_click_interval", "auto_click_min_contrast",
              "auto_click_max_clicks", "auto_click_settle_ms",
              "auto_click_repeat_px", "auto_click_radius"]
TAB_DETECT = ["accent_color", "exclude_color"]
TAB_KEYS = ["key_launch", "key_pause", "key_mode1", "key_mode2",
            "key_record", "key_record_stop", "key_play", "key_play1",
            "key_play2", "key_play3", "key_play4", "key_play5"]
TAB_COLOR = ["contrast_threshold", "min_contrast",
             "min_area", "max_area", "max_dim",
             "accent_tolerance", "accent_soft", "accent_boost"]
TAB_ADV = ["radius", "on_target_dist", "glide_ms", "watcher_seconds",
           "stall_pause_seconds", "merge_distance",
           "motion_lead_ms", "follow_seconds",
           "snap_offset_x", "snap_offset_y"]
# Every "choice" (dropdown) setting.  Derived from META's kinds rather
# than hand-kept, so a dropdown added to META in the future lands here
# by construction and can never silently sit on the wrong tab - which
# is the rule this tab exists to enforce.
TAB_EXPERIMENTAL = [k for k in META if META[k][2] in ("choice", "map")]

def val_slug(value):
    """Catalog-safe slug of a stored dropdown value: 1.0 -> "1_0"."""
    return str(value).replace(".", "_")


def val_key(key, value):
    return "val.%s.%s" % (key, val_slug(value))


def map_pairs(key):
    """The (EN display, stored-value) pairs of a "map" (dropdown-with-
    values) setting, e.g. follow_boost's 25%..100% -> 0.25..1.0."""
    return list(META[key][3])


def map_pairs_live(key):
    """The same pairs with the display strings in the LIVE language.

    v8.40 fix: dropdown values are user-visible text, so they are
    catalog keys (val.<setting>.<value>) like everything else, with the
    English META display as fallback.  A Combobox's `values` list is
    frozen at creation, so every map row rebuilds it from here on a
    language change."""
    out = []
    for disp, val in META[key][3]:
        t = i18n.L(val_key(key, val))
        out.append((t if t != val_key(key, val) else disp, val))
    return out


def map_display(key, value):
    """Display string for a stored value, in the LIVE language.

    Exact match first (this is how the code-word maps work: "auto",
    "accent", 4 ...).  Only when nothing matches exactly and both sides
    are numbers - an old config.json carrying follow_boost = 2.0, which
    a four-step dropdown cannot show - fall back to the NEAREST step,
    so the widget stays honest instead of blank."""
    pairs = map_pairs_live(key)
    for disp, val in pairs:
        if str(val) == str(value):
            return disp
    try:
        num = float(value)
    except (TypeError, ValueError):
        return pairs[0][0]
    try:
        return min(pairs, key=lambda p: abs(float(p[1]) - num))[0]
    except (TypeError, ValueError):
        return pairs[0][0]


def map_value(key, display):
    """Stored value for a display string, or None when unknown.

    Accepts the display in ANY language (live first, English as a
    second pass): a StringVar can still hold the previous language's
    word for one paint cycle after a switch, and Apply must never lose
    a setting because of that."""
    for pairs in (map_pairs_live(key), map_pairs(key)):
        for disp, val in pairs:
            if disp == display:
                return val
    return None


# ----------------------------------------------------------------------
# English prose, published into the i18n catalog at import (v8.40).
#
# The English source of truth stays here, next to the widgets it
# describes, while every other locale overrides by key.  All of it is
# written in the words the settings themselves use - no config keys,
# no engine jargon - because the reader is a person with low vision,
# not a developer.
# ----------------------------------------------------------------------

PROSE = {
    "desc.default": "Hover over a setting name to see what it does.",

    "note.assist":
        "Every switch that changes behaviour while launched. The two "
        "modes switch with your mode keys - the Keybindings tab "
        "explains what each mode does. Assistance always starts "
        "paused; Launch is the only on/off. Where the engine looks and "
        "how clicks feel live on Advanced; what counts as an item "
        "lives on Handler.",
    "note.colors":
        "The two lists at the top choose which colours Snappy AI "
        "prefers or refuses. Each shows its colours as boxes on the "
        "right, fifteen at most; clicking a box removes that colour "
        "again, and an empty list shows a crossed-out box and counts "
        "as off. 'Add to preferred colours' and 'Add to refused "
        "colours' put the colour standing in the picker into the "
        "matching list. 'Current RGB Value' is three glow boxes - "
        "brighter means more red, green or blue in the picked colour; "
        "it follows the picker and cannot be typed into. The picker "
        "mixes a colour like a paint program. Beside it: fifteen "
        "preset swatches load a colour into the picker; 'Pick color "
        "from screen' takes the single colour under the cursor (after "
        "a 3 s countdown); 'Suggest colors from screen' fills a row "
        "with the main UI colours found around the cursor - click one "
        "to load it into the picker.",
    # v8.42: the read-only R,G,B row under the two colour lists.
    # v8.43: its three boxes are no longer numbers - each one glows
    # with how much of its channel the picked colour holds.
    "col.rgb.name": "Current RGB Value",
    "col.rgb.desc":
        "Three boxes showing the colour sitting in the picker right "
        "now: the first glows with how much red it holds, the second "
        "with green, the third with blue - brighter means more. The "
        "row follows the picker, the preset swatches and the screen "
        "buttons; it cannot be typed into.",
    "note.handler":
        "What counts as a clickable item: how faint an edge may be, "
        "how crisp it must be, and how big or small an item may be. "
        "Nothing found? Loosen these. Wrong thing found? Tighten them, "
        "or use your colour on the Colors tab.",
    "note.keybindings":
        "Every shortcut - and below it, what the two modes do, how to "
        "record your own key and mouse input, and how single keys "
        "differ from key combos.",
    "note.macros":
        "A macro turns one key press into a whole combo while "
        "launched. Beside the macros, your recordings: up to five "
        "named captures of everything you did - every key, mouse "
        "click and cursor move - that replay exactly as recorded. "
        "Click a recording to select it; each row carries its own "
        "'Repeat until stopped' switch, and 'Rename', 'Export', "
        "'Import' and 'Delete' sit at the bottom of the box.",
    "note.advanced":
        "Distance and timing settings that change how clicks feel "
        "rather than what is found. Most people never need to touch "
        "these; the defaults are the tested ones.",
    "note.macros_keys":
        "Record/play shortcuts live on the Keybindings tab (defaults: "
        "Ctrl+Alt+R record, Ctrl+Alt+S stop and save, Ctrl+Alt+M play, "
        "Ctrl+1..5 play recordings #1..#5 by list position).",
    "note.experimental":
        "Engine choices, each with a tested default. Change them only "
        "when comparing engines, on unusual hardware, or when support "
        "asks - the capture engine applies on restart.",

    "kb.mode.t": "What the two modes do",
    "kb.mode.b":
        "Guide mode (default, shortcut 2): your click always reaches "
        "the program untouched; after you release the button, the "
        "cursor moves onto the nearest clear item, so your next click "
        "starts from it. Nothing is ever eaten - the safest mode.  "
        "Classic mode (shortcut 1): if you click near an item, that "
        "mis-click is caught, the cursor snaps onto the item and "
        "Snappy AI clicks it for you; if nothing is near, your click "
        "is given back untouched.  In both modes, holding Shift while "
        "clicking bypasses assistance for that one click.",
    "kb.rec.t": "How to record and replay your own key and mouse input",
    "kb.rec.b":
        "While launched, press your start-recording shortcut "
        "(Ctrl+Alt+R by default): every key you press, every mouse "
        "button you click and every cursor move is captured AND still "
        "reaches your programs, so you can work normally while "
        "recording. Press the stop shortcut (Ctrl+Alt+S) to save it "
        "into the list on the Macros tab - five recordings fit there. "
        "Click a recording to select it, rename or export it, and set "
        "its own 'Repeat until stopped' switch. The play shortcut "
        "(Ctrl+Alt+M) replays the recording selected there; Ctrl+1 to "
        "Ctrl+5 replay by position in the list. Paused, nothing is "
        "recorded and nothing is injected - your input is entirely "
        "yours.",
    "kb.keys.t": "Single keys versus key combos",
    "kb.keys.b":
        "A shortcut that includes Ctrl, Alt, Shift or Win is reserved "
        "system-wide: only Snappy AI sees it. A bare single key (like "
        "1 or 2) works in every program AND still types normally - the "
        "trade-off is that typing that key mid-sentence also triggers "
        "its action. If you would rather have classic behaviour, turn "
        "on 'Single-key shortcuts swallow the key' on the Assistance "
        "tab. Macros go one step further: while launched, the trigger "
        "key is swallowed and the combo beside it is sent exactly "
        "once.",

    "help.title": "Tuning Snappy AI in plain words",
    "help.sub":
        "Every setting by the name you see on its tab, in the order "
        "you will want it. Hover a setting name for its one-line "
        "description; this page is the long form.",
    "help.tail":
        "Settings apply when you press Apply. A config.ini beside the "
        "program overrides config.json. This page explains; it does "
        "not configure.",
    "help.1.t": "What happens when you click",
    "help.1.b":
        "Snappy AI looks at the screen around your cursor, finds the "
        "solid item-shaped things near it - buttons, icons, links - "
        "and picks the best one: crisp edges, a decent size and close "
        "to your cursor win. Your colour, the never-click list and the "
        "memory of your last click can tilt the choice. The cursor is "
        "then aimed at the middle of the item, not at the corner of "
        "its box.",
    "help.2.t": "Start here: mode and search distance",
    "help.2.b":
        "Guide mode (the default) never eats a click: your click "
        "reaches the program and, after you release, the cursor moves "
        "onto the nearest clear item. Classic mode is stronger: a "
        "mis-click near an item is caught, the cursor snaps onto the "
        "item and Snappy AI clicks it for you. 'How far from the "
        "cursor to look' decides the search circle - raise it when the "
        "item you want is just out of reach, lower it when the wrong "
        "neighbour wins. Holding Shift bypasses one click in both "
        "modes.",
    "help.3.t": "Nothing is found - or too much is",
    "help.3.b":
        "On the Handler tab, 'How faint an edge may be' and 'Minimum "
        "edge strength' decide which edges count at all: lower them to "
        "find fainter items, raise them to ignore noise. 'Smallest "
        "item size', 'Largest item size' and 'Largest item width or "
        "height' drop specks and whole windows. 'Glue nearby pieces "
        "together' joins a broken outline, or an icon beside its "
        "label, into one item. On the Assistance tab, 'Auto-adjust for "
        "dim screens' and 'Judge edges by relative brightness' make "
        "dark themes behave like light ones - keep both on.",
    "help.4.t": "Working with colours",
    "help.4.b":
        "On the Colors tab, 'My colour(s)' is the colour Snappy AI "
        "prefers and 'Never-click colour(s)' is absolute: items with "
        "that colour are never assisted. 'Only assist my colour' "
        "restricts assistance to matching items. On the Handler tab, "
        "'Colour match strictness' says how close a shade must be, "
        "'Accept near-miss shades' lets lighter or washed-out versions "
        "count partly, and 'Colour tie-break strength' says how much "
        "your colour lifts an item - raise it when the wrong item "
        "still wins.",
    "help.5.t": "Repeated clicks on one control",
    "help.5.b":
        "'Remember the last clicked item' keeps preferring the item "
        "your last successful click landed on, for 'How long to "
        "remember' seconds - this is what makes scrollbars and dialog "
        "buttons pleasant. 'Memory strength' says how strongly it "
        "wins, and 'What the memory may learn' protects it: with 'Only "
        "items in my colour', a misclick cannot retarget it. 'Keep "
        "following while the button is held' steadies drags, and the "
        "right-button actions on the Experimental tab can follow or "
        "clear the memory by mouse.",
    "help.6.t": "Clicking moving things",
    "help.6.b":
        "'Lead moving items' measures how fast the chosen item travels "
        "and aims ahead by 'How far ahead to aim' milliseconds, so the "
        "click lands on a scrolling list or a video seek bar instead "
        "of behind it. The lead caps at 80 pixels and switches itself "
        "off for still or turning items.",
    "help.7.t": "How clicks feel",
    "help.7.b":
        "'Animate cursor moves' = 0 jumps instantly; 40-120 glides so "
        "you can watch, and moving the mouse yourself cancels the "
        "glide. 'Double-click window' turns a second snap near the "
        "same spot into a double-click in classic mode. 'Assist every "
        "click in a fast burst' assists every click of a rapid series "
        "instead of only the first. 'Pause after a hiccup' is the "
        "safety valve that gives a held click back if a scan ever "
        "stalls.",
    "help.8.t": "Keys, macros and recordings",
    "help.8.b":
        "The Keybindings tab explains the two modes and the recording "
        "workflow. In short: shortcuts with Ctrl, Alt, Shift or Win "
        "are reserved system-wide; bare single keys fire everywhere "
        "and still type. A macro turns one blocked key press into one "
        "whole combo. Recordings capture your real input - every key, "
        "mouse click and cursor move - and replay it from the Macros "
        "tab, each with its own play-once or repeat-until-stopped "
        "switch.",
    "help.9.t": "Language",
    "help.9.b":
        "The Language button - beside Export Config, and on the "
        "sign-in and subscription windows too - switches the whole "
        "interface at once, without restarting, and remembers your "
        "choice. Languages that are still being translated are not "
        "offered, so anything you can pick is complete.",
    "help.10.t": "When it misbehaves, check in this order",
    "help.10.b":
        "1. Is it launched? Paused means nothing is intercepted - "
        "'Shortcut: start assisting' (Ctrl+L by default) is the only "
        "on/off.  2. Hold Shift for one click to confirm the "
        "assistance was the problem.  3. Wrong item wins: lower 'How "
        "far from the cursor to look', then set 'My colour(s)' or "
        "raise 'Colour tie-break strength'.  4. Nothing is found: "
        "lower 'How faint an edge may be' and 'Minimum edge strength', "
        "raise 'Largest item width or height', or raise 'Glue nearby "
        "pieces together'.  5. One thing must never be assisted: put "
        "its colour in 'Never-click colour(s)'.  6. Still wrong: tell "
        "support what you clicked and what you expected instead, and "
        "include the log file Snappy AI writes to its data folder.",

    "login.title": "%s - Sign in",
    "login.sub": "Sign in with Discord - your subscription is bound to "
                 "this account, and payments must use its e-mail "
                 "address. No password here.",
    "login.note": "The sign-in opens your browser and comes back to "
                  "this window on its own.",
    "login.provider": "Sign in with %s",
    "login.waiting": "Waiting for the browser - finish the %s sign-in...",
    "login.signedin": "Signed in as %s.",
    "login.failed": "%s sign-in did not complete - try again.",
    "login.unreachable": "Auth server unreachable: %s",

    "gate.title": "%s - Subscription%s",
    "gate.prices": "2-day trial: 1.99\u20ac (one time)  -  subscription: "
                   "9.99\u20ac / month.\nActivation lands up to ~10 "
                   "minutes after payment; renewals re-enable this same "
                   "login automatically.",
    "gate.btn.monthly": "Monthly Subscription for 9.99\u20ac",
    "gate.btn.trial": "Trial Purchase for 1.99\u20ac",
    # gate.btn.recheck / gate.btn.activate (the manual "Re-check now"
    # and "I paid - activate now" buttons) are gone: the gate re-checks
    # by itself every 30 seconds, so no key is registered for them in
    # any locale.
    "gate.note": "The engine starts as soon as the subscription is "
                 "active - this window re-checks by itself every 30 "
                 "seconds. Closing it returns to sign-in.",
    "gate.head.shared":
        "This account is in use on ANOTHER computer right now. Snappy "
        "AI stays off while the same Discord account runs it in two "
        "places at once - close the other session, then re-check. "
        "Sharing subscriptions is what keeps prices up; please don't.",
    "gate.head.refunded":
        "This purchase was refunded or charged back, so the entitlement "
        "was revoked. A new subscription on this Discord e-mail "
        "re-activates it.",
    "gate.head.canceling":
        "Your subscription is set to cancel - it stays active until "
        "%s, then this login locks again unless you renew.",
    "gate.head.email_mismatch":
        "The payment was made with a different e-mail than your Discord "
        "account. Subscriptions only work on the Discord e-mail shown "
        "below - re-subscribe with it, or contact support.",
    "gate.head.expired":
        "Your subscription for this login expired - renew it on Stripe "
        "to continue.",
    "gate.head.past_due":
        "The last subscription payment failed - fix it on Stripe to "
        "re-enable this login.",
    "gate.head.canceled":
        "This subscription was canceled - start a new one on Stripe to "
        "continue.",
    "gate.head.none":
        "You are signed in, but this login has no active subscription. "
        "Pay with THIS Discord e-mail - a purchase on any other address "
        "cannot activate it.",
    "gate.msg.checking": "Checking with the server...",
    "gate.msg.open_ok": "Stripe is open in your browser - pay there. "
                        "This window notices the payment by itself and "
                        "starts the engine.",
    "gate.msg.open_fail": "Could not open a browser. Open this link by "
                          "hand:\n%s",
    "gate.msg.no_link": "That payment link is not configured on this "
                        "build.",
    # gate.msg.dispatching / gate.msg.no_dispatch / gate.msg.not_live
    # belonged to the removed "I paid - activate now" flow; the 30 s
    # auto re-check covers activation, so no locale registers them.
    "gate.msg.unreachable": "Auth server unreachable: %s",
    "gate.msg.session_gone": "Session gone - sign in again.",
    "gate.msg.active": "Subscription active - starting Snappy AI...",
    "gate.msg.still_shared": "Still in use on another computer - close "
                             "that session, then re-check.",
    "gate.msg.still_none": "Still no active subscription for this "
                           "login.",

    "shared.title": "Account in use elsewhere",
    "shared.body":
        "This Discord account is running Snappy AI on another computer "
        "right now.\nAssistance is paused here until only one session "
        "remains.\n\nOne subscription, one machine at a time - that "
        "is what keeps\nthe price down and the development going.",
    "shared.recheck": "Re-check now",
    "shared.close": "Close",
    "shared.back": "Welcome back - press Launch when ready.",
    "shared.still": "Still in use elsewhere - staying paused.",
    "shared.unreachable": "Server unreachable - will re-check.",
    "theme.light": "Light",
    "theme.dark": "Dark",
    "hdr.build": "build %s",
    "st.registered": "Registered to: %s    Status: %s",
    "mac.row": "Macro %d",
    "err.auth_unreachable": "The Snappy AI auth server is "
                            "unreachable:\n%s\n\nSnappy AI only runs "
                            "with a live answer from it.\nRetry?",
    "err.start_fail": "Snappy AI could not start.\nRun with --console "
                      "to see details.",

    "st.engine_dead": "Engine thread unavailable - hotkeys will not "
                      "respond.",
    "st.ini_over": "Applied, but config.ini overrides: %s",
    "st.saved_bad": "Saved, but invalid (old kept): %s",
    "st.saved": "Saved and applied.",
    # v8.49: st.accent_set / st.exclude_set / st.loaded / st.loaded_none
    # were deleted here. They died in the v8.43-8.44 picker rework (the
    # chip strip and "Add to preferred colours" replaced "Set as accent" /
    # "Load accent"), but stayed in PROSE - which is not harmless: PROSE is
    # published into the ENGLISH catalog, and run_gui registers every
    # English key as required, so one stale string here drops all 15 other
    # locales below the 100% bar and silently hides every language from the
    # chooser. i18n.diagnose() now reports that drift at start-up.
    "st.exported": "Settings exported to %s",
    "st.export_fail": "Export failed: %r",
    "st.select_rec": "Select a recording first.",
    "st.name_empty": "The name must not be empty.",
    "st.renamed": "Recording renamed.",
    "st.deleted": "Recording deleted.",
    "st.lib_empty": "Library is empty - nothing to export.",
    "st.rec_now": "%r now %s.",
    "st.rec_repeats": "repeats until stopped",
    "st.rec_once": "plays once",
    "st.rec_recording": "RECORDING - press %s to stop and save",
    "st.rec_playing_loop": "Playing %r until stopped",
    "st.rec_playing": "Playing %r...",
    "st.rec_count": "%d of 5 recordings",
    "st.pick_wait": "Move the cursor onto the colour - capturing in "
                    "3 s...",
    "st.pick_ok": "Picked rgb(%d, %d, %d) at (%d, %d).",
    "st.pick_fail": "Capture failed - try again.",
    "st.pick_err": "Pick failed: %r",
    "st.sug_wait": "Point at the app you work in - sampling in 3 s...",
    "st.sug_none": "No colour suggestions from this region.",
    "st.sug_ok": "%d suggestions - click one to load it into the "
                 "picker.",
    "st.sug_fail": "Suggest failed: %r",
    "st.rgb_bad": "Enter valid R/G/B values first.",
    "st.sug_loaded": "Suggestion rgb(%d, %d, %d) is in the picker - "
                     "add it to a list with the buttons above.",
    "st.sug_loaded_desc": "Suggested UI colour rgb(%d, %d, %d) - %d%% "
                          "of the sampled region. Click to load it "
                          "into the picker.",
    "st.preset_desc": "Preset swatch: %s - click to load it into the "
                      "picker.",
    "st.loop_desc": "This recording's playback style: off = play once; "
                    "on = repeat until you press the play shortcut "
                    "again. Each recording has its own switch, saved "
                    "with the recording itself.",
    "st.delete_confirm": "Delete recording %r?\nThis cannot be undone.",
    "st.rename_prompt": "New name for recording #%d:",
    "st.reset_confirm": "Reset every setting to its default?\nAccounts "
                        "are kept; this only affects settings.",
    "st.export_title": "Export settings",
    "st.import_title": "Import settings",
    "st.export_rec_title": "Export recording",
    "st.import_rec_title": "Import recording(s)",
    "st.file_settings": "Snappy AI settings",
    "st.file_rec": "Snappy AI recording",
    "st.all_files": "All files",
    "st.shared_paused": "ACCOUNT IN USE ELSEWHERE - assistance paused; "
                        "one subscription = one machine at a time.",
    "st.ent_paused": "Subscription %s - assistance paused. Re-subscribe "
                     "on Stripe, then restart.",
    "st.ent_unreachable": "Entitlement re-check: server unreachable "
                          "(session keeps running).",
    "login.not_configured": "The subscription file is not configured on "
                            "this build yet.",
    "login.no_provider": "No sign-in provider is built into this copy.",
}

i18n.publish("en", PROSE)
# Descriptions: concrete keys for real settings, pattern keys for the
# generated macro/play families (see desc_key).
i18n.publish("en", {"desc." + k: META[k][1] for k in META
                    if desc_key(k) == "desc." + k})
# Dropdown values are text the user reads, so they are catalog keys.
# The four follow_boost steps are pure percentages - language-neutral -
# so every locale receives them from English instead of carrying four
# identical strings sixteen times.
_VALS = {}
for _k in META:
    if META[_k][2] == "map":
        for _d, _v in META[_k][3]:
            _VALS[val_key(_k, _v)] = _d
i18n.publish("en", _VALS)
for _c in i18n.codes():
    for _k, _v in _VALS.items():
        if _k.startswith("val.follow_boost."):
            i18n.STRINGS[_c].setdefault(_k, _v)

i18n.publish("en", {"lbl.macro_key": "Macro %d: press this key",
                     "lbl.macro_action": "Macro %d: sends this instead",
                     "lbl.key_play_n": "Shortcut: play recording #%d",
                     "desc.macro_key": META["macro1_key"][1],
                     "desc.macro_action": META["macro1_action"][1],
                     "desc.key_play_n": META["key_play1"][1]
                     .replace("#1", "#%d")})

DESC_DEFAULT = "Hover over a setting name to see what it does."

# Clickable preset swatches on the Color Picker tab.
# v8.45: FIFTEEN premade swatches - the owner's alignment grid is 15
# boxes wide (the colour lists hold 15, the suggestions show 15, the
# R,G,B row is 3 boxes of 5 units each), so the preset row joins it:
# 15 swatches, one exact 15-box span.  Four new material tones fill
# the gaps in the rainbow: lime, teal, indigo, brown.
COLOR_PRESETS = [
    ("red", (229, 57, 53)), ("orange", (255, 152, 0)),
    ("yellow", (253, 216, 53)), ("lime", (192, 202, 51)),
    ("green", (67, 160, 71)), ("teal", (0, 137, 123)),
    ("cyan", (0, 183, 199)), ("blue", (30, 136, 229)),
    ("indigo", (57, 73, 171)), ("purple", (142, 36, 170)),
    ("pink", (216, 27, 96)), ("brown", (121, 85, 72)),
    ("grey", (158, 158, 158)), ("white", (245, 245, 245)),
    ("black", (33, 33, 33)),
]


def _surf_of(widget, fallback="#ffffff"):
    """Live background colour of a widget's parent surface."""
    try:
        parent = widget.nametowidget(widget.winfo_parent())
        return str(parent.cget("bg"))
    except Exception:
        return fallback


# ----------------------------------------------------------------------
def _wrapping_note(parent, kit, pal, key, pady=(10, 2), padx=12):
    """Full-width muted page note that wraps to whatever room it has.

    A bare tk.Label sizes itself to its whole text: wider than the
    window it gets centred and clipped on BOTH ends (the page notes
    looked like that for as long as they were single-line labels).
    This one fills the page row and re-fits its wraplength whenever the
    page is resized, so the note always wraps inside the window - at
    980 px and at the 640 px minimum alike.
    """
    lb = tk.Label(parent, font=F_DESC, bg=pal["card"], fg=pal["muted"],
                  text=i18n.L(key), justify="left", anchor="w")
    kit.reg(lb, "card_muted")
    R(lambda: lb.configure(text=i18n.L(key)) if _live(lb) else False)

    def _fit(_event=None):
        try:
            w = lb.master.winfo_width()
            if w > 60:
                want = max(120, w - 2 * padx - 4)
                if str(lb.cget("wraplength")) != str(want):
                    lb.configure(wraplength=want)
        except Exception:
            pass

    lb.pack(fill="x", padx=padx, pady=pady)
    lb.bind("<Configure>", _fit)
    lb.master.bind("<Configure>", _fit, add="+")
    _fit()
    return lb


# ----------------------------------------------------------------------
# Help tab (v8.38): the tuning guide
#
# Read-only prose, in the order a person actually tunes the product:
# what a scan does, then the knobs grouped by the stage of the scan
# they move.  Defaults and ranges quoted here are the enforced ones
# (DEFAULT_CONFIG / Config._RANGES), so this page cannot drift from the
# engine without somebody editing both.
# ----------------------------------------------------------------------

HELP_KEYS = [("help.%d.t" % i, "help.%d.b" % i) for i in range(1, 11)]
KB_KEYS = [("kb.mode.t", "kb.mode.b"), ("kb.rec.t", "kb.rec.b"),
           ("kb.keys.t", "kb.keys.b")]


def _scrollable(page, kit, pal):
    """(inner frame, wheel-binder) for a vertically scrollable page.

    Every other tab fits the window; a page of tuning prose does not,
    so Help gets a canvas plus a themed scrollbar.  The wheel is bound
    per widget (Tk delivers the event to whatever is under the pointer,
    which here is usually a label, not the canvas) and the step is a
    fraction of the content height, so one notch moves the same distance
    on Windows (<MouseWheel>, delta in +-120 multiples) and on X11
    (Button-4 / Button-5)."""
    host = tk.Frame(page, bg=pal["card"])
    kit.reg(host, "card")
    host.pack(fill="both", expand=True)

    bar = ttk.Scrollbar(host, orient="vertical")
    cvs = tk.Canvas(host, highlightthickness=0, takefocus=0, bd=0,
                    bg=pal["card"], yscrollcommand=bar.set)
    kit.reg(cvs, "canvas_card")
    bar.configure(command=cvs.yview)
    bar.pack(side="right", fill="y")
    cvs.pack(side="left", fill="both", expand=True)

    inner = tk.Frame(cvs, bg=pal["card"])
    kit.reg(inner, "card")
    win = cvs.create_window(0, 0, anchor="nw", window=inner)

    def _fit(_event=None):
        try:
            cvs.itemconfigure(win, width=max(120, cvs.winfo_width()))
            cvs.configure(scrollregion=cvs.bbox("all"))
        except tk.TclError:
            pass

    inner.bind("<Configure>", _fit)
    cvs.bind("<Configure>", _fit)

    def _wheel(step):
        try:
            total = max(1, inner.winfo_height())
            low, _high = cvs.yview()
            frac = low + (step * 60.0 / total)
            cvs.yview_moveto(min(1.0, max(0.0, frac)))
        except tk.TclError:
            pass

    def bind_wheel(widget):
        widget.bind("<MouseWheel>", lambda e: _wheel(-int(e.delta) // 120))
        widget.bind("<Button-4>", lambda e: _wheel(-1))
        widget.bind("<Button-5>", lambda e: _wheel(1))

    bind_wheel(cvs)
    return inner, bind_wheel


def _fill_help(page, kit, pal):
    """Build the read-only Help tab: title, then HELP_KEYS as heading +
    wrapping body pairs on a scrollable card.  Every label re-texts
    live, so a language switch re-words the page in place."""
    inner, bind_wheel = _scrollable(page, kit, pal)
    bodies = []

    def para(parent, key, font, role, pady, wheel=True):
        lb = tk.Label(parent, text=i18n.L(key), font=font,
                      bg=pal["card"],
                      fg=pal["text"] if role != "card_muted"
                      else pal["muted"],
                      anchor="w", justify="left")
        kit.reg(lb, role)
        lb.pack(fill="x", padx=14, pady=pady)
        if wheel:
            bind_wheel(lb)
        R(lambda: lb.configure(text=i18n.L(key)) if _live(lb) else False)
        bodies.append(lb)
        return lb

    head = tk.Label(inner, text=i18n.L("help.title"), font=F_H1,
                    bg=pal["card"], fg=pal["text"], anchor="w")
    kit.reg(head, "card_text")
    head.pack(fill="x", padx=14, pady=(12, 0))
    bind_wheel(head)
    R(lambda: head.configure(text=i18n.L("help.title")) if _live(head)
      else False)

    para(inner, "help.sub", F_DESC, "card_muted", (2, 4))
    for tk_, bk_ in HELP_KEYS:
        h = tk.Label(inner, text=i18n.L(tk_), font=F_BOLD, bg=pal["card"],
                     fg=pal["text"], anchor="w")
        kit.reg(h, "card_bold")
        h.pack(fill="x", padx=14, pady=(12, 2))
        bind_wheel(h)
        R(lambda h=h, k=tk_: h.configure(text=i18n.L(k)) if _live(h)
          else False)
        para(inner, bk_, F_DESC, "card_muted", (0, 2))
    para(inner, "help.tail", F_DESC, "card_muted", (14, 12))

    def _rewrap(_event=None):
        """Wrap every paragraph to the width the canvas actually gave
        the inner frame - the same fix _wrapping_note applies to the
        tab notes, for a page that resizes with the window."""
        try:
            want = max(200, inner.winfo_width() - 32)
            for lb in bodies:
                if str(lb.cget("wraplength")) != str(want):
                    lb.configure(wraplength=want)
        except tk.TclError:
            pass

    inner.bind("<Configure>", _rewrap, add="+")
    _rewrap()
    return inner


# ThemeKit: live theme, rounded buttons, role-based restyle
# ----------------------------------------------------------------------

class ThemeKit:
    # v8.45: the pill height of a normal (non-big) rounded button, as a
    # class constant - the Colors tab's right column is pixel
    # arithmetic (its showcase height solves so the suggestion boxes
    # end level with the hue slider), so the layout may not guess the
    # button height, it has to KNOW it.
    BTN_H = 31

    def __init__(self, cfg):
        self.cfg = cfg
        self.pal = dict(THEMES[str(cfg.get("theme", "light"))])
        self.roots = []
        self.repaints = []
        self._img_cache = {}

    # -- palette / windows -------------------------------------------
    def attach(self, root):
        self.roots.append(root)
        return root

    def reg(self, widget, role):
        try:
            widget._tkrole = role
        except Exception:
            pass
        return widget

    def repaint(self, fn):
        self.repaints.append(fn)
        return fn

    def current(self):
        return "dark" if self.pal.get("bg") == THEMES["dark"]["bg"] \
            else "light"

    def switch_to(self, name):
        self.pal.clear()
        self.pal.update(THEMES[name])
        self.cfg.set("theme", name, save=True)
        self.apply()

    def toggle(self):
        self.switch_to("dark" if self.current() == "light" else "light")

    def apply(self):
        for root in list(self.roots):
            try:
                if not root.winfo_exists():
                    self.roots.remove(root)
                    continue
                self._walk(root)
            except tk.TclError:
                pass
        # v8.46: iterate a COPY - repaint callbacks may add or remove
        # entries while they run (the Macros recorder rows rebuild
        # themselves and prune their own switches' paint callbacks).
        for fn in list(self.repaints):
            try:
                fn()
            except tk.TclError:
                pass

    def _walk(self, w):
        # v8.46: destroyed widgets are skipped - the recorder rows are
        # rebuilt dynamically, and configuring a dead widget would
        # abort the whole theme walk.
        try:
            if not w.winfo_exists():
                return
        except tk.TclError:
            return
        role = getattr(w, "_tkrole", None)
        if role:
            self._style_one(w, role)
        for c in w.winfo_children():
            self._walk(c)

    def _style_one(self, w, role):
        pal = self.pal
        if role == "bg":
            w.configure(bg=pal["bg"])
        elif role == "bg_text":
            w.configure(bg=pal["bg"], fg=pal["text"])
        elif role == "canvas_bg":
            w.configure(bg=pal["bg"])
        elif role == "card":
            w.configure(bg=pal["card"])
        elif role == "card_text":
            w.configure(bg=pal["card"], fg=pal["text"])
        elif role == "card_muted":
            w.configure(bg=pal["card"], fg=pal["muted"])
        elif role == "card_bold":
            w.configure(bg=pal["card"], fg=pal["text"])
        elif role == "entry":
            # v8.42: readonlybackground too, so a themed read-only
            # Entry takes its colour from that option, not from bg.
            # (v8.43 turned the Current RGB Value row into colour
            # boxes, but the option stays correct for any read-only
            # field the product grows later.)
            w.configure(bg=pal["entry"], fg=pal["text"],
                        insertbackground=pal["text"],
                        readonlybackground=pal["entry"],
                        highlightbackground=pal["entry_bd"])
        elif role == "check":
            w.configure(bg=pal["card"], fg=pal["muted"],
                        selectcolor=pal["entry"],
                        activebackground=pal["card"])
        elif role == "listbox":
            w.configure(bg=pal["entry"], fg=pal["text"],
                        highlightbackground=pal["entry_bd"],
                        selectbackground=pal["accent"],
                        selectforeground="#ffffff")
        elif role == "desc":
            w.configure(bg=pal["desc_bg"], fg=pal["muted"])
        elif role == "desc_frame":
            # v8.39: the row that carries the description bar AND the
            # Apply button; bg-only, like status_frame.
            w.configure(bg=pal["desc_bg"])
        elif role == "status":
            w.configure(bg=pal["status_bg"], fg=pal["muted"])
        elif role == "status_frame":
            # v8.34: the status bar became a Frame holding two Labels, so
            # it needs a bg-only role - "status" also sets fg, which a
            # Frame has no option for and would raise inside the theme
            # walk (aborting the restyle of every widget after it).
            w.configure(bg=pal["status_bg"])
        elif role == "canvas_card":
            w.configure(bg=pal["card"])
        elif role == "panel":
            # v8.46: a bordered panel on the card - the Macros tab's
            # recordings box (bg + border only; a Frame has no fg).
            w.configure(bg=pal["card"],
                        highlightbackground=pal["entry_bd"])
        elif role == "hl":
            w.configure(highlightbackground=pal["entry_bd"])
        elif role in ("btn", "btn_accent", "btn_green", "btn_amber"):
            meta = getattr(w, "_rmeta", None)
            bg, fg = self._btn_colors(role)
            surface = pal[meta[2]] if meta else pal["card"]
            w.configure(fg=fg, bg=surface, activebackground=surface,
                        activeforeground=fg, bd=0)
            if meta and HAVE_PIL:
                try:
                    img = self.rounded(meta[3], meta[4], bg, 7)
                    w.configure(image=img)
                    w._img = img
                except Exception:
                    pass

    def _btn_colors(self, role):
        pal = self.pal
        if role == "btn_accent":
            return pal["accent"], "#ffffff"
        if role == "btn_green":
            return pal["green"], "#ffffff"
        if role == "btn_amber":
            return pal["amber"], "#ffffff"
        return pal["light_bg"], pal["text"]

    # -- rounded corner images ----------------------------------------
    def rounded(self, width, height, fill_hex, radius=7):
        key = (width, height, fill_hex, radius)
        if key not in self._img_cache:
            img = _PILImage.new("RGBA", (width, height), (0, 0, 0, 0))
            d = _PILDraw.Draw(img)
            d.rounded_rectangle((0, 0, width - 1, height - 1),
                                radius=radius,
                                fill=hex2rgb(fill_hex) + (255,))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            self._img_cache[key] = buf.getvalue()
        return tk.PhotoImage(data=self._img_cache[key])

    def button(self, parent, text, command, kind="plain", big=False,
               surface="card", fixed_w=None):
        """Rounded, flash-free, focus-ring-free button.

        v8.45: `fixed_w` pins the pill to an exact pixel width no
        matter what the label says - the Colors tab's four screen/add
        buttons are all one size and together span exactly the
        fifteen-box grid, so their width is layout arithmetic, not a
        text measurement.  The pin survives live language switching
        (set_text re-draws at the same width)."""
        role = {"plain": "btn", "accent": "btn_accent",
                "green": "btn_green", "amber": "btn_amber"}[kind]
        bg, fg = self._btn_colors(role)
        surf = self.pal[surface]
        b = tk.Button(parent, text=text, relief="flat", bd=0,
                      font=(F_BTN_BIG if big else F_BTN),
                      bg=surf, fg=fg, activebackground=surf,
                      activeforeground=fg, highlightthickness=0,
                      takefocus=0, cursor="hand2", compound="center",
                      padx=0, pady=0,
                      disabledforeground="#9aa0a6")
        f = tkfont.Font(font=(F_BTN_BIG if big else F_BTN))
        w = int(fixed_w) if fixed_w else \
            int(f.measure(text)) + (44 if big else 30)
        h = 40 if big else self.BTN_H
        b._rmeta = (text, big, surface, w, h, role)
        if fixed_w:
            b._fixed_w = int(fixed_w)
        if HAVE_PIL:
            try:
                img = self.rounded(w, h, bg, 7)
                b.configure(image=img)
                b._img = img
            except Exception:
                pass
        b.configure(command=command)
        return self.reg(b, role)

    def _draw_pill(self, cvs, right, track_hex, knob_hex):
        """Paint one pill track (SW_W x SW_H) with its knob on the left
        (`right` false) or on the RIGHT (`right` true).

        Shared by the Light/Dark switch and the Assistance tab's on/off
        switches, so the two control families can never drift apart.
        Keeps a reference to the rounded-track PhotoImage on the canvas:
        Tk frees an image nothing holds, which would blank the track on
        the next idle cycle.  Without Pillow the track degrades to a
        plain rectangle - the state is still legible, only the corners
        are square."""
        cvs.delete("all")
        if HAVE_PIL:
            img = self.rounded(SW_W, SW_H, track_hex, SW_RADIUS)
            cvs.create_image(0, 0, anchor="nw", image=img)
            cvs._track = img
        else:
            cvs.create_rectangle(0, 0, SW_W - 1, SW_H - 1,
                                 fill=track_hex, outline="")
        x = (SW_W - SW_PAD - SW_KNOB) if right else SW_PAD
        cvs.create_oval(x, SW_PAD, x + SW_KNOB, SW_PAD + SW_KNOB,
                        fill=knob_hex, outline="")

    def set_text(self, b, text):
        """Swap a rounded button's label and resize its pill to fit.

        The one place that knows a button's measured geometry (_rmeta),
        so live language switching and the Colors tab's Set/Load
        retitling share it instead of each re-measuring."""
        meta = getattr(b, "_rmeta", None)
        b.configure(text=text)
        if meta is None:
            return
        _t, big, surface, _w, h, role = meta
        bg, _fg = self._btn_colors(role)
        f = tkfont.Font(font=(F_BTN_BIG if big else F_BTN))
        # v8.45: a fixed-width button keeps its width in every
        # language - only the label (and its pill image) is swapped.
        w = getattr(b, "_fixed_w", None) or \
            int(f.measure(text)) + (44 if big else 30)
        if HAVE_PIL:
            try:
                img = self.rounded(w, h, bg, 7)
                b.configure(image=img)
                b._img = img
            except Exception:
                pass
        b._rmeta = (text, big, surface, w, h, role)

    def switch_widget(self, parent, on_toggle):
        """Light [pill switch] Dark control; grey rounded track."""
        pal = self.pal
        f = tk.Frame(parent, bg=pal["card"])
        self.reg(f, "card")
        left = tk.Label(f, text=i18n.L("theme.light"), font=F_DESC,
                        bg=pal["card"], fg=pal["text"])
        self.reg(left, "card_text")
        R(lambda: left.configure(text=i18n.L("theme.light"))
          if _live(left) else False)
        cvs = tk.Canvas(f, width=SW_W, height=SW_H, highlightthickness=0,
                        takefocus=0, bg=pal["card"])
        self.reg(cvs, "canvas_card")
        right = tk.Label(f, text=i18n.L("theme.dark"), font=F_DESC,
                         bg=pal["card"], fg=pal["text"])
        self.reg(right, "card_text")
        R(lambda: right.configure(text=i18n.L("theme.dark"))
          if _live(right) else False)
        left.pack(side="left", padx=(0, 6))
        cvs.pack(side="left")
        right.pack(side="left", padx=(6, 0))

        def paint():
            dark = self.current() == "dark"
            self._draw_pill(cvs, dark, self.pal["light_bg"],
                            self.pal["text"] if dark else "#ffffff")

        self.repaint(paint)
        for w in (cvs, left, right):
            w.bind("<Button-1>", lambda e: (on_toggle(), paint()))
        paint()
        return f

    def bool_switch(self, parent, var, word=True):
        """An on/off pill switch bound to a tk.BooleanVar.

        Replaces the Assistance tab's "On" checkboxes with the same
        control the header uses for Light/Dark:

          * knob ON THE RIGHT  = the setting is ON, and the track fills
            with pal["switch_on"] - the red sampled from the logo;
          * knob on the left   = off, on the neutral light_bg track.

        `var` stays the single source of truth, so the switch follows
        refresh_fields(), a config reload, an import and Restore
        Defaults exactly like the checkbox did: it repaints from a trace
        on the var, and a click only ever WRITES the var - which is what
        fires the caller's dirty trace and makes Apply appear.

        `word` puts a small On/Off label beside the pill.  The state is
        already colour-coded, and colour alone is not an accessible
        encoding in a product whose users have low vision, so the word
        stays on by default; pass word=False for the pill alone.
        Returns the frame to grid/pack (the pill is always its
        right-most child, so a column of switches lines up)."""
        pal = self.pal
        f = tk.Frame(parent, bg=pal["card"])
        self.reg(f, "card")

        lbl = None
        if word:
            lbl = tk.Label(f, text=i18n.L("word.off"), width=3, anchor="e",
                           font=F_DESC, bg=pal["card"], fg=pal["muted"])
            self.reg(lbl, "card_muted")
            lbl.pack(side="left", padx=(0, 6))

        cvs = tk.Canvas(f, width=SW_W, height=SW_H, highlightthickness=0,
                        takefocus=0, bd=0, bg=pal["card"], cursor="hand2")
        self.reg(cvs, "canvas_card")
        cvs.pack(side="left")

        def paint(*_a):
            try:
                if not cvs.winfo_exists():
                    return
            except tk.TclError:
                return                  # window closed mid-repaint
            try:
                on = bool(var.get())
            except (tk.TclError, ValueError):
                on = False              # a bad hand-edited value reads off
            pal = self.pal
            self._draw_pill(
                cvs, on,
                pal["switch_on"] if on else pal["light_bg"],
                "#ffffff" if (on or self.current() == "light")
                else pal["text"])
            if lbl is not None:
                try:
                    lbl.configure(text=i18n.L("word.on") if on
                                  else i18n.L("word.off"),
                                  fg=pal["switch_on"] if on
                                  else pal["muted"])
                except tk.TclError:
                    pass

        def toggle(_event=None):
            try:
                var.set(not bool(var.get()))
            except (tk.TclError, ValueError):
                var.set(True)
            paint()

        for w in ([cvs, lbl] if lbl is not None else [cvs]):
            w.bind("<Button-1>", toggle)
        # space/return for anyone who tabs to the pill (it is takefocus=0
        # like every other control here, so this only fires once a
        # future build makes it focusable - harmless until then)
        cvs.bind("<space>", toggle)
        cvs.bind("<Return>", toggle)

        var.trace_add("write", paint)   # programmatic sets repaint too
        self.repaint(paint)             # ...and so does a theme switch
        paint()
        return f

    def titlebar_hook(self, root):
        """Re-colour the window title bar on every theme change."""
        def _apply():
            try:
                if not root.winfo_exists():
                    return
                hwnd = int(root.frame(), 16)
                apply_window_theme(hwnd, self.current() == "dark",
                                   hex2rgb(self.pal["bg"]),
                                   hex2rgb(self.pal["text"]))
            except Exception:
                pass
        self.repaint(_apply)
        try:
            root.update_idletasks()   # window must exist for DWM
        except Exception:
            pass
        _apply()
        try:
            root.after(150, _apply)   # and again once fully mapped
        except Exception:
            pass

    def defocus_hook(self, root):
        """Clicking a button must not leave a focus ring behind."""
        def _defocus(event):
            try:
                if event.widget.winfo_class() in ("Button", "Checkbutton"):
                    event.widget.winfo_toplevel().focus_set()
            except Exception:
                pass
        root.bind("<ButtonRelease-1>", _defocus)


# ----------------------------------------------------------------------
# sign-in
# ----------------------------------------------------------------------

def _clipboard_put(root, text):
    """Best-effort clipboard write; True when the text took."""
    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()                  # survives the window closing
        return True
    except Exception:
        return False


def registration_line(identity, ent):
    """One line: who is signed in, and what their licence is doing.

    v8.34: this was two lines in the header card (the e-mail, then the
    licence status). Moving it to the right end of the status bar keeps
    both facts a support message needs on screen, in the same face as
    the counters beside it, and stops the header carrying any text long
    enough to wrap - which is what made the 74 px card tight in the
    first place.

    Defensive on purpose: this runs inside a Tk `after` callback fed by
    online.me(), and me() legitimately returns (None, None) when the
    session died server-side. An exception here would surface as a
    callback traceback on every 30-minute re-check."""
    try:
        who = online.identity_label(identity) if identity else ""
    except Exception:
        who = ""
    return i18n.L("st.registered",
                  (who or "").strip() or "unknown",
                  online.entitlement_summary(ent))


def _language_window(cfg, kit, parent):
    """Chooser for the live interface language (v8.39).

    One row per locale: native name (the one a person recognises as
    theirs), English name, and how much of the interface that locale
    actually carries - computed, not claimed.  Clicking a row switches
    the WHOLE application at once, this window included, because every
    visible string re-registers itself through R(); nothing restarts.
    The window stays open on purpose: picking a language you cannot
    yet read is exactly when you want to see the result before you
    close anything.  The choice persists as config "language"."""
    pal = kit.pal
    win = tk.Toplevel(parent)
    kit.attach(win)
    kit.reg(win, "card")
    win.title("%s - %s" % (APP_NAME, i18n.L("lang.title")))
    win.configure(background=pal["card"])
    win.resizable(False, False)
    win.transient(parent)
    W, H = 480, 560
    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry("%dx%d+%d+%d" % (W, H, max(0, (sw - W) // 2),
                                  max(0, (sh - H) // 3)))
    try:
        win.iconbitmap(logo.ico_path())
    except Exception:
        pass
    kit.defocus_hook(win)
    kit.titlebar_hook(win)

    head = tk.Label(win, text=i18n.L("lang.title"), font=F_H1,
                    bg=pal["card"], fg=pal["text"])
    kit.reg(head, "card_text")
    head.pack(pady=(14, 2))
    cur = tk.StringVar(value=i18n.L("lang.current",
                                    i18n.native_name(i18n.current())))
    curl = tk.Label(win, textvariable=cur, font=F_DESC, bg=pal["card"],
                    fg=pal["muted"])
    kit.reg(curl, "card_muted")
    curl.pack(pady=(0, 8))

    codes = i18n.offered_codes()
    progress = i18n.in_progress()

    def row_text(code):
        return "%s   %s   -   %s" % (
            i18n.native_name(code), i18n.english_name(code),
            i18n.L("lang.coverage",
                   int(round(100 * i18n.coverage(code)))))

    lb = tk.Listbox(win, font=F_BASE, activestyle="none",
                    selectmode="single", exportselection=False,
                    takefocus=0, bg=pal["entry"], fg=pal["text"],
                    highlightthickness=1,
                    highlightbackground=pal["entry_bd"])
    kit.reg(lb, "listbox")
    for c in codes:
        lb.insert("end", row_text(c))
    here = codes.index(i18n.current())
    lb.selection_set(here)
    lb.see(here)
    lb.pack(fill="both", expand=True, padx=16, pady=(0, 8))

    if progress:
        prog = tk.Label(win, text=i18n.L(
            "lang.progress",
            ", ".join(i18n.native_name(c) for c, _f in progress)),
            font=F_DESC, bg=pal["card"], fg=pal["muted"],
            wraplength=430, justify="center")
        kit.reg(prog, "card_muted")
        prog.pack(pady=(0, 6))
        R(lambda: prog.configure(text=i18n.L(
            "lang.progress",
            ", ".join(i18n.native_name(c) for c, _f in progress)))
          if _live(prog) else False)

    note = tk.Label(win, text=i18n.L("lang.prompt"), font=F_DESC,
                    bg=pal["card"], fg=pal["muted"], wraplength=430,
                    justify="center")
    kit.reg(note, "card_muted")
    note.pack(pady=(0, 10))

    close_btn = kit.button(win, i18n.L("lang.close"), win.destroy)
    close_btn.pack(pady=(0, 14))

    def reword_self():
        if not _live(win):
            return False
        win.title("%s - %s" % (APP_NAME, i18n.L("lang.title")))
        head.configure(text=i18n.L("lang.title"))
        note.configure(text=i18n.L("lang.prompt"))
        cur.set(i18n.L("lang.current",
                        i18n.native_name(i18n.current())))
        keep = codes.index(i18n.current())
        lb.delete(0, "end")
        for c in codes:
            lb.insert("end", row_text(c))
        lb.selection_set(keep)
        lb.see(keep)
        kit.set_text(close_btn, i18n.L("lang.close"))
        return True

    R(reword_self)

    def choose(_event=None):
        sel = lb.curselection()
        if not sel:
            return
        code = codes[sel[0]]
        if code == i18n.current():
            return
        i18n.set_language(code)
        cfg.set("language", code, save=True)
        apply_language()          # rewords the main window and us

    lb.bind("<<ListboxSelect>>", choose)
    win.protocol("WM_DELETE_WINDOW", win.destroy)
    return win


def _login_window(cfg, kit):
    """Sign-in: one Discord button and nothing else.

    No usernames, no passwords, no local accounts: the browser
    authenticates against Discord, the app exchanges the code itself
    (loopback hop, native-app OAuth), and the subscription is bound to
    that Discord identity - including the e-mail Stripe must charge.
    Returns the identity dict, or None when the window was closed.
    """
    pal = kit.pal
    result = {}
    W, H = 560, 640

    root = tk.Tk()
    kit.attach(root)
    kit.reg(root, "card")
    root.title(i18n.L("login.title", APP_NAME))
    root.configure(background=pal["card"])
    root.resizable(False, False)
    root.update_idletasks()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+%d+%d" % (W, H, max(0, (sw - W) // 2),
                                   max(0, (sh - H) // 3)))
    try:
        root.iconbitmap(logo.ico_path())   # real .ico: title bar + taskbar
    except Exception:
        try:
            root.iconphoto(True, logo.photoimage(tk, 64))
        except Exception:
            pass
    kit.defocus_hook(root)
    kit.titlebar_hook(root)

    top = tk.Frame(root, bg=pal["card"])
    kit.reg(top, "card")
    top.pack(fill="x", padx=14, pady=(10, 0))
    kit.switch_widget(top, kit.toggle).pack(side="right")

    def _surf_of(widget):
        """Live background colour of the widget's parent surface."""
        try:
            parent = widget.nametowidget(widget.winfo_parent())
            return str(parent.cget("bg"))
        except Exception:
            return pal["card"]

    try:
        lb = tk.Label(root, bg=pal["card"])
        kit.reg(lb, "card")
        im = logo.surface_image(tk, 112, _surf_of(lb))
        lb.configure(image=im, bg=_surf_of(lb))
        lb._img = im
        lb.pack(pady=(10, 2))

        def _relogo():
            surf = _surf_of(lb)
            im2 = logo.surface_image(tk, 112, surf)
            lb.configure(image=im2, bg=surf)
            lb._img = im2
        kit.repaint(_relogo)
    except Exception:
        pass

    t = tk.Label(root, text=APP_NAME, font=F_H1, bg=pal["card"],
                 fg=pal["text"])
    kit.reg(t, "card_text")
    t.pack()
    # The sub line wraps inside the window (wraplength 460 leaves 50 px
    # of margin on each side of the 560 px frame). Without it the text
    # ran off the window edge as one long line - and longer translations
    # did the same. Centre-justified like the note below it.
    sub = tk.Label(root, font=F_DESC, bg=pal["card"], fg=pal["muted"],
                   text=i18n.L("login.sub"),
                   wraplength=460, justify="center")
    kit.reg(sub, "card_muted")
    sub.pack(pady=(2, 12))

    msg = tk.StringVar(value="")
    msg_lbl = tk.Label(root, textvariable=msg, font=F_DESC, bg=pal["card"],
                       fg=pal["accent"], wraplength=460, justify="center")
    kit.reg(msg_lbl, "card")
    msg_lbl.pack(side="bottom", pady=(0, 12))
    msg_kind = ["err"]

    def _remsg():
        # keep the message colour themed across light/dark switches
        msg_lbl.configure(fg=(pal["green"] if msg_kind[0] == "ok"
                              else pal["accent"]))
    kit.repaint(_remsg)

    def set_msg(text, ok=False):
        msg_kind[0] = "ok" if ok else "err"
        msg_lbl.configure(fg=(pal["green"] if ok else pal["accent"]))
        msg.set(text)

    body = tk.Frame(root, bg=pal["card"])
    kit.reg(body, "card")
    body.pack(pady=(0, 6))

    btns = {}
    waiting = {"on": False}

    def done(identity, err, label):
        waiting["on"] = False
        for b in btns.values():
            b.configure(state="normal")
        if identity:
            result["identity"] = identity
            set_msg(i18n.L("login.signedin",
                         online.identity_label(identity)), ok=True)
            root.after(350, root.destroy)
            return
        set_msg(err or i18n.L("login.failed", label))

    def choose(provider, label):
        if waiting["on"]:
            return
        if not online.configured(cfg):
            set_msg(i18n.L("login.not_configured"))
            return
        waiting["on"] = True
        set_msg(i18n.L("login.waiting", label))
        for b in btns.values():
            b.configure(state="disabled")

        def worker():
            try:
                identity, msg = online.login_with_provider(cfg,
                                                           provider)
            except online.OnlineError as exc:
                identity, msg = None, i18n.L("login.unreachable", exc)
            root.after(0, lambda: done(identity, msg, label))

        threading.Thread(target=worker, daemon=True,
                         name="login-%s" % provider).start()

    # Provider pills: the brand mark on the left, the label centred -
    # like every other "Sign in with ..." button out there. Composited
    # with PIL so the pill keeps the theme colours and the mark stays
    # a crisp PNG; without Pillow (or in an old partial copy without
    # provider_logos.py) the buttons degrade to plain text.
    def provider_pill(pid, w, h, bg, dark):
        img = _PILImage.new("RGBA", (w, h), (0, 0, 0, 0))
        dr = _PILDraw.Draw(img)
        dr.rounded_rectangle((0, 0, w - 1, h - 1), radius=7,
                             fill=hex2rgb(bg) + (255,))
        name = pid + "_dark" if (dark and pid == "github") else pid
        mark = _PILImage.open(io.BytesIO(base64.b64decode(
            provider_logos.PROVIDER_LOGO_B64[name])))
        th = 20 if pid == "discord" else 24     # optical, not metric
        if mark.height != th:
            mark = mark.resize(
                (max(1, int(round(mark.width * th / mark.height))), th),
                _PILImage.LANCZOS)
        img.paste(mark, (16, (h - th) // 2), mark)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return tk.PhotoImage(data=buf.getvalue())

    def paint_provider_buttons():
        dark = kit.current() == "dark"
        bg, fg = kit._btn_colors("btn")
        for pid, b in btns.items():
            b.configure(fg=fg, bg=pal["card"], activebackground=pal["card"],
                        activeforeground=fg)
            if provider_logos is None or not HAVE_PIL:
                continue
            text, w, h = b._pmeta
            try:
                img = provider_pill(pid, w, h, bg, dark)
                b.configure(image=img)
                b._img = img
            except Exception:
                pass

    for pid, label in online.PROVIDERS:
        if not online.PROVIDER_TABLE[pid]["client_id"]:
            continue          # not registered for this build: no dead button
        text = i18n.L("login.provider", label)
        f = tkfont.Font(font=F_BTN_BIG)
        w = int(f.measure(text)) + 96        # logo gutter + padding
        h = 40
        b = tk.Button(body, text=text, relief="flat", bd=0, font=F_BTN_BIG,
                      highlightthickness=0, takefocus=0, cursor="hand2",
                      compound="center",
                      disabledforeground="#9aa0a6",
                      command=lambda p=pid, l=label: choose(p, l))
        b._pmeta = (text, w, h)
        btns[pid] = b
    # one shared width: sign-in pillars look like a column, not a ragbag
    wmax = max([b._pmeta[1] for b in btns.values()] or [0])
    for b in btns.values():
        text, _w, h = b._pmeta
        b._pmeta = (text, wmax, h)
        b.pack(fill="x", padx=60, pady=(0, 8))
    if not btns:
        # v8.49: catalogued. This was hard-coded English while
        # login.no_provider sat translated in all 16 locales unused - and
        # the two wordings had drifted apart.
        set_msg(i18n.L("login.no_provider"))
    paint_provider_buttons()
    kit.repaint(paint_provider_buttons)

    note = tk.Label(body, font=F_DESC, bg=pal["card"], fg=pal["muted"],
                    text=i18n.L("login.note"),
                    wraplength=440, justify="center")
    kit.reg(note, "card_muted")
    note.pack(pady=(6, 4))

    R(lambda: sub.configure(text=i18n.L("login.sub")) if _live(sub)
      else False)
    R(lambda: note.configure(text=i18n.L("login.note")) if _live(note)
      else False)

    # v8.40: the language chooser is reachable before sign-in too.
    lang_row = tk.Frame(body, bg=pal["card"])
    kit.reg(lang_row, "card")
    lang_row.pack(pady=(0, 12))
    _b_lg = kit.button(lang_row, i18n.L(
        "btn.language", i18n.native_name(i18n.current())),
        lambda: _language_window(cfg, kit, root))
    _b_lg.pack(side="left")
    R(lambda: kit.set_text(_b_lg, i18n.L(
        "btn.language", i18n.native_name(i18n.current())))
      if _live(_b_lg) else False)

    # v8.40: translations are longer than English; grow the fixed
    # window instead of clipping the last row (same trick as the gate).
    root.update_idletasks()
    need = root.winfo_reqheight() + 8
    if need > H:
        H = need
        root.geometry("%dx%d+%d+%d" % (W, H, max(0, (sw - W) // 2),
                                       max(0, (sh - H) // 3)))

    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
    return result.get("identity")


# ----------------------------------------------------------------------
# main window
# ----------------------------------------------------------------------

def _run_main(cfg, identity, app, hook_thread, kit, ent=None):
    action = {"now": "quit"}
    pal = kit.pal


    # Pending after-ids, cancelled on close. v8.49: pruned as it grows.
    # poll_status appends one id every 500 ms and nothing ever removed the
    # ones that had already fired, so this was the one unbounded structure
    # in the GUI (~7,200 dead integers per hour per window). Every other
    # registry here - RETEXT and kit.repaints - is pruned correctly.
    aids = []
    AIDS_CAP = 64

    def after_ms(ms, fn):
        """root.after that keeps `aids` bounded."""
        aid = root.after(ms, fn)
        aids.append(aid)
        if len(aids) > AIDS_CAP:
            del aids[:len(aids) - AIDS_CAP]   # oldest have already fired
        return aid

    def post(hid):
        tid = app.thread_id
        if tid:
            try:
                PostThreadMessage(tid, WM_HOTKEY, hid, 0)
            except Exception:
                pass
        else:
            status_msg(i18n.L("st.engine_dead"))

    vars_ = {}
    dirty = {"on": False}
    suppress = [False]

    root = tk.Tk()
    kit.attach(root)
    kit.reg(root, "bg")
    root.title(APP_NAME)
    root.configure(background=pal["bg"])
    root.update_idletasks()
    # Clamp to the (physical) screen so the title bar stays reachable
    # on short displays; min size follows, never above the clamp.
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    # v8.32: 770 - the +10 px the taller header strip asked for, so
    # the tab pages below keep the room they had in v8.31.
    gw, gh = min(980, max(640, sw - 24)), min(770, max(480, sh - 24))
    root.geometry("%dx%d" % (gw, gh))
    root.minsize(min(860, gw), min(640, gh))
    try:
        root.iconbitmap(logo.ico_path())   # real .ico: title bar + taskbar
    except Exception:
        try:
            root.iconphoto(True, logo.photoimage(tk, 64))
        except Exception:
            pass
    kit.defocus_hook(root)
    kit.titlebar_hook(root)

    # Single-key binds fire system-wide via the pass-through keyboard
    # hook; while the user types in OUR text fields (or type-selects
    # in our listboxes) they must stay silent, so track focus.
    def _focus_watch(event):
        app.input_focused = event.widget.winfo_class() in (
            "Entry", "Combobox", "TCombobox", "Listbox")
    root.bind_all("<FocusIn>", _focus_watch, add="+")
    root.bind_all("<FocusOut>",
                  lambda e: setattr(app, "input_focused", False),
                  add="+")


    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    def restyle_tt():
        style.configure("TCombobox", fieldbackground=pal["entry"],
                        background=pal["light_bg"], foreground=pal["text"],
                        arrowcolor=pal["text"], font=F_BASE, padding=4,
                        borderwidth=1)
        style.map("TCombobox",
                  fieldbackground=[("readonly", pal["entry"])],
                  foreground=[("readonly", pal["text"])])
        style.configure("TScrollbar", background=pal["light_bg"],
                        troughcolor=pal["bg"], arrowcolor=pal["text"],
                        borderwidth=0)
    kit.repaint(restyle_tt)
    restyle_tt()

    # ---------------- header ----------------
    # v8.27: a TALLER header strip - the identity line is the plain
    # e-mail address (no provider tag) with the licence status on its
    # OWN line underneath; the Quit button is gone (the window close
    # button quits) and the light/dark switch moved next to Log Out.
    # v8.29: the strip packs FLUSH with the client-area top - no top
    # pady.  The owner's Windows crop showed the native title bar
    # caption ("Snappy AI" beside the window icon) riding in a dark
    # band above the header card: the old 10 px top gap pushed the
    # e-mail/subscription card down and left the caption high in the
    # band.  Flush packing shrinks the band between the window top and
    # the card top to exactly the title bar, so the caption sits
    # centred in it by construction and the card starts as high as the
    # client area allows.
    # v8.30: the SIDE gutters are back - the owner only wanted the
    # card higher, not full-bleed.  padx=10 keeps the same 10 px
    # background margin on the left and right that every other card in
    # the window has; only the top edge stays flush.
    header = tk.Frame(root, bg=pal["card"])
    kit.reg(header, "card")
    header.pack(fill="x", padx=10, pady=(0, 6))
    # v8.31: fixed-height strip - 20 px shorter than v8.30's 84 px -
    # with a bigger logo and compacted identity lines inside it.
    # v8.32: the strip takes 10 px back (HEADER_H) and the window
    # grows with it; the logo seat below is untouched.
    header.configure(height=HEADER_H)
    header.pack_propagate(False)
    try:
        hl = tk.Label(header, bg=pal["card"])
        kit.reg(hl, "card")
        himg = logo.surface_image(tk, HEADER_LOGO_PX,
                                  _surf_of(hl, pal["card"]))
        hl.configure(image=himg, bg=_surf_of(hl, pal["card"]),
                     padx=0, pady=0, borderwidth=0)
        hl._img = himg
        hl.pack(side="left", padx=(14, 10))

        def _relogo_header():
            surf = _surf_of(hl, pal["card"])
            im2 = logo.surface_image(tk, HEADER_LOGO_PX, surf)
            hl.configure(image=im2, bg=surf)
            hl._img = im2
        kit.repaint(_relogo_header)
    except Exception:
        pass
    # v8.32: the identity stack hangs from the strip top instead of
    # riding centred - the frame spans the full card height and the
    # title packs on HEADER_TEXT_TOP.  v8.33 raised that seat by
    # HEADER_TEXT_RAISE (4 px) above the logo's centring remainder so
    # the licence line clears the card's bottom edge; the e-mail and
    # licence lines keep their 1 px gaps and travel with the title.
    # The logo's own seat is untouched, so the mark never moves.
    # v8.34: the stack is only TWO lines now - the title and a build
    # stamp.  The customer e-mail and the licence status moved down to
    # the status bar (right-hand side), so the header no longer carries
    # anything that can wrap, and the card has room to breathe.
    tt = tk.Frame(header, bg=pal["card"])
    kit.reg(tt, "card")
    tt.pack(side="left", fill="y")
    h1 = tk.Label(tt, text=APP_NAME, font=F_HEAD_H1, bg=pal["card"],
                  fg=pal["text"])
    kit.reg(h1, "card_text")
    h1.pack(anchor="w", pady=(HEADER_TEXT_TOP, 0))
    # Build stamp, in the seat the customer e-mail occupied before
    # v8.34 - same face constant as the old e-mail line, same 1 px gap
    # under the title.  v8.36 adds HEADER_BUILD_INDENT of left inset so
    # the smaller glyphs line up optically with the 20 pt bold title
    # above them (see the constant's comment for why this is needed even
    # though both labels are anchored west in the same frame).
    h2 = tk.Label(tt, text=i18n.L("hdr.build", APP_VERSION),
                  font=F_HEAD_LINE, bg=pal["card"], fg=pal["muted"])
    kit.reg(h2, "card_muted")
    h2.pack(anchor="w", padx=(HEADER_BUILD_INDENT, 0), pady=(1, 0))
    R(lambda: h2.configure(text=i18n.L("hdr.build", APP_VERSION))
      if _live(h2) else False)

    right = tk.Frame(header, bg=pal["card"])
    kit.reg(right, "card")
    right.pack(side="right", padx=12)

    def close_all(code):
        action["now"] = code
        for aid in aids:
            try:
                root.after_cancel(aid)
            except (tk.TclError, ValueError):
                pass
        root.destroy()

    def do_logout():
        app.request_quit()
        try:
            hook_thread.join(timeout=2.0)
        except Exception:
            pass
        close_all("logout")

    # right cluster: [theme switch] [Log Out] | [Pause] [Launch].
    # The switch sits directly next to Log Out (v8.27); Quit is gone -
    # the window's close button is the only exit.
    kit.switch_widget(right, kit.toggle).pack(side="left", padx=(0, 10))
    _b_logout = kit.button(right, i18n.L("btn.logout"), do_logout)
    _b_logout.pack(side="left", padx=(0, 18))
    _b_pause = kit.button(right, i18n.L("btn.pause"), lambda: post(11),
                          kind="amber")
    _b_pause.pack(side="left", padx=(0, 6))
    _b_launch = kit.button(right, i18n.L("btn.launch"), lambda: post(10),
                           kind="green")
    _b_launch.pack(side="left")
    for _b, _k in ((_b_logout, "btn.logout"), (_b_pause, "btn.pause"),
                   (_b_launch, "btn.launch")):
        R(lambda b=_b, k=_k: kit.set_text(b, i18n.L(k)) if _live(b)
          else False)

    # ---------------- tab bar ----------------
    bar = tk.Frame(root, bg=pal["tab_bg"])
    kit.reg(bar, "bg")
    bar.pack(fill="x", padx=10)
    # v8.27: five tabs by option category - the Color Picker merged
    # into Colors.
    # v8.38: Handler sits right after Colors (it
    # holds the advanced colour/brightness knobs the picker tab does
    # not), Experimental collects every dropdown, Help closes the row.
    # v8.39: tabs are keyed by SLUG, never by display name - the names
    # come from the live catalog, so they cannot be dict keys.
    tab_names = ["assist", "colors", "handler", "hotkeys", "macros",
                 "advanced", "experimental", "help"]
    tab_btns = {}
    pages = {}
    current = {"tab": tab_names[0]}

    content_host = tk.Frame(root, bg=pal["card"])
    kit.reg(content_host, "card")
    content_host.pack(fill="both", expand=True, padx=10, pady=(0, 4))

    def show_tab(name):
        current["tab"] = name
        for tn, b in tab_btns.items():
            sel = (tn == name)
            fill = pal["card"] if sel else pal["tab_bg"]
            b.configure(font=(F_TAB if sel else F_TAB_OFF),
                        fg=(pal["accent"] if sel else pal["muted"]),
                        bg=pal["tab_bg"], activebackground=pal["tab_bg"],
                        activeforeground=(pal["accent"] if sel
                                          else pal["muted"]),
                        bd=0)
            meta = getattr(b, "_tmeta", None)
            if meta and HAVE_PIL:
                try:
                    img = kit.rounded(meta[0], 34 if sel else 28, fill, 6)
                    b.configure(image=img, compound="center")
                    b._img = img
                except Exception:
                    pass
        for tn, pg in pages.items():
            if tn == name:
                pg.pack(fill="both", expand=True)
            else:
                pg.pack_forget()
    kit.repaint(lambda: show_tab(current["tab"]))

    # Row frames for the wrapping tab bar. They MUST be created before
    # the tab buttons: the buttons stay children of `bar` and are packed
    # into a row with pack(in_=...), and Tk paints a master's children in
    # creation order - a frame created after the buttons would paint its
    # background right over them. One frame per possible row; unused
    # frames simply stay unpacked.
    tab_rows = []
    for _i in range(len(tab_names)):
        fr = tk.Frame(bar, bg=pal["tab_bg"])
        kit.reg(fr, "bg")
        tab_rows.append(fr)

    def _tab_row(i):
        return tab_rows[i]

    for tn in tab_names:
        text = "  %s  " % i18n.L("tab." + tn)
        b = tk.Button(bar, text=text, takefocus=0, bd=0,
                      highlightthickness=0, relief="flat",
                      cursor="hand2",
                      command=lambda n=tn: show_tab(n))
        f = tkfont.Font(font=F_TAB)
        b._tmeta = (int(f.measure(text)) + 12,)
        b._tabrow = None
        tab_btns[tn] = b
        pages[tn] = tk.Frame(content_host, bg=pal["card"])
        kit.reg(pages[tn], "card")

        def _retab(b=b, tn=tn):
            if not _live(b):
                return False
            t = "  %s  " % i18n.L("tab." + tn)
            b.configure(text=t)
            b._tmeta = (int(tkfont.Font(font=F_TAB).measure(t)) + 12,)
            layout_tabs()
        R(_retab)

    # The tab bar WRAPS. Packed in one row, the eight tabs run past the
    # window edge with any font wider than Segoe UI - the last tabs
    # (the last tabs) were then invisible AND unclickable.
    # layout_tabs() re-flows the buttons into the row frames whenever
    # the bar is resized.
    def layout_tabs(_event=None):
        try:
            avail = bar.winfo_width()
            if avail < 200:
                avail = root.winfo_width() - 24
            if avail < 200:
                return                  # not mapped yet
        except Exception:
            return
        row = 0
        used = 0
        for tn in tab_names:
            b = tab_btns[tn]
            w = b._tmeta[0] + 8
            if used and used + w > avail:
                row += 1
                used = 0
            used += w
            if b._tabrow != row:
                b.pack_forget()
                b.pack(in_=_tab_row(row), side="left", padx=(3, 0))
                b._tabrow = row
        for i, fr in enumerate(tab_rows):
            if i <= row:
                fr.pack(fill="x")
            else:
                fr.pack_forget()

    bar.bind("<Configure>", layout_tabs)
    root.after(60, layout_tabs)

    # ---------------- description bar + Apply ----------------
    # v8.39: Apply lives in THIS row, flush right, opposite the setting
    # description it commits.  It used to appear in the footer next to
    # the Running/Standby light, which read as if it belonged to the
    # engine state instead of to the edited settings.
    desc_row = tk.Frame(root, bg=pal["desc_bg"])
    kit.reg(desc_row, "desc_frame")
    desc_row.pack(fill="x", padx=10)

    desc_var = tk.StringVar(value=i18n.L("desc.default"))
    # v8.51: multi-line bar. A single-line label wrapped only as far
    # as the window grew tall; long descriptions (and longer
    # translations) were clipped outright - "fully visible" now means
    # the bar takes up to five lines and GROWS its own height, so no
    # setting's text is ever cut off.
    desc_bar = tk.Label(desc_row, textvariable=desc_var, font=F_DESC,
                        bg=pal["desc_bg"], fg=pal["muted"], anchor="w",
                        justify="left", padx=12, pady=6, wraplength=660)
    kit.reg(desc_bar, "desc")
    desc_bar.pack(side="left", fill="both", expand=True)

    DESC_MAX_LINES = 5          # normal hover texts fit well inside
    DESC_MAX_CHARS = 1900       # absolute ceiling for huge locales

    def _desc_height(_event=None):
        """Fit the bar's own line count to the CURRENT text at the
        CURRENT width - never more than DESC_MAX_LINES, so one long
        description cannot push the tabs off a small screen."""
        try:
            w = desc_row.winfo_width()
            if w > 80:
                want = max(160, w - 24)
                if str(desc_bar.cget("wraplength")) != str(want):
                    desc_bar.configure(wraplength=want)
                txt = desc_var.get()
                lines = 0
                for para in txt.split("\n"):
                    lines += max(1, len(para) // int(want * 0.92) + 1)
                want_h = min(DESC_MAX_LINES, max(2, lines))
                if int(desc_bar.cget("height")) != want_h:
                    desc_bar.configure(height=want_h)
        except tk.TclError:
            pass

    desc_row.bind("<Configure>", _desc_height)
    _desc_height()

    # v8.40: the description bar remembers WHERE its current text came
    # from, so a language switch can re-translate it in place.  Without
    # this the bar kept showing the previous language's description
    # until the next hover - which read as "descriptions are not
    # translated".
    desc_src = [None]

    def set_desc(fn):
        """fn() -> the description text in the live language, or None
        for the default hint."""
        desc_src[0] = fn
        desc_var.set(fn() if fn else i18n.L("desc.default"))
        _desc_height()

    def _redesc():
        if not _live(desc_bar):
            return False
        desc_var.set(desc_src[0]() if desc_src[0]
                     else i18n.L("desc.default"))
        _desc_height()
        return True

    R(_redesc)

    apply_btn = kit.button(desc_row, i18n.L("btn.apply"), lambda: None,
                           kind="accent", surface="desc_bg")
    R(lambda: kit.set_text(apply_btn, i18n.L("btn.apply"))
      if _live(apply_btn) else False)

    # ---------------- footer ----------------
    footer = tk.Frame(root, bg=pal["bg"])
    kit.reg(footer, "bg")
    footer.pack(fill="x", padx=10, pady=(2, 4))

    status_until = [0.0]
    status_var = tk.StringVar(value="")

    def status_msg(text):
        status_var.set(text)
        status_until[0] = time.perf_counter() + 4.0

    def mark_dirty(_a=None, _b=None, _c=None):
        if suppress[0] or dirty["on"]:
            return
        dirty["on"] = True
        apply_btn.pack(side="right", padx=(6, 6), pady=3)

    def refresh_fields():
        suppress[0] = True
        try:
            for key, (kind, var) in vars_.items():
                value = cfg.get(key)
                if kind == "bool":
                    var.set(bool(value))
                elif kind == "map":
                    var.set(map_display(key, value))
                else:
                    var.set(str(value))
        finally:
            suppress[0] = False

    def widget_values():
        """Parse every widget into values; returns (values, bad_keys)."""
        values = {}
        bad = []
        for key, (kind, var) in vars_.items():
            raw = var.get()
            if kind == "bool":
                values[key] = bool(raw)
                continue
            if kind == "map":
                value = map_value(key, raw)
                if value is None:
                    bad.append(key)
                else:
                    values[key] = value
                continue
            ok, value = _coerce_value(raw, DEFAULT_CONFIG.get(key))
            if ok:
                values[key] = value
            else:
                bad.append(key)
        return values, bad

    def _sync_from_cfg(snapshot=None):
        """Re-sync the GUI from the effective config (after the hook
        thread reload), surface theme changes and config.ini overrides."""
        refresh_fields()
        dirty["on"] = False
        apply_btn.pack_forget()
        theme = str(cfg.get("theme", "light"))
        if theme != kit.current():
            kit.switch_to(theme)
        if snapshot:
            over = [k for k in snapshot if cfg.get(k) != snapshot[k]]
            if over:
                status_msg(i18n.L("st.ini_over", ", ".join(over)))

    def save_and_apply():
        values, bad = widget_values()
        for key, value in values.items():
            cfg.set(key, value, save=False)
        cfg.sanitize()
        snapshot = {k: cfg.get(k) for k in vars_}
        cfg.save()
        post(6)
        dirty["on"] = False
        apply_btn.pack_forget()
        root.after(350, lambda: _sync_from_cfg(snapshot))
        if bad:
            status_msg(i18n.L("st.saved_bad", ", ".join(bad)))
        else:
            status_msg(i18n.L("st.saved"))

    apply_btn.configure(command=save_and_apply)

    def do_export():
        path = filedialog.asksaveasfilename(
            title=i18n.L("st.export_title"),
            initialfile="snappyai-settings.json",
            defaultextension=".json",
            filetypes=[(i18n.L("st.file_settings"), "*.json")])
        if path:
            # export what you SEE: widget edits win over saved values,
            # without silently changing the running config
            values, _bad = widget_values()
            merged = dict(cfg.values)
            merged.update(values)
            try:
                # v8.49: localised, and routed through Config.export_to so
                # the SENSITIVE_KEYS filter applies to GUI exports too - an
                # exported settings file is the one artefact a user
                # deliberately hands to someone else.
                ok, text = cfg.export_to(path)
                status_msg(text)
            except OSError as exc:
                status_msg(i18n.L("st.export_fail", exc))

    def do_import():
        path = filedialog.askopenfilename(
            title=i18n.L("st.import_title"),
            filetypes=[(i18n.L("st.file_settings"), "*.json"),
                       (i18n.L("st.all_files"), "*.*")])
        if path:
            ok, text = cfg.import_from(path)
            if ok:
                cfg.save()
                post(6)
                root.after(350, lambda: _sync_from_cfg())
            status_msg(text)

    def restore_defaults():
        if not messagebox.askyesno(APP_NAME, i18n.L("st.reset_confirm")):
            return
        theme = cfg.get("theme")
        # v8.49: the deployment constants are no longer settings, so there
        # is nothing to preserve across a reset - they come from
        # build_secrets and cannot be changed from here. This keep-list used
        # to carry entitlement_repo / entitlement_branch / both Stripe links
        # through a restore, which was the last path by which they could
        # reach config.json.
        cfg.values = dict(DEFAULT_CONFIG)
        cfg.values["theme"] = theme
        cfg.save()
        refresh_fields()
        post(6)
        status_msg(i18n.L("st.defaults_restored"))

    _b_rest = kit.button(footer, i18n.L("btn.restore"), restore_defaults,
                         surface="bg")
    _b_rest.pack(side="left", padx=(4, 16))
    _b_imp = kit.button(footer, i18n.L("btn.import"), do_import,
                        surface="bg")
    _b_imp.pack(side="left", padx=(0, 6))
    _b_exp = kit.button(footer, i18n.L("btn.export"), do_export,
                        surface="bg")
    _b_exp.pack(side="left", padx=(0, 6))

    # v8.39: the language chooser sits right beside Export Config.
    _b_lang = kit.button(
        footer,
        i18n.L("btn.language", i18n.native_name(i18n.current())),
        lambda: _language_window(cfg, kit, root), surface="bg")
    _b_lang.pack(side="left")

    for _b, _k in ((_b_rest, "btn.restore"), (_b_imp, "btn.import"),
                   (_b_exp, "btn.export")):
        R(lambda b=_b, k=_k: kit.set_text(b, i18n.L(k)) if _live(b)
          else False)

    def _relang():
        if not _live(_b_lang):
            return False
        kit.set_text(_b_lang, i18n.L(
            "btn.language", i18n.native_name(i18n.current())))
        return True

    R(_relang)
    # a language change also re-colours/re-rounds everything themed
    R(lambda: (kit.apply(), True)[1] if _live(root) else False)
    # ...and re-pushes every stored value into its widget, which is
    # what turns a follow_boost var holding "100%" into "100%" of the
    # new language (refresh_fields suppresses the dirty trace, so this
    # never makes Apply appear).
    R(lambda: (refresh_fields(), True)[1] if _live(root) else False)

    # v8.27: the running-status light moved from the header down to the
    # bottom-right corner (this row): "Running.." + green dot while
    # launched, "Standby.." + orange dot while paused. The Reload
    # Config button is gone - Apply reloads the engine anyway.
    light_box = tk.Frame(footer, bg=pal["bg"])
    kit.reg(light_box, "bg")
    light_box.pack(side="right", padx=(8, 4))
    run_state = tk.StringVar(value="Standby..")
    run_lbl = tk.Label(light_box, textvariable=run_state, font=F_BOLD,
                       bg=pal["bg"], fg=pal["text"])
    kit.reg(run_lbl, "bg_text")
    run_lbl.pack(side="left", padx=(0, 6))
    light = tk.Canvas(light_box, width=16, height=16,
                      highlightthickness=0, bg=pal["bg"])
    kit.reg(light, "canvas_bg")
    light.pack(side="left", pady=2)
    light_dot = light.create_oval(3, 3, 13, 13, fill=pal["amber"],
                                  outline="")

    # v8.34: the status bar is now a two-sided row. The left keeps the
    # live counters ("Assisted N | passed N | theme: X"); the right carries
    # the identity + licence line that used to be two lines in the header.
    # Same face (F_DESC), same muted colour, same status_bg - one row, two
    # anchors, so the registration text always hugs the right edge however
    # long the counters get.
    status_row = tk.Frame(root, bg=pal["status_bg"])
    kit.reg(status_row, "status_frame")
    status_row.pack(fill="x", side="bottom")

    sb = tk.Label(status_row, textvariable=status_var, font=F_DESC,
                  anchor="w", bg=pal["status_bg"], fg=pal["muted"],
                  padx=12, pady=5)
    kit.reg(sb, "status")
    sb.pack(side="left")

    reg_var = tk.StringVar(value=registration_line(identity, ent))
    reg_lbl = tk.Label(status_row, textvariable=reg_var, font=F_DESC,
                       anchor="e", bg=pal["status_bg"], fg=pal["muted"],
                       padx=12, pady=5)
    kit.reg(reg_lbl, "status")
    reg_lbl.pack(side="right")

    def _status_fit(_event=None):
        """The status row carries two anchored labels; a long language
        (German registration + licence line) must wrap instead of
        pushing the counters off the window (v8.40)."""
        try:
            w = status_row.winfo_width()
            if w < 200:
                return
            rw = reg_lbl.winfo_reqwidth()
            if rw > int(w * 0.62):
                reg_lbl.configure(wraplength=int(w * 0.62))
                rw = int(w * 0.62)
            want = max(140, w - rw - 24)
            if str(sb.cget("wraplength")) != str(want):
                sb.configure(wraplength=want)
        except tk.TclError:
            pass

    status_row.bind("<Configure>", _status_fit)
    _status_fit()

    # ---------------- setting rows ----------------
    def make_row(parent, key, row):
        label, desc, kind, choices = META[key]
        if key not in vars_:
            cur = cfg.get(key)
            var = (tk.BooleanVar(value=bool(cur)) if kind == "bool"
                   else tk.StringVar(value=str(cur)))
            vars_[key] = (kind, var)
            var.trace_add("write", mark_dirty)
        else:
            kind, var = vars_[key]

        cell = tk.Frame(parent, bg=pal["card"])
        kit.reg(cell, "card")
        cell.grid(row=row, column=0, sticky="we", padx=10, pady=4)
        cell.columnconfigure(0, weight=1)

        # v8.40 fix: the NAME is catalog text (tr_label), not the raw
        # English META string, and it re-registers so a live language
        # switch re-words it in place.
        lbl = tk.Label(cell, text=tr_label(key), font=F_BOLD,
                       bg=pal["card"], fg=pal["text"], anchor="w")
        kit.reg(lbl, "card_bold")
        lbl.grid(row=0, column=0, sticky="w", padx=(0, 10))
        lbl.bind("<Enter>", lambda e, k=key: set_desc(
            lambda: tr_desc(k)))
        lbl.bind("<Leave>", lambda e: set_desc(None))
        R(lambda l=lbl, k=key: l.configure(text=tr_label(k))
          if _live(l) else False)

        if kind == "bool":
            # v8.37: pill switch instead of the "On" checkbox - knob
            # right = on, track in the logo's red (see ThemeKit.
            # bool_switch).  Same var contract as the Checkbutton, so
            # widget_values()/refresh_fields() are untouched.
            w = kit.bool_switch(cell, var)
        elif kind == "map":
            # v8.39: a dropdown whose display strings map onto stored
            # values (follow_boost: "25%".."100%" -> 0.25..1.0).
            # v8.40: the display strings are catalog text, and the
            # frozen `values` list is rebuilt on every language change.
            def _val_width(k):
                """Chars for the closed field: long enough for the
                LONGEST translated value, so no language ever shows a
                truncated word in a closed dropdown (v8.40 "always
                fully visible").  The 56 cap only bites beyond the
                longest string any catalog currently ships (53), and
                even then the open list shows the whole string."""
                longest = max([len(d) for d, _v in map_pairs_live(k)]
                              or [14])
                return max(14, min(56, longest))

            w = ttk.Combobox(cell, textvariable=var,
                             values=[d for d, _v in map_pairs_live(key)],
                             state="readonly", width=_val_width(key),
                             font=F_BASE)

            def _revals(w=w, k=key):
                if not _live(w):
                    return False
                w.configure(values=[d for d, _v in map_pairs_live(k)],
                            width=_val_width(k))
                return True

            R(_revals)

            if key == "input_backend":
                # v8.50: tell the truth about the driver option up
                # front. Interception needs a DLL AND a kernel driver;
                # when either is missing the choice still works (the
                # engine falls back to the standard method with one
                # log line), but the user must see that it is NOT
                # active before picking it. The probe runs in a worker
                # thread because creating an Interception context can
                # block briefly while the driver loads.
                note = tk.Label(cell, text="", font=F_DESC,
                                bg=pal["card"], fg=pal["muted"],
                                anchor="e", justify="right")
                kit.reg(note, "card_muted")
                note.grid(row=1, column=0, columnspan=2, sticky="e")

                def _avail_probe(txt=note):
                    try:
                        from input_backend import InterceptionBackend
                        ok = InterceptionBackend.available()
                    except Exception:
                        ok = False
                    def _paint(ok=ok, txt=txt):
                        if not _live(txt):
                            return False
                        txt.configure(text=(
                            "Interception detected - ready to use."
                            if ok else
                            "Not installed here: picking this keeps "
                            "the standard Windows method."))
                        return True
                    R(_paint)

                threading.Thread(target=_avail_probe, daemon=True).start()
        elif kind == "colors":
            # v8.43: a colour-list row is SEEN, not read - the value
            # side is a strip of colour boxes (same look as the preset
            # swatches below), one per stored colour, right-aligned
            # like every other tab's value.  Clicking a box removes
            # that colour; the two add buttons below fill the
            # strip (fifteen boxes max - v8.45's grid is 15 boxes
            # wide, so a full list spans exactly the preset row).
            # The StringVar behind it still holds the classic
            # "r,g,b; r,g,b" (or "off"), so config, engine, import
            # and export are untouched.
            w = tk.Frame(cell, bg=pal["card"])
            kit.reg(w, "card")
            _chip_strips[key] = (w, var)
            var.trace_add("write", lambda *a, k=key: rebuild_chips(k))
            rebuild_chips(key)
        else:
            w = tk.Entry(cell, textvariable=var, width=16, font=F_ENTRY,
                         relief="solid", borderwidth=1, bg=pal["entry"],
                         fg=pal["text"], insertbackground=pal["text"],
                         highlightbackground=pal["entry_bd"],
                         highlightthickness=1)
            kit.reg(w, "entry")
        w.grid(row=0, column=1, sticky="e")

    # ---------------- colour-list chips (v8.43) ----------------
    # The two colour settings show their value as COLOUR BOXES, so
    # these helpers translate between the stored ";" string and the
    # strip on screen.  Fifteen colours per setting is the owner's
    # cap (v8.45: the whole right side is one 15-box grid, so a full
    # strip spans exactly the preset row below it); an empty list
    # stores "off" - the word the engine already understands for
    # "disabled".
    _chip_strips = {}
    _OFF_WORDS = ("off", "none", "disabled", "false")
    _MAX_CHIPS = 15
    CHIP_SW, CHIP_PAD = 24, 2      # same box as the preset swatches
    CHIP_OFF_X = "#cc2f38"         # v8.44: the red X of an empty list

    def _token_rgb(tok):
        """RGB triple of one stored colour token, or None.

        Accepts the same forms the engine accepts: a preset name
        (blue, grey, ...) resolved through vision's table, or three
        numbers r,g,b."""
        preset = vision.ACCENT_PRESETS.get(tok.strip().lower())
        if preset is not None:
            return tuple(int(v) for v in vision.hsv_to_rgb(*preset))
        try:
            parts = [int(p.strip()) for p in tok.split(",")]
        except ValueError:
            return None
        if len(parts) != 3:
            return None
        return tuple(min(255, max(0, p)) for p in parts)

    def _color_tokens(value):
        """The raw ';' tokens of a colour-list value, minus off-words
        and blanks - the tokens stay RAW so removing one box never
        rewrites the others."""
        s = str(value or "").strip()
        if not s or s.lower() in _OFF_WORDS:
            return []
        return [t.strip() for t in s.split(";") if t.strip()]

    def rebuild_chips(key):
        """Repaint one colour-list strip from the value it carries."""
        entry = _chip_strips.get(key)
        if entry is None:
            return
        strip, var = entry
        if not _live(strip):
            return
        for c in strip.winfo_children():
            c.destroy()
        toks = _color_tokens(var.get())
        shown = [(i, _token_rgb(t)) for i, t in enumerate(toks)]
        shown = [(i, rgb) for i, rgb in shown if rgb is not None]
        if not shown:
            # v8.44: an empty list shows the SAME box a colour would
            # get, crossed out with a red X - "off" in the language of
            # the boxes around it instead of a word.  Hovering it
            # explains in plain words.
            off = tk.Canvas(strip, width=CHIP_SW, height=CHIP_SW,
                            bg=pal["light_bg"], highlightthickness=1,
                            highlightbackground=pal["entry_bd"],
                            takefocus=0)
            kit.reg(off, "hl")
            off.pack(side="left", padx=CHIP_PAD)
            off.create_line(6, 6, CHIP_SW - 6, CHIP_SW - 6,
                            fill=CHIP_OFF_X, width=2)
            off.create_line(CHIP_SW - 6, 6, 6, CHIP_SW - 6,
                            fill=CHIP_OFF_X, width=2)
            off.bind("<Enter>", lambda e, k=key: set_desc(
                lambda: i18n.L("col.chip_off", tr_label(k))))
            off.bind("<Leave>", lambda e: set_desc(None))
            return
        for i, rgb in shown[:_MAX_CHIPS]:
            hx = "#%02x%02x%02x" % rgb
            chip = tk.Canvas(strip, width=CHIP_SW, height=CHIP_SW,
                             bg=hx, highlightthickness=1,
                             highlightbackground=pal["entry_bd"],
                             cursor="hand2", takefocus=0)
            kit.reg(chip, "hl")
            chip.pack(side="left", padx=CHIP_PAD)
            chip.bind("<Button-1>",
                      lambda e, k=key, idx=i: remove_chip(k, idx))
            chip.bind("<Enter>", lambda e, k=key, rr=rgb: set_desc(
                lambda: i18n.L("col.chip_desc", rr[0], rr[1], rr[2],
                               tr_label(k))))
            chip.bind("<Leave>", lambda e: set_desc(None))

    def remove_chip(key, idx):
        """A click on a box: that colour leaves the list.  The write
        trace repaints the strip and marks the tab dirty."""
        entry = _chip_strips.get(key)
        if entry is None:
            return
        _strip, var = entry
        toks = _color_tokens(var.get())
        if not (0 <= idx < len(toks)):
            return
        rgb = _token_rgb(toks[idx]) or (0, 0, 0)
        del toks[idx]
        var.set("; ".join(toks) if toks else "off")
        status_msg(i18n.L("st.color_removed", rgb[0], rgb[1], rgb[2],
                          tr_label(key)))

    def _reword_chips():
        """Live language switch: the strips rebuild so even the
        crossed-out box's hover text re-translates."""
        alive = False
        for k in list(_chip_strips):
            if _live(_chip_strips[k][0]):
                rebuild_chips(k)
                alive = True
        return alive

    R(_reword_chips)

    def fill_list(page, keys):
        grid = tk.Frame(page, bg=pal["card"])
        kit.reg(grid, "card")
        grid.pack(fill="x", padx=6, pady=8)
        grid.columnconfigure(0, weight=1)
        for i, key in enumerate(keys):
            make_row(grid, key, i)

    # ---------------- Assistance ----------------
    # v8.27: EVERY on/off checkbox of the product lives on this tab.
    assist_page = pages["assist"]
    fill_list(assist_page, TAB_ASSIST)
    _wrapping_note(assist_page, kit, pal, "note.assist")

    # ---------------- Colors ----------------
    # v8.27: the old Color Picker tab merged INTO this one; v8.39
    # renamed it Colors and gave it the left-aligned picker layout.
    cp = pages["colors"]


    # v8.43 layout, values on the right like EVERY other tab - and
    # v8.45 makes the whole right side ONE 15-BOX GRID: the setting
    # rows open the page at full window width - name on the left,
    # value flush with the right edge - and the two colour lists show
    # their colours as BOXES (make_row's "colors" kind), fifteen at
    # most, instead of an "r,g,b; r,g,b" string; an empty list shows
    # one crossed-out box (v8.44) instead of the word Off.  A full
    # list spans exactly the 15-box grid everything below keeps.
    # Current RGB Value keeps its place under them, but its three
    # boxes are no longer numbers: each one glows with how much red /
    # green / blue the picked colour holds - and each one is FIVE
    # boxes wide (3 x 5 = 15), so the row spans the same grid.  Under
    # the rows the picker keeps its place on the left, and everything
    # that belongs to the picked colour - showcase, presets, the two
    # add buttons, the screen row, the suggestion boxes - sits on the
    # RIGHT SIDE of the window: its gap to the right edge is the same
    # 16 px the setting values keep, mirroring the picker's 16 px
    # inset on the left.
    cgrid = tk.Frame(cp, bg=pal["card"])
    kit.reg(cgrid, "card")
    cgrid.pack(fill="x", padx=6, pady=(8, 2))
    cgrid.columnconfigure(0, weight=1)
    for _ri, _ckey in enumerate(TAB_DETECT):
        make_row(cgrid, _ckey, _ri)

    # v8.42: the picked colour's R,G,B row UNDER the two colour
    # lists.  v8.43: still its own setting row, still right-aligned,
    # still fed only by the picker (and the preset / screen buttons)
    # - but the three boxes now CHANGE COLOUR with the amounts:
    # the red box carries the red share of the picked colour (#rr0000),
    # the green box the green share, the blue box the blue share, so
    # the row is read as colour instead of numbers.  The numbers
    # themselves live on in the same StringVars the picker pushes
    # into, further down.
    # v8.45: each box is FIVE colour boxes wide - 144 px + its 2 px
    # border + 2 px pack padding on each side = one 150 px slot, five
    # of the 30 px box pitches - so three boxes span exactly the
    # 15-box grid the lists, the presets and the buttons below keep
    # (3 x 5 = 15), left and right edges included.
    rgb_vars = {}
    for _ch, _dflt in (("r", "198"), ("g", "40"), ("b", "40")):
        rgb_vars[_ch] = tk.StringVar(value=_dflt)

    rgb_cell = tk.Frame(cgrid, bg=pal["card"])
    kit.reg(rgb_cell, "card")
    rgb_cell.grid(row=2, column=0, sticky="we", padx=10, pady=4)
    rgb_cell.columnconfigure(0, weight=1)
    rgb_lbl = tk.Label(rgb_cell, text=i18n.L("col.rgb.name"),
                       font=F_BOLD, bg=pal["card"], fg=pal["text"],
                       anchor="w")
    kit.reg(rgb_lbl, "card_bold")
    rgb_lbl.grid(row=0, column=0, sticky="w", padx=(0, 10))
    rgb_lbl.bind("<Enter>", lambda e: set_desc(
        lambda: i18n.L("col.rgb.desc")))
    rgb_lbl.bind("<Leave>", lambda e: set_desc(None))
    R(lambda l=rgb_lbl: l.configure(text=i18n.L("col.rgb.name"))
      if _live(l) else False)

    # v8.45 arithmetic: one slot of the 15-box grid is one box pitch
    # times five - pitch = canvas 24 + border 2 + pack padding 2*2 =
    # 30 px, so the slot is 150 px and the canvas is 150 - 4 padding
    # - 2 border = 144 px.  Three of them span exactly 446 px outer
    # edge to outer edge - the same span as the fifteen preset
    # swatches below, edges included.
    RGB_SLOT = 5 * (CHIP_SW + 2 + 2 * CHIP_PAD)         # 150
    RGB_BW, RGB_BH = RGB_SLOT - 2 * CHIP_PAD - 2, 22    # 144
    rgb_box = tk.Frame(rgb_cell, bg=pal["card"])
    kit.reg(rgb_box, "card")
    rgb_box.grid(row=0, column=1, sticky="e")
    rgb_chips = {}
    for _ch in ("r", "g", "b"):
        _bx = tk.Canvas(rgb_box, width=RGB_BW, height=RGB_BH,
                        bg="#000000", highlightthickness=1,
                        highlightbackground=pal["entry_bd"], takefocus=0)
        kit.reg(_bx, "hl")
        _bx.pack(side="left", padx=CHIP_PAD)
        rgb_chips[_ch] = _bx

    def paint_rgb_chips():
        """v8.43: glow each channel box with its own share - brighter
        red means more red in the picked colour, and so on."""
        try:
            vals = {"r": max(0, min(255, int(rgb_vars["r"].get()))),
                    "g": max(0, min(255, int(rgb_vars["g"].get()))),
                    "b": max(0, min(255, int(rgb_vars["b"].get())))}
        except (ValueError, tk.TclError):
            return
        for ch, val in vals.items():
            box = rgb_chips.get(ch)
            if box is None or not _live(box):
                continue
            try:
                if ch == "r":
                    box.configure(bg="#%02x0000" % val)
                elif ch == "g":
                    box.configure(bg="#00%02x00" % val)
                else:
                    box.configure(bg="#0000%02x" % val)
            except tk.TclError:
                pass

    host = tk.Frame(cp, bg=pal["card"])
    kit.reg(host, "card")
    host.pack(fill="x", padx=6, pady=(0, 8))
    # v8.43: column 0 takes all the slack, so the controls column is
    # pushed against the RIGHT edge of the window; its own 10 px pad
    # plus the host's 6 px make the same 16 px gap every setting
    # value keeps on every tab.
    host.columnconfigure(0, weight=1)

    # Row 1: picker left, everything about the picked colour on the
    # right side of the window - the two columns start on the same
    # row, so the value stack sits exactly beside the picker, not
    # beside the settings above it.
    left = tk.Frame(host, bg=pal["card"])
    kit.reg(left, "card")
    left.grid(row=0, column=0, sticky="nw")

    SV = 200
    sv_canvas = tk.Canvas(left, width=SV, height=SV, cursor="crosshair",
                          highlightthickness=1,
                          highlightbackground=pal["entry_bd"], takefocus=0)
    sv_canvas.pack(anchor="w", pady=(6, 0), padx=(10, 0))
    kit.reg(sv_canvas, "hl")
    hue_canvas = tk.Canvas(left, width=SV, height=22, cursor="crosshair",
                           highlightthickness=1,
                           highlightbackground=pal["entry_bd"], takefocus=0)
    hue_canvas.pack(anchor="w", pady=(6, 0), padx=(10, 0))
    kit.reg(hue_canvas, "hl")

    right = tk.Frame(host, bg=pal["card"])
    kit.reg(right, "card")
    right.grid(row=0, column=1, sticky="ne", padx=(18, 10))

    # v8.45 layout, top to bottom, every block flush with the same
    # RIGHT edge - the window's, minus the shared 16 px gap - AND
    # every block spanning the same 15-BOX GRID (the owner's
    # alignment rule): colour showcase (with its #value drawn INSIDE
    # it) -> the fifteen presets -> the two add buttons (one per
    # list, no Target caption) -> the screen row (no Auto caption) ->
    # the fifteen suggestion boxes, empty until "Suggest colors from
    # screen" fills them.  The R,G,B row lives UP in the settings
    # grid as three glowing channel boxes of five units each, so this
    # block opens level with the TOP of the picker surface (same pady
    # as the picker canvas).
    #
    # The showcase size is arithmetic, NOT measured: a
    # winfo_reqwidth() taken before the window maps returns garbage on
    # real Tk (the old "as wide as the RGB row" rule silently shipped a
    # 120 px box).  WIDTH: it spans exactly the preset row below it -
    # right edge on the last swatch's right edge, left edge on the
    # first swatch's left edge (owner's rule, now read from the
    # right).  HEIGHT (v8.45): the showcase absorbs all the vertical
    # slack so the BOTTOM of the suggestion boxes lands exactly on
    # the bottom of the hue slider in the left column.  Both columns
    # start on the same row and every block below the showcase has a
    # fixed pixel height - swatch rows are canvas 24 + border 2, the
    # button pills are ThemeKit.BTN_H - and fixed pack padding, so
    # this is exact subtraction, not measurement:
    #   left  = 6 + (SV + 2) + 6 + (22 + 2)                  = 238
    #   right = 6 + (SHOW_H + 2) + (8 + 26 + 8) + (BTN_H + 6)
    #           + (BTN_H + 6) + (4 + 26)
    # SHOW_H solves to 84.
    PRESET_SW, PRESET_PAD = 24, 2
    PRESET_SPAN = (len(COLOR_PRESETS) * (PRESET_SW + 2 + 2 * PRESET_PAD)
                   - 2 * PRESET_PAD)          # 15 boxes: 446
    SHOW_W = PRESET_SPAN - 2          # minus the showcase's own border
    BTN_GAP = 6                       # between the two buttons of a row
    BTN_W = (PRESET_SPAN - BTN_GAP) // 2   # 220: 2 + 220 + 6 + 220 + 2
    LEFT_H = 6 + (SV + 2) + 6 + (22 + 2)
    SHOW_H = (LEFT_H - 8
              - (8 + PRESET_SW + 2 + 8)
              - 2 * (kit.BTN_H + 6)
              - (4 + PRESET_SW + 2))
    prev = tk.Canvas(right, width=SHOW_W, height=SHOW_H, bg="#c62828",
                     highlightthickness=1,
                     highlightbackground=pal["entry_bd"])
    prev.pack(anchor="e", padx=(0, PRESET_PAD), pady=(6, 0))
    kit.reg(prev, "hl")

    sw_row = tk.Frame(right, bg=pal["card"])
    kit.reg(sw_row, "card")
    sw_row.pack(anchor="e", pady=(8, 8))

    picker = {"h": 0.02, "s": 0.8, "v": 0.8, "lock": False}
    sv_photo = [None]
    hue_photo = [None]
    sv_mark = [None]
    hue_mark = [None]

    def _hsv_grid(h, size=SV):
        ys, xs = np.mgrid[0:size, 0:size].astype(np.float64)
        ss = xs / (size - 1)
        vv = 1.0 - ys / (size - 1)
        h6 = h * 6.0
        i = (np.floor(h6) % 6).astype(np.int64)
        f = h6 - np.floor(h6)
        p = vv * (1 - ss)
        q = vv * (1 - ss * f)
        t = vv * (1 - ss * (1 - f))
        r = np.choose(i, [vv, q, p, p, t, vv])
        g = np.choose(i, [t, vv, vv, q, p, p])
        b = np.choose(i, [p, p, t, vv, vv, q])
        return (np.dstack([r, g, b]) * 255).astype(np.uint8)

    def render_sv():
        buf = io.BytesIO()
        _PILImage.fromarray(_hsv_grid(picker["h"]), "RGB").save(
            buf, format="PNG")
        sv_photo[0] = tk.PhotoImage(data=buf.getvalue())
        sv_canvas.delete("bg")
        sv_canvas.create_image(0, 0, anchor="nw", image=sv_photo[0],
                               tags="bg")
        place_sv_mark()

    def render_hue():
        arr = np.zeros((22, SV, 3), dtype=np.uint8)
        for x in range(SV):
            r, g, b = colorsys.hsv_to_rgb(x / (SV - 1.0), 1.0, 1.0)
            arr[:, x] = (int(r * 255), int(g * 255), int(b * 255))
        buf = io.BytesIO()
        _PILImage.fromarray(arr, "RGB").save(buf, format="PNG")
        hue_photo[0] = tk.PhotoImage(data=buf.getvalue())
        # v8.44: tag the gradient so a re-render replaces it instead
        # of stacking a second image under the first.
        hue_canvas.delete("bg")
        hue_canvas.create_image(0, 0, anchor="nw", image=hue_photo[0],
                                tags="bg")
        place_hue_mark()

    def place_sv_mark():
        x = picker["s"] * (SV - 1)
        y = (1.0 - picker["v"]) * (SV - 1)
        # v8.44: tag-based, like the hue mark - item ids are per
        # canvas, so an id kept from one canvas must never be used to
        # delete on it again.
        sv_canvas.delete("smark")
        sv_mark[0] = sv_canvas.create_oval(x - 5, y - 5, x + 5, y + 5,
                                           outline="#ffffff", width=2,
                                           tags="smark")

    def place_hue_mark():
        x = picker["h"] * (SV - 1)
        # v8.44 WHITE-SLIDER FIX: this used to delete the OLD mark on
        # sv_canvas (wrong canvas!) and then draw a NEW white rectangle
        # on the hue bar every single call.  The deletes ate items of
        # the picker square and the undeleted marks stacked up on the
        # bar - after a few drags the hue slider was a solid white
        # strip (still clickable, hence "works but looks weird").  One
        # tagged mark, replaced in place, on its own canvas.
        hue_canvas.delete("hmark")
        hue_mark[0] = hue_canvas.create_rectangle(x - 2, 0, x + 2, 21,
                                                  outline="#ffffff",
                                                  width=2, tags="hmark")

    def paint_preview(*_a):
        """The showcase: fill it with the picked colour and draw the
        #value inside it, in whichever of black/white contrasts - and
        (v8.43) glow the three channel boxes of the Current RGB Value
        row with their share of the same colour."""
        paint_rgb_chips()
        try:
            r = max(0, min(255, int(rgb_vars["r"].get())))
            g = max(0, min(255, int(rgb_vars["g"].get())))
            b = max(0, min(255, int(rgb_vars["b"].get())))
        except (ValueError, tk.TclError):
            return
        hx = "#%02x%02x%02x" % (r, g, b)
        try:
            prev.configure(bg=hx)
            prev.delete("all")
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
            # v8.45: the showcase is tall now - keep the #value dead
            # centre of it, read back from the widget, not hardcoded.
            prev.create_text(int(prev.cget("width")) // 2,
                             int(prev.cget("height")) // 2,
                             text=hx, font=F_BTN,
                             fill="#ffffff" if lum < 0.55 else "#1b1b1b")
        except tk.TclError:
            pass

    def push_to_entries():
        picker["lock"] = True
        r, g, b = colorsys.hsv_to_rgb(picker["h"], picker["s"],
                                      picker["v"])
        rgb_vars["r"].set(str(int(round(r * 255))))
        rgb_vars["g"].set(str(int(round(g * 255))))
        rgb_vars["b"].set(str(int(round(b * 255))))
        paint_preview()
        picker["lock"] = False

    def entries_changed(*_a):
        if picker["lock"]:
            return
        try:
            r = max(0, min(255, int(rgb_vars["r"].get())))
            g = max(0, min(255, int(rgb_vars["g"].get())))
            b = max(0, min(255, int(rgb_vars["b"].get())))
        except (ValueError, tk.TclError):
            return
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        picker["h"], picker["s"], picker["v"] = h, s, v
        render_sv()
        place_hue_mark()
        paint_preview()

    # v8.41: the traces are attached AFTER entries_changed exists - the
    # R,G,B row is built first now (it is the topmost block), so the
    # old order would have referenced the function too early.
    for _v in rgb_vars.values():
        _v.trace_add("write", entries_changed)

    def on_sv(event):
        x = max(0, min(SV - 1, event.x))
        y = max(0, min(SV - 1, event.y))
        picker["s"] = x / (SV - 1.0)
        picker["v"] = 1.0 - y / (SV - 1.0)
        place_sv_mark()
        push_to_entries()

    def on_hue(event):
        x = max(0, min(SV - 1, event.x))
        picker["h"] = x / (SV - 1.0)
        render_sv()
        place_hue_mark()
        push_to_entries()

    sv_canvas.bind("<Button-1>", on_sv)
    sv_canvas.bind("<B1-Motion>", on_sv)
    hue_canvas.bind("<Button-1>", on_hue)
    hue_canvas.bind("<B1-Motion>", on_hue)

    def set_rgb(r, g, b):
        picker["lock"] = True
        rgb_vars["r"].set(str(r))
        rgb_vars["g"].set(str(g))
        rgb_vars["b"].set(str(b))
        picker["lock"] = False
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        picker["h"], picker["s"], picker["v"] = h, s, v
        render_sv()
        place_hue_mark()
        paint_preview()

    for name, rgb in COLOR_PRESETS:
        hx = "#%02x%02x%02x" % rgb
        sw = tk.Canvas(sw_row, width=PRESET_SW, height=PRESET_SW, bg=hx,
                       highlightthickness=1,
                       highlightbackground=pal["entry_bd"],
                       cursor="hand2", takefocus=0)
        sw.pack(side="left", padx=PRESET_PAD)
        sw.bind("<Button-1>", lambda e, rr=rgb: set_rgb(*rr))
        sw.bind("<Enter>", lambda e, n=name: set_desc(
            lambda: i18n.L("st.preset_desc", n)))
        sw.bind("<Leave>", lambda e: set_desc(None))

    # ---- v8.44: two ADD buttons, no Target row --------------------
    # The old row asked the user to aim a selector (Accent | Exclude)
    # and THEN press Add Color.  Now every list owns its button: the
    # colour standing in the picker goes straight where the label
    # says - "Add to preferred colours" / "Add to refused colours".
    # No "Target:" caption: the two buttons are the whole row.
    # v8.45: all FOUR buttons of the right column are one size - each
    # exactly BTN_W (220) px wide - and the two of a row span the
    # 15-box grid perfectly: 2 px outer padding + 220 + 6 px gap +
    # 220 + 2 px = the same 450 px row, the same outer edges as the
    # preset swatches above and below.
    add_row = tk.Frame(right, bg=pal["card"])
    kit.reg(add_row, "card")
    add_row.pack(anchor="e", pady=(0, 6))
    _TARGET_KEY = {"accent": "accent_color", "exclude": "exclude_color"}
    _TARGET_NAME = {"accent": i18n.L("col.accent"),
                    "exclude": i18n.L("col.exclude")}
    R(lambda: (_TARGET_NAME.update(
        {"accent": i18n.L("col.accent"),
         "exclude": i18n.L("col.exclude")}), True)[1])

    def read_rgb():
        try:
            r = max(0, min(255, int(rgb_vars["r"].get())))
            g = max(0, min(255, int(rgb_vars["g"].get())))
            b = max(0, min(255, int(rgb_vars["b"].get())))
            return r, g, b
        except (ValueError, tk.TclError):
            return None

    def add_color(which):
        """v8.41: APPEND the picked colour to the chosen field with a
        ';' separator - the old replace behaviour silently threw the
        user's existing colour list away.
        v8.43: the list is capped (the strip of boxes the setting
        shows), and the press past the cap says so instead of growing
        the value past what the row can display.  v8.45: the cap is
        FIFTEEN - one full span of the 15-box grid - so the sixteenth
        press is the one that refuses.
        v8.44: `which` is the button that was pressed ("accent" /
        "exclude") - the button label IS the target, no selector."""
        rgb = read_rgb()
        if rgb is None:
            status_msg(i18n.L("st.rgb_bad"))
            return
        key = _TARGET_KEY[which]
        var = vars_[key][1]
        cur = str(var.get() or "").strip()
        parts = ([p.strip() for p in cur.split(";") if p.strip()]
                 if cur.lower() not in ("", "off") else [])
        if len(parts) >= _MAX_CHIPS:
            status_msg(i18n.L("st.color_full", _TARGET_NAME[which]))
            return
        spec = "%d,%d,%d" % rgb
        if spec in parts:
            status_msg(i18n.L("st.color_already", rgb[0], rgb[1],
                              rgb[2], _TARGET_NAME[which]))
            return
        parts.append(spec)
        var.set("; ".join(parts))
        status_msg(i18n.L("st.color_added", rgb[0], rgb[1], rgb[2],
                          _TARGET_NAME[which]))

    add_pref_btn = kit.button(add_row, i18n.L("col.add_pref"),
                              lambda: add_color("accent"), kind="accent",
                              fixed_w=BTN_W)
    add_pref_btn.pack(side="left", padx=(PRESET_PAD, BTN_GAP // 2))
    R(lambda: kit.set_text(add_pref_btn, i18n.L("col.add_pref"))
      if _live(add_pref_btn) else False)
    add_ref_btn = kit.button(add_row, i18n.L("col.add_ref"),
                             lambda: add_color("exclude"), fixed_w=BTN_W)
    add_ref_btn.pack(side="left", padx=(BTN_GAP // 2, PRESET_PAD))
    R(lambda: kit.set_text(add_ref_btn, i18n.L("col.add_ref"))
      if _live(add_ref_btn) else False)

    # ---- v8.44: the screen row - no "Auto:" caption either --------
    # Two buttons, nothing else: one takes the single colour under
    # the cursor, the other fills the suggestion strip below.
    auto_row = tk.Frame(right, bg=pal["card"])
    kit.reg(auto_row, "card")
    auto_row.pack(anchor="e", pady=(0, 6))

    def pick_from_screen():
        status_msg(i18n.L("st.pick_wait"))

        def cap():
            try:
                x, y = get_cursor_pos()
                img = app._capture.grab(x, y, x + 1, y + 1)
                if img is not None:
                    bb, gg, rr = [int(vv) for vv in img[0, 0]]
                    set_rgb(rr, gg, bb)
                    status_msg(i18n.L("st.pick_ok", rr, gg, bb, x, y))
                else:
                    status_msg(i18n.L("st.pick_fail"))
            except Exception as exc:
                status_msg(i18n.L("st.pick_err", exc))
        root.after(3000, cap)

    pick_btn = kit.button(auto_row, i18n.L("col.pick"), pick_from_screen,
                          fixed_w=BTN_W)
    pick_btn.pack(side="left", padx=(PRESET_PAD, BTN_GAP // 2))
    R(lambda: kit.set_text(pick_btn, i18n.L("col.pick"))
      if _live(pick_btn) else False)

    # ---- suggested swatches (v8.44) --------------------------------
    # FIFTEEN boxes (v8.45), the SAME size and spacing as the premade
    # preset swatches above, in their own right-flush row under the
    # screen buttons - so the suggestion row spans the same 15-box
    # grid as everything else.  The row starts empty and fills when
    # "Suggest colors from screen" finds colours around the cursor;
    # clicking a box loads it into the picker like a preset does.
    SUG_N = 15
    sug_row = tk.Frame(right, bg=pal["card"])
    kit.reg(sug_row, "card")
    sug_row.pack(anchor="e", pady=(4, 0))

    def _show_suggestions(sug):
        """Rebuild the suggestion strip - main thread only."""
        if not _live(sug_row):
            return
        for child in sug_row.winfo_children():
            child.destroy()
        sug = list(sug or [])[:SUG_N]
        if not sug:
            status_msg(i18n.L("st.sug_none"))
            return
        for rgb, frac in sug:
            hx = "#%02x%02x%02x" % rgb
            sw = tk.Canvas(sug_row, width=PRESET_SW, height=PRESET_SW,
                           bg=hx, highlightthickness=1,
                           highlightbackground=pal["entry_bd"],
                           cursor="hand2", takefocus=0)
            kit.reg(sw, "hl")
            sw.pack(side="left", padx=PRESET_PAD)
            sw.bind("<Button-1>", lambda e, rr=rgb: (
                set_rgb(*rr),
                status_msg(i18n.L("st.sug_loaded", rr[0], rr[1],
                                  rr[2]))))
            sw.bind("<Enter>",
                    lambda e, rr=rgb, ff=frac: set_desc(
                        lambda: i18n.L("st.sug_loaded_desc",
                                       rr[0], rr[1], rr[2],
                                       int(round(ff * 100)))))
            sw.bind("<Leave>", lambda e: set_desc(None))
        status_msg(i18n.L("st.sug_ok", len(sug)))

    def suggest_from_screen():
        status_msg(i18n.L("st.sug_wait"))

        def work():
            # v8.44 debug: capture + binning now run OFF the UI thread.
            # On the main thread a slow first capture (mss setup, dxcam
            # retrying a static desktop) froze the window for seconds
            # and any raise inside the after() callback died with no
            # status at all - the button looked dead.  The worker only
            # touches plain data; every outcome - colour boxes, "no
            # suggestions", "capture failed", the exception text -
            # comes back through root.after as a readable status.
            try:
                # the status line promises 3 s to point at the target
                # app - sleep HERE, in the worker, so the window stays
                # responsive while the aim time runs down (and so the
                # sample never catches our own settings window)
                time.sleep(3.0)
                x, y = get_cursor_pos()
                vx, vy, vw, vh = virtual_screen()
                w, h = min(640, vw), min(400, vh)
                left = max(vx, min(x - w // 2, vx + vw - w))
                top = max(vy, min(y - h // 2, vy + vh - h))
                img = app._capture.grab(left, top, left + w, top + h)
                if img is None:
                    # a static desktop hands dxcam no new frame at
                    # all: one patient retry before giving up
                    time.sleep(0.3)
                    img = app._capture.grab(left, top, left + w,
                                            top + h)
                if img is None:
                    root.after(0, lambda: status_msg(
                        i18n.L("st.pick_fail")))
                    return
                sug = vision.suggest_accents(img, SUG_N)
                root.after(0, lambda: _show_suggestions(sug))
            except Exception as exc:
                # Eager default-arg capture: Python deletes an
                # `except ... as` name when the block exits, so a bare
                # closure over exc would raise NameError when the
                # deferred callback finally runs (exactly when the
                # error report matters most).
                root.after(0, lambda exc=exc: status_msg(
                    i18n.L("st.sug_fail", exc)))

        threading.Thread(target=work, daemon=True,
                         name="snappy-suggest").start()

    # v8.41: the suggest button lives in the screen row, beside the
    # picker button - one row for everything taken from the screen.
    # v8.45: same fixed size as the other three, so the row spans the
    # 15-box grid exactly like the add row above it.
    _b_sug = kit.button(auto_row, i18n.L("col.suggest"),
                        suggest_from_screen, fixed_w=BTN_W)
    _b_sug.pack(side="left", padx=(BTN_GAP // 2, PRESET_PAD))
    R(lambda: kit.set_text(_b_sug, i18n.L("col.suggest"))
      if _live(_b_sug) else False)

    render_hue()
    render_sv()
    entries_changed()

    _wrapping_note(cp, kit, pal, "note.colors")

    # v8.40: the Keybindings tab explains itself.  Shortcut rows on
    # top (the settings), then what the two modes do, how recordings
    # work and how single keys differ from combos, then the tab note -
    # the page scrolls because prose plus twelve rows no longer fits.
    # NB: the SLUG is "hotkeys" (only the display name is
    # "Keybindings"), so the page lives at pages["hotkeys"].
    kbp = pages["hotkeys"]
    kinner, kbind = _scrollable(kbp, kit, pal)
    kgrid = tk.Frame(kinner, bg=pal["card"])
    kit.reg(kgrid, "card")
    kgrid.pack(fill="x", padx=6, pady=8)
    kgrid.columnconfigure(0, weight=1)
    for _ki, _kkey in enumerate(TAB_KEYS):
        make_row(kgrid, _kkey, _ki)

    def _kb_block(title_key, body_key):
        h = tk.Label(kinner, text=i18n.L(title_key), font=F_BOLD,
                     bg=pal["card"], fg=pal["text"], anchor="w")
        kit.reg(h, "card_bold")
        h.pack(fill="x", padx=14, pady=(12, 2))
        kbind(h)
        R(lambda: h.configure(text=i18n.L(title_key)) if _live(h)
          else False)
        b = tk.Label(kinner, text=i18n.L(body_key), font=F_DESC,
                     bg=pal["card"], fg=pal["muted"], anchor="w",
                     justify="left")
        kit.reg(b, "card_muted")
        b.pack(fill="x", padx=14, pady=(0, 2))
        kbind(b)
        R(lambda: b.configure(text=i18n.L(body_key)) if _live(b)
          else False)
        return b

    _kb_blocks = [_kb_block(t, b) for t, b in KB_KEYS]

    def _kb_wrap(_event=None):
        try:
            want = max(200, kinner.winfo_width() - 32)
            for lb in _kb_blocks:
                if str(lb.cget("wraplength")) != str(want):
                    lb.configure(wraplength=want)
        except tk.TclError:
            pass

    kinner.bind("<Configure>", _kb_wrap, add="+")
    _kb_wrap()
    _wrapping_note(kinner, kit, pal, "note.keybindings")

    # ---------------- Macros (v8.46) ----------------
    # Two columns. LEFT: the five KEY MACROS - one blocked trigger ->
    # one combo press; the per-row "one press, trigger blocked" hint is
    # gone (the tab note says it once). RIGHT: the recorder library in
    # a compact bordered box - FIVE recordings is the cap (Ctrl+1..5
    # launch them by list position), so the old full-height listbox
    # shrank to a fixed five-row window that sits BESIDE the macros.
    # Every recording row carries its OWN "Repeat until stopped" pill
    # switch (the Assistance tab's control; the switch column is only
    # visible once at least one recording exists), Rename / Export /
    # Import / Delete sit side by side in the box's bottom-right
    # corner, and clicking a row selects that recording for those
    # buttons and the play shortcut. Since v8.46 a recording captures
    # EVERYTHING: every key, every mouse button and the cursor trail.
    mac = pages["macros"]
    mbody = tk.Frame(mac, bg=pal["card"])
    kit.reg(mbody, "card")
    mbody.pack(fill="x", padx=14, pady=8)

    def mac_head(parent, key):
        """One column heading; re-words itself on a language switch."""
        h = tk.Label(parent, text=i18n.L(key), font=F_BOLD,
                     bg=pal["card"], fg=pal["text"], anchor="w")
        kit.reg(h, "card_bold")
        h.pack(fill="x", pady=(0, 6))
        R(lambda h=h, k=key: h.configure(text=i18n.L(k))
          if _live(h) else False)
        h.bind("<Enter>", lambda e: set_desc(
            lambda: i18n.L("note.macros")))
        h.bind("<Leave>", lambda e: set_desc(None))
        return h

    # ---- left column: the five key macros ----------------------------
    mleft = tk.Frame(mbody, bg=pal["card"])
    kit.reg(mleft, "card")
    mleft.pack(side="left", fill="y")
    mac_head(mleft, "mac.keys_head")

    def macro_entry(parent, key, width, desc_key):
        if key not in vars_:
            var = tk.StringVar(value=str(cfg.get(key)))
            vars_[key] = ("str", var)
            var.trace_add("write", mark_dirty)
        else:
            var = vars_[key][1]
        en = tk.Entry(parent, textvariable=var, width=width,
                      font=F_ENTRY, relief="solid", borderwidth=1,
                      bg=pal["entry"], fg=pal["text"],
                      insertbackground=pal["text"],
                      highlightbackground=pal["entry_bd"],
                      highlightthickness=1)
        kit.reg(en, "entry")
        en.bind("<Enter>", lambda e, k=desc_key: set_desc(
            lambda: tr_desc(k)))
        en.bind("<Leave>", lambda e: set_desc(None))
        return en

    def macro_word(parent, key, desc_key):
        w = tk.Label(parent, text=i18n.L(key), font=F_DESC,
                     bg=pal["card"], fg=pal["muted"])
        kit.reg(w, "card_muted")
        w.pack(side="left", padx=(0, 6))
        R(lambda: w.configure(text=i18n.L(key)) if _live(w) else False)
        w.bind("<Enter>", lambda e, k=desc_key: set_desc(
            lambda: tr_desc(k)))
        w.bind("<Leave>", lambda e: set_desc(None))
        return w

    for i in range(1, MACRO_SLOTS + 1):
        row = tk.Frame(mleft, bg=pal["card"])
        kit.reg(row, "card")
        row.pack(fill="x", pady=6)

        lb = tk.Label(row, text=i18n.L("mac.row", i), font=F_BOLD,
                      width=8, bg=pal["card"], fg=pal["text"],
                      anchor="w")
        kit.reg(lb, "card_bold")
        lb.pack(side="left")
        R(lambda l=lb, n=i: l.configure(text=i18n.L("mac.row", n))
          if _live(l) else False)
        mkey = "macro%d_key" % i
        mact = "macro%d_action" % i
        lb.bind("<Enter>", lambda e, k=mkey: set_desc(
            lambda: tr_desc(k)))
        lb.bind("<Leave>", lambda e: set_desc(None))

        macro_entry(row, mkey, 10, mkey).pack(side="left", padx=(0, 8))
        macro_word(row, "mac.sends", mact)
        macro_entry(row, mact, 16, mact).pack(side="left")

    # ---- right column: the recorder library box ----------------------
    mright = tk.Frame(mbody, bg=pal["card"])
    kit.reg(mright, "card")
    mright.pack(side="left", fill="both", expand=True, padx=(24, 0))
    mac_head(mright, "mac.recordings")

    rec_state = tk.StringVar(value="")
    rec_lbl = tk.Label(mright, textvariable=rec_state, font=F_DESC,
                       bg=pal["card"], fg=pal["muted"], anchor="w",
                       justify="left")
    kit.reg(rec_lbl, "card_muted")
    rec_lbl.pack(fill="x", pady=(0, 6))

    REC_ROW_H = 26                       # one recording row's height
    rec_box = tk.Frame(mright, bg=pal["card"], highlightthickness=1,
                       highlightbackground=pal["entry_bd"],
                       highlightcolor=pal["entry_bd"])
    kit.reg(rec_box, "panel")
    rec_box.pack(fill="x")

    # Pack order inside the box: the button row reserves the BOTTOM
    # first, the rows area fills what is left, and the switch-column
    # caption packs itself above the rows (only while recordings
    # exist) when the library rebuilds.
    btn_row = tk.Frame(rec_box, bg=pal["card"])
    kit.reg(btn_row, "card")
    btn_row.pack(side="bottom", fill="x", padx=8, pady=(4, 8))

    loop_head = tk.Label(rec_box, text=i18n.L("mac.loop"),
                         font=F_DESC, bg=pal["card"], fg=pal["muted"],
                         anchor="e")
    kit.reg(loop_head, "card_muted")
    R(lambda: loop_head.configure(text=i18n.L("mac.loop"))
      if _live(loop_head) else False)
    loop_head.bind("<Enter>", lambda e: set_desc(
        lambda: i18n.L("st.loop_desc")))
    loop_head.bind("<Leave>", lambda e: set_desc(None))

    rec_rows = tk.Frame(rec_box, bg=pal["card"])
    kit.reg(rec_rows, "card")
    rec_rows.pack(side="top", fill="both", expand=True,
                  padx=6, pady=(0, 2))
    rec_rows.pack_propagate(False)
    rec_rows.configure(height=REC_ROW_H * REC_PLAY_SLOTS)

    rec_ids = []
    rec_row_w = []          # [(rid, frame, [widgets wearing the row bg])]
    rec_row_paints = []     # the rows' switch repaint callbacks
    sel_rid = [None]
    rec_ph = [None]         # the empty-library placeholder label

    def selected_rid():
        rid = sel_rid[0]
        return rid if rid in rec_ids else None

    def paint_rows():
        sel = selected_rid()
        for r_id, _fr, ws in rec_row_w:
            on = (r_id == sel)
            bg = pal["light_bg"] if on else pal["card"]
            for w in ws:
                try:
                    w.configure(bg=bg)
                except tk.TclError:
                    pass
            try:
                ws[1].configure(fg=pal["accent"] if on
                                else pal["text"])
            except tk.TclError:
                pass

    def select_rec(rid, _event=None):
        sel_rid[0] = rid
        app.set_play_target(rid)
        paint_rows()

    def make_rec_row(n, rec):
        rid = rec["id"]
        bg = pal["light_bg"] if rid == selected_rid() else pal["card"]
        fr = tk.Frame(rec_rows, bg=bg, cursor="hand2")
        fr.pack(fill="x", pady=1)

        # the row's OWN repeat switch (independent per recording)
        var = tk.BooleanVar(value=bool(rec["loop"]))
        sw = kit.bool_switch(fr, var, word=True)
        sw.pack(side="right", padx=(6, 6))

        def on_toggle(*_a):
            try:
                on = bool(var.get())
            except (tk.TclError, ValueError):
                on = False
            if app.rec_store.set_loop(rid, on):
                app.rec_store.save()
                status_msg(i18n.L(
                    "st.rec_now", rec["name"],
                    i18n.L("st.rec_repeats") if on
                    else i18n.L("st.rec_once")))
        var.trace_add("write", on_toggle)

        st_lbl = tk.Label(fr, text=i18n.L("mac.steps", len(rec["steps"])),
                          font=F_DESC, bg=bg, fg=pal["muted"])
        st_lbl.pack(side="right", padx=(8, 0))
        num = tk.Label(fr, text="%d." % n, font=F_BOLD, width=3,
                       bg=bg, fg=pal["text"], anchor="w")
        num.pack(side="left")
        name = tk.Label(fr, text=rec["name"], font=F_BASE, bg=bg,
                        fg=pal["text"], anchor="w")
        name.pack(side="left", fill="x", expand=True, padx=(2, 6))

        for w in (fr, num, name, st_lbl):
            w.bind("<Button-1>", lambda e, r=rid: select_rec(r))
        sw_widgets = [sw] + list(sw.winfo_children())
        for w in sw_widgets:
            try:
                w.configure(bg=bg)
            except tk.TclError:
                pass
            w.bind("<Enter>", lambda e: set_desc(
                lambda: i18n.L("st.loop_desc")))
            w.bind("<Leave>", lambda e: set_desc(None))
        rec_row_w.append((rid, fr, [fr, num, name, st_lbl] + sw_widgets))

    def _ph_fit(_event=None):
        """Wrap the empty-library placeholder to the row area's live
        width (garbage-safe: winfo_width is 1 before the first map)."""
        ph = rec_ph[0]
        if ph is None or not _live(ph):
            return
        try:
            want = rec_rows.winfo_width() - 20
            if want > 120 and str(ph.cget("wraplength")) != str(want):
                ph.configure(wraplength=want)
        except tk.TclError:
            pass

    rec_rows.bind("<Configure>", _ph_fit)

    def do_rename_rec():
        rid = selected_rid()
        rec = app.rec_store.get(rid) if rid is not None else None
        if rec is None:
            status_msg(i18n.L("st.select_rec") if rec_ids
                       else i18n.L("st.lib_empty"))
            return
        position = rec_ids.index(rid) + 1
        new = simpledialog.askstring(
            APP_NAME, i18n.L("st.rename_prompt", position),
            initialvalue=rec["name"], parent=root)
        if new is None:
            return
        if app.rec_store.set_name(rid, new):
            app.rec_store.save()
            rebuild_recs()
            status_msg(i18n.L("st.renamed"))
        else:
            status_msg(i18n.L("st.name_empty"))

    def do_delete_rec():
        rid = selected_rid()
        rec = app.rec_store.get(rid) if rid is not None else None
        if rec is None:
            status_msg(i18n.L("st.select_rec") if rec_ids
                       else i18n.L("st.lib_empty"))
            return
        if not messagebox.askyesno(
                APP_NAME, i18n.L("st.delete_confirm", rec["name"]),
                parent=root):
            return
        app.rec_store.remove(rid)
        app.rec_store.save()
        if sel_rid[0] == rid:
            sel_rid[0] = None
        rebuild_recs()
        status_msg(i18n.L("st.deleted"))

    def _safe_filename(name):
        """A save-dialog initial filename built from the recording's
        name - cross-platform-safe characters only."""
        safe = "".join(c if (c.isalnum() or c in " -_") else "_"
                       for c in str(name)).strip(" -_")
        return (safe[:40] or "recording") + ".json"

    def do_export_rec():
        # v8.46 fix: Export saves the recording the user CLICKED (its
        # row selection), and the dialog is owned by the main window -
        # unowned dialogs could open behind it, which read as "Export
        # does nothing".
        rid = selected_rid()
        rec = app.rec_store.get(rid) if rid is not None else None
        if rec is None:
            status_msg(i18n.L("st.select_rec") if rec_ids
                       else i18n.L("st.lib_empty"))
            return
        path = filedialog.asksaveasfilename(
            parent=root,
            title=i18n.L("st.export_rec_title"),
            initialfile=_safe_filename(rec["name"]),
            defaultextension=".json",
            filetypes=[(i18n.L("st.file_rec"), "*.json")])
        if not path:
            return
        _ok, text = app.rec_store.export_to(path, rid)
        status_msg(text)

    def do_import_rec():
        path = filedialog.askopenfilename(
            parent=root,
            title=i18n.L("st.import_rec_title"),
            filetypes=[(i18n.L("st.file_rec"), "*.json"),
                       (i18n.L("st.all_files"), "*.*")])
        if not path:
            return
        _ok, text = app.rec_store.import_from(path)
        rebuild_recs()
        status_msg(text)

    # The four library buttons in the box's bottom-right corner, side
    # by side; packed right-first, so they READ Rename | Export |
    # Import | Delete with Delete (amber) on the far right.
    for _rk, _rf, _kd in (("mac.delete", do_delete_rec, "amber"),
                          ("mac.import", do_import_rec, "plain"),
                          ("mac.export", do_export_rec, "plain"),
                          ("mac.rename", do_rename_rec, "plain")):
        _b = kit.button(btn_row, i18n.L(_rk), _rf, kind=_kd)
        _b.pack(side="right", padx=(6, 0))
        R(lambda b=_b, k=_rk: kit.set_text(b, i18n.L(k))
          if _live(b) else False)

    def rebuild_recs():
        """Rebuild the five-row library: the poller calls this when the
        store/engine moved, and theme and language switches call it
        through kit.repaint / R.  Rows are transient widgets; their
        switch repaint callbacks are pruned here so kit.repaints can
        never grow without bound."""
        if not _live(rec_rows):
            return False
        for fn in rec_row_paints:
            try:
                kit.repaints.remove(fn)
            except ValueError:
                pass
        del rec_row_paints[:]
        for _rid, fr, _ws in rec_row_w:
            try:
                fr.destroy()
            except tk.TclError:
                pass
        del rec_row_w[:]
        ph = rec_ph[0]
        if ph is not None:
            try:
                ph.destroy()
            except tk.TclError:
                pass
            rec_ph[0] = None

        rec_ids[:] = [r["id"] for r in app.rec_store.recordings]
        if selected_rid() is None:
            sel_rid[0] = None

        n0 = len(kit.repaints)
        if rec_ids:
            # the switch column's caption is only visible once at
            # least one recording exists (v8.46, owner rule 4)
            loop_head.pack(side="top", fill="x", padx=8, pady=(6, 2),
                           before=rec_rows)
            for n, r in enumerate(app.rec_store.recordings, 1):
                make_rec_row(n, r)
        else:
            loop_head.pack_forget()
            ph = tk.Label(rec_rows, text=i18n.L("mac.empty"),
                          font=F_DESC, bg=pal["card"], fg=pal["muted"],
                          anchor="w", justify="left", wraplength=360)
            kit.reg(ph, "card_muted")
            ph.pack(fill="both", expand=True, padx=10, pady=6)
            rec_ph[0] = ph
            _ph_fit()
        rec_row_paints[:] = kit.repaints[n0:]
        paint_rows()

        recording = app._rec_buffer is not None
        playing = app._play_busy
        looping = playing and app._play_looping
        pname = ""
        if app._play_rid is not None:
            pr = app.rec_store.get(app._play_rid)
            pname = pr["name"] if pr else ""
        if recording:
            rec_state.set(i18n.L(
                "st.rec_recording",
                str(cfg.get("key_record_stop", "ctrl+alt+s")).lower()))
        elif looping:
            rec_state.set(i18n.L("st.rec_playing_loop", pname))
        elif playing:
            rec_state.set(i18n.L("st.rec_playing", pname))
        else:
            rec_state.set(i18n.L("st.rec_count", len(rec_ids)))
        return True

    # a language switch rebuilds the rows in the new wording
    R(lambda: rebuild_recs() if _live(rec_rows) else False)
    kit.repaint(rebuild_recs)
    rebuild_recs()

    _wrapping_note(mac, kit, pal, "note.macros", pady=(8, 2), padx=16)
    _wrapping_note(mac, kit, pal, "note.macros_keys", pady=(2, 2),
                   padx=16)

    # ---------------- Advanced ----------------
    # v8.27: EVERY remaining value option lived here; v8.39 made it a
    # single left-aligned column of geometry/timing values - the size
    # and contrast gates moved to Handler, the dropdowns to
    # Experimental, the switches stay on Assistance.
    adv = pages["advanced"]
    fill_list(adv, TAB_ADV)
    _wrapping_note(adv, kit, pal, "note.advanced")

    # ---------------- Handler (v8.38, renamed v8.39) ----------------
    # What counts as an item: the two contrast gates, the three size
    # gates and the three accent-matching knobs.  Single column, like
    # every other settings tab; the adaptivity switches live on
    # Assistance, the picker on Colors.
    chp = pages["handler"]
    fill_list(chp, TAB_COLOR)
    _wrapping_note(chp, kit, pal, "note.handler")

    # ---------------- Experimental (v8.38) ----------------
    # Every "choice"/"map" setting.  Each has a tested default; the
    # alternatives exist for A/B comparison (oklab vs hsv), special
    # hardware (capture backends) or tuning taste (follow boost).
    exp = pages["experimental"]
    fill_list(exp, TAB_EXPERIMENTAL)
    _wrapping_note(exp, kit, pal, "note.experimental")

    # ---------------- Help (v8.38) ----------------
    _fill_help(pages["help"], kit, pal)

    # ---------------- pollers ----------------
    poll_tick = [0]
    rec_ui = [None]

    def poll_status():
        if not root.winfo_exists():
            return
        running = app.running
        run_state.set(i18n.L("st.running") if running
                      else i18n.L("st.standby"))
        light.itemconfigure(light_dot,
                            fill=(pal["green"] if running
                                  else pal["amber"]))
        poll_tick[0] += 1
        if poll_tick[0] % 4 == 0 and not dirty["on"]:
            refresh_fields()      # pick up hotkey-driven changes live
        state_now = (app.rec_store.revision,
                     app.is_recording(),
                     app._play_busy, app._play_looping, app._play_rid)
        if rec_ui[0] != state_now:
            rec_ui[0] = state_now
            rebuild_recs()        # recorder / playback / library moved
        if time.perf_counter() > status_until[0]:
            mem = app.follow
            follow = ""
            if mem.when > 0:
                follow = i18n.L("st.follow",
                                int(time.perf_counter() - mem.when))
            _th = str(cfg.get("theme"))
            status_var.set(i18n.L(
                "st.line", app.snap_count, app.pass_count, follow,
                i18n.L("theme." + _th) if _th in ("light", "dark")
                else _th))
        after_ms(500, poll_status)

    shared_win = {"win": None}

    def close_shared_dialog():
        win = shared_win["win"]
        shared_win["win"] = None
        if win is not None:
            try:
                win.destroy()
            except tk.TclError:
                pass

    def open_shared_dialog():
        if shared_win["win"] is not None:
            return
        win = tk.Toplevel(root)
        shared_win["win"] = win
        kit.reg(win, "card")
        win.title("%s - %s" % (APP_NAME, i18n.L("shared.title")))
        win.configure(background=pal["card"])
        win.resizable(False, False)
        win.transient(root)
        win.grab_set()
        W2, H2 = 560, 400
        win.update_idletasks()
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        win.geometry("%dx%d+%d+%d" % (W2, H2, max(0, (sw - W2) // 2),
                                      max(0, (sh - H2) // 3)))
        # v8.47: flat themed card, same cleanup as the reject window -
        # the blurred-logo backdrop left red blotches in the margins.
        box = tk.Frame(win, bg=pal["card"])
        kit.reg(box, "card")
        box.place(relx=0.5, rely=0.5, anchor="center")
        t1 = tk.Label(box, text=i18n.L("shared.title"),
                      font=F_H1, bg=pal["card"], fg=pal["text"])
        kit.reg(t1, "card_text")
        t1.pack(pady=(14, 4))
        t2 = tk.Label(box, text=i18n.L("shared.body"),
                      font=F_DESC, bg=pal["card"], fg=pal["muted"],
                      justify="center", wraplength=440)
        kit.reg(t2, "card_muted")
        t2.pack(pady=(0, 12))

        def recheck():
            def worker():
                try:
                    rows, _gen = online.fetch_entitlements(cfg)
                except online.OnlineError:
                    root.after(0, lambda: status_msg(
                        i18n.L("shared.unreachable")))
                    return
                idh = identity_hash[0]
                shared = bool((rows.get(idh) or {}).get("shared"))
                root.after(0, lambda: finish(not shared))
            threading.Thread(target=worker, daemon=True,
                             name="shared-recheck").start()

        def finish(clean):
            if clean:
                close_shared_dialog()
                status_msg(i18n.L("shared.back"))
            else:
                status_msg(i18n.L("shared.still"))
        _s_rc = kit.button(box, i18n.L("shared.recheck"), recheck,
                           kind="green", big=True)
        _s_rc.pack(pady=(0, 8))
        _s_cl = kit.button(box, i18n.L("shared.close"), close_shared_dialog)
        _s_cl.pack(pady=(0, 14))

        def _shared_retext():
            if not _live(win):
                return False
            win.title("%s - %s" % (APP_NAME, i18n.L("shared.title")))
            t1.configure(text=i18n.L("shared.title"))
            t2.configure(text=i18n.L("shared.body"))
            kit.set_text(_s_rc, i18n.L("shared.recheck"))
            kit.set_text(_s_cl, i18n.L("shared.close"))
            return True

        R(_shared_retext)
        # v8.40: grow for long translations instead of clipping
        win.update_idletasks()
        need2 = box.winfo_reqheight() + 40
        if need2 > H2:
            H2 = need2
            win.geometry("%dx%d+%d+%d"
                         % (W2, H2, max(0, (sw - W2) // 2),
                            max(0, (sh - H2) // 3)))

        win.protocol("WM_DELETE_WINDOW", close_shared_dialog)

    identity_hash = [None]
    if identity:
        identity_hash[0] = online.row_hash(identity)

    def presence_watch():
        """Poll the shared flag at the (fixed) heartbeat cadence.

        The cadence comes from online.presence_interval_seconds(), not
        from config: it is part of the sharing enforcement, so it is not
        a user setting."""
        if not root.winfo_exists():
            return
        def worker():
            if not identity_hash[0]:
                return
            try:
                rows, _gen = online.fetch_entitlements(cfg)
            except online.OnlineError:
                return
            shared = bool((rows.get(identity_hash[0]) or {})
                          .get("shared"))
            root.after(0, lambda: apply_shared(shared))
        def apply_shared(shared):
            if not shared:
                return
            if app.running:
                post(11)
                log(i18n.L("st.shared_paused"))
            open_shared_dialog()
        threading.Thread(target=worker, daemon=True,
                         name="presence-watch").start()
        after_ms(max(1, online.presence_interval_seconds()) * 1000,
                 presence_watch)

    after_ms(max(1, online.presence_interval_seconds()) * 1000,
             presence_watch)

    def watchdog():
        if not root.winfo_exists():
            return
        if app.stop.is_set():
            try:
                if root.winfo_exists():
                    root.destroy()
            except tk.TclError:
                pass
            return
        after_ms(250, watchdog)

    def entitlement_watch():
        """Runtime re-check of the subscription (every 30 minutes).

        Start-up is strict (no live answer, no engine); while running,
        a lapsed or revoked subscription pauses assistance, and a pure
        network blip only logs - an accessibility tool must not yank
        the mouse away because of a router hiccup.
        """
        def worker():
            # v8.49: NO Tk call from this thread. `root.winfo_exists()` used
            # to be the first statement here, which evaluates Tcl off the
            # main thread - the one thing this file's own docstring and the
            # comment six lines below both forbid, and the only place in
            # gui.py that did it. It fires every 30 minutes per session and
            # fails at interpreter level, not with a traceback, most often
            # exactly while the window is being destroyed.
            #
            # The guard was also redundant: the main-thread callback below
            # already checks winfo_exists() before spawning this worker, and
            # every result is marshalled through root.after(0, ...), which
            # is a no-op once the interpreter is gone.
            try:
                ident, ent_now = online.me(cfg)
            except online.OnlineError:
                log(i18n.L("st.ent_unreachable"))
                return
            # v8.34: keep the status bar's registration line current - it
            # now carries the licence summary that used to sit in the
            # header. Marshalled onto the Tk main loop: Tk is not
            # thread-safe, and this runs in a worker thread. Skipped when
            # the identity came back None (session died server-side) -
            # the pause path below owns that case.
            if ident:
                try:
                    root.after(0, lambda i=ident, e=ent_now:
                               reg_var.set(registration_line(i, e)))
                except tk.TclError:
                    return
            active = bool(ident) and online.entitlement_active(ent_now)
            if active:
                return
            state = str((ent_now or {}).get("status", "inactive"))
            if app.running:
                post(11)
            # Same rule: never touch a Tk variable from this thread.
            try:
                root.after(0, lambda s=state: status_msg(
                    i18n.L("st.ent_paused", s)))
            except tk.TclError:
                return
            log("Entitlement re-check: %s - paused assistance." % state)
        if root.winfo_exists():
            threading.Thread(target=worker, daemon=True,
                             name="entitlement-watch").start()
            after_ms(check_ms(), entitlement_watch)

    # v8.27: the re-check cadence is a built-in constant - the
    # "Subscription re-check (minutes)" setting was removed.
    def check_ms():
        return ENTITLEMENT_CHECK_MINUTES * 60000

    after_ms(check_ms(), entitlement_watch)

    root.protocol("WM_DELETE_WINDOW",
                  lambda: (app.request_quit(), close_all("quit")))

    show_tab(tab_names[0])
    refresh_fields()
    poll_status()
    watchdog()
    log("GUI ready - signed in as %s."
        % online.identity_label(identity))
    root.mainloop()

    return action["now"]


def _gate_window(cfg, kit, identity, ent):
    """Subscription gate for a signed-in but unsubscribed identity.

    Shows the product logo on one clean themed card, the two
    payment buttons ("Monthly
    Subscription for 9.99 EUR" and "Trial Purchase for 1.99 EUR" -
    each checkout binds to the PAID e-mail, which must be this
    Discord e-mail). No manual re-check or activation buttons: the
    window re-checks the subscription by itself every 30 seconds
    (auto_loop), so a fresh purchase starts the engine without any
    click. Returns True once the
    worker reports an active entitlement; False when the window was
    closed. The engine is never started while this window exists.
    v8.47 dropped the blurred-logo backdrop: its red blotches showed
    through the window margins as dirty spots, so the gate is now a
    flat card like every other window, and refit() re-sizes the
    frame whenever the card's text changes.
    """
    pal = kit.pal
    result = {}
    gaids = []
    W, H = 620, 500

    root = tk.Tk()
    kit.attach(root)
    kit.reg(root, "card")
    root.title(i18n.L("gate.title", APP_NAME))
    root.configure(background=pal["card"])
    root.resizable(False, False)
    root.update_idletasks()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+%d+%d" % (W, H, max(0, (sw - W) // 2),
                                   max(0, (sh - H) // 3)))
    try:
        root.iconbitmap(logo.ico_path())
    except Exception:
        pass
    kit.defocus_hook(root)
    kit.titlebar_hook(root)

    # v8.47: ONE clean themed card, no backdrop image. The old
    # blurred-logo backdrop put saturated red blotches (the snake,
    # GaussianBlur 14) behind the centred card: whatever peeked out
    # at the window sides read as dirty spots and texture, and the
    # flat margins around it as dead areas. A flat card cannot go
    # stale on a theme switch and needs no re-render on a resize.
    box = tk.Frame(root, bg=pal["card"])
    kit.reg(box, "card")
    box.place(relx=0.5, rely=0.5, anchor="center")

    def refit():
        """Re-size the window to the card it carries (v8.47).

        Translated text wraps differently in every locale and the
        language can be switched WHILE this window is open (the
        Language button lives on the card), so a fixed frame would
        clip a tall card at both ends. With no backdrop image left
        there is nothing to regenerate: one geometry call re-fits
        the window, width included, and re-centres it."""
        nonlocal W, H
        try:
            root.update_idletasks()
            sw = root.winfo_screenwidth()
            sh = root.winfo_screenheight()
            W = max(620, box.winfo_reqwidth() + 24)
            H = max(500, box.winfo_reqheight() + 16)
            root.geometry("%dx%d+%d+%d" % (W, H,
                                           max(0, (sw - W) // 2),
                                           max(0, (sh - H) // 3)))
        except Exception:
            pass

    # v8.28: the rejection page carries the same crisp logo as the
    # sign-in window, above the title. Composited onto the LIVE card
    # colour and recomposited on every theme switch - Tk on Windows
    # ignores PNG alpha, so a transparent paste would show a white
    # square around the snake on the dark theme.
    lg = tk.Label(box, bg=pal["card"])
    kit.reg(lg, "card")
    lim = logo.surface_image(tk, 96, _surf_of(lg, pal["card"]))
    lg.configure(image=lim, bg=_surf_of(lg, pal["card"]))
    lg._img = lim
    lg.pack(pady=(14, 0))

    def _relogo_gate():
        surf = _surf_of(lg, pal["card"])
        im2 = logo.surface_image(tk, 96, surf)
        lg.configure(image=im2, bg=surf)
        lg._img = im2
    kit.repaint(_relogo_gate)

    t = tk.Label(box, text=APP_NAME, font=F_H1, bg=pal["card"],
                 fg=pal["text"])
    kit.reg(t, "card_text")
    t.pack(pady=(2, 2))

    def head_for(ent_now):
        state = str((ent_now or {}).get("status", "unsubscribed"))
        if (ent_now or {}).get("shared"):
            return i18n.L("gate.head.shared")
        if state == "refunded":
            return i18n.L("gate.head.refunded")
        if state == "canceling":
            return i18n.L("gate.head.canceling",
                          time.strftime("%Y-%m-%d",
                                        time.gmtime(int(ent_now.get("until")
                                                        or 0))))
        if state == "email_mismatch":
            return i18n.L("gate.head.email_mismatch")
        if state == "expired":
            return i18n.L("gate.head.expired")
        if state == "past_due":
            return i18n.L("gate.head.past_due")
        if state == "canceled":
            return i18n.L("gate.head.canceled")
        return i18n.L("gate.head.none")

    h1 = tk.Label(box, text=head_for(ent), font=F_BOLD, bg=pal["card"],
                  fg=pal["text"], wraplength=460, justify="center")
    kit.reg(h1, "card_bold")
    h1.pack(pady=(6, 2))
    h2 = tk.Label(box, text=i18n.L("gate.prices"),
                  font=F_DESC, bg=pal["card"], fg=pal["muted"],
                  wraplength=460, justify="center")
    kit.reg(h2, "card_muted")
    h2.pack(pady=(0, 10))

    who = tk.Label(box, text=online.identity_label(identity),
                   font=F_DESC, bg=pal["card"], fg=pal["muted"])
    kit.reg(who, "card_muted")
    who.pack(pady=(0, 4))
    sum_lbl = tk.Label(box, text=online.entitlement_summary(ent),
                       font=F_DESC, bg=pal["card"], fg=pal["amber"],
                       wraplength=460, justify="center")
    kit.reg(sum_lbl, "card_muted")
    sum_lbl.pack(pady=(0, 10))

    msg = tk.StringVar(value="")
    msg_lbl = tk.Label(box, textvariable=msg, font=F_DESC,
                       bg=pal["card"], fg=pal["accent"], wraplength=460,
                       justify="center")
    msg_kind = ["err"]

    def _remsg():
        msg_lbl.configure(fg=(pal["green"] if msg_kind[0] == "ok"
                              else pal["accent"]))
    kit.repaint(_remsg)

    def set_msg(text, ok=False):
        msg_kind[0] = "ok" if ok else "err"
        msg_lbl.configure(fg=(pal["green"] if ok else pal["accent"]))
        msg.set(text)

    def do_subscribe(kind="monthly"):
        url = online.subscribe_url(cfg, identity, kind)
        if not url:
            set_msg(i18n.L("gate.msg.no_link"))
            return
        if online.open_subscribe(cfg, identity, kind):
            set_msg(i18n.L("gate.msg.open_ok"))
        else:
            set_msg(i18n.L("gate.msg.open_fail", url))

    def do_recheck(_event=None, silent=True):
        """Silent entitlement re-check. The gate has no buttons any
        more - auto_loop drives this every 30 seconds, so a finished
        payment starts the engine without a click (_event may still be
        a Tk event object)."""
        def worker():
            try:
                # the silent 30 s auto re-check shares the CDN bucket
                # with everyone else
                ident, ent_now = online.me(cfg, fresh=False)
                err = None
            except online.OnlineError as exc:
                ident, ent_now, err = None, None, str(exc)
            root.after(0, lambda: checked(ident, ent_now, err))

        threading.Thread(target=worker, daemon=True,
                         name="entitlement-recheck").start()

    def checked(ident, ent_now, err):
        if err:
            set_msg(i18n.L("gate.msg.unreachable", err))
            return
        if ident is None:
            set_msg(i18n.L("gate.msg.session_gone"))
            root.after(600, root.destroy)
            return
        ent_cur[0] = ent_now
        h1.configure(text=head_for(ent_now))
        sum_lbl.configure(text=online.entitlement_summary(ent_now))
        # `shared` is part of the gate, exactly as it is in run_gui
        # and both console paths. Testing only
        # entitlement_active() here let an ACTIVE-BUT-SHARED account
        # through on the 30 s auto re-check - the window said
        # "Subscription active - starting Snappy AI..." while its own
        # header said "in use on ANOTHER computer right now".
        if online.entitlement_active(ent_now) and not ent_now.get("shared"):
            result["ok"] = True
            set_msg(i18n.L("gate.msg.active"), ok=True)
            for aid in gaids:
                try:
                    root.after_cancel(aid)
                except (tk.TclError, ValueError):
                    pass
            root.after(350, root.destroy)
        elif ent_now.get("shared"):
            set_msg(i18n.L("gate.msg.still_shared"))
        else:
            set_msg(i18n.L("gate.msg.still_none"))

    msg_lbl.pack(pady=(0, 10))
    ent_cur = [ent]

    def _gate_retext():
        if not _live(box):
            return False
        h1.configure(text=head_for(ent_cur[0]))
        h2.configure(text=i18n.L("gate.prices"))
        note.configure(text=i18n.L("gate.note"))
        kit.set_text(sub_btn, i18n.L("gate.btn.monthly"))
        kit.set_text(tri_btn, i18n.L("gate.btn.trial"))
        kit.set_text(_g_lang, i18n.L(
            "btn.language", i18n.native_name(i18n.current())))
        refit()          # v8.47: new text, new card size, new frame
        return True

    pay_btns = []
    sub_btn = kit.button(box, i18n.L("gate.btn.monthly"),
                         lambda: do_subscribe("monthly"),
                         kind="accent", big=True)
    sub_btn.pack(pady=(0, 6))
    pay_btns.append(sub_btn)
    # The trial is part of the offer, so its button is ALWAYS shown -
    # an unset stripe_trial_link explains itself on click instead of
    # silently hiding the cheaper entry point.
    tri_btn = kit.button(box, i18n.L("gate.btn.trial"),
                         lambda: do_subscribe("trial"),
                         kind="green", big=True)
    tri_btn.pack(pady=(0, 6))
    pay_btns.append(tri_btn)
    # The manual "Re-check now" and "I paid - activate now" buttons
    # are gone: auto_loop below re-checks the entitlement silently
    # every 30 seconds, so a finished payment starts the engine
    # without any click.

    _g_lang = kit.button(box, i18n.L(
        "btn.language", i18n.native_name(i18n.current())),
        lambda: _language_window(cfg, kit, root))
    _g_lang.pack(pady=(0, 6))
    root.update_idletasks()
    bw = max([b.winfo_width() for b in pay_btns] + [300])
    for b in pay_btns:
        meta = getattr(b, "_rmeta", None)
        if meta and HAVE_PIL and bw > 10:
            text, big, surface, _w, h, role = meta
            bg, _fg = kit._btn_colors(role)
            try:
                img = kit.rounded(bw, h, bg, 7)
                b.configure(image=img)
                b._img = img
            except Exception:
                pass

    note = tk.Label(box, text=i18n.L("gate.note"),
                    font=F_DESC, bg=pal["card"], fg=pal["muted"],
                    wraplength=460, justify="center")
    kit.reg(note, "card_muted")
    note.pack(pady=(4, 14))

    # v8.26: the offer is two payment buttons. The box is centred, so
    # an over-tall box spills out of a fixed-height window at BOTH ends
    # (clipped title, clipped note) - size the window to the content
    # instead.  v8.47: refit() does it, width included, and runs again
    # on every re-text.
    refit()

    R(_gate_retext)

    def auto_loop():
        if result.get("ok") or not root.winfo_exists():
            return
        do_recheck(silent=True)
        # bounded, like the main window's aids: the gate can stay open for
        # hours, and one id per 30 s is the same slow leak.
        gaids.append(root.after(30000, auto_loop))
        if len(gaids) > 32:
            del gaids[:len(gaids) - 32]

    gaids.append(root.after(30000, auto_loop))
    root.bind("<Return>", do_recheck)
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
    return bool(result.get("ok"))


def run_gui(cfg):
    """Sign-in -> subscription gate -> main window, in a loop.

    Strict online policy (v8.22): nothing starts without a live,
    positive answer from the auth worker. Unreachable server at start
    = retry dialog, then exit; never a half-started engine.
    """
    # v8.39: the saved language is live from the first window on, and
    # the coverage figures in the chooser need the complete key list.
    i18n.register_keys(sorted(set(i18n.STRINGS["en"])
                              | {label_key(k) for k in META}
                              | {desc_key(k) for k in META}
                              | {val_key(k, v) for k in META
                                 if META[k][2] == "map"
                                 for _d, v in META[k][3]}))
    # v8.49: report catalog drift BEFORE choosing a language, because the
    # 100% rule can silently hide every translation (see i18n.diagnose).
    for code, cov, missing in i18n.diagnose():
        log("i18n: %s is %.1f%% translated and therefore NOT offered - "
            "missing %d key(s): %s%s"
            % (code, cov * 100.0, len(missing), ", ".join(missing[:8]),
               " ..." if len(missing) > 8 else ""))
    stale = i18n.english_only_keys()
    if stale:
        log("i18n: %d English key(s) no other locale carries (%s%s) - if a "
            "widget was redesigned, delete them from PROSE, or they will "
            "keep every language below the 100%% bar."
            % (len(stale), ", ".join(stale[:6]),
               " ..." if len(stale) > 6 else ""))
    i18n.set_language(str(cfg.get("language", "en") or "en"))
    kit = ThemeKit(cfg)
    force_login = False

    def server_error(exc):
        """Retry dialog for the strict start-up policy."""
        try:
            r = tk.Tk()
            r.withdraw()
            again = messagebox.askretrycancel(
                APP_NAME,
                i18n.L("err.auth_unreachable", exc))
            r.destroy()
            return bool(again)
        except Exception:
            return False

    while True:
        identity = None
        ent = None
        sess = online.load_session()

        if not force_login and sess and sess.get("provider"):
            try:
                identity, ent = online.me(cfg, fresh=True)
            except online.OnlineError as exc:
                log("Auth server unreachable at start: %s" % exc)
                if not server_error(exc):
                    return 1
                continue
            if identity is None:
                online.clear_session()      # token died server-side

        if identity is None:
            identity = _login_window(cfg, kit)
            if identity is None:
                return 0
            # verify straight after sign-in: an account that already
            # has an entitlement must go directly to the main window
            try:
                identity, ent = online.me(cfg, fresh=True)
            except online.OnlineError as exc:
                log("Entitlement check after sign-in failed: %s" % exc)
                if not server_error(exc):
                    return 1
                continue
            if identity is None:
                continue            # session vanished: sign in again
        force_login = False

        # Shareware gate, server-side: the engine, its hooks and its
        # hotkeys start only for identities with an active entitlement
        # (Stripe webhook driven). No key boxes, no offline path.
        if not online.entitlement_active(ent) or ent.get("shared"):
            if not _gate_window(cfg, kit, identity, ent):
                force_login = True          # closed the gate: sign in again
                continue

        app, hook_thread = start_app(cfg, identity)
        if app is None:
            try:
                r = tk.Tk()
                r.withdraw()
                messagebox.showerror(APP_NAME,
                                     i18n.L("err.start_fail"))
                r.destroy()
            except Exception:
                pass
            return 1

        action = _run_main(cfg, identity, app, hook_thread, kit, ent)

        if not app.stop.is_set():
            app.request_quit()
        try:
            hook_thread.join(timeout=2.0)
        except Exception:
            pass

        if action == "logout":
            online.clear_session()
            force_login = True              # Log Out overrides the session
            log("Signed out.")
            continue
        return 0