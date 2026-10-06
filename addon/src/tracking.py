"""Target persistence and motion tracking for the addon.

Ported from the main app's vision.py: FollowMemory (target lock-on),
predict_motion (legacy linear lead) and MotionTracker (gated
constant-velocity Kalman filter). Kept dependency-free beyond numpy so
the addon stays as light as it is today.

The safety contract shared by both predictors: too slow -> zero, stale
-> zero, capped at max_offset px, and anything statistically absurd
resets the track instead of producing a wild offset. Standing items
behave exactly as before.
"""

import math
import time

import numpy as np

MOTION_MIN_SPEED = 20.0
MOTION_MAX_DEVIATION = 12.0
MOTION_MIN_SPAN = 0.03   # s of history needed before a velocity is real


class FollowMemory(object):
    """
    Remembers the last successfully locked target so the next frames can
    prefer "more of the same" instead of flipping between similar items.

    A successful snap teaches the tracker what the user is working on;
    similar blobs get a temporary, decaying scoring boost. An expired
    memory changes nothing.
    """

    def __init__(self):
        self.when = 0.0        # perf_counter timestamp of the last snap
        self.x = 0             # capture-region coords of the snap point
        self.y = 0
        self.area = 0          # blob area in px
        self.bw = 0            # bounding-box width
        self.bh = 0            # bounding-box height
        self.hits = 0          # successful snaps remembered this session

    def store(self, x, y, rect, area):
        """Remember the chosen blob (rect = (x, y, w, h) in region coords)."""
        self.when = time.perf_counter()
        self.x, self.y = int(x), int(y)
        self.rect = tuple(int(v) for v in rect)
        self.area = int(area)
        self.bw = int(rect[2])
        self.bh = int(rect[3])
        self.hits += 1

    def forget(self):
        self.when = 0.0
        self.area = 0
        self.bw = 0
        self.bh = 0

    def context(self, follow_seconds):
        """Return (rect, area, decay 0..1) or None when expired/empty."""
        if self.when <= 0.0 or self.bw <= 0:
            return None
        age = time.perf_counter() - self.when
        if follow_seconds <= 0 or age > follow_seconds:
            return None
        decay = max(0.0, 1.0 - age / float(follow_seconds))
        return (self.rect, self.area, decay)


def score_blob(distance_sq, area, rect, memory, focus_area_sq):
    """
    Score one candidate blob; higher wins. Replaces the old
    "bare-nearest contour" pick, which flipped selection between two
    similar targets whenever jitter moved one a pixel closer.

    Components (all cheap, all vectorised-friendly scalars):
      * distance: closeness to the crosshair, normalised by the focus
        area (so 0..~1, smaller is better);
      * size: bigger blobs are more likely the real item than specks;
      * fill: how much of the bounding box is actual mask - solid icons
        beat scattered noise;
      * memory: overlap with the last locked target gets a decaying
        boost so the lock persists through occlusion and neighbours.
    """
    dist_term = math.sqrt(max(distance_sq, 0.0))
    norm = math.sqrt(max(focus_area_sq, 1.0))
    proximity = 1.0 - min(dist_term / norm, 1.0)          # 0..1, 1 = centred

    w, h = max(rect[2], 1), max(rect[3], 1)
    fill = min(area / float(w * h), 1.0)                  # 0..1

    size_bonus = min(math.log1p(area) / 12.0, 1.0)        # ~0..1

    score = 2.0 * proximity + 0.6 * fill + 0.4 * size_bonus

    if memory is not None:
        mem_rect, mem_area, decay = memory
        mx, my, mw, mh = mem_rect
        ix = max(min(rect[0] + rect[2], mx + mw) - max(rect[0], mx), 0)
        iy = max(min(rect[1] + rect[3], my + mh) - max(rect[1], my), 0)
        inter = ix * iy
        union = w * h + mw * mh - inter
        iou = inter / float(union) if union > 0 else 0.0
        area_sim = 1.0 - min(abs(math.log1p(area) - math.log1p(mem_area)) / 3.0, 1.0)
        score += decay * (3.0 * iou + 0.5 * area_sim)

    return score


