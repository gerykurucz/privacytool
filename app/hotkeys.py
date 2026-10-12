
import re

from core import log







HOTKEY_MODS = {"ctrl": 0x0002, "alt": 0x0001, "shift": 0x0004, "win": 0x0008}
HOTKEY_NOREPEAT = 0x4000

_NAMED_KEYS = {
    "space": 0x20, "enter": 0x0D, "return": 0x0D, "esc": 0x1B,
    "escape": 0x1B, "tab": 0x09, "backspace": 0x08, "insert": 0x2D,
    "delete": 0x2E, "home": 0x24, "end": 0x23, "pgup": 0x21, "pgdn": 0x22,
    "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27,
    "comma": 0xBC, "period": 0xBE, "minus": 0xBD, "plus": 0xBB,
}


def _key_to_vk(key):
    if len(key) == 1:
        c = key.upper()
        if "A" <= c <= "Z" or "0" <= c <= "9":
            return ord(c)
        return {" ": 0x20, ",": 0xBC, ".": 0xBE, "-": 0xBD, "+": 0xBB}.get(key)

    if key in _NAMED_KEYS:
        return _NAMED_KEYS[key]

    if key.startswith("f") and key[1:].isdigit():
        n = int(key[1:])
        if 1 <= n <= 24:
            return 0x70 + n - 1

    return None


_MOD_HEAD = re.compile(r"^(ctrl|alt|shift|win)\+(.*)$",
                       re.IGNORECASE | re.DOTALL)


def _parse_hotkey(spec):
    """"ctrl+alt+r" -> (mods, vk). The key is whatever follows the last
    modifier, so "+" itself stays bindable ("ctrl++", "shift+-")."""
    if spec is None:
        return None
    raw = re.sub(r"\s*\+\s*", "+", str(spec).strip())
    if not raw:
        return None
    mods = HOTKEY_NOREPEAT
    seen_mods = set()
    while True:
        head = _MOD_HEAD.match(raw)
        if head is None:
            break
        name = head.group(1).lower()
        if name in seen_mods:
            return None
        seen_mods.add(name)
        mods |= HOTKEY_MODS[name]
        raw = head.group(2)
    key = raw.strip().lower()
    if not key:
        return None
    vk = _key_to_vk(key)
    if vk is None:
        return None
    return mods, vk


MOD_VKS = {"ctrl": (0x11,), "alt": (0x12,), "shift": (0x10,),
           "win": (0x5B, 0x5C)}
MOD_ORDER = ("ctrl", "alt", "shift", "win")


def parse_bypass_spec(spec):
    """A HELD-input spec -> (mods, vk); vk is None for modifiers only.

    A hotkey is a press, so its grammar needs a non-modifier key at the end
    ("shift" alone is not a shortcut). The bypass is a hold, and "while Shift
    is down" is exactly what people expect from it, so this also accepts what
    _parse_hotkey rejects: one modifier on its own, or several together. A
    normal combination goes through the shared parser, so "ctrl+alt+x" means
    the same thing here as it does everywhere else.

    None means "reject": an empty spec, an unknown name, or a repeated
    modifier. Callers keep the previous value and say so.
    """
    parsed = _parse_hotkey(spec)
    if parsed is not None:
        return parsed[0] & ~HOTKEY_NOREPEAT, parsed[1]
    raw = re.sub(r"\s*\+\s*", "+", str(spec or "").strip().lower())
    if not raw:
        return None
    mods = 0
    for part in raw.split("+"):
        bit = HOTKEY_MODS.get(part)
        if bit is None or mods & bit:
            return None
        mods |= bit
    return (mods, None) if mods else None


def describe_bypass_spec(spec):
    """The canonical spelling of a bypass spec, or "" when it is invalid.

    Modifiers first, in a fixed order, so "SHIFT + ctrl" and "ctrl+shift"
    store and display identically - the same rule format_buttons applies to
    controller combinations.
    """
    parsed = parse_bypass_spec(spec)
    if parsed is None:
        return ""
    mods, vk = parsed
    head = [name for name in MOD_ORDER if mods & HOTKEY_MODS[name]]
    if vk is None:
        return "+".join(head)
    # The key keeps its own spelling, so "+" stays bindable ("ctrl++"): strip
    # the modifier heads the same way the parser does and keep the remainder.
    raw = re.sub(r"\s*\+\s*", "+", str(spec).strip().lower())
    while True:
        match = _MOD_HEAD.match(raw)
        if match is None:
            break
        raw = match.group(2)
    return "+".join(head + [raw.strip()])


def bypass_mod_vks(mods):
    """The virtual-key codes a modifier mask stands for, one tuple per mod.

    GetAsyncKeyState on a generic VK (VK_SHIFT) reports either side down, and
    Win has no generic VK at all, so left and right are both listed.
    """
    out = []
    for name in MOD_ORDER:
        if mods & HOTKEY_MODS[name]:
            out.append(MOD_VKS[name])
    return out


