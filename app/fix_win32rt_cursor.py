with open('win32rt.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix get_cursor_pos to raise on failure
for i in range(374, 385):
    if 'return 0, 0' in lines[i]:
        lines[i] = '        raise RuntimeError("GetCursorPos failed")\n'
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

with open('win32rt.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')