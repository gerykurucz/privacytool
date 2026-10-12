with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the indentation: lines 3154-3158 need restructuring
# Current:
#             if used and used + w > avail:
#                 row += 1
#             row = min(row, len(tab_rows) - 1)
#                 used = 0
# Should be:
#             if used and used + w > avail:
#                 row += 1
#                 row = min(row, len(tab_rows) - 1)
#                 used = 0

# Delete the misplaced clamp line (3156) and the misindented used=0 line (3157)
# and re-insert correctly
del lines[3155]  # removes the clamp at wrong indent (was line 3156)
del lines[3155]  # removes the misindented used=0 (was line 3157)

# Now insert correctly after row += 1 (now at line 3155)
lines.insert(3156, '                row = min(row, len(tab_rows) - 1)\n')
lines.insert(3157, '                used = 0\n')

print('Fixed indentation')

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')