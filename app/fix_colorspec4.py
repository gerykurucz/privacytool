with open('colorspec.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the duplicate lines at 129-134
# Remove the duplicate and fix the block
del lines[128:135]  # remove the broken block

# Insert correct block
new_block = [
    '    if (len(items) == 3 and not isinstance(items, str)\n',
    '            and all(isinstance(p, (int, float, str)) and not isinstance(p, bool)\n',
    '                    for p in items)):\n',
    '        items = [items]\n',
    '\n',
]
lines[128:128] = new_block

with open('colorspec.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed duplicate')