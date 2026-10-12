with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix mouse capture dialog: ignore ButtonPress on Button widgets
# Find the for loop that binds ButtonPress
for i in range(2068, 2080):
    if 'win.bind(seq, lambda _e, n=_TK_MOUSE_BUTTONS[num]: finish(n))' in lines[i]:
        # Replace the lambda with one that checks widget class
        lines[i] = '        win.bind(seq, lambda e, n=_TK_MOUSE_BUTTONS[num]: (e.widget.winfo_class() != "Button" and finish(n)))\n'
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')