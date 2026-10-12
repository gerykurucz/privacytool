with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove duplicate line 2753
del lines[2752]  # remove the duplicate

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed duplicate')