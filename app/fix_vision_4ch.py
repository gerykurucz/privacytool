with open('vision.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix 4-channel crash: add guard after h,w extraction
for i in range(1898, 1905):
    if 'h, w = a.shape[:2]' in lines[i]:
        lines.insert(i+1, '    if a.shape[2] > 3:\n')
        lines.insert(i+2, '        a = a[..., :3]\n')
        print(f'Added 4-channel guard at line {i+2}')
        break

with open('vision.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')