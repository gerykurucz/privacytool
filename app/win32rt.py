"""Windows runtime: ctypes bindings, DPI awareness, cursor helpers,
capture backends (dxcam fast path + mss fallback) and audio/voice
feedback. Importable on any platform - contents exist on Windows only."""

import threading
import time

import numpy as np

from core import IS_WINDOWS, log

if IS_WINDOWS:
    import ctypes
    import ctypes.wintypes as wt

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    WH_MOUSE_LL = 14
    WH_KEYBOARD_LL = 13
    HC_ACTION = 0
    WM_QUIT = 0x0012
    WM_HOTKEY = 0x0312
    WM_KEYDOWN = 0x0100
    WM_KEYUP = 0x0101
    LLKHF_INJECTED = 0x00000010

    # v8.46: the macro recorder captures EVERY physical mouse event,
    # so the hook now also sees moves, middle-button clicks and the
    # double-click message (recorded as a second left-down: the
    # recorded rhythm reproduces the double-click on playback).
    WM_MOUSEMOVE = 0x0200
    WM_LBUTTONDOWN = 0x0201
    WM_LBUTTONUP = 0x0202
    WM_LBUTTONDBLCLK = 0x0203

    WM_RBUTTONDOWN = 0x0204
    WM_RBUTTONUP = 0x0205

    WM_MBUTTONDOWN = 0x0207
    WM_MBUTTONUP = 0x0208

    LLMHF_INJECTED = 0x00000001
    LLMHF_LOWER_IL_INJECTED = 0x00000002

    MOD_ALT = 0x0001
    MOD_CONTROL = 0x0002
    MOD_NOREPEAT = 0x4000

    VK_SHIFT = 0x10
    VK_CONTROL = 0x11
    VK_MENU = 0x12
    VK_LBUTTON = 0x01
    VK_RBUTTON = 0x02   # live cross-check in assist._mouse2_hold_check
    VK_LWIN = 0x5B

    SM_XVIRTUALSCREEN = 76
    SM_YVIRTUALSCREEN = 77
    SM_CXVIRTUALSCREEN = 78
    SM_CYVIRTUALSCREEN = 79

    INPUT_MOUSE = 0
    INPUT_KEYBOARD = 1
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_RIGHTDOWN = 0x0008
    MOUSEEVENTF_RIGHTUP = 0x0010
    MOUSEEVENTF_MIDDLEDOWN = 0x0020
    MOUSEEVENTF_MIDDLEUP = 0x0040
    KEYEVENTF_KEYUP = 0x0002

    WPARAM_T = ctypes.c_size_t
    LPARAM_T = ctypes.c_ssize_t
    LRESULT_T = ctypes.c_ssize_t

    class POINT(ctypes.Structure):
        _fields_ = [("x", wt.LONG), ("y", wt.LONG)]

    class MSLLHOOKSTRUCT(ctypes.Structure):
        _fields_ = [
            ("pt", POINT),
            ("mouseData", wt.DWORD),
            ("flags", wt.DWORD),
            ("time", wt.DWORD),
            ("dwExtraInfo", ctypes.c_void_p),
        ]

    class KBDLLHOOKSTRUCT(ctypes.Structure):
        _fields_ = [
            ("vkCode", wt.DWORD),
            ("scanCode", wt.DWORD),
            ("flags", wt.DWORD),
            ("time", wt.DWORD),
            ("dwExtraInfo", ctypes.c_void_p),
        ]

    class MSG(ctypes.Structure):
        _fields_ = [
            ("hwnd", ctypes.c_void_p),
            ("message", wt.UINT),
            ("wParam", WPARAM_T),
            ("lParam", LPARAM_T),
            ("time", wt.DWORD),
            ("pt", POINT),
        ]

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [
            ("dx", wt.LONG),
            ("dy", wt.LONG),
            ("mouseData", wt.DWORD),
            ("dwFlags", wt.DWORD),
            ("time", wt.DWORD),
            ("dwExtraInfo", ctypes.c_void_p),
        ]

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", wt.WORD),
            ("wScan", wt.WORD),
            ("dwFlags", wt.DWORD),
            ("time", wt.DWORD),
            ("dwExtraInfo", ctypes.c_void_p),
        ]

    class _INPUT_UNION(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT)]

    class INPUT(ctypes.Structure):
        _fields_ = [("type", wt.DWORD), ("u", _INPUT_UNION)]

    HOOKPROC = ctypes.WINFUNCTYPE(LRESULT_T, ctypes.c_int, WPARAM_T, LPARAM_T)

    def _resolve(lib, *names):
        for name in names:
            try:
                return getattr(lib, name)
            except AttributeError:
                continue
        raise AttributeError("function not found: %s" % (names,))

    RegisterHotKey = _resolve(user32, "RegisterHotKey", "RegisterHotKeyW")
    UnregisterHotKey = _resolve(user32, "UnregisterHotKey")
    PostThreadMessage = _resolve(user32, "PostThreadMessageW", "PostThreadMessage")
    GetMessage = _resolve(user32, "GetMessageW", "GetMessage")
    PostMessageW = _resolve(user32, "PostMessageW", "PostMessage")

    user32.SetWindowsHookExW.restype = ctypes.c_void_p
    user32.SetWindowsHookExW.argtypes = [
        ctypes.c_int,
        HOOKPROC,
        ctypes.c_void_p,
        wt.DWORD,
    ]

    user32.CallNextHookEx.restype = LRESULT_T
    user32.CallNextHookEx.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int,
        WPARAM_T,
        LPARAM_T,
    ]

    user32.UnhookWindowsHookEx.argtypes = [ctypes.c_void_p]

    kernel32.GetModuleHandleW.restype = ctypes.c_void_p
    kernel32.GetModuleHandleW.argtypes = [wt.LPCWSTR]

    kernel32.GetCurrentThreadId.restype = wt.DWORD

    GetMessage.restype = ctypes.c_int
    GetMessage.argtypes = [
        ctypes.POINTER(MSG),
        ctypes.c_void_p,
        wt.UINT,
        wt.UINT,
    ]

    RegisterHotKey.restype = wt.BOOL
    RegisterHotKey.argtypes = [wt.HWND, ctypes.c_int, wt.UINT, wt.UINT]

    UnregisterHotKey.argtypes = [wt.HWND, ctypes.c_int]

    PostThreadMessage.argtypes = [wt.DWORD, wt.UINT, WPARAM_T, LPARAM_T]

    user32.GetAsyncKeyState.restype = ctypes.c_short
    user32.GetAsyncKeyState.argtypes = [ctypes.c_int]

    user32.GetForegroundWindow.restype = ctypes.c_void_p
    user32.GetForegroundWindow.argtypes = []

    user32.GetWindowThreadProcessId.restype = wt.DWORD
    user32.GetWindowThreadProcessId.argtypes = [
        ctypes.c_void_p, ctypes.POINTER(wt.DWORD)]

    user32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]

    user32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]

    if hasattr(user32, "GetPhysicalCursorPos"):
        user32.GetPhysicalCursorPos.argtypes = [ctypes.POINTER(POINT)]

    user32.WindowFromPoint.restype = ctypes.c_void_p
    user32.WindowFromPoint.argtypes = [POINT]

    user32.ScreenToClient.argtypes = [ctypes.c_void_p, ctypes.POINTER(POINT)]

    PostMessageW.restype = wt.BOOL
    PostMessageW.argtypes = [ctypes.c_void_p, wt.UINT, WPARAM_T, LPARAM_T]

    user32.SendInput.restype = wt.UINT
    user32.SendInput.argtypes = [wt.UINT, ctypes.POINTER(INPUT), ctypes.c_int]

    # Mod-mask bits (HOTKEY_MODS layout: ctrl 2, alt 1, shift 4, win 8)
    # to the virtual keys that carry them, in press order.
    _MACRO_MOD_VKS = ((0x0004, VK_SHIFT), (0x0002, VK_CONTROL),
                      (0x0001, VK_MENU), (0x0008, VK_LWIN))

    def inject_combo(mods, vk):
        """
        Press and release mods+vk as injected keystrokes (macro engine).

        One SendInput call for the whole down/up sequence so Windows
        cannot interleave foreign input mid-combo. Injected events carry
        LLMF_INJECTED, so Snappy AI's own hooks ignore them.
        """
        seq = [mv for mask, mv in _MACRO_MOD_VKS if mods & mask]
        seq.append(vk)

        inputs = []
        for key in seq:
            inp = INPUT()
            inp.type = INPUT_KEYBOARD
            inp.u.ki.wVk = key
            inputs.append(inp)
        for key in reversed(seq):
            inp = INPUT()
            inp.type = INPUT_KEYBOARD
            inp.u.ki.wVk = key
            inp.u.ki.dwFlags = KEYEVENTF_KEYUP
            inputs.append(inp)

        arr = (INPUT * len(inputs))(*inputs)
        user32.SendInput(len(inputs), arr, ctypes.sizeof(INPUT))

    # v8.46 recording playback: recorded steps carry mouse moves and
    # button transitions of ALL THREE buttons, so the worker needs a
    # cursor teleport and one injected down/up per button. Injected
    # mouse events carry LLMHF_INJECTED, so Snappy AI's own hooks
    # (assistance AND the recorder) ignore them - playback can never
    # feed itself back into a recording.
    _MOUSE_BTN_FLAGS = (
        (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP),
        (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP),
        (MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP),
    )

    def move_cursor(x, y):
        """Teleport the cursor (playback of a recorded move)."""
        user32.SetCursorPos(int(x), int(y))

    def inject_mouse(button, down):
        """One injected mouse-button transition: button 0=left,
        1=right, 2=middle; down True presses, False releases."""
        flags = _MOUSE_BTN_FLAGS[int(button)]
        inp = INPUT()
        inp.type = INPUT_MOUSE
        inp.u.mi.dwFlags = flags[0] if down else flags[1]
        user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

    def apply_window_theme(hwnd, dark, caption_rgb, text_rgb):
        """
        Colour the window title bar to match the app theme.

        Windows 11: caption + text colour attributes.
        Windows 10: immersive dark mode toggle (best available).
        Silently does nothing on older systems.
        """
        try:
            dwm = ctypes.windll.dwmapi

            def _cref(rgb):
                r, g, b = rgb
                return (b << 16) | (g << 8) | r

            flag = ctypes.c_int(1 if dark else 0)
            dwm.DwmSetWindowAttribute(
                ctypes.c_void_p(hwnd), 20,  # DWMWA_USE_IMMERSIVE_DARK_MODE
                ctypes.byref(flag), ctypes.sizeof(flag))

            cap = ctypes.c_int(_cref(caption_rgb))
            dwm.DwmSetWindowAttribute(
                ctypes.c_void_p(hwnd), 35,  # DWMWA_CAPTION_COLOR
                ctypes.byref(cap), ctypes.sizeof(cap))

            txt = ctypes.c_int(_cref(text_rgb))
            dwm.DwmSetWindowAttribute(
                ctypes.c_void_p(hwnd), 36,  # DWMWA_TEXT_COLOR
                ctypes.byref(txt), ctypes.sizeof(txt))
        except Exception:
            pass

    def get_cursor_pos():
        pt = POINT()

        try:
            if hasattr(user32, "GetPhysicalCursorPos"):
                if user32.GetPhysicalCursorPos(ctypes.byref(pt)):
                    return int(pt.x), int(pt.y)
        except Exception:
            pass

        try:
            if user32.GetCursorPos(ctypes.byref(pt)):
                return int(pt.x), int(pt.y)
        except Exception:
            pass

        return 0, 0

    def setup_dpi_awareness():
        """
        Physical pixels everywhere. Important on scaled displays.
        """
        try:
            user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
            return
        except (AttributeError, OSError):
            pass

        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
            return
        except (AttributeError, OSError):
            pass

        try:
            user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass

    def get_dpi_scale():
        try:
            dpi = user32.GetDpiForSystem()
            if dpi:
                return max(1.0, float(dpi) / 96.0)
        except (AttributeError, OSError):
            pass

        return 1.0

    def virtual_screen():
        """(x, y, w, h) of the whole virtual screen, physical pixels."""
        try:
            return (int(user32.GetSystemMetrics(SM_XVIRTUALSCREEN)),
                    int(user32.GetSystemMetrics(SM_YVIRTUALSCREEN)),
                    int(user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)),
                    int(user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)))
        except Exception:
            try:                        # primary screen fallback
                return (0, 0, int(user32.GetSystemMetrics(0)),
                        int(user32.GetSystemMetrics(1)))
            except Exception:
                return 0, 0, 1920, 1080

    # v8.27: the Feedback class (voice announcements via a powershell
    # speech child + winsound beeps) was removed with the whole voice-
    # feedback feature - the product is silent by design now.

    class CaptureBackend(object):
        """
        Region screenshots as BGR uint8 arrays.

        Fast path: dxcam (Windows Desktop Duplication), typically 1-3 ms
        per region grab. Opt-in alternative: capture_backend = wgc uses
        Windows.Graphics.Capture via the optional 'windows-capture'
        package - push-based (frames only when the screen changes),
        more reliable than Desktop Duplication on some laptops and HDR
        setups. Any wgc failure degrades to the dxcam/mss chain.
        Two dxcam quirks are handled here:
        - dxcam only covers the primary display and returns None when the
          desktop has not redrawn since the last frame, so every grab
          falls back to mss when needed;
        - dxcam allows one camera per output per process, so the camera
          is shared behind a lock (SnappyAI scans are serialized anyway),
          while mss objects stay per-thread as mss requires.
        """

        def __init__(self, prefer="auto"):
            self.prefer = str(prefer or "auto").lower()
            self._dx_cam = None
            self._dx_tried = False
            self._dx_lock = threading.Lock()
            self._wgc_state = None
            self._wgc_tried = False
            self._wgc_lock = threading.Lock()
            # mss instances are per-thread (mss requires that), but the
            # click workers are DISPOSABLE threads and mss has no GC
            # finaliser - every instance holds GDI handles. The cache
            # keeps (thread, instance) pairs and closes the instances of
            # dead threads on the next grab, so long sessions cannot
            # leak GDI objects.
            self._mss_lock = threading.Lock()
            self._mss_cache = {}     # thread ident -> (thread, sct)
            self._notes = set()
            self._note_lock = threading.Lock()

        def _note(self, msg):
            with self._note_lock:
                if msg not in self._notes:
                    self._notes.add(msg)
                    log(msg)

        def _dx(self):
            with self._dx_lock:
                if self._dx_tried:
                    return self._dx_cam
                self._dx_tried = True

                if self.prefer not in ("auto", "dxcam", "wgc"):
                    return None

                try:
                    import dxcam
                except ImportError:
                    if self.prefer == "dxcam":
                        self._note("Capture: dxcam requested but not installed; using mss.")
                    return None

                try:
                    self._dx_cam = dxcam.create(output_color="BGR")
                    if self._dx_cam is None:
                        self._note("Capture: dxcam output busy; using mss.")
                    else:
                        self._note("Capture: dxcam active (fast path); mss kept as fallback.")
                except Exception as exc:
                    self._dx_cam = None
                    self._note("Capture: dxcam unavailable (%r); using mss. "
                               "Normal on Remote Desktop/VMs/old GPU drivers; "
                               "set capture_backend = mss in config.ini to "
                               "skip this message." % (exc,))

                return self._dx_cam

        def _mss(self):
            cur = threading.current_thread()
            with self._mss_lock:
                for tid in list(self._mss_cache):
                    thr, sct = self._mss_cache[tid]
                    if not thr.is_alive():
                        try:
                            sct.close()   # release GDI handles
                        except Exception:
                            pass
                        del self._mss_cache[tid]
                entry = self._mss_cache.get(cur.ident)
                if entry is None:
                    import mss
                    # mss >= 10 renamed the factory (mss.mss -> mss.MSS);
                    # support both so no DeprecationWarning is printed.
                    factory = getattr(mss, "MSS", None) or mss.mss
                    sct = factory()
                    self._mss_cache[cur.ident] = (cur, sct)
                else:
                    sct = entry[1]
            return sct

        def _wgc(self):
            """
            Opt-in Windows.Graphics.Capture backend (capture_backend =
            wgc), via the optional 'windows-capture' package (MIT,
            Rust core, abi3 wheel - works on modern CPythons).

            Push-based: the session delivers a frame ONLY when the
            screen actually changes and the latest one is kept in a
            buffer, so grab() is a lock + crop - no per-grab capture
            round trip, and a static desktop costs nothing (dxcam
            instead returns None on static screens and burns retries).
            The cursor is excluded (cursor_capture=False) so the
            pointer can never pollute colour statistics, and the
            yellow WGC border is disabled (draw_border=False).

            Any failure (package missing, old Windows, RDP quirks)
            degrades permanently to the dxcam/mss chain with a single
            log note - assistance never depends on this path.
            Returns (capture, state, lock) or None.
            """
            with self._wgc_lock:
                if self._wgc_tried:
                    return self._wgc_state
                self._wgc_tried = True
                if self.prefer != "wgc":
                    return None

                try:
                    from windows_capture import WindowsCapture
                except ImportError as exc:
                    self._note("Capture: wgc requested but the optional "
                               "'windows-capture' package could not be "
                               "imported (%r); falling back to dxcam/mss. "
                               "(pip install windows-capture - it also "
                               "needs numpy and opencv-python.)" % (exc,))
                    return None

                try:
                    state = {"frame": None, "closed": False, "errs": 0}
                    lock = threading.Lock()
                    cap = WindowsCapture(cursor_capture=False,
                                         draw_border=False,
                                         monitor_index=0,
                                         window_name=None)

                    def on_frame_arrived(frame, control):
                        try:
                            arr = None
                            # windows-capture 2.x hands the WGC callback
                            # a Frame with .frame_buffer: a ZERO-COPY
                            # view (h, w, 4) of the native mapped frame,
                            # in capture order BGRA. It must be copied
                            # out immediately - the native buffer is
                            # recycled by the session once the callback
                            # returns (keeping a view would pin a WGC
                            # pool buffer and starve delivery).
                            buf = getattr(frame, "frame_buffer", None)
                            if buf is not None:
                                arr = np.ascontiguousarray(
                                    np.asarray(buf)[:, :, :3],
                                    dtype=np.uint8)
                            else:
                                to_bgr = getattr(frame, "to_bgr", None)
                                if to_bgr is not None:
                                    # binding variants that expose the
                                    # colour format themselves (handles
                                    # bgra8, rgba8 and float16 HDR):
                                    # always yields BGR 0..255.
                                    arr = np.ascontiguousarray(
                                        to_bgr(), dtype=np.uint8)
                                else:
                                    to_np = getattr(frame, "to_numpy", None)
                                    if to_np is not None:
                                        arr = np.array(
                                            to_np(), dtype=np.uint8
                                        )[:, :, :3]
                            if arr is None:
                                # older/alternate binding surface
                                ptr = getattr(frame, "buffer_pointer", None)
                                fw = int(getattr(frame, "width", 0) or 0)
                                fh = int(getattr(frame, "height", 0) or 0)
                                if ptr and fw and fh:
                                    import ctypes
                                    cbuf = (ctypes.c_uint8
                                            * (fw * fh * 4)).from_address(
                                                int(ptr))
                                    arr = np.array(
                                        np.frombuffer(cbuf, np.uint8
                                                      ).reshape(fh, fw, 4
                                                                )[:, :, :3])
                            if (arr is None or arr.ndim != 3
                                    or arr.shape[2] != 3):
                                raise RuntimeError("frame has no usable "
                                                   "numpy accessor")
                            with lock:
                                # owned, contiguous BGR copy - never a
                                # view into the recycled native buffer
                                state["frame"] = np.ascontiguousarray(
                                    arr, dtype=np.uint8)
                                state["errs"] = 0
                        except Exception:
                            with lock:
                                state["errs"] += 1
                                if state["errs"] >= 30:
                                    state["closed"] = True

                    def on_closed():
                        with lock:
                            state["closed"] = True

                    cap.event(on_frame_arrived)
                    cap.event(on_closed)

                    if hasattr(cap, "start_free_threaded"):
                        cap.start_free_threaded()
                    else:
                        threading.Thread(target=cap.start, daemon=True,
                                         name="wgc-capture").start()

                    deadline = time.perf_counter() + 1.5
                    while time.perf_counter() < deadline:
                        with lock:
                            if state["frame"] is not None:
                                break
                            closed = state["closed"]
                        if closed:
                            break
                        time.sleep(0.02)

                    with lock:
                        first = state["frame"]
                    if first is None:
                        raise RuntimeError("session delivered no frame "
                                           "within 1.5 s")

                    self._wgc_state = (cap, state, lock)
                    self._note("Capture: wgc active "
                               "(Windows.Graphics.Capture, monitor 0, "
                               "frames %dx%d); dxcam/mss kept as fallback."
                               % (first.shape[0], first.shape[1]))
                except Exception as exc:
                    self._wgc_state = None
                    self._note("Capture: wgc unavailable (%r); falling "
                               "back to dxcam/mss." % (exc,))
                return self._wgc_state

        def _wgc_grab(self, region):
            """Crop the latest buffered WGC frame (owned BGR copy), or
            None when the region is not fully inside monitor 0."""
            st = self._wgc()
            if st is None:
                return None
            _cap, state, lock = st
            with lock:
                frame = state["frame"]
                closed = state["closed"]
            if closed:
                self._note("Capture: wgc session closed; using "
                           "dxcam/mss fallback.")
                return None
            if frame is None:
                return None
            fh, fw = frame.shape[:2]
            l, t, r, b = region
            # The session captures monitor 0 only: unless the region
            # lies FULLY inside that frame, the crop would be shifted
            # or short (and downstream code indexes it with cursor-
            # relative coordinates). Anything else - other monitors,
            # negative virtual-screen coords, overhang - hands over to
            # the dxcam/mss chain, which covers the virtual screen.
            if l < 0 or t < 0 or r > fw or b > fh or r <= l or b <= t:
                return None
            return np.ascontiguousarray(frame[t:b, l:r])

        def grab(self, left, top, right, bottom):
            """Return a contiguous BGR uint8 array, or None on failure."""
            region = (int(left), int(top), int(right), int(bottom))

            if self.prefer == "wgc":
                shot = self._wgc_grab(region)
                if shot is not None:
                    return shot
                # fall through: wgc -> dxcam -> mss

            cam = self._dx()
            if cam is not None:
                frame = None
                try:
                    with self._dx_lock:
                        # Retry briefly: a static desktop delivers no new
                        # frames, and grab() then returns None. Five tries
                        # is the sweet spot - a live frame almost always
                        # arrives within the first two, and each extra
                        # millisecond here delays the click itself. Past
                        # that the mss fallback below is faster than
                        # waiting on a desktop that is not redrawing.
                        for _ in range(5):
                            frame = cam.grab(region=region)
                            if frame is not None:
                                break
                            time.sleep(0.001)
                except Exception:
                    frame = None

                if frame is not None:
                    return np.ascontiguousarray(frame[:, :, :3], dtype=np.uint8)

            try:
                shot = self._mss().grab({
                    "left": region[0],
                    "top": region[1],
                    "width": region[2] - region[0],
                    "height": region[3] - region[1],
                })
                img = np.frombuffer(shot.bgra, dtype=np.uint8).reshape(
                    shot.height, shot.width, 4
                )[:, :, :3]
                return np.ascontiguousarray(img)
            except Exception as exc:
                self._note("Capture: mss error %r" % (exc,))
                return None

