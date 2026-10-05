"""Saved macro recordings: storage, validation, export/import.

Recordings live in macros.json next to the configuration: variable-
length user data does not belong in config.json.
A recording is a NAME plus a list of tagged steps - the delay is
always the LAST field of a step and is the gap BEFORE it, so playback
reproduces the rhythm of the original recording - plus its own
playback style ("loop": play once vs repeat until stopped).

v8.46 step format: a recording captures EVERYTHING the user did, so
a step is one of
    (STEP_KEY,    mods, vk, delay)             a key press
    (STEP_MOVE,   x, y, delay)                 a cursor move
    (STEP_BUTTON, btn, phase, x, y, delay)     a mouse button down/up
Old v8.27 files carry bare (mods, vk, delay) keyboard steps; they
load fine and are normalized to the tagged form.

v8.27: the old slot assignments are gone. The library is simply a
numbered list (1. icon clicks, 2. icon selects, ...) and the
Ctrl+1..Ctrl+5 hotkeys replay recordings BY LIST POSITION. Old
macros.json files load fine: their "slot" fields are ignored and a
missing "loop" flag defaults to play-once.

v8.46: the library cap is 5 - exactly the recordings Ctrl+1..5 can
launch by list position - and MAX_STEPS grew because cursor trails
cost steps too (moves merge while they keep coming, see assist.py).

This is an offline, local convenience store - a corrupt or hand-edited
file warns and degrades to an empty library, never crashes.
"""

import json
import os
import time

from config import config_dir
from core import log

import i18n

i18n.publish("en", {
    "rec.no_sel": "Nothing selected to export.",
    "rec.exported": "Exported to %s",
    "rec.export_fail": "Export failed: %r",
    "rec.import_fail": "Import failed: %r",
    "rec.notfile": "Import failed: not a recording file.",
    "rec.imported": "Imported %d recording(s)%s.",
    "rec.imported_none": " (none were valid)",
})

REC_FILE = "macros.json"

# v8.46 tagged step format (see the module docstring).
STEP_KEY = 0
STEP_MOVE = 1
STEP_BUTTON = 2
BTN_LEFT, BTN_RIGHT, BTN_MIDDLE = 0, 1, 2
PHASE_DOWN, PHASE_UP = 0, 1

MAX_STEPS = 2000         # per recording (longer recordings truncate)
MAX_RECORDINGS = 5       # library cap: Ctrl+1..5 play positions 1..5
MAX_DELAY_MS = 5000      # per-step gap clamp
MAX_NAME_LEN = 60
MAX_COORD = 65536        # sane bound for virtual-screen coordinates


def validate_steps(raw):
    """
    Coerce a json step list into tagged tuples, or None.

    Accepted shapes (v8.46):
        3 items  (mods, vk, delay)             legacy keyboard step
        4 items  (STEP_KEY, mods, vk, delay)
        4 items  (STEP_MOVE, x, y, delay)
        6 items  (STEP_BUTTON, btn, phase, x, y, delay)
    Modifier masks must stay within ctrl/alt/shift/win, buttons and
    phases must be known, coordinates must be plausible; delays clamp
    instead of failing. Anything else -> None (caller warns).
    Legacy 3-item steps normalize to the tagged form, so the rest of
    the product only ever sees tagged steps.
    """
    if not isinstance(raw, (list, tuple)) or not raw:
        return None
    if len(raw) > MAX_STEPS:
        return None
    out = []
    for step in raw:
        if not isinstance(step, (list, tuple)):
            return None
        try:
            vals = [int(v) for v in step]
        except (TypeError, ValueError):
            return None
        n = len(vals)
        if n == 3:                          # legacy keyboard step
            tag, mods, vk, delay = STEP_KEY, vals[0], vals[1], vals[2]
        elif n == 4:
            tag = vals[0]
            if tag == STEP_KEY:
                mods, vk, delay = vals[1], vals[2], vals[3]
            elif tag == STEP_MOVE:
                x, y, delay = vals[1], vals[2], vals[3]
                if not -MAX_COORD <= x <= MAX_COORD \
                        or not -MAX_COORD <= y <= MAX_COORD:
                    return None
                out.append((STEP_MOVE, x, y,
                            max(0, min(MAX_DELAY_MS, delay))))
                continue
            else:
                return None
        elif n == 6 and vals[0] == STEP_BUTTON:
            btn, phase, x, y, delay = vals[1], vals[2], vals[3], \
                vals[4], vals[5]
            if btn not in (BTN_LEFT, BTN_RIGHT, BTN_MIDDLE):
                return None
            if phase not in (PHASE_DOWN, PHASE_UP):
                return None
            if not -MAX_COORD <= x <= MAX_COORD \
                    or not -MAX_COORD <= y <= MAX_COORD:
                return None
            out.append((STEP_BUTTON, btn, phase, x, y,
                        max(0, min(MAX_DELAY_MS, delay))))
            continue
        else:
            return None
        # the keyboard path (legacy or tagged)
        if not 0 <= mods <= 0x000F or not 1 <= vk <= 254:
            return None
        out.append((STEP_KEY, mods, vk, max(0, min(MAX_DELAY_MS, delay))))
    return out


