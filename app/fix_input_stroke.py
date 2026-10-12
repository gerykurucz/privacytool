with open('input_backend.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix _STROKE_LEN from 20 to 24
for i in range(225, 235):
    if '_STROKE_LEN = 20' in lines[i]:
        lines[i] = '    _STROKE_LEN = 24\n'
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

with open('input_backend.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')