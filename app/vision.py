
import functools
import math
import threading
import time

import numpy as np

from colorspec import (ACCENT_PRESETS,
                        hsv_to_rgb,
                        parse_accent as _parse_accent,
                        parse_accents as _parse_accents)







_LOG_SINK = None

try:



    from win32rt import get_dpi_scale as _get_dpi_scale
except Exception:
    _get_dpi_scale = None


def set_log_sink(fn):
    global _LOG_SINK
    _LOG_SINK = fn if callable(fn) else None


def _log(text):
    fn = _LOG_SINK
    if fn is None:
        return
    try:
        fn(text)
    except Exception:
        pass

_CH_WEIGHTS = np.array([0.114, 0.587, 0.299], dtype=np.float32)
_SCAN_DEADLINE = threading.local()

CS = 4
CELL_SOLID = 0.28
CELL_WEAK = 0.18
BLUR_WIN = 9
MIN_FILL = 0.45










NORM_C = 24.0
NORM_K = 152.0
NORM_MIN = 0.5
NORM_MAX = 3.0









ADAPTIVE_PERCENTILE = 98.0
ADAPTIVE_K = 0.5
ADAPTIVE_FLOOR = 14.0
ADAPTIVE_BASE = 38.0



MIN_CONTRAST_FLOOR = 28.0







MIN_CONTRAST_BASE = 48.0








CONTRAST_CORE_FRAC = 0.35
CONTRAST_METRIC_SCALE = 0.83


class SnapTarget(object):
    __slots__ = ("dx", "dy", "dist", "area", "contrast", "bw", "bh", "sig")

    def __init__(self, dx, dy, dist, area, contrast, bw, bh, sig=None):
        self.dx = dx
        self.dy = dy
        self.dist = dist
        self.area = area
        self.contrast = contrast
        self.bw = bw
        self.bh = bh
        self.sig = sig


class ScanResult(object):
    __slots__ = ("kind", "target", "ms")

    def __init__(self, kind, target=None, ms=0.0):
        self.kind = kind
        self.target = target
        self.ms = ms


def _box_blur(a, win):
    try:
        import cv2
        return cv2.blur(a, (int(win), int(win)),
                        borderType=cv2.BORDER_REPLICATE)
    except Exception:
        pass
    r = win // 2
    h, w, _ = a.shape
    p = np.pad(a, ((r, r), (r, r), (0, 0)), mode="edge")
    c = p.cumsum(axis=0).cumsum(axis=1)
    c = np.pad(c, ((1, 0), (1, 0), (0, 0)))
    total = (
        c[win:win + h, win:win + w]
        - c[:h, win:win + w]
        - c[win:win + h, :w]
        + c[:h, :w]
    )
    return total / float(win * win)


def _dilate(m, n=1):
    for _ in range(n):
        o = m.copy()
        o[1:, :] |= m[:-1, :]
        o[:-1, :] |= m[1:, :]
        o[:, 1:] |= m[:, :-1]
        o[:, :-1] |= m[:, 1:]
        m = o
    return m


def _erode(m, n=1):






    for _ in range(n):
        o = m.copy()
        o[1:, :] &= m[:-1, :]
        o[:-1, :] &= m[1:, :]
        o[:, 1:] &= m[:, :-1]
        o[:, :-1] &= m[:, 1:]
        o[0, :] = False
        o[-1, :] = False
        o[:, 0] = False
        o[:, -1] = False
        m = o
    return m


def _dilate8(m):
    o = m.copy()
    o[1:, :] |= m[:-1, :]
    o[:-1, :] |= m[1:, :]
    o[:, 1:] |= m[:, :-1]
    o[:, :-1] |= m[:, 1:]
    o[1:, 1:] |= m[:-1, :-1]
    o[1:, :-1] |= m[:-1, 1:]
    o[:-1, 1:] |= m[1:, :-1]
    o[:-1, :-1] |= m[1:, 1:]
    return o


