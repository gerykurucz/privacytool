"""Native controller input: XInput, the button vocabulary, and the spec grammar.

WHY THIS MODULE EXISTS
----------------------
`assist.py` needs to answer three questions about a gamepad and nothing else:
what is the pad doing right now, which of those states is a *new* event, and
what does a user-written binding such as "rb+a" mean. All three live here so
the engine stays free of ctypes and so the grammar can be unit-tested on any
platform (no Windows, no pad, no driver).

XInput is read-only. It reports a pad; it cannot make one. Output therefore
lives in `input_backend.py` (ViGEmBus when the user has it, keyboard/mouse
emulation otherwise) exactly as every other delivery path in this project does.

Design rules (mirrors colorspec.py / input_backend.py):
- pure stdlib ctypes; imports cleanly on any OS, so the GUI can read
  available() to decorate its switch and the tests can run head-less;
- NEVER fatal: no DLL, no pad, a pad unplugged mid-session or a wedged driver
  all degrade to "not connected" plus at most one log line;
- no polling here. `read()` is one call; the caller owns the cadence.

BUTTON AND AXIS IDS
-------------------
`PAD_BUTTONS` and `PAD_AXES` are the stable numeric ids stored in recordings,
so they are append-only: never reorder them, never reuse an index, or every
saved macro library silently changes meaning.

SPEC GRAMMAR
------------
    ""                  -> nothing bound
    "a"                 -> one button
    "rb+a"              -> a combination (order is irrelevant)
    "lt"                -> an analogue trigger, pressed past its threshold
    "LS+RS"             -> case is irrelevant
Accepted names and aliases are in `ALIASES`.
"""

import ctypes
import math
import threading
import time

from core import IS_WINDOWS, log

XUSER_MAX_COUNT = 4

PAD_BUTTONS = ("up", "down", "left", "right", "start", "back", "ls", "rs",
               "lb", "rb", "a", "b", "x", "y", "lt", "rt")

PAD_AXES = ("lt", "rt", "lx", "ly", "rx", "ry")

TRIGGER_BUTTONS = frozenset((PAD_BUTTONS.index("lt"), PAD_BUTTONS.index("rt")))

_XINPUT_MASKS = {
    "up": 0x0001, "down": 0x0002, "left": 0x0004, "right": 0x0008,
    "start": 0x0010, "back": 0x0020, "ls": 0x0040, "rs": 0x0080,
    "lb": 0x0100, "rb": 0x0200, "a": 0x1000, "b": 0x2000,
    "x": 0x4000, "y": 0x8000,
}

ALIASES = {
    "dpad_up": "up", "dpad_down": "down", "dpad_left": "left",
    "dpad_right": "right",
    "l3": "ls", "r3": "rs", "left_thumb": "ls", "right_thumb": "rs",
    "left_stick": "ls", "right_stick": "rs",
    "l1": "lb", "r1": "rb", "left_shoulder": "lb", "right_shoulder": "rb",
    "bumper_l": "lb", "bumper_r": "rb",
    "select": "back", "view": "back", "menu": "start",
    "lt": "lt", "rt": "rt", "left_trigger": "lt", "right_trigger": "rt",
    "trigger_l": "lt", "trigger_r": "rt",
    "a": "a", "b": "b", "x": "x", "y": "y",
    "cross": "a", "circle": "b", "square": "x", "triangle": "y",
}

DEADZONE_LEFT = 7849
DEADZONE_RIGHT = 8689
DEADZONE_TRIGGER = 30

AXIS_FULL = 32767
TRIGGER_FULL = 255

PAD_EMU_DEFAULT = ("a=enter;b=esc;x=space;y=tab;up=up;down=down;left=left;"
                   "right=right;lb=mouse4;rb=mouse5;ls=mouse1;rs=mouse2;"
                   "lt=mouse2;rt=mouse1;start=off;back=off")

DEFAULT_TRIGGER_THRESHOLD = 128
DEFAULT_POLL_HZ = 125

