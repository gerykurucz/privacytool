with open('console.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix indentation at line 276
lines[275] = '                return None\n'

with open('console.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed indent')