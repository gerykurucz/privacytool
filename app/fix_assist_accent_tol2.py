with open('assist.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the broken nested return - replace lines 1186-1203
new_block = [
    '        try:\n',
    '            tol = float(self.cfg.get("accent_tolerance", 26))\n',
    '        except Exception:\n',
    '            tol = 26.0\n',
    '        return _sig_matches_accents(\n',
    '            getattr(target, "sig", None), accents,\n',
    '            tol,\n',
    '            accent_soft_of(self.cfg),\n',
    '            accent_matcher_of(self.cfg),\n',
    '            variants=accent_variants_of(self.cfg),\n',
    '        )\n',
    '\n',
    '\n',
    '\n',
]

lines[1185:1204] = new_block

with open('assist.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed properly')