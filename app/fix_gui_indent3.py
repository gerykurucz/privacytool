with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix indentation at line 3745 - bind_wheel should be at same level as grid = ...
# Current:
#        if scroll:
#            host, bind_wheel = _scrollable(page, kit, pal)
#            _FIT.append(host)
#        grid = tk.Frame(host, bg=pal["card"])
#            bind_wheel(grid)  <- wrong indent
# Should be:
#        if scroll:
#            host, bind_wheel = _scrollable(page, kit, pal)
#            _FIT.append(host)
#        grid = tk.Frame(host, bg=pal["card"])
#        bind_wheel(grid)

lines[3744] = '        bind_wheel(grid)\n'  # fix indent

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed indent')