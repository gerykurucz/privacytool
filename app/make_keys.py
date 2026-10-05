#!/usr/bin/env python3
"""One-time Ed25519 keypair generator for the entitlements pipeline.

    python make_keys.py

Prints:
    ED25519_SECRET  -> GitHub repo secret of the PRIVATE controller repo
    entitlement_pubkey -> value for the app's config.json
                          (and nothing else; the public key is safe
                          everywhere - it only VERIFIES)

The private seed never leaves your hands: it lives in repo secrets and
signs entitlements.json from GitHub Actions only.
"""

import base64
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
# edsig.py sits beside this file in the controller repo; fall back to the
# app/ folder of the full project tree.
sys.path.insert(0, os.path.join(_HERE, "..", "..", "app"))
sys.path.insert(0, _HERE)
import edsig  # noqa: E402


def main():
    seed = os.urandom(32)
    pub = edsig.public_from_secret(seed)
    print("ED25519_SECRET (repo secret)      : %s" % seed.hex())
    print("entitlement_pubkey (config.json)  : %s"
          % base64.b64encode(pub).decode("ascii"))
    print("")
    print("Self-check signature over b'snappyai': %s"
          % base64.b64encode(edsig.sign(seed, b"snappyai")).decode()[:44]
          + "...")
    ok = edsig.verify(pub, b"snappyai",
                      base64.b64decode(base64.b64encode(
                          edsig.sign(seed, b"snappyai")).decode()))
    print("verify(pub, msg, sig)             : %s" % ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
