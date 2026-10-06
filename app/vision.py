"""Screen analysis engine.

Finds solid, item-shaped, high-contrast objects near a point: cell-grid
blob detection with hysteresis, big-blob splitting, fragment merging,
accent colour priority/exclusivity, follow memory (target persistence),
adaptive thresholding and luminance normalisation. Pure numpy - runs on
any OS."""

import math
import time

import numpy as np

# vision.py is a dependency-free leaf (numpy only), which is what makes it
# testable off-Windows and keeps the analysis engine honest. It still needs
# to report the one degradation a user cannot see for themselves, so the log
# sink is injected rather than imported: core.log registers itself at start.
_LOG_SINK = None


def set_log_sink(fn):
    """Install fn(text) as this module's diagnostic sink (core.log)."""
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

_CH_WEIGHTS = np.array([0.114, 0.587, 0.299], dtype=np.float32)  # B, G, R

CS = 4              # cell size for fast blob grouping
CELL_WALL = 0.28    # strong ink fraction making a cell a wall
CELL_WEAK = 0.18    # weak ink fraction for hysteresis growth
BLUR_WIN = 9        # local background window
MIN_FILL = 0.45     # minimum solidness

# Luminance normalisation (Weber-style): diff is scaled by
# NORM_K / (local_luminance + NORM_C), clamped to [NORM_MIN, NORM_MAX].
# NORM_K == 128 + NORM_C, so mid-grey content scores exactly as before;
# dark regions amplify (up to 3x), bright regions damp mildly (0.75x).
NORM_C = 24.0
NORM_K = 152.0
NORM_MIN = 0.75
NORM_MAX = 3.0

# Adaptive threshold: thr = clamp(percentile(diff, P) * K, FLOOR, base).
# The region's own edge energy may LOWER the ink bar for inherently dim
# scenes, never raise it; the floor keeps flat dither/noise from
# becoming ink. ADAPTIVE_BASE is the stock contrast_threshold the
# behaviour was tuned around: a user setting at or below it gets the
# adaptive treatment, a setting above it is an explicit raise and is
# respected exactly (otherwise raising the knob would silently do
# nothing while adaptive is on).
ADAPTIVE_PERCENTILE = 98.0
ADAPTIVE_K = 0.5
ADAPTIVE_FLOOR = 14.0
ADAPTIVE_BASE = 38.0

# min_contrast floor (legacy units) when the adaptive threshold lowered
# the bar: rescued dim items must still clear a real quality gate.
MIN_CONTRAST_FLOOR = 28.0

# Stock min_contrast (DEFAULT_CONFIG) - the same role for the quality
# gate that ADAPTIVE_BASE plays for the ink bar: at or below it the
# gate may follow a lowered bar, above it the user explicitly raised
# the floor and adaptive_threshold must not quietly relax it again
# (otherwise "raise it if it clicks the wrong thing" would only hold
# while adaptive is off).
MIN_CONTRAST_BASE = 48.0

# Contrast is measured as the 90th percentile of pixels within the top
# (1 - CONTRAST_CORE_FRAC) of the item's own diff range. Because blur
# and subtraction are linear, this scales exactly with true edge
# magnitude for same-shape items - one consistent ruler across hues,
# brightness levels, and threshold settings. The new metric reads about
# 1.2x the old fixed-threshold one, so the user-facing gate is scaled by
# ~1/1.2 to keep min_contrast's documented meaning.
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
        self.sig = sig  # HSV centre of the item's median colour (follow memory)


class ScanResult(object):
    __slots__ = ("kind", "target", "ms")

    def __init__(self, kind, target=None, ms=0.0):
        self.kind = kind
        self.target = target
        self.ms = ms


