with open('logo.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove leftover return None
del lines[5483]  # remove the return None line

with open('logo.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed logo.py')