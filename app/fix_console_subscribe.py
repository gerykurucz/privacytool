with open('console.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix _console_subscribe_loop to return updated identity
# Change return type from bool to identity
for i in range(270, 325):
    if 'def _console_subscribe_loop(cfg, identity):' in lines[i]:
        lines[i] = 'def _console_subscribe_loop(cfg, identity):\n'
        # The function should return identity on success, None on failure
        # Change return True -> return identity
        # Change return False -> return None
        for j in range(i+1, i+60):
            if 'return True' in lines[j] and 'online.entitlement_active' in lines[j-1]:
                lines[j] = '            return identity\n'
                print(f'Fixed return True at line {j+1}')
            if 'return False' in lines[j] and ('identity is None' in lines[j-1] or 'ans in ("q"' in lines[j-1] or '_retry_prompt()' in lines[j-1] or 'return False' in lines[j-1]):
                lines[j] = '            return None\n'
                print(f'Fixed return False at line {j+1}')
        break

# Also update the caller in console_gate
for i in range(340, 360):
    if 'if not _console_subscribe_loop(cfg, identity):' in lines[i]:
        lines[i] = '        identity = _console_subscribe_loop(cfg, identity)\n'
        lines.insert(i+1, '        if identity is None:\n')
        lines.insert(i+2, '            return None\n')
        print(f'Fixed caller at line {i+1}')
        break

with open('console.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')