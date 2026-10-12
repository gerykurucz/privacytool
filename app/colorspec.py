"""Colour specs: the one vocabulary for "which colour does the user mean".

Shared leaf module, no dependencies beyond the standard library.

WHY IT IS SEPARATE
------------------
`config.py` needs to answer one question - "does this accent spec name a
real colour?" - so that accent_only / auto_click can warn when they are
switched on with nothing to aim at. That question used to be answered by
importing `vision`, which pulled numpy and the whole analysis engine into
the settings layer: config.py stopped being pure-Python and independently
testable, and `hotkeys.py`'s "cross-platform and unit-testable" claim was
the only one left standing.

So the parsing vocabulary lives here. `vision.py` imports it and keeps its
historical private aliases (`_parse_accent`, `_parse_accents`) so every
existing call site, and every saved config file, keeps working unchanged.

Accepted forms, for accent_color and exclude_color alike:
    "off" / "none" / "disabled" / "false" / ""   -> no colour
    "blue"                                        -> a preset name
    "60,120,220"                                  -> r,g,b 0-255
    "blue; red; 60,120,220"                       -> several, ";"-separated
    [60, 120, 220]                                -> one JSON triple
    [[60, 120, 220], "red"]                       -> several, JSON list
"""

ACCENT_PRESETS = {
    "red":    (0.0, 210.0, 190.0),
    "orange": (15.0, 215.0, 215.0),
    "yellow": (30.0, 215.0, 215.0),
    "green":  (60.0, 210.0, 180.0),
    "cyan":   (90.0, 210.0, 200.0),
    "blue":   (120.0, 215.0, 200.0),
    "purple": (145.0, 190.0, 180.0),
    "pink":   (168.0, 150.0, 215.0),
    "lime":   (45.0, 190.0, 200.0),
    "teal":   (85.0, 220.0, 175.0),
    "indigo": (130.0, 210.0, 175.0),
    "brown":  (12.0, 165.0, 140.0),
    "grey":   (0.0, 0.0, 150.0),
    "gray":   (0.0, 0.0, 150.0),
    "white":  (0.0, 0.0, 235.0),
    "black":  (0.0, 0.0, 30.0),
}


def parse_accent(spec):
    if spec is None:
        return None

    # Handle numpy arrays and other sequence types
    if hasattr(spec, '__iter__') and not isinstance(spec, (str, bytes)):
        try:
            spec = list(spec)
        except (TypeError, ValueError):
            return None

    if isinstance(spec, str):
        preset = ACCENT_PRESETS.get(spec.strip().lower())
        if preset is not None:
            return preset
        # Parse "r,g,b" format
        try:
            parts = [int(p.strip()) for p in spec.split(",")]
        except (ValueError, OverflowError):
            return None
    elif isinstance(spec, (list, tuple)):
        try:
            if any(isinstance(p, bool) for p in spec):
                return None
            def _to_int(p):
                if isinstance(p, int):
                    return p
                if isinstance(p, float):
                    return int(p) if p.is_integer() else None
                if isinstance(p, str):
                    f = float(p)
                    return int(f) if f.is_integer() else None
                return None
            parts = [_to_int(p) for p in spec]
            if any(p is None for p in parts):
                return None
        except (TypeError, ValueError, OverflowError):
            return None
    else:
        return None
    if len(parts) != 3:
        return None
    for p in parts:
        if p < 0 or p > 255:
            return None
    r, g, b = parts
    rf, gf, bf = r / 255.0, g / 255.0, b / 255.0

    mx = max(rf, gf, bf)
    mn = min(rf, gf, bf)
    d = mx - mn
    v = mx
    s = 0.0 if mx == 0 else d / mx

    if d == 0:
        h = 0.0
    elif mx == rf:
        h = ((gf - bf) / d) % 6.0
    elif mx == gf:
        h = ((bf - rf) / d + 2.0) % 6.0
    else:
        h = ((rf - gf) / d + 4.0) % 6.0

    return (min(h * 30.0, 179.0), s * 255.0, v * 255.0)


def parse_accents(spec):
    if spec is None:
        return []

    items = spec

    # Handle numpy arrays and other sequence types (but not strings)
    if hasattr(items, '__iter__') and not isinstance(items, (str, bytes)):
        try:
            items = list(items)
        except (TypeError, ValueError):
            return []

    if isinstance(items, str):
        s = items.strip()
        if not s or s.lower() in ("off", "none", "disabled", "false"):
            return []
        items = [t.strip() for t in s.split(";") if t.strip()]

    if not isinstance(items, (list, tuple)):
        items = [items]

    if (len(items) == 3 and not isinstance(items, str)
            and all(isinstance(p, (int, float, str)) and not isinstance(p, bool)
                    for p in items)):
        items = [items]

    out = []
    for item in items:
        if isinstance(item, str):
            preset = ACCENT_PRESETS.get(item.strip().lower())
            if preset is not None:
                out.append(preset)
                continue

        hsv = parse_accent(item)
        if hsv is not None:
            out.append(hsv)

    return out


def hsv_to_rgb(h, s, v):
    h = max(0.0, min(359.999, float(h) * 2.0))
    s = max(0.0, min(1.0, float(s) / 255.0))
    v = max(0.0, min(1.0, float(v) / 255.0))
    c = v * s
    x = c * (1.0 - abs((h / 60.0) % 2.0 - 1.0))
    m = v - c
    if h < 60:
        r, g, b = c, x, 0.0
    elif h < 120:
        r, g, b = x, c, 0.0
    elif h < 180:
        r, g, b = 0.0, c, x
    elif h < 240:
        r, g, b = 0.0, x, c
    elif h < 300:
        r, g, b = x, 0.0, c
    else:
        r, g, b = c, 0.0, x
    return (max(0, min(255, int(round((r + m) * 255.0)))),
            max(0, min(255, int(round((g + m) * 255.0)))),
            max(0, min(255, int(round((b + m) * 255.0)))))


def _parse_accent(spec):
    return parse_accent(spec)


def _parse_accents(spec):
    return parse_accents(spec)


_ACCENT_PRESETS = ACCENT_PRESETS
