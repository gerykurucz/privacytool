"""Assistance engine: the low-level mouse hook, the click workers for
mode 1 (classic) and mode 2 (guide), hotkey actions, cursor glide,
follow-memory gating, and start_app() which wires the threads up.

Only the left mouse button is ever assisted; every other button passes
straight through to Windows. The right button can additionally fire the
programmable mouse2 side actions - a short press fires mouse2_action, a
hold of at least MOUSE2_HOLD_SECONDS fires mouse2_hold_action instead -
always alongside, never suppressed."""

import math
import os
import queue
import secrets
import threading
import time
from collections import deque

import numpy as np

import vision
import online
from core import IS_WINDOWS, log
from hotkeys import (ACTION_IDS, build_hotkey_table, build_macro_table,
                     effective_mode_key)
from recordings import (RecordingStore, MAX_STEPS as REC_MAX_STEPS,
                        MAX_RECORDINGS as REC_MAX, STEP_KEY, STEP_MOVE,
                        STEP_BUTTON, BTN_LEFT, BTN_RIGHT, BTN_MIDDLE,
                        PHASE_DOWN, PHASE_UP)
from vision import (FollowMemory, scan_region, accent_soft_of,
                    accent_matcher_of, accent_variants_of, _parse_accents,
                    _sig_matches_accents)
from input_backend import make_input_backend

if IS_WINDOWS:
    # v8.49: an EXPLICIT import list, not `from win32rt import *`.
    #
    # The star import made ~90% of this module unanalysable - every Win32
    # constant, struct and handle arrived anonymously, so a static check
    # could only say "may be undefined" (78 such reports) and a renamed
    # constant in win32rt.py surfaced as a NameError at click time rather
    # than at import time. In the one module that swallows and re-injects
    # a user's clicks, "fails at import" is much better than "fails while
    # your button is down".
    #
    # ctypes / wintypes are imported directly rather than inherited from
    # win32rt's namespace: relying on a star import for a stdlib module is
    # how a file stops being readable.
    import ctypes
    import ctypes.wintypes as wt
    from win32rt import (
        CaptureBackend, GetMessage, HC_ACTION, HOOKPROC, INPUT, INPUT_MOUSE,
        KBDLLHOOKSTRUCT, LLKHF_INJECTED, LLMHF_INJECTED,
        LLMHF_LOWER_IL_INJECTED, MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP,
        MSG, MSLLHOOKSTRUCT, PostThreadMessage, RegisterHotKey,
        SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN, SM_XVIRTUALSCREEN,
        SM_YVIRTUALSCREEN, UnregisterHotKey, VK_CONTROL, VK_LWIN, VK_MENU,
        VK_RBUTTON, VK_SHIFT, WH_KEYBOARD_LL, WH_MOUSE_LL, WM_HOTKEY,
        WM_KEYDOWN, WM_KEYUP, WM_LBUTTONDOWN, WM_LBUTTONUP, WM_MOUSEMOVE,
        WM_QUIT, WM_RBUTTONDOWN, WM_RBUTTONUP, get_cursor_pos,
        get_dpi_scale, inject_combo, inject_mouse, kernel32, move_cursor,
        setup_dpi_awareness, user32,
    )

# How long the right button must be held to count as a HOLD (fires
# mouse2_hold_action) instead of a short press (fires mouse2_action).
MOUSE2_HOLD_SECONDS = 0.45

# Motion lead: hard cap on the predicted offset, so a wild history can
# never fling a click across the screen (vision.predict_motion caps).
MOTION_MAX_OFFSET = 80.0

# v8.46 recorder: consecutive cursor moves inside this window MERGE
# into one step (the newest position wins), so a smooth drag costs
# ~20 steps/second instead of one step per hardware event.
REC_MOVE_MERGE_S = 0.05

# Mouse messages the recorder captures, mapped to (button, phase).
# Literal message codes so the table exists on every platform (the
# hooks that feed it only run on Windows). The double-click message
# records as a second left-DOWN: down/up/down/up with the recorded
# rhythm replays as a real double-click.
_MOUSE_REC_MAP = {
    0x0201: (BTN_LEFT, PHASE_DOWN),      # WM_LBUTTONDOWN
    0x0202: (BTN_LEFT, PHASE_UP),        # WM_LBUTTONUP
    0x0203: (BTN_LEFT, PHASE_DOWN),      # WM_LBUTTONDBLCLK
    0x0204: (BTN_RIGHT, PHASE_DOWN),     # WM_RBUTTONDOWN
    0x0205: (BTN_RIGHT, PHASE_UP),       # WM_RBUTTONUP
    0x0207: (BTN_MIDDLE, PHASE_DOWN),    # WM_MBUTTONDOWN
    0x0208: (BTN_MIDDLE, PHASE_UP),      # WM_MBUTTONUP
}


