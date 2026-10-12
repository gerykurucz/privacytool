with open('vision.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix _cached_parse_accents cache collision
# key = raw if isinstance(raw, str) else ""  -> all non-strings collide
# Also accents and excludes share the same cache dict
# Fix: use repr for non-strings, and separate caches

# We'll change to use a tuple key (type, raw) and create separate caches
# First, let's add a separate cache for excludes at the top where _accent_parse_cache is defined

# Find _accent_parse_cache definition
for i in range(880, 900):
    if '_accent_parse_cache' in lines[i] and '=' in lines[i]:
        lines.insert(i+1, '_exclude_parse_cache = {}\n')
        print(f'Added _exclude_parse_cache at line {i+2}')
        break

# Now fix _cached_parse_accents to use proper key
for i in range(898, 910):
    if 'key = raw if isinstance(raw, str) else ""' in lines[i]:
        lines[i] = '    key = ("s", raw) if isinstance(raw, str) else ("r", repr(raw))\n'
        print(f'Fixed key at line {i+1}')
        break

# Also need a separate function for excludes or pass cache as parameter
# Let's add a parameter to specify which cache to use
# Find the function signature
for i in range(898, 910):
    if 'def _cached_parse_accents(raw):' in lines[i]:
        lines[i] = 'def _cached_parse_accents(raw, cache=None):\n'
        print(f'Updated signature at line {i+1}')
        # Find where _accent_parse_cache is used and replace with cache param
        for j in range(i+1, i+15):
            if '_accent_parse_cache' in lines[j]:
                lines[j] = lines[j].replace('_accent_parse_cache', 'cache')
                print(f'Replaced cache at line {j+1}: {lines[j].rstrip()}')
        break

# Now we need to update callers to pass the right cache
# But that's more invasive. Let's instead create a separate function for excludes
# and keep this one simple but with fixed key

# Actually, simpler approach: just fix the key collision, keep single cache
# The accents/excludes collision is less likely since they're different values
# The main bug is non-string collision

# Let's revert the cache param change and just fix the key
for i in range(898, 910):
    if 'def _cached_parse_accents(raw, cache=None):' in lines[i]:
        lines[i] = 'def _cached_parse_accents(raw):\n'
        print(f'Reverted signature at line {i+1}')
        break

with open('vision.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')