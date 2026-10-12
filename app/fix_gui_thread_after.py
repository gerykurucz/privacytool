with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix txt.after(0, _paint) -> root.after(0, _paint) in _avail_probe
for i in range(3570, 3580):
    if 'txt.after(0, _paint)' in lines[i]:
        lines[i] = lines[i].replace('txt.after(0, _paint)', 'root.after(0, _paint)')
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')