def _close_gaps(m, gap):
    try:
        g = int(float(gap))
    except (TypeError, ValueError):
        return m
    if g <= 0:
        return m
    g = min(g, min(m.shape) // 2 - 1)
    if g <= 0:
        return m
    try:
        import cv2
        se = np.ones((2 * g + 1, 2 * g + 1), np.uint8)
        e = cv2.morphologyEx(m.astype(np.uint8),
                             cv2.MORPH_CLOSE, se).astype(bool)
    except Exception:



        return m



    e[:g, :] = False
    e[-g:, :] = False
    e[:, :g] = False
    e[:, -g:] = False
    return e


def _meanshift(xs, ys, sx, sy, sigma=25.0, iters=8):
    px, py = float(sx), float(sy)
    inv2s2 = 1.0 / (2.0 * sigma * sigma)

    for _ in range(iters):
        w = np.exp(-(((xs - px) ** 2 + (ys - py) ** 2) * inv2s2))
        sw = float(w.sum())
        if sw < 1e-3:
            return None

        nx = float((xs * w).sum() / sw)
        ny = float((ys * w).sum() / sw)
        moved = abs(nx - px) + abs(ny - py)
        px, py = nx, ny

        if moved < 0.4:
            break

    return px, py


def _grow_cells(strong, weak):
    keep = strong.copy()
    for i in range(256):
        grown = _dilate8(keep) & weak
        grown |= keep
        if np.array_equal(grown, keep):
            return keep
        keep = grown
        if (i & 31) == 31 and time.perf_counter() > getattr(_SCAN_DEADLINE, 'deadline', float('inf')):
            return keep
    return keep


def _flood_bg(solids, mask):
    gh, gw = solids.shape
    free = mask & ~solids
    bg = np.zeros((gh, gw), dtype=bool)
    if not free.any():
        return bg

    border = np.zeros((gh, gw), dtype=bool)
    border[0, :] = True
    border[gh - 1, :] = True
    border[:, 0] = True
    border[:, gw - 1] = True
    seed = free & (border | _dilate8(~mask))
    if not seed.any():
        return bg
    bg = seed.copy()

    for i in range(256):
        g = bg.copy()
        g[1:, :] |= bg[:-1, :]
        g[:-1, :] |= bg[1:, :]
        g[:, 1:] |= bg[:, :-1]
        g[:, :-1] |= bg[:, 1:]
        g &= free
        if np.array_equal(g, bg):
            return bg
        bg = g
        if (i & 31) == 31 and time.perf_counter() > getattr(_SCAN_DEADLINE, 'deadline', float('inf')):
            return bg
    return bg


def _label_cells(cells):
    gh, gw = cells.shape
    labels = np.zeros((gh, gw), dtype=np.int32)
    runs_y = []
    runs_x0 = []
    runs_x1 = []
    parent = []

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            if ra < rb:
                parent[rb] = ra
            else:
                parent[ra] = rb

    prev = []
    for y in range(gh):
        xs = np.flatnonzero(cells[y])
        if xs.size == 0:
            prev = []
            continue
        jumps = np.flatnonzero(np.diff(xs) > 1)
        starts = np.concatenate(([xs[0]], xs[jumps + 1]))
        ends = np.concatenate((xs[jumps] + 1, [xs[-1] + 1]))
        cur = []
        for x0, x1 in zip(starts, ends):
            rid = len(parent)
            parent.append(rid)
            runs_y.append(y)
            runs_x0.append(int(x0))
            runs_x1.append(int(x1))
            cur.append((int(x0), int(x1), rid))
            for px0, px1, prid in prev:
                if px0 <= x1 and x0 <= px1:
                    union(rid, prid)
        prev = cur

    nruns = len(parent)
    if nruns == 0:
        return labels, []
    roots = np.empty(nruns, dtype=np.int32)
    for r in range(nruns):
        roots[r] = find(r)

    order = {}
    for r in range(nruns):
        rt = roots[r]
        if rt not in order:
            order[rt] = len(order) + 1
    comp = np.empty(nruns, dtype=np.int32)
    for r in range(nruns):
        comp[r] = order[roots[r]]
    ncomp = len(order)

    ry = np.asarray(runs_y, dtype=np.int32)
    rx0 = np.asarray(runs_x0, dtype=np.int32)
    rx1 = np.asarray(runs_x1, dtype=np.int32)
    for k in range(nruns):
        labels[ry[k], rx0[k]:rx1[k]] = comp[k]

    lengths = (rx1 - rx0).astype(np.int64)
    counts = np.zeros(ncomp + 1, dtype=np.int64)
    np.add.at(counts, comp, lengths)
    y0 = np.full(ncomp + 1, gh, dtype=np.int32)
    y1 = np.zeros(ncomp + 1, dtype=np.int32)
    x0 = np.full(ncomp + 1, gw, dtype=np.int32)
    x1 = np.zeros(ncomp + 1, dtype=np.int32)
    np.minimum.at(y0, comp, ry)
    np.maximum.at(y1, comp, ry)
    np.minimum.at(x0, comp, rx0)
    np.maximum.at(x1, comp, rx1 - 1)
    info = [(i, int(counts[i]), int(y0[i]), int(x0[i]), int(y1[i]) + 1,
             int(x1[i]) + 1) for i in range(1, ncomp + 1)]
    return labels, info


MIN_FRAG_AREA = 64


















AREA_SCORE_CAP = 6000.0
DIST_FALLOFF = 2.0







PROX_CORE_PX = 24.0
PROX_CORE_BONUS = 0.5


def _prox_mult(dist):
    if dist >= PROX_CORE_PX:
        return 1.0
    return 1.0 + PROX_CORE_BONUS * (1.0 - dist / PROX_CORE_PX)

















SHAPE_LO = 1.2
SHAPE_PLATEAU_LO = 1.6
SHAPE_PLATEAU_HI = 2.4
SHAPE_HI = 3.0
SHAPE_BONUS = 0.6
SHAPE_SQ_LO = 0.75
SHAPE_SQ_HI = 1.33
SHAPE_SQ_BONUS = 0.3
SHAPE_MIN_H = 24
SHAPE_MIN_AREA = 200



SHAPE_TIER_MIN_F = 0.25


def _shape_mult(bw, bh, area):
    if bw <= 0 or bh < SHAPE_MIN_H or area < SHAPE_MIN_AREA:
        return 1.0
    r = float(bh) / float(bw)
    best = 1.0
    if SHAPE_LO < r < SHAPE_HI:
        if r < SHAPE_PLATEAU_LO:
            f = (r - SHAPE_LO) / (SHAPE_PLATEAU_LO - SHAPE_LO)
        elif r <= SHAPE_PLATEAU_HI:
            f = 1.0
        else:
            f = (SHAPE_HI - r) / (SHAPE_HI - SHAPE_PLATEAU_HI)
        best = max(best, 1.0 + SHAPE_BONUS * f)
    if SHAPE_SQ_LO < r < SHAPE_SQ_HI:
        if r <= 1.0:
            f = (r - SHAPE_SQ_LO) / (1.0 - SHAPE_SQ_LO)
        else:
            f = (SHAPE_SQ_HI - r) / (SHAPE_SQ_HI - 1.0)
        best = max(best, 1.0 + SHAPE_SQ_BONUS * f)
    return best


def _shape_tier(bw, bh, area):
    if bw <= 0 or bh < SHAPE_MIN_H or area < SHAPE_MIN_AREA:
        return 0
    r = float(bh) / float(bw)
    if SHAPE_LO < r < SHAPE_HI:
        if r < SHAPE_PLATEAU_LO:
            f = (r - SHAPE_LO) / (SHAPE_PLATEAU_LO - SHAPE_LO)
        elif r <= SHAPE_PLATEAU_HI:
            f = 1.0
        else:
            f = (SHAPE_HI - r) / (SHAPE_HI - SHAPE_PLATEAU_HI)



        if f >= SHAPE_TIER_MIN_F:
            return 2
    if SHAPE_SQ_LO < r < SHAPE_SQ_HI:
        if r <= 1.0:
            f = (r - SHAPE_SQ_LO) / (1.0 - SHAPE_SQ_LO)
        else:
            f = (SHAPE_SQ_HI - r) / (SHAPE_SQ_HI - 1.0)
        if f >= SHAPE_TIER_MIN_F:
            return 1
    return 0






EXCLUDE_ERODE_PX = 5
EXCLUDE_CORE_MIN = 8








ACCENT_RANK_CAP = 1.2


def _base_score(contrast, area, fill, dist, shape=1.0):
    return (contrast * math.sqrt(min(area, AREA_SCORE_CAP))
            * (0.4 + 0.6 * fill) * _prox_mult(dist) * shape
            / (12.0 + dist) ** DIST_FALLOFF)




ACCENT_MIN_FRACTION = 0.05











ACCENT_STRONG_SIM = 0.55
ACCENT_TONE_BONUS = 0.25


FOLLOW_COLOR_TOL = 18
FOLLOW_COLOR_FRAC = 0.25
FOLLOW_POS_SIM = 0.8

FOLLOW_POS_PAD = 48


class FollowMemory(object):

    def __init__(self):
        import threading as _th
        self._lock = _th.Lock()
        self.when = 0.0
        self.x = 0
        self.y = 0
        self.sig = None
        self.area = 0
        self.bw = 0
        self.bh = 0
        self.hits = 0

    def store(self, x, y, target):




        with self._lock:
            self.when = time.perf_counter()
            self.x, self.y = int(x), int(y)
            self.sig = getattr(target, "sig", None)
            self.area = getattr(target, "area", 0)
            self.bw = getattr(target, "bw", 0)
            self.bh = getattr(target, "bh", 0)
            self.hits += 1

    def context(self, origin_x, origin_y, follow_seconds):
        with self._lock:
            when, x, y = self.when, self.x, self.y
            sig = self.sig
        if when <= 0.0:
            return None

        age = time.perf_counter() - when
        if follow_seconds <= 0 or age > follow_seconds:
            return None

        decay = max(0.0, 1.0 - age / float(follow_seconds))
        return (sig, x - int(origin_x), y - int(origin_y), decay)


def _merge_nearby(candidates, fragments, merge_distance,
                  min_area, max_area, max_dim, max_aspect, scale=1.0,
                  cx=None, cy=None, w=None, h=None, edge_flags=None,
                  deadline=None):


    pool = list(candidates) + list(fragments)
    n_full = len(candidates)
    n = len(pool)

    if n == 0:
        return candidates
    if n == 1:

        return candidates




    boxes = [(c[2], c[1], c[2] + c[7], c[1] + c[8]) for c in pool]

    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[rj] = ri

    for i in range(n):



        if deadline is not None and i > 0 \
                and time.perf_counter() > deadline:
            break
        ax0, ay0, ax1, ay1 = boxes[i]
        for j in range(i + 1, n):
            bx0, by0, bx1, by1 = boxes[j]
            gap_x = max(ax0 - bx1, bx0 - ax1, 0)
            gap_y = max(ay0 - by1, by0 - ay1, 0)


            if math.hypot(gap_x, gap_y) <= merge_distance:
                union(i, j)

    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)

    out = []

    for members in groups.values():
        full_members = [pool[m] for m in members if m < n_full]

        if len(members) == 1:
            if members[0] < n_full:
                out.append(pool[members[0]])
            continue




        if all(m < n_full for m in members):
            out.extend(full_members)
            continue

        X0 = min(boxes[m][0] for m in members)
        Y0 = min(boxes[m][1] for m in members)
        X1 = max(boxes[m][2] for m in members)
        Y1 = max(boxes[m][3] for m in members)
        bw, bh = X1 - X0, Y1 - Y0




        if w is not None and h is not None \
                and _touches_screen_edge(Y0, X0, Y1, X1, w, h,
                                         edge_flags):
            dim_cap = max_dim * 2
            aspect_cap = max_aspect * 2.5
        else:
            dim_cap = max_dim
            aspect_cap = max_aspect
        shape_ok = (
            max(bw, bh) <= dim_cap
            and max(bw, bh) <= aspect_cap * max(1, min(bw, bh))
        )

        if not shape_ok:
            out.extend(full_members)
            continue

        canvas = np.zeros((bh, bw), dtype=bool)
        contrast = 0.0

        for m in members:
            _s, mY0, mX0, cl, _d, _a, ct, mbw, mbh = pool[m]
            oy, ox = mY0 - Y0, mX0 - X0
            dst = canvas[oy:oy + mbh, ox:ox + mbw]
            np.logical_or(dst, cl[:dst.shape[0], :dst.shape[1]], out=dst)
            contrast = max(contrast, ct)

        area = int(canvas.sum())

        if area < min_area or area > max_area:
            out.extend(full_members)
            continue

        fill = area / float(bw * bh)




        if fill < MIN_FILL:
            out.extend(full_members)
            continue

        if cx is not None and cy is not None:



            dist = math.hypot(max(X0 - cx, 0, cx - (X1 - 1)),
                              max(Y0 - cy, 0, cy - (Y1 - 1)))
        else:
            dist = min(pool[m][4] for m in members)
        score = _base_score(contrast, area, fill, dist,
                            shape=_shape_mult(bw, bh, area))
        out.append((score, Y0, X0, canvas, dist, area, contrast, bw, bh))

    return out










__all__ = [
    "ACCENT_PRESETS", "AREA_SCORE_CAP", "CONTRAST_METRIC_SCALE",
    "DIST_FALLOFF", "FollowMemory", "MotionTracker", "ScanResult",
    "SnapTarget", "_accent_fraction", "_accent_stats", "_parse_accent",
    "_parse_accents", "_sig_matches_accents", "accent_coherent_of",
    "accent_matcher_of", "accent_soft_of", "accent_variants_of",
    "blend_similarity", "calibrate_accent", "ciede2000",
    "color_adapt_of", "hsv_to_rgb", "motion_sense_of", "parse_accent",
    "parse_accents", "predict_motion", "scan_region", "set_log_sink",
    "suggest_accents",
]


