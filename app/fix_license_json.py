with open('license_client.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix JSON decode error - wrap json.loads in try/except
for i in range(308, 315):
    if 'return resp.status, (json.loads(raw) if raw.strip() else {})' in lines[i]:
        lines[i] = '            try:\n'
        lines.insert(i+1, '                data = json.loads(raw) if raw.strip() else {}\n')
        lines.insert(i+2, '            except ValueError:\n')
        lines.insert(i+3, '                raise LicenseError("invalid JSON from server")\n')
        lines.insert(i+4, '            return resp.status, data\n')
        # Remove old line
        del lines[i+5]
        print(f'Fixed JSON decode at line {i+1}')
        break

with open('license_client.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')