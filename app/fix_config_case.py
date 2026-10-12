with open('config.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix case-sensitive INI: lowercase keys
for i in range(540, 550):
    if 'parser.optionxform = str' in lines[i]:
        lines[i] = '        parser.optionxform = lambda s: s.lower()\n'
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

with open('config.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')