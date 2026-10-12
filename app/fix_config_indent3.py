with open('config.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix indent at line 1043
lines[1042] = '                    imported_keys.append(key)\n'

with open('config.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed indent')