def _soft_band(d, half, falloff):
    if falloff <= 0:
        return np.where(d <= half, 1.0, 0.0)
    return np.clip(1.0 - (d - half) / falloff, 0.0, 1.0)


def _accent_similarity(h, s, v, ah, asat, av, tol, soft=0.0):
    dh = np.abs(h - ah)
    dh = np.minimum(dh, 180.0 - dh)

    sv_band = tol * 2.2
    h_sim = _soft_band(dh, tol, tol * 2.0 * soft)
    s_sim = _soft_band(np.abs(s - asat), sv_band, sv_band * 2.0 * soft)
    v_sim = _soft_band(np.abs(v - av), sv_band, sv_band * 2.0 * soft)


    rel = min(1.0, float(asat) / 50.0)
    h_sim = h_sim * rel + (1.0 - rel)

    sim = (h_sim ** 0.50) * (s_sim ** 0.20) * (v_sim ** 0.30)

    if soft > 0:
        sim = sim + ACCENT_TONE_BONUS * soft * s_sim * v_sim \
            * (1.0 - h_sim)

    return np.minimum(sim, 1.0)












OKLAB_BLEND_MIN_A = 0.25
OKLAB_BLEND_EPS = 0.05


def _rgb01_to_oklab(px):
    def lin(c):
        return np.where(c <= 0.04045, c / 12.92,
                        ((c + 0.055) / 1.055) ** 2.4)

    r, g, b = lin(px[..., 0]), lin(px[..., 1]), lin(px[..., 2])
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = np.cbrt(l), np.cbrt(m), np.cbrt(s)
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    A = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    B = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return np.stack([L, A, B], axis=-1)


def blend_similarity(px_bgr01, acc_rgb01, bg_bgr01):
    acc = np.asarray(acc_rgb01, dtype=np.float32)[::-1]
    bg = np.asarray(bg_bgr01, dtype=np.float32)
    d = acc - bg
    denom = float(np.dot(d, d))
    if denom < 1e-4:
        return np.zeros(px_bgr01.shape[:-1], dtype=np.float32)
    t = np.sum((px_bgr01 - bg) * d, axis=-1) / denom
    proj = bg + t[..., None] * d
    res = np.sqrt(np.sum((px_bgr01 - proj) ** 2, axis=-1))


    return np.where((t >= OKLAB_BLEND_MIN_A) & (res <= OKLAB_BLEND_EPS),
                    np.minimum(t, 1.0), 0.0).astype(np.float32)
































DE_TOL_BASE = 4.0
DE_TOL_SOFT = 32.0










ACCENT_L_VARIANTS = (0.0, 7.0, -7.0, 14.0, -14.0)
HSV_V_VARIANTS = (0.0, 18.0, -18.0, 36.0, -36.0)








ADAPT_MAX_AB = 10.0
ADAPT_STRENGTH = 0.6






ACCENT_COHERENT_FRAC = 0.5
ACCENT_COHERENT_MIN = 8






ACCENT_MAX_PIXELS = 3000

_lab_cache = {}





_accent_parse_cache = {}
_exclude_parse_cache = {}


def _cached_parse_accents(raw):
    key = ("s", raw) if isinstance(raw, str) else ("r", repr(raw))
    hit = _accent_parse_cache.get(key)
    if hit is None:
        if len(_accent_parse_cache) > 32:
            _accent_parse_cache.clear()
        hit = _parse_accents(raw)
        _accent_parse_cache[key] = hit
    return hit


def _rgb01_to_lab(px):
    def lin(c):
        return np.where(c <= 0.04045, c / 12.92,
                        ((c + 0.055) / 1.055) ** 2.4)

    r, g, b = lin(px[..., 0]), lin(px[..., 1]), lin(px[..., 2])
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047
    y = (0.2126729 * r + 0.7151522 * g + 0.0721750 * b)
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883

    def f(t):
        return np.where(t > 0.008856, np.cbrt(np.maximum(t, 1e-12)),
                        7.787 * t + 16.0 / 116.0)

    fx, fy, fz = f(x), f(y), f(z)
    L = 116.0 * fy - 16.0
    A = 500.0 * (fx - fy)
    B = 200.0 * (fy - fz)
    return np.stack([L, A, B], axis=-1)


@functools.lru_cache(maxsize=128)
def _accent_lab_quantised(ah, asat, av):
    rgb = np.array(hsv_to_rgb(ah, asat, av), dtype=np.float32) / 255.0
    lab = _rgb01_to_lab(rgb)
    hit = (lab, float(np.hypot(lab[1], lab[2])), rgb)
    return hit


def _accent_lab(ah, asat, av):
    """Lab/rgb of an accent, cached on a 2-decimal quantisation of the HSV
    triple: the caller's hues jitter in the low bits, and caching the raw
    floats turned a 128-entry cache into a miss on every call."""
    return _accent_lab_quantised(round(float(ah), 2), round(float(asat), 2),
                                 round(float(av), 2))


def ciede2000(lab1, lab2, kL=1.0, kC=1.0, kH=1.0):
    L1, a1, b1 = lab1[..., 0], lab1[..., 1], lab1[..., 2]
    L2, a2, b2 = lab2[..., 0], lab2[..., 1], lab2[..., 2]

    C1 = np.hypot(a1, b1)
    C2 = np.hypot(a2, b2)
    Cb = 0.5 * (C1 + C2)
    c7 = Cb ** 7
    G = 0.5 * (1.0 - np.sqrt(c7 / (c7 + 25.0 ** 7)))

    a1p = a1 * (1.0 + G)
    a2p = a2 * (1.0 + G)
    C1p = np.hypot(a1p, b1)
    C2p = np.hypot(a2p, b2)

    h1p = np.arctan2(b1, a1p) % (2.0 * np.pi)
    h2p = np.arctan2(b2, a2p) % (2.0 * np.pi)

    dLp = L2 - L1
    dCp = C2p - C1p




    h_diff = h2p - h1p
    dhp = np.where(h_diff > np.pi, h_diff - 2.0 * np.pi, h_diff)
    dhp = np.where(h_diff < -np.pi, dhp + 2.0 * np.pi, dhp)
    cc = C1p * C2p
    dhp = np.where(cc == 0.0, 0.0, dhp)
    dHp = 2.0 * np.sqrt(np.maximum(cc, 0.0)) * np.sin(dhp / 2.0)

    Lbp = 0.5 * (L1 + L2)
    Cbp = 0.5 * (C1p + C2p)

    hsum = h1p + h2p
    hbp = np.where(np.logical_and(cc != 0.0, np.abs(h_diff) > np.pi),
                   np.where(hsum < 2.0 * np.pi, hsum + 2.0 * np.pi,
                            hsum - 2.0 * np.pi),
                   hsum) * 0.5

    T = (1.0
         - 0.17 * np.cos(hbp - np.deg2rad(30.0))
         + 0.24 * np.cos(2.0 * hbp)
         + 0.32 * np.cos(3.0 * hbp + np.deg2rad(6.0))
         - 0.20 * np.cos(4.0 * hbp - np.deg2rad(63.0)))
    tmp = (Lbp - 50.0) ** 2
    SL = 1.0 + 0.015 * tmp / np.sqrt(20.0 + tmp)
    SC = 1.0 + 0.045 * Cbp
    SH = 1.0 + 0.015 * Cbp * T

    dRo = 30.0 * np.exp(-((np.rad2deg(hbp) - 275.0) / 25.0) ** 2)
    c7b = Cbp ** 7
    Rc = 2.0 * np.sqrt(c7b / (c7b + 25.0 ** 7))
    RT = -np.sin(2.0 * np.deg2rad(dRo)) * Rc

    dE2 = ((dLp / (kL * SL)) ** 2 + (dCp / (kC * SC)) ** 2
           + (dHp / (kH * SH)) ** 2
           + RT * (dCp / (kC * SC)) * (dHp / (kH * SH)))
    return np.sqrt(np.maximum(dE2, 0.0)).astype(np.float32)


def _de_terms(p_lab, acc_lab, neutral_chroma=None):
    d = ciede2000(p_lab, acc_lab)
    if neutral_chroma is not None and neutral_chroma < 8.0:
        cpx = np.hypot(p_lab[..., 1], p_lab[..., 2])
        extra = 2.0 * np.clip(cpx - (neutral_chroma + 1.5), 0.0, None)
        d = np.sqrt(d * d + extra * extra)
    return d


def _coherent_enough(mask, min_n=ACCENT_COHERENT_MIN):
    n = int(mask.sum())
    if n < min_n:
        return True
    _labels, info = _label_cells(mask)
    if not info:
        return False
    biggest = max(entry[1] for entry in info)
    return biggest >= ACCENT_COHERENT_FRAC * n


