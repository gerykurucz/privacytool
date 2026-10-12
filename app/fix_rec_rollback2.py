with open('recordings.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix remove()
content = content.replace(
    '''        self.recordings.remove(rec)
        return self.save()''',
    '''        self.recordings.remove(rec)
        if not self.save():
            self.recordings.append(rec)  # rollback
            return False
        return True''')

# Fix set_name()
content = content.replace(
    '''        rec["name"] = name
        return self.save()''',
    '''        old_name = rec["name"]
        rec["name"] = name
        if not self.save():
            rec["name"] = old_name
            return False
        return True''')

# Fix set_loop()
content = content.replace(
    '''        rec["loop"] = _as_bool(loop, False)
        return self.save()''',
    '''        old_loop = rec["loop"]
        rec["loop"] = _as_bool(loop, False)
        if not self.save():
            rec["loop"] = old_loop
            return False
        return True''')

with open('recordings.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed rollback')