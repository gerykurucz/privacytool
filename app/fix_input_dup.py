with open('input_backend.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix duplicate with self._lock line
del lines[1158]  # remove duplicate

with open('input_backend.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed duplicate')