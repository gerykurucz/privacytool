with open('input_backend.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix transient cursor failure - don't call note_failure
for i in range(490, 500):
    if 'self.note_failure("cursor read")' in lines[i]:
        lines[i] = '            # Transient failure: fall back without degrading\n'
        lines.insert(i+1, '            win32rt.user32.SetCursorPos(tx, ty)\n')
        print(f'Fixed cursor failure at line {i+1}')
        break

with open('input_backend.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')