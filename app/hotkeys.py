"""Bindable hotkeys: spec parsing ("ctrl+alt+s", "f5", ...) and the
action-id table. Cross-platform and unit-testable."""

from core import log

# ----------------------------------------------------------------------
#
# Key bindings are user-configurable strings like "ctrl+alt+s", "f5" or
# "1". Modifier values match the Win32 MOD_* constants, so the parser is
# usable (and testable) on any platform.

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
    """Virtual-key code for a key name, or None."""
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


def _parse_hotkey(spec):
    """Parse 'ctrl+alt+s' into (mods, vk), or None when invalid."""
    if spec is None:
        return None

    parts = [p.strip().lower() for p in str(spec).split("+")]

    # v8.49: an EMPTY part is a malformed spec, not something to filter out.
    # Filtering meant "ctrl++s" silently bound ctrl+s, "esc+" bound esc and
    # "++s" bound s - so a typo produced a working-but-wrong binding with no
    # warning, while a genuinely unknown key got one. Reject it and let
    # build_hotkey_table() report it like every other bad spec.
    if not parts or any(not p for p in parts):
        return None

    mods = HOTKEY_NOREPEAT
    for p in parts[:-1]:
        if p not in HOTKEY_MODS:
            return None
        mods |= HOTKEY_MODS[p]

    vk = _key_to_vk(parts[-1])
    if vk is None:
        return None

    return mods, vk


def effective_mode_key(cfg, which):
    """
    How the mode-switch key behaves, for humans.

    With block_bound_keys off (default), modifier-less specs like "1"
    work system-wide through a pass-through keyboard hook: the action
    fires in every app AND the key still reaches the focused app, so
    typing is never blocked.
    """
    spec = str(cfg.get("key_mode%d" % which, str(which))).strip().lower()
    if "+" not in spec and not bool(cfg.get("block_bound_keys", False)):
        return spec + " (fires everywhere, key still types)"
    return spec + " (blocks typing while bound)"


MACRO_SLOTS = 5

# Recording playback hotkeys (key_play1..5 -> ids 32..36). Since v8.27
# they play recordings BY LIST POSITION (Ctrl+1 = recording #1 in the
# Macros tab library); the old slot assignments are gone.
REC_PLAY_SLOTS = 5


