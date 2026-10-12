with open('license_client.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix exception hole - catch Exception
for i in range(320, 330):
    if 'except (urllib.error.URLError, socket.timeout, TimeoutError, OSError) as exc:' in lines[i]:
        lines[i] = '    except Exception as exc:\n'
        print(f'Fixed exception hole at line {i+1}: {lines[i].rstrip()}')
        break

with open('license_client.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')