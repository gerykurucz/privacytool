with open('assist.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the pending_classics loop
for i in range(2020, 2040):
    if 'for entry in self.pending_classics:' in lines[i]:
        print(f'Found at line {i+1}')
        # Insert pad check after the for line
        lines.insert(i+1, '                if entry.get("pad"):\n')
        lines.insert(i+2, '                    continue\n')
        break

with open('assist.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')