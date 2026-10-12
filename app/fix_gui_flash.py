with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix: withdraw window at creation, deiconify at the end after all widgets built
# Change line 2868: root = tk.Tk() -> root = tk.Tk(); root.withdraw()
for i in range(2865, 2875):
    if 'root = tk.Tk()' in lines[i]:
        lines[i] = '    root = tk.Tk()\n    root.withdraw()  # hide until fully built\n'
        print(f'Added withdraw at line {i+1}')
        break

# Find the end of _run_main where we should deiconify
# Look for the mainloop or end of function
for i in range(5600, 5720):
    if 'root.mainloop()' in lines[i]:
        # Insert deiconify before mainloop
        lines.insert(i, '    root.deiconify()  # show fully built window\n')
        print(f'Added deiconify at line {i+1}')
        break

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')