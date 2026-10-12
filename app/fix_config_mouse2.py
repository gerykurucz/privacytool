with open('config.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix mouse2 truncation - use round
for i in range(1008, 1015):
    if 'm2 = int(self.values.get(key, 4))' in lines[i]:
        lines[i] = '                 m2 = int(round(self.values.get(key, 4)))\n'
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

with open('config.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')