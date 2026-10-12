with open('config.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove dead _leak_warned code in _public_values
for i in range(1070, 1090):
    if 'dropped and not self._leak_warned:' in lines[i]:
        # Remove the block
        del lines[i:i+5]  # remove the if block
        print(f'Removed dead leak_warned at line {i+1}')
        break

# Also remove the class attribute _leak_warned = False
for i in range(1080, 1100):
    if '_leak_warned = False' in lines[i]:
        del lines[i]
        print(f'Removed class attribute at line {i+1}')
        break

with open('config.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')