with open('license_client.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix self.received = to type(self).received =
for i in range(335, 345):
    if 'self.received = ' in lines[i]:
        lines[i] = lines[i].replace('self.received = ', 'type(self).received = ')
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

with open('license_client.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')