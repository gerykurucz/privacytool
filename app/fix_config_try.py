with open('config.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix empty try block - replace with pass or remove
# Since save is commented out, just remove the try/except
for i in range(730, 740):
    if 'try:' in lines[i] and '# self.save()' in lines[i+1]:
        # Remove try/except block
        del lines[i:i+4]  # remove try, comment, except, pass
        print(f'Removed empty try block at line {i+1}')
        break

with open('config.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')