def build_hotkey_table(cfg):
    """
    Build (always, local) from the config.

    always: (id, mods, vk) registered system-wide via RegisterHotKey.
            Specs that include a modifier are always safe to register
            (they never swallow bare typing).
    local:  (id, vk) modifier-less specs. With block_bound_keys off they
            are handled by the pass-through keyboard hook (fire action
            + never block the key); with block_bound_keys on they move
            into `always` (classic hotkeys that swallow the key).
    Invalid specs are reported and skipped.
    """
    specs = {
        10: cfg.get("key_launch", "ctrl+l"),
        11: cfg.get("key_pause", "ctrl+p"),
        30: cfg.get("key_record", "ctrl+alt+r"),
        37: cfg.get("key_record_stop", "ctrl+alt+s"),
        31: cfg.get("key_play", "ctrl+alt+m"),
    }
    # v8.27: the radius / feedback / reload / quit hotkeys are gone.
    # Id 6 ("reload") survives as an INTERNAL action - the GUI posts it
    # after Apply/Import/Restore-Defaults - but it is never registered
    # as a key binding anymore.
    # Play-slot hotkeys: 32..36 play recording slot 1..5.
    for i in range(1, REC_PLAY_SLOTS + 1):
        specs[31 + i] = cfg.get("key_play%d" % i, "ctrl+%d" % i)

    block = bool(cfg.get("block_bound_keys", False))
    always = []
    local = []
    # action id -> the binding text the user typed, so a collision can be
    # reported as "ctrl+s" instead of as a (mods, vk) tuple. Kept beside the
    # tables rather than inside them: assist.py unpacks (hid, mods, vk) and
    # (hid, vk), and widening those tuples would break every call site for
    # the sake of a log message.
    _specs = {}

    for hid, spec in specs.items():
        parsed = _parse_hotkey(spec)
        if parsed is None:
            log("Key binding %r is invalid; that action has no hotkey."
                % (spec,))
            continue
        mods, vk = parsed
        _specs[hid] = spec
        if block or bool(mods & 0x000F):   # 0x000F = ctrl|alt|shift|win
            always.append((hid, mods, vk))
        else:
            local.append((hid, vk))

    # Mode switches accept up to MAX_KEYS_PER_MODE comma-separated specs.
    for which, ids in MODE_KEY_IDS.items():
        raw = str(cfg.get("key_mode%d" % which, str(which)))
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        if len(parts) > MAX_KEYS_PER_MODE:
            log("key_mode%d: more than %d keys given; extra ones ignored."
                % (which, MAX_KEYS_PER_MODE))
            parts = parts[:MAX_KEYS_PER_MODE]
        for spec, hid in zip(parts, ids):
            parsed = _parse_hotkey(spec)
            if parsed is None:
                log("Mode key %r is invalid; skipped." % (spec,))
                continue
            mods, vk = parsed
            _specs[hid] = spec
            if block or bool(mods & 0x000F):
                always.append((hid, mods, vk))
            else:
                local.append((hid, vk))

    # Duplicates: one physical key can only carry one action. Without
    # this note the collision would be silent (last binding wins for
    # bare keys; RegisterHotKey fails for the second classic hotkey).
    seen_always = {}
    for hid, mods, vk in always:
        k = (mods & 0x000F, vk)
        if k in seen_always:
            # Log the SPEC the user typed, not a (mods, vk) tuple: "%r" of
            # (2, 83) tells nobody that they bound ctrl+s twice. _specs maps
            # an action id back to its binding text; the tuple shapes stay
            # exactly what assist.py unpacks.
            log("Key binding %r is assigned to two actions (ids %d and %d); "
                "only the first can register."
                % (_specs.get(hid, "?"), seen_always[k], hid))
        else:
            seen_always[k] = hid
    seen_local = {}
    for hid, vk in local:
        if vk in seen_local:
            log("Key binding %r is assigned to two actions (ids %d and %d); "
                "the last one wins."
                % (_specs.get(hid, "?"), seen_local[vk], hid))
        else:
            seen_local[vk] = hid

    return always, local



# ----------------------------------------------------------------------
#
# Macros: one physical key sends a whole combo - exactly ONCE per
# press (v8.27). Five slots, each two settings (macroN_key /
# macroN_action). The trigger is ALWAYS SWALLOWED while the app is
# launched - that is the semantics ("B means Ctrl+C") - so unlike the
# pass-through action binds, typing the trigger key never types it
# anywhere. Trigger and action both use the hotkey spec syntax, so an
# action can be any combo ("ctrl+c", "ctrl+shift+s", "space", "f5").

def build_macro_table(cfg):
    """
    Parse the five macro slots into
        (macros, macro_map)
    macros:   [(tmods, tvk, amods, avk)]
    macro_map: {(mods_without_norepeat, vk): macro_tuple} for the hook.

    Every macro is a blocked, single-shot replacement: the physical
    trigger press is swallowed and exactly one combo press is injected
    while Snappy AI is launched; paused, the keyboard is entirely the
    user's.

    A slot is off while its trigger or its action is empty. Invalid
    specs warn and skip, never fatal; duplicate triggers keep the first
    slot and warn.
    """
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
            log("Macro %d: trigger %r is invalid; macro skipped."
                % (i, tspec))
            continue
        if act is None:
            log("Macro %d: action %r is invalid; macro skipped."
                % (i, aspec))
            continue

        key = (trig[0] & 0x000F, trig[1])
        if key in seen:
            log("Macro %d: trigger %r is already used by macro %d; "
                "skipped." % (i, tspec, seen[key]))
            continue
        seen[key] = i

        macros.append((trig[0], trig[1], act[0], act[1]))

    macro_map = {(m[0] & 0x000F, m[1]): m for m in macros}
    return macros, macro_map


ACTION_IDS = {
    10: "launch",
    11: "pause",
    # 6 has no key binding since v8.27 (the reload hotkey was removed);
    # the GUI still posts it internally after saving settings.
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

MODE_KEY_IDS = {1: (20, 22, 23, 24), 2: (21, 25, 26, 27)}
MAX_KEYS_PER_MODE = 4

