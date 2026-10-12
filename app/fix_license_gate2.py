with open('license_client.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the if block - need proper indentation and body
lines[833] = '                if ent.get("active") and until > time.time():\n'
lines[834] = '                    return True, "live", body\n'
lines.insert(835, '                return False, "no_entitlement", body\n')

with open('license_client.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed gate if block')