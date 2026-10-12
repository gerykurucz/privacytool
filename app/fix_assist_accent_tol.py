with open('assist.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix unguarded float(accent_tolerance) at line 1188
for i in range(1185, 1195):
    if 'float(self.cfg.get("accent_tolerance", 26))' in lines[i]:
        lines[i] = '            try:\n'
        lines.insert(i+1, '                tol = float(self.cfg.get("accent_tolerance", 26))\n')
        lines.insert(i+2, '            except Exception:\n')
        lines.insert(i+3, '                tol = 26.0\n')
        lines.insert(i+4, '            return _sig_matches_accents(\n')
        lines.insert(i+5, '                getattr(target, "sig", None), accents,\n')
        lines.insert(i+6, '                tol,\n')
        lines.insert(i+7, '                accent_soft_of(self.cfg),\n')
        lines.insert(i+8, '                accent_matcher_of(self.cfg),\n')
        # Need to remove the old return line and following lines
        # Find the end of the return statement
        j = i + 9
        while j < len(lines) and ')' not in lines[j]:
            j += 1
        if j < len(lines):
            j += 1  # include the closing )
        del lines[i+9:j]
        print(f'Fixed accent_tolerance at line {i+1}')
        break

with open('assist.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')