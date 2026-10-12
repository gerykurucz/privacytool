with open('online.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix plan.lower() - ensure string
for i in range(1260, 1270):
    if 'plan = ent.get("plan") or ""' in lines[i]:
        lines[i] = '    plan = str(ent.get("plan") or "")\n'
        print(f'Fixed plan at line {i+1}: {lines[i].rstrip()}')
        break

with open('online.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')