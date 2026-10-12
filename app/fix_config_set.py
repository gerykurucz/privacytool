with open('config.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix set() to reject unknown keys
for i in range(1085, 1120):
    if 'def set(self, key, value, save=True):' in lines[i]:
        # Insert after the SENSITIVE_KEYS check
        for j in range(i, i+15):
            if 'with self.lock:' in lines[j]:
                lines.insert(j, '        if key not in DEFAULT_CONFIG:\n')
                lines.insert(j+1, '            log("config.set(%r) ignored - unknown key" % (key,))\n')
                lines.insert(j+2, '            return\n')
                lines.insert(j+3, '\n')
                print(f'Added unknown key check at line {j+1}')
                break
        break

# Fix cycle() div-zero
for i in range(1115, 1140):
    if 'def cycle(self, key, steps):' in lines[i]:
        for j in range(i+1, i+20):
            if 'if current in values:' in lines[j]:
                lines.insert(j, '        if not steps:\n')
                lines.insert(j+1, '            return current\n')
                lines.insert(j+2, '\n')
                print(f'Added cycle div-zero guard at line {j+1}')
                break
        break

with open('config.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')