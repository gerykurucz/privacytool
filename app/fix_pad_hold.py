with open('assist.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix 1: line ~3186 - _center_hold_cycle check for _lbtn_down
for i in range(3180, 3195):
    if 'or not self._lbtn_down:' in lines[i]:
        lines[i] = lines[i].replace(
            'or not self._lbtn_down:',
            'or (not self._lbtn_down and not self._pad_click_down and not self._pad_raw_down):'
        )
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

# Fix 2: line ~3032 - _center_follow_cycle check for _lbtn_down or _rbtn_down
for i in range(3025, 3045):
    if 'if self._lbtn_down or self._rbtn_down:' in lines[i]:
        lines[i] = lines[i].replace(
            'if self._lbtn_down or self._rbtn_down:',
            'if self._lbtn_down or self._rbtn_down or self._pad_click_down or self._pad_raw_down:'
        )
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

with open('assist.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')