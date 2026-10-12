with open('logo.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix logo.py:5394 - raw bytes to base64
for i in range(5390, 5400):
    if 'return tk_module.PhotoImage(data=_CACHE[key])' in lines[i]:
        lines[i] = '        return tk_module.PhotoImage(data=base64.b64encode(_CACHE[key]).decode("ascii"))\n'
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

# Fix logo.py:5421 - raw bytes to base64
for i in range(5418, 5428):
    if 'return tk_module.PhotoImage(data=_SURF_CACHE[key])' in lines[i]:
        lines[i] = '        return tk_module.PhotoImage(data=base64.b64encode(_SURF_CACHE[key]).decode("ascii"))\n'
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

with open('logo.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done logo.py')