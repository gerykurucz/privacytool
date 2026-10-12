with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix PROVIDER_LOGO_B64 direct index to use .get() with fallback
for i in range(2750, 2760):
    if 'logo.PROVIDER_LOGO_B64[name]' in lines[i]:
        lines[i] = '            logo.PROVIDER_LOGO_B64.get(name, logo.PROVIDER_LOGO_B64.get("discord", ""))))\n'
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')