class App(object):
    def __init__(self, cfg, identity=None):
        self.cfg = cfg
        self.identity = identity

        # v8.27: assistance is always available (no master switch) and
        # every start begins PAUSED - Launch is the only gate.
        self.running = False

        self.stop = threading.Event()
        self.ready = threading.Event()

        self.click_q = queue.Queue()

        # Mode-1 suppression bookkeeping: every suppressed left DOWN
        # appends one FIFO entry {"x", "y", "up"}; its physical UP
        # marks the entry, and the click's job removes it when done.
        # A list (not a single slot) so rapid_click_snap can keep
        # several clicks in flight without losing the exactly-once
        # safety net for any of them.
        self.pending_classics = []

        self.worker_active = False
        self.scanner_dead = False
        self.fail_count = 0

        self.pause_until = 0.0
        self._slow_log_at = 0.0
        self.last_lbutton_time = 0.0
        self.rbutton_down_time = 0.0
        self.snap_count = 0
        self.pass_count = 0

        self.last_snap_time = 0.0
        self.last_snap_pos = None

        self.dpi_scale = 1.0

        # Per-INSTANCE (v8.49): this used to be a class attribute mutated
        # through self, so every App shared one cache and a logout/login
        # cycle inherited up to 2 s of the previous session's display
        # topology. A class-level mutable default is a bug waiting for the
        # second instance.
        self._vs_cache = {"t": 0.0, "v": None}

        self.hook = None
        self.proc_ref = None
        self.thread_id = None

        self._capture = CaptureBackend(cfg.get("capture_backend", "auto"))
        # v8.50: click DELIVERY is a backend too. Default "win32" is the
        # exact SendInput/SetCursorPos path used since v1 (bit-for-bit);
        # "interception" delivers at the driver layer for games that
        # ignore synthetic input, and degrades back to win32 on any
        # problem so a half-installed setup can never eat a click.
        self._input = make_input_backend(cfg)
        self.follow = FollowMemory()

        # physical left-button state, tracked from the hook (used by
        # hold-to-follow: a snap-time lock only while you keep holding)
        self._lbtn_down = False

        # physical right-button state, tracked from the hook: a short
        # press fires mouse2_action, a hold of at least
        # MOUSE2_HOLD_SECONDS fires mouse2_hold_action - never both
        self._rbtn_down = False
        self._rbtn_armed = False        # press began while armed
        self._rbtn_hold_done = False    # hold action already fired
        self._rbtn_press_id = 0         # generation: cancels stale timers
        self._rbtn_lock = threading.Lock()

        self._hk_always = []
        self.local_binds = []
        self._local_map = {}          # vk -> action id (pass-through keys)
        self._key_held = set()        # repeat filtering for the key hook
        self.input_focused = False    # true while a GUI text field has focus
        self.key_hook = None
        self.key_proc_ref = None

        # macros: trigger -> injected combo (worker thread injects)
        self.macro_q = queue.Queue()
        self._macros = []
        self._macro_map = {}

        # macro recordings (macros.json): library + live capture buffer
        self.rec_store = RecordingStore()
        self._rec_buffer = None       # list while recording, else None
        self._rec_last_t = 0.0
        self._rec_last_move = 0.0     # merge window for cursor moves
        self._rec_combos = set()      # (mods, vk) of record start/stop
        self._rec_full = False
        self.play_target_rid = None   # GUI selection / last played

        # playback transport: loop/until-stopped support
        self._play_cancel = threading.Event()
        self._play_busy = False       # a rec job is injecting right now
        self._play_looping = False    # current job loops until stopped
        self._play_rid = None         # recording the current job plays

        # auto-click: the one feature that acts with no user gesture.
        # _auto_count is the session safety cap already spent, _auto_at
        # the last absolute click point (the repeat guard), and
        # _auto_next when the worker may act again.
        self._auto_count = 0
        self._auto_at = None
        self._auto_next = 0.0
        self._auto_lock = threading.Lock()
        self._auto_armed = False      # armed after the colour check passed
        self._auto_done = False       # cap reached; say it once, stop

        # motion lead: recent (t, x, y) observations of whatever item
        # the click workers keep choosing (the follow worker does not
        # feed this - its scans are its own business). _tracker is the
        # same history through a Kalman filter, position plus scale,
        # for the motion_3d engine.
        self._track = deque(maxlen=32)
        self._tracker = vision.MotionTracker(dim=3)

        # follow-lock subsystem (hold-follow / mouse2 actions)
        self.follow_lock = None           # {"active", "accent", "source", "misses"}
        self._follow_stable = 0           # consecutive no-move scans (backoff)

        # centre-watch follow subsystem ("Keep the cursor on it"): while
        # the switch is on and an item was picked in the watched square,
        # this dict holds {"x", "y", "sig", "when", "misses", "stable"}.
        # It lives apart from follow_lock: that one drags the user's
        # cursor around during a hold - this one only parks the cursor
        # on the moving item when the user is not touching the buttons.
        self._center_follow = None
        self._pick_at = None              # candidate seen once (arming)
        self._pick_at_time = 0.0

        # own process id: clicks inside our own windows/dialogs are
        # never assisted (see _fg_is_own)
        self._own_pid = os.getpid()

        # presence (account-sharing detector): one nonce per run,
        # beaten to the Discord webhook while assistance is launched
        self._presence_nonce = secrets.token_hex(8)
        self._hb_sent = False
        self._bye_sent = False

    def is_recording(self):
        """True while a macro recording is armed (public read-only view of
        the capture buffer, so the GUI poller no longer reaches into
        app._rec_buffer)."""
        return self._rec_buffer is not None

    def presence_hash(self):
        """Row hash of the entitlement key (the e-mail): two machines
        signed into the same Discord account beat the same key, which
        is exactly the sharing we detect."""
        if not self.identity:
            return None
        return online.row_hash(self.identity)

    def run_presence_worker(self):
        """Beat the Discord presence webhook while LAUNCHED.

        Paused = a goodbye beat, so a closed/paused session frees the
        account immediately instead of after the window expires.
        Best-effort: missed beats just look like gaps.

        The cadence is a build-time constant (online.presence_interval_
        seconds), NOT a setting: a user-writable 0 used to turn the whole
        account-sharing detector off from config.ini."""
        idh = self.presence_hash()
        was_running = None
        while not self.stop.is_set():
            secs = online.presence_interval_seconds()
            if not idh or not online.presence_webhook():
                if self.stop.wait(30):
                    break
                continue
            # edge-triggered: beat the moment assistance launches and
            # bye the moment it pauses, so sharing is visible within
            # seconds of the second session starting and a paused
            # session never looks "live" for up to a whole window
            if self.running and was_running is not True:
                if online.post_presence(self.cfg, idh,
                                        self._presence_nonce):
                    self._hb_sent = True
                    self._bye_sent = False
                was_running = True
                continue
            if not self.running and was_running is not False:
                if self._hb_sent and not self._bye_sent:
                    if online.post_presence(self.cfg, idh,
                                            self._presence_nonce,
                                            bye=True):
                        self._bye_sent = True
                was_running = False
                continue
            was_running = bool(self.running)
            if self.stop.wait(max(1, secs)):
                break
            if self.running:
                if online.post_presence(self.cfg, idh,
                                        self._presence_nonce):
                    self._hb_sent = True
                    self._bye_sent = False
            elif self._hb_sent and not self._bye_sent:
                if online.post_presence(self.cfg, idh,
                                        self._presence_nonce, bye=True):
                    self._bye_sent = True
        if idh and self._hb_sent and not self._bye_sent:
            online.post_presence(self.cfg, idh, self._presence_nonce,
                                 bye=True)

    def _fg_is_own(self):
        """True when the foreground window belongs to Snappy AI itself
        (main GUI, popups, file dialogs). Assistance must stay out of
        the tool's own interface."""
        try:
            fg = user32.GetForegroundWindow()
            if not fg:
                return False
            pid = wt.DWORD()
            user32.GetWindowThreadProcessId(fg, ctypes.byref(pid))
            return pid.value == self._own_pid
        except Exception:
            return False

    def radius_px(self):
        return int(round(float(self.cfg.get("radius", 150)) * self.dpi_scale))

    def _virtual_screen(self):
        """Virtual-screen rect, cached 2 s: four Win32 syscalls per
        grab added up across every scan of every session for nothing -
        display topology changes far slower than that."""
        now = time.perf_counter()
        if self._vs_cache["v"] is not None and \
                now - self._vs_cache["t"] < 2.0:
            return self._vs_cache["v"]
        v = (user32.GetSystemMetrics(SM_XVIRTUALSCREEN),
             user32.GetSystemMetrics(SM_YVIRTUALSCREEN),
             user32.GetSystemMetrics(SM_CXVIRTUALSCREEN),
             user32.GetSystemMetrics(SM_CYVIRTUALSCREEN))
        self._vs_cache["t"] = now
        self._vs_cache["v"] = v
        return v

    def grab_around(self, x, y, radius):
        """
        Capture a square around (x, y).
        Returns (img, cx, cy, origin, edges) or (None, None, None,
        None, None). img is BGR uint8; origin is the region's (left,
        top) on the virtual screen; edges is (left, top, right, bottom)
        - which region borders are true screen edges. Per-call values:
        the click workers and the follow worker run concurrently and
        must never share this state through self.
        """
        pad = radius + 12
        left = x - pad
        top = y - pad
        side = 2 * pad + 1

        vx, vy, vw, vh = self._virtual_screen()

        l = max(left, vx)
        t = max(top, vy)
        r = min(left + side, vx + vw)
        b = min(top + side, vy + vh)

        gw = r - l
        gh = b - t

        if gw < 40 or gh < 40:
            return None, None, None, None, None

        origin = (int(l), int(t))
        # Which of the region's borders are true screen edges (scrollbars
        # and docked bars live there and are not "clipped" items).
        edges = (l == vx, t == vy, r == vx + vw, b == vy + vh)

        img = self._capture.grab(l, t, r, b)

        if img is None:
            return None, None, None, None, None

        return img, x - l, y - t, origin, edges

    def scan_near(self, x, y, state=None, track=None):
        """
        Scan around cursor and return SnapTarget or None.

        track: optional deque fed with (t, abs_x, abs_y) observations of
        the chosen target - the motion-lead history. Only the click
        workers pass it; the follow worker's scans stay out of it.
        """
        if state is not None and state.get("abandoned"):
            return None

        # "Watch the screen centre only": the search box lives at the
        # middle of the virtual screen, fixed, no matter where the cursor
        # is - for kiosk-style layouts whose items never move. A click
        # that lands outside the box (plus the reach the user configured)
        # passes through untouched, exactly like a click over empty space
        # in the normal mode.
        watch_center = False
        try:
            watch_center = bool(self.cfg.get("watch_center_only", False))
        except Exception:
            watch_center = False
        if watch_center:
            # Applies to every assisted path - classic snap, guide and
            # the hold-follow worker alike: with the switch on, the
            # whole product watches only the screen centre.
            vx, vy, vw, vh = self._virtual_screen()
            mx = vx + vw // 2
            my = vy + vh // 2
            # The watched square is exactly the classic screen-centre
            # capture: "search distance" is read as the SIDE length of
            # the box, default 150 -> a 150x150 window fixed at the
            # middle, scaled with DPI like every other distance here.
            half = max(24, int(round(
                float(self.cfg.get("radius", 150)) * self.dpi_scale))) // 2
            # A press outside the box is not assistance territory at all:
            # mark it and let the caller replay the click untouched at
            # the pointer - no scanning, no snapping toward the middle.
            if abs(x - mx) > half or abs(y - my) > half:
                if state is not None:
                    state["center_pass"] = True
                return None
            # Inside the box: always analyse the full centre square,
            # anchored on the screen middle regardless of where the
            # cursor actually is.
            cap = max(48, half * 2)
            img, cx, cy, origin, edges = self.grab_around(mx, my, cap)
            if img is None:
                return None
            follow_ctx = None
            if bool(self.cfg.get("follow_enabled")):
                follow_ctx = self.follow.context(
                    origin[0], origin[1],
                    float(self.cfg.get("follow_seconds", 20))
                )
            try:
                res = scan_region(img, cx, cy, self.cfg.values, cap,
                                  follow_ctx=follow_ctx,
                                  edge_flags=edges)
            except Exception as exc:
                self.fail_count += 1
                log("scan error: %r" % (exc,))
                if self.fail_count >= 5:
                    self.scanner_dead = True
                    log("Scanner disabled after repeated errors. "
                        "Clicks pass through.")
                return None
            self.fail_count = 0
            if res.kind == "target" and res.target is not None:
                # SnapTarget stores region-relative dx/dy (see the main
                # path below, which feeds them straight into SetCursorPos
                # at the pointer); no abs_x attribute exists.
                ax = origin[0] + res.target.dx
                ay = origin[1] + res.target.dy
                track = self._track
                if track is not None:
                    now = time.perf_counter()
                    track.append((now, ax, ay))
                    while track and now - track[0][0] > 0.6:
                        track.popleft()
                    try:
                        area = float(getattr(res.target, "area", 0) or 0)
                        if area > 0.0:
                            self._tracker.update(
                                now, (ax, ay, math.sqrt(area)))
                    except Exception:
                        pass
                # "Keep the cursor on it": any scan that found an item
                # inside the watched square arms/refreshes the centre
                # follow - both the click workers and the follow worker
                # itself call scan_near, so a moving plane keeps the
                # lock alive without needing another click. The gate
                # lives in run_follow_worker (switch, buttons, pick
                # radius), so arming here stays cheap and safe.
                if bool(self.cfg.get("center_follow", False)):
                    prev = self._center_follow
                    if (prev is not None
                            and math.hypot(ax - prev["x"],
                                           ay - prev["y"]) > 3.0):
                        # the item actually moved between scans: this
                        # is a live tracking cycle, drop the backoff
                        self._follow_stable = 0
                    self._center_follow = {
                        "x": ax, "y": ay,
                        "sig": res.target.sig,
                        "when": time.perf_counter(),
                        "misses": 0,
                    }
                return res.target
            return None

        # The capture is ALWAYS the full radius the user asked for. An
        # older perf governor shrank it to 60% whenever a scan ran over
        # 90 ms, which silently broke the "search distance in pixels"
        # promise (and only on the manual path - auto-click has always
        # scanned its whole auto_click_radius), so the same radius
        # reached different distances depending on what happened to be
        # on screen. Latency is already bounded by scan_region's own
        # 120 ms deadline, and slow scans are reported instead of being
        # paid for with reach.
        radius = self.radius_px()
        cap = max(48, int(radius))

        img, cx, cy, origin, edges = self.grab_around(x, y, cap)

        if state is not None and state.get("abandoned"):
            return None

        if img is None:
            return None

        follow_ctx = None
        if bool(self.cfg.get("follow_enabled")):
            follow_ctx = self.follow.context(
                origin[0], origin[1],
                float(self.cfg.get("follow_seconds", 20))
            )

        try:
            res = scan_region(img, cx, cy, self.cfg.values, cap,
                              follow_ctx=follow_ctx,
                              edge_flags=edges)
        except Exception as exc:
            self.fail_count += 1
            log("scan error: %r" % (exc,))

            if self.fail_count >= 5:
                self.scanner_dead = True
                log("Scanner disabled after repeated errors. Clicks pass through.")

            return None

        self.fail_count = 0

        if res.ms > 90 and time.perf_counter() - self._slow_log_at > 30.0:
            # Support evidence, not a governor: the scan used its whole
            # radius (that is the setting doing its job) and simply
            # took long, so a slow machine can be told apart from a
            # misconfigured one instead of the reach being cut silently.
            self._slow_log_at = time.perf_counter()
            log("Slow scan: %.0f ms at radius %d px. The full search "
                "distance is always scanned - lower the radius if "
                "clicks feel late." % (res.ms, cap))

        if state is not None and state.get("abandoned"):
            return None

        if res.kind == "target" and res.target is not None:
            if track is not None:
                now = time.perf_counter()
                ax, ay = x + res.target.dx, y + res.target.dy
                track.append((now, ax, ay))
                while track and now - track[0][0] > 0.6:
                    track.popleft()
                # Feed the Kalman tracker in parallel (position plus
                # linear size). It validates everything itself and can
                # never raise into the scan path; a zero area simply
                # means "no scale info on this observation".
                try:
                    area = float(getattr(res.target, "area", 0) or 0)
                    if area > 0.0:
                        self._tracker.update(now, (ax, ay, math.sqrt(area)))
                except Exception:
                    pass
            return res.target

        return None

    @staticmethod
    def _send_button(flag):
        """Raw Win32 left-button transition (kept for reference paths
        that must bypass the backend; assistance itself goes through
        _button below)."""
        inp = INPUT()
        inp.type = INPUT_MOUSE
        inp.u.mi.dwFlags = flag
        user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

    def _button(self, down):
        """One left-button transition through the active input backend."""
        self._input.button(down)

    def _warp(self, x, y):
        """Move the cursor through the active input backend."""
        self._input.move(x, y)

    def send_click(self, x, y, double=False):
        self._warp(x, y)
        time.sleep(0.012)

        self._button(True)
        time.sleep(0.015)
        self._button(False)

        if double:
            time.sleep(0.055)
            self._button(True)
            time.sleep(0.015)
            self._button(False)

    def _follow_may_learn(self, target):
        """
        Decide whether a successful snap may be remembered.

        With follow_learn = "accent" (default) and an accent colour
        configured, only accent-matching items are learned - so a
        misclick that snapped to some other item never poisons the
        memory: it keeps following the colour you configured.
        """
        learn = str(self.cfg.get("follow_learn", "accent")).lower()
        if learn == "any":
            return True

        accents = _parse_accents(self.cfg.get("accent_color", "off"))
        if not accents:
            return True  # no declared colour intent: learn anything

        return _sig_matches_accents(
            getattr(target, "sig", None), accents,
            float(self.cfg.get("accent_tolerance", 26)),
            accent_soft_of(self.cfg),
            accent_matcher_of(self.cfg),
            # The learn gate reads the SAME colour switches the click
            # gate reads: with "Catch bright and dim states of my
            # colour" off, a brighter copy of the accent is no match
            # here either - a switch must mean the same thing in both
            # places or one of them silently overrides the other.
            variants=accent_variants_of(self.cfg),
        )

    def glide_cursor(self, nx, ny):
        """
        Move the cursor to (nx, ny).

        glide_ms = 0 (default): one instant jump, lowest latency.
        glide_ms > 0: animated ease-out move over that many
        milliseconds so the user can follow where the cursor went.
        Any physical mouse movement aborts the animation immediately
        and hands control back to the user.

        Returns True if the cursor reached (nx, ny).
        """
        ms = int(self.cfg.get("glide_ms", 0) or 0)

        if ms <= 0:
            self._warp(nx, ny)
            return True

        x0, y0 = get_cursor_pos()
        steps = max(3, ms // 10)

        for i in range(1, steps + 1):
            t = i / float(steps)
            ease = 1.0 - (1.0 - t) ** 3  # ease-out cubic
            px = int(round(x0 + (nx - x0) * ease))
            py = int(round(y0 + (ny - y0) * ease))
            self._warp(px, py)
            time.sleep(0.010)

            ax, ay = get_cursor_pos()
            if abs(ax - px) > 2 or abs(ay - py) > 2:
                return False  # user physically moved: abort the glide

        return True

    def reinject_click(self, x, y):
        """
        Give back a click that classic mode suppressed but did not assist.
        """
        try:
            self.send_click(x, y, double=False)
        except Exception as exc:
            log("reinject error: %r" % (exc,))

    def _claim_delivery(self, state):
        """
        Exactly-once guard for a suppressed classic click.

        The disposable worker and the scanner's stall path race: without
        this, a worker that finishes just after the 1 s join timeout
        could deliver its snap click ON TOP of the click the scanner
        already returned (a double click from one physical press). Only
        the caller that claims may deliver or reinject; a click is
        returned exactly once - never zero, never twice.
        """
        lock = state.get("lock")
        if lock is None:
            return True                     # no protocol on this job
        with lock:
            if state.get("abandoned") or state.get("delivered"):
                return False
            state["delivered"] = True
            return True

    def _emergency_release(self):
        """
        If classic clicks were suppressed but never completed, give
        them back - EXACTLY ONCE.

        Queued (not yet started) jobs are returned by _drain_queue FIRST,
        so whatever is still in pending_classics afterwards belongs to the
        job currently in flight. That is precisely why this must not simply
        re-inject: before v8.49 it did, and a worker still inside
        scan_near() went on to deliver its own snap click on top of the
        returned one - TWO clicks from one physical press, which is the
        exact failure _claim_delivery() exists to prevent. Reachable by
        tapping a bare mode key ("1"/"2") during a drag, or by pausing
        while a click is being assisted.

        Each entry now carries its job's state dict, so this path claims
        through the same latch every other delivery path uses. An entry
        with no state (queued but never picked up) is only returned when no
        worker is active - if one is, the job is in flight and its state
        has not been attached yet, so returning it would duplicate.
        """
        pending = self.pending_classics
        self.pending_classics = []
        for entry in pending:
            if entry.get("up"):
                continue          # the physical UP already reached Windows
            state = entry.get("state")
            if state is not None:
                if not self._claim_delivery(state):
                    continue      # the worker owns this click
            elif self.worker_active:
                continue          # in flight, unclaimable: do not duplicate
            self.reinject_click(entry["x"], entry["y"])
            log("Suppressed click returned safely.")

    def _drain_queue(self):
        """
        Discard queued jobs. A discarded classic job will never be
        delivered by a worker, so its suppressed click is returned
        here - exactly once: the job's pending entry is removed too,
        so _emergency_release cannot return it a second time.
        """
        while True:
            try:
                item = self.click_q.get_nowait()
            except queue.Empty:
                break
            if item[0] == "classic":
                entry = item[4] if len(item) > 4 else None
                if entry is not None:
                    try:
                        self.pending_classics.remove(entry)
                    except ValueError:
                        pass
                self.reinject_click(item[1], item[2])
                log("Queued click returned safely.")

    def do_classic(self, x, y, out, state):
        """
        Mode 1:
        The physical down was suppressed.
        Find target, move, click. If no target, return the click.
        """
        try:
            if state.get("abandoned"):
                out["handled"] = True
                return

            target = self.scan_near(x, y, state, self._track)

            if state.get("abandoned"):
                out["handled"] = True
                return

            if target is None:
                self.pass_count += 1
                # exactly-once here too: the scanner's stall path may
                # have returned this click a moment ago.
                # "Watch the screen centre only" deliberately refused
                # this spot (state["center_pass"]) - the press must be
                # replayed at the pointer, not snapped to the middle.
                if self._claim_delivery(state):
                    self.reinject_click(x, y)
                out["handled"] = True
                return

            # on_target_dist is read HERE, in the mode that actually
            # clicks - guide mode and the hold-follow worker already
            # honour it. The setting promises "within this many pixels
            # of an item's centre nothing moves - you hit it", and a
            # click is precisely where that promise has to hold; before
            # this branch existed the window only ever suppressed
            # moves in the two paths that never click, i.e. the one
            # mode that delivers your press always nudged the cursor.
            #
            # The in-box test is deliberate: within on_target px of the
            # centre AND really standing on the item. The second half
            # keeps tiny controls assistable - a press 8 px from the
            # middle of a 6 px checkbox is inside the window yet has
            # hit nothing, and that is exactly the case snapping
            # exists for.
            move = math.hypot(target.dx, target.dy)
            hit = (move <= float(self.cfg.get("on_target_dist", 10))
                   and abs(target.dx) * 2.0 <= target.bw
                   and abs(target.dy) * 2.0 <= target.bh)

            if hit:
                # Your own press already landed on it: no move, no
                # lead, no offset - the click goes down where your
                # finger put it, which is what the setting promises.
                nx, ny = x, y
            else:
                nx = x + target.dx
                ny = y + target.dy

                # Smart follower: aim where the item WILL be, not where
                # the scan saw it. Standing items get a zero offset, so
                # classic behaviour is bit-for-bit unchanged while both
                # motion switches are off (default) or the item does
                # not move.
                if bool(self.cfg.get("motion_predict", False)) \
                        or bool(self.cfg.get("motion_3d", False)):
                    nx, ny = self._apply_motion_lead(nx, ny)

                # Snap offset: the user's own re-aiming of the click
                # point (snap_offset_x/y). Applied after the motion
                # lead so the offset is exact on screen, and before the
                # double-click watcher so repeats are judged on the
                # real click point.
                nx, ny = self._apply_snap_offset(nx, ny)

            now = time.perf_counter()
            watcher = float(self.cfg.get("watcher_seconds", 0.45))

            double = False
            if (
                self.last_snap_pos is not None
                and now - self.last_snap_time < watcher
            ):
                lx, ly = self.last_snap_pos
                if math.hypot(nx - lx, ny - ly) <= 35.0:
                    double = True

            # Claim the click BEFORE any side effect: if the scanner
            # already returned it (stall path), this worker must not
            # snap, learn or click anything.
            if not self._claim_delivery(state):
                out["handled"] = True
                return

            self.snap_count += 1
            if self._follow_may_learn(target):
                self.follow.store(nx, ny, target)

            # Hold-to-follow continuation: still physically holding the
            # button (mode 1 suppresses the press, so Windows itself
            # cannot report it) -> lock onto the colour of the item we
            # just snapped to, so the drag tracks the item. The hook
            # drops the lock on button-up; the follow worker also drops
            # it if the button is already up (creation race).
            if (bool(self.cfg.get("hold_follow", True))
                    and self._lbtn_down
                    and target.sig is not None
                    and not (self.follow_lock
                             and self.follow_lock.get("active"))):
                rgb = vision.hsv_to_rgb(*target.sig)
                self.follow_lock = {
                    "active": True,
                    "accent": "%d,%d,%d" % rgb,
                    "source": "hold",
                    "misses": 0,
                }

            # A hit needs no travel: skip the glide (there is nothing
            # to animate) but the click is still delivered exactly
            # once, at the press point.
            if hit or self.glide_cursor(nx, ny):
                self.send_click(nx, ny, double=double)
            else:
                # User moved during the glide: deliver their click
                # where the cursor is now; it is never swallowed.
                log("Glide aborted by user movement; clicking at current position.")
                time.sleep(0.012)
                self._button(True)
                time.sleep(0.015)
                self._button(False)

            self.last_snap_time = time.perf_counter()
            self.last_snap_pos = (int(nx), int(ny))

            log(
                "Classic assist: moved %.0f px to (%d, %d)%s%s"
                % (
                    math.hypot(nx - x, ny - y),
                    int(nx),
                    int(ny),
                    " (already on it - nothing moved)" if hit else "",
                    " and double-clicked" if double else "",
                )
            )

            out["handled"] = True

        except Exception as exc:
            log("classic worker error: %r" % (exc,))
            if self._claim_delivery(state):
                try:
                    self.reinject_click(x, y)
                except Exception:
                    pass
            out["handled"] = True

    def do_guide(self, x, y, out, state):
        """
        Mode 2:
        The user's click already passed through.
        After release, move cursor onto the nearest clear item.
        """
        try:
            if state.get("abandoned"):
                out["handled"] = True
                return

            target = self.scan_near(x, y, state, self._track)

            if state.get("abandoned"):
                out["handled"] = True
                return

            if target is None:
                self.pass_count += 1
                # "Watch the screen centre only": a press outside the
                # watched box must not even be guided onto the middle -
                # leave the cursor exactly where the user left it.
                out["handled"] = True
                return

            move = math.hypot(target.dx, target.dy)
            on_target = float(self.cfg.get("on_target_dist", 10))

            if move <= on_target:
                self.pass_count += 1
                out["handled"] = True
                return

            nx = x + target.dx
            ny = y + target.dy

            # Smart follower (see do_classic): lead the moving item.
            if bool(self.cfg.get("motion_predict", False)) \
                    or bool(self.cfg.get("motion_3d", False)):
                nx, ny = self._apply_motion_lead(nx, ny)

            nx, ny = self._apply_snap_offset(nx, ny)

            completed = self.glide_cursor(nx, ny)

            self.snap_count += 1
            if self._follow_may_learn(target):
                self.follow.store(nx, ny, target)
            self.last_snap_time = time.perf_counter()
            self.last_snap_pos = (int(nx), int(ny))

            log(
                "Guide assist: cursor moved %.0f px to (%d, %d)%s"
                % (move, int(nx), int(ny),
                   "" if completed else " (glide aborted: you took over)")
            )

            out["handled"] = True

        except Exception as exc:
            log("guide worker error: %r" % (exc,))
            out["handled"] = True

    def run_scanner(self):
        """
        Process queued click assistance jobs.
        Long operations run in disposable threads so the hook never freezes.
        Also expires deferred jobs from the double-click guard.
        """
        while not self.stop.is_set():
            try:
                item = self.click_q.get(timeout=0.1)
            except queue.Empty:
                continue

            kind, x, y = item[0], item[1], item[2]
            entry = item[4] if len(item) > 4 else None

            out = {}
            state = {"abandoned": False, "delivered": False,
                     "lock": threading.Lock()}

            # Publish the state on the pending entry BEFORE the worker
            # starts, so _emergency_release (hook thread) can claim through
            # the same latch instead of guessing whether a worker owns this
            # click. Written under the state's own lock: the hook thread
            # reads it concurrently.
            if entry is not None:
                with state["lock"]:
                    entry["state"] = state

            if kind == "classic":
                func = self.do_classic
            elif kind == "guide":
                func = self.do_guide
            else:
                continue

            self.worker_active = True

            th = threading.Thread(
                target=func,
                args=(x, y, out, state),
                name="assist-worker",
                daemon=True,
            )
            th.start()
            th.join(timeout=1.0)

            self.worker_active = False

            if th.is_alive():
                with state["lock"]:
                    state["abandoned"] = True
                    already = state["delivered"]

                if kind == "classic" and not already:
                    # The worker can no longer claim the click, so the
                    # scanner returns it: exactly once, never twice.
                    self.reinject_click(x, y)
                    log("Assist worker stalled. Suppressed click returned.")

                self.pause_until = time.perf_counter() + float(
                    self.cfg.get("stall_pause_seconds", 0.25)
                )

            elif kind == "classic" and not out.get("handled"):
                # Belt-and-braces: worker exited without handling.
                if self._claim_delivery(state):
                    self.reinject_click(x, y)

            if kind == "classic" and entry is not None:
                # Job done (delivered, returned or abandoned): its
                # suppressed-press record is no longer needed.
                try:
                    self.pending_classics.remove(entry)
                except ValueError:
                    pass

    def make_hook_proc(self):
        def proc(nCode, wParam, lParam):
            try:
                if nCode == HC_ACTION and not self.stop.is_set():
                    info = ctypes.cast(
                        lParam, ctypes.POINTER(MSLLHOOKSTRUCT)
                    ).contents

                    # v8.46: while a recording is armed the hook
                    # captures EVERY physical mouse event - every
                    # button's clicks and the whole cursor trail.
                    # Recording never blocks anything: the event
                    # always continues to Windows below. Our own
                    # injected events (playback, assisted clicks) and
                    # clicks inside our own windows are skipped, so
                    # playback can never record itself.
                    if self._rec_buffer is not None and self.running \
                            and not (info.flags
                                     & (LLMHF_INJECTED
                                        | LLMHF_LOWER_IL_INJECTED)):
                        rmsg = int(wParam)
                        if rmsg == WM_MOUSEMOVE:
                            self._record_move(info.pt.x, info.pt.y)
                            return user32.CallNextHookEx(
                                self.hook, nCode, wParam, lParam)
                        if rmsg in _MOUSE_REC_MAP and not self._fg_is_own():
                            self._record_button(rmsg, info.pt.x,
                                                info.pt.y)

                    # Only the LEFT button is ever ASSISTED (suppressed
                    # or acted on). The right button is watched solely
                    # for the optional mouse2_action (short press) and
                    # mouse2_hold_action (hold) side effects and is
                    # ALWAYS passed straight through, as are middle and
                    # side buttons: pure Windows behaviour, every mode.
                    if wParam not in (WM_LBUTTONDOWN, WM_LBUTTONUP,
                                      WM_RBUTTONDOWN, WM_RBUTTONUP):
                        return user32.CallNextHookEx(
                            self.hook, nCode, wParam, lParam)

                    # Ignore events injected by SnappyAI itself.
                    if not (info.flags & (LLMHF_INJECTED | LLMHF_LOWER_IL_INJECTED)):
                        # Never assist clicks inside our own UI.
                        if self._fg_is_own():
                            return user32.CallNextHookEx(
                                self.hook, nCode, wParam, lParam)

                        now = time.perf_counter()
                        msg = wParam

                        shift = bool(
                            user32.GetAsyncKeyState(VK_SHIFT) & 0x8000
                        )

                        armed = (
                            self.running
                            and not self.scanner_dead
                            and now >= self.pause_until
                            and not shift
                        )

                        mode = int(self.cfg.get("mode", 2))

                        if msg == WM_RBUTTONDOWN:
                            # Side effects only; the click itself always
                            # continues to Windows below. A short press
                            # fires mouse2_action, a hold of at least
                            # MOUSE2_HOLD_SECONDS fires
                            # mouse2_hold_action instead - never both.
                            self._rbtn_down = True
                            self.rbutton_down_time = now
                            if armed:
                                if self._mouse2_hold_action() == 4:
                                    # Nothing bound to a hold: keep the
                                    # classic timing and fire the click
                                    # action right on the press.
                                    self._handle_mouse2()
                                else:
                                    # Click vs hold is only known on
                                    # release (or when the hold timer
                                    # expires): defer the decision.
                                    self._rbtn_armed = True
                                    self._start_mouse2_hold_timer()

                        elif msg == WM_RBUTTONUP:
                            self._rbtn_down = False
                            self._finish_mouse2(now)

                        if msg == WM_LBUTTONDOWN:
                            self._lbtn_down = True

                            # hold-to-follow: while the button is held,
                            # keep the cursor on the last snapped item's
                            # colour (memory must be fresh, see
                            # follow_seconds). Only when the press is
                            # ON/NEAR that remembered item - a press
                            # anywhere else is an unrelated drag or text
                            # selection and must never be yanked around.
                            pad = vision.FOLLOW_POS_PAD
                            near_memory = (
                                abs(info.pt.x - self.follow.x) <= pad
                                and abs(info.pt.y - self.follow.y) <= pad
                            )
                            if (bool(self.cfg.get("hold_follow", True))
                                    and armed
                                    and self.follow.sig is not None
                                    and self.follow.when > 0
                                    and (now - self.follow.when)
                                    <= float(self.cfg.get("follow_seconds", 20))
                                    and near_memory
                                    and not (self.follow_lock
                                             and self.follow_lock.get("active"))):
                                rgb = vision.hsv_to_rgb(*self.follow.sig)
                                self.follow_lock = {
                                    "active": True,
                                    "accent": "%d,%d,%d" % rgb,
                                    "source": "hold",
                                    "misses": 0,
                                }
                            elif (self.follow_lock
                                    and self.follow_lock.get("active")
                                    and self.follow_lock.get("source") == "mouse2"):
                                # a new left press takes over from a
                                # right-button follow-lock
                                self.follow_lock = None

                            # rapid_click_snap (LEFT button only):
                            # assist EVERY click of a burst - continuous
                            # clicking or double-clicks keep snapping to
                            # icons/colours instead of only the first
                            # click being assisted and the rest passing
                            # through while the worker is still busy.
                            # Off (default): the classic one-at-a-time
                            # gate below. The right button is never
                            # affected by this.
                            rapid = bool(self.cfg.get("rapid_click_snap",
                                                      False))
                            un_upped = any(
                                not e.get("up")
                                for e in self.pending_classics
                            )
                            if (
                                mode == 1
                                and armed
                                and not un_upped
                                and (rapid
                                     or (self.click_q.qsize() == 0
                                         and not self.worker_active))
                            ):
                                entry = {"x": info.pt.x, "y": info.pt.y,
                                         "up": False, "state": None}
                                self.pending_classics.append(entry)
                                self.click_q.put(
                                    ("classic", info.pt.x, info.pt.y,
                                     now, entry)
                                )
                                return 1

                        elif msg == WM_LBUTTONUP:
                            self._lbtn_down = False

                            if self.follow_lock and \
                                    self.follow_lock.get("source") == "hold":
                                self.follow_lock = None

                            # Swallow the UP of a suppressed classic
                            # DOWN (the worker delivers that click);
                            # entries are matched in FIFO order.
                            for entry in self.pending_classics:
                                if not entry.get("up"):
                                    entry["up"] = True
                                    return 1

                            if mode == 2 and armed:
                                self.click_q.put(
                                    ("guide", info.pt.x, info.pt.y,
                                     now, None)
                                )

            except Exception as exc:
                log("hook error: %r" % (exc,))

            return user32.CallNextHookEx(self.hook, nCode, wParam, lParam)

        return HOOKPROC(proc)

    def make_key_hook_proc(self):
        """
        Pass-through keyboard hook for single-key bindings.

        Never blocks anything: every key event is handed straight to
        Windows. When a bound single key is pressed (not a repeat, not
        injected, no modifier held, not while typing in our own text
        fields), the bound action ALSO fires - system-wide, in whatever
        app is focused.
        """
        def proc(nCode, wParam, lParam):
            try:
                if nCode == HC_ACTION and not self.stop.is_set():
                    info = ctypes.cast(
                        lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)
                    ).contents
                    vk = int(info.vkCode)

                    if wParam == WM_KEYUP:
                        self._key_held.discard(vk)
                    elif wParam == WM_KEYDOWN:
                        if vk in self._key_held:
                            pass            # auto-repeat: ignore
                        else:
                            self._key_held.add(vk)
                            if not (info.flags & LLKHF_INJECTED) \
                                    and not self.input_focused:
                                # Recorder first (passive capture), then
                                # macros: block slots swallow the press
                                # (one D, not two); unblocked slots fire
                                # and still type, like pass-through keys.
                                self._record_press(vk)
                                fired, swallow = self._macro_press(vk)
                                if swallow:
                                    return 1
                                if not fired:
                                    self._maybe_fire_single_key(vk)
            except Exception as exc:
                log("key hook error: %r" % (exc,))

            return user32.CallNextHookEx(
                self.key_hook, nCode, wParam, lParam)

        return HOOKPROC(proc)

    def _maybe_fire_single_key(self, vk):
        if bool(self.cfg.get("block_bound_keys", False)):
            return                      # classic RegisterHotKey handles it
        hid = self._local_map.get(vk)
        if hid is None:
            return
        for mv in (VK_SHIFT, VK_CONTROL, VK_MENU):
            if user32.GetAsyncKeyState(mv) & 0x8000:
                return                  # part of a combo: leave it alone
        self.handle_hotkey(hid)

    def _mark_rec_full(self):
        if not self._rec_full:
            self._rec_full = True
            log("Recording capped at %d steps - further input is not "
                "captured." % REC_MAX_STEPS)

    def _record_press(self, vk):
        """
        Passive capture for the macro recorder: while a recording is
        armed (launched only) every deliberate physical press becomes a
        step (held modifiers, vk, gap since the previous step). Keys
        still reach the focused app - recording never blocks anything.
        The record-toggle combo itself is never captured, and injected
        events (macro playback) are filtered by the hook already.
        """
        if self._rec_buffer is None or not self.running:
            return

        held = 0
        for mask, mv in ((0x0002, VK_CONTROL), (0x0001, VK_MENU),
                         (0x0004, VK_SHIFT), (0x0008, VK_LWIN)):
            try:
                if user32.GetAsyncKeyState(mv) & 0x8000:
                    held |= mask
            except Exception:
                pass

        if (held, vk) in self._rec_combos:
            return        # start/stop presses are controls, not content
        if vk in (VK_SHIFT, VK_CONTROL, VK_MENU, VK_LWIN, 0x5C):
            return                      # bare modifier press: its held
                                        # state rides on the key's step

        now = time.perf_counter()
        delay = 0 if not self._rec_buffer else \
            int(round((now - self._rec_last_t) * 1000.0))
        self._rec_last_t = now
        if len(self._rec_buffer) >= REC_MAX_STEPS:
            self._mark_rec_full()
            return
        self._rec_buffer.append(
            (STEP_KEY, held, vk, max(0, min(5000, delay))))

    def _record_move(self, x, y):
        """
        Passive capture of cursor motion (v8.46): consecutive moves
        inside REC_MOVE_MERGE_S merge into ONE step whose position
        updates to the newest point, while the step keeps its original
        gap - so the recorded timeline stays exact (the next event's
        delay is measured from the merged step's first sample) and a
        smooth drag costs ~20 steps per second instead of one step per
        hardware event.
        """
        if self._rec_buffer is None or not self.running:
            return
        now = time.perf_counter()
        buf = self._rec_buffer
        if buf and buf[-1][0] == STEP_MOVE \
                and (now - self._rec_last_move) <= REC_MOVE_MERGE_S:
            buf[-1] = (STEP_MOVE, int(x), int(y), buf[-1][3])
            self._rec_last_move = now
            return
        if len(buf) >= REC_MAX_STEPS:
            self._mark_rec_full()
            return
        delay = 0 if not buf else \
            int(round((now - self._rec_last_t) * 1000.0))
        self._rec_last_t = now
        self._rec_last_move = now
        buf.append((STEP_MOVE, int(x), int(y),
                    max(0, min(5000, delay))))

    def _record_button(self, msg, x, y):
        """Passive capture of one physical mouse-button transition
        (left/right/middle, down/up, double-click as a second down).
        The click still reaches the focused app untouched."""
        if self._rec_buffer is None or not self.running:
            return
        pair = _MOUSE_REC_MAP.get(int(msg))
        if pair is None:
            return
        btn, phase = pair
        now = time.perf_counter()
        buf = self._rec_buffer
        if len(buf) >= REC_MAX_STEPS:
            self._mark_rec_full()
            return
        delay = 0 if not buf else \
            int(round((now - self._rec_last_t) * 1000.0))
        self._rec_last_t = now
        buf.append((STEP_BUTTON, btn, phase, int(x), int(y),
                    max(0, min(5000, delay))))

    def _start_recording(self):
        if self._rec_buffer is not None:
            log("Already recording - press %s to stop and save."
                % str(self.cfg.get("key_record_stop", "ctrl+alt+s"))
                .lower())
            return
        if not self.running:
            log("Recording arms while launched - press Launch first "
                "(paused means the keyboard is entirely yours).")
            return
        self._rec_buffer = []
        self._rec_last_t = time.perf_counter()
        self._rec_last_move = 0.0
        self._rec_full = False
        log("RECORDING - every key, mouse click and cursor move is "
            "captured and still reaches your apps. Press %s to stop "
            "and save."
            % str(self.cfg.get("key_record_stop", "ctrl+alt+s")).lower())

    def _stop_recording(self):
        # The stop key is the big red button: it halts a running
        # playback too, exactly as its description promises. (Pressing
        # play on a looping recording is the other way to stop it.)
        self.stop_playback()
        if self._rec_buffer is None:
            log("Not recording - nothing to stop.")
            return
        steps = self._rec_buffer
        self._rec_buffer = None
        if not steps:
            log("Recording stopped - no keys captured, nothing saved.")
            return
        name = "Recording %d" % (len(self.rec_store.recordings) + 1)
        rec = self.rec_store.add(name, steps)
        if rec is None:
            if len(self.rec_store.recordings) >= REC_MAX:
                log("Recording NOT saved: the library holds its cap of "
                    "%d recordings - delete one in the Macros tab "
                    "first." % REC_MAX)
            else:
                log("Recording not saved (no valid steps captured).")
            return
        self.rec_store.save()
        self.play_target_rid = rec["id"]
        log("Recording saved as #%d: %r (%d steps). Rename it in the "
            "Macros tab; replay with %s, or Ctrl+1..5 by list position."
            % (len(self.rec_store.recordings), rec["name"], len(steps),
               str(self.cfg.get("key_play", "ctrl+alt+m")).lower()))

    def set_play_target(self, rid):
        """GUI selection: what the plain play hotkey replays."""
        self.play_target_rid = rid

    def _play_recording(self, rid=None):
        rec = self.rec_store.get(rid) if rid else None
        if rec is None:
            rec = self.rec_store.most_recent()
        if rec is None:
            log("Nothing recorded yet - press %s to record a sequence."
                % str(self.cfg.get("key_record", "ctrl+alt+r")).lower())
            return
        self._start_playback(rec)

    def _play_slot(self, position):
        """Ctrl+1..5: play the recording at that LIST POSITION."""
        rec = self.rec_store.by_position(position)
        if rec is None:
            log("No recording at position %d (the library has %d). "
                "Ctrl+1..5 play recordings by list order."
                % (position, len(self.rec_store.recordings)))
            return
        self._start_playback(rec)

    def _start_playback(self, rec):
        """Queue one playback job in the recording's OWN saved style
        (v8.27: the "loop" flag on the recording itself - play once or
        repeat until stopped; the global play_mode/play_repeat settings
        are gone).

        Pressing play for the recording that is currently LOOPING
        stops it instead; starting a different job replaces the
        running one.

        Launched-only, like recording and macros: paused means the
        keyboard is entirely yours, so a play press while paused is
        refused instead of queued (the worker would otherwise inject
        it anyway - it only watches the stop event, not the state).
        """
        if not self.running:
            log("Playback arms while launched - press Launch first "
                "(paused means the keyboard is entirely yours).")
            return
        loop = bool(rec.get("loop"))

        if self._play_busy and self._play_rid == rec["id"] \
                and (self._play_looping or loop):
            self.stop_playback()
            return

        self._play_cancel.clear()
        self.macro_q.put(("rec", rec["steps"], "loop" if loop else "once"))
        self._play_rid = rec["id"]
        self._play_looping = loop
        self.play_target_rid = rec["id"]
        log("Playing recording %r (%d steps, %s)."
            % (rec["name"], len(rec["steps"]),
               "until stopped" if loop else "once"))

    def stop_playback(self):
        """Cancel a running OR QUEUED playback (responsive mid-gap).

        v8.49: this used to bail out unless `_play_busy or _play_looping`,
        and _start_playback sets neither for a play-once job until the
        worker picks it up - so pressing stop immediately after play did
        nothing at all and the recording injected anyway. _play_rid is set
        at queue time for every job, which makes it the reliable test."""
        if not (self._play_busy or self._play_looping
                or self._play_rid is not None):
            return False
        self._play_cancel.set()
        self._play_looping = False
        log("Playback stopped.")
        return True

    def _macro_press(self, vk):
        """
        Fire the macro bound to (held modifiers, vk), if any.

        Returns (fired, swallow):
          fired  - a combo was queued for the worker;
          swallow - the physical press must be blocked (return 1 from
                    the hook) so the focused app only sees the injected
                    combo - "D = D types one D".

        v8.27: every macro is blocked and single-shot - one trigger
        press injects exactly one combo press, and only while launched
        (paused, the keyboard is entirely yours). The trigger fires
        with EXACTLY its own modifiers held, so Ctrl+<trigger> etc.
        stay with the focused app. The hook only queues; the worker
        injects.
        """
        held = self._held_mods()
        spec = self._macro_map.get((held, vk))
        if spec is None:
            return False, False
        if not self.running:
            return False, False     # paused: keyboard is entirely yours
        _tm, _tv, amods, avk = spec
        self.macro_q.put(("combo", amods, avk))
        log("Macro: trigger fired - sending the combo once.")
        return True, True           # the physical press is swallowed

    def _held_mods(self):
        held = 0
        for mask, mv in ((0x0002, VK_CONTROL), (0x0001, VK_MENU),
                         (0x0004, VK_SHIFT), (0x0008, VK_LWIN)):
            try:
                if user32.GetAsyncKeyState(mv) & 0x8000:
                    held |= mask
            except Exception:
                pass
        return held

    def run_macro_worker(self):
        """Inject queued macro combos and recordings (the hook thread
        never sleeps). Jobs: ("combo", mods, vk) - one press - and
        ("rec", steps, mode) with mode "once"/"loop".

        v8.46: recording steps are TAGGED (see recordings.py): keys
        inject as before, moves teleport the cursor, and button steps
        aim the cursor at their recorded point first, then press or
        release left/right/middle. Everything injects with the
        LLMHF_INJECTED/LLKHF_INJECTED marks, so neither the assistance
        hooks nor a running recorder ever react to playback."""
        while not self.stop.is_set():
            try:
                job = self.macro_q.get(timeout=0.2)
            except queue.Empty:
                continue

            if job[0] == "combo":
                _kind, amods, avk = job
                try:
                    inject_combo(amods, avk)
                except Exception as exc:
                    log("macro inject error: %r" % (exc,))
                continue

            if job[0] == "rec":
                _kind, steps, mode = job
                self._play_busy = True
                passes = 1 if mode != "loop" else None
                done = 0
                while not self.stop.is_set() \
                        and not self._play_cancel.is_set():
                    for step in steps:
                        if self.stop.is_set() \
                                or self._play_cancel.is_set():
                            break
                        delay = int(step[-1])
                        if delay > 0:
                            end = time.perf_counter() \
                                + min(5.0, delay / 1000.0)
                            while time.perf_counter() < end:
                                if self.stop.is_set() or \
                                        self._play_cancel.is_set():
                                    break
                                time.sleep(0.05)
                        if self.stop.is_set() \
                                or self._play_cancel.is_set():
                            break
                        try:
                            tag = int(step[0])
                            if tag == STEP_MOVE:
                                move_cursor(step[1], step[2])
                            elif tag == STEP_BUTTON:
                                move_cursor(step[3], step[4])
                                time.sleep(0.008)
                                inject_mouse(step[1],
                                             step[2] == PHASE_DOWN)
                            else:
                                inject_combo(step[1], step[2])
                        except Exception as exc:
                            log("recording inject error: %r" % (exc,))
                            self._play_cancel.set()
                            break
                    done += 1
                    if passes is not None and done >= passes:
                        break
                self._play_busy = False
                self._play_looping = False

    def _mouse2_hold_action(self):
        """Validated mouse2_hold_action value (1-4, fallback 4)."""
        try:
            action = int(self.cfg.get("mouse2_hold_action", 4))
        except (TypeError, ValueError):
            return 4
        return action if action in (1, 2, 3, 4) else 4

    def _armed_now(self):
        """Live version of the hook's per-event 'armed' gate, checked
        again when a deferred right-button action actually fires (hold
        timer / button release) - pausing mid-press cancels it."""
        try:
            shift = bool(user32.GetAsyncKeyState(VK_SHIFT) & 0x8000)
        except Exception:
            shift = False
        return (self.running
                and not self.scanner_dead
                and time.perf_counter() >= self.pause_until
                and not shift)

    def _start_mouse2_hold_timer(self):
        """Arm the hold detector for the current right-button press.
        A short timer thread (never the hook itself, which must stay
        fast) fires the hold action if the button is still down."""
        with self._rbtn_lock:
            self._rbtn_hold_done = False
            self._rbtn_press_id += 1
            pid = self._rbtn_press_id
        t = threading.Timer(MOUSE2_HOLD_SECONDS,
                            self._mouse2_hold_check, args=(pid,))
        t.daemon = True
        t.start()

    def _mouse2_hold_check(self, pid):
        """Timer callback: still holding the same press? -> run the
        HOLD action (mouse2_hold_action)."""
        try:
            with self._rbtn_lock:
                if (pid != self._rbtn_press_id
                        or not self._rbtn_down
                        or self._rbtn_hold_done):
                    return
                self._rbtn_hold_done = True
            # Live cross-check: a release over our OWN window is
            # filtered by the hook, so bookkeeping alone could say
            # "still down" when the button is really up.
            try:
                still = bool(user32.GetAsyncKeyState(VK_RBUTTON) & 0x8000)
            except Exception:
                still = True        # trust the hook state
            if still and self._armed_now():
                self._handle_mouse2("mouse2_hold_action",
                                    "right-button hold")
        except Exception as exc:
            log("mouse2 hold error: %r" % (exc,))

    def _finish_mouse2(self, now):
        """Right button released: fire the CLICK action unless the
        press was (or just became) a hold - a press is never both."""
        try:
            with self._rbtn_lock:
                armed_down = self._rbtn_armed
                self._rbtn_armed = False
                held = self._rbtn_hold_done
                self._rbtn_hold_done = False
                self._rbtn_press_id += 1   # cancel a pending timer
                dur = now - self.rbutton_down_time
            if held or not armed_down:
                return          # hold already fired / press was unarmed
            if not self._armed_now():
                return
            if dur >= MOUSE2_HOLD_SECONDS:
                # The timer was late (system load) - a long press is a
                # hold even if it only ended now.
                self._handle_mouse2("mouse2_hold_action",
                                    "right-button hold")
            else:
                self._handle_mouse2("mouse2_action", "right-click")
        except Exception as exc:
            log("mouse2 release error: %r" % (exc,))

    def _handle_mouse2(self, key="mouse2_action", label="right-click"):
        """Programmable right-button side action, fired by a short
        press (key = mouse2_action) or a hold (key =
        mouse2_hold_action). The right button itself always keeps its
        normal Windows function - we only react alongside, never
        suppress it."""
        try:
            action = int(self.cfg.get(key, 4))
        except (TypeError, ValueError):
            action = 4

        if action == 1:
            if self.follow_lock or self.pending_classics:
                self.follow_lock = None
                log("Current follow task cleared.")

        elif action == 2:
            if self.follow_lock and self.follow_lock.get("active"):
                self.follow_lock = None
                log("Colour follow toggled off.")
                return
            mem = self.follow
            if mem.sig is not None and mem.when > 0:
                rgb = vision.hsv_to_rgb(*mem.sig)
                self.follow_lock = {
                    "active": True,
                    "accent": "%d,%d,%d" % rgb,
                    "source": "mouse2",
                    "misses": 0,
                }
                log("Following snapped colour rgb%s (%s or "
                    "clear to stop)." % (rgb, label))
            else:
                log("Nothing snapped yet - nothing to follow.")

        elif action == 3:
            self.follow_lock = {
                "active": True,
                "accent": None,
                "pick_until": time.perf_counter() + 2.0,
                "source": "mouse2",
                "misses": 0,
            }
            log("Pick window open: place the cursor on the colour "
                "(2 seconds)...")

        # action 4 (default): nothing, program-wise.

    def _sample_cursor_color(self):
        """RGB tuple of the pixel under the cursor, or None."""
        try:
            x, y = get_cursor_pos()
            img = self._capture.grab(x, y, x + 1, y + 1)
            if img is None:
                return None
            b, g, r = (int(v) for v in img[0, 0])
            return (r, g, b)
        except Exception:
            return None

    def _center_follow_cycle(self):
        """One pass of "Keep the cursor on it" (centre-watch follow).

        Only ever runs while BOTH switches are on: "Watch the screen
        centre only" and this one - exactly as requested, the feature
        exists to keep the cursor glued to a picked target inside the
        watched square (a moving scroll plane keeps being tracked even
        after it slides across the box).

        Safety rules, in order:
          * never fights the user: while any mouse button is held, or a
            hold/mouse2 follow-lock owns the cursor, this stays out;
          * arms on a click that snapped to an item inside the box, or
            when the user parks their cursor on an item there for ~0.3 s
            (the pick); dies after ~0.5 s without a fresh sighting;
          * the cursor rides the Kalman motion lead when the leading
            switches are on, so fast planes are chased, not lagged.
        """
        if not bool(self.cfg.get("watch_center_only", False)):
            return False
        if bool(self.cfg.get("motion_predict", False)) \
                or bool(self.cfg.get("motion_3d", False)):
            # the lead history must be fed even between clicks, or the
            # tracker goes stale mid-chase and the cursor lags behind
            self._feed_motion_track()
        cf = self._center_follow
        now = time.perf_counter()

        if cf is None or (now - cf["when"]) > 1.0:
            if cf is not None:
                # the chase went blind for a whole second: let go, and
                # require a fresh dwell before locking onto anything
                self._center_follow = None
            # nothing armed (or the sighting went stale): try to pick
            # from where the cursor currently sits inside the box
            vx, vy, vw, vh = self._virtual_screen()
            mx = vx + vw // 2
            my = vy + vh // 2
            half = max(24, int(round(
                float(self.cfg.get("radius", 150)) * self.dpi_scale))) // 2
            x, y = get_cursor_pos()
            if abs(x - mx) > half or abs(y - my) > half:
                return False
            before = self._center_follow
            target = self.scan_near(x, y, None, None)
            if target is not None:
                ax, ay = x + target.dx, y + target.dy
                # did the SCAN arm a sighting of its own (a click
                # worker's snap refreshed it a moment ago)? then the
                # chase starts instantly - no dwell required.
                armed_by_scan = (self._center_follow is not None
                                 and (before is None
                                      or (now - before["when"]) > 0.9))
                if armed_by_scan:
                    log("Centre follow: keeping the cursor on the "
                        "clicked item.")
                    self._pick_at = None
                elif (self._pick_at is not None
                        and math.hypot(ax - self._pick_at[0],
                                       ay - self._pick_at[1]) <= 6.0
                        and now - self._pick_at_time >= 0.25):
                    # the same item seen on two scans ~0.3 s apart:
                    # the user parked the cursor on it - arm the chase
                    self._center_follow = {
                        "x": ax, "y": ay, "sig": target.sig,
                        "when": now, "misses": 0,
                    }
                    self._pick_at = None
                    log("Centre follow: keeping the cursor on the "
                        "picked item.")
                else:
                    self._pick_at = (ax, ay)
                    self._pick_at_time = now
            else:
                self._pick_at = None
            return True

        self._pick_at = None

        # never fight the user's own input
        if self._lbtn_down or self._rbtn_down:
            return True
        lock = self.follow_lock
        if lock and lock.get("active"):
            return True

        cx, cy = cf["x"], cf["y"]
        nx, ny = self._apply_motion_lead(cx, cy)
        px, py = get_cursor_pos()
        if math.hypot(nx - px, ny - py) > 2.0:
            self._warp(nx, ny)
            self._follow_stable = 0
        else:
            self._follow_stable += 1
        return True

    def _feed_motion_track(self):
        """Refresh the Kalman/linear track with the freshest centre
        sighting so the motion lead stays alive during a chase."""
        cf = self._center_follow
        if cf is None:
            return
        now = time.perf_counter()
        self._track.append((now, cf["x"], cf["y"]))
        while self._track and now - self._track[0][0] > 0.6:
            self._track.popleft()
        try:
            sig = cf.get("sig")
            area = float(getattr(sig, "area", 0) or 0) if sig else 0.0
            if area > 0.0:
                self._tracker.update(now, (cf["x"], cf["y"],
                                           math.sqrt(area)))
        except Exception:
            pass

    def run_follow_worker(self):
        """
        While a follow-lock is active, keep the cursor on the locked
        colour's nearest item (stabilises drags, e.g. scrollbar thumbs).

        Also drives "Keep the cursor on it": with the centre watch on,
        park the cursor on the picked item inside the watched square
        and chase it while it moves (scroll planes and similar).
        """
        while not self.stop.is_set():
            if not self.running \
                    or time.perf_counter() < self.pause_until:
                time.sleep(0.05)
                continue

            lock = self.follow_lock
            center_on = (bool(self.cfg.get("center_follow", False))
                         and bool(self.cfg.get("watch_center_only", False)))
            if not center_on:
                self._center_follow = None
                self._pick_at = None
            if not lock or not lock.get("active"):
                if center_on and self._center_follow_cycle():
                    time.sleep(0.08 if self._follow_stable >= 4 else 0.04)
                    continue
                time.sleep(0.05)
                continue

            # A "hold" lock lives exactly as long as the button: drop a
            # stale one (button-up raced the lock creation) instead of
            # dragging the user's cursor around.
            if lock.get("source") == "hold" and not self._lbtn_down:
                self.follow_lock = None
                continue

            try:
                if lock.get("pick_until"):
                    if time.perf_counter() >= lock["pick_until"]:
                        rgb = self._sample_cursor_color()
                        if rgb:
                            lock["accent"] = "%d,%d,%d" % rgb
                            lock["pick_until"] = None
                            log("Locked onto colour rgb%s - following."
                                % (rgb,))
                        else:
                            self.follow_lock = None
                            log("Colour pick failed - follow cancelled.")
                    time.sleep(0.05)
                    continue

                accent = lock.get("accent")
                if not accent:
                    time.sleep(0.05)
                    continue

                x, y = get_cursor_pos()
                radius = self.radius_px()
                img, cx, cy, _origin, _edges = self.grab_around(x, y, radius)
                if img is not None:
                    cfgv = dict(self.cfg.values)
                    cfgv["accent_color"] = accent
                    cfgv["accent_only"] = True
                    res = vision.scan_region(img, cx, cy, cfgv, radius)
                    if res.kind == "target" and res.target is not None:
                        lock["misses"] = 0
                        if res.target.dist > float(
                                self.cfg.get("on_target_dist", 10)):
                            self._warp(x + res.target.dx, y + res.target.dy)
                            self._follow_stable = 0
                        else:
                            # Already on the item: nothing to do. After a
                            # few stable scans the loop backs off to half
                            # rate - a held drag that sits still for a
                            # moment stops burning a full grab + scan
                            # every 40 ms, and the first scan that has to
                            # move anything drops straight back to full
                            # rate. A moving item under a still cursor
                            # always counts as unstable (its scans keep
                            # moving the cursor), so tracking never lags.
                            self._follow_stable += 1
                    else:
                        # lost the item: drop the lock after ~0.5 s so an
                        # unrelated drag can never be yanked around
                        lock["misses"] = lock.get("misses", 0) + 1
                        self._follow_stable = 0
                        if lock["misses"] >= 12:
                            self.follow_lock = None
                            self._follow_stable = 0
            except Exception as exc:
                log("follow worker error: %r" % (exc,))
                self._follow_stable = 0

            time.sleep(0.08 if self._follow_stable >= 4 else 0.04)

    # ------------------------------------------------------------------
    # Auto-click: "click the blue thing for me".
    #
    # This is the only code path in the product that clicks without the
    # user asking for that specific click, so it is deliberately the most
    # conservative. Every gate below can only PREVENT a click:
    #
    #   1. the setting must be on, and an accent colour must exist - a
    #      colour is the only statement of intent available, so with
    #      accent_color off the feature never arms (config._sanitize
    #      keeps your switches exactly as you left them and only logs
    #      the mismatch; _auto_can_arm below is what refuses to act);
    #   2. the app must be LAUNCHED. Paused means the keyboard and mouse
    #      are entirely the user's - same rule as every other action;
    #   3. the foreground window must not be ours;
    #   4. the session click cap must not be spent;
    #   5. the item must carry the accent colour (accent_only forced on
    #      for this scan) AND clear the contrast gate;
    #   6. exclude_color removes the item outright - never-click still
    #      outranks everything;
    #   7. the last auto-click point must be far enough away, so a target
    #      that stays on screen is not clicked in a loop;
    #   8. the cursor moves onto the target and WAITS (settle) before the
    #      click, so the app sees the hover state first.
    #
    # It runs on its own daemon thread and never touches the hook, so a
    # slow capture here cannot delay a real user click.
    # ------------------------------------------------------------------

    def _auto_can_arm(self):
        """(ok, reason) - may the auto-click loop act at all right now?"""
        if not bool(self.cfg.get("auto_click", False)):
            return False, "auto_click is off"

        if self._auto_done:
            return False, "the per-session cap is spent"

        accents = vision._parse_accents(self.cfg.get("accent_color"))
        if not accents:
            return False, "no accent colour to aim at"
        return True, ""

    def _auto_reset_session(self):
        """Give the feature a fresh click budget (on launch).

        The first scan also waits one full interval, so arming never
        clicks before the user has seen that auto-click is on.
        """
        with self._auto_lock:
            self._auto_count = 0
            self._auto_at = None
            self._auto_done = False
            self._auto_armed = False
            try:
                gap = float(self.cfg.get("auto_click_interval", 2.0))
            except (TypeError, ValueError):
                gap = 2.0
            self._auto_next = time.perf_counter() + max(0.5, gap)

    def _auto_scan_config(self):
        """Config snapshot for the auto scan.

        accent_only is forced ON: the user already chose which colour the
        click is for, so nothing else may qualify. min_contrast is raised
        to auto_click_min_contrast, the same gate a manual click has to
        clear but tuned for acting without feedback - a guess that is only
        half-sure must not press a button on its own. Every other setting
        (accent colour, exclude list, tolerances, size gates) is the
        user's own, untouched.
        """
        cfgv = dict(self.cfg.values)
        cfgv["accent_only"] = True
        cfgv["min_contrast"] = max(
            float(cfgv.get("min_contrast", 48)),
            float(self.cfg.get("auto_click_min_contrast", 60)),
        )
        return cfgv

    def _auto_pick(self):
        """Find the best auto-click target: (abs_x, abs_y) or None.

        Scans the CENTRE of the screen - the place a person means by "the
        button in the middle" - not wherever the cursor happens to rest,
        so a click is decided by the target and not by mouse drift.
        """
        vx, vy, vw, vh = self._virtual_screen()
        cx = vx + vw // 2
        cy = vy + vh // 2
        radius = int(round(float(self.cfg.get("auto_click_radius", 200))
                           * self.dpi_scale))

        img, ix, iy, origin, edges = self.grab_around(cx, cy, radius)
        if img is None:
            return None

        cfgv = self._auto_scan_config()
        try:
            res = scan_region(img, ix, iy, cfgv, radius, edge_flags=edges)
        except Exception as exc:
            log("auto-click scan error: %r" % (exc,))
            return None

        if res.kind != "target" or res.target is None:
            return None
        return origin[0] + res.target.dx, origin[1] + res.target.dy

    def _apply_motion_lead(self, nx, ny):
        """Aim at where the tracked item WILL be, not where the scan
        saw it. Returns the (possibly unchanged) snap point.

        Two engines behind one switch: the legacy linear fit
        (predict_motion) by default, or the Kalman tracker - position
        plus scale - when motion_3d is on. Either switch alone enables
        leading (motion_3d does not need motion_predict); both share
        the same gates (too slow, too stale, capped), so the engine
        choice never changes what a click is allowed to do, only how
        well it follows. The scale reading is logged when there is a
        lead to report, so a growing dialog visibly explains itself.
        """
        lead_ms = float(self.cfg.get("motion_lead_ms", 50))
        tag = ""
        if bool(self.cfg.get("motion_3d", False)):
            pred = self._tracker.predict(lead_ms, MOTION_MAX_OFFSET)
            ox, oy = float(pred[0]), float(pred[1])
            if len(pred) > 2:
                try:
                    ratio = float(pred[2])
                    # Only worth mentioning when the size is actually
                    # changing; a steady x1.00 on every lead would be
                    # log spam for the common case.
                    tag = ", scale x%.2f" % ratio \
                        if abs(ratio - 1.0) >= 0.02 else ""
                except (TypeError, ValueError):
                    tag = ""
        else:
            ox, oy = vision.predict_motion(list(self._track), lead_ms,
                                           MOTION_MAX_OFFSET)
        if abs(ox) + abs(oy) >= 1.5:
            nx = int(round(nx + ox))
            ny = int(round(ny + oy))
            log("Motion lead: %+d,%+d px%s" % (ox, oy, tag))
        return nx, ny

    def _apply_snap_offset(self, nx, ny):
        """Shift a snap point by the user's snap_offset_x/y.

        Returns (int, int). A zero offset is returned untouched, so the
        default configuration behaves bit-for-bit as before.
        """
        try:
            ox = int(self.cfg.get("snap_offset_x", 0) or 0)
        except (TypeError, ValueError):
            ox = 0
        try:
            oy = int(self.cfg.get("snap_offset_y", 0) or 0)
        except (TypeError, ValueError):
            oy = 0
        if ox or oy:
            return int(nx + ox), int(ny + oy)
        return int(nx), int(ny)

    def _auto_fire(self, x, y):
        """Move onto (x, y), let the app settle, click once.

        The point must already carry the snap offset (the worker
        applies it before the repeat guard, so the guard compares real
        click points with real click points).
        """
        settle = float(self.cfg.get("auto_click_settle_ms", 120)) / 1000.0

        if not self.glide_cursor(x, y):
            # The user grabbed the mouse mid-move: that is a request to
            # take over, and an auto click would fight them for it.
            log("Auto-click cancelled: you moved the mouse yourself.")
            return False

        if settle > 0:
            time.sleep(settle)

        self.send_click(x, y, double=False)

        with self._auto_lock:
            self._auto_count += 1
            self._auto_at = (int(x), int(y))
            spent = self._auto_count
            cap = int(self.cfg.get("auto_click_max_clicks", 10))
            if spent >= cap:
                self._auto_done = True

        log("Auto-click %d/%d: clicked (%d, %d)."
            % (spent, cap, int(x), int(y)))

        if self._auto_done:
            log("Auto-click reached its limit of %d clicks for this "
                "session. Turn Auto-click items off and on again, or "
                "raise the limit, to let it continue." % cap)
        return True

    def run_auto_click_worker(self):
        """The auto-click loop. Own thread, daemon, never blocks a click."""
        idle = 0.2

        while not self.stop.is_set():
            try:
                ok, reason = self._auto_can_arm()
                if not ok:
                    # The cap is terminal for this session: only a fresh
                    # launch (which calls _auto_reset_session) restores
                    # the budget. Resetting it here would turn the safety
                    # cap into a rate limit, which is not what it is.
                    # All other "not ok" reasons just mean "wait".
                    del reason
                    time.sleep(idle)
                    continue

                if not self.running \
                        or time.perf_counter() < self.pause_until:
                    time.sleep(idle)
                    continue

                if self.stop.wait(self._auto_next - time.perf_counter()):
                    break

                # Our own windows are never auto-clicked: the settings
                # window is full of buttons that mean something else.
                if self._fg_is_own():
                    time.sleep(idle)
                    continue

                target = self._auto_pick()
                if target is None:
                    time.sleep(idle)
                    continue

                x, y = self._apply_snap_offset(*target)
                with self._auto_lock:
                    last = self._auto_at
                repeat = float(self.cfg.get("auto_click_repeat_px", 60))
                if last is not None and math.hypot(x - last[0],
                                                   y - last[1]) < repeat:
                    # Same place as last time - it is either still up, or
                    # the scan has not caught up with the click. Wait.
                    self._auto_next = time.perf_counter() + \
                        float(self.cfg.get("auto_click_interval", 2.0))
                    time.sleep(idle)
                    continue

                with self._auto_lock:
                    announced = self._auto_armed
                    self._auto_armed = True
                if not announced:
                    log("Auto-click is ON: scanning for %s every %ss."
                        % (self.cfg.get("accent_color"),
                           float(self.cfg.get("auto_click_interval", 2.0))))

                self._auto_fire(x, y)
                self._auto_next = time.perf_counter() + \
                    float(self.cfg.get("auto_click_interval", 2.0))
            except Exception as exc:
                log("auto-click worker error: %r" % (exc,))
                time.sleep(idle)

    def _rebind_hotkeys(self):
        """Rebuild the hotkey tables from config (hook thread only)."""
        for hid, _m, _v in self._hk_always:
            try:
                UnregisterHotKey(None, hid)
            except Exception:
                pass

        always, local = build_hotkey_table(self.cfg)
        self._hk_always = always
        self.local_binds = local
        self._local_map = {vk: hid for hid, vk in local}

        self._macros, self._macro_map = build_macro_table(self.cfg)
        self._rec_combos = set()
        # Recorder control combos are NEVER captured as recording
        # content: start (30), stop (37) and the whole play family
        # (31, 32-36) - a captured play press would re-trigger playback
        # inside every later replay. Controls can live in either table
        # (modified specs register system-wide, bare ones ride the
        # pass-through hook), so both are scanned.
        _CONTROL_IDS = (30, 31, 32, 33, 34, 35, 36, 37)
        for hid, mods, vk in always:
            if hid in _CONTROL_IDS:
                self._rec_combos.add((mods & 0x000F, vk))
        for hid, vk in local:
            if hid in _CONTROL_IDS:
                self._rec_combos.add((0, vk))
        for m in self._macros:
            k = (m[0] & 0x000F, m[1])
            if k in self._local_map or k in self._rec_combos or any(
                    (mm & 0x000F, vv) == k for _h, mm, vv in always):
                log("Macro trigger shares a key with an action or "
                    "recorder hotkey; while launched, the macro wins "
                    "that key.")
        for hid, mods, vk in always:
            if not RegisterHotKey(None, hid, mods, vk):
                log("Hotkey id %d could not be registered." % hid)

    def toggle_running(self):
        if self.running:
            self.handle_hotkey(11)
        else:
            self.handle_hotkey(10)

    def handle_hotkey(self, hid):
        action = ACTION_IDS.get(hid)
        if action is None:
            return                      # unknown id: nothing to dispatch

        if action == "launch":
            if not self.running:
                self.running = True
                # Auto-click gets a fresh budget per launched session:
                # the cap is meant to bound one sitting, not to run out
                # for the rest of the app's life.
                self._auto_reset_session()
                log(
                    "LAUNCHED - assist active, mode %s "
                    "(%s pauses, %s / %s switch modes)"
                    % (self.cfg.get("mode"),
                       self.cfg.get("key_pause", "ctrl+p"),
                       effective_mode_key(self.cfg, 1),
                       effective_mode_key(self.cfg, 2))
                )

        elif action == "pause":
            if self.running:
                self._drain_queue()
                self._emergency_release()
                self.follow_lock = None
                # A looping (or long one-shot) playback keeps
                # generating NEW input, so unlike a suppressed click
                # it must not complete - it stops here, same as quit.
                self.stop_playback()
                self.running = False
                log("PAUSED - your mouse and keyboard are entirely yours.")

        elif action == "reload":
            self._drain_queue()
            self._emergency_release()
            self.follow_lock = None
            self.cfg.reload()
            self._rebind_hotkeys()

            note = ""
            backend = str(self.cfg.get("capture_backend", "auto"))
            if backend != self._capture.prefer:
                note = " (capture_backend change needs a restart)"

            log("CONFIG RELOADED from disk%s." % note)

        elif action == "mode1":
            self._drain_queue()
            self._emergency_release()
            self.cfg.set("mode", 1)
            log(
                "MODE 1 classic: mis-click suppressed, snap, auto-click. "
                "Shift bypasses."
            )

        elif action == "mode2":
            self._drain_queue()
            self._emergency_release()
            self.cfg.set("mode", 2)
            log(
                "MODE 2 guide: your clicks always pass through; "
                "cursor moves onto items after release."
            )

        elif action == "record_macro":
            self._start_recording()

        elif action == "stop_macro":
            self._stop_recording()

        elif action == "play_macro":
            self._play_recording(self.play_target_rid)

        elif action.startswith("play_macro") and action[-1].isdigit():
            self._play_slot(int(action[-1]))

    def request_quit(self):
        self._drain_queue()
        self._emergency_release()
        self.follow_lock = None
        self._play_cancel.set()         # never keep injecting after quit
        while True:                     # never inject macros after quit
            try:
                self.macro_q.get_nowait()
            except queue.Empty:
                break
        self.stop.set()

        if self.thread_id:
            try:
                PostThreadMessage(self.thread_id, WM_QUIT, 0, 0)
            except Exception:
                pass

    def run_hook_thread(self):
        self.thread_id = kernel32.GetCurrentThreadId()
        self.dpi_scale = get_dpi_scale()

        # Warm up capture and analysis so the first real click is faster.
        try:
            warm = np.full((64, 64, 3), 128, dtype=np.uint8)
            scan_region(warm, 32, 32, self.cfg.values, 50)

            x, y = get_cursor_pos()
            self.grab_around(x, y, 40)
        except Exception as exc:
            log("warmup note: %r" % (exc,))

        self.proc_ref = self.make_hook_proc()

        self.hook = user32.SetWindowsHookExW(
            WH_MOUSE_LL,
            self.proc_ref,
            kernel32.GetModuleHandleW(None),
            0,
        )

        if not self.hook:
            log("FATAL: could not install the mouse hook.")
            log("Another program may be blocking it. Try restarting Windows.")
            self.stop.set()
            self.ready.set()
            return

        self.key_proc_ref = self.make_key_hook_proc()
        self.key_hook = user32.SetWindowsHookExW(
            WH_KEYBOARD_LL,
            self.key_proc_ref,
            kernel32.GetModuleHandleW(None),
            0,
        )
        if not self.key_hook:
            log("WARNING: keyboard hook unavailable; single-key binds "
                "fall back to registered hotkeys only.")

        self._rebind_hotkeys()

        self.ready.set()

        msg = MSG()

        while not self.stop.is_set():
            ret = GetMessage(ctypes.byref(msg), None, 0, 0)

            if ret == 0 or ret == -1:
                break

            if msg.message == WM_HOTKEY:
                try:
                    hid = int(msg.wParam)
                    self.handle_hotkey(hid)
                except Exception as exc:
                    log("hotkey error: %r" % (exc,))

        for hid, _m, _v in self._hk_always:
            try:
                UnregisterHotKey(None, hid)
            except Exception:
                pass

        if self.hook:
            try:
                user32.UnhookWindowsHookEx(self.hook)
            except Exception:
                pass

            self.hook = None

        if self.key_hook:
            try:
                user32.UnhookWindowsHookEx(self.key_hook)
            except Exception:
                pass

            self.key_hook = None


def start_app(cfg, identity=None):
    """Create the App and start its threads. Returns (app, hook_thread)."""
    try:
        import mss  # noqa: F401
    except ImportError:
        print("Snappy AI needs mss on Windows.")
        print("Install with:")
        print("    python -m pip install numpy mss")
        print("Optional extras (faster capture, new capture engine):")
        print("    python -m pip install dxcam")
        print("    python -m pip install windows-capture   # capture_backend = wgc")
        return None, None

    setup_dpi_awareness()

    app = App(cfg, identity)

    hook_thread = threading.Thread(
        target=app.run_hook_thread,
        name="hook",
        daemon=True,
    )
    hook_thread.start()

    threading.Thread(
        target=app.run_scanner,
        name="scanner",
        daemon=True,
    ).start()

    threading.Thread(
        target=app.run_follow_worker,
        name="follow",
        daemon=True,
    ).start()

    threading.Thread(
        target=app.run_auto_click_worker,
        name="auto-click",
        daemon=True,
    ).start()

    threading.Thread(
        target=app.run_macro_worker,
        name="macros",
        daemon=True,
    ).start()

    threading.Thread(
        target=app.run_presence_worker,
        name="presence",
        daemon=True,
    ).start()

    app.ready.wait(timeout=10)

    if app.stop.is_set():
        print("")
        print("Snappy AI could not start. See messages above.")
        return None, None

    return app, hook_thread

