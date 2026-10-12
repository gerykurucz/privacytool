with open('vision.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Add colorspec import at top after numpy
for i in range(5, 15):
    if 'import numpy as np' in lines[i]:
        lines.insert(i+1, '\n')
        lines.insert(i+2, 'from colorspec import (ACCENT_PRESETS,\n')
        lines.insert(i+3, '                        hsv_to_rgb,\n')
        lines.insert(i+4, '                        parse_accent as _parse_accent,\n')
        lines.insert(i+5, '                        parse_accents as _parse_accents)\n')
        print(f'Added import at line {i+3}')
        break

# Remove mid-file import and aliases
for i in range(715, 735):
    if 'from colorspec import' in lines[i]:
        # Remove 7 lines: import (5 lines) + blank + 2 alias lines
        del lines[i:i+11]
        print(f'Removed mid-file import at line {i+1}')
        break

with open('vision.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')