def effective_mode_key(cfg, which):
    raw = cfg.get("key_mode%d" % which, str(which))
    if raw is None or str(raw).strip() == "":
        return str(which) + " (fires everywhere, key still types)"
    specs = [p.strip().lower() for p in str(raw).split(",") if p.strip()]
    if not specs:
        return str(which) + " (fires everywhere, key still types)"
    last = specs[-1]
    if "+" not in last:
        if _parse_hotkey(last) is None:
            return last + " (not a valid shortcut)"
        return last + " (fires everywhere, key still types)"
    return last + " (blocks typing while bound)"


MACRO_SLOTS = 5




REC_PLAY_SLOTS = 5


def build_hotkey_table(cfg):
    specs = {
        10: cfg.get("key_launch", "ctrl+l"),
        11: cfg.get("key_pause", "ctrl+p"),
        30: cfg.get("key_record", "ctrl+alt+r"),
        37: cfg.get("key_record_stop", "ctrl+alt+s"),
        31: cfg.get("key_play", "ctrl+alt+m"),
    }





    for i in range(1, REC_PLAY_SLOTS + 1):
        specs[31 + i] = cfg.get("key_play%d" % i, "ctrl+%d" % i)

    always = []
    local = []





    _specs = {}

    for key_id, spec in specs.items():
        if spec is None or str(spec).strip() == "":
            continue
        parsed = _parse_hotkey(spec)
        if parsed is None:
            log("Key binding %r is invalid; that action has no hotkey."
                % (spec,))
            continue
        mods, vk = parsed
        _specs[key_id] = spec
        if bool(mods & 0x000F):
            always.append((key_id, mods, vk))
        else:
            local.append((key_id, vk))


    for which, ids in MODE_KEY_IDS.items():
        raw = str(cfg.get("key_mode%d" % which, str(which)))
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        if len(parts) > MAX_KEYS_PER_MODE:
            log("key_mode%d: more than %d keys given; extra ones ignored."
                % (which, MAX_KEYS_PER_MODE))
            parts = parts[:MAX_KEYS_PER_MODE]
        for spec, key_id in zip(parts, ids):
            parsed = _parse_hotkey(spec)
            if parsed is None:
                log("Mode key %r is invalid; skipped." % (spec,))
                continue
            mods, vk = parsed
            _specs[key_id] = spec
            if bool(mods & 0x000F):
                always.append((key_id, mods, vk))
            else:
                local.append((key_id, vk))




    seen_always = {}
    for key_id, mods, vk in always:
        k = (mods & 0x000F, vk)
        if k in seen_always:
            log("Key binding %r is assigned to two actions (ids %d and %d); "
                "only the first can register."
                % (_specs.get(key_id, "?"), seen_always[k], key_id))
        else:
            seen_always[k] = key_id
    seen_local = {}
    for key_id, vk in local:
        if vk in seen_local:
            log("Key binding %r is assigned to two actions (ids %d and %d); "
                "the last one wins."
                % (_specs.get(key_id, "?"), seen_local[vk], key_id))
        else:
            seen_local[vk] = key_id

    return always, local













def build_macro_table(cfg):
    macros = []
    seen = {}

    for i in range(1, MACRO_SLOTS + 1):
        tspec = str(cfg.get("macro%d_key" % i, "") or "").strip()
        aspec = str(cfg.get("macro%d_action" % i, "") or "").strip()
        if not tspec or not aspec:
            continue

        trig = _parse_hotkey(tspec)
        act = _parse_hotkey(aspec)
        if trig is None:
            log("Macro %d: macro key %r is invalid; macro skipped."
                % (i, tspec))
            continue
        if act is None:
            log("Macro %d: action %r is invalid; macro skipped."
                % (i, aspec))
            continue

        key = (trig[0] & 0x000F, trig[1])
        if key in seen:
            log("Macro %d: macro key %r is already used by macro %d; "
                "skipped." % (i, tspec, seen[key]))
            continue
        seen[key] = i

        macros.append((trig[0], trig[1], act[0], act[1]))

    macro_map = {(m[0] & 0x000F, m[1]): m for m in macros}
    return macros, macro_map


ACTION_IDS = {
    10: "launch",
    11: "pause",


    6: "reload",
    20: "mode1",
    22: "mode1",
    23: "mode1",
    24: "mode1",
    21: "mode2",
    25: "mode2",
    26: "mode2",
    27: "mode2",
    30: "record_macro",
    37: "stop_macro",
    31: "play_macro",
    32: "play_macro1",
    33: "play_macro2",
    34: "play_macro3",
    35: "play_macro4",
    36: "play_macro5",
}

CONTROL_ACTION_NAMES = ("record_macro", "stop_macro", "play_macro",
                        "play_macro1", "play_macro2", "play_macro3",
                        "play_macro4", "play_macro5")

MODE_KEY_IDS = {1: (20, 22, 23, 24), 2: (21, 25, 26, 27)}
MAX_KEYS_PER_MODE = 4

