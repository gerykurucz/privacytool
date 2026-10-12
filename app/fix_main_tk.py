with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove dead Tk completeness check (lines 399-401)
# The import would fail anyway if incomplete
for i in range(395, 410):
    if 'if not (tkinter.Tk and ttk.Style' in lines[i]:
        # Remove this line and the next one (raise ImportError)
        del lines[i:i+2]  # removes 399 and 400
        print(f'Removed dead Tk check at line {i+1}')
        break

with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')