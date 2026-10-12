with open('assist.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 3617: unguarded float(motion_lead_ms)
for i in range(3615, 3625):
    if 'lead_ms = float(self.cfg.get("motion_lead_ms", 50))' in lines[i]:
        lines[i] = '        try:\n'
        lines.insert(i+1, '            lead_ms = float(self.cfg.get("motion_lead_ms", 50))\n')
        lines.insert(i+2, '        except Exception:\n')
        lines.insert(i+3, '            lead_ms = 50.0\n')
        print(f'Fixed line {i+1}')
        break

with open('assist.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')