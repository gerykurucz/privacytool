with open('config.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Add mode to _RANGES
for i in range(799, 810):
    if '"radius": (40, 400),' in lines[i]:
        lines.insert(i+1, '        "mode": (1, 2),\n')
        print(f'Added mode to _RANGES at line {i+2}')
        break

with open('config.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')