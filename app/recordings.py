
import json
import os
import time

import gamepad
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
PAD_REC_FILE = "pad_macros.json"


STEP_KEY = 0
STEP_MOVE = 1
STEP_BUTTON = 2
STEP_PAD_BUTTON = 3
STEP_PAD_AXIS = 4
BTN_LEFT, BTN_RIGHT, BTN_MIDDLE = 0, 1, 2
BTN_X1, BTN_X2 = 3, 4
BTN_ALL = (BTN_LEFT, BTN_RIGHT, BTN_MIDDLE, BTN_X1, BTN_X2)
PHASE_DOWN, PHASE_UP = 0, 1

MAX_STEPS = 2000
MAX_RECORDINGS = 5
MAX_DELAY_MS = 5000
MAX_NAME_LEN = 60
MAX_COORD = 65536
FORMAT_VERSION = 3


def pad_axis_range(index):
    """(low, high) for a recorded controller axis, per gamepad.PAD_AXES."""
    name = gamepad.PAD_AXES[index]
    if name in ("lt", "rt"):
        return 0, gamepad.TRIGGER_FULL
    return -gamepad.AXIS_FULL - 1, gamepad.AXIS_FULL


def describe_step(step):
    """One step as a short human string, for the console and the log."""
    try:
        tag = step[0]
        if tag == STEP_KEY:
            return "key(%d,%d)+%dms" % (step[1], step[2], step[3])
        if tag == STEP_MOVE:
            return "move(%d,%d)+%dms" % (step[1], step[2], step[3])
        if tag == STEP_BUTTON:
            return "btn%d:%s+%dms" % (step[1], "up" if step[2] else "down", step[5])
        if tag == STEP_PAD_BUTTON:
            return "pad %s:%s+%dms" % (gamepad.PAD_BUTTONS[step[1]],
                                       "up" if step[2] else "down", step[3])
        if tag == STEP_PAD_AXIS:
            return "pad %s=%d+%dms" % (gamepad.PAD_AXES[step[1]], step[2], step[3])
        return "step%d" % tag
    except (IndexError, TypeError):
        return "?"


def validate_steps(raw):
    if not isinstance(raw, (list, tuple)) or not raw:
        return None
    if len(raw) > MAX_STEPS:
        raw = list(raw)[:MAX_STEPS]
    out = []
    for step in raw:
        if not isinstance(step, (list, tuple)):
            return None
        try:
            vals = []
            for v in step:
                if isinstance(v, bool) or not isinstance(v, int):
                    return None
                vals.append(v)
        except (TypeError, ValueError):
            return None
        n = len(vals)
        if n == 3:
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
            elif tag == STEP_PAD_BUTTON:
                btn, phase, delay = vals[1], vals[2], vals[3]
                if not 0 <= btn < len(gamepad.PAD_BUTTONS):
                    return None
                if phase not in (PHASE_DOWN, PHASE_UP):
                    return None
                out.append((STEP_PAD_BUTTON, btn, phase,
                            max(0, min(MAX_DELAY_MS, delay))))
                continue
            elif tag == STEP_PAD_AXIS:
                axis, value, delay = vals[1], vals[2], vals[3]
                if not 0 <= axis < len(gamepad.PAD_AXES):
                    return None
                low, high = pad_axis_range(axis)
                if not low <= value <= high:
                    return None
                out.append((STEP_PAD_AXIS, axis, value,
                            max(0, min(MAX_DELAY_MS, delay))))
                continue
            else:
                return None
        elif n == 6 and vals[0] == STEP_BUTTON:
            btn, phase, x, y, delay = vals[1], vals[2], vals[3], \
                vals[4], vals[5]
            if btn not in BTN_ALL:
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

        if not 0 <= mods <= 0x000F or not 1 <= vk <= 254:
            return None
        out.append((STEP_KEY, mods, vk, max(0, min(MAX_DELAY_MS, delay))))
    return out


def _as_bool(value, default=False):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    if value is None:
        return default
    return bool(value)


