with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix all 5 PhotoImage(data=buf.getvalue()) to base64
# 1. Line 2355
for i in range(2350, 2360):
    if 'return tk.PhotoImage(data=self._img_cache[key])' in lines[i]:
        lines[i] = '        return tk.PhotoImage(data=base64.b64encode(self._img_cache[key]).decode("ascii"))\n'
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

# 2. Line 2762
for i in range(2758, 2770):
    if 'return tk.PhotoImage(data=buf.getvalue())' in lines[i]:
        lines[i] = '        return tk.PhotoImage(data=base64.b64encode(buf.getvalue()).decode("ascii"))\n'
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

# 3. Line 3977
for i in range(3970, 3985):
    if 'sv_photo[0] = tk.PhotoImage(data=buf.getvalue())' in lines[i]:
        lines[i] = '        sv_photo[0] = tk.PhotoImage(data=base64.b64encode(buf.getvalue()).decode("ascii"))\n'
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

# 4. Line 4010
for i in range(4005, 4015):
    if 'hue_photo[0] = tk.PhotoImage(data=buf.getvalue())' in lines[i]:
        lines[i] = '        hue_photo[0] = tk.PhotoImage(data=base64.b64encode(buf.getvalue()).decode("ascii"))\n'
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

# 5. Check if there's another one - the rounded() function might also use this
# Let me check line 2355 again - that's in rounded()

# Also need to ensure base64 is imported in gui.py
# Check imports at top
for i in range(0, 50):
    if 'import base64' in lines[i]:
        break
else:
    # Add import
    for i in range(0, 30):
        if 'import' in lines[i] and ('import tkinter' in lines[i] or 'from tkinter' in lines[i]):
            lines.insert(i, 'import base64\n')
            print(f'Added base64 import at line {i+1}')
            break

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done gui.py')