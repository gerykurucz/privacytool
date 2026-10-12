with open('config.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix all empty try blocks with only commented save
# Pattern: try: -> comment -> except Exception: -> pass
# Replace with nothing

i = 0
while i < len(lines):
    if i+3 < len(lines) and 'try:' in lines[i] and '# self.save()' in lines[i+1] and 'except Exception:' in lines[i+2] and 'pass' in lines[i+3]:
        del lines[i:i+4]
        print(f'Removed empty try block at line {i+1}')
        continue
    i += 1

with open('config.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')