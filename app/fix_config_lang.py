with open('config.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix language silent reset - add log
for i in range(955, 965):
    if 'self.values["language"] = lang if lang in i18n.codes() else "en"' in lines[i]:
        lines[i] = '        if lang not in i18n.codes():\n'
        lines.insert(i+1, '            log("config: unknown language %r, defaulting to en" % (lang,))\n')
        lines.insert(i+2, '            lang = "en"\n')
        lines.insert(i+3, '        self.values["language"] = lang\n')
        print(f'Fixed language reset at line {i+1}')
        break

with open('config.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')