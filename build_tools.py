"""Build-time helpers: secret exposure scan, hash manifest, DLL pins.

Stdlib only, no imports from the app, safe to run on any platform.
"""

import argparse
import ast
import hashlib
import os
import sys

BLOB_MODULE = "general_utils.py"
MANIFEST_NAME = "SHA256SUMS.txt"


def _sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            block = handle.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def read_secret_blob(project_dir):
    """Pull _KEY and _BLOB straight out of the source with ast (no import)."""
    path = os.path.join(project_dir, BLOB_MODULE)
    with open(path, "r", encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=path)
    key = None
    blob = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        if target.id == "_KEY":
            key = ast.literal_eval(node.value)
        elif target.id == "_BLOB":
            blob = ast.literal_eval(node.value)
    if key is None:
        raise SystemExit("could not find _KEY in %s" % path)
    return key, blob


def decode_blob(key, blob):
    import base64
    ks = hashlib.sha256(key).digest()
    out = {}
    for name, raw in sorted(blob.items()):
        if not raw:
            continue
        try:
            data = base64.b64decode(raw, validate=True)
            out[name] = bytes(c ^ ks[i % len(ks)]
                              for i, c in enumerate(data)).decode("utf-8")
        except Exception as exc:
            out[name] = "<undecodable: %r>" % (exc,)
    return out


def _needles(value, raw):
    """Byte patterns a `strings`-style attacker would find for one secret."""
    found = []
    if value:
        found.append(("plaintext", value.encode("utf-8")))
        found.append(("utf16", value.encode("utf-16-le")))
    if raw:
        found.append(("base64", raw.encode("utf-8")))
    return found


def _mask(value):
    if len(value) <= 10:
        return value
    return "%s*** (%d chars)" % (value[:6], len(value))


def _blockers(decoded):
    """Plain-language problems, safe to paste into a build log."""
    out = []
    if decoded.get("DISCORD_CLIENT_SEC"):
        out.append("a Discord OAuth CLIENT SECRET ships inside the exe. It is "
                   "a server-side credential: anyone who lifts it can exchange "
                   "stolen authorisation codes as your app. PKCE is already "
                   "implemented (online.py sets pkce=True), so mark the Discord "
                   "application public, drop the secret and ROTATE the current "
                   "one - it has already been distributed.")
    if decoded.get("PRESENCE_WEBHOOK"):
        out.append("a Discord webhook URL ships inside the exe. The token in "
                   "the path lets anyone post to that channel and edit or "
                   "delete what it posted. ROTATE it and move the posting "
                   "server-side.")
    for name in ("STRIPE_MONTHLY", "STRIPE_TRIAL"):
        if "/test_" in decoded.get(name, ""):
            out.append("%s is a Stripe TEST link - checkout completes but no "
                       "money moves and no subscription activates." % name)
    return out


def scan_binary(target, project_dir, verbose=False, reveal=False):
    """Report which build secrets are recoverable from a shipped file."""
    key, blob = read_secret_blob(project_dir)
    decoded = decode_blob(key, blob)
    with open(target, "rb") as handle:
        payload = handle.read()

    rows = []
    for name, value in decoded.items():
        hits = [label for label, needle in _needles(value, blob.get(name, ""))
                if needle in payload]
        rows.append((name, value, hits))

    width = max([len(n) for n, _, _ in rows] + [18])
    print("")
    print("Secret exposure scan: %s" % os.path.basename(target))
    print("  %.1f MiB scanned; XOR key literal present: %s"
          % (len(payload) / 1048576.0,
             "YES" if key in payload else "no"))
    print("  Nuitka compiles the source to machine code, but string literals")
    print("  survive in the data section - the XOR layer is obfuscation, not")
    print("  encryption. This is what a static scan recovers:")
    print("")
    exposed = 0
    for name, value, hits in rows:
        shown = value if reveal or len(value) <= 10 else _mask(value)
        if hits:
            exposed += 1
            print("  %-*s  RECOVERABLE (%s)  %s"
                  % (width, name, ",".join(sorted(set(hits))), shown))
        elif verbose:
            print("  %-*s  not found" % (width, name))
    empty = sorted(n for n, v in blob.items() if not v)

    print("")
    print("  %d of %d populated value(s) recoverable." % (exposed, len(rows)))
    if empty:
        print("  empty at build time: %s" % ", ".join(empty))

    problems = _blockers(decoded)
    if not blob.get("ROW_PEPPER"):
        problems.append("ROW_PEPPER is empty, so entitlement rows are keyed by "
                        "unsalted sha256(e-mail) in a public file.")
    if problems:
        print("")
        print("  Release blockers found by this scan:")
        for text in problems:
            print("   ! %s" % text)
    else:
        print("  No release blockers found by this scan.")
    print("")
    return exposed


