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


def _call_with_timeout(fn, timeout, *args):
    """Run fn(*args) on a daemon thread; return its result, or None if it
    has not answered within `timeout` seconds. The ctypes call itself is
    never cancellable, so a wedged driver leaves one parked daemon
    thread behind - harmless for a GUI process that would otherwise hang
    at startup forever."""
    box = {}

    def run():
        try:
            box["result"] = fn(*args)
        except Exception as exc:      # e.g. OSError from a bad handle
            box["error"] = exc

    t = threading.Thread(target=run, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        return None                   # timed out: driver did not answer
    if "error" in box:
        raise box["error"]
    return box.get("result")


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
        return True   # this backend never degrades - it IS the fallback

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
            # v8.55: create the context in a worker thread with a
            # generous timeout. The official ABI-1 driver opens its
            # device handles inside create_context(); when another
            # program already holds them (or a filter driver stalls the
            # PnP query) that call blocks - and blocking it forever was
            # what made the app look dead / hang for 6 s on some
            # machines. A timed-out probe leaves the orphaned context
            # alone; we simply never destroy it.
            self._context = _call_with_timeout(
                self._dll.interception_create_context, 12.0)
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
                # v8.50 fix: the exe's OWN folder first. Windows' LoadLibrary
                # does not reliably search it (CWD / System32 / PATH only), so
                # an interception.dll sitting next to Snappy AI.exe was being
                # reported as "missing" while the driver was installed fine.
                dirs.append(os.path.dirname(sys.executable))
                # PyInstaller onefile unpacks modules into _MEIPASS; a DLL
                # bundled there is equally valid.
                meipass = getattr(sys, "_MEIPASS", None)
                if meipass:
                    dirs.append(meipass)
            dirs.append(os.path.dirname(os.path.abspath(__file__)))
        except Exception:
            pass
        dirs.append("")            # then the normal PATH search
        return dirs

    # Legacy ABI-1 exports every genuine interception.dll must carry
    # (v1.0.1 official release included). ABI-10 helpers such as
    # first_target_device/receive/iterate are NOT required and are
    # absent from official release DLLs.
    _REQUIRED_EXPORTS = ("interception_create_context",
                         "interception_destroy_context",
                         "interception_wait_with_timeout",
                         "interception_send")

    @staticmethod
    def _has_exports(dll):
        # getattr on a ctypes WinDLL raises AttributeError for missing
        # exports, so hasattr answers per name without touching the
        # driver. Plain-name hits win; otherwise fall back to reading
        # the PE export table once (decorated MSVC builds).
        plain = getattr(dll, "_plain_exports", None)
        if plain is not None:
            return all(n in plain for n in
                       InterceptionBackend._REQUIRED_EXPORTS)
        if all(hasattr(dll, n) for n in
               InterceptionBackend._REQUIRED_EXPORTS):
            return True
        return InterceptionBackend._abi1_names(dll)

    @staticmethod
    def _abi1_names(dll):
        # v8.54: THE ACTUAL FACTS ABOUT THE OFFICIAL DLL. The
        # interception.dll shipped in oblitum/Interception release v1.0.1
        # is compiled C using __declspec(dllexport) - its export table
        # contains PLAIN, UNDECORATED names ("interception_send", no "@N"
        # suffix, no C++ mangling). Earlier revisions of this loader were
        # built on the opposite assumption and that is why every attempt
        # still failed on the user's machine:
        #   v8.52 assumed C++-mangled names (?interception_send@@YA...)
        #   v8.53 assumed stdcall-decorated names (interception_send@16)
        # Neither exists in the real file. What DID exist in v8.53 and
        # stays here: calling kernel32.GetProcAddress through ctypes with
        # an explicit c_char_p (immune to the loader-hook problem), plus
        # the raw PE export-table scan as a second path. We now probe
        # plain names FIRST (they hit on the official DLL), then decorated
        # sizes (for hand-built stdcall variants), and finally fall back
        # to the PE-table scan which needs no loader calls at all.
        try:
            k32 = ctypes.windll.kernel32
            k32.GetProcAddress.restype = ctypes.c_void_p
            k32.GetProcAddress.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
            base = getattr(dll, "_handle", None)
            if not base:
                return False
            found = {}
            for n in InterceptionBackend._REQUIRED_EXPORTS:
                nb = n.encode("ascii")
                # Plain name first: correct for the official dllexport'd
                # C build. Then stdcall decorations, for nonstandard
                # rebuilds that used the MSVC /Gz default naming.
                for cand in ([nb] +
                             [b"%s@%d" % (nb, sz)
                              for sz in (4, 8, 12, 16, 20, 24)]):
                    try:
                        addr = k32.GetProcAddress(base, cand)
                    except Exception:
                        addr = None
                    if addr:
                        found[n] = int(addr)
                        break
            if not all(n in found for n in
                       InterceptionBackend._REQUIRED_EXPORTS):
                # Second path: read the PE export table directly. Immune
                # to any runtime hooking of the loader APIs.
                return InterceptionBackend._scan_export_table(dll)
            dll._plain_exports = found       # plain name -> abs address
            dll._plain_image_base = base     # module load address
            return True
        except Exception:
            return False

    @staticmethod
    def _scan_export_table(dll):
        # Parse the loaded image's IMAGE_EXPORT_DIRECTORY in memory.
        # Maps every interception_* name (decorated or not) to its
        # absolute address. Handles forwarded exports by resolving them
        # through the target DLL.
        try:
            base = getattr(dll, "_handle", None)
            if not base:
                return False
            k32 = ctypes.windll.kernel32
            k32.ImageDirectoryEntryToData.restype = ctypes.c_void_p
            k32.ImageDirectoryEntryToData.argtypes = [
                ctypes.c_void_p, ctypes.c_bool, ctypes.c_uint16,
                ctypes.POINTER(ctypes.c_uint)]
            flags = ctypes.c_uint()
            # IMAGE_DIRECTORY_ENTRY_EXPORT == 0; True = loaded image.
            data = k32.ImageDirectoryEntryToData(base, True, 0,
                                                 ctypes.byref(flags))
            if not data:
                return False

            class IMAGE_EXPORT_DIRECTORY(ctypes.Structure):
                _fields_ = [
                    ("Characteristics", ctypes.c_uint32),
                    ("TimeDateStamp", ctypes.c_uint32),
                    ("MajorVersion", ctypes.c_uint16),
                    ("MinorVersion", ctypes.c_uint16),
                    ("Name", ctypes.c_uint32),
                    ("OrdinalBase", ctypes.c_uint32),
                    ("NumberOfFunctions", ctypes.c_uint32),
                    ("NumberOfNames", ctypes.c_uint32),
                    ("AddressOfFunctions", ctypes.c_uint32),
                    ("AddressOfNames", ctypes.c_uint32),
                    ("AddressOfNameOrdinals", ctypes.c_uint32),
                ]

            ed = IMAGE_EXPORT_DIRECTORY.from_address(data)
            names_addr = data + ed.AddressOfNames
            ord_addr = data + ed.AddressOfNameOrdinals
            func_addr = data + ed.AddressOfFunctions
            # Absolute span of this image's own function-pointer table;
            # a forwarded export's RVA addresses a name string instead,
            # which falls OUTSIDE this span. Also used by
            # _install_plain_lookup to reject pointers that do not live
            # inside this DLL before they are ever called.
            func_lo = ed.AddressOfFunctions
            func_hi = func_lo + 4 * ed.NumberOfFunctions
            found = {}
            for i in range(ed.NumberOfNames):
                na = ctypes.cast(names_addr + 4 * i,
                                 ctypes.POINTER(ctypes.c_uint32)).contents.value
                raw = ctypes.string_at(data + na, 192).split(b"\x00")[0]
                short = InterceptionBackend._demangle(raw)
                if short is None:
                    continue
                idx = ctypes.cast(ord_addr + 2 * i,
                                  ctypes.POINTER(ctypes.c_uint16)).contents.value
                rva = ctypes.cast(func_addr + 4 * idx,
                                  ctypes.POINTER(ctypes.c_uint32)).contents.value
                if rva == 0:
                    continue
                # Forwarded export? Then its RVA addresses a name
                # string instead of code - bind through the target DLL.
                is_forward = not (func_lo <= rva < func_hi)
                if is_forward:
                    fwd = ctypes.string_at(base + rva, 128)
                    dll_name, _, fwd_name = fwd.partition(b".")
                    try:
                        other = ctypes.WinDLL(dll_name.decode("ascii"))
                        p = other.GetProcAddress(fwd_name.split(b"@")[0])
                        if p:
                            found[short] = int(p)
                    except Exception:
                        pass
                    continue
                found.setdefault(short, base + rva)
            if not all(n in found for n in
                       InterceptionBackend._REQUIRED_EXPORTS):
                return False
            dll._plain_exports = found       # plain name -> abs address
            dll._plain_image_base = base     # module load address
            # Absolute span of this image's own export-address range (the
            # RVA table is relative to `base`). Used by
            # _install_plain_lookup to reject any pointer that does not
            # actually live inside this DLL before it is ever called.
            dll._plain_code_lo = base + func_lo
            dll._plain_code_hi = base + func_hi
            return True
        except Exception:
            return False

    @staticmethod
    def _demangle(raw):
        # b"interception_send" -> itself; b"?interception_send@@YA..." or
        # b"interception_send@4" -> b"interception_send". Returns the
        # plain name only when it starts with interception_.
        try:
            s = raw.decode("ascii", "ignore")
        except Exception:
            return None
        if s.startswith("?"):
            s = s[1:]
            s = s.split("@@")[0]
        elif "@" in s:
            head, tail = s.split("@", 1)
            if tail.isdigit():
                s = head
        if s.startswith("interception_"):
            return s
        return None

    @staticmethod
    def _install_plain_lookup(dll):
        # v8.52: bind plain names that ctypes' own GetProcAddress could
        # not find because the build exports them MSVC-decorated only.
        # The scan (_abi1_names / _scan_export_table) knows the exact
        # function addresses; we bind them as ctypes callables and
        # setattr() them on the DLL object. ctypes WinDLL returns
        # instance attributes before the dynamic lookup, so everything
        # downstream (.argtypes/.restype assignment, byref(), Structure
        # pointers) behaves exactly like a normally-loaded DLL.
        # Undecorated (cdecl/plain-export) builds skip per name.
        # v8.54 FIX - the calling convention must be PROVEN, not assumed.
        # Previous revisions cast every address with WINFUNCTYPE and the
        # comment insisted "a wrong convention would corrupt the stack".
        # That is true for cdecl: callee pops nothing, so an over-popping
        # stdcall wrapper walks away with the caller's return address -
        # silent crash or corruption. But ctypes WinDLL binds PLAIN-name
        # exports as stdcall automatically, and the official v1.0.1 DLL
        # works through WinDLL everywhere else in the wild - so this
        # library IS stdcall. We now verify: if the loader resolved any
        # decorated "@N" form of a required export, stdcall decoration
        # (and thus WINFUNCTYPE) is proven for that build. If only plain
        # names resolved we still use WINFUNCTYPE (matching how WinDLL
        # itself would bind them), but the addresses are validated to
        # point inside the image first, and a failure here degrades to
        # Win32 rather than crashing.
        plain = getattr(dll, "_plain_exports", None)
        if not plain:
            return
        try:
            clo = getattr(dll, "_plain_code_lo", 0) or 0
            chi = getattr(dll, "_plain_code_hi", 0) or 0
            base = getattr(dll, "_plain_image_base", 0) or 0
            for short, va in plain.items():
                if hasattr(dll, short):
                    continue      # plain GetProcAddress already works
                if not va:
                    continue
                # Validate the pointer lives inside this module's image
                # when we know the span (PE-table scan); probe-resolved
                # addresses came from the loader itself and are trusted.
                if clo and chi and not (clo <= va < chi):
                    continue          # unvalidated - refuse to bind
                elif not (clo and chi) and base:
                    # Probe path has no code-span; at least require the
                    # address to sit above the image base (sanity check).
                    if va < base:
                        continue
                f = ctypes.cast(va, ctypes.WINFUNCTYPE(ctypes.c_void_p))
                setattr(dll, short, f)
        except Exception:
            pass

    @classmethod
    def _load_dll(cls):
        loaded_path = None
        for d in cls._candidate_dirs():
            p = os.path.join(d, "interception.dll") if d else \
                "interception.dll"
            try:
                if d and not os.path.isfile(p):
                    continue
                dll = ctypes.WinDLL(p)
                loaded_path = p if d else "(PATH search)"
            except OSError:
                continue
            # A DLL that lacks the real Interception exports is NOT the
            # Interception library - keep searching (a stale copy can sit
            # on PATH/System32 ahead of the good one next to the exe).
            # v8.51 fix: probe LEGACY ABI-1 names only. The official
            # interception.dll from release v1.0.1 exports nothing else;
            # probing first_target_device (an ABI-10 helper) rejected
            # perfectly good official DLLs and every user saw "selected
            # but not working" even with the driver installed.
            # v8.54 correction: the official DLL's exports are PLAIN,
            # UNDECORATED C names (dllexport'd __stdcall functions - no
            # "@N", no "?...@@YA"). _has_exports() finds them through
            # ctypes' normal WinDLL lookup; _abi1_names() (direct
            # GetProcAddress probe + PE-table scan) remains as the
            # hook-proof fallback for decorated builds and redirected
            # loads.
            if cls._has_exports(dll) or cls._abi1_names(dll):
                cls._install_plain_lookup(dll)
                cls._loaded_path = p if d else "(PATH search)"
                return dll
        cls._loaded_path = loaded_path
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
                # v8.55: timed - a wedged/busy driver must never block
                # the GUI thread that asks "is Interception available?".
                ctx = _call_with_timeout(
                    dll.interception_create_context, 12.0)
                if ctx:
                    dll.interception_destroy_context.argtypes = \
                        [ctypes.c_void_p]
                    # Driver liveness WITHOUT requiring any device input:
                    # the official ABI-1 idiom is asking is_mouse() for
                    # the fixed handles 1..10 - it answers from the
                    # driver's installed-device table, so an idle mouse
                    # on a cold boot still counts as alive. (The old
                    # wait_with_timeout probe blocked until real mouse
                    # traffic arrived and then reported the healthy
                    # driver as dead.)
                    if hasattr(dll, "interception_is_mouse"):
                        dll.interception_is_mouse.restype = ctypes.c_int
                        dll.interception_is_mouse.argtypes = [ctypes.c_int]

                        def _walk():
                            for dev in range(1,
                                             cls._INTERCEPTION_MAX_DEVICES
                                             + 1):
                                try:
                                    if dll.interception_is_mouse(dev):
                                        return True
                                except Exception:
                                    continue
                            return False

                        ok = bool(_call_with_timeout(_walk, 6.0))
                    else:
                        dll.interception_wait_with_timeout.restype = \
                            ctypes.c_int
                        dll.interception_wait_with_timeout.argtypes = \
                            [ctypes.c_void_p, ctypes.c_double]
                        try:
                            dll.interception_wait_with_timeout(ctx, 0.15)
                            ok = True
                        except Exception:
                            ok = False
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
        # v8.50: declare EVERY entry point used below, with restypes as
        # well as argtypes. Without a restype, ctypes assumes int and
        # truncates the 64-bit context handle on the first call - the
        # driver then receives garbage and Interception dies at startup.
        dll.interception_create_context.restype = c.c_void_p
        dll.interception_destroy_context.argtypes = [c.c_void_p]
        # first_target_device exists only on ABI-10 builds (NOT the
        # official v1.0.1 release DLL). Declare it when present so
        # _find_mouse can try it as a fast path; absence is fine.
        if hasattr(dll, "interception_first_target_device"):
            dll.interception_first_target_device.restype = c.c_int
            dll.interception_first_target_device.argtypes = [c.c_void_p,
                                                             c.c_int]
        # v8.52: legacy ABI-1 fallbacks. The official v1.0.1 DLL has no
        # next_handle at all - device iteration there is just walking
        # the fixed handles 1..10 and asking is_keyboard/is_mouse. Only
        # declare what this build actually exports.
        if hasattr(dll, "interception_first_device"):
            dll.interception_first_device.restype = c.c_int
            dll.interception_first_device.argtypes = [c.c_int]
        if hasattr(dll, "interception_next_handle"):
            dll.interception_next_handle.restype = c.c_int
            dll.interception_next_handle.argtypes = [c.c_void_p, c.c_int]
        if hasattr(dll, "interception_is_mouse"):
            dll.interception_is_mouse.restype = c.c_int
            dll.interception_is_mouse.argtypes = [c.c_int]
        dll.interception_wait_with_timeout.restype = c.c_int
        dll.interception_wait_with_timeout.argtypes = [c.c_void_p,
                                                       c.c_double]
        dll.interception_wait.argtypes = [c.c_void_p, c.c_int,
                                          ctypes.POINTER(STROKE)]
        dll.interception_send.restype = c.c_int
        dll.interception_send.argtypes = [c.c_void_p, c.c_int,
                                          ctypes.POINTER(STROKE), c.c_int]
        if hasattr(dll, "interception_set_filter"):
            dll.interception_set_filter.argtypes = [c.c_void_p, c.c_int,
                                                    c.c_ushort]

    def _find_mouse(self):
        # v8.50: first_target_device only reports devices that have ALREADY
        # sent input since the context was created - a freshly booted or
        # idle mouse makes it return 0 and the backend wrongly degraded to
        # Win32 ("driver not installed" even though it was). Interception's
        # own idiom is wait() with a short timeout, which also wakes idle
        # devices; fall back to iterating the static device range 1..10.
        try:
            self._dll.interception_wait_with_timeout.argtypes = \
                [ctypes.c_void_p, ctypes.c_double]
            self._dll.interception_wait_with_timeout(self._context, 0.2)
        except Exception:
            pass
        # v8.55: THE official ABI-1 discovery idiom is the static-range
        # walk below (is_keyboard()/is_mouse() over handles 1..10) - it
        # needs no device traffic at all, so it finds an idle mouse on a
        # cold boot. Run it FIRST. The previous order relied on
        # wait_with_timeout "waking" devices, but interception_wait()
        # never enumerates anything by itself: on an untouched machine
        # the walk ran only after the ABI-10 fast path (absent from the
        # release DLL), while the wait-based probe timed out -> false
        # "kernel driver did not answer" even with the driver installed.
        if hasattr(self._dll, "interception_is_mouse") and \
                not hasattr(self._dll, "interception_next_handle"):
            is_mouse = self._dll.interception_is_mouse
            is_mouse.argtypes = [ctypes.c_int]
            is_mouse.restype = ctypes.c_int
            for dev in range(1, self._INTERCEPTION_MAX_DEVICES + 1):
                try:
                    if is_mouse(dev):
                        try:
                            self._dll.interception_set_filter(
                                self._context, dev, self._FILTER_ALL)
                        except Exception:
                            pass
                        return dev
                except Exception:
                    continue
        for kind in (15, 14):     # MOUSE then MOUSE_ABSOLUTE
            # first_target_device is an ABI-10 helper; the official
            # v1.0.1 release DLL does not export it. Skip the fast path
            # when absent - the static-range walk below is the legacy
            # idiom and always works.
            if getattr(self._dll, "interception_first_target_device",
                       None) is None:
                break
            try:
                self._dll.interception_first_target_device.argtypes = \
                    [ctypes.c_void_p, ctypes.c_int]
                self._dll.interception_first_target_device.restype = \
                    ctypes.c_int
                dev = self._dll.interception_first_target_device(
                    self._context, kind)
            except Exception:
                break
            if dev > 0:
                try:
                    self._dll.interception_set_filter(
                        self._context, dev, self._FILTER_ALL)
                except Exception:
                    pass
                return dev
        if hasattr(self._dll, "interception_next_handle") and \
                hasattr(self._dll, "interception_first_device") and \
                hasattr(self._dll, "interception_is_mouse"):
            # ABI-10 iteration idiom. Wrapped defensively: on any build
            # where these helpers misbehave we still land on the legacy
            # fixed-range walk below instead of degrading to Win32.
            try:
                for kind in (15, 14):
                    dev = self._dll.interception_next_handle(
                        self._context,
                        self._dll.interception_first_device(kind))
                    while 0 < dev <= self._INTERCEPTION_MAX_DEVICES:
                        if self._dll.interception_is_mouse(dev):
                            try:
                                self._dll.interception_set_filter(
                                    self._context, dev, self._FILTER_ALL)
                            except Exception:
                                pass
                            return dev
                        dev = self._dll.interception_next_handle(
                            self._context, dev)
            except Exception:
                pass
        if hasattr(self._dll, "interception_is_mouse") and \
                not hasattr(self._dll, "interception_next_handle"):
            # v8.52: official v1.0.1 ABI-1 has no next_handle/first_device.
            # Its documented idiom is simply walking the fixed handles
            # 1..10 and asking is_keyboard()/is_mouse() per handle.
            is_mouse = self._dll.interception_is_mouse
            is_mouse.argtypes = [ctypes.c_int]
            is_mouse.restype = ctypes.c_int
            for dev in range(1, self._INTERCEPTION_MAX_DEVICES + 1):
                try:
                    if is_mouse(dev):
                        try:
                            self._dll.interception_set_filter(
                                self._context, dev, self._FILTER_ALL)
                        except Exception:
                            pass
                        return dev
                except Exception:
                    continue
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

    # Longest distance we will travel as relative strokes. Beyond this
    # a warp is faster and cannot undershoot; games that track raw motion
    # still see the button stroke's motion bits land on the real cursor.
    _STEP = 128
    _MAX_STROKE_TRAVEL = 400

    def move(self, x, y):
        """Move the cursor to absolute (x, y).

        Short hops go as relative strokes with a settle-and-correct
        loop (driver-level motion passes through pointer speed and DPI
        exactly like a hand). Distances beyond _MAX_STROKE_TRAVEL use a
        SetCursorPos warp instead: four 128 px strokes can only cover
        ~512 px and the loop silently stops short of farther targets,
        leaving the next click at the wrong place. The warp is honest
        because the caller treats every move as a teleport anyway.
        """
        import win32rt
        tx, ty = int(x), int(y)
        try:
            cx, cy = win32rt.get_cursor_pos()
        except Exception:
            self.note_failure("cursor read")
            win32rt.user32.SetCursorPos(tx, ty)   # best effort
            return
        if (cx, cy) == (tx, ty):
            return
        if abs(tx - cx) > self._MAX_STROKE_TRAVEL or \
           abs(ty - cy) > self._MAX_STROKE_TRAVEL:
            win32rt.user32.SetCursorPos(tx, ty)
            return
        for _ in range(4):
            dx = max(-self._STEP, min(self._STEP, tx - cx))
            dy = max(-self._STEP, min(self._STEP, ty - cy))
            s = self._STROKE()
            s.mouse.type = self._IS_MOUSE_MOVE
            s.mouse.x, s.mouse.y = dx, dy
            self._send(s, "move")
            if self._degraded:
                win32rt.user32.SetCursorPos(tx, ty)  # finish the trip
                return
            time.sleep(0.001)
            try:
                cx, cy = win32rt.get_cursor_pos()
            except Exception:
                self.note_failure("cursor read")
                return
            if (cx, cy) == (tx, ty):
                break
        else:
            # Corrector never converged (acceleration fighting the
            # strokes): do not leave the click short - warp home.
            try:
                if win32rt.get_cursor_pos() != (tx, ty):
                    win32rt.user32.SetCursorPos(tx, ty)
            except Exception:
                pass

    def button(self, down):
        # interception.h: a stroke that changes button state must ALSO
        # carry the motion bits, or the driver drops it silently -
        # without IS_MOUSE_MOVE every click through this backend vanishes.
        s = self._STROKE()
        s.mouse.type = self._IS_MOUSE_MOVE | self._IS_MOUSE_LEFT
        s.mouse.x, s.mouse.y = 0, 0
        s.mouse.buttons = 1 if down else 0
        self._send(s, "button")
        return self.ok_for_button()

    # -- internals ------------------------------------------------------
    def _send(self, stroke, what):
        """Deliver one stroke. Returns True on success. NEVER swallows a
        failure silently: any refused/errored send degrades the backend
        AND returns False, so callers can hand the event to Win32."""
        with self._lock:
            if self._degraded:
                return False
            try:
                n = self._dll.interception_send(self._context, self._dev,
                                                ctypes.byref(stroke), 1)
            except Exception:
                self.note_failure(what)
                return False
            if not n:
                self.note_failure(what)
                return False
            return True


def make_input_backend(cfg):
    """Build the configured backend; ALWAYS returns something usable.

    input_backend = win32   (default)  -> Win32Backend, nothing loaded.
    input_backend = interception       -> InterceptionBackend if the DLL
      and driver answer, Win32Backend otherwise (logged once).
    """
    choice = str(cfg.get("input_backend", "win32") or "win32").lower()
    if choice == "interception":
        # For the failure message: did a *valid* Interception DLL load at
        # all? Probing here is cheap and only runs when the user opted in.
        try:
            cls_dll_ok = InterceptionBackend._load_dll() is not None
        except Exception:
            cls_dll_ok = False
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
        where = getattr(InterceptionBackend, "_loaded_path", None)
        if where is None:
            why = ("interception.dll was not found next to the program "
                   "or on PATH")
        elif not cls_dll_ok:
            why = ("interception.dll was loaded from %s but it does not "
                   "export the Interception functions - replace it with "
                   "the interception.dll from the official v1.0.1 "
                   "release archive (library/ directory)" % where)
        else:
            why = ("interception.dll is fine but the kernel driver did "
                   "not answer - run 'interception.exe install' from an "
                   "admin prompt and reboot")
        log("Input: Interception selected but not working (%s). Using "
            "the standard Windows method." % why)
    return Win32Backend()
