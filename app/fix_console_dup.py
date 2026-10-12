with open('console.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove duplicate line 104
del lines[103]  # remove the duplicate

with open('console.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed duplicate')