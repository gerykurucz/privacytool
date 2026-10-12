with open('online.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix duplicate url line
del lines[1354]  # remove the broken first url line

with open('online.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed duplicate')