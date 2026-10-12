with open('online.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove global _bs function
for i in range(95, 105):
    if 'def _bs(name):' in lines[i]:
        del lines[i:i+2]  # remove function and blank line
        print(f'Removed _bs at line {i+1}')
        break

with open('online.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')