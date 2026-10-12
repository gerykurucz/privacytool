with open('console.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix banner: print bare key in column, add g=gamepad
for i in range(95, 102):
    if 'print("     %-14s mode 1 classic" % effective_mode_key(cfg, 1))' in lines[i]:
        lines[i] = '    print("     %-14s mode 1 classic" % effective_mode_key(cfg, 1).split()[0])\n'
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
    if 'print("     %-14s mode 2 guide" % effective_mode_key(cfg, 2))' in lines[i+1]:
        lines[i+1] = '    print("     %-14s mode 2 guide" % effective_mode_key(cfg, 2).split()[0])\n'
        print(f'Fixed line {i+2}: {lines[i+1].rstrip()}')
    if 's=status t=toggle h=help q=quit a=accent f=follow' in lines[i+2]:
        lines[i+2] = '    print("     s=status t=toggle h=help q=quit a=accent f=follow g=gamepad c=autoclick v=calibrate p=capture")\n'
        print(f'Fixed line {i+3}: {lines[i+2].rstrip()}')
        break

with open('console.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')