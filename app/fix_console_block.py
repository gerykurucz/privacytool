with open('console.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the broken block - lines 288-296
new_block = [
    '            try:\n',
    '                ans = input("   Enter re-checks, q quits: ").strip().lower()\n',
    '            except (EOFError, KeyboardInterrupt):\n',
    '                print("")\n',
    '                return None\n',
    '            if ans in ("q", "quit"):\n',
    '                return None\n',
    '            online.nudge_publisher(cfg)\n',
    '            continue\n',
    '        state = str((ent or {}).get("status", "unsubscribed"))\n',
]

lines[287:297] = new_block

with open('console.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed block')