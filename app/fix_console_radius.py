with open('console.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix rad_label to show scaled value
for i in range(18, 26):
    if 'rad_label = dict(RADIUS_STEPS).get(rad_value, "custom")' in lines[i]:
        lines[i] = '    scaled_px = app.radius_px()\n'
        lines.insert(i+1, '    rad_label = dict(RADIUS_STEPS).get(rad_value, "custom")\n')
        lines.insert(i+2, '    if scaled_px != rad_value:\n')
        lines.insert(i+3, '        rad_label = "%s (scaled %d px)" % (rad_label, scaled_px)\n')
        print(f'Fixed rad_label at line {i+1}')
        break

with open('console.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')