ERROR_SUCCESS = 0
ERROR_DEVICE_NOT_CONNECTED = 1167
ERROR_EMPTY = 4306

_DLL_NAMES = ("xinput1_4.dll", "xinput1_3.dll", "xinput9_1_0.dll")

_dll = None
_dll_tried = False
_dll_lock = threading.Lock()


class _Gamepad(ctypes.Structure):
    _fields_ = [("wButtons", ctypes.c_ushort),
                ("bLeftTrigger", ctypes.c_ubyte),
                ("bRightTrigger", ctypes.c_ubyte),
                ("sThumbLX", ctypes.c_short),
                ("sThumbLY", ctypes.c_short),
                ("sThumbRX", ctypes.c_short),
                ("sThumbRY", ctypes.c_short)]


class _State(ctypes.Structure):
    _fields_ = [("dwPacketNumber", ctypes.c_ulong),
                ("Gamepad", _Gamepad)]


class _Capabilities(ctypes.Structure):
    _fields_ = [("Type", ctypes.c_ubyte),
                ("SubType", ctypes.c_ubyte),
                ("Flags", ctypes.c_ushort),
                ("Gamepad", _Gamepad),
                ("Vibration", ctypes.c_ushort * 2)]


class _Vibration(ctypes.Structure):
    _fields_ = [("wLeftMotorSpeed", ctypes.c_ushort),
                ("wRightMotorSpeed", ctypes.c_ushort)]


def _load_dll():
    """Load the first XInput that this Windows has. Cached; never raises."""
    global _dll, _dll_tried
    with _dll_lock:
        if _dll_tried:
            return _dll
        _dll_tried = True
        if not IS_WINDOWS:
            return None
        for name in _DLL_NAMES:
            try:
                dll = ctypes.windll.LoadLibrary(name)
            except Exception:
                continue
            try:
                dll.XInputGetState.restype = ctypes.c_ulong
                dll.XInputGetState.argtypes = [ctypes.c_ulong,
                                               ctypes.POINTER(_State)]
                dll.XInputSetState.restype = ctypes.c_ulong
                dll.XInputSetState.argtypes = [ctypes.c_ulong,
                                               ctypes.POINTER(_Vibration)]
                if hasattr(dll, "XInputGetCapabilities"):
                    dll.XInputGetCapabilities.restype = ctypes.c_ulong
                    dll.XInputGetCapabilities.argtypes = [
                        ctypes.c_ulong, ctypes.c_ulong,
                        ctypes.POINTER(_Capabilities)]
            except Exception:
                continue
            _dll = dll
            return _dll
        log("Controller: none of %s could be loaded, so no controller can be "
            "read on this machine. XInput 1.4 ships with Windows 8 and later; "
            "on Windows 7 install the DirectX end-user runtime. The rest of "
            "Snappy AI is unaffected." % ", ".join(_DLL_NAMES))
        return None


def available():
    """True when an XInput runtime could be loaded (a pad may still be absent).

    Safe on every platform; the GUI reads it to word the switch, and it is the
    reason enabling the switch on a machine with no XInput says so once
    instead of failing silently.
    """
    return _load_dll() is not None


class PadState(object):
    """One normalised sample of a pad.

    `buttons` is a bitmask over PAD_BUTTONS indices (triggers included, so a
    binding never has to know that lt/rt are analogue); `raw` keeps the
    un-thresholded trigger bytes for recording.
    """

    __slots__ = ("connected", "packet", "buttons", "lt", "rt",
                 "lx", "ly", "rx", "ry", "when")

    def __init__(self, connected=False, packet=0, buttons=0, lt=0, rt=0,
                 lx=0, ly=0, rx=0, ry=0, when=0.0):
        self.connected = connected
        self.packet = packet
        self.buttons = buttons
        self.lt = lt
        self.rt = rt
        self.lx = lx
        self.ly = ly
        self.rx = rx
        self.ry = ry
        self.when = when

    def down(self, index):
        return bool(self.buttons & (1 << index))

    def axis(self, index):
        name = PAD_AXES[index]
        return getattr(self, name)

    def as_dict(self):
        return {"buttons": self.buttons, "lt": self.lt, "rt": self.rt,
                "lx": self.lx, "ly": self.ly, "rx": self.rx, "ry": self.ry}

    def __repr__(self):
        return ("<PadState connected=%s packet=%d buttons=%s lt=%d rt=%d "
                "l=(%d,%d) r=(%d,%d)>"
                % (self.connected, self.packet, format_buttons(self.buttons),
                   self.lt, self.rt, self.lx, self.ly, self.rx, self.ry))


