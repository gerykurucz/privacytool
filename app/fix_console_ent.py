with open('console.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix ent possibly unbound - init at loop top
for i in range(325, 335):
    if 'while True:' in lines[i]:
        lines.insert(i+1, '            ent = None\n')
        print(f'Added ent init at line {i+2}')
        break

with open('console.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')