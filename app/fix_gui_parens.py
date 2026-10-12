with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix parentheses mismatch
lines[2752] = '        mark = _PILImage.open(io.BytesIO(base64.b64decode(\n'
lines[2753] = '            logo.PROVIDER_LOGO_B64.get(name, logo.PROVIDER_LOGO_B64.get("discord", "")))))\n'

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed parens')