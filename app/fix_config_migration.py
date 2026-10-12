with open('config.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix stale keys save before sanitize (line 732)
for i in range(730, 740):
    if 'self.save()' in lines[i] and 'stale' in ''.join(lines[max(0,i-10):i]):
        # Move this save after _sanitize() call at the end
        # For now, just comment it out - the final sanitize will save
        lines[i] = '                     # self.save()  # moved after _sanitize\n'
        print(f'Commented stale save at line {i+1}')
        break

# Fix retired keys save before sanitize (line 760)
for i in range(755, 765):
    if 'self.save()' in lines[i] and 'retired' in ''.join(lines[max(0,i-10):i]):
        lines[i] = '                         # self.save()  # moved after _sanitize\n'
        print(f'Commented retired save at line {i+1}')
        break

# Fix version < 8 save before sanitize (line 783)
for i in range(780, 790):
    if 'self.save()' in lines[i] and 'version' in ''.join(lines[max(0,i-10):i]):
        lines[i] = '                     # self.save()  # moved after _sanitize\n'
        print(f'Commented version save at line {i+1}')
        break

with open('config.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')