def _box_blur(a, win):
    """Mean filter using an integral image. a: (H,W,3) float32."""
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
    # NOTE: the border zeroing is load-bearing, not cosmetic. Without
    # it a shift-AND erode leaves the outermost rows/columns untouched,
    # so _dilate+_erode "closing" grows every blob by a ring instead of
    # cancelling - which inflated small items past min_area and kept a
    # 1 px garbage ring at capture borders. Interior features erode
    # identically either way; only the array edge changes.
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
    """
    Morphological closing with a square (2*gap+1) structuring element,
    implemented as separable sliding max (dilate) then sliding min
    (erode). Joins ink pieces separated by a break of at most `gap` px
    into one connected blob - the anti-aliased gaps that make an
    outlined button or sub-pixel rendered icon fragment into several
    detected items.

    Separable means it bridges axis-aligned breaks (the common case for
    outlines and text) without filling diagonal staircases: two blobs
    touching only at corners are not welded into a solid block, so
    neighbouring controls stay separate targets.

    Safety properties, load-bearing for the scan pipeline:
      * monotone - original ink is re-OR'd at the end, so closing can
        only ADD pixels, never remove them. A weak hysteresis seed that
        survived the pre-close cleanup cannot be thinned back below its
        ratio floor (a naive dilate+erode could, which would change
        detection results unpredictably);
      * border dead zone preserved - the outermost rows/columns stay
        cleared like scan_region's own 2 px zeroing, so no 1 px garbage
        ring returns at capture borders;
      * O(gap^2) vectorised array ops, no per-pixel Python loops.
    """
    try:
        g = int(float(gap))
    except (TypeError, ValueError):
        return m
    if g <= 0:
        return m
    g = min(g, min(m.shape) // 2 - 1)   # keep every slice/pad non-degenerate
    if g <= 0:
        return m
    # Dilation by the square (2g+1)x(2g+1) SE = Minkowski sum of a
    # horizontal and a vertical line SE: dilate by each arm in turn.
    # _dilate/_erode use only forward slices with non-negative pads, so
    # no negative-index arithmetic can leak into np.pad here (a naive
    # symmetric-shift formulation crashed warmup with
    # ValueError("index can't contain negative values")).
    d = _dilate(_dilate(m, g), g)
    e = _erode(_erode(d, g), g)
    e |= m & ~e               # monotone: closing adds pixels, never removes ink
    e[:g, :] = False          # keep the capture-border dead zone
    e[-g:, :] = False
    e[:, :g] = False
    e[:, -g:] = False
    return e


def _meanshift(xs, ys, sx, sy, sigma=25.0, iters=8):
    """
    Walk from (sx, sy) toward the centre of mass of nearby object pixels.
    This helps snap to the closest part of an item, not just its bounding box.

    Eight iterations (was four): each step can only pull so far, so a
    short walk silently gave up on items past ~100 px - detected,
    colour-approved, then dropped at the `move > radius + 10` gate
    below because the walk never arrived. The extra steps cost a few
    microseconds and only improve convergence (the walk still stops the
    moment it moves less than half a pixel); the radius gate keeps the
    leash exactly where it was.
    """
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
    """
    Hysteresis: keep weak cells that 8-connect to a strong cell.
    This closes outlines that dip in contrast along part of their edge.

    Vectorised fixpoint (round 8): identical result to the old Python
    BFS - a weak cell survives iff it 8-connects to the strong set -
    but each propagation step is one dilate8 instead of per-cell
    deque work (~5 ms -> ~0.3 ms per scan).

    The iteration cap bounds pathological inputs (a full-weak grid
    propagates one cell per step): convergence normally takes a handful
    of steps, so the cap never triggers on real screens - it only stops
    a freak frame from stalling the hook past the scan deadline.
    """
    keep = strong.copy()
    for _ in range(1024):
        grown = _dilate8(keep) & weak
        grown |= keep
        if np.array_equal(grown, keep):
            return keep
        keep = grown
    return keep


def _flood_bg(walls, mask):
    """
    Flood background cells through non-wall cells inside mask.
    Returns a boolean background array.

    Vectorised fixpoint (round 8): same seed set as the old BFS (border
    free cells plus free cells touching the outside of mask) and same
    4-connected growth, but propagation is whole-array shifts - the
    single hottest function in the profile (~17 ms/scan, 216k Python
    seed() calls) drops to well under a millisecond.

    Same iteration cap as _grow_cells: a flood across an enormous open
    grid propagates a few cells per step, and an uncapped loop is the
    most likely source of an occasional multi-hundred-ms stall.
    """
    gh, gw = walls.shape
    free = mask & ~walls
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

    for _ in range(1024):
        g = bg.copy()
        g[1:, :] |= bg[:-1, :]
        g[:-1, :] |= bg[1:, :]
        g[:, 1:] |= bg[:, :-1]
        g[:, :-1] |= bg[:, 1:]
        g &= free
        g |= seed
        if np.array_equal(g, bg):
            return bg
        bg = g
    return bg


def _label_cells(cells):
    """
    8-connected labelling of a boolean cell grid.
    Returns (labels, info).
    info entries: (id, cell_count, y0, x0, y1_exclusive, x1_exclusive)

    Row-run union-find (round 8): each row is split into runs of set
    cells, runs are unioned with the previous row's runs when their
    intervals overlap within one column (8-connectivity), and labels
    are painted back with per-run slice assignments. Python work is
    O(runs) - tens per scan - instead of O(cells); the old Python BFS
    cost ~7 ms/scan, this measures ~0.5 ms. Component ids follow
    row-major first-run order, identical to the old BFS discovery
    order (winsim/test_vision_equiv.py fuzzes all three rewrites
    against the originals, spirals and snakes included).
    """
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
    # compact ids in row-major first-run order (= old discovery order)
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


MIN_FRAG_AREA = 64  # px; smaller blobs are noise, not mergeable fragments

# Ranking shape (v8.49): proximity dominates, quality decides close
# calls. Two structural facts forced this:
#
# * the area term was unbounded, so a far container (tens of thousands
#   of ink px) outscored a near button by size alone - with NO boosts
#   active at all. AREA_SCORE_CAP stops paying for size past a generous
#   button (~100x60): bigger blobs are usually containers, whose
#   buttons are the real targets anyway.
# * the distance falloff was 1/(12+d) while boosts multiply up to ~2x
#   each at defaults, so a configured colour routinely overruled a 2x
#   distance advantage - although every description promises the colour
#   only "wins ties". DIST_FALLOFF=2 makes a 2x distance gap cost 4x,
#   which no single default boost can cross: boosts break ties, as
#   documented, instead of dominating.
AREA_SCORE_CAP = 6000.0
DIST_FALLOFF = 2.0


def _base_score(contrast, area, fill, dist):
    """One ranking number for an item. Higher = more clickable.

    Contrast times capped size times solidness, over distance squared.
    Only relative order matters (candidates are sorted); the absolute
    values are meaningless.
    """
    return (contrast * math.sqrt(min(area, AREA_SCORE_CAP))
            * (0.4 + 0.6 * fill) / (12.0 + dist) ** DIST_FALLOFF)

# An item counts as "the accent colour" in accent_only mode when at least
# this fraction of its pixels match (5% tolerates icons whose colour is a
# glyph or badge on a neutral body).
ACCENT_MIN_FRACTION = 0.05

# Smart (soft) accent matching. Pixels score a similarity 0..1 against the
# accent centre instead of a hard in/out tolerance box. A pixel at or
# above ACCENT_STRONG_SIM counts as a REAL match - that strict gate still
# drives accent_only exclusion and what follow memory may learn, so
# softening can never make unrelated items clickable. Below it, similar
# shades (lighter/darker, washed-out, hue-shifted) earn graded partial
# credit that lifts their ranking; colours with the same brightness AND
# vividness but a clearly different hue earn up to ACCENT_TONE_BONUS *
# accent_soft (~10-20% at default settings - a "looks related" nudge,
# never a win on its own).
ACCENT_STRONG_SIM = 0.55
ACCENT_TONE_BONUS = 0.25

# Follow memory tuning.
FOLLOW_COLOR_TOL = 18     # hue band (deg) for "same colour as remembered"
FOLLOW_COLOR_FRAC = 0.25  # item must be >= 25% that colour to count
FOLLOW_POS_SIM = 0.8      # strength of the same-place bonus (capped so a
                          # true colour match elsewhere can still win)
FOLLOW_POS_PAD = 48       # px around the remembered click that counts


class FollowMemory(object):
    """
    Remembers the last successfully snapped-to item so the next scans can
    prefer "more of the same".

    This is the accessibility form of target persistence: the user's own
    successful click teaches the tool what they are working on (a
    scrollbar thumb, a dialog button, a colour-coded cell), and similar
    items get a temporary, decaying scoring boost. Nothing is ever
    clicked autonomously; an expired memory changes nothing.
    """

    def __init__(self):
        self.when = 0.0        # perf_counter timestamp of the last snap
        self.x = 0             # screen coords of the snap point
        self.y = 0
        self.sig = None        # HSV centre of the item's median colour
        self.area = 0
        self.bw = 0
        self.bh = 0
        self.hits = 0          # successful snaps remembered this session

    def store(self, x, y, target):
        self.when = time.perf_counter()
        self.x, self.y = int(x), int(y)
        self.sig = getattr(target, "sig", None)
        self.area = getattr(target, "area", 0)
        self.bw = getattr(target, "bw", 0)
        self.bh = getattr(target, "bh", 0)
        self.hits += 1

    def context(self, origin_x, origin_y, follow_seconds):
        """
        Build the tuple scan_region consumes, in region coordinates:
        (sig_hsv, mem_x, mem_y, decay 0..1). None when expired/empty.

        A memory with no colour signature still counts: sig=None makes
        the colour-sim branch of the boost inert (it can never match),
        but the POSITION branch - "the same control, different state" -
        is exactly what a contrast-only session needs. Dropping the
        whole context here would silently kill position persistence for
        every user who never configured an accent colour.
        """
        if self.when <= 0.0:
            return None

        age = time.perf_counter() - self.when
        if follow_seconds <= 0 or age > follow_seconds:
            return None

        decay = max(0.0, 1.0 - age / float(follow_seconds))
        return (self.sig, self.x - int(origin_x), self.y - int(origin_y), decay)


def _merge_nearby(candidates, fragments, merge_distance,
                  min_area, max_area, max_dim, max_aspect, scale=1.0):
    """
    Group detected boxes that sit close together.

    Desktop items are often detected in pieces: a broken outline, an icon
    beside its text label, or fragments individually smaller than
    min_area. Pieces whose boxes are within merge_distance pixels are
    combined into one item so the cursor lands on the whole thing.

    Safety rule: a cluster is only combined when it contains at least one
    true fragment (a piece too small to snap to on its own). Two fully
    valid neighbours - say two adjacent buttons - are never merged, so
    the cursor can't land in the dead space between them. Clusters that
    would violate the size limits keep their original full members
    instead; lone small fragments are dropped.

    candidates / fragments entries:
        (score, Y0, X0, cl_px, dist, area, contrast, bw, bh)
    """
    # merge_distance is a virtual-px user setting; detected boxes are in
    # physical px of the captured region - compare like for like.
    merge_distance = merge_distance * scale
    pool = list(candidates) + list(fragments)
    n_full = len(candidates)
    n = len(pool)

    if n == 0:
        return candidates
    if n == 1:
        # A single candidate survives; a single fragment does not.
        return candidates

    # Entry layout: (score, Y0, X0, cl_px, dist, area, contrast, bw, bh)
    # -> index 7 is the WIDTH, index 8 the HEIGHT (a past swap of the
    # two broke gap measurement for every non-square item).
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
        ax0, ay0, ax1, ay1 = boxes[i]
        for j in range(i + 1, n):
            bx0, by0, bx1, by1 = boxes[j]
            gap_x = max(ax0 - bx1, bx0 - ax1, 0)
            gap_y = max(ay0 - by1, by0 - ay1, 0)
            if gap_x <= merge_distance and gap_y <= merge_distance \
                    and math.hypot(gap_x, gap_y) <= merge_distance:
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

        # Only rescue clusters that contain a sub-min_area fragment.
        # Fully valid items stay independent so the cursor always lands
        # on a real control, never between two of them.
        if all(m < n_full for m in members):
            out.extend(full_members)
            continue

        X0 = min(boxes[m][0] for m in members)
        Y0 = min(boxes[m][1] for m in members)
        X1 = max(boxes[m][2] for m in members)
        Y1 = max(boxes[m][3] for m in members)
        bw, bh = X1 - X0, Y1 - Y0

        shape_ok = (
            max(bw, bh) <= max_dim
            and max(bw, bh) <= max_aspect * max(1, min(bw, bh))
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
        dist = min(pool[m][4] for m in members)
        score = _base_score(contrast, area, fill, dist)
        out.append((score, Y0, X0, canvas, dist, area, contrast, bw, bh))

    return out


# v8.49: the colour-spec vocabulary moved to colorspec.py so config.py
# can validate an accent without importing numpy and the whole engine.
# The historical private names stay as aliases: every call site in this
# module, in assist.py and in gui.py, and every saved config file, keeps
# working exactly as before.
from colorspec import (ACCENT_PRESETS,  # noqa: F401  (re-exported for gui)
                       hsv_to_rgb,
                       parse_accent as _parse_accent,
                       parse_accents as _parse_accents)

# Re-exported for assist.py / gui.py, which import them from here. New code
# should import colorspec directly: the colour vocabulary is not part of the
# analysis engine, and pulling it from here drags numpy along with it.
parse_accent = _parse_accent
parse_accents = _parse_accents

# The module's public surface. Declaring it also tells static analysis that
# ACCENT_PRESETS and hsv_to_rgb are deliberate re-exports rather than unused
# imports (pyflakes honours __all__).
__all__ = [
    "ACCENT_PRESETS", "AREA_SCORE_CAP", "CONTRAST_METRIC_SCALE",
    "DIST_FALLOFF", "FollowMemory", "MotionTracker", "ScanResult",
    "SnapTarget", "_accent_fraction", "_accent_stats", "_parse_accent",
    "_parse_accents", "accent_coherent_of", "accent_matcher_of",
    "accent_soft_of", "accent_variants_of", "blend_similarity",
    "calibrate_accent", "ciede2000", "color_adapt_of", "hsv_to_rgb",
    "parse_accent", "parse_accents", "predict_motion", "predict_motion_3d",
    "scan_region", "set_log_sink", "suggest_accents",
]


def _soft_band(d, half, falloff):
    """
    1.0 while distance d is within the core half-width, then a linear
    fade to 0.0 across `falloff` more. falloff <= 0 degenerates to the
    hard box (classic behaviour). Works elementwise on numpy arrays or
    plain scalars.
    """
    if falloff <= 0:
        return np.where(d <= half, 1.0, 0.0)
    return np.clip(1.0 - (d - half) / falloff, 0.0, 1.0)


def _accent_similarity(h, s, v, ah, asat, av, tol, soft=0.0):
    """
    Soft similarity 0..1 between pixel colour(s) and one accent centre,
    elementwise (OpenCV-style HSV: h 0-179, s/v 0-255).

    soft = 0 reproduces the classic hard tolerance box exactly (1.0
    inside, 0.0 outside). soft > 0 ("smart colour matching", config
    accent_soft 1-100) extends a linear fade-out zone past every band,
    so close-but-not-exact shades score proportionally to how close
    they are instead of zero:

      * weighted geometric mean: hue leads (0.50), brightness follows
        (0.30), saturation (0.20) - lighter/darker, washed-out or
        slightly hue-shifted variants of the accent still score high
        (hover, pressed, dimmed and re-themed states);
      * hue is ignored for grey-ish accents (grey/white/black
        presets), where it carries no meaning;
      * a wildly different saturation (grey vs neon) collapses the
        score whatever the hue, so neutral items never masquerade as
        accent matches;
      * "same tone" bonus: a colour sharing BOTH the accent's
        brightness and vividness earns a little partial credit (up to
        ACCENT_TONE_BONUS * soft, ~10-20% at default settings) even
        when its hue is clearly different - a "looks related" nudge
        that ranks it above unrelated items, never a win on its own.
    """
    dh = np.abs(h - ah)
    dh = np.minimum(dh, 180.0 - dh)

    sv_band = tol * 2.2
    h_sim = _soft_band(dh, tol, tol * 2.0 * soft)
    s_sim = _soft_band(np.abs(s - asat), sv_band, sv_band * 2.0 * soft)
    v_sim = _soft_band(np.abs(v - av), sv_band, sv_band * 2.0 * soft)

    # Hue only means something when the accent itself is colourful.
    rel = min(1.0, float(asat) / 50.0)
    h_sim = h_sim * rel + (1.0 - rel)

    sim = (h_sim ** 0.50) * (s_sim ** 0.20) * (v_sim ** 0.30)

    if soft > 0:
        sim = sim + ACCENT_TONE_BONUS * soft * s_sim * v_sim \
            * (1.0 - h_sim)

    return np.minimum(sim, 1.0)


# ----------------------------------------------------------------------
# Perceptual matching (accent_matcher = "oklab", the default)
#
# OKLab (Bjoern Ottosson, 2020) is a perceptually uniform colour space:
# equal numeric distance ~ equal perceived difference, with lightness,
# chroma and hue properly separated. Two consequences for the accent
# engine:
#   * "hue is meaningless for grey accents" falls out of the maths
#     instead of needing the classic scorer's saturation-ratio hack,
#     and a fully saturated green can never ride a blue accent's
#     tolerance just because their s/v stats agree (a real false
#     positive class of the weighted-HSV matcher);
#   * the conversion is two small matrix multiplies plus a cube root -
#     vectorised with numpy it measures ~2x FASTER per frame than the
#     HSV path it replaces. No new dependency: the published formulae
#     (MIT reference implementations) are inlined below.
# ----------------------------------------------------------------------
OKLAB_WL = 1.6             # lightness forgiven more than hue/chroma
OKLAB_TOL_BASE = 0.05      # distance budget floor (OKLab units)
OKLAB_TOL_SOFT = 0.30      # ...plus this * accent_soft fraction
OKLAB_NEUTRAL_C = 0.05     # accent chroma below this reads as "grey"
OKLAB_NEUTRAL_ALLOW = 0.03 # ClearType/edge fringe allowance near grey
OKLAB_NEUTRAL_K = 2.0      # extra chroma penalty for neutral accents
OKLAB_BLEND_MIN_A = 0.25   # blend line: minimum accent ink amount
OKLAB_BLEND_EPS = 0.05     # blend line: max deviation (0..1 RGB)

_oklab_cache = {}


def _rgb01_to_oklab(px):
    """(...,3) float 0..1 RGB -> OKLab (L, a, b), elementwise."""
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


def _accent_oklab(ah, asat, av):
    """Cached ((L, a, b), chroma, rgb01) for one accent in OpenCV HSV."""
    key = (round(float(ah), 2), round(float(asat), 2), round(float(av), 2))
    hit = _oklab_cache.get(key)
    if hit is None:
        if len(_oklab_cache) > 128:
            _oklab_cache.clear()
        rgb = np.array(hsv_to_rgb(ah, asat, av), dtype=np.float32) / 255.0
        lab = _rgb01_to_oklab(rgb)
        hit = (lab, float(np.hypot(lab[1], lab[2])), rgb)
        _oklab_cache[key] = hit
    return hit


def blend_similarity(px_bgr01, acc_rgb01, bg_bgr01):
    """
    Anti-aliasing rescue, elementwise: score pixels that sit on the
    straight blend line between the item's local background and the
    accent colour. Rendered glyph/icon edges are exactly
    bg * (1 - t) + accent * t, so t is the pixel's "ink amount"; it is
    returned for pixels close enough to the line, 0.0 for everything
    else. Pale accent ink therefore matches on ANY background - even
    surfaces that push the blend result far outside any fixed colour
    tolerance - without widening the perceptual matcher.
    """
    acc = np.asarray(acc_rgb01, dtype=np.float32)[::-1]   # RGB -> BGR
    bg = np.asarray(bg_bgr01, dtype=np.float32)
    d = acc - bg
    denom = float(np.dot(d, d))
    if denom < 1e-4:
        return np.zeros(px_bgr01.shape[:-1], dtype=np.float32)
    t = np.sum((px_bgr01 - bg) * d, axis=-1) / denom
    proj = bg + t[..., None] * d
    res = np.sqrt(np.sum((px_bgr01 - proj) ** 2, axis=-1))
    # Cap at 1.0: a pixel past the pure accent on the blend line (the
    # estimated background drifting on gradients) must never score > 1.
    return np.where((t >= OKLAB_BLEND_MIN_A) & (res <= OKLAB_BLEND_EPS),
                    np.minimum(t, 1.0), 0.0).astype(np.float32)


# ----------------------------------------------------------------------
# Perceptual core, round 2 (v8.48).
#
# The matcher named "oklab" in config now measures colour difference
# with CIEDE2000 on CIELAB - the CIE recommendation, and what every
# serious colour project converges on (colour-science, scikit-image's
# deltaE_ciede2000, basic_colormath, hexcraft's default metric). OKLab
# Euclidean was already a large step up from weighted HSV, but it still
# let saturated impostors ride an accent's tolerance (green on blue)
# and disagreed with human judgement on near-neutrals. CIEDE2000's hue
# rotation term and chroma-dependent weighting fix exactly those two
# classes. Implemented dependency-free and vectorised, the same way the
# rest of this engine is: per-pixel cost is higher than a Euclidean
# distance, but patches are subsampled before matching (see
# _subsample_patch), so a typical item costs well under a millisecond.
# ----------------------------------------------------------------------

# CIEDE2000 distance budget: similarity fades linearly from 1.0 at
# distance 0 to 0.0 at the budget. dE < 1 is imperceptible, 1-2 needs a
# trained eye, > 5 is clearly different. Calibrated empirically
# (calib_hue.py): at the default soft of 60 the budget is ~23, which
# admits exact and close shades as REAL matches (dE <= ~10: darker and
# dimmed states), gives hover/lighter shades meaningful partial credit
# (dE ~15 -> ~0.3, still a real boost multiplier), and leaves
# wrong-hue impostors at ~0 (green ~75, red ~43, purple ~17 -> 0.26
# partial at most - never a gate pass). Washed-out pastels vs vivid
# near-hue impostors (washed blue dE 26 vs purple dE 17) are genuinely
# ambiguous in ANY colorimetric space - humans use context there - so
# both stay out of the strict gate at defaults and accent_soft exists
# precisely to pull the washed family in when the user asks for loose.
DE_TOL_BASE = 4.0
DE_TOL_SOFT = 32.0

# Brightness variants of one accent: CIELAB lightness offsets for the
# perceptual path, V (0-255) offsets for the classic HSV path. The
# canonical centre plus brighter and dimmer copies, two steps out. Hover,
# pressed, disabled and dimmed states of a control move mostly along
# lightness, so testing all five and taking the best rescues them
# without widening the hue tolerance at all (a green can still never
# ride a blue accent). Five vectorised distance evaluations over an
# already-converted patch - the conversion, not the distances, is the
# cost, and it is paid once per item.
ACCENT_L_VARIANTS = (0.0, 7.0, -7.0, 14.0, -14.0)
HSV_V_VARIANTS = (0.0, 18.0, -18.0, 36.0, -36.0)

# Illuminant adaptation (night light, HDR tone mapping, strong theme
# casts): the local background's chromaticity, capped this far in Lab
# a/b, is treated as the scene illuminant and subtracted from the
# pixels before matching - a von-Kries-lite white balance. The cap is
# what keeps a genuinely coloured backdrop (blue wallpaper) from
# erasing real colour differences. Scaled by ADAPT_STRENGTH so the
# correction stays conservative.
ADAPT_MAX_AB = 10.0
ADAPT_STRENGTH = 0.6

# Coherent-blob gate: accent-strong pixels must connect into one blob
# covering at least this share of themselves (and number at least this
# many pixels), otherwise they are dither speckle or compression noise
# and must not count as "containing the colour" - for boosting, for
# accent_only eligibility, or for never-click exclusion alike.
ACCENT_COHERENT_FRAC = 0.5
ACCENT_COHERENT_MIN = 8

# Patches larger than this many item pixels are block-averaged 2x2
# before matching: 4x fewer pixels to convert and compare (the single
# largest per-item cost), and the averaging itself dissolves ClearType
# subpixel fringes and dither patterns back toward the true colour.
# Small items keep every pixel - there is nothing to average away.
ACCENT_MAX_PIXELS = 3000

_lab_cache = {}


def _rgb01_to_lab(px):
    """(...,3) float 0..1 RGB -> CIELAB (L 0..100), elementwise, D65."""
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


def _accent_lab(ah, asat, av):
    """Cached (Lab, chroma, rgb01) for one accent in OpenCV HSV."""
    key = (round(float(ah), 2), round(float(asat), 2), round(float(av), 2))
    hit = _lab_cache.get(key)
    if hit is None:
        if len(_lab_cache) > 128:
            _lab_cache.clear()
        rgb = np.array(hsv_to_rgb(ah, asat, av), dtype=np.float32) / 255.0
        lab = _rgb01_to_lab(rgb)
        hit = (lab, float(np.hypot(lab[1], lab[2])), rgb)
        _lab_cache[key] = hit
    return hit


def ciede2000(lab1, lab2, kL=1.0, kC=1.0, kH=1.0):
    """CIEDE2000 colour difference, vectorised over (...,3) CIELAB.

    lab2 may be a single (3,) colour - it broadcasts. Follows Sharma's
    implementation notes (the same reference scikit-image implements):
    chroma-dependent G correction, hue rotation term, SL/SC/SH
    weighting. Returns the distance array, 0 for identical colours.
    """
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
    # h_diff is the UNWRAPPED hue difference: the mean-hue correction
    # below must test it BEFORE wrapping (testing the wrapped value is
    # always false, which silently breaks every pair straddling 0 -
    # i.e. the whole blue region the rotation term exists for).
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
    """Raw CIEDE2000 distances from pre-converted pixel Lab to one
    accent Lab, with the neutral-accent chroma penalty folded in.

    p_lab is converted ONCE per item by the caller and shared across
    every accent - converting per accent (as the old OKLab path did)
    re-ran the two matrix multiplies plus cube root per colour.
    neutral_chroma is the accent's own chroma: below ~8 the accent
    reads as grey, and pixels whose chroma drifts away pay an extra
    penalty so purple-tinted items cannot ride a grey accent.
    """
    d = ciede2000(p_lab, acc_lab)
    if neutral_chroma is not None and neutral_chroma < 8.0:
        cpx = np.hypot(p_lab[..., 1], p_lab[..., 2])
        extra = 2.0 * np.clip(cpx - (neutral_chroma + 1.5), 0.0, None)
        d = np.sqrt(d * d + extra * extra)
    return d


def _coherent_enough(mask):
    """True when the accent-strong pixels form a real blob, not speckle.

    Dither, compression noise and ClearType fringes scatter isolated
    strong pixels across an item; a genuine colour badge connects into
    one component. Tiny badges pass trivially (fewer pixels than the
    minimum cannot be speckle either way).
    """
    n = int(mask.sum())
    if n < ACCENT_COHERENT_MIN:
        return True
    _labels, info = _label_cells(mask)
    if not info:
        return False
    biggest = max(entry[1] for entry in info)
    return biggest >= ACCENT_COHERENT_FRAC * n


def _subsample_patch(sub_f32, mask):
    """Block-average a (h,w,3) float patch + bool mask down 2x2.

    Only for large patches (see ACCENT_MAX_PIXELS): 4x fewer pixels for
    every conversion and distance below, and the averaging dissolves
    subpixel-fringe and dither noise toward the true colour - the same
    reason image pyramids start every serious matcher. Degenerate masks
    fall back to the original patch instead of an empty one.
    """
    if int(mask.sum()) <= ACCENT_MAX_PIXELS:
        return sub_f32, mask
    h, w = mask.shape
    h2, w2 = (h // 2) * 2, (w // 2) * 2
    if h2 < 2 or w2 < 2:
        return sub_f32, mask
    s = sub_f32[:h2, :w2].reshape(h2 // 2, 2, w2 // 2, 2, 3)
    s = s.mean(axis=(1, 3))
    m = mask[:h2, :w2].reshape(h2 // 2, 2, w2 // 2, 2)
    m = m.mean(axis=(1, 3)) >= 0.5
    if not m.any():
        return sub_f32, mask
    return s.astype(np.float32), m


def accent_soft_of(cfgv):
    """accent_soft setting (0-100) as a 0..1 fraction, safely."""
    try:
        return min(1.0, max(0.0, float(cfgv.get("accent_soft", 60)) / 100.0))
    except (TypeError, ValueError):
        return 0.6


def accent_matcher_of(cfgv):
    """accent_matcher setting, normalised to "hsv" or "oklab".

    "oklab" is the perceptual matcher. Since v8.48 its distance is
    CIEDE2000 on CIELAB (see the round-2 block above), which ranks
    colours the way they actually look; the name stays so existing
    config files keep working.
    """
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
    """color_adapt: white-balance each item against its own background
    before matching, so night light and theme casts stop shifting the
    accent out of tolerance. On by default; turn off only for A/B
    comparison against the unadapted matcher."""
    return _bool_of(cfgv, "color_adapt", True)


def accent_variants_of(cfgv):
    """accent_variants: also test brighter/dimmer copies of the accent,
    so hover, pressed and dimmed states of a control match without
    widening the hue tolerance. Lightness-only, so a wrong hue can
    never ride it."""
    return _bool_of(cfgv, "accent_variants", True)


def accent_coherent_of(cfgv):
    """accent_coherent: accent-strong pixels must connect into a blob
    to count (see _coherent_enough). Off restores the old behaviour
    where scattered specks counted."""
    return _bool_of(cfgv, "accent_coherent", True)


def suggest_accents(img, max_suggestions=6):
    """
    Dominant-colour suggestions from a BGR screenshot region - the
    Accent Advisor behind the Detection & Colours tab's "Suggest from screen".

    Pixels are binned in OKLab (bins are even perceptual steps), each
    bin is ranked by coverage with a chroma preference so vivid UI
    accent colours surface above flat wallpaper, and a suggestion is
    the mean RGB of its bin. Returns [(rgb, fraction), ...], best
    first. Pure numpy, deterministic, no new dependency.
    """
    a = np.asarray(img)
    if a.ndim != 3 or a.shape[2] < 3 or a.size == 0:
        return []

    h, w = a.shape[:2]
    step = max(1, int(np.sqrt(float(h * w) / 24000.0)))
    a = a[::step, ::step, :3]
    px01 = a.astype(np.float32)[..., ::-1] / 255.0        # BGR -> RGB
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

    # Near-neutral clusters (wallpaper, page backgrounds) are noise for
    # an ACCENT advisor - keep them only as a fallback when the region
    # holds nothing colourful at all.
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
    """
    True when an item's median-colour signature (HSV centre) is a real
    match for any configured accent colour. Used to decide what the
    follow memory is allowed to learn when follow_learn = "accent": a
    misclick that snapped to some non-accent item must not poison the
    memory. With soft > 0, near shades of the accent still count
    (similarity >= ACCENT_STRONG_SIM), but mere "same brightness,
    wrong hue" partial credit never does. matcher = "oklab" scores the
    signature in the same perceptual space as the pixel matcher, so
    the learn gate and the click gate can never disagree.

    variants carries the accent_variants switch: brighter/dimmer copies
    of the accent are tested ONLY when that setting is on, exactly as
    the pixel matcher treats them. A switch the user turned off must
    stay off here too - the gate may never be looser than the matcher
    (that would let non-matching items into the memory) NOR stricter
    (that would starve it).
    """
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
            # The same strict gate the pixel matcher applies: a real
            # match means similarity >= ACCENT_STRONG_SIM, i.e. the
            # distance sits inside the strong share of the budget.
            if best <= (1.0 - ACCENT_STRONG_SIM) * tol_e:
                return True
        return False

    # Brightness variants, gated by the accent_variants switch exactly
    # like the oklab branch: the gate must accept everything the pixel
    # matcher can call a real match, never less - otherwise
    # successfully snapped items would starve the follow memory - and
    # it must refuse what the matcher refuses when the switch is off.
    # Brightness-only, same as pixels.
    for (ah, asat, av) in accents:
        for dV in (HSV_V_VARIANTS if variants else (0.0,)):
            vv = min(255.0, max(0.0, av + dV))
            sim = float(_accent_similarity(sh, ss, sv, ah, asat, vv, tol,
                                           soft))
            if sim >= ACCENT_STRONG_SIM:
                return True

    return False


def _accent_stats(img, cl_px, X0, Y0, accents, tol, soft=0.0,
                  matcher="hsv", coherent=False, adapt=False,
                  variants=False):
    """
    (mean_similarity, strong_fraction) of an item against ANY accent.

    img is BGR uint8; cl_px is the item's boolean pixel mask with its
    box origin at (X0, Y0).

    matcher = "hsv" is the classic path: matching happens in HSV, so
    tolerance behaves the way people expect around colours, and
    saturation/value get a wider band than hue because desktop themes
    vary item brightness a lot.

    matcher = "oklab" (with soft > 0) scores pixels with CIEDE2000 on
    CIELAB instead (see the round-2 block), plus a blend-line rescue:
    the item's local background (median of the non-item pixels inside
    its box - the control's own surface) defines the anti-aliasing
    blend line toward the accent, so pale accent ink on that surface
    counts even when the blend result is perceptually far from the
    pure accent.

    Three robustness upgrades apply to both paths:

    * large patches are block-averaged 2x2 first (faster AND cleaner -
      subpixel fringes and dither dissolve toward the true colour);
    * the mean is the best of the whole item and its edge band, so a
      thin accent-coloured border is not diluted away by a neutral
      interior ("the blue button" with a white middle still reads as
      blue);
    * with coherent=True, accent-strong pixels must connect into a blob
      to count at all (dither speckle must never make an item eligible,
      boostable, or excludable).

    adapt (white-balance the patch against its own background: night
    light and theme casts) and variants (brighter/dimmer accent copies
    for hover and pressed states - lightness/value-only, so a wrong
    hue can never ride them) work in BOTH paths: Lab lightness shifts
    in the perceptual path, V shifts plus RGB white balance in the
    classic path. Every colour switch therefore does something no
    matter which matching engine is selected.

    accent_tolerance scales the perceptual budget too (proportionally
    around the default 26, which behaves exactly as before), so the
    strictness knob is honoured by both engines instead of silently
    doing nothing under the default matcher.

    mean_similarity (0..1) is the soft-match average over the item's
    pixels and scales the scoring boost - "mostly the accent" beats "a
    speck of it", and (soft > 0) near shades earn graded partial
    credit. strong_fraction is the share of pixels that are REAL
    matches (similarity >= ACCENT_STRONG_SIM); that strict number
    drives accent_only exclusion, which partial credit must never
    loosen.
    """
    ph, pw = cl_px.shape
    sub = img[Y0:Y0 + ph, X0:X0 + pw].astype(np.float32) / 255.0
    sub, m = _subsample_patch(sub, cl_px)
    px = sub[m]

    if px.shape[0] == 0 or not accents:
        return 0.0, 0.0

    # Edge band = the mask's own 1 px perimeter. Computed inline so it
    # stays independent of the morphology primitives. For a bordered
    # button the perimeter IS the coloured part, so this is what stops
    # a neutral interior from diluting it away.
    inner = np.zeros_like(m)
    if m.shape[0] > 2 and m.shape[1] > 2:
        inner[1:-1, 1:-1] = (m[1:-1, 1:-1] & m[:-2, 1:-1] & m[2:, 1:-1]
                              & m[1:-1, :-2] & m[1:-1, 2:])
    edge = (m & ~inner)[m]
    use_edge = bool(edge.any() and int(edge.sum()) >= 4)

    # The item's local background (median of the non-item pixels in its
    # box): the control's own surface. Feeds the blend-line rescue, the
    # illuminant adaptation, and the classic-path white balance alike.
    bgm = sub[~m]
    bg = None
    if bgm.shape[0] >= 8:
        bg = np.median(bgm.reshape(-1, 3), axis=0)   # 0..1 BGR

    # accent_tolerance scales the perceptual budget around the default
    # 26 (which behaves exactly as before): the strictness knob works
    # under both matchers instead of going quiet under "oklab".
    tol_scale = max(0.15, min(3.5, float(tol) / 26.0))

    if matcher == "oklab" and soft > 0:
        # Convert the patch ONCE and share it across every accent:
        # the RGB->Lab chain (matrices plus cube root) is the single
        # most expensive per-item operation - converting per accent
        # would multiply it by the colour count for nothing.
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
                if not _coherent_enough(grid):
                    continue        # speckle, not a colour badge
            if mean > best_mean:
                best_mean = mean
            if strong > best_strong:
                best_strong = strong
        return best_mean, best_strong

    # Classic-path white balance (the color_adapt switch, engine
    # independent): scale each channel so the local background reads
    # as neutral grey, exactly like a camera's white balance. Same
    # idea as the Lab-side adaptation above, in RGB where the classic
    # path lives. Capped per channel so a strongly coloured backdrop
    # (blue wallpaper) can attenuate the correction, never invert it.
    pxc = px
    if adapt and bg is not None:
        ref = float(bg.mean())
        gain = ref / np.maximum(bg, 1e-3)
        gain = np.clip(gain, 0.5, 2.0).astype(np.float32)
        pxc = np.clip(px * gain, 0.0, 1.0)

    b, g, r = pxc[:, 0], pxc[:, 1], pxc[:, 2]  # images are BGR

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
            if not _coherent_enough(grid):
                continue
        if mean > best_mean:
            best_mean = mean
        if strong > best_strong:
            best_strong = strong

    return best_mean, best_strong


# Motion lead (smart follower): velocity is trusted only above this
# speed (px/s) - slower reads as a standing item and gets no lead - and
# only when every middle observation sits within this many px of the
# straight line between first and last (a direction change, or a
# different item scanned in between, disables the lead entirely).
MOTION_MIN_SPEED = 20.0
MOTION_MAX_DEVIATION = 12.0
MOTION_MIN_SPAN = 0.03   # s of history needed before a velocity is real


def predict_motion(obs, lead_ms, max_offset):
    """
    Linear lead for a moving target (scrollbars, seek bars, scrolling
    lists): where will the item be `lead_ms` from now?

    obs:
        Chronological [(t, x, y), ...] observations (perf_counter
        seconds, absolute screen px) of the item the scanner keeps
        choosing.
    Returns (ox, oy): offset to add to a snap point so the click lands
    on the item instead of where it was. (0.0, 0.0) when the history is
    too short, too slow, or inconsistent - standing items must behave
    exactly as before. The offset magnitude is capped at max_offset px
    so a wild history can never fling a click across the screen.
    """
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


# ----------------------------------------------------------------------
# Kalman snap follower (v8.49): 2D and 3D tracking for moving targets.
#
# predict_motion above is the legacy linear fit - first-to-last
# velocity with a straight-line gate. It is kept byte-for-byte because
# it is simple, predictable, and pinned by regression. Its weaknesses
# are structural: ONE deviating middle observation blinds it entirely
# (it returns zero until the history flushes), a single bad scan
# poisons the velocity, and it knows nothing about scale - a growing
# dialog and a shrunken thumbnail look identical to it.
#
# MotionTracker fixes all three with a constant-velocity Kalman
# filter, dependency-free (a handful of tiny matrix ops per update -
# microseconds next to a 16 ms scan):
#
#   dim=2: state (x, y, vx, vy) - the smarter 2D follower. Outliers
#     are rejected per observation (one bad scan costs a damped step,
#     not the whole track), and adaptive process noise lets the filter
#     swing through direction changes in two or three scans instead of
#     going blind until the deque flushes.
#   dim=3: state (x, y, s, vx, vy, vs) with s = ln(linear size) - the
#     3D follower. Scale is tracked alongside position: a sudden scale
#     jump means the scanner picked a DIFFERENT item, so the track
#     resets instead of aiming with a poisoned velocity. Uniform
#     scaling about the centre never moves the click point, which is
#     why predict() returns the position offset plus the scale ratio
#     separately instead of mixing them.
#
# The safety contract is identical to predict_motion in both dims:
# too slow -> zero, stale -> zero, capped at max_offset, and anything
# statistically absurd resets the track instead of producing a wild
# offset. Switching engines never changes what the click is allowed
# to do, only how well it follows.
# ----------------------------------------------------------------------

class MotionTracker(object):
    """Constant-velocity Kalman tracker for one followed item.

    dim=2 observes (x, y) screen px; dim=3 observes (x, y, size) with
    size a LINEAR size in px (sqrt of area) - stored internally as its
    logarithm so growing and shrinking are symmetric.
    """

    # Measurement variance: detection jitter is a few px per scan, and
    # ~0.05 in log-scale (5% size wobble).
    POS_R = 9.0
    SCALE_R = 0.0025
    # Process noise (white-noise acceleration): snappy enough to follow
    # a flicked scrollbar, calm enough to smooth detection jitter.
    POS_Q = 2500.0
    SCALE_Q = 0.02
    # Consecutive gated misses before the track is dropped outright.
    MISS_RESET = 3
    # No observation this long mirrors the legacy deque pruning (0.6 s
    # of history): the world moved on, so the track restarts.
    STALE_S = 0.6
    # A scale doubling/halving between two scans is not growth, it is a
    # different item under the scanner.
    SCALE_JUMP = 0.69
    # Absolute residual floors: below these, innovation is jitter, not
    # manoeuvre, however tight the covariance has become.
    POS_GATE_FLOOR = 4.0
    SCALE_GATE_FLOOR = 0.10

    def __init__(self, dim=2):
        if dim not in (2, 3):
            raise ValueError("MotionTracker dim is 2 or 3")
        self.dim = dim
        self.n = 2 * dim
        # Most recent raw observation, regardless of acceptance. Only
        # ever moves forward in time; lets a restarted track
        # dead-reckon its velocity from the last two raw points instead
        # of waiting for the filter to converge from zero. Deliberately
        # NOT part of reset(): a restart must still see the point
        # before it, and seeding only fires inside the staleness
        # window, so ancient history can never sneak back in.
        self._prev_obs = None
        self.reset()

    def reset(self):
        """Forget everything: the next observation starts a new track."""
        self.x = None            # state vector
        self.P = None            # covariance
        self.last_t = None
        self.updates = 0         # accepted observations
        self.misses = 0          # consecutive gated rejections
        self.q_mult = 1.0        # adaptive process-noise multiplier

    def _init(self, t, z):
        """Start a track at (t, z). Dead-reckons velocity from the
        previous raw observation when fresh; otherwise velocity starts
        fully uncertain so the second observation teaches it in one
        step. Init never rejects."""
        n = self.dim
        self.x = np.zeros(2 * n, dtype=np.float64)
        self.x[:n] = z
        # Position is trusted like a measurement; velocity starts
        # fully uncertain ((200 px/s)^2).
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
        """Observation tuple -> measured position vector (log-scale)."""
        if self.dim == 2:
            return np.array([float(pos[0]), float(pos[1])],
                            dtype=np.float64)
        s = float(pos[2])
        if not math.isfinite(s) or s <= 0.0:
            return None
        return np.array([float(pos[0]), float(pos[1]), math.log(s)],
                        dtype=np.float64)

    def update(self, t, pos):
        """Fold one observation in. Returns True when accepted.

        t is perf_counter seconds; pos is (x, y) or (x, y, size).
        Non-finite inputs, backwards timestamps and scale teleports
        never raise - they are ignored or restart the track.
        """
        try:
            t = float(t)
            z = self._to_state_pos(pos)
        except (TypeError, ValueError, IndexError):
            return False
        if z is None or not math.isfinite(t) or not np.all(np.isfinite(z)):
            return False

        # Raw history for dead-reckoning restarts: monotonic only, so
        # an out-of-order point can never become the seed. prev is the
        # point BEFORE this one (or None on the very first sighting).
        prev = self._prev_obs
        if prev is None or t > prev[0]:
            self._prev_obs = (t, z.copy())

        if self.last_t is None:
            return self._init(t, z)

        dt = t - self.last_t
        if dt <= 0.0:
            return False                    # out-of-order: ignore
        if dt > self.STALE_S:
            self.reset()                    # world moved on: fresh track
            return self.update(t, pos)

        n = self.dim
        if n == 3 and abs(z[2] - self.x[2]) > self.SCALE_JUMP:
            self.reset()                    # different item: fresh track
            return self.update(t, pos)

        # Predict with adaptive process noise (q_mult rides up through
        # manoeuvres and decays back in steady flight).
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

        # Gate per dimension: 3 sigma with an absolute floor, so a
        # converged filter still tolerates ordinary detection jitter.
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
                # Three rejections in a row is not noise, it is a new
                # reality (teleport, flick, re-acquired item): restart
                # AND dead-reckon from the last two raw points, so
                # genuinely fast motion re-acquires in one step instead
                # of bouncing off the init gate forever. Still capped
                # downstream, like every other fresh track. (prev is
                # the point before this one - the entry bookkeeping
                # above already moved _prev_obs onto the current point,
                # so hand the older one back for the seed.)
                self.reset()
                if prev is not None:
                    self._prev_obs = prev
                return self._init(t, z)
            return False                    # outlier: damped, not dead

        # Accepted: Joseph-form update (numerically stable), then adapt
        # the process noise to how surprising this observation was.
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
        """Current estimated screen speed in px/s, or 0.0."""
        if self.x is None:
            return 0.0
        n = self.dim
        return float(math.hypot(self.x[n], self.x[n + 1]))

    def predict(self, lead_ms, max_offset, min_speed=MOTION_MIN_SPEED):
        """Where the item will be `lead_ms` from now.

        dim=2 returns (ox, oy); dim=3 returns (ox, oy, scale_ratio).
        (0.0, 0.0[, 1.0]) when the history is too short, too slow, or
        has recent rejections - standing items behave exactly as
        before. The offset magnitude is capped at max_offset px, and
        the scale ratio is clipped to 4x either way, so a diverged
        filter can never fling a click across the screen or onto a
        phantom size. Recent misses damp the lead instead of killing
        it: one bad scan halves the step, two quarter it, three reset
        the track.
        """
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


def predict_motion_3d(obs, lead_ms, max_offset):
    """Kalman lead for a moving AND scaling target.

    obs: chronological [(t, x, y, size), ...] with size a LINEAR size
    in px (sqrt of area). Returns (ox, oy, scale_ratio): the offset to
    add to a snap point plus the predicted size change (1.0 = same
    size). (0.0, 0.0, 1.0) under the same conditions predict_motion
    returns zero - plus a scale teleport, which means the scanner
    picked a different item and the track restarts.
    """
    if lead_ms <= 0 or len(obs) < 2 or max_offset <= 0:
        return 0.0, 0.0, 1.0
    tr = MotionTracker(dim=3)
    for item in obs:
        try:
            t, x, y, s = item
        except (TypeError, ValueError):
            return 0.0, 0.0, 1.0
        tr.update(t, (x, y, s))
    return tr.predict(lead_ms, max_offset)


def _accent_fraction(img, cl_px, X0, Y0, accents, tol, soft=0.0,
                      matcher="hsv", coherent=False, adapt=False,
                      variants=False):
    """
    Best soft-match fraction (0..1) of an item's pixels near ANY
    accent colour - the simple entry point into _accent_stats for
    callers that only need boost strength (follow-memory colour sim).
    """
    return _accent_stats(img, cl_px, X0, Y0, accents, tol, soft, matcher,
                         coherent, adapt, variants)[0]


# Cursor-weighted calibration (v8.49): half weight at this many px from the
# cursor, and nothing further out than CALIB_MIN_WEIGHT contributes. The
# values track the search radius the console 'v' command captures with.
CALIB_HALF_WEIGHT_PX = 60.0
CALIB_MIN_WEIGHT = 0.02


def _weighted_mean(values, weights):
    w = float(np.sum(weights))
    if w <= 0.0:
        return float(np.mean(values)) if len(values) else 0.0
    return float(np.sum(values * weights) / w)


def _weighted_percentile(values, weights, pct):
    """Percentile where each sample carries a weight (the cursor falloff)."""
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
    """Measure how one accent reads on THIS screen right now.

    img is a BGR uint8 region with the cursor at (cx, cy); every pixel
    is scored against the accents with the live matcher, and the
    distance distribution is reported along with the accent_soft value
    that would put the 95th percentile of near-accent pixels inside the
    budget. Powers the console 'v' (calibrate) command: the user points
    at the app they work in, and gets a number tuned to their display
    instead of a guess.

    Returns {"pixels", "p50", "p95", "strong_frac", "suggested_soft"}
    with distances in CIEDE2000 units (or 1-similarity for the hsv
    path). None when there is nothing to measure.
    """
    if not accents or img is None:
        return None
    a = np.asarray(img)
    if a.ndim != 3 or a.shape[2] < 3 or a.size == 0:
        return None

    # v8.49: MEASURE AROUND THE CURSOR, not the whole capture.
    #
    # (cx, cy) was accepted, documented as "a region with the cursor at
    # (cx, cy)", and then discarded with `_ = (cx, cy)` - so the report was
    # a distribution over the entire radius, which at the default 150 px is
    # mostly wallpaper. That made p50 and p95 describe the desktop rather
    # than the control the user pointed at, and pushed suggested_soft to its
    # maximum: the console 'v' command was telling low-vision users to set
    # the matcher to its loosest value based on their background.
    #
    # Weight by distance from the cursor instead of cropping, so a control
    # bigger than the window still contributes, but nearby pixels dominate.
    h, w = a.shape[:2]
    cx = min(max(int(cx), 0), max(0, w - 1))
    cy = min(max(int(cy), 0), max(0, h - 1))
    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2).astype(np.float32)
    # half weight at CALIB_HALF_WEIGHT_PX, ~zero beyond ~3x that
    weight = 1.0 / (1.0 + (dist / CALIB_HALF_WEIGHT_PX) ** 2)

    px = a.reshape(-1, 3).astype(np.float32) / 255.0
    wt = weight.reshape(-1)
    keep = wt >= CALIB_MIN_WEIGHT
    if int(keep.sum()) >= 64:
        px, wt = px[keep], wt[keep]
    if px.shape[0] > 20000:
        # Same subsampling philosophy as the matcher: a stable,
        # deterministic slice, not every pixel.
        step = px.shape[0] // 20000 + 1
        px, wt = px[::step], wt[::step]

    if matcher == "oklab" and soft > 0:
        p_lab = _rgb01_to_lab(px[:, ::-1])
        best = None
        for (ah, asat, av) in accents:
            lab, chroma, _ = _accent_lab(ah, asat, av)
            d = _de_terms(p_lab, lab, chroma)
            best = d if best is None else np.minimum(best, d)
        dist = best
        tol_now = DE_TOL_BASE + DE_TOL_SOFT * max(0.0, min(1.0, float(soft)))
        strong = float(_weighted_mean(
            (dist <= (1.0 - ACCENT_STRONG_SIM) * tol_now).astype(np.float32),
            wt))
        unit = "dE"
    else:
        b, g, r = px[:, 0], px[:, 1], px[:, 2]
        mx = np.maximum(np.maximum(r, g), b)
        mn = np.minimum(np.minimum(r, g), b)
        d = mx - mn
        safe = np.where(d > 0, d, 1.0)
        h = np.where(d == 0, 0.0, np.where(
            mx == r, ((g - b) / safe) % 6.0,
            np.where(mx == g, ((b - r) / safe) + 2.0,
                     ((r - g) / safe) + 4.0))) * 30.0
        h %= 180.0
        s = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0.0) * 255.0
        v = mx * 255.0
        best = None
        for (ah, asat, av) in accents:
            sim = _accent_similarity(h, s, v, ah, asat, av, tol, soft)
            dist = 1.0 - sim
            best = dist if best is None else np.minimum(best, dist)
        dist = best
        strong = float(_weighted_mean(
            (dist <= 1.0 - ACCENT_STRONG_SIM).astype(np.float32), wt))
        unit = "1-sim"

    if dist.size == 0:
        return None
    p50 = float(_weighted_percentile(dist, wt, 50.0))
    p95 = float(_weighted_percentile(dist, wt, 95.0))
    # "strong matches now" is a share of the CURSOR NEIGHBOURHOOD, weighted
    # the same way, so it describes the control under the pointer.
    if unit == "dE":
        # Inverted through the same scaled budget the matcher applies
        # (see _accent_stats), so the suggestion already accounts for
        # the user's accent_tolerance.
        scale = max(0.15, min(3.5, float(tol) / 26.0))
        suggested = int(round(min(1.0, max(0.0, (p95 / scale - DE_TOL_BASE)
                                             / DE_TOL_SOFT)) * 100.0))
    else:
        suggested = int(round(min(1.0, max(0.0, float(soft))) * 100.0))
    return {"pixels": int(px.shape[0]), "p50": p50, "p95": p95,
            "strong_frac": strong, "suggested_soft": suggested,
            "unit": unit, "cursor": (cx, cy)}


# How close (px) an item's detected box must be to a screen-edge
# border to count as "at the edge". NOT 2: outlines within ~6 px of a
# screen edge are unmeasurable (blur radius 4 + 2 px ink clearing + cell
# rounding), so a flush control's detected box starts several px
# inside. A 2 px test would only ever fire for items the detector
# cannot see - the exact items the edge rules exist for.
EDGE_TOUCH_PX = 8


def _touches_screen_edge(Y0, X0, Y1, X1, w, h, edge_flags):
    """True when a pixel bbox touches a capture-region border that IS a
    true screen edge. Scrollbars and docked bars live exactly there;
    items merely near the capture border (clipped mid-screen content)
    do not count."""
    if not edge_flags:
        return False
    try:
        el, et, er, eb = edge_flags
    except (TypeError, ValueError):
        return False
    return ((el and X0 <= EDGE_TOUCH_PX)
            or (et and Y0 <= EDGE_TOUCH_PX)
            or (er and X1 >= w - EDGE_TOUCH_PX)
            or (eb and Y1 >= h - EDGE_TOUCH_PX))


def _is_clipped(Y0, X0, bw, bh, w, h, edge_flags):
    """
    True when the box touches a capture-region border that is NOT a
    screen border - i.e. the item likely continues outside the capture
    and we only see part of it. Items at a true screen edge (scrollbars,
    docked bars) are complete, not clipped.
    """
    el = et = er = eb = False
    if edge_flags is not None:
        el, et, er, eb = edge_flags

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
                deadline_ms=None):
    """
    Look for the best click-assist target near the cursor.

    img:
        (H,W,3) uint8 BGR screenshot region.
    cx, cy:
        Cursor position inside img.
    cfgv:
        Config values dictionary.
    radius:
        Search radius in pixels.
    follow_ctx:
        Optional (sig_hsv, mem_x, mem_y, decay) from FollowMemory, in
        region coordinates. Similar/same-place items get a boost.
    edge_flags:
        Optional (left, top, right, bottom): which borders of the capture
        region are true screen edges. Items at a screen edge get relaxed
        shape limits (scrollbar thumbs are long and thin by nature) and
        are not treated as clipped.
    deadline_ms:
        Scan budget in milliseconds. None reads scan_budget_ms from the
        settings (default 350 ms); callers that already bound their own
        latency can pass an explicit value.

    Returns ScanResult.
    """
    if deadline_ms is None:
        try:
            deadline_ms = float(cfgv.get("scan_budget_ms", 350))
        except Exception:
            deadline_ms = 350.0
    deadline_ms = min(max(deadline_ms, 60.0), 2000.0)
    t0 = time.perf_counter()
    deadline = t0 + deadline_ms / 1000.0

    a = img.astype(np.float32)
    h, w = a.shape[:2]

    bg = _box_blur(a, BLUR_WIN)

    # Pixels that differ strongly from their local background.
    diff = np.sqrt(((a - bg) ** 2 * _CH_WEIGHTS).sum(axis=2))

    # Luminance normalisation (Weber-style): the eye notices relative
    # edges. The same delta-L is obvious on a dark background and
    # invisible on a bright one, so score diff relative to the local
    # background brightness. Mid-grey regions are unchanged by design.
    if bool(cfgv.get("luminance_norm", True)):
        lum = (bg * _CH_WEIGHTS).sum(axis=2)
        diff = diff * np.clip(NORM_K / (lum + NORM_C), NORM_MIN, NORM_MAX)

    thr = float(cfgv["contrast_threshold"])
    adapt_scale = 1.0

    # Adaptive threshold: let the region's own edge energy lower the ink
    # bar when everything here is inherently dim (dark themes, washed-out
    # documents). Never raises it above the stock baseline - but an
    # explicitly RAISED user setting is respected as-is: min() would
    # otherwise drag a deliberate 200 straight back down to the scene
    # energy, making "higher needs crisper edges" a lie whenever
    # adaptive is on (the default). Hard floor keeps flat dither and
    # noise from becoming ink.
    if bool(cfgv.get("adaptive_threshold", True)) and thr <= ADAPTIVE_BASE:
        energy = float(np.percentile(diff, ADAPTIVE_PERCENTILE))
        adapted = max(ADAPTIVE_FLOOR, min(thr, energy * ADAPTIVE_K))
        adapt_scale = adapted / thr if thr > 0 else 1.0
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

    # Morphological closing before grouping (v8.64). Anti-aliased and
    # sub-pixel rendered outlines break into several thin pieces; without
    # this they fragment into multiple detected items (or fall under
    # min_area and vanish entirely). Closing bridges row/column gaps up
    # to `gap` px with a cross structuring element - diagonal neighbours
    # are never joined, so corner-touching controls stay separate. The
    # operation is monotone (adds pixels only), so weak hysteresis seeds
    # cannot be thinned below their ratio floor by an erosion step.
    # Reach follows "Glue nearby pieces together" (merge_distance, in
    # virtual px, DPI-scaled like every other distance) at half strength:
    # closing handles hairline breaks, box-level merging stays with
    # _merge_nearby. gap == 0 (setting off) reproduces the old pipeline
    # exactly.
    merge_distance = float(cfgv.get("merge_distance", 0) or 0)
    scale = 1.0
    if merge_distance > 0:
        try:
            from win32rt import get_dpi_scale as _get_dpi_scale
            scale = _get_dpi_scale()
        except Exception:
            scale = 1.0
        # The capture is in PHYSICAL pixels; merge_distance is a virtual
        # (DPI-independent) user setting, so the pixel reach scales with
        # the display factor.
        gap = int(min(3, max(1, round(0.5 * merge_distance * scale))))
        ink = _close_gaps(ink, gap)
        ink_w = _close_gaps(ink_w, gap)

    # Coarse cell grid.
    ph = (CS - h % CS) % CS
    pw = (CS - w % CS) % CS

    ink_p = np.pad(ink, ((0, ph), (0, pw))) if (ph or pw) else ink
    inkw_p = np.pad(ink_w, ((0, ph), (0, pw))) if (pw or ph) else ink_w

    gh, gw = ink_p.shape[0] // CS, ink_p.shape[1] // CS

    ratio = ink_p.reshape(gh, CS, gw, CS).mean(axis=(1, 3))
    ratio_w = inkw_p.reshape(gh, CS, gw, CS).mean(axis=(1, 3))

    strong = ratio >= CELL_WALL
    weak = ratio_w >= CELL_WEAK

    walls = _grow_cells(strong, weak)
    walls = _erode(_dilate(walls, 1), 1)

    # Objects are walls plus enclosed non-background areas.
    full = np.ones((gh, gw), dtype=bool)
    obj_cells = ~_flood_bg(walls, full)

    min_area = int(cfgv["min_area"])
    max_area = int(cfgv["max_area"])
    max_dim = int(cfgv["max_dim"])
    # When the adaptive threshold lowered the ink bar, relax the
    # contrast gate proportionally - rescued dim items must still clear
    # a real quality floor. Scaled to the relative-core metric below so
    # user-facing min_contrast keeps its documented meaning. The
    # relaxation is for the DEFAULT floor only: a min_contrast the user
    # deliberately raised (above the stock value) is an explicit
    # promise and is honoured as-is, exactly like a raised
    # contrast_threshold above - adaptive_threshold lowers a bar, it
    # never overrules one.
    user_min_contrast = float(cfgv["min_contrast"])
    if user_min_contrast > MIN_CONTRAST_BASE:
        min_contrast = user_min_contrast * CONTRAST_METRIC_SCALE
    else:
        min_contrast = max(MIN_CONTRAST_FLOOR,
                           user_min_contrast * adapt_scale) \
            * CONTRAST_METRIC_SCALE
    max_aspect = 10.0

    finals = []
    labels, info = _label_cells(obj_cells)
    pending = [(labels, info, 0)]
    guard = 0

    # Recursively split overly large blobs, e.g. whole windows or text blocks.
    while pending and guard < 10:
        guard += 1

        if time.perf_counter() > deadline:
            break

        lab, inf, depth = pending.pop()

        for cid, count, gy0, gx0, gy1, gx1 in inf:
            bw = (gx1 - gx0) * CS
            bh = (gy1 - gy0) * CS

            if depth < 2 and (bw > 200 or bh > 200 or count * CS * CS > 25000):
                cmask = (lab == cid)

                # Split using background reachable from outside the blob.
                sub_obj = cmask & ~_flood_bg(walls, cmask)
                slab, sinfo = _label_cells(sub_obj)

                if sinfo and not (len(sinfo) == 1 and sinfo[0][1] >= count * 0.9):
                    pending.append((slab, sinfo, depth + 1))
                    continue

                # Sealed large blob: keep inner items, treat large open
                # interior areas as background.
                free = cmask & ~walls
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

            finals.append((lab, cid, gy0, gx0, gy1, gx1))

    candidates = []
    fragments = []

    for lab, cid, gy0, gx0, gy1, gx1 in finals:
        if time.perf_counter() > deadline:
            break

        Y0, X0 = gy0 * CS, gx0 * CS
        Y1, X1 = min(gy1 * CS, h), min(gx1 * CS, w)

        if Y1 <= Y0 or X1 <= X0:
            continue

        bw, bh = X1 - X0, Y1 - Y0

        # Items at a true screen edge (scrollbars, docked bars) are long
        # and thin by nature; relax the shape rules only there. The
        # threshold is EDGE_TOUCH_PX, not 2: a flush item's detected
        # box starts inside the blur dead zone, so 2 px would only ever
        # match items too close to the edge to be measured at all.
        at_edge = False
        if edge_flags is not None:
            el, et, er, eb = edge_flags
            at_edge = ((X0 <= EDGE_TOUCH_PX and el)
                       or (Y0 <= EDGE_TOUCH_PX and et)
                       or (X1 >= w - EDGE_TOUCH_PX and er)
                       or (Y1 >= h - EDGE_TOUCH_PX and eb))

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
        # Fragments below this can never be rescued by merging; it
        # follows min_area down so a deliberately lowered gate keeps
        # working instead of silently keeping the stock 64 px floor.
        # At the default min_area the floor is unchanged.
        if too_small and area < min(MIN_FRAG_AREA, min_area):
            continue

        fill = area / float(bw * bh)

        if fill < MIN_FILL:
            # Hollow at a true screen edge: the screen-side outline is
            # physically unmeasurable (local background estimation has
            # nothing beyond the border to compare against), so a low
            # fill here is expected evidence of a flush control - a
            # scrollbar, a docked bar - not of noise. Complete it to
            # its bounding rectangle (which also aims the snap at its
            # middle instead of one surviving edge). Hollow anywhere
            # else is still dropped: mid-screen hollowness means a
            # broken outline or texture, and completing those would
            # invent items.
            if _touches_screen_edge(Y0, X0, Y1, X1, w, h, edge_flags):
                cl_px = np.ones((Y1 - Y0, X1 - X0), dtype=bool)
                area = int(cl_px.sum())
                if area > max_area:
                    continue
                fill = 1.0
            else:
                continue

        # Relative edge-core measurement: percentile over pixels within
        # the item's own top diff range. Blur and subtraction are linear
        # operations, so this scales exactly with true edge magnitude for
        # same-shape items - faint and bright, dark-mode and light-mode
        # are measured with one consistent ruler (a fixed-threshold
        # pixel set instead changes composition as the ink bar moves).
        sub_d = diff[Y0:Y1, X0:X1]
        d_vals = sub_d[cl_px]

        if d_vals.size == 0:
            continue

        d_max = float(d_vals.max())
        core = d_vals >= (d_max * CONTRAST_CORE_FRAC)

        if int(core.sum()) >= 8:
            contrast = float(np.percentile(d_vals[core], 90))
        else:
            contrast = d_max * 0.7

        if contrast < min_contrast:
            continue

        score = _base_score(contrast, area, fill, dist)
        entry = (score, Y0, X0, cl_px, dist, area, contrast, bw, bh)

        if too_small:
            fragments.append(entry)
        else:
            candidates.append(entry)

    # Merge pieces of one visual item (broken outlines, icon + label
    # pairs, fragments too small on their own) so the snap lands on the
    # whole item instead of one shard of it. (merge_distance was read and
    # DPI-scaled for pixel closing above; reused unchanged here.)
    if merge_distance > 0 and (fragments or len(candidates) > 1):
        candidates = _merge_nearby(
            candidates, fragments, merge_distance,
            min_area, max_area, max_dim, max_aspect, scale,
        )

    # Accent colour priority / exclusivity (opt-in). The boost only
    # re-ranks; accent_only additionally drops non-matching items.
    # v8.27: ONE accent field - "accent_color" itself accepts an
    # unlimited ";"-separated list, so the old accent_color2 /
    # accent_boost2 pair is gone.
    # v8.49: score the NEAREST candidates first. The colour stage is the
    # part that can be cut short by the scan deadline, and which item gets
    # cut used to be whatever order connected-component labelling happened
    # to produce. Distance order means a blown budget costs the far items
    # that were unlikely to win anyway - and it makes the "unscored"
    # accounting below meaningful instead of arbitrary.
    candidates.sort(key=lambda c: c[4])

    # How many items the colour gates could not score before the deadline.
    # "Unscored" must never be confused with "scored zero": the two gates
    # below read a zero in opposite directions, and conflating them is what
    # made exclude_color silently invert under load.
    unscored = [0]

    accents = _parse_accents(cfgv.get("accent_color", "off"))
    accent_boost = float(cfgv.get("accent_boost", 0.0) or 0.0)
    accent_only = bool(cfgv.get("accent_only", False)) and bool(accents)
    soft = accent_soft_of(cfgv)  # smart colour matching, 0..1
    matcher = accent_matcher_of(cfgv)  # "oklab" (default) or classic "hsv"
    # Round-2 colour handling: white-balance, shade variants and the
    # coherent-blob gate. Read once per scan, applied to every item and
    # to the follow-memory colour sim below.
    adapt = color_adapt_of(cfgv)
    variants = accent_variants_of(cfgv)
    coherent = accent_coherent_of(cfgv)

    if accents and candidates and (accent_boost > 0 or accent_only):
        tol = float(cfgv.get("accent_tolerance", 26))
        accented = []

        for cand in candidates:
            frac = 0.0
            strong = 0.0
            scored = time.perf_counter() <= deadline
            if scored:
                frac, strong = _accent_stats(
                    img, cand[3], cand[2], cand[1], accents, tol, soft,
                    matcher, coherent, adapt, variants)
            else:
                unscored[0] += 1

            # Exclusion stays strict: only REAL matches (not partial
            # "similar tone" credit) keep an item clickable. An UNSCORED
            # item is not a match either, so accent_only fails CLOSED -
            # which was already the behaviour, but it was silent, and the
            # field symptom was "assistance stopped working" with nothing in
            # the log to explain it.
            if accent_only and (not scored or strong < ACCENT_MIN_FRACTION):
                continue  # not one of the colours the user asked for

            mult = 1.0
            if frac > 0 and accent_boost > 0:
                mult *= (1.0 + accent_boost * frac)
            if mult != 1.0:
                cand = (cand[0] * mult,) + cand[1:]
            accented.append(cand)

        candidates = accented

    # Hard exclusion ("never clickable" colours, config exclude_color).
    # Same strictness as accent_only: an item is dropped when a REAL
    # match (>= ACCENT_MIN_FRACTION of its pixels at similarity >=
    # ACCENT_STRONG_SIM) exists - soft partial credit can never keep
    # an excluded item clickable, and exclusion outranks every boost.
    excludes = _parse_accents(cfgv.get("exclude_color", "off"))
    if excludes and candidates:
        tol = float(cfgv.get("accent_tolerance", 26))
        kept = []

        for cand in candidates:
            strong = 0.0
            scored = time.perf_counter() <= deadline
            if scored:
                _mean, strong = _accent_stats(
                    img, cand[3], cand[2], cand[1], excludes, tol, soft,
                    matcher, coherent, adapt, variants)
            else:
                unscored[0] += 1
            # SAFETY (v8.49): an UNSCORED item is dropped, not kept.
            #
            # exclude_color is documented as a hard promise - "never
            # clickable", "exclusion outranks every accent boost". Before
            # v8.49 `strong` was initialised to 0.0 and only overwritten
            # inside the deadline check, so a scan that ran out of budget
            # left every item reading as "no excluded colour present" and
            # the engine snapped happily to the exact colour the user had
            # forbidden. That is a safety promise failing OPEN, silently,
            # under load - the worst possible direction for a tool whose
            # users cannot see well enough to notice.
            #
            # Failing closed costs one unassisted click, which passes
            # straight through to Windows: that is precisely what exclusion
            # means, so the degradation is the feature, not a regression.
            if not scored or strong >= ACCENT_MIN_FRACTION:
                continue
            kept.append(cand)

        candidates = kept

    # Follow memory ("colour following"): prefer items that look like or
    # sit where the last successfully snapped item was.
    if follow_ctx is not None and candidates:
        f_boost = float(cfgv.get("follow_boost", 1.0) or 0.0)
        sig, mem_x, mem_y, decay = follow_ctx

        if f_boost > 0 and decay > 0:
            followed = []

            for cand in candidates:
                sim = 0.0

                if sig is not None and time.perf_counter() <= deadline:
                    # Follow-memory colour sim stays classic (no soft
                    # credit): the remembered EXACT colour must beat its
                    # own hover/theme variants; the position bonus
                    # already covers "same control, different state".
                    # It still gets the subsample speedup and the
                    # coherent-blob gate - dither speckle must never
                    # re-acquire a memory.
                    # sig None = a position-only memory (contrast-only
                    # session): the colour branch is inert by definition,
                    # so it is skipped rather than fed a [None] accents
                    # list (which would crash _accent_stats).
                    frac = _accent_fraction(img, cand[3], cand[2], cand[1],
                                            [sig], FOLLOW_COLOR_TOL,
                                            coherent=coherent)
                    if frac >= FOLLOW_COLOR_FRAC:
                        sim = frac
                else:
                    # A ranking nudge only: an unscored item simply gets no
                    # follow boost. Safe in either direction, but counted so
                    # the log line below can say how much of the colour
                    # stage was actually skipped.
                    unscored[0] += 1

                bx0, by0 = cand[2], cand[1]
                bx1, by1 = bx0 + cand[7], by0 + cand[8]   # +bw, +bh
                if (bx0 - FOLLOW_POS_PAD <= mem_x <= bx1 + FOLLOW_POS_PAD
                        and by0 - FOLLOW_POS_PAD <= mem_y <= by1 + FOLLOW_POS_PAD):
                    sim = max(sim, FOLLOW_POS_SIM)

                if sim > 0:
                    cand = (cand[0] * (1.0 + f_boost * decay * sim),) + cand[1:]
                followed.append(cand)

            candidates = followed

    if unscored[0]:
        # Loud, and once per scan: the two colour gates fail CLOSED when
        # they cannot measure, so the visible symptom is "assistance
        # stopped" or "fewer items", and support needs the evidence.
        _log("Colour stage cut short: %d item(s) went unscored before the "
             "%.0f ms scan budget ran out. accent_only and exclude_color "
             "fail closed for those items - lower the search radius, or "
             "raise the scan budget, if this repeats."
             % (unscored[0], (deadline - t0) * 1000.0))

    ms = (time.perf_counter() - t0) * 1000.0

    if not candidates:
        return ScanResult("none", None, ms)

    # Prefer fully visible items and items occupying a decent share of
    # region - but only as a nudge, not a second size term. The old
    # (1 + 2*vis) could double a big item's score on top of its area
    # term, letting far containers outrank near buttons a third time
    # over; (1 + vis) caps the whole preference at 1.5x.
    region_area = float(h * w)
    boosted = []

    for score, Y0, X0, cl_px, dist, area, contrast, bw, bh in candidates:
        clipped = _is_clipped(Y0, X0, bw, bh, w, h, edge_flags)
        vis = min(0.5, area / region_area)
        score *= (1.0 + vis) * (0.6 if clipped else 1.0)
        boosted.append((score, Y0, X0, cl_px, dist, area, contrast, bw, bh))

    candidates = boosted
    candidates.sort(key=lambda c: -c[0])

    for _s, Y0, X0, cl_px, dist, area, contrast, bw, bh in candidates[:3]:
        ys, xs = np.nonzero(cl_px)
        xs = xs.astype(np.float32) + X0
        ys = ys.astype(np.float32) + Y0

        pt = _meanshift(xs, ys, cx, cy)

        if pt is None:
            continue

        tcx, tcy = pt
        ddx = tcx - cx
        ddy = tcy - cy
        move = math.hypot(ddx, ddy)

        if move > radius + 10:
            continue

        ms = (time.perf_counter() - t0) * 1000.0

        # Median colour of the item's pixels, as an HSV centre. Median
        # (not mean) so the background halo around the item does not
        # skew the remembered colour. Feeds the follow memory.
        sig = None
        try:
            body = img[Y0:Y0 + cl_px.shape[0], X0:X0 + cl_px.shape[1]][cl_px]
            if body.shape[0] > 0:
                med = np.median(body.astype(np.float32), axis=0)  # BGR
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
    return ScanResult("none", None, ms)


