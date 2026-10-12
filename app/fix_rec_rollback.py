with open('recordings.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix remove() to rollback on save failure
for i in range(263, 275):
    if 'def remove(self, rid):' in lines[i]:
        # Find the return self.save() line and wrap
        for j in range(i, i+10):
            if 'return self.save()' in lines[j]:
                lines[j] = '        if not self.save():\n'
                lines.insert(j+1, '            self.recordings.append(rec)  # rollback\n')
                lines.insert(j+2, '            return False\n')
                lines.insert(j+3, '        return True\n')
                del lines[j+4:j+5]  # remove old return
                print(f'Fixed remove at line {j+1}')
                break
        break

# Fix set_name() to rollback on save failure
for i in range(270, 285):
    if 'def set_name(self, rid, name):' in lines[i]:
        for j in range(i, i+15):
            if 'rec["name"] = name' in lines[j]:
                name_line = j
            if 'return self.save()' in lines[j]:
                lines.insert(j, '        old_name = rec["name"]\n')
                lines[j+1] = '        rec["name"] = name\n'
                lines[j+2] = '        if not self.save():\n'
                lines.insert(j+3, '            rec["name"] = old_name\n')
                lines.insert(j+4, '            return False\n')
                lines.insert(j+5, '        return True\n')
                del lines[j+6:j+7]
                print(f'Fixed set_name at line {j+1}')
                break
        break

# Fix set_loop() to rollback on save failure
for i in range(280, 295):
    if 'def set_loop(self, rid, loop):' in lines[i]:
        for j in range(i, i+15):
            if 'rec["loop"] = _as_bool(loop, False)' in lines[j]:
                loop_line = j
            if 'return self.save()' in lines[j]:
                lines.insert(j, '        old_loop = rec["loop"]\n')
                lines[j+1] = '        rec["loop"] = _as_bool(loop, False)\n'
                lines[j+2] = '        if not self.save():\n'
                lines.insert(j+3, '            rec["loop"] = old_loop\n')
                lines.insert(j+4, '            return False\n')
                lines.insert(j+5, '        return True\n')
                del lines[j+6:j+7]
                print(f'Fixed set_loop at line {j+1}')
                break
        break

with open('recordings.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')