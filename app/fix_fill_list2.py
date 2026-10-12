with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix fill_list properly - define grid first, then conditionally bind wheel
new_block = [
    '        host = page\n',
    '        if scroll:\n',
    '            host, bind_wheel = _scrollable(page, kit, pal)\n',
    '            _FIT.append(host)\n',
    '        grid = tk.Frame(host, bg=pal["card"])\n',
    '        if scroll:\n',
    '            bind_wheel(grid)\n',
    '        kit.reg(grid, "card")\n',
    '        grid.pack(fill="x", padx=6, pady=8)\n',
    '        grid.columnconfigure(0, weight=1)\n',
    '        for i, key in enumerate(keys):\n',
    '            make_row(grid, key, i)\n',
    '\n',
    '\n',
]

lines[3738:3751] = new_block

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed fill_list properly')