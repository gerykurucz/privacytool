with open('colorspec.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Rewrite parse_accents properly
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

    return out

'''

# Find and replace the function
for i in range(109, 160):
    if 'def parse_accents(spec):' in lines[i]:
        # Find end of function
        j = i + 1
        while j < len(lines) and (lines[j].startswith(' ') or lines[j].startswith('\t') or lines[j].strip() == ''):
            j += 1
        lines[i:j] = new_func.splitlines(keepends=True)
        print(f'Rewrote parse_accents at line {i+1}')
        break

with open('colorspec.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')