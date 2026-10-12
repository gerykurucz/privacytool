with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix fill_list - only bind_wheel when scroll=True
for i in range(3738, 3755):
    if 'grid = tk.Frame(host, bg=pal["card"])' in lines[i]:
        # Insert bind_wheel only when scroll is True
        lines[i] = '        if scroll:\n'
        lines.insert(i+1, '            bind_wheel(grid)\n')
        lines.insert(i+2, '        grid = tk.Frame(host, bg=pal["card"])\n')
        # Remove the old grid line
        del lines[i+3]
        print(f'Fixed fill_list at line {i+1}')
        break

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')