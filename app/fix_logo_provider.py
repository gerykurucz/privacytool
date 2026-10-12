with open('logo.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix get_provider_logo dead try/except
for i in range(5480, 5490):
    if 'def get_provider_logo(name):' in lines[i]:
        lines[i+1] = '    return PROVIDER_LOGO_B64.get(name)\n'
        del lines[i+2:i+4]  # remove try/except
        print(f'Fixed get_provider_logo at line {i+1}')
        break

with open('logo.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')