EMPTY_STATE = PadState()


def _threshold_triggers(lt, rt, threshold):
    mask = 0
    if lt >= threshold:
        mask |= 1 << PAD_BUTTONS.index("lt")
    if rt >= threshold:
        mask |= 1 << PAD_BUTTONS.index("rt")
    return mask


def read(index=0, trigger_threshold=DEFAULT_TRIGGER_THRESHOLD, reader=None):
    """One sample from pad `index`. Never raises; answers EMPTY_STATE on any
    failure so the caller can treat "no pad" and "pad glitch" identically.

    `reader` is injectable: the tests drive the whole engine from synthetic
    frames, and no other seam in this project needs a physical device.
    """
    if reader is not None:
        try:
            state = reader(index)
        except Exception as exc:
            log("Controller: the injected reader failed (%r)." % (exc,))
            return EMPTY_STATE
        if state is None:
            return EMPTY_STATE
        if not isinstance(state, PadState):
            return EMPTY_STATE
        state.buttons = (state.buttons & ~(
            (1 << PAD_BUTTONS.index("lt")) | (1 << PAD_BUTTONS.index("rt")))) \
            | _threshold_triggers(state.lt, state.rt, trigger_threshold)
        return state
    dll = _load_dll()
    if dll is None:
        return EMPTY_STATE
    if not 0 <= int(index) < XUSER_MAX_COUNT:
        return EMPTY_STATE
    raw = _State()
    try:
        result = dll.XInputGetState(ctypes.c_ulong(int(index)),
                                    ctypes.byref(raw))
    except (OSError, ValueError, ctypes.ArgumentError) as exc:
        log("Controller: XInputGetState failed (%r)." % (exc,))
        return EMPTY_STATE
    if result == ERROR_DEVICE_NOT_CONNECTED or result == ERROR_EMPTY:
        return EMPTY_STATE
    if result != ERROR_SUCCESS:
        return EMPTY_STATE
    pad = raw.Gamepad
    buttons = int(pad.wButtons) & 0xF3FF
    lt = int(pad.bLeftTrigger)
    rt = int(pad.bRightTrigger)
    return PadState(connected=True, packet=int(raw.dwPacketNumber),
                    buttons=buttons | _threshold_triggers(lt, rt,
                                                          trigger_threshold),
                    lt=lt, rt=rt,
                    lx=int(pad.sThumbLX), ly=int(pad.sThumbLY),
                    rx=int(pad.sThumbRX), ry=int(pad.sThumbRY),
                    when=time.perf_counter())


def capabilities(index=0):
    """(type, subtype, flags) for a connected pad, or None."""
    dll = _load_dll()
    if dll is None or not hasattr(dll, "XInputGetCapabilities"):
        return None
    caps = _Capabilities()
    try:
        result = dll.XInputGetCapabilities(ctypes.c_ulong(int(index)),
                                           ctypes.c_ulong(0),
                                           ctypes.byref(caps))
    except (OSError, ValueError, ctypes.ArgumentError):
        return None
    if result != ERROR_SUCCESS:
        return None
    return int(caps.Type), int(caps.SubType), int(caps.Flags)


