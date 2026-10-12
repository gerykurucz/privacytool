with open('vision.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix _subsample_patch to use while loop for ACCENT_MAX_PIXELS
for i in range(1028, 1045):
    if 'if int(mask.sum()) <= ACCENT_MAX_PIXELS:' in lines[i]:
        # Replace the whole block
        new_block = [
            '    while int(mask.sum()) > ACCENT_MAX_PIXELS:\n',
            '        h, w = mask.shape\n',
            '        h2, w2 = (h // 2) * 2, (w // 2) * 2\n',
            '        if h2 < 2 or w2 < 2:\n',
            '            break\n',
            '        s = sub_f32[:h2, :w2].reshape(h2 // 2, 2, w2 // 2, 2, 3)\n',
            '        s = s.mean(axis=(1, 3))\n',
            '        m = mask[:h2, :w2].reshape(h2 // 2, 2, w2 // 2, 2)\n',
            '        m = m.mean(axis=(1, 3)) >= 0.5\n',
            '        if not m.any():\n',
            '            break\n',
            '        sub_f32 = s.astype(np.float32)\n',
            '        mask = m\n',
            '    return sub_f32, mask\n',
        ]
        # Replace lines i to i+13 (the whole function body)
        lines[i:i+14] = new_block
        print(f'Fixed _subsample_patch at line {i+1}')
        break

with open('vision.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')