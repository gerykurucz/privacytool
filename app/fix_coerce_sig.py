with open('config.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix _coerce_value signature
for i in range(625, 635):
    if 'def _coerce_value(raw, default):' in lines[i]:
        lines[i] = 'def _coerce_value(raw, default, key=None):\n'
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

with open('config.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')