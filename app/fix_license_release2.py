with open('license_client.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the broken release function
new_release = '''def release(session):
    """Graceful exit: free the seat at once instead of making the other machine
    wait out the lease. Best effort -- a failure just means the lease lapses."""
    token = (session or {}).get("access_token")
    if not token:
        return False
    try:
        status, body = _request("/api/v1/access/release",
                          data={"device_id": device_id()}, token=token, timeout=5)
        if 200 <= status < 300:
            log("seat released")
            return True
        return False
    except LicenseError as exc:
        log("release failed (the lease will lapse on its own): %s" % exc)
        return False


'''

# Find and replace the broken function
for i in range(665, 690):
    if 'def release(session):' in lines[i]:
        # Find end of function
        j = i + 1
        while j < len(lines) and (lines[j].startswith(' ') or lines[j].startswith('\t') or lines[j].strip() == ''):
            j += 1
        lines[i:j] = new_release.splitlines(keepends=True)
        print(f'Fixed release function at line {i+1}')
        break

with open('license_client.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')