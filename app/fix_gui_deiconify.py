with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix: add deiconify before mainloop in _run_main
for i in range(5360, 5370):
    if 'root.mainloop()' in lines[i]:
        lines.insert(i, '    root.deiconify()  # show fully built window\n')
        print(f'Added deiconify at line {i+1}')
        break

# Remove the incorrect deiconify from _gate_window (it creates its own Tk)
for i in range(5625, 5640):
    if 'root.deiconify()' in lines[i] and 'show fully built window' in lines[i]:
        del lines[i]
        print(f'Removed incorrect deiconify at line {i+1}')
        break

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')