with open('recordings.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix import_from to check FORMAT_VERSION
for i in range(330, 350):
    if 'items = []' in lines[i]:
        # Add version check before processing items
        lines.insert(i, '        # Check format version\n')
        lines.insert(i+1, '        version = data.get("snappyai_recording") or data.get("snappyai_recordings")\n')
        lines.insert(i+2, '        if version is not None and version != FORMAT_VERSION:\n')
        lines.insert(i+3, '            log("recordings: import format version %r != %d, ignoring" % (version, FORMAT_VERSION))\n')
        lines.insert(i+4, '            return False, i18n.L("rec.bad_version", version, FORMAT_VERSION)\n')
        lines.insert(i+5, '\n')
        print(f'Added version check at line {i+1}')
        break

with open('recordings.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')