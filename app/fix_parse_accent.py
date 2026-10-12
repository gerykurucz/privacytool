with open('colorspec.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix parse_accent - add string parsing for "60,120,220" format
# Replace lines 59-85 with proper logic
new_block = [
    '    if isinstance(spec, str):\n',
    '        preset = ACCENT_PRESETS.get(spec.strip().lower())\n',
    '        if preset is not None:\n',
    '            return preset\n',
    '        # Parse "r,g,b" format\n',
    '        try:\n',
    '            parts = [int(p.strip()) for p in spec.split(",")]\n',
    '        except (ValueError, OverflowError):\n',
    '            return None\n',
    '    elif isinstance(spec, (list, tuple)):\n',
    '        try:\n',
    '            if any(isinstance(p, bool) for p in spec):\n',
    '                return None\n',
    '            def _to_int(p):\n',
    '                if isinstance(p, int):\n',
    '                    return p\n',
    '                if isinstance(p, float):\n',
    '                    return int(p) if p.is_integer() else None\n',
    '                if isinstance(p, str):\n',
    '                    f = float(p)\n',
    '                    return int(f) if f.is_integer() else None\n',
    '                return None\n',
    '            parts = [_to_int(p) for p in spec]\n',
    '            if any(p is None for p in parts):\n',
    '                return None\n',
    '        except (TypeError, ValueError, OverflowError):\n',
    '            return None\n',
    '    else:\n',
    '        return None\n',
    '    if len(parts) != 3:\n',
    '        return None\n',
]

lines[58:84] = new_block

with open('colorspec.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed parse_accent')