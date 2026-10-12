with open('console.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix "shipped example" reference
for i in range(230, 240):
    if 'see the shipped example' in lines[i]:
        lines[i] = '    print("    be tuned in config.ini / config.json; see %s." % app.cfg.path)\n'
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

with open('console.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')