def predict_motion(obs, lead_ms, max_offset):
    """
    Linear lead for a moving target: where will the item be `lead_ms`
    from now?

    obs: chronological [(t, x, y), ...] observations (perf_counter
    seconds, region-relative px) of the item the scanner keeps choosing.
    Returns (ox, oy): offset to add to the aim point so the move leads
    the target instead of chasing where it was. (0.0, 0.0) when the
    history is too short, too slow, or inconsistent - standing items
    must behave exactly as before. The magnitude is capped at
    max_offset px so a wild history can never fling the cursor.
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


class MotionTracker(object):
    """Constant-velocity Kalman tracker for one followed item (dim=2).

    State (x, y, vx, vy). Outliers are rejected per observation (one bad
    scan costs a damped step, not the whole track), and adaptive process
    noise lets the filter swing through direction changes in two or
    three scans instead of going blind until the history flushes.
    """

    # Measurement variance: detection jitter is a few px per scan.
    POS_R = 9.0
    # Process noise (white-noise acceleration): snappy enough to follow
    # a flicked target, calm enough to smooth detection jitter.
    POS_Q = 2500.0
    # Consecutive gated misses before the track is dropped outright.
    MISS_RESET = 3
    # No observation this long: the world moved on, so the track restarts.
    STALE_S = 0.6
    # Absolute residual floor: below this, innovation is jitter, not
    # manoeuvre, however tight the covariance has become.
    POS_GATE_FLOOR = 4.0

    def __init__(self):
        self.n = 4
        # Most recent raw observation, regardless of acceptance. Lets a
        # restarted track dead-reckon its velocity from the last two raw
        # points instead of waiting for the filter to converge from zero.
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

    def _r_vec(self):
        return np.array([self.POS_R, self.POS_R], dtype=np.float64)

    def _q_base(self):
        return np.array([self.POS_Q, self.POS_Q], dtype=np.float64) * self.q_mult

    def _init(self, t, z):
        """Start a track at (t, z). Dead-reckons velocity from the
        previous raw observation when fresh; otherwise velocity starts
        fully uncertain so the second observation teaches it in one
        step. Init never rejects."""
        self.x = np.zeros(4, dtype=np.float64)
        self.x[:2] = z
        self.P = np.diag(np.concatenate(
            [self._r_vec(), np.full(2, 40000.0)]))
        self.updates = 1
        prev = self._prev_obs
        if prev is not None:
            pt, pz = prev
            if pz.shape == z.shape and 0.0 < t - pt <= self.STALE_S:
                self.x[2:] = (z - pz) / (t - pt)
                self.updates = 2
        self.last_t = t
        self.misses = 0
        self.q_mult = 1.0
        return True

    def update(self, t, pos):
        """Fold one observation in. Returns True when accepted.

        t is perf_counter seconds; pos is (x, y) region-relative px.
        Non-finite inputs and backwards timestamps never raise - they
        are ignored or restart the track.
        """
        try:
            t = float(t)
            z = np.array([float(pos[0]), float(pos[1])], dtype=np.float64)
        except (TypeError, ValueError, IndexError):
            return False
        if not math.isfinite(t) or not np.all(np.isfinite(z)):
            return False

        # Raw history for dead-reckoning restarts: monotonic only, so
        # an out-of-order point can never become the seed.
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

        # Predict with adaptive process noise (q_mult rides up through
        # manoeuvres and decays back in steady flight).
        F = np.eye(4, dtype=np.float64)
        F[:2, 2:] = np.eye(2, dtype=np.float64) * dt
        qb = self._q_base()
        Q = np.zeros((4, 4), dtype=np.float64)
        Q[:2, :2] = np.diag(qb * dt ** 3 / 3.0)
        Q[:2, 2:] = np.diag(qb * dt ** 2 / 2.0)
        Q[2:, :2] = np.diag(qb * dt ** 2 / 2.0)
        Q[2:, 2:] = np.diag(qb * dt)
        xp = F.dot(self.x)
        Pp = F.dot(self.P).dot(F.T) + Q

        # Gate: 3 sigma with an absolute floor, so a converged filter
        # still tolerates ordinary detection jitter.
        R = self._r_vec()
        S_diag = np.maximum(np.diag(Pp)[:2] + R, 1e-9)
        y = z - xp[:2]
        gate = np.maximum(3.0 * np.sqrt(S_diag), self.POS_GATE_FLOOR)
        if np.any(np.abs(y) > gate):
            self.misses += 1
            if self.misses >= self.MISS_RESET:
                # Three rejections in a row is not noise, it is a new
                # reality (teleport, re-acquired item): restart AND
                # dead-reckon from the last two raw points.
                self.reset()
                if prev is not None:
                    self._prev_obs = prev
                return self._init(t, z)
            return False                    # outlier: damped, not dead

        # Accepted: Joseph-form update (numerically stable), then adapt
        # the process noise to how surprising this observation was.
        H = np.zeros((2, 4), dtype=np.float64)
        H[:, :2] = np.eye(2, dtype=np.float64)
        S = H.dot(Pp).dot(H.T) + np.diag(R)
        try:
            K = Pp.dot(H.T).dot(np.linalg.inv(S))
        except np.linalg.LinAlgError:
            return False
        self.x = xp + K.dot(y)
        I_KH = np.eye(4, dtype=np.float64) - K.dot(H)
        self.P = I_KH.dot(Pp).dot(I_KH.T) \
            + K.dot(np.diag(R)).dot(K.T)
        normed = float(np.max(np.abs(y) / gate))
        self.q_mult = 16.0 if normed > 0.5 else max(1.0, self.q_mult * 0.5)
        self.last_t = t
        self.updates += 1
        self.misses = 0
        return True

    def speed(self):
        """Current estimated speed in px/s, or 0.0."""
        if self.x is None:
            return 0.0
        return float(math.hypot(self.x[2], self.x[3]))

    def predict(self, lead_ms, max_offset, min_speed=MOTION_MIN_SPEED):
        """Where the item will be `lead_ms` from now: (ox, oy).

        (0.0, 0.0) when the history is too short, too slow, or has
        recent rejections - standing items behave exactly as before.
        The offset magnitude is capped at max_offset px, so a diverged
        filter can never fling the cursor across the screen. Recent
        misses damp the lead instead of killing it: one bad scan halves
        the step, two quarter it, three reset the track.
        """
        try:
            lead = float(lead_ms) / 1000.0
        except (TypeError, ValueError):
            return 0.0, 0.0
        if lead <= 0 or max_offset <= 0 or self.x is None \
                or self.updates < 2:
            return 0.0, 0.0

        vx, vy = float(self.x[2]), float(self.x[3])
        if math.hypot(vx, vy) < min_speed:
            return 0.0, 0.0

        damp = 1.0 if self.misses == 0 else (
            0.5 if self.misses == 1 else 0.25)
        ox, oy = vx * lead * damp, vy * lead * damp
        mag = math.hypot(ox, oy)
        if mag > max_offset:
            k = max_offset / mag
            ox, oy = ox * k, oy * k
        return ox, oy
