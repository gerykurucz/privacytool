with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix fill_list to bind wheel to content
# Find: host, _bind = _scrollable(page, kit, pal)
for i in range(3725, 3745):
    if 'host, _bind = _scrollable(page, kit, pal)' in lines[i]:
        # Change to capture bind function and use it on grid
        lines[i] = '            host, bind_wheel = _scrollable(page, kit, pal)\n'
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        # Find where grid is created and bind wheel to it
        for j in range(i+1, i+15):
            if 'grid = tk.Frame(host, bg=pal["card"])' in lines[j]:
                lines.insert(j+1, '            bind_wheel(grid)\n')
                print(f'Added bind_wheel at line {j+2}')
                break
        break

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')