with open('online.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix redact_url to also redact client_reference_id
for i in range(1475, 1485):
    if 'prefilled_email=' in lines[i]:
        lines[i] = '_EMAIL_IN_URL = re.compile(r"(prefilled_email=|client_reference_id=)[^&]*")\n'
        print(f'Fixed redact regex at line {i+1}: {lines[i].rstrip()}')
        break

with open('online.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')