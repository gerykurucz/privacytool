with open('license_client.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix release() to check HTTP status
for i in range(659, 675):
    if 'return True' in lines[i] and 'log("seat released")' in lines[i-1]:
        # Change to capture status from _request
        lines[i-2] = '        status, body = _request("/api/v1/access/release",\n'
        lines.insert(i-1, '                          data={"device_id": device_id()}, token=token, timeout=5)\n')
        lines[i] = '        if 200 <= status < 300:\n'
        lines.insert(i+1, '            log("seat released")\n')
        lines.insert(i+2, '            return True\n')
        lines.insert(i+3, '        return False\n')
        # Remove old lines
        del lines[i+4:i+6]
        print(f'Fixed release status check at line {i+1}')
        break

with open('license_client.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')