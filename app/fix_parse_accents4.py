with open('colorspec.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the entire function with a proper one
old_func = '''def parse_accents(spec):
    if spec is None:
        return []

    # Handle numpy arrays and other sequence types
    if hasattr(spec, '__iter__') and not isinstance(spec, (str, bytes)):
        try:
            items = list(spec)
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

    return out'''

new_func = '''def parse_accents(spec):
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

    return out'''

if old_func in content:
    content = content.replace(old_func, new_func)
    with open('colorspec.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed parse_accents')
else:
    print('Old function not found')