def set_rumble(index, left=0.0, right=0.0, seconds=0.0):
    """Spin the motors (0.0-1.0 each). Fire-and-forget, never raises.

    Used for the two moments a pad user cannot see: recording started and
    recording saved. Rumble is scheduled by XInput itself, so `seconds` only
    bounds how long we keep the motors on.
    """
    dll = _load_dll()
    if dll is None or seconds <= 0:
        return False
    vib = _Vibration()
    vib.wLeftMotorSpeed = int(max(0.0, min(1.0, float(left))) * 65535)
    vib.wRightMotorSpeed = int(max(0.0, min(1.0, float(right))) * 65535)
    try:
        if dll.XInputSetState(ctypes.c_ulong(int(index)), ctypes.byref(vib)):
            return False
        time.sleep(max(0.0, float(seconds)))
        vib.wLeftMotorSpeed = 0
        vib.wRightMotorSpeed = 0
        dll.XInputSetState(ctypes.c_ulong(int(index)), ctypes.byref(vib))
        return True
    except (OSError, ValueError, ctypes.ArgumentError):
        return False


def apply_deadzone(x, y, deadzone, scale=1.0):
    """Radial deadzone, the one Xbox documentation recommends.

    Per-axis deadzones make a stick drift diagonally; a radial one does not.
    Returns (fx, fy) in -1.0..1.0, already scaled, so a caller can turn them
    straight into a cursor delta.
    """
    try:
        x = float(x)
        y = float(y)
        dz = max(0.0, min(float(deadzone), AXIS_FULL - 1.0))
    except (TypeError, ValueError):
        return 0.0, 0.0
    mag = math.hypot(x, y)
    if mag <= dz or mag <= 0.0:
        return 0.0, 0.0
    normalised = (mag - dz) / (AXIS_FULL - dz)
    k = min(1.0, normalised) / mag * float(scale)
    return x * k, y * k


def trigger_value(raw, threshold=DEADZONE_TRIGGER):
    """Analogue trigger byte -> 0.0..1.0, with the documented deadzone."""
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return 0.0
    if v <= threshold:
        return 0.0
    return min(1.0, (v - threshold) / float(TRIGGER_FULL - threshold))


def normalise_axis(index, value):
    """Clamp a recorded axis value to the range its axis really has."""
    name = PAD_AXES[index]
    try:
        v = int(value)
    except (TypeError, ValueError):
        return 0
    if name in ("lt", "rt"):
        return max(0, min(TRIGGER_FULL, v))
    return max(-AXIS_FULL - 1, min(AXIS_FULL, v))


def parse_token(token):
    """One button name -> its PAD_BUTTONS index, or None."""
    name = str(token or "").strip().lower()
    if not name:
        return None
    name = ALIASES.get(name, name)
    if name in PAD_BUTTONS:
        return PAD_BUTTONS.index(name)
    return None


def parse_spec(spec):
    """A binding spec -> a frozenset of button indices, or None if invalid.

    None means "reject this binding" (the caller logs and keeps the previous
    value); an EMPTY spec is also None, because an unbound slot must never
    match a pad that is doing nothing.
    """
    if spec is None:
        return None
    raw = str(spec).strip()
    if not raw:
        return None
    indices = set()
    for token in raw.split("+"):
        index = parse_token(token)
        if index is None:
            return None
        if index in indices:
            return None
        indices.add(index)
    if not indices:
        return None
    return frozenset(indices)


def spec_mask(spec):
    """A binding spec -> the bitmask its buttons set, or 0 when invalid."""
    indices = parse_spec(spec)
    if not indices:
        return 0
    mask = 0
    for index in indices:
        mask |= 1 << index
    return mask


def format_buttons(buttons):
    """A bitmask -> the canonical spec text ("rb+a"). Sorted by PAD_BUTTONS
    order so the same combination always renders the same way."""
    if not buttons:
        return ""
    names = [PAD_BUTTONS[i] for i in range(len(PAD_BUTTONS))
             if buttons & (1 << i)]
    return "+".join(names)


def describe_spec(spec):
    """Human text for the GUI: the canonical spelling, or why it was rejected."""
    indices = parse_spec(spec)
    if indices is None:
        return ""
    mask = 0
    for index in indices:
        mask |= 1 << index
    return format_buttons(mask)


