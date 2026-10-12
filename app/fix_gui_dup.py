with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the duplicate line at 3488 - remove the old else branch
# Line 3487 has the new ternary, line 3488 is the old leftover
del lines[3487]  # remove the old "else tk.StringVar(value=str(cur)))" line

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed duplicate')