with open('license_client.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix docstring - remove reference to missing license_base_url
for i in range(33, 45):
    if 'build_secrets.license_base_url()' in lines[i]:
        lines[i] = '    lc.configure(base_url="https://api.example.com",\n'
        print(f'Fixed docstring at line {i+1}: {lines[i].rstrip()}')
        break

with open('license_client.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')