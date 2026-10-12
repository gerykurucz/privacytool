with open('config.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix import_from count - count after sanitize
for i in range(1037, 1060):
    if 'applied = 0' in lines[i]:
        # Change logic: collect keys first, then apply and count
        lines[i] = '        imported_keys = []\n'
        print(f'Changed applied to imported_keys at line {i+1}')
        break

# Find where applied += 1 and change to imported_keys.append(key)
for i in range(1045, 1060):
    if 'applied += 1' in lines[i]:
        lines[i] = '                     imported_keys.append(key)\n'
        print(f'Fixed applied increment at line {i+1}')
        break

# After sanitize, count valid keys
for i in range(1050, 1065):
    if 'self._sanitize()' in lines[i]:
        lines.insert(i+1, '            applied = len([k for k in imported_keys if k in self.values])\n')
        print(f'Added count after sanitize at line {i+2}')
        break

with open('config.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')