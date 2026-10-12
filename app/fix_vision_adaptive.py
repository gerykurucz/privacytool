with open('vision.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix hidden switch at contrast_threshold=38
for i in range(1925, 1935):
    if 'thr <= ADAPTIVE_BASE' in lines[i]:
        lines[i] = lines[i].replace(' and thr <= ADAPTIVE_BASE:', ':')
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

with open('vision.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')