with open('console.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix indent at line 326
lines[325] = '        ent = None\n'

with open('console.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed indent')