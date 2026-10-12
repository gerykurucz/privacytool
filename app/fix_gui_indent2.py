with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix properly - need to restructure lines 3154-3159
# Current broken state:
#             if used and used + w > avail:
#                 row += 1
#             used += w
#                 row = min(row, len(tab_rows) - 1)
#                 used = 0
# Should be:
#             if used and used + w > avail:
#                 row += 1
#                 row = min(row, len(tab_rows) - 1)
#                 used = 0
#             used += w

# Replace lines 3154-3159 (indices 3153-3158)
new_block = [
    '            if used and used + w > avail:\n',
    '                row += 1\n',
    '                row = min(row, len(tab_rows) - 1)\n',
    '                used = 0\n',
    '            used += w\n',
    '            side = "right" if tn == "help" else "left"\n',
]

lines[3153:3159] = new_block

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed properly')