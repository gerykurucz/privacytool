with open('license_client.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the whole gate block properly
new_block = [
    '                try:\n',
    '                    until = float(ent.get("until") or 0)\n',
    '                except Exception:\n',
    '                    until = 0.0\n',
    '                if ent.get("active") and until > time.time():\n',
    '                    return True, "live", body\n',
    '                return False, "no_entitlement", body\n',
    '            if not row_is_active(row):\n',
    '                return False, str(row.get("status") or "no_entitlement"), body\n',
    '            return True, "live", body\n',
    '\n',
]

lines[828:839] = new_block

with open('license_client.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed gate block')