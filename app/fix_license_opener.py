with open('license_client.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix opener return value ignored
for i in range(500, 515):
    if '(opener or OPEN_URL)(authorize_url)' in lines[i]:
        lines[i] = '        opened = (opener or OPEN_URL)(authorize_url)\n'
        lines.insert(i+1, '        if not opened:\n')
        lines.insert(i+2, '            log("browser opener returned False")\n')
        lines.insert(i+3, '            raise LicenseError("could not open browser")\n')
        print(f'Fixed opener check at line {i+1}')
        break

with open('license_client.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')