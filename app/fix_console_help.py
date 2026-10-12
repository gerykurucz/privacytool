with open('console.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix print_help: "quitting goes through the window's close button" -> "q quits"
for i in range(145, 155):
    if "quitting goes through the window's close button" in lines[i]:
        lines[i] = '    print("    q quits")\n'
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

with open('console.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')