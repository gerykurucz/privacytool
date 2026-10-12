with open('vision.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the cache references - use _accent_parse_cache
for i in range(900, 910):
    if 'hit = cache.get(key)' in lines[i]:
        lines[i] = '    hit = _accent_parse_cache.get(key)\n'
    elif 'if len(cache) > 32:' in lines[i]:
        lines[i] = '        if len(_accent_parse_cache) > 32:\n'
    elif 'cache.clear()' in lines[i]:
        lines[i] = '            _accent_parse_cache.clear()\n'
    elif 'cache[key] = hit' in lines[i]:
        lines[i] = '        _accent_parse_cache[key] = hit\n'

with open('vision.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed cache references')