with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove the orphaned raise line (line 399)
del lines[398]  # removes the raise ImportError line

with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed main.py')