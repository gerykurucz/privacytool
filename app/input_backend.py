"""Mouse input delivery backends: Windows SendInput (default) and an
optional Interception backend (github.com/oblitum/Interception).

Why both exist
--------------
SendInput is what every accessibility tool uses: no driver, works out of
the box, and Snappy AI's own low-level hooks recognise injected events
(LLMHF_INJECTED) so assistance never feeds itself. Its one weakness is
that a minority of games and Raw-Input applications ignore synthetic
events entirely - clicks simply never arrive there.

Interception injects at the driver layer, below Raw Input, so those
applications see the click as genuine hardware. The price: it needs a
signed kernel driver installed by the user (interception.exe install +
reboot) and two DLLs on PATH or beside this app. That friction is why
Win32 stays the DEFAULT and Interception is strictly opt-in.

Design rules (mirrors the capture_backend pattern)
--------------------------------------------------
- Pure stdlib ctypes; imports cleanly on any OS (the GUI reads
  available() to decorate its dropdown), loads the DLL only when the
  user actually selects "interception".
- NEVER fatal: any failure (no DLL, no driver, device busy, send
  refused) logs once and degrades to Win32 for that call AND for all
  future calls, so a half-installed setup can never eat a click.
- Coordinates: absolute SetCursorPos is emulated with per-move relative
  strokes (x = target - current cursor). Relative deltas are exactly
  what the mouse protocol carries, so apps that read raw motion stay in
  sync with where the pointer actually is.

Backend contract (what assist.py / win32rt.py consume):
    move(x, y)             teleport/warp the cursor to screen (x, y)
    button(down)           left-button transition (True = press)
    ok_for_button()        True if a real button event may be sent here
    note_failure(where)    log-once + permanent degrade to Win32
    available()            classmethod: is this even possible right now?
"""

import ctypes
import os
import sys
import threading
import time

from core import IS_WINDOWS, log


class Win32Backend(object):
    """The default: SetCursorPos warps plus SendInput button events.

    Thin indirection over the exact calls used since v1 - behaviour is
    bit-for-bit unchanged when this backend is active.
    """

    name = "win32"

    @classmethod
    def available(cls):
        return IS_WINDOWS

    def move(self, x, y):
        import win32rt
        win32rt.user32.SetCursorPos(int(x), int(y))

    def button(self, down):
        import win32rt
        inp = win32rt.INPUT()
        inp.type = win32rt.INPUT_MOUSE
        inp.u.mi.dwFlags = (win32rt.MOUSEEVENTF_LEFTDOWN if down
                            else win32rt.MOUSEEVENTF_LEFTUP)
        win32rt.user32.SendInput(1, ctypes.byref(inp),
                                 ctypes.sizeof(win32rt.INPUT))

    def ok_for_button(self):
        return True

    def note_failure(self, where):
        pass


