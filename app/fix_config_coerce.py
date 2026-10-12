with open('config.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix _coerce_value signature and logic to reject lists for non-color keys
for i in range(628, 630):
    if 'def _coerce_value(raw, default):' in lines[i]:
        lines[i] = 'def _coerce_value(raw, default, key=None):\n'
        print(f'Fixed signature at line {i+1}')
        break

# Fix the list/tuple acceptance - only allow for accent_color and exclude_color
for i in range(660, 670):
    if 'if isinstance(raw, (list, tuple)):' in lines[i]:
        lines[i] = '        if isinstance(raw, (list, tuple)):\n'
        lines.insert(i+1, '            if key not in ("accent_color", "exclude_color"):\n')
        lines.insert(i+2, '                return False, None\n')
        lines.insert(i+3, '            return True, raw\n')
        print(f'Fixed list check at line {i+1}')
        # Remove the old return True, raw line
        # The old line 664 was "return True, raw" - now it's at i+4
        del lines[i+5]  # remove duplicate
        break

with open('config.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')