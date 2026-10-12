with open('colorspec.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix parse_accent to accept integral float strings like "60.0"
# Line 59: parts = [int(p) if isinstance(p, int) else int(float(p)) if isinstance(p, float) and float(p).is_integer() else None for p in spec]
# Need to also handle strings that are integral floats

# First, let's fix the list/tuple branch to handle strings
for i in range(48, 75):
    if 'parts = [int(p) if isinstance(p, int) else int(float(p)) if isinstance(p, float) and float(p).is_integer() else None for p in spec]' in lines[i]:
        lines[i] = '        try:\n'
        lines.insert(i+1, '            def _to_int(p):\n')
        lines.insert(i+2, '                if isinstance(p, int):\n')
        lines.insert(i+3, '                    return p\n')
        lines.insert(i+4, '                if isinstance(p, float):\n')
        lines.insert(i+5, '                    return int(p) if p.is_integer() else None\n')
        lines.insert(i+6, '                if isinstance(p, str):\n')
        lines.insert(i+7, '                    f = float(p)\n')
        lines.insert(i+8, '                    return int(f) if f.is_integer() else None\n')
        lines.insert(i+9, '                return None\n')
        lines.insert(i+10, '            parts = [_to_int(p) for p in spec]\n')
        lines.insert(i+11, '        except (TypeError, ValueError, OverflowError):\n')
        lines.insert(i+12, '            return None\n')
        print(f'Fixed parse_accent list handling at line {i+1}')
        # Need to remove the old lines - they're now shifted
        # The old line was at i, now it's at i+13, and the except block continues
        # Let's find and remove the old except block
        for j in range(i+13, i+30):
            if 'else:' in lines[j] and 's = str(spec)' in lines[j+1]:
                # Remove from j to the end of the else block
                # The else block ends before the parts length check
                k = j
                while k < len(lines) and 'if len(parts) != 3:' not in lines[k]:
                    k += 1
                del lines[j:k]
                print(f'Removed old else block from {j+1} to {k+1}')
                break
        break

with open('colorspec.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')