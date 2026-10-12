with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix make_row to use map_display for map kind
for i in range(3470, 3485):
    if 'var = (tk.BooleanVar(value=bool(cur)) if kind == "bool"' in lines[i]:
        # Replace with map_display for map kind
        lines[i] = '            var = (tk.BooleanVar(value=bool(cur)) if kind == "bool"\n'
        lines.insert(i+1, '                       else tk.StringVar(value=map_display(key, cur) if kind == "map" else str(cur)))\n')
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        print(f'Inserted line {i+2}: {lines[i+1].rstrip()}')
        break

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')