with open('config.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove duplicate line 711
del lines[710]  # remove the old DEFAULT_CONFIG[key]) line

with open('config.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed duplicate')