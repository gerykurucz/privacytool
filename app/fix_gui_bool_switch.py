with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix bool_switch takefocus=0 -> takefocus=1 for keyboard accessibility
for i in range(2460, 2475):
    if 'takefocus=0' in lines[i]:
        lines[i] = lines[i].replace('takefocus=0', 'takefocus=1')
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')