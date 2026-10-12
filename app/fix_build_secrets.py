with open('build_secrets.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix SENSITIVE_KEYS to match actual getter names
for i in range(150, 165):
    if 'SENSITIVE_KEYS = frozenset((' in lines[i]:
        lines[i] = 'SENSITIVE_KEYS = frozenset((\n'
        lines[i+1] = '    "entitlement_repo", "entitlement_branch", "entitlement_pubkey",\n'
        lines[i+2] = '    "stripe_monthly_link", "stripe_trial_link",\n'
        lines[i+3] = '    "discord_client_id", "discord_client_secret",\n'
        lines[i+4] = '    "presence_webhook", "dispatch_pat", "row_pepper",\n'
        lines[i+5] = '))\n'
        print(f'Fixed SENSITIVE_KEYS at line {i+1}')
        break

with open('build_secrets.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')