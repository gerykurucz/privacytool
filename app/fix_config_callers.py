with open('config.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Update first caller at line 709
for i in range(705, 715):
    if '_coerce_value(data[key],' in lines[i]:
        lines[i] = '                         ok, value = _coerce_value(data[key],\n'
        lines.insert(i+1, '                                                   DEFAULT_CONFIG[key], key)\n')
        print(f'Fixed first caller at line {i+1}')
        break

# Find and fix second caller
for i in range(1035, 1060):
    if '_coerce_value(data[key], DEFAULT_CONFIG[key])' in lines[i]:
        lines[i] = '                ok, value = _coerce_value(data[key], DEFAULT_CONFIG[key], key)\n'
        print(f'Fixed second caller at line {i+1}')
        break

with open('config.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')