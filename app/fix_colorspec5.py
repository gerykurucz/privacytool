with open('colorspec.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove line 119 which overwrites the conversion
del lines[118]  # remove "items = spec"

with open('colorspec.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed overwrite')