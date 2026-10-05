"""Encode (or decode) a build_secrets.py _BLOB value.

build_secrets.py obfuscates deployment constants with XOR(sha256(_KEY)) +
base64. This helper produces those blob strings so you never have to touch
the arithmetic by hand — e.g. after rotating the Discord client secret.

Usage (any terminal, no dependencies):

    # encode: prints the exact line to paste into _BLOB
    python encode_secret.py DISCORD_CLIENT_SEC "the-new-plaintext-secret"

    # decode: shows what a blob value currently holds (sanity check)
    python encode_secret.py --decode ENTITLEMENT_PUBKEY "4lqKf9of1F8uhwq51I4RV3lsHynUlVzQYDeaQqkkf1LuD5tmkRbUIiOYNc0="

    # decode everything in build_secrets.py next to this file
    python encode_secret.py --dump

Reminder: this is OBFUSCATION, not encryption (the key ships in the exe).
Its job is keeping credentials out of `strings` output, config.json and
casual scraping — see the build_secrets.py docstring for the threat model.
"""

import base64
import hashlib
import sys

# MUST stay identical to build_secrets.py, or blobs won't decode there.
_KEY = b"SnappyAI/build-secrets/v1"
_ks = hashlib.sha256(_KEY).digest()


def encode(plaintext: str) -> str:
    data = plaintext.encode("utf-8")
    return base64.b64encode(
        bytes(c ^ _ks[i % len(_ks)] for i, c in enumerate(data))
    ).decode("ascii")


def decode(blob: str) -> str:
    data = base64.b64decode(blob)
    return bytes(c ^ _ks[i % len(_ks)] for i, c in enumerate(data)).decode("utf-8")


def _dump() -> None:
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import build_secrets
    for name, raw in sorted(build_secrets._BLOB.items()):
        shown = decode(raw) if raw else "(empty)"
        if "SEC" in name or "WEBHOOK" in name:
            # mask the middle of anything credential-shaped
            shown = shown[:4] + "..." + shown[-4:] if len(shown) > 12 else "(set)"
        print(f"  {name:22s} = {shown}")


def main(argv):
    if len(argv) == 2 and argv[1] == "--dump":
        _dump()
        return 0
    if len(argv) == 4 and argv[1] == "--decode":
        print(decode(argv[3]))
        return 0
    if len(argv) == 3:
        name, plaintext = argv[1], argv[2]
        blob = encode(plaintext)
        # round-trip check before handing it over
        assert decode(blob) == plaintext, "round-trip failed"
        print(f'    "{name}": "{blob}",')
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
