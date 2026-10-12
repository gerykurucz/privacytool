with open('online.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix subscribe_url to handle None identity
for i in range(1283, 1295):
    if 'def subscribe_url(cfg, identity, kind="monthly"):' in lines[i]:
        lines.insert(i+1, '    if not isinstance(identity, dict):\n')
        lines.insert(i+2, '        return ""\n')
        print(f'Added identity check at line {i+2}')
        break

with open('online.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')