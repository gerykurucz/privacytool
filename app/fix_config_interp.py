with open('config.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix interpolation issue: add interpolation=None
for i in range(540, 550):
    if 'parser = ConfigParser(strict=False)' in lines[i]:
        lines[i] = '        parser = ConfigParser(strict=False, interpolation=None)\n'
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

# Also wrap raw = getter(key) in try/except
for i in range(560, 590):
    if 'raw = getter(key)' in lines[i]:
        lines[i] = '                try:\n'
        lines.insert(i+1, '                    raw = getter(key)\n')
        lines.insert(i+2, '                except Exception:\n')
        lines.insert(i+3, '                    continue\n')
        print(f'Wrapped getter at line {i+1}')
        break

with open('config.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')