with open('input_backend.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Add close() method after _close_all
for i in range(375, 385):
    if 'self._handle = None' in lines[i]:
        lines.insert(i+1, '\n')
        lines.insert(i+2, '    def close(self):\n')
        lines.insert(i+3, '        self._close_all()\n')
        lines.insert(i+4, '        if self._accel_disabled:\n')
        lines.insert(i+5, '            try:\n')
        lines.insert(i+6, '                import win32rt\n')
        lines.insert(i+7, '                win32rt.user32.SystemParametersInfoA(\n')
        lines.insert(i+8, '                    0x0071, 0, ctypes.c_int(self._prev_accel), 2)\n')
        lines.insert(i+9, '            except Exception:\n')
        lines.insert(i+10, '                pass\n')
        lines.insert(i+11, '            self._accel_disabled = False\n')
        print(f'Added close() method at line {i+2}')
        break

with open('input_backend.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')