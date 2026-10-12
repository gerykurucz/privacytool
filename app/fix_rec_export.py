with open('recordings.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix export_to to use atomic write and makedirs
for i in range(330, 345):
    if 'try:' in lines[i] and 'with open(path, "w"' in lines[i+1]:
        # Replace the whole block
        new_block = [
            '        folder = os.path.dirname(path)\n',
            '        if folder:\n',
            '            os.makedirs(folder, exist_ok=True)\n',
            '        tmp = path + ".tmp"\n',
            '        try:\n',
            '            with open(tmp, "w", encoding="utf-8") as fh:\n',
            '                json.dump(payload, fh, indent=2)\n',
            '            os.replace(tmp, path)\n',
            '            return True, i18n.L("rec.exported", path)\n',
            '        except (OSError, TypeError, ValueError) as exc:\n',
            '            try:\n',
            '                os.remove(tmp)\n',
            '            except OSError:\n',
            '                pass\n',
            '            return False, i18n.L("rec.export_fail", exc)\n',
        ]
        # Find end of try block
        j = i
        while j < len(lines) and 'except' not in lines[j]:
            j += 1
        while j < len(lines) and 'return' not in lines[j]:
            j += 1
        if j < len(lines):
            j += 1
        lines[i:j] = new_block
        print(f'Fixed export_to at line {i+1}')
        break

with open('recordings.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')