with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Add tab_bg case in _style_one after bg case
for i in range(2260, 2270):
    if 'elif role == "bg_text":' in lines[i]:
        lines.insert(i, '        elif role == "tab_bg":\n')
        lines.insert(i+1, '            w.configure(bg=pal["tab_bg"])\n')
        print(f'Added tab_bg case at line {i+1}')
        break

# Change bar registration from "bg" to "tab_bg"
for i in range(3040, 3050):
    if 'kit.reg(bar, "bg")' in lines[i]:
        lines[i] = lines[i].replace('kit.reg(bar, "bg")', 'kit.reg(bar, "tab_bg")')
        print(f'Fixed bar registration at line {i+1}: {lines[i].rstrip()}')
        break

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')