def valid_names():
    """Every accepted spelling, for the GUI's hint line and the console help."""
    return sorted(set(list(PAD_BUTTONS) + list(ALIASES)))


class PadTracker(object):
    """Turns a stream of samples into one event per press.

    A combination fires only while EVERY button of it is down, and only once
    per press - holding never auto-repeats. That is the keyboard's rule
    (HOTKEY_NOREPEAT), and it is what makes a held trigger safe to steer with:
    the drive path needs the press and the release, not a burst of actions.
    """

    def __init__(self, indices):
        self.indices = frozenset(indices or ())
        self._mask = 0
        for index in self.indices:
            self._mask |= 1 << index
        self.reset()

    def reset(self):
        self.down = False

    def matches(self, buttons):
        return bool(self._mask) and (buttons & self._mask) == self._mask

    def update(self, buttons, now=None):
        """Advance one sample. Returns "press" for a new press, else None."""
        if not self.matches(buttons):
            self.down = False
            return None
        if self.down:
            return None
        self.down = True
        return "press"


def shadowed_indices(bindings, buttons):
    """Indices of bindings that a LONGER matching binding swallows this sample.

    With "a" bound to launch and "rb+a" bound to record, pressing rb+a must
    record and must not also launch. A binding is shadowed while another
    binding that is down right now contains all of its buttons plus more.

    The shadowed tracker is still advanced (so its own down/fired state stays
    honest) - only its EVENT is dropped. Dropping the update as well would
    make the shorter binding fire late: hold rb, press a, release rb and the
    lone "a" would suddenly launch.
    """
    matching = [b for b in bindings if b.indices and b.tracker.matches(buttons)]
    out = set()
    for short in matching:
        for long in matching:
            if long is short:
                continue
            if short.indices < long.indices:
                out.add(id(short))
                break
    return out


class PadBinding(object):
    """A resolved binding: what to press, and what to do about it."""

    __slots__ = ("key", "spec", "indices", "tracker", "action")

    def __init__(self, key, spec, action):
        self.key = key
        self.spec = spec
        self.indices = parse_spec(spec)
        self.action = action
        self.tracker = PadTracker(self.indices or ())

    @property
    def valid(self):
        return self.indices is not None


def build_bindings(table):
    """{config key: (spec, action)} -> [PadBinding], duplicates reported.

    A spec claimed by two keys is kept by the FIRST, in the order the caller
    declared them, and the second is logged - the same policy
    `hotkeys.build_hotkey_table` uses for keyboard bindings.
    """
    out = []
    seen = {}
    for key in table:
        spec, action = table[key]
        indices = parse_spec(spec)
        if indices is None:
            if str(spec or "").strip():
                log("Controller binding %r is invalid (%r); that action has "
                    "no controller button." % (key, spec))
            continue
        if indices in seen:
            log("Controller binding %r is assigned to two actions (%s and "
                "%s); only the first can fire."
                % (format_buttons(_mask_of(indices)), seen[indices], key))
            continue
        seen[indices] = key
        out.append(PadBinding(key, spec, action))
    return out


def _mask_of(indices):
    mask = 0
    for index in indices:
        mask |= 1 << index
    return mask


MACRO_SLOTS = 5

ACTION_KEYS = (
    ("pad_launch", "launch"),
    ("pad_pause", "pause"),
    ("pad_mode1", "mode1"),
    ("pad_mode2", "mode2"),
    ("pad_record", "record_macro"),
    ("pad_record_stop", "stop_macro"),
    ("pad_play", "play_macro"),
    ("pad_play1", "play_macro1"),
    ("pad_play2", "play_macro2"),
    ("pad_play3", "play_macro3"),
    ("pad_play4", "play_macro4"),
    ("pad_play5", "play_macro5"),
)


def action_ids():
    """Action name -> the hotkey id that already implements it.

    Reusing hotkeys.ACTION_IDS means a controller binding and a keyboard
    binding run the SAME code path in assist.handle_hotkey, which is what
    makes the two feature sets 1:1 instead of two parallel implementations.
    """
    import hotkeys
    out = {}
    for hid, name in hotkeys.ACTION_IDS.items():
        out.setdefault(name, hid)
    return out