def write_manifest(dist_dir):
    entries = []
    for root, dirs, files in os.walk(dist_dir):
        dirs.sort()
        for name in sorted(files):
            if name == MANIFEST_NAME:
                continue
            full = os.path.join(root, name)
            rel = os.path.relpath(full, dist_dir).replace(os.sep, "/")
            entries.append((rel, _sha256_file(full), os.path.getsize(full)))
    out = os.path.join(dist_dir, MANIFEST_NAME)
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("# SHA-256 of every file in this folder, relative paths.\n")
        handle.write("# Regenerate: python build_tools.py manifest <folder>\n")
        for rel, digest, size in entries:
            handle.write("%s  %d  %s\n" % (digest, size, rel))
    print("Wrote %s (%d files)" % (out, len(entries)))
    return out


def verify_manifest(dist_dir):
    path = os.path.join(dist_dir, MANIFEST_NAME)
    if not os.path.exists(path):
        print("No %s in %s" % (MANIFEST_NAME, dist_dir))
        return 1
    bad = 0
    checked = 0
    listed = set()
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("  ", 2)
            if len(parts) != 3:
                print("  MALFORMED  %s" % line[:80])
                bad += 1
                continue
            digest, _size, rel = parts
            listed.add(rel)
            full = os.path.join(dist_dir, rel.replace("/", os.sep))
            checked += 1
            if not os.path.exists(full):
                print("  MISSING  %s" % rel)
                bad += 1
            elif _sha256_file(full) != digest:
                print("  CHANGED  %s" % rel)
                bad += 1
    for root, _dirs, files in os.walk(dist_dir):
        for name in files:
            if name == MANIFEST_NAME:
                continue
            rel = os.path.relpath(os.path.join(root, name),
                                  dist_dir).replace(os.sep, "/")
            if rel not in listed:
                print("  UNLISTED  %s" % rel)
                bad += 1
    print("Verified %d file(s), %d problem(s)." % (checked, bad))
    return 1 if bad else 0


def pin_dll(dll_path):
    """Write <dll>.sha256 so the app can refuse a swapped DLL at load time."""
    digest = _sha256_file(dll_path)
    out = dll_path + ".sha256"
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("%s  %s\n" % (digest, os.path.basename(dll_path)))
    print("Pinned %s -> %s" % (os.path.basename(dll_path), digest))
    return out


def sign(dist_dir, exe_name):
    """Authenticode-sign the exe when a certificate is configured.

    Skipped silently unless SNAPPYAI_CERT_SUBJECT (store lookup) or
    SNAPPYAI_CERT_PFX + SNAPPYAI_CERT_PASSWORD (file) is set.
    """
    subject = os.environ.get("SNAPPYAI_CERT_SUBJECT", "").strip()
    pfx = os.environ.get("SNAPPYAI_CERT_PFX", "").strip()
    if not subject and not pfx:
        print("Signing skipped: set SNAPPYAI_CERT_SUBJECT or SNAPPYAI_CERT_PFX.")
        return 0
    exe = os.path.join(dist_dir, exe_name)
    if not os.path.exists(exe):
        print("Signing skipped: %s not found" % exe)
        return 1
    args = ["signtool", "sign", "/fd", "SHA256", "/td", "SHA256",
            "/tr", os.environ.get(
                "SNAPPYAI_TIMESTAMP_URL",
                "http://timestamp.digicert.com")]
    if pfx:
        args += ["/f", pfx]
        password = os.environ.get("SNAPPYAI_CERT_PASSWORD", "")
        if password:
            args += ["/p", password]
    else:
        args += ["/sha1" if len(subject) == 40 else "/n", subject]
    args.append(exe)
    shown = ["****" if a == password else a for a in args] if pfx and password \
        else list(args)
    print("Running: %s" % " ".join(shown))
    import subprocess
    try:
        rc = subprocess.call(args)
    except OSError as exc:
        print("signtool could not be started (%r)." % (exc,))
        print("It ships with the Windows SDK: 'Windows SDK Signing Tools'.")
        return 1
    if rc == 0:
        print("Signed %s" % exe)
    else:
        print("signtool exited %d - the build is UNSIGNED." % rc)
    return rc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("scan", help="report recoverable build secrets")
    p.add_argument("target")
    p.add_argument("--project", default=os.path.dirname(
        os.path.abspath(__file__)))
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--reveal", action="store_true",
                   help="print recovered values in full (default: masked, so "
                        "the build log stays safe to paste)")

    p = sub.add_parser("manifest", help="write SHA256SUMS.txt for a folder")
    p.add_argument("dist")

    p = sub.add_parser("verify", help="check a folder against SHA256SUMS.txt")
    p.add_argument("dist")

    p = sub.add_parser("pin", help="write a <dll>.sha256 pin")
    p.add_argument("dll")

    p = sub.add_parser("sign", help="Authenticode-sign the exe if configured")
    p.add_argument("dist")
    p.add_argument("--exe", default="SnappyAI.exe")

    args = parser.parse_args(argv)
    if args.command == "scan":
        scan_binary(args.target, args.project, args.verbose, args.reveal)
        return 0
    if args.command == "manifest":
        write_manifest(args.dist)
        return 0
    if args.command == "verify":
        return verify_manifest(args.dist)
    if args.command == "pin":
        pin_dll(args.dll)
        return 0
    if args.command == "sign":
        return 1 if sign(args.dist, args.exe) else 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