def _clean_rec(data, fallback_name):
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
    """The macro library. Every mutation persists: callers used to have to
    remember save() after remove/set_name/set_loop, and any caller that
    forgot lost the change at the next start-up."""

    def __init__(self, path=None):
        self.path = path or os.path.join(config_dir(), REC_FILE)
        self.recordings = []
        self.revision = 0
        self._next_id = 1
        self._load()


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
            folder = os.path.dirname(self.path)
            if folder:
                os.makedirs(folder, exist_ok=True)
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump({"recordings": [
                    {"id": r["id"], "name": r["name"], "loop": r["loop"],
                     "created": r["created"],
                     "steps": [list(s) for s in r["steps"]]}
                    for r in self.recordings]}, fh, indent=2)
            os.replace(tmp, self.path)
            self.revision += 1
            return True
        except (OSError, TypeError, ValueError) as exc:
            log("macros.json: could not save (%r)" % (exc,))
            return False


    def _add_clean(self, rec):
        rec["id"] = self._next_id
        self._next_id += 1
        self.recordings.append(rec)
        return rec

    def add(self, name, steps, loop=False):
        if len(self.recordings) >= MAX_RECORDINGS:
            log("Recording library full (%d) - remove one first."
                % MAX_RECORDINGS)
            return None
        clean_name = str(name or "").strip()[:MAX_NAME_LEN]
        if not clean_name:
            return None
        rec = _clean_rec({"name": clean_name, "steps": steps, "loop": loop,
                          "created": int(time.time())}, clean_name)
        if rec is None:
            return None
        self._add_clean(rec)
        if not self.save():
            self.recordings.remove(rec)
            return None
        return rec

    def get(self, rid):
        try:
            rid = int(rid)
        except (TypeError, ValueError):
            return None
        for rec in self.recordings:
            if rec["id"] == rid:
                return rec
        return None

    def remove(self, rid):
        rec = self.get(rid)
        if rec is None:
            return False
        self.recordings.remove(rec)
        if not self.save():
            self.recordings.append(rec)  # rollback
            return False
        return True

    def set_name(self, rid, name):
        rec = self.get(rid)
        if rec is None:
            return False
        name = str(name or "").strip()[:MAX_NAME_LEN]
        if not name:
            return False
        old_name = rec["name"]
        rec["name"] = name
        if not self.save():
            rec["name"] = old_name
            return False
        return True

    def set_loop(self, rid, loop):
        rec = self.get(rid)
        if rec is None:
            return False
        old_loop = rec["loop"]
        rec["loop"] = _as_bool(loop, False)
        if not self.save():
            rec["loop"] = old_loop
            return False
        return True

    def by_position(self, position):
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


    def export_to(self, path, rid=None):
        if rid is not None:
            rec = self.get(rid)
            if rec is None:
                return False, i18n.L("rec.no_sel")
            payload = {"snappyai_recording": FORMAT_VERSION,
                       "name": rec["name"],
                       "loop": rec["loop"],
                       "created": rec["created"],
                       "steps": [list(s) for s in rec["steps"]]}
        else:
            payload = {"snappyai_recordings": FORMAT_VERSION,
                       "recordings": [
                {"name": r["name"], "loop": r["loop"],
                 "created": r["created"],
                 "steps": [list(s) for s in r["steps"]]}
                for r in self.recordings]}
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        tmp = path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2)
            os.replace(tmp, path)
            return True, i18n.L("rec.exported", path)
        except (OSError, TypeError, ValueError) as exc:
            try:
                os.remove(tmp)
            except OSError:
                pass
            return False, i18n.L("rec.export_fail", exc)

    def import_from(self, path):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError) as exc:
            return False, i18n.L("rec.import_fail", exc)

        # Check format version
        version = data.get("snappyai_recording") or data.get("snappyai_recordings")
        if version is not None and version != FORMAT_VERSION:
            log("recordings: import format version %r != %d, ignoring" % (version, FORMAT_VERSION))
            return False, i18n.L("rec.bad_version", version, FORMAT_VERSION)

        items = []
        if isinstance(data, dict):
            if isinstance(data.get("recordings"), list):
                items = data["recordings"]
                if not items:
                    return True, i18n.L("rec.imported", 0, "")
            elif "steps" in data:
                items = [data]
        if not items:
            return False, i18n.L("rec.notfile")

        added = 0
        for i, item in enumerate(items):
            rec = _clean_rec(item, "Imported %d" % (i + 1))
            if rec is None:
                continue
            try:
                _orig_created = int(item.get("created", 0)) if isinstance(item, dict) else 0
            except (TypeError, ValueError):
                _orig_created = 0
            rec["created"] = _orig_created if _orig_created > 0 else int(time.time())
            if len(self.recordings) >= MAX_RECORDINGS:
                log("Import stopped at %d recordings (library full)."
                    % MAX_RECORDINGS)
                break
            names = set(r["name"] for r in self.recordings)
            base, n = rec["name"], 2
            while rec["name"] in names:
                suffix = " (%d)" % n
                rec["name"] = base[:max(0, MAX_NAME_LEN - len(suffix))] \
                    + suffix
                n += 1
            self._add_clean(rec)
            added += 1

        if added:
            if not self.save():
                return False, i18n.L("rec.import_fail", "could not save library")
        return added > 0, i18n.L(
            "rec.imported", added,
            "" if added else i18n.L("rec.imported_none"))
