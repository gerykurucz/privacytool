with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix dark mode Combobox popdown: add option_add for Listbox
for i in range(2916, 2930):
    if 'kit.repaint(restyle_tt)' in lines[i]:
        # Insert before this line
        lines.insert(i, '        try:\n')
        lines.insert(i+1, '            root.option_add("*TCombobox*Listbox.background", pal["entry"])\n')
        lines.insert(i+2, '            root.option_add("*TCombobox*Listbox.foreground", pal["text"])\n')
        lines.insert(i+3, '            root.option_add("*TCombobox*Listbox.selectBackground", pal["accent"])\n')
        lines.insert(i+4, '            root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")\n')
        lines.insert(i+5, '        except Exception:\n')
        lines.insert(i+6, '            pass\n')
        print(f'Added Combobox listbox styling at line {i+1}')
        break

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')