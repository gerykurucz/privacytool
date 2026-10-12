with open('colorspec.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix parse_accents - use 'spec' instead of 'items'
for i in range(109, 130):
    if 'hasattr(items' in lines[i]:
        lines[i] = '    if hasattr(spec, \'__iter__\') and not isinstance(spec, (str, bytes)):\n'
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        # Also fix the next lines
        lines[i+1] = '        try:\n'
        lines[i+2] = '            items = list(spec)\n'
        print(f'Fixed line {i+3}: {lines[i+2].rstrip()}')
        break

with open('colorspec.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')