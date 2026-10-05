"""Tiny dependency-free Ed25519 (RFC 8032) sign + verify.

Why hand-rolled: the entitlement file lives in a PUBLIC GitHub repo and
is fetched without authentication, so it must carry a signature the exe
can *verify* with a public key while only the GitHub Action ever holds
the private one. Pulling `cryptography`/PyNaCl into the frozen exe for
one signature per start is not worth it; the RFC reference arithmetic
is ~80 lines and is cross-checked against the `cryptography` package in
winsim/run_all_tests.sh (test stage 2b).

Speed is irrelevant here: one verify per app start and per re-check.
"""

import hashlib

_P = 2 ** 255 - 19
_L = 2 ** 252 + 27742317777372353535851937790883648493
_D = (-121665 * pow(121666, _P - 2, _P)) % _P


def _sha512(b):
    return hashlib.sha512(b).digest()


def _inv(x):
    return pow(x, _P - 2, _P)


def _recover_x(y, sign):
    if y >= _P:
        return None
    xx = (y * y - 1) * _inv(_D * y * y + 1)
    x = pow(xx, (_P + 3) // 8, _P)
    if (x * x - xx) % _P != 0:
        x = (x * pow(2, (_P - 1) // 4, _P)) % _P
    if (x * x - xx) % _P != 0:
        return None
    if (x & 1) != sign:
        x = _P - x
    return x


_Gy = 4 * _inv(5) % _P
_Gx = _recover_x(_Gy, 0)


def _decode_point(s):
    if len(s) != 32:
        return None
    b = bytearray(s)
    sign = b[31] >> 7
    y = int.from_bytes(b, "little") & ((1 << 255) - 1)
    x = _recover_x(y, sign)
    if x is None:
        return None
    return (x, y, 1, x * y % _P)


def _encode_point(pt):
    x, y, z, _t = pt
    if z == 0:
        return (0).to_bytes(32, "little")
    zi = _inv(z)
    x = x * zi % _P
    y = y * zi % _P
    b = (y | ((x & 1) << 255)).to_bytes(32, "little")
    return bytes(b)


def _add(p1, p2):
    x1, y1, z1, t1 = p1
    x2, y2, z2, t2 = p2
    a = (y1 - x1) * (y2 - x2) % _P
    b = (y1 + x1) * (y2 + x2) % _P
    c = 2 * t1 * t2 % _P * _D % _P
    d = 2 * z1 * z2 % _P
    e, f, g, h = b - a, d - c, d + c, b + a
    return (e * f % _P, g * h % _P, f * g % _P, e * h % _P)


def _mul(s, pt):
    out = (0, 1, 1, 0)
    while s > 0:
        if s & 1:
            out = _add(out, pt)
        pt = _add(pt, pt)
        s >>= 1
    return out


def _point_equal(a, b):
    return _encode_point(a) == _encode_point(b)


def public_from_secret(secret):
    """32-byte seed -> 32-byte public key."""
    h = _sha512(secret)
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    return _encode_point(_mul(a, (_Gx, _Gy, 1, _Gx * _Gy % _P)))


def sign(secret, message):
    """RFC 8032 pure Ed25519: 64-byte signature over message."""
    h = _sha512(secret)
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    prefix = h[32:]
    pub = _encode_point(_mul(a, (_Gx, _Gy, 1, _Gx * _Gy % _P)))
    r = int.from_bytes(_sha512(prefix + message), "little") % _L
    R = _encode_point(_mul(r, (_Gx, _Gy, 1, _Gx * _Gy % _P)))
    k = int.from_bytes(_sha512(R + pub + message), "little") % _L
    S = (r + k * a) % _L
    return R + S.to_bytes(32, "little")


def verify(pub, message, sig):
    """True only for a valid 64-byte signature under pub."""
    try:
        if len(sig) != 64 or len(pub) != 32:
            return False
        A = _decode_point(pub)
        if A is None:
            return False
        R = _decode_point(sig[:32])
        if R is None:
            return False
        S = int.from_bytes(sig[32:], "little")
        if S >= _L:
            return False
        k = int.from_bytes(_sha512(sig[:32] + pub + message),
                           "little") % _L
        left = _mul(S, (_Gx, _Gy, 1, _Gx * _Gy % _P))
        right = _add(R, _mul(k, A))
        return _point_equal(left, right)
    except Exception:
        return False
