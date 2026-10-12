with open('config.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix indentation at line 709
lines[708] = '                    ok, value = _coerce_value(data[key],\n'
lines[709] = '                                                   DEFAULT_CONFIG[key], key)\n'
lines[710] = '                    if ok:\n'

with open('config.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed indent')