def build_action_bindings(cfg):
    """{config key -> PadBinding} for the twelve action slots."""
    ids = action_ids()
    table = {}
    for key, name in ACTION_KEYS:
        if name not in ids:
            continue
        table[key] = (str(cfg.get(key, "") or ""), ids[name])
    return build_bindings(table)


def parse_macro_action(spec):
    """A macro's output: ("key", mods, vk) or ("pad", mask), or None.

    A keyboard/mouse combo works everywhere. A "pad:a+b" combo needs the
    ViGEmBus virtual pad - there is no other way to make a controller press
    appear - so the caller checks the active output backend before firing one
    and says so once instead of silently doing nothing.
    """
    raw = str(spec or "").strip()
    if not raw:
        return None
    if raw.lower().startswith("pad:"):
        mask = spec_mask(raw[4:])
        if not mask:
            return None
        return ("pad", mask)
    import hotkeys
    parsed = hotkeys._parse_hotkey(raw)
    if parsed is None:
        return None
    return ("key", parsed[0] & 0x000F, parsed[1])


def build_macro_table(cfg):
    """Pad macros, mirroring hotkeys.build_macro_table slot for slot.

    Returns [(slot, spec, indices, action)]. A trigger claimed by an earlier
    slot is logged and skipped, exactly as the keyboard macros do.
    """
    macros = []
    seen = {}
    for slot in range(1, MACRO_SLOTS + 1):
        tspec = str(cfg.get("pad_macro%d_key" % slot, "") or "").strip()
        aspec = str(cfg.get("pad_macro%d_action" % slot, "") or "").strip()
        if not tspec or not aspec:
            continue
        indices = parse_spec(tspec)
        if indices is None:
            log("Pad macro %d: trigger %r is not a controller button or "
                "combination; macro skipped." % (slot, tspec))
            continue
        action = parse_macro_action(aspec)
        if action is None:
            log("Pad macro %d: action %r is neither a key combo (ctrl+c) nor "
                "a controller combo (pad:a+b); macro skipped." % (slot, aspec))
            continue
        if indices in seen:
            log("Pad macro %d: trigger %r is already used by pad macro %d; "
                "skipped." % (slot, tspec, seen[indices]))
            continue
        seen[indices] = slot
        macros.append((slot, tspec, indices, action))
    return macros


def first_connected(index=0, reader=None, count=XUSER_MAX_COUNT):
    """The index of the first pad that answers, or None.

    `pad_index = -1` (the default) means "whoever is plugged in", which is
    what an accessibility tool wants: the user has one pad and does not care
    which slot Windows gave it.
    """
    if reader is None and not available():
        return None
    if index is not None and int(index) >= 0:
        state = read(int(index), reader=reader)
        return int(index) if state.connected else None
    for candidate in range(max(1, int(count))):
        if read(candidate, reader=reader).connected:
            return candidate
    return None


def describe(index=None, reader=None):
    """One-paragraph status for the console `gamepad` command and the log."""
    if reader is None and not available():
        return ("Controller: no XInput runtime on this machine, so controller "
                "support is unavailable.")
    lines = ["Controller: XInput present."]
    found = 0
    for candidate in range(XUSER_MAX_COUNT):
        state = read(candidate, reader=reader)
        if not state.connected:
            continue
        found += 1
        caps = capabilities(candidate) if reader is None else None
        kind = ""
        if caps:
            kind = " (type %d, subtype %d)" % (caps[0], caps[1])
        lines.append("  pad %d: connected%s, packet %d, buttons %s, "
                     "lt=%d rt=%d, L=(%d,%d) R=(%d,%d)"
                     % (candidate, kind, state.packet,
                        format_buttons(state.buttons) or "none",
                        state.lt, state.rt, state.lx, state.ly,
                        state.rx, state.ry))
    if not found:
        lines.append("  no pad is connected right now.")
    return "\n".join(lines)
