with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix restore_defaults: add dirty["on"] = False and apply_btn.pack_forget()
for i in range(3370, 3390):
    if 'refresh_fields()' in lines[i] and 'post(6)' in lines[i+1]:
        lines.insert(i+2, '        dirty["on"] = False\n')
        lines.insert(i+3, '        apply_btn.pack_forget()\n')
        print(f'Fixed restore_defaults at line {i+1}')
        break

# Fix do_import: after successful import, call _sync_from_cfg directly (bypass dirty check)
# or clear dirty and refresh
for i in range(3354, 3370):
    if 'root.after(350, lambda: _sync_from_cfg())' in lines[i]:
        # Replace with direct call to avoid dirty check
        lines[i] = '                    _sync_from_cfg()\n'
        print(f'Fixed do_import at line {i+1}')
        break

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')