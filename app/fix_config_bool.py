with open('config.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix _convert to return error for unrecognized bool strings
for i in range(602, 610):
    if 'return raw.lower() in ("1", "true", "yes", "on")' in lines[i]:
        lines[i] = '            val = raw.lower()\n'
        lines.insert(i+1, '            if val not in ("1", "true", "yes", "on", "0", "false", "no", "off"):\n')
        lines.insert(i+2, '                raise ValueError("not a boolean")\n')
        lines.insert(i+3, '            return val in ("1", "true", "yes", "on")\n')
        print(f'Fixed _convert bool at line {i+1}')
        break

# Fix _coerce_value to reject list/tuple for non-color keys
# The function needs to know the key to check - but it's a standalone function
# We'll change the logic at line 657-661 to be more restrictive
# Actually, the caller (_normalize_choice) should know the key
# Let's check where _coerce_value is called from

with open('config.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')