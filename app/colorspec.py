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

def parse_accent(spec):
    """
    Parse an accent colour spec into an OpenCV-style HSV centre.

    Accepts "off"/None (returns None), an "r,g,b" string (config files),
    or an [r, g, b] list (JSON config). Returns (h 0-179, s 0-255,
    v 0-255) or None.
    """
    if spec is None:
        return None

    if isinstance(spec, (list, tuple)):
        try:
            parts = [int(p) for p in spec]
        except (TypeError, ValueError):
            return None
    else:
        s = str(spec).strip().lower()
        if not s or s in ("off", "none", "disabled", "false"):
            return None
        try:
            parts = [int(p.strip()) for p in s.split(",")]
        except ValueError:
            return None

    if len(parts) != 3:
        return None

    r, g, b = (min(255, max(0, p)) for p in parts)
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
        h = (bf - rf) / d + 2.0
    else:
        h = (rf - gf) / d + 4.0

    return (h * 30.0, s * 255.0, v * 255.0)


# Named colour families, in OpenCV-style HSV (h 0-179, s/v 0-255), so
# "accent_color = blue" works without knowing any numbers. Grey/white/
# black sit at zero saturation and match desaturated pixels of that
# brightness. For unusual shades, give an explicit "r,g,b" instead.
ACCENT_PRESETS = {
    "red":    (0.0, 210.0, 190.0),
    "orange": (15.0, 215.0, 215.0),
    "yellow": (30.0, 215.0, 215.0),
    "green":  (60.0, 210.0, 180.0),
    "cyan":   (90.0, 210.0, 200.0),
    "blue":   (120.0, 215.0, 200.0),
    "purple": (145.0, 190.0, 180.0),
    "pink":   (168.0, 150.0, 215.0),
    # v8.49: the four material tones the GUI's preset grid offers. They
    # were clickable swatches that stored "r,g,b" (so they worked), but a
    # hand-written `accent_color = teal` silently parsed to nothing -
    # every name the interface shows must be a name the engine knows.
    "lime":   (45.0, 190.0, 200.0),
    "teal":   (85.0, 220.0, 175.0),
    "indigo": (130.0, 210.0, 175.0),
    "brown":  (12.0, 165.0, 140.0),
    "grey":   (0.0, 0.0, 150.0),
    "gray":   (0.0, 0.0, 150.0),
    "white":  (0.0, 0.0, 235.0),
    "black":  (0.0, 0.0, 30.0),
}


def parse_accents(spec):
    """
    Parse an accent spec into a list of HSV centres (possibly empty).

    Accepts everything parse_accent does, plus several colours in one
    spec, separated by ";": "blue; red", "60,120,220; 200,60,60", or a
    JSON list like [[60, 120, 220], "red"]. Preset names are matched
    case-insensitively.
    """
    if spec is None:
        return []

    items = spec
    if isinstance(items, str):
        s = items.strip()
        if not s or s.lower() in ("off", "none", "disabled", "false"):
            return []
        items = [t.strip() for t in s.split(";") if t.strip()]

    if not isinstance(items, (list, tuple)):
        items = [items]

    # v8.49: a BARE [r, g, b] triple. config.py has always accepted and
    # stored that form from a hand-edited config.json ("accent_color also
    # accepts [r, g, b]"), but a list is otherwise read as SEVERAL colour
    # specs - so the three ints were each parsed on their own, each failed
    # the "exactly three numbers" test, and the user's colour silently
    # became "off" with no warning anywhere. Disambiguate: a list of three
    # numbers is one colour; anything else is a list of colours.
    if (len(items) == 3 and not isinstance(items, str)
            and all(isinstance(p, (int, float)) and not isinstance(p, bool)
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
    """OpenCV-style HSV (h 0-180, s/v 0-255) -> RGB 0-255 tuple."""
    h = (float(h) * 2.0) % 360.0
    s = float(s) / 255.0
    v = float(v) / 255.0
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
    return (int(round((r + m) * 255.0)),
            int(round((g + m) * 255.0)),
            int(round((b + m) * 255.0)))
