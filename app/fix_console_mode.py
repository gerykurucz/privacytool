with open('console.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix mode label - use int conversion with fallback
for i in range(28, 32):
    if '1 classic" if cfg.get("mode") == 1 else "2 guide"' in lines[i]:
        lines[i] = '    print("   MODE        : %s" % ("1 classic" if int(str(cfg.get("mode", "2"))).strip() in ("1", "2") and int(cfg.get("mode", "2")) == 1 else "2 guide"))\n'
        print(f'Fixed line {i+1}: {lines[i].rstrip()}')
        break

with open('console.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')