with open('colorspec.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix parse_accents to accept numeric strings and array-likes
# First, add array-like handling at the start
for i in range(109, 130):
    if 'items = spec' in lines[i]:
        lines[i] = '''    # Handle numpy arrays and other sequence types
    if hasattr(items, '__iter__') and not isinstance(items, (str, bytes)):
        try:
            items = list(items)
        except (TypeError, ValueError):
            return []
    items = spec\n'''
        print(f'Added array handling at line {i+1}')
        break

# Fix the single RGB triple detection to accept numeric strings
for i in range(120, 140):
    if 'all(isinstance(p, (int, float)) and not isinstance(p, bool)' in lines[i]:
        lines[i] = '    if (len(items) == 3 and not isinstance(items, str)\n'
        lines.insert(i+1, '            and all(isinstance(p, (int, float, str)) and not isinstance(p, bool)\n')
        lines.insert(i+2, '                    for p in items)):\n')
        print(f'Fixed triple detection at line {i+1}')
        break

with open('colorspec.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')