def _as_bool(value, default=False):
    """Bool from json/ini values that may arrive as strings."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    if value is None:
        return default
    return bool(value)


def _clean_rec(data, fallback_name):
    """Validate one recording dict; returns a clean copy or None.

    Legacy "slot" fields (pre-v8.27) are dropped silently; the list
    position is the only "number" a recording has now.
    """
    if not isinstance(data, dict):
        return None
    steps = validate_steps(data.get("steps"))
    if not steps:
        return None
    name = str(data.get("name") or fallback_name).strip()[:MAX_NAME_LEN] \
        or fallback_name
    loop = _as_bool(data.get("loop"), False)
    try:
        created = int(data.get("created", 0))
    except (TypeError, ValueError):
        created = 0
    return {"name": name, "steps": steps, "loop": loop,
            "created": created, "id": None}


class RecordingStore(object):
    """The macro recording library (macros.json)."""

    def __init__(self, path=None):
        self.path = path or os.path.join(config_dir(), REC_FILE)
        self.recordings = []
        self.revision = 0          # GUI pollers watch this
        self._next_id = 1
        self._load()

    # ---------------- storage ----------------
    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            return
        items = data.get("recordings") if isinstance(data, dict) else None
        if not isinstance(items, list):
            if data:
                log("macros.json: unreadable library - starting empty.")
            return
        for i, item in enumerate(items):
            if len(self.recordings) >= MAX_RECORDINGS:
                # v8.46: the library is five recordings - exactly what
                # Ctrl+1..5 can launch. A hand-edited/legacy file with
                # more keeps its first five.
                log("macros.json: library cap is %d - ignored %d extra "
                    "recording(s)." % (MAX_RECORDINGS, len(items) - i))
                break
            rec = _clean_rec(item, "Recording %d" % (i + 1))
            if rec is None:
                log("macros.json: ignored an invalid recording entry.")
                continue
            self._add_clean(rec)

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as fh:
                json.dump({"recordings": [
                    {"id": r["id"], "name": r["name"], "loop": r["loop"],
                     "created": r["created"],
                     "steps": [list(s) for s in r["steps"]]}
                    for r in self.recordings]}, fh, indent=2)
            self.revision += 1
            return True
        except OSError as exc:
            log("macros.json: could not save (%r)" % (exc,))
            return False

    # ---------------- library ----------------
    def _add_clean(self, rec):
        rec["id"] = self._next_id
        self._next_id += 1
        self.recordings.append(rec)
        return rec

    def add(self, name, steps):
        if len(self.recordings) >= MAX_RECORDINGS:
            log("Recording library full (%d) - remove one first."
                % MAX_RECORDINGS)
            return None
        rec = _clean_rec({"name": name, "steps": steps, "loop": False,
                          "created": int(time.time())}, name)
        if rec is None:
            return None
        self._add_clean(rec)
        self.revision += 1
        return rec

    def get(self, rid):
        for rec in self.recordings:
            if rec["id"] == rid:
                return rec
        return None

    def remove(self, rid):
        rec = self.get(rid)
        if rec is None:
            return False
        self.recordings.remove(rec)
        self.revision += 1
        return True

    def set_name(self, rid, name):
        """Rename a recording (1..MAX_NAME_LEN chars after strip)."""
        rec = self.get(rid)
        if rec is None:
            return False
        name = str(name or "").strip()[:MAX_NAME_LEN]
        if not name:
            return False
        rec["name"] = name
        self.revision += 1
        return True

    def set_loop(self, rid, loop):
        """Per-recording playback style: False = play once,
        True = repeat until stopped."""
        rec = self.get(rid)
        if rec is None:
            return False
        rec["loop"] = bool(loop)
        self.revision += 1
        return True

    def by_position(self, position):
        """The recording at 1-based list position n (Ctrl+n hotkeys),
        or None when the library is shorter than that."""
        try:
            n = int(position)
        except (TypeError, ValueError):
            return None
        if 1 <= n <= len(self.recordings):
            return self.recordings[n - 1]
        return None

    def most_recent(self):
        if not self.recordings:
            return None
        return max(self.recordings,
                   key=lambda r: (r["created"], r["id"]))

    # ---------------- share ----------------
    def export_to(self, path, rid=None):
        """One recording (rid) or the whole library as a bundle.

        v8.46: format marker 2 - the steps are tagged (keys, cursor
        moves, mouse buttons). Marker 1 files (keyboard-only steps)
        still IMPORT fine; they simply predate mouse capture."""
        if rid is not None:
            rec = self.get(rid)
            if rec is None:
                return False, i18n.L("rec.no_sel")
            payload = {"snappyai_recording": 2, "name": rec["name"],
                       "loop": rec["loop"],
                       "steps": [list(s) for s in rec["steps"]]}
        else:
            payload = {"snappyai_recordings": 2, "recordings": [
                {"name": r["name"], "loop": r["loop"],
                 "steps": [list(s) for s in r["steps"]]}
                for r in self.recordings]}
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2)
            return True, i18n.L("rec.exported", path)
        except OSError as exc:
            return False, i18n.L("rec.export_fail", exc)

    def import_from(self, path):
        """Accept a single-recording file or a bundle; validate all."""
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError) as exc:
            return False, i18n.L("rec.import_fail", exc)

        items = []
        if isinstance(data, dict):
            if isinstance(data.get("recordings"), list):
                items = data["recordings"]
            elif "steps" in data:
                items = [data]
        if not items:
            return False, i18n.L("rec.notfile")

        added = 0
        for i, item in enumerate(items):
            rec = _clean_rec(item, "Imported %d" % (i + 1))
            if rec is None:
                continue
            rec["created"] = int(time.time())
            if len(self.recordings) >= MAX_RECORDINGS:
                log("Import stopped at %d recordings (library full)."
                    % MAX_RECORDINGS)
                break
            # unique-ish name
            names = set(r["name"] for r in self.recordings)
            base, n = rec["name"], 2
            while rec["name"] in names:
                rec["name"] = "%s (%d)" % (base, n)
                n += 1
            self._add_clean(rec)
            added += 1

        if added:
            self.save()
        return added > 0, i18n.L(
            "rec.imported", added,
            "" if added else i18n.L("rec.imported_none"))
