with open('online.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove dead globals
for i in range(123, 130):
    if 'DEFAULT_ENTITLEMENT_BRANCH' in lines[i]:
        del lines[i:i+3]  # remove all three
        print(f'Removed dead globals at line {i+1}')
        break

with open('online.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')