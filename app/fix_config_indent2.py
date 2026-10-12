with open('config.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the entire block properly
# Lines 707-715 need to be:
#                 for key in DEFAULT_CONFIG:
#                     if key in data:
#                         ok, value = _coerce_value(data[key],
#                                                   DEFAULT_CONFIG[key], key)
#                         if ok:
#                             self.values[key] = value
#                         else:
#                             log("config.json: ignored invalid %s = %r"
#                                 % (key, data[key]))

new_block = [
    '                for key in DEFAULT_CONFIG:\n',
    '                    if key in data:\n',
    '                        ok, value = _coerce_value(data[key],\n',
    '                                                   DEFAULT_CONFIG[key], key)\n',
    '                        if ok:\n',
    '                            self.values[key] = value\n',
    '                        else:\n',
    '                            log("config.json: ignored invalid %s = %r"\n',
    '                                % (key, data[key]))\n',
    '\n',
]

lines[706:715] = new_block

with open('config.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed block')