def _subsample_patch(sub_f32, mask):
    while int(mask.sum()) > ACCENT_MAX_PIXELS:
        h, w = mask.shape
        h2, w2 = (h // 2) * 2, (w // 2) * 2
        if h2 < 2 or w2 < 2:
            break
        s = sub_f32[:h2, :w2].reshape(h2 // 2, 2, w2 // 2, 2, 3)
        s = s.mean(axis=(1, 3))
        m = mask[:h2, :w2].reshape(h2 // 2, 2, w2 // 2, 2)
        m = m.mean(axis=(1, 3)) >= 0.5
        if not m.any():
            break
        sub_f32 = s.astype(np.float32)
        mask = m
    return sub_f32, mask

def accent_soft_of(cfgv):
    try:
        return min(1.0, max(0.0, float(cfgv.get("accent_soft", 60)) / 100.0))
    except (TypeError, ValueError):
        return 0.6


def accent_matcher_of(cfgv):
    try:
        m = str(cfgv.get("accent_matcher", "oklab") or "oklab")
    except (TypeError, ValueError):
        return "oklab"
    m = m.strip().lower()
    return m if m in ("hsv", "oklab") else "oklab"


def _bool_of(cfgv, key, default):
    try:
        v = cfgv.get(key, default)
    except (TypeError, ValueError, AttributeError):
        return bool(default)
    if isinstance(v, str):
        return v.strip().lower() in ("1", "true", "yes", "on")
    return bool(v)


def color_adapt_of(cfgv):
    return _bool_of(cfgv, "color_adapt", True)


def accent_variants_of(cfgv):
    return _bool_of(cfgv, "accent_variants", True)


def accent_coherent_of(cfgv):
    return _bool_of(cfgv, "accent_coherent", True)


def suggest_accents(img, max_suggestions=6):
    a = np.asarray(img)
    if a.ndim != 3 or a.shape[2] < 3 or a.size == 0:
        return []

    h, w = a.shape[:2]
    step = max(1, int(np.sqrt(float(h * w) / 24000.0)))
    a = a[::step, ::step, :3]
    px01 = a.astype(np.float32)[..., ::-1] / 255.0
    lab = _rgb01_to_oklab(px01).reshape(-1, 3)
    rgb = px01.reshape(-1, 3)

    q = np.stack([np.round(lab[:, 0] / 0.05),
                  np.round(lab[:, 1] / 0.04),
                  np.round(lab[:, 2] / 0.04)], axis=1)
    keys, inv, counts = np.unique(q, axis=0, return_inverse=True,
                                  return_counts=True)
    inv = inv.ravel()
    total = max(float(len(inv)), 1.0)

    sums = np.stack([np.bincount(inv, weights=rgb[:, c],
                                 minlength=len(counts))
                     for c in range(3)], axis=1)
    means = sums / np.maximum(counts, 1)[:, None]

    chroma = np.hypot(keys[:, 1] * 0.04, keys[:, 2] * 0.04)
    rank = (counts / total) * (0.25 + np.minimum(chroma, 0.25) * 3.0)
    order = np.argsort(-rank)




    out = []
    fallback = []
    for idx in order:
        m = means[idx]
        item = ((int(round(float(m[0]) * 255.0)),
                 int(round(float(m[1]) * 255.0)),
                 int(round(float(m[2]) * 255.0))),
                float(counts[idx]) / total)
        (out if chroma[idx] >= 0.03 else fallback).append(item)
        if len(out) >= max(1, int(max_suggestions)):
            break
    while len(out) < max(1, int(max_suggestions)) and fallback:
        out.append(fallback.pop(0))
    return out[:max(1, int(max_suggestions))]


def _sig_matches_accents(sig, accents, tol, soft=0.0, matcher="hsv",
                         variants=True):
    if sig is None or not accents:
        return False

    sh, ss, sv = float(sig[0]), float(sig[1]), float(sig[2])

    if matcher == "oklab" and soft > 0:
        rgb01 = (np.array(hsv_to_rgb(sh, ss, sv), dtype=np.float32)
                 / 255.0)
        sig_lab = _rgb01_to_lab(rgb01)
        tol_e = (DE_TOL_BASE
                 + DE_TOL_SOFT * max(0.0, min(1.0, float(soft)))) \
            * max(0.15, min(3.5, float(tol) / 26.0))
        for (ah, asat, av) in accents:
            lab, chroma, _ = _accent_lab(ah, asat, av)
            best = None
            for dL in (ACCENT_L_VARIANTS if variants else (0.0,)):
                d = float(_de_terms(sig_lab,
                                    lab + np.array(
                                        [dL, 0.0, 0.0], dtype=np.float32),
                                    chroma))
                best = d if best is None else min(best, d)



            if best <= (1.0 - ACCENT_STRONG_SIM) * tol_e:
                return True
        return False







    for (ah, asat, av) in accents:
        for dV in (HSV_V_VARIANTS if variants else (0.0,)):
            vv = min(255.0, max(0.0, av + dV))
            sim = float(_accent_similarity(sh, ss, sv, ah, asat, vv, tol,
                                           soft))
            if sim >= ACCENT_STRONG_SIM:
                return True

    return False


def _bgr01_to_hsv(px):
    b, g, r = px[:, 0], px[:, 1], px[:, 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    d = mx - mn
    safe_d = np.where(d > 0, d, 1.0)
    h_r = ((g - b) / safe_d) % 6.0
    h_g = ((b - r) / safe_d) + 2.0
    h_b = ((r - g) / safe_d) + 4.0
    h = np.where(d == 0, 0.0,
                 np.where(mx == r, h_r, np.where(mx == g, h_g, h_b))) * 30.0
    h %= 180.0
    s = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0.0) * 255.0
    v = mx * 255.0
    return h, s, v


def _accent_stats(img, cl_px, X0, Y0, accents, tol, soft=0.0,
                  matcher="hsv", coherent=False, adapt=False,
                  variants=False, bg_from=None):
    ph, pw = cl_px.shape
    sub = img[Y0:Y0 + ph, X0:X0 + pw].astype(np.float32) / 255.0
    sub0 = sub
    sub, m = _subsample_patch(sub, cl_px)
    px = sub[m]

    if px.shape[0] == 0 or not accents:
        return 0.0, 0.0





    inner = np.zeros_like(m)
    if m.shape[0] > 2 and m.shape[1] > 2:
        inner[1:-1, 1:-1] = (m[1:-1, 1:-1] & m[:-2, 1:-1] & m[2:, 1:-1]
                              & m[1:-1, :-2] & m[1:-1, 2:])
    edge = (m & ~inner)[m]
    use_edge = bool(edge.any() and int(edge.sum()) >= 4)






    if bg_from is not None and bg_from.shape == cl_px.shape:
        _sub_bg, m_bg = _subsample_patch(sub0, bg_from)
        bgm = _sub_bg[~m_bg]
    else:
        bgm = sub[~m]
    bg = None
    if bgm.shape[0] >= 8:
        bg = np.median(bgm.reshape(-1, 3), axis=0)




    coh_min = ACCENT_COHERENT_MIN if m.shape == cl_px.shape \
        else max(2, ACCENT_COHERENT_MIN // 4)




    tol_scale = max(0.15, min(3.5, float(tol) / 26.0))

    if matcher == "oklab" and soft > 0:




        p_lab = _rgb01_to_lab(px[:, ::-1])
        adapt_ab = None
        if adapt and bg is not None:
            blab = _rgb01_to_lab(bg[::-1])
            shift = blab[1:3].astype(np.float32)
            n = float(np.hypot(shift[0], shift[1]))
            if n > 1e-6:
                adapt_ab = shift * min(1.0, ADAPT_MAX_AB / n) \
                    * ADAPT_STRENGTH
                p_lab = p_lab.copy()
                p_lab[..., 1:3] -= adapt_ab

        tol_e = (DE_TOL_BASE
                 + DE_TOL_SOFT * max(0.0, min(1.0, float(soft)))) \
            * tol_scale
        best_mean = 0.0
        best_strong = 0.0
        for (ah, asat, av) in accents:
            lab, chroma, rgb01 = _accent_lab(ah, asat, av)
            best_d = None
            for dL in ACCENT_L_VARIANTS if variants else (0.0,):
                var = lab + np.array([dL, 0.0, 0.0], dtype=np.float32)
                d = _de_terms(p_lab, var, chroma)
                best_d = d if best_d is None else np.minimum(best_d, d)
            sim = np.clip(1.0 - best_d / tol_e, 0.0, 1.0)
            if bg is not None:
                sim = np.maximum(sim, blend_similarity(px, rgb01, bg))
            mean = float(sim.mean())
            if use_edge:
                mean = max(mean, float(sim[edge].mean()))
            strong_mask = sim >= ACCENT_STRONG_SIM
            strong = float(strong_mask.mean())
            if coherent and strong > 0.0:
                grid = np.zeros(m.shape, dtype=bool)
                grid[m] = strong_mask
                if not _coherent_enough(grid, coh_min):
                    continue








            if mean > best_mean:
                best_mean = mean
            if strong > best_strong:
                best_strong = strong
        return best_mean, best_strong







    pxc = px
    if adapt and bg is not None:
        ref = float(bg.mean())
        gain = ref / np.maximum(bg, 1e-3)
        gain = np.clip(gain, 0.5, 2.0).astype(np.float32)
        pxc = np.clip(px * gain, 0.0, 1.0)

    h, s, v = _bgr01_to_hsv(pxc)

    best_mean = 0.0
    best_strong = 0.0

    for (ah, asat, av) in accents:
        best_sim = None
        for dV in HSV_V_VARIANTS if variants else (0.0,):
            vv = min(255.0, max(0.0, av + dV))
            sim = _accent_similarity(h, s, v, ah, asat, vv, tol, soft)
            best_sim = sim if best_sim is None \
                else np.maximum(best_sim, sim)
        sim = best_sim
        mean = float(sim.mean())
        if use_edge:
            mean = max(mean, float(sim[edge].mean()))
        strong_mask = sim >= ACCENT_STRONG_SIM
        strong = float(strong_mask.mean())
        if coherent and strong > 0.0:
            grid = np.zeros(m.shape, dtype=bool)
            grid[m] = strong_mask
            if not _coherent_enough(grid, coh_min):
                continue

        if mean > best_mean:
            best_mean = mean
        if strong > best_strong:
            best_strong = strong

    return best_mean, best_strong







MOTION_MIN_SPEED = 20.0
MOTION_MAX_DEVIATION = 12.0
MOTION_MIN_SPAN = 0.03


def predict_motion(obs, lead_ms, max_offset):
    if lead_ms <= 0 or len(obs) < 2 or max_offset <= 0:
        return 0.0, 0.0

    (t0, x0, y0), (t1, x1, y1) = obs[0], obs[-1]
    span = t1 - t0
    if span < MOTION_MIN_SPAN:
        return 0.0, 0.0

    vx = (x1 - x0) / span
    vy = (y1 - y0) / span
    if math.hypot(vx, vy) < MOTION_MIN_SPEED:
        return 0.0, 0.0

    for (t, x, y) in obs[1:-1]:
        dx = x - (x0 + vx * (t - t0))
        dy = y - (y0 + vy * (t - t0))
        if math.hypot(dx, dy) > MOTION_MAX_DEVIATION:
            return 0.0, 0.0

    lead = float(lead_ms) / 1000.0
    ox, oy = vx * lead, vy * lead
    mag = math.hypot(ox, oy)
    if mag > max_offset:
        k = max_offset / mag
        ox, oy = ox * k, oy * k
    return ox, oy





































class MotionTracker(object):



    POS_R = 9.0
    SCALE_R = 0.0025


    POS_Q = 2500.0
    SCALE_Q = 0.02

    MISS_RESET = 3


    STALE_S = 0.6


    SCALE_JUMP = 0.69


    POS_GATE_FLOOR = 4.0
    SCALE_GATE_FLOOR = 0.10

    def __init__(self, dim=2):
        if dim not in (2, 3):
            raise ValueError("MotionTracker dim is 2 or 3")
        self.dim = dim
        self.n = 2 * dim







        self._prev_obs = None
        self.reset()

    def reset(self):
        self.x = None
        self.P = None
        self.last_t = None
        self.updates = 0
        self.misses = 0
        self.q_mult = 1.0

    def _init(self, t, z):
        n = self.dim
        self.x = np.zeros(2 * n, dtype=np.float64)
        self.x[:n] = z


        self.P = np.diag(np.concatenate(
            [self._r_vec(), np.full(n, 40000.0)]))
        self.updates = 1
        prev = self._prev_obs
        if prev is not None:
            pt, pz = prev
            if pz.shape == z.shape and 0.0 < t - pt <= self.STALE_S:
                self.x[n:] = (z - pz) / (t - pt)
                self.updates = 2
        self.last_t = t
        self.misses = 0
        self.q_mult = 1.0
        return True

    def _r_vec(self):
        if self.dim == 2:
            return np.array([self.POS_R, self.POS_R], dtype=np.float64)
        return np.array([self.POS_R, self.POS_R, self.SCALE_R],
                        dtype=np.float64)

    def _q_base(self):
        if self.dim == 2:
            return np.array([self.POS_Q, self.POS_Q], dtype=np.float64)
        return np.array([self.POS_Q, self.POS_Q, self.SCALE_Q],
                        dtype=np.float64)

    def _to_state_pos(self, pos):
        if self.dim == 2:
            return np.array([float(pos[0]), float(pos[1])],
                            dtype=np.float64)
        s = float(pos[2])
        if not math.isfinite(s) or s <= 0.0:
            return None
        return np.array([float(pos[0]), float(pos[1]), math.log(s)],
                        dtype=np.float64)

    def update(self, t, pos):
        try:
            t = float(t)
            z = self._to_state_pos(pos)
        except (TypeError, ValueError, IndexError):
            return False
        if z is None or not math.isfinite(t) or not np.all(np.isfinite(z)):
            return False




        prev = self._prev_obs
        if prev is None or t > prev[0]:
            self._prev_obs = (t, z.copy())

        if self.last_t is None:
            return self._init(t, z)

        dt = t - self.last_t
        if dt <= 0.0:
            return False
        if dt > self.STALE_S:
            self.reset()
            return self.update(t, pos)

        n = self.dim
        if n == 3 and abs(z[2] - self.x[2]) > self.SCALE_JUMP:





            self.reset()
            return self.update(t, pos)



        F = np.eye(2 * n, dtype=np.float64)
        F[:n, n:] = np.eye(n, dtype=np.float64) * dt
        qb = self._q_base() * self.q_mult
        Q = np.zeros((2 * n, 2 * n), dtype=np.float64)
        Q[:n, :n] = np.diag(qb * dt ** 3 / 3.0)
        Q[:n, n:] = np.diag(qb * dt ** 2 / 2.0)
        Q[n:, :n] = np.diag(qb * dt ** 2 / 2.0)
        Q[n:, n:] = np.diag(qb * dt)
        xp = F.dot(self.x)
        Pp = F.dot(self.P).dot(F.T) + Q



        R = self._r_vec()
        S_diag = np.diag(Pp)[:n] + R
        S_diag = np.maximum(S_diag, 1e-9)
        y = z - xp[:n]
        floors = np.empty(n, dtype=np.float64)
        floors[:] = self.POS_GATE_FLOOR
        if n == 3:
            floors[2] = self.SCALE_GATE_FLOOR
        gate = np.maximum(3.0 * np.sqrt(S_diag), floors)
        if np.any(np.abs(y) > gate):
            self.misses += 1
            if self.misses >= self.MISS_RESET:









                self.reset()
                if prev is not None:
                    self._prev_obs = prev
                return self._init(t, z)
            return False



        H = np.zeros((n, 2 * n), dtype=np.float64)
        H[:, :n] = np.eye(n, dtype=np.float64)
        S = H.dot(Pp).dot(H.T) + np.diag(R)
        try:
            K = Pp.dot(H.T).dot(np.linalg.inv(S))
        except np.linalg.LinAlgError:
            return False
        self.x = xp + K.dot(y)
        I_KH = np.eye(2 * n, dtype=np.float64) - K.dot(H)
        self.P = I_KH.dot(Pp).dot(I_KH.T) \
            + K.dot(np.diag(R)).dot(K.T)
        normed = float(np.max(np.abs(y) / gate))
        self.q_mult = 16.0 if normed > 0.5 else max(1.0, self.q_mult * 0.5)
        self.last_t = t
        self.updates += 1
        self.misses = 0
        return True

    def speed(self):
        if self.x is None:
            return 0.0
        n = self.dim
        return float(math.hypot(self.x[n], self.x[n + 1]))

    def predict(self, lead_ms, max_offset, min_speed=MOTION_MIN_SPEED):
        zero3 = (0.0, 0.0, 1.0)
        zero2 = (0.0, 0.0)
        try:
            lead = float(lead_ms) / 1000.0
        except (TypeError, ValueError):
            return zero3 if self.dim == 3 else zero2
        if lead <= 0 or max_offset <= 0 or self.x is None \
                or self.updates < 2:
            return zero3 if self.dim == 3 else zero2

        n = self.dim
        vx, vy = float(self.x[n]), float(self.x[n + 1])
        if math.hypot(vx, vy) < min_speed:
            return zero3 if self.dim == 3 else zero2

        damp = 1.0 if self.misses == 0 else (
            0.5 if self.misses == 1 else 0.25)
        ox, oy = vx * lead * damp, vy * lead * damp
        mag = math.hypot(ox, oy)
        if mag > max_offset:
            k = max_offset / mag
            ox, oy = ox * k, oy * k

        if self.dim == 3:
            try:
                lr = max(-math.log(4.0),
                         min(math.log(4.0),
                             float(self.x[5]) * lead * damp))
                ratio = math.exp(lr)
            except (ValueError, OverflowError):
                ratio = 1.0
            return ox, oy, ratio
        return ox, oy












MOTION_DIFF_LO = 18.0
MOTION_DIFF_HI = 90.0
MOTION_WHITE_CUT = 210.0


def _frame_movers(prev_gray, curr_gray):
    try:
        if prev_gray is None or curr_gray is None:
            raise ValueError("no baseline")
        p = np.asarray(prev_gray, dtype=np.float32)
        c = np.asarray(curr_gray, dtype=np.float32)
        if p.shape != c.shape or p.size == 0:
            raise ValueError("shape")
        d = np.abs(c - p)
        m = (d >= MOTION_DIFF_LO) & (
            (d <= MOTION_DIFF_HI) | (c < MOTION_WHITE_CUT))
        return _erode(m, 1)
    except Exception:
        try:
            return np.zeros(np.asarray(curr_gray).shape[:2], dtype=bool)
        except Exception:
            return np.zeros((0, 0), dtype=bool)


def motion_sense_of(cfgv):
    try:
        return min(1.0, max(0.0, float(cfgv.get("motion_sense", 0)) / 100.0))
    except (TypeError, ValueError):
        return 0.0


def _accent_fraction(img, cl_px, X0, Y0, accents, tol, soft=0.0,
                      matcher="hsv", coherent=False, adapt=False,
                      variants=False):
    return _accent_stats(img, cl_px, X0, Y0, accents, tol, soft, matcher,
                         coherent, adapt, variants)[0]





CALIB_HALF_WEIGHT_PX = 60.0
CALIB_MIN_WEIGHT = 0.02


def _weighted_mean(values, weights):
    w = float(np.sum(weights))
    if w <= 0.0:
        return float(np.mean(values)) if len(values) else 0.0
    return float(np.sum(values * weights) / w)


def _weighted_percentile(values, weights, pct):
    values = np.asarray(values, dtype=np.float64).reshape(-1)
    weights = np.asarray(weights, dtype=np.float64).reshape(-1)
    if values.size == 0:
        return 0.0
    if values.size == 1 or float(np.sum(weights)) <= 0.0:
        return float(np.percentile(values, pct))
    order = np.argsort(values)
    v, w = values[order], weights[order]
    cum = np.cumsum(w)
    total = cum[-1]
    target = total * (float(pct) / 100.0)
    idx = int(np.searchsorted(cum, target))
    return float(v[min(idx, v.size - 1)])


def calibrate_accent(img, cx, cy, accents, tol, soft, matcher="hsv"):
    if not accents or img is None:
        return None
    a = np.asarray(img)
    if a.ndim != 3 or a.shape[2] < 3 or a.size == 0:
        return None













    h, w = a.shape[:2]
    cx = min(max(int(cx), 0), max(0, w - 1))
    cy = min(max(int(cy), 0), max(0, h - 1))
    yy, xx = np.mgrid[0:h, 0:w]
    spatial = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2).astype(np.float32)



    weight = 1.0 / (1.0 + (spatial / CALIB_HALF_WEIGHT_PX) ** 2)

    px = a.reshape(-1, 3).astype(np.float32) / 255.0
    wt = weight.reshape(-1)
    keep = wt >= CALIB_MIN_WEIGHT
    if int(keep.sum()) >= 64:
        px, wt = px[keep], wt[keep]
    if px.shape[0] > 20000:


        step = px.shape[0] // 20000 + 1
        px, wt = px[::step], wt[::step]

    if matcher == "oklab" and soft > 0:








        p_lab = _rgb01_to_lab(px[:, ::-1])
        best = None
        for (ah, asat, av) in accents:
            lab, chroma, _ = _accent_lab(ah, asat, av)
            best_d = None
            for dL in ACCENT_L_VARIANTS:
                d = _de_terms(p_lab,
                              lab + np.array([dL, 0.0, 0.0],
                                             dtype=np.float32),
                              chroma)
                best_d = d if best_d is None else np.minimum(best_d, d)
            best = best_d if best is None else np.minimum(best, best_d)
        color_d = best
        tol_now = DE_TOL_BASE + DE_TOL_SOFT * max(0.0, min(1.0, float(soft)))
        strong = float(_weighted_mean(
            (color_d <= (1.0 - ACCENT_STRONG_SIM) * tol_now).astype(np.float32),
            wt))
        unit = "dE"
    else:
        h, s, v = _bgr01_to_hsv(px)
        best = None
        for (ah, asat, av) in accents:
            sim = _accent_similarity(h, s, v, ah, asat, av, tol, soft)
            color_d = 1.0 - sim
            best = color_d if best is None else np.minimum(best, color_d)
        color_d = best
        strong = float(_weighted_mean(
            (color_d <= 1.0 - ACCENT_STRONG_SIM).astype(np.float32), wt))
        unit = "1-sim"

    if color_d.size == 0:
        return None
    p50 = float(_weighted_percentile(color_d, wt, 50.0))
    p95 = float(_weighted_percentile(color_d, wt, 95.0))


    if unit == "dE":



        scale = max(0.15, min(3.5, float(tol) / 26.0))
        suggested = int(round(min(1.0, max(0.0, (p95 / scale - DE_TOL_BASE)
                                             / DE_TOL_SOFT)) * 100.0))
    else:







        gate = 1.0 - ACCENT_STRONG_SIM
        cur = min(1.0, max(0.0, float(soft))) * 100.0
        if p95 <= gate:
            suggested = int(round(cur))
        else:
            frac = min(1.0, (p95 - gate) / max(1e-6, 1.0 - gate))
            suggested = int(round(cur + frac * (100.0 - cur)))
    return {"pixels": int(px.shape[0]), "p50": p50, "p95": p95,
            "strong_frac": strong, "suggested_soft": suggested,
            "unit": unit, "cursor": (cx, cy)}












EDGE_TOUCH_PX = 12


def _touches_screen_edge(Y0, X0, Y1, X1, w, h, edge_flags):
    if not edge_flags:
        return False
    try:
        el, et, er, eb = edge_flags
    except (TypeError, ValueError):
        return False


    return ((el and X0 <= EDGE_TOUCH_PX)
            or (et and Y0 <= EDGE_TOUCH_PX)
            or (er and X1 - 1 >= w - EDGE_TOUCH_PX)
            or (eb and Y1 - 1 >= h - EDGE_TOUCH_PX))


def _is_clipped(Y0, X0, bw, bh, w, h, edge_flags):
    el = et = er = eb = False
    if edge_flags is not None:
        try:
            el, et, er, eb = edge_flags
        except (TypeError, ValueError):
            pass

    if Y0 <= 2 and not et:
        return True
    if X0 <= 2 and not el:
        return True
    if Y0 + bh >= h - 2 and not eb:
        return True
    if X0 + bw >= w - 2 and not er:
        return True
    return False



def scan_region(img, cx, cy, cfgv, radius, follow_ctx=None, edge_flags=None,
                deadline_ms=None, collect=None, anchor_blind_area=0,
                motion_ctx=None, focus_bias=0.0, require_tier=0):
    if deadline_ms is None:
        try:
            deadline_ms = float(cfgv.get("scan_budget_ms", 350))
        except Exception:
            deadline_ms = 350.0


        deadline_ms = min(max(deadline_ms, 60.0), 2000.0)
    t0 = time.perf_counter()
    deadline = t0 + deadline_ms / 1000.0
    _SCAN_DEADLINE.deadline = deadline

    a = img.astype(np.float32)
    h, w = a.shape[:2]
    if a.shape[2] > 3:
        a = a[..., :3]

    bg = _box_blur(a, BLUR_WIN)


    diff = np.sqrt(((a - bg) ** 2 * _CH_WEIGHTS).sum(axis=2))





    if bool(cfgv.get("luminance_norm", True)):
        lum = (bg * _CH_WEIGHTS).sum(axis=2)
        diff = diff * np.clip(NORM_K / (lum + NORM_C), NORM_MIN, NORM_MAX)

    try:
        thr = float(cfgv.get("contrast_threshold", 38))
    except (TypeError, ValueError):
        thr = 38.0
    adapt_scale = 1.0









    if bool(cfgv.get("adaptive_threshold", True)):




        flat = diff.ravel()
        if flat.size > 20000:
            flat = flat[::flat.size // 20000 + 1]
        energy = float(np.percentile(flat, ADAPTIVE_PERCENTILE))
        adapted = max(ADAPTIVE_FLOOR, min(thr, energy * ADAPTIVE_K))


        adapt_scale = min(1.0, adapted / thr) if thr > 0 else 1.0
        thr = adapted

    ink = diff > thr
    ink_w = diff > thr * 0.55

    for m in (ink, ink_w):
        m[:2, :] = False
        m[-2:, :] = False
        m[:, :2] = False
        m[:, -2:] = False

    ink = _erode(_dilate(ink, 1), 1)
    ink_w = _erode(_dilate(ink_w, 1), 1)
















    merge_distance = float(cfgv.get("merge_distance", 0) or 0)
    scale = 1.0
    if merge_distance > 0:


        if _get_dpi_scale is not None:
            try:
                scale = _get_dpi_scale()
            except Exception:
                scale = 1.0



        gap = int(min(3, max(1, round(0.5 * merge_distance * scale))))
        ink = _close_gaps(ink, gap)
        ink_w = _close_gaps(ink_w, gap)


    ph = (CS - h % CS) % CS
    pw = (CS - w % CS) % CS

    ink_p = np.pad(ink, ((0, ph), (0, pw))) if (ph or pw) else ink
    inkw_p = np.pad(ink_w, ((0, ph), (0, pw))) if (pw or ph) else ink_w

    gh, gw = ink_p.shape[0] // CS, ink_p.shape[1] // CS

    ratio = ink_p.reshape(gh, CS, gw, CS).mean(axis=(1, 3))
    ratio_w = inkw_p.reshape(gh, CS, gw, CS).mean(axis=(1, 3))

    strong = ratio >= CELL_SOLID
    weak = ratio_w >= CELL_WEAK

    solids = _grow_cells(strong, weak)
    solids = _erode(_dilate(solids, 1), 1)


    full = np.ones((gh, gw), dtype=bool)
    obj_cells = ~_flood_bg(solids, full)

    try:
        min_area = int(cfgv.get("min_area", 220))
    except (TypeError, ValueError):
        min_area = 220
    try:
        max_area = int(cfgv.get("max_area", 45000))
    except (TypeError, ValueError):
        max_area = 45000
    try:
        max_dim = int(cfgv.get("max_dim", 300))
    except (TypeError, ValueError):
        max_dim = 300









    try:
        user_min_contrast = float(cfgv.get("min_contrast", 48))
    except (TypeError, ValueError):
        user_min_contrast = 48.0
    if user_min_contrast > MIN_CONTRAST_BASE:
        min_contrast = user_min_contrast * adapt_scale * CONTRAST_METRIC_SCALE
    else:
        min_contrast = max(MIN_CONTRAST_FLOOR,
                           user_min_contrast * adapt_scale) \
            * CONTRAST_METRIC_SCALE
    max_aspect = 10.0





    frag_floor_split = 64

    finals = []
    labels, info = _label_cells(obj_cells)






    def _box_edge_dist(e):
        _cid, _count, _gy0, _gx0, _gy1, _gx1 = e
        return math.hypot(max(_gx0 * CS - cx, 0, cx - (_gx1 * CS - 1)),
                          max(_gy0 * CS - cy, 0, cy - (_gy1 * CS - 1)))
    try:
        info = sorted(info, key=_box_edge_dist)
    except Exception:
        pass
    pending = [(labels, info, 0)]
    guard = 0






    split_tries = 0
    SPLIT_TRY_CAP = 8





    detection_dropped = 0


    while pending and guard < 10:
        guard += 1

        if time.perf_counter() > deadline:
            detection_dropped += sum(len(inf) for _lab, inf, _d in pending)
            break

        lab, inf, depth = pending.pop()

        for cid, count, gy0, gx0, gy1, gx1 in inf:
            bw = (gx1 - gx0) * CS
            bh = (gy1 - gy0) * CS

            if depth < 2 and (bw > 200 or bh > 200 or count * CS * CS > 25000):
                if split_tries >= SPLIT_TRY_CAP:


                    finals.append((lab, cid, gy0, gx0, gy1, gx1))
                    continue
                split_tries += 1
                cmask = (lab == cid)


                sub_obj = cmask & ~_flood_bg(solids, cmask)
                slab, sinfo = _label_cells(sub_obj)

                if sinfo and not (len(sinfo) == 1 and sinfo[0][1] >= count * 0.9):
                    pending.append((slab, sinfo, depth + 1))
                    continue



                free = cmask & ~solids
                lf, lfi = _label_cells(free)
                big = np.zeros_like(cmask)
                big_min = max(30, int(0.40 * count))

                for fid, fcount, _a, _b, _c2, _d in lfi:
                    if fcount >= big_min:
                        big |= (lf == fid)

                sub_b = cmask & ~big
                lbb, ibi = _label_cells(sub_b)

                if ibi and not (len(ibi) == 1 and ibi[0][1] >= count * 0.9):
                    pending.append((lbb, ibi, depth + 1))
                    continue













                if bool(cfgv.get("subject_priority", False)):
                    core = _dilate(strong, 1) & cmask
                    slab2, sinfo2 = _label_cells(core)
                    kept = [e for e in sinfo2
                            if e[1] * CS * CS >= frag_floor_split]
                    if len(kept) > 1:
                        pending.append((slab2, kept, depth + 1))
                        continue

            finals.append((lab, cid, gy0, gx0, gy1, gx1))





    try:
        finals.sort(key=lambda e: math.hypot(
            max(e[3] * CS - cx, 0, cx - (e[5] * CS - 1)),
            max(e[2] * CS - cy, 0, cy - (e[4] * CS - 1))))
    except Exception:
        pass

    candidates = []
    fragments = []

    for _fi, (lab, cid, gy0, gx0, gy1, gx1) in enumerate(finals):
        if time.perf_counter() > deadline:
            detection_dropped += len(finals) - _fi
            break

        Y0, X0 = gy0 * CS, gx0 * CS
        Y1, X1 = min(gy1 * CS, h), min(gx1 * CS, w)

        if Y1 <= Y0 or X1 <= X0:
            continue

        bw, bh = X1 - X0, Y1 - Y0





        at_edge = _touches_screen_edge(Y0, X0, Y1, X1, w, h, edge_flags)

        dim_cap = max_dim * 2 if at_edge else max_dim
        aspect_cap = max_aspect * 2.5 if at_edge else max_aspect

        if max(bw, bh) > dim_cap:
            continue

        if max(bw, bh) > aspect_cap * max(1, min(bw, bh)):
            continue










        ddx = max(X0 - cx, 0, cx - (X1 - 1))
        ddy = max(Y0 - cy, 0, cy - (Y1 - 1))
        dist = math.hypot(ddx, ddy)

        if dist > radius + 20:
            continue

        cl_cells = (lab[gy0:gy1, gx0:gx1] == cid)
        cl_px = np.repeat(np.repeat(cl_cells, CS, axis=0), CS, axis=1)
        cl_px = cl_px[:Y1 - Y0, :X1 - X0]

        area = int(cl_px.sum())

        if area > max_area:
            continue

        too_small = area < min_area







        frag_floor = min(MIN_FRAG_AREA, max(8, min_area * 3 // 4))
        if too_small and area < frag_floor:
            continue

        fill = area / float(bw * bh)

        if fill < MIN_FILL:










            if _touches_screen_edge(Y0, X0, Y1, X1, w, h, edge_flags):
                cl_px = np.ones((Y1 - Y0, X1 - X0), dtype=bool)
                area = int(cl_px.sum())
                if area > max_area:
                    continue
                fill = 1.0
            else:
                continue







        sub_d = diff[Y0:Y1, X0:X1]
        d_vals = sub_d[cl_px]

        if d_vals.size == 0:
            continue

        d_max = float(d_vals.max())
        core = d_vals >= (d_max * CONTRAST_CORE_FRAC)




        if d_vals.size > 4000:
            _dv = d_vals[::d_vals.size // 4000 + 1]
            _core = _dv >= (d_max * CONTRAST_CORE_FRAC)
        else:
            _dv, _core = d_vals, core
        if int(_core.sum()) >= 8:
            contrast = float(np.percentile(_dv[_core], 90))
        else:
            contrast = d_max * 0.7

        if contrast < min_contrast:
            continue

        score = _base_score(contrast, area, fill, dist,
                            shape=_shape_mult(bw, bh, area))
        entry = (score, Y0, X0, cl_px, dist, area, contrast, bw, bh)

        if too_small:
            fragments.append(entry)
        else:
            candidates.append(entry)







    if merge_distance > 0 and (fragments or len(candidates) > 1):
        candidates = _merge_nearby(
            candidates, fragments, merge_distance,
            min_area, max_area, max_dim, max_aspect, scale,
            cx=cx, cy=cy, w=w, h=h, edge_flags=edge_flags,
            deadline=deadline,
        )












    candidates.sort(key=lambda c: c[4])












    if anchor_blind_area and anchor_blind_area > 0:


        blind_idx = {i for i, c in enumerate(candidates)
                     if c[2] <= cx < c[2] + c[7]
                     and c[1] <= cy < c[1] + c[8]
                     and c[5] <= anchor_blind_area}
        if blind_idx and len(blind_idx) < len(candidates):
            candidates = [c for i, c in enumerate(candidates)
                          if i not in blind_idx]














    if bool(cfgv.get("subject_priority", False)) and candidates:
        tiers = [_shape_tier(c[7], c[8], c[5]) for c in candidates]
        best_tier = max(tiers)
        if best_tier > 0:
            candidates = [c for c, tr in zip(candidates, tiers)
                          if tr == best_tier]






    try:
        _need = int(require_tier or 0)
    except (TypeError, ValueError):
        _need = 0
    if _need > 0 and candidates:
        candidates = [c for c in candidates
                      if _shape_tier(c[7], c[8], c[5]) >= _need]








    unscored = 0
    follow_skipped = 0

    accents = _cached_parse_accents(cfgv.get("accent_color", "off"))
    try:
        accent_boost = max(0.0, float(cfgv.get("accent_boost", 0.0) or 0.0))
    except (TypeError, ValueError):
        accent_boost = 0.0





    accent_only = bool(cfgv.get("accent_only", False))
    soft = accent_soft_of(cfgv)
    matcher = accent_matcher_of(cfgv)



    adapt = color_adapt_of(cfgv)
    variants = accent_variants_of(cfgv)
    coherent = accent_coherent_of(cfgv)
    try:
        tol = float(cfgv.get("accent_tolerance", 26))
    except (TypeError, ValueError):
        tol = 26.0

    if candidates and (accent_boost > 0 or accent_only):
        accented = []

        for cand in candidates:
            frac = 0.0
            strong = 0.0
            scored = time.perf_counter() <= deadline
            if scored and accents:
                frac, strong = _accent_stats(
                    img, cand[3], cand[2], cand[1], accents, tol, soft,
                    matcher, coherent, adapt, variants)
            else:
                unscored += 1







            if accent_only and (not scored or strong < ACCENT_MIN_FRACTION):
                continue

            mult = 1.0
            if frac > 0 and accent_boost > 0:
                mult = min(1.0 + accent_boost * frac, ACCENT_RANK_CAP)
            if mult != 1.0:
                cand = (cand[0] * mult,) + cand[1:]
            accented.append(cand)

        candidates = accented














    excludes = _cached_parse_accents(cfgv.get("exclude_color", "off"))
    if excludes and candidates:
        kept = []

        for cand in candidates:
            strong = 0.0
            scored = time.perf_counter() <= deadline
            if scored:




                if int(cand[3].sum()) < EXCLUDE_CORE_MIN:
                    core = cand[3]
                    use_core = False
                else:
                    core = _erode(cand[3], EXCLUDE_ERODE_PX)
                    use_core = int(core.sum()) >= EXCLUDE_CORE_MIN
                    if not use_core:
                        core = cand[3]
                _mean, strong = _accent_stats(
                    img, core, cand[2], cand[1], excludes, tol, soft,
                    matcher, coherent, adapt, variants,
                    bg_from=cand[3] if use_core else None)
            else:
                unscored += 1















            if not scored or strong >= ACCENT_MIN_FRACTION:
                continue
            kept.append(cand)

        candidates = kept



    if follow_ctx is not None and candidates:
        f_boost = float(cfgv.get("follow_boost", 1.0) or 0.0)
        try:
            sig, mem_x, mem_y, decay = follow_ctx
        except (TypeError, ValueError):
            sig, mem_x, mem_y, decay = None, 0, 0, 0.0

        if f_boost > 0 and decay > 0:
            followed = []

            for cand in candidates:
                sim = 0.0

                if sig is not None:
                    if time.perf_counter() <= deadline:







                        frac = _accent_fraction(img, cand[3], cand[2],
                                                cand[1], [sig],
                                                FOLLOW_COLOR_TOL,
                                                soft=soft, matcher=matcher,
                                                coherent=coherent,
                                                adapt=adapt,
                                                variants=variants)
                        if frac >= FOLLOW_COLOR_FRAC:
                            sim = frac
                    else:




                        follow_skipped += 1






                bx0, by0 = cand[2], cand[1]
                bx1, by1 = bx0 + cand[7], by0 + cand[8]
                if (bx0 - FOLLOW_POS_PAD <= mem_x <= bx1 + FOLLOW_POS_PAD
                        and by0 - FOLLOW_POS_PAD <= mem_y <= by1 + FOLLOW_POS_PAD):
                    sim = max(sim, FOLLOW_POS_SIM)

                if sim > 0:
                    cand = (cand[0] * (1.0 + f_boost * decay * sim),) + cand[1:]
                followed.append(cand)

            candidates = followed








    if motion_ctx is not None and candidates:
        try:
            _mmask, _mboost = motion_ctx
        except (TypeError, ValueError):
            _mmask, _mboost = None, 0.0
        if _mmask is not None and _mboost > 0:
            _moved = []
            for _cand in candidates:
                _frac = 0.0
                try:
                    _mY0, _mX0 = _cand[1], _cand[2]
                    _mh, _mw = _cand[3].shape
                    _win = _mmask[_mY0:_mY0 + _mh, _mX0:_mX0 + _mw]
                    if _win.shape == _cand[3].shape and _win.size:
                        _npx = int(_cand[3].sum())
                        if _npx > 0:
                            _frac = float(np.logical_and(
                                _cand[3], _win).sum()) / _npx
                except Exception:
                    _frac = 0.0
                if _frac > 0:
                    _cand = (_cand[0] * min(1.0 + _mboost * _frac,
                                            1.0 + _mboost),) + _cand[1:]
                _moved.append(_cand)
            candidates = _moved

    def _report_drops():











        if not (unscored or detection_dropped or follow_skipped):
            return
        tail = ""
        if follow_skipped:
            tail += " (%d follow nudge(s) skipped)" % follow_skipped
        if (accents and accent_only) or excludes:
            tail += (" - accent_only and exclude_color fail closed for "
                     "unscored items")
        else:
            tail += (" - unscored items were kept (no fail-closed "
                     "colour gate configured)")
        _log("Colour stage cut short: %d item(s) went unscored and %d "
             "unmeasured in detection before the %.0f ms scan budget "
             "ran out%s. Lower the search radius, or raise the scan "
             "budget, if this repeats."
             % (unscored, detection_dropped,
                (deadline - t0) * 1000.0, tail))

    ms = (time.perf_counter() - t0) * 1000.0

    if not candidates:
        _report_drops()
        return ScanResult("none", None, ms)






    region_area = float(h * w)
    boosted = []

    for score, Y0, X0, cl_px, dist, area, contrast, bw, bh in candidates:
        clipped = _is_clipped(Y0, X0, bw, bh, w, h, edge_flags)
        vis = min(0.5, area / region_area)
        score *= (1.0 + vis) * (0.6 if clipped else 1.0)
        boosted.append((score, Y0, X0, cl_px, dist, area, contrast, bw, bh))

    candidates = boosted
    candidates.sort(key=lambda c: -c[0])

    if collect is not None:




        for _s, _Y0, _X0, _cl, _d, _a, _ct, _bw, _bh in candidates:
            _ys, _xs = np.nonzero(_cl)
            if _xs.size == 0:
                continue
            _pt = _meanshift(_xs.astype(np.float32) + _X0,
                             _ys.astype(np.float32) + _Y0, cx, cy)
            if _pt is None:
                _ddx = _X0 + _bw / 2.0 - cx
                _ddy = _Y0 + _bh / 2.0 - cy
            else:
                _ddx, _ddy = _pt[0] - cx, _pt[1] - cy
            collect.append((_s, _ddx, _ddy, _d, _a, _ct, _bw, _bh))








    for _s, Y0, X0, cl_px, dist, area, contrast, bw, bh in candidates:
        if time.perf_counter() > deadline:
            detection_dropped += 1
            break
        ys, xs = np.nonzero(cl_px)
        if xs.size > 4000:
            step = xs.size // 4000 + 1
            xs, ys = xs[::step], ys[::step]
        xs = xs.astype(np.float32) + X0
        ys = ys.astype(np.float32) + Y0

        pt = _meanshift(xs, ys, cx, cy)

        if pt is None:




            tcx, tcy = X0 + bw / 2.0, Y0 + bh / 2.0
        else:
            tcx, tcy = pt
        if focus_bias > 0.0 and _shape_tier(bw, bh, area) == 2:





            tcy -= max(0.0, tcy - Y0) * min(1.0, focus_bias)
        ddx = tcx - cx
        ddy = tcy - cy
        move = math.hypot(ddx, ddy)

        if move > radius + 10:
            continue

        ms = (time.perf_counter() - t0) * 1000.0




        sig = None
        try:
            body = img[Y0:Y0 + cl_px.shape[0], X0:X0 + cl_px.shape[1]][cl_px]
            if body.shape[0] > 0:
                med = np.median(body.astype(np.float32), axis=0)
                sig = _parse_accent("%d,%d,%d"
                                    % (int(med[2]), int(med[1]), int(med[0])))
        except Exception:
            sig = None

        target = SnapTarget(
            int(round(ddx)),
            int(round(ddy)),
            move,
            area,
            contrast,
            bw,
            bh,
            sig,
        )

        return ScanResult("target", target, ms)

    ms = (time.perf_counter() - t0) * 1000.0
    _report_drops()
    return ScanResult("none", None, ms)


