with open('input_backend.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix ViGemPadBackend.button() to use _XINPUT_MASKS
for i in range(1143, 1155):
    if 'bit = 1 << int(index)' in lines[i]:
        lines[i] = '''        with self._lock:
            try:
                name = gamepad.PAD_BUTTONS[int(index)]
            except (IndexError, TypeError, ValueError):
                return False
            # LT/RT are triggers, not buttons - they go via axis()
            if name in ("lt", "rt"):
                return True
            mask = gamepad._XINPUT_MASKS.get(name)
            if mask is None:
                return False
            if down:
                self._report.wButtons |= mask
            else:
                self._report.wButtons &= ~mask & 0xFFFF
            self._dirty = True\n'''
        # Remove the old lines until the return
        j = i + 1
        while j < len(lines) and 'return True' not in lines[j]:
            j += 1
        if j < len(lines):
            j += 1  # include return True
        del lines[i+1:j]
        print(f'Fixed button mapping at line {i+1}')
        break

with open('input_backend.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')