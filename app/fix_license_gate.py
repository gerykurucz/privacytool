with open('license_client.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix gate float error - wrap in try/except
for i in range(818, 825):
    if 'float(ent.get("until") or 0)' in lines[i]:
        lines[i] = '                try:\n'
        lines.insert(i+1, '                    until = float(ent.get("until") or 0)\n')
        lines.insert(i+2, '                except Exception:\n')
        lines.insert(i+3, '                    until = 0.0\n')
        lines.insert(i+4, '                if ent.get("active") and until > time.time():\n')
        # Remove old line
        del lines[i+5]
        print(f'Fixed gate float at line {i+1}')
        break

with open('license_client.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')