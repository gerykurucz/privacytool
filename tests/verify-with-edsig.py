#!/usr/bin/env python3
"""Verify a Worker-signed entitlements.json with the client's OWN edsig.py.

This is the check that would otherwise only fail in production, in front of
every customer at once: if the Worker's canonicalisation or signature differs by
one byte from what edsig.py expects, every shipped exe rejects the file and the
symptom is a total lockout that looks like a server outage.

It deliberately uses the UNMODIFIED edsig.py from the backend repo -- the same
module that ships inside the exe -- and reproduces online.py's exact verification
path: recompute the canonical bytes from the signed document, then verify.

    python3 test/verify-with-edsig.py [path-to-interop-json]

Prints ALL OK on success and exits 0; any failure prints the reason and exits 1.
"""

from __future__ import annotations

import base64
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
CANDIDATES = [
    # v14 archive layout: the client's own edsig.py, the exact module that ships
    # inside the exe, lives in src/app/.
    HERE.parent / "src" / "app" / "edsig.py",
    # older archive layouts, kept so the script still works if unpacked elsewhere
    HERE.parent.parent / "edsig.py",
    HERE.parent.parent.parent / "merged" / "snappyai-backend" / "edsig.py",
    HERE.parent.parent.parent / "snappyai-backend" / "edsig.py",
    HERE.parent / "edsig.py",
]

edsig_path = next((p for p in CANDIDATES if p.is_file()), None)
if edsig_path is None:
    print("FAIL: could not locate edsig.py; looked in:")
    for p in CANDIDATES:
        print("   ", p)
    sys.exit(1)

sys.path.insert(0, str(edsig_path.parent))
import edsig  # noqa: E402

payload_path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/publisher-interop.json")
data = json.loads(payload_path.read_text())

pub = base64.b64decode(data["pubkey_b64"])
doc = data["signed_doc"]
sig = base64.b64decode(doc["sig"])

# Exactly what online._canonical_bytes does: sorted keys, compact separators,
# `sig` excluded.
payload = {k: v for k, v in doc.items() if k != "sig"}
canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

checks = []

checks.append(("public key is 32 bytes", len(pub) == 32))
checks.append(("signature is 64 bytes", len(sig) == 64))
checks.append(("document carries a row", bool(doc.get("rows"))))
checks.append(("edsig.verify(pub, canonical, sig)", edsig.verify(pub, canonical, sig)))

# And the derived public key must match, so a rotated seed is caught here too.
if data.get("seed_hex"):
    derived = edsig.public_from_secret(bytes.fromhex(data["seed_hex"]))
    checks.append(("edsig.public_from_secret(seed) == pubkey", derived == pub))

# A tampered document must NOT verify -- otherwise the check above proves nothing.
tampered = dict(doc)
tampered["generated_at"] = int(doc.get("generated_at", 0)) + 1
t_payload = {k: v for k, v in tampered.items() if k != "sig"}
t_canonical = json.dumps(t_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
checks.append(
    ("tampered document is REJECTED", not edsig.verify(pub, t_canonical, sig))
)

failed = False
for label, ok in checks:
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}")
    failed = failed or not ok

if failed:
    print("NOT OK")
    sys.exit(1)
print("ALL OK")
