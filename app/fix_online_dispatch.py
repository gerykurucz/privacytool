with open('online.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix dispatch endpoint - use correct repo and ref parameter
for i in range(1347, 1370):
    if 'workflows/entitlements.yml/dispatches' in lines[i]:
        lines[i] = '    url = "https://api.github.com/repos/%s/actions/workflows/entitlements.yml/dispatches" % repo\n'
        print(f'Fixed URL at line {i+1}')
    if '"event_type": "publish"' in lines[i]:
        lines[i] = '    body = json.dumps({"ref": "main"}).encode()\n'
        print(f'Fixed body at line {i+1}')
        break

with open('online.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')