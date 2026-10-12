with open('colorspec.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the entire parse_accent function with a clean version
old_parse_accent = '''def parse_accent(spec):
    if spec is None:
        return None
    if isinstance(spec, str):
        preset = ACCENT_PRESETS.get(spec.strip().lower())
        if preset is not None:
            return preset
    if isinstance(spec, (list, tuple)):
        try:
            if any(isinstance(p, bool) for p in spec):
                return None
        try:
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
        except (TypeError, ValueError, OverflowError):
            return None
            if any(p is None for p in parts):
                return None
        except (TypeError, ValueError, OverflowError):
            return None
    if len(parts) != 3:
        return None'''

new_parse_accent = '''def parse_accent(spec):
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

    if isinstance(spec, (list, tuple)):
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

        if len(parts) != 3:
            return None'''

content = content.replace(old_parse_accent, new_parse_accent)

with open('colorspec.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed parse_accent')