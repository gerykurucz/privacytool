with open('license_client.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix device_id to create directory
for i in range(264, 275):
    if 'with open(path, "w", encoding="utf-8") as fh:' in lines[i]:
        lines.insert(i, '        try:\n')
        lines.insert(i+1, '            os.makedirs(os.path.dirname(path), exist_ok=True)\n')
        lines.insert(i+2, '        except Exception:\n')
        lines.insert(i+3, '            pass\n')
        print(f'Added makedirs at line {i+1}')
        break

with open('license_client.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')