class InterceptionBackend(object):
    """Driver-level injection via the Interception library (opt-in).

    Loads interception.dll (searched next to this file, next to the
    executable, then on PATH). Sends relative moves and button state
    changes to the first mouse device. Any problem degrades PERMANENTLY
    to Win32 - a click must always reach the desktop somehow.
    """

    name = "interception"

    # Interception constants (interception.h)
    _IS_MOUSE_MOVE = 1 << 7      # stroke carries x/y motion
    _IS_MOUSE_LEFT = 1 << 0      # stroke carries left-button state
    _FILTER_ALL = 0xFFFF
    _INTERCEPTION_MAX_DEVICES = 10
    _WHEEL_MS = 8                # tiny pause so scroll planes never
                                 # swallow wheel messages behind a burst

    def __init__(self, ctx=None):
        self._lock = threading.Lock()
        self._degraded = False       # sticky: fall back to Win32 forever
        self._ctx = ctx              # optional pre-built context (tests)
        self._dll = None
        self._dev = None
        if ctx is not None:
            return                 # test double: nothing to load
        if not IS_WINDOWS:
            self._degraded = True
            return
        try:
            self._dll = self._load_dll()
            if self._dll is None:
                self._degraded = True
                return
            self._build_signatures()
            self._context = self._dll.interception_create_context()
            if not self._context:
                self._degraded = True
                return
            self._dev = self._find_mouse()
            if self._dev is None:
                self._degraded = True
        except Exception as exc:
            log("Input: Interception init failed (%r); using Windows "
                "injection instead." % (exc,))
            self._degraded = True

    # -- discovery ----------------------------------------------------
    @staticmethod
    def _candidate_dirs():
        dirs = []
        try:
            if getattr(sys, "frozen", False):
                dirs.append(os.path.dirname(sys.executable))
            dirs.append(os.path.dirname(os.path.abspath(__file__)))
        except Exception:
            pass
        dirs.append("")            # then the normal PATH search
        return dirs

    @classmethod
    def _load_dll(cls):
        for d in cls._candidate_dirs():
            p = os.path.join(d, "interception.dll") if d else \
                "interception.dll"
            try:
                if d and not os.path.isfile(p):
                    continue
                return ctypes.WinDLL(p)
            except OSError:
                continue
        return None

    @classmethod
    def available(cls):
        """Cheap check for the GUI: DLL present AND driver devices alive.

        Safe off Windows and without the library: returns False, never
        raises. Result is cached after the first probe."""
        if not IS_WINDOWS:
            return False
        cached = getattr(cls, "_avail_cache", None)
        if cached is not None:
            return cached
        ok = False
        try:
            dll = cls._load_dll()
            if dll is not None:
                dll.interception_create_context.restype = ctypes.c_void_p
                ctx = dll.interception_create_context()
                if ctx:
                    # wait() would block up to timeout ms; iterate() is
                    # non-blocking and returns 0 while nothing moved.
                    dll.interception_iterate.argtypes = [ctypes.c_void_p,
                                                         ctypes.c_double]
                    dll.interception_destroy_context.argtypes = \
                        [ctypes.c_void_p]
                    deadline = time.time() + 0.25
                    while time.time() < deadline:
                        if dll.interception_iterate(ctx, 0.0):
                            ok = True
                            break
                        time.sleep(0.01)
                    dll.interception_destroy_context(ctx)
        except Exception:
            ok = False
        cls._avail_cache = ok
        return ok

    def _build_signatures(self):
        c = ctypes

        class MOUSE(c.Structure):
            _fields_ = [("type", c.c_ushort),
                        ("reserved", c.c_ushort),
                        ("x", c.c_int), ("y", c.c_int),
                        ("normalized_position", c.c_uint),
                        ("rolling_to_x", c.c_int),
                        ("rolling_to_y", c.c_int),
                        ("buttons", c.c_ushort),
                        ("movement", c.c_short),
                        ("speed", c.c_long)]

        class STROKE(c.Union):
            _fields_ = [("mouse", MOUSE),
                        ("pad", c.c_byte * 60)]

        self._STROKE = STROKE
        dll = self._dll
        dll.interception_first_target_device.restype = c.c_int
        dll.interception_first_target_device.argtypes = [c.c_void_p,
                                                         c.c_int]
        dll.interception_wait.argtypes = [c.c_void_p, c.c_int,
                                          ctypes.POINTER(STROKE)]
        dll.interception_send.restype = c.c_int
        dll.interception_send.argtypes = [c.c_void_p, c.c_int,
                                          ctypes.POINTER(STROKE), c.c_int]
        dll.interception_set_filter.argtypes = [c.c_void_p, c.c_int,
                                                c.c_ushort]
        dll.interception_destroy_context.argtypes = [c.c_void_p]

    def _find_mouse(self):
        for kind in (15, 14):     # MOUSE then MOUSE_ABSOLUTE
            dev = self._dll.interception_first_target_device(
                self._context, kind)
            if dev > 0:
                try:
                    self._dll.interception_set_filter(
                        self._context, dev, self._FILTER_ALL)
                except Exception:
                    pass
                return dev
        log("Input: Interception found no mouse target device - is the "
            "driver installed (interception.exe install + reboot)? "
            "Using Windows injection.")
        return None

    # -- contract ------------------------------------------------------
    def ok_for_button(self):
        return (not self._degraded) and self._dev is not None

    def note_failure(self, where):
        if not self._degraded:
            self._degraded = True
            log("Input: Interception %s failed; falling back to Windows "
                "injection for the rest of this session." % (where,))

    def move(self, x, y):
        """Warp to absolute (x, y) as small relative strokes with a
        settle-and-correct loop. Driver-level motion travels through
        the same pipeline as a physical mouse, so pointer speed and DPI
        apply exactly as they would for a hand - the correction loop
        converges regardless."""
        import win32rt
        try:
            cx, cy = win32rt.get_cursor_pos()
        except Exception:
            self.note_failure("cursor read")
            return
        tx, ty = int(x), int(y)
        if (cx, cy) == (tx, ty):
            return
        for _ in range(4):
            dx = max(-self._STEP, min(self._STEP, tx - cx))
            dy = max(-self._STEP, min(self._STEP, ty - cy))
            s = self._STROKE()
            s.mouse.type = self._IS_MOUSE_MOVE
            s.mouse.x, s.mouse.y = dx, dy
            self._send(s, "move")
            time.sleep(0.001)
            try:
                cx, cy = win32rt.get_cursor_pos()
            except Exception:
                self.note_failure("cursor read")
                return
            if (cx, cy) == (tx, ty):
                break

    _STEP = 128

    def button(self, down):
        s = self._STROKE()
        s.mouse.type = self._IS_MOUSE_LEFT
        s.mouse.buttons = 1 if down else 0
        self._send(s, "button")

    # -- internals ------------------------------------------------------
    def _send(self, stroke, what):
        with self._lock:
            if self._degraded:
                return
            try:
                n = self._dll.interception_send(self._context, self._dev,
                                                ctypes.byref(stroke), 1)
            except Exception:
                self.note_failure(what)
                return
            if not n:
                self.note_failure(what)


def make_input_backend(cfg):
    """Build the configured backend; ALWAYS returns something usable.

    input_backend = win32   (default)  -> Win32Backend, nothing loaded.
    input_backend = interception       -> InterceptionBackend if the DLL
      and driver answer, Win32Backend otherwise (logged once).
    """
    choice = str(cfg.get("input_backend", "win32") or "win32").lower()
    if choice == "interception":
        try:
            be = InterceptionBackend()
            if be.ok_for_button():
                log("Input: Interception active - clicks are delivered "
                    "at the driver level. If a game still ignores them, "
                    "install the driver: run interception.exe install "
                    "from an admin prompt, then reboot.")
                return be
        except Exception as exc:
            log("Input: Interception unavailable (%r); using the "
                "standard Windows method." % (exc,))
        log("Input: Interception selected but not working (missing "
            "interception.dll or driver not installed). Using the "
            "standard Windows method.")
    return Win32Backend()
