with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix layout_tabs row index overflow
for i in range(3145, 3160):
    if 'row += 1' in lines[i]:
        lines.insert(i+1, '            row = min(row, len(tab_rows) - 1)\n')
        print(f'Added row clamp at line {i+2}')
        break

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')