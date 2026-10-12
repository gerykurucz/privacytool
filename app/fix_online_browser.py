with open('online.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix browser-open failure return
for i in range(1729, 1740):
    if 'return None, None' in lines[i]:
        lines[i] = '        msg = "Could not open a browser automatically - open this URL by hand:\\n    %s" % url\n'
        lines.insert(i+1, '        log(msg)\n')
        lines.insert(i+2, '        return None, msg\n')
        del lines[i+3]  # remove old log line
        print(f'Fixed browser failure return at line {i+1}')
        break

with open('online.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')