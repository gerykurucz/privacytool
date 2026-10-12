with open('console.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix returns inside _console_subscribe_loop
for i in range(270, 330):
    if 'return True' in lines[i] and 'online.entitlement_active' in ''.join(lines[max(0,i-3):i]):
        lines[i] = '            return identity\n'
        print(f'Fixed return True at line {i+1}')
    if 'return False' in lines[i]:
        lines[i] = '            return None\n'
        print(f'Fixed return False at line {i+1}')

with open('console.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')