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


class _Timeout(Exception):
    """Raised by _call_with_timeout when the callee never answered."""


def _call_with_timeout(fn, timeout, *args):
    """Run fn(*args) on a daemon thread; RETURN its result, or raise
    _Timeout if it has not answered within `timeout` seconds.

    v8.61: this used to signal a timeout by returning None - which is
    indistinguishable from a function that legitimately answers "nothing
    found". Our discovery walk returns None exactly that way, so every
    empty answer was mis-reported as "device discovery did not return
    within 8 s (driver installed but wedged)" even when the driver had
    answered instantly and simply listed no mouse. Raising makes the two
    cases impossible to confuse. The ctypes call itself is never
    cancellable, so a genuinely wedged driver still leaves one parked
    daemon thread behind - harmless for a GUI process that would
    otherwise hang at startup forever."""
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
        raise _Timeout("did not return within %.0f s" % timeout)
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
    # v8.62: Interception's handle space is 1..20, NOT 1..10. Handles
    # 1..10 are HARDWARE (observer) devices - they receive real input;
    # 11..20 are SOFTWARE (target) devices - the ones interception_send
    # injects through. The official headers define INTERCEPTION_MAX_KEYBOARD
    # / INTERCEPTION_MAX_MOUSE as 10 each per category, and working
    # examples loop dev over 1..(2*max) checking is_mouse(dev). Probing
    # only 1..10 missed every software mouse handle (11..20), which is
    # why healthy installs reported "the driver lists no mouse".
    _INTERCEPTION_HARDWARE_DEVICES = 10
    _INTERCEPTION_MAX_DEVICES = 20
    _WHEEL_MS = 8                # tiny pause so scroll planes never
                                 # swallow wheel messages behind a burst

    def __init__(self, ctx=None):
        self._lock = threading.Lock()
        self._degraded = False       # sticky: fall back to Win32 forever
        self._ctx = ctx              # optional pre-built context (tests)
        self._dll = None
        self._dev = None
        self._reason = ""            # why init failed (for honest logs)
        if ctx is not None:
            return                 # test double: nothing to load
        if not IS_WINDOWS:
            self._degraded = True
            return
        try:
            # v8.58: EVERY kernel-driver handshake runs behind a timeout
            # on a daemon thread. interception.dll's DllMain enumerates
            # devices at LoadLibrary time and interception_create_context
            # opens the driver handles - either can block indefinitely
            # when the filter driver is wedged or another program holds
            # the devices. Until now those calls ran synchronously on
            # the main GUI thread, so one blocked call meant "process
            # exists, no window, forever" - exactly the silent-death
            # report from users whose machine has interception.dll next
            # to the exe. A timed-out probe parks a harmless daemon
            # thread instead of parking the whole app.
            load = _call_with_timeout(self._load_dll, 8.0)
            if not load:
                # legitimately "no DLL anywhere" (never a timeout -
                # those raise _Timeout now): stay silent here and let
                # make_input_backend() print the accurate one-liner.
                self._degraded = True
                return
            self._dll, frozen = load
            if frozen:
                self._reason = ("interception.dll appears frozen by "
                                "antivirus software (file handle open by "
                                "another process, scan never finishes)")
                self._degraded = True
                return
            if self._dll is None:
                self._degraded = True
                return
            self._build_signatures()
            ctx = _call_with_timeout(
                self._dll.interception_create_context, 8.0)
            if not ctx:
                self._reason = ("interception_create_context returned no "
                                "context - reinstall the driver with "
                                "'interception.exe install' from an admin "
                                "prompt and reboot")
                self._degraded = True
                return
            self._context = ctx
            # v8.59: THE ORDERING BUG BEHIND "device discovery did not
            # return within 8 s" on HEALTHY installs. Interception's ABI-1
            # interception_wait()/interception_wait_with_timeout() do NOT
            # merely poll - the FIRST call attaches the user-mode filter
            # to every installed device, which requires each device to
            # answer. An idle mouse answers nothing until real traffic
            # arrives, so that first wait blocks for its whole timeout.
            # Our old code called wait_with_timeout(ctx, 0.2) as a
            # "wake-up" before the static-range walk; with PyInstaller's
            # GIL switch interval (default 5 ms) the parked worker never
            # got scheduled inside 8 s and _find_mouse timed out - even
            # though the driver was perfectly alive (create_context had
            # just succeeded). The official ABI-1 discovery idiom is the
            # static-range walk of is_mouse(1..10), which reads the
            # driver's installed-device TABLE and needs no device
            # traffic at all. So: discover first; only wake devices via
            # a short bounded wait if the table says there are none.
            found = _call_with_timeout(self._find_mouse, 8.0)
            self._dev = found
            if self._dev is None:
                # Cold-boot / idle case: ask the driver to attach to the
                # devices once (bounded), then re-walk the table. This
                # runs on a daemon thread behind a timeout, so even a
                # wedged wait here cannot park the GUI.
                def _wake_and_walk():
                    try:
                        self._dll.interception_wait_with_timeout.argtypes = \
                            [ctypes.c_void_p, ctypes.c_double]
                        self._dll.interception_wait_with_timeout(
                            self._context, 0.2)
                    except Exception:
                        pass
                    return self._find_mouse()

                try:
                    self._dev = _call_with_timeout(_wake_and_walk, 4.0)
                except _Timeout:
                    self._dev = None
            if self._dev is None:
                # v8.61 DIAGNOSTIC PROBE: before blaming the driver's
                # table, send one zero-effect stroke (type 0 = carries
                # no button or motion state) to handle 1 and read the
                # return value. This distinguishes "the library loaded
                # but its handles never reached the kernel driver"
                # (send returns 0 - e.g. a non-Interception DLL with
                # same-named stub exports, or a driver whose control
                # device could not be opened despite create_context
                # succeeding) from "the driver answers but genuinely
                # lists no mouse". Without this, both cases print the
                # same message and users keep reinstalling a perfectly
                # fine driver.
                probe = "?"
                try:
                    st = self._STROKE()
                    st.mouse.type = 0
                    n = self._dll.interception_send(self._context, 1,
                                                    ctypes.byref(st), 1)
                    probe = ("interception_send(handle 1) returned %r"
                             % (n,))
                except Exception as exc:
                    probe = "interception_send raised %r" % (exc,)
                self._reason = ("the driver answered but reports no mouse "
                                "device (is the mouse connected through a "
                                "driver the filter does not see? probe: "
                                "%s)" % probe)
                log("Input: Interception found no mouse device. Probe: %s. "
                    "If the probe says it returned 0, the loaded DLL is "
                    "not really talking to the kernel driver - replace it "
                    "with interception.dll from the official v1.0.1 "
                    "archive (library/ folder). Using Windows injection."
                    % probe)
                self._degraded = True
        except _Timeout as exc:
            # v8.61: real timeouts now raise instead of returning None,
            # so this branch can only mean a call genuinely hung - never
            # a legitimate "nothing found" answer that used to be
            # mislabelled "driver installed but wedged".
            log("Input: Interception init timed out (%s); using Windows "
                "injection instead." % (exc,))
            self._reason = str(exc)
            self._degraded = True
        except Exception as exc:
            log("Input: Interception init failed (%r); using Windows "
                "injection instead." % (exc,))
            self._reason = repr(exc)
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
        # v8.57: ctypes' own lookup FIRST. The official v1.0.1 DLL
        # exports plain dllexport'd C names, so this hits on any genuine
        # library and we never touch the loader APIs at all.
        if all(hasattr(dll, n) for n in
               InterceptionBackend._REQUIRED_EXPORTS):
            return True
        # Only nonstandard (decorated) rebuilds fall through to the
        # direct GetProcAddress probe. No PE-table scan anywhere: that
        # path loaded contract DLLs via forwarded-export resolution and
        # silently killed the process (v8.56 regression). A DLL that
        # fails both checks is simply not Interception - keep searching.
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
        # an explicit c_char_p (immune to the loader-hook problem). We
        # probe plain names FIRST (they hit on the official DLL), then
        # decorated sizes for hand-built stdcall variants. There is NO
        # PE-export-table fallback any more - see the v8.58 note below;
        # if this probe cannot find the names, the file is not a usable
        # Interception library and _load_dll keeps searching.
        try:
            k32 = ctypes.windll.kernel32
            k32.GetProcAddress.restype = ctypes.c_void_p
            k32.GetProcAddress.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
            # v8.58: this fallback must NEVER load another module. The
            # old code called LoadLibraryExW(LOAD_LIBRARY_AS_DATAFILE)
            # via _module_handle() when the DLL arrived through a
            # redirected/PATH search - forwarding to api-ms-win-crt-*
            # contract stubs and destabilising the process (the silent-
            # death family of bugs). If we do not already know the real
            # image base from our own explicit-path load, we simply give
            # up on decorated-name probing; the plain ctypes lookup in
            # _has_exports() already covers every genuine DLL.
            base = getattr(dll, "_snappy_module", 0) or 0
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
                # v8.57/58: NO PE-export-table fallback - it loaded
                # api-ms-win-crt-* contract modules mid-startup via
                # forwarded-export resolution and silently killed the
                # process. If the GetProcAddress probe cannot find the
                # four required names, this file is not a usable
                # Interception library; _load_dll keeps searching.
                return False
            dll._plain_exports = found       # plain name -> abs address
            dll._plain_image_base = base     # module load address
            return True
        except Exception:
            return False

    # v8.58: the PE-export-table scanner of v8.56 is DELETED, not just
    # disabled. It resolved forwarded exports by calling WinDLL() on the
    # forward-target name found at an RVA inside our own file read - for
    # MSVC-built DLLs that name is an api-ms-win-crt-* contract stub,
    # and Windows' API-set shim loads the real runtime DLL into the
    # process mid-startup. That loader interference is what made Snappy
    # AI sit in the process list with no window whenever
    # interception.dll was present. Nothing here may ever load a module
    # other than the one the user pointed us at; ctypes' plain lookup
    # plus a GetProcAddress probe on OUR OWN handle cover every genuine
    # build between them.

    @staticmethod
    def _install_plain_lookup(dll):
        # Bind the plain names our scan resolved but ctypes' own lookup
        # could not find (decorated-only builds). The scan knows exact
        # addresses; we cast them to stdcall callables and setattr()
        # them on the DLL object - ctypes WinDLL returns instance
        # attributes before dynamic lookup, so everything downstream
        # (.argtypes/.restype, byref(), Structure pointers) behaves
        # like a normally-loaded DLL.
        # v8.56: RVA-vs-absolute bookkeeping is explicit now. The
        # file-based scan records RVAs (offset them by the handle we
        # really loaded via LoadLibraryEx - never ctypes' private
        # `_handle`, which is NOT an HMODULE); GetProcAddress-probe and
        # forwarded-export entries are already absolute and trusted.
        # Forwarded exports resolve through the target DLL instead.
        plain = getattr(dll, "_plain_exports", None)
        if not plain:
            return
        try:
            rvas = bool(getattr(dll, "_plain_rvas", False))
            module = getattr(dll, "_snappy_module", 0) or 0
            for short, va in list(plain.items()):
                if hasattr(dll, short):
                    continue      # plain GetProcAddress already works
                if not va:
                    continue
                if rvas:
                    if not module:
                        continue          # cannot offset - refuse to bind
                    addr = module + int(va)   # RVA -> absolute
                else:
                    addr = int(va)            # absolute, probe-resolved
                f = ctypes.cast(addr, ctypes.WINFUNCTYPE(ctypes.c_void_p))
                setattr(dll, short, f)
        except Exception:
            pass

    @staticmethod
    def _module_handle(path):
        """True HMODULE for an already-loaded DLL.

        LoadLibraryExW with LOAD_LIBRARY_AS_DATAFILE (0x2) maps the file
        as data only - it never runs DllMain and never blocks on a wedged
        driver - but its return value is still based on the image's load
        address, so `handle & ~0x3` recovers the same base the normal
        WinDLL load used. This is the officially sanctioned idiom for
        reading a loaded module's headers; ctypes' private `_handle` is
        NOT an HMODULE and must never be used for this."""
        if not IS_WINDOWS:
            return 0
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.LoadLibraryExW.restype = ctypes.c_void_p
        k32.LoadLibraryExW.argtypes = [ctypes.c_wchar_p, ctypes.c_void_p,
                                       ctypes.c_uint]
        h = k32.LoadLibraryExW(os.path.abspath(path), None, 0x2)
        if not h:
            return 0
        try:
            k32.FreeLibrary(ctypes.c_void_p(h))   # drop the data mapping
        except Exception:
            pass
        return int(h) & ~0x3

    @staticmethod
    def _file_frozen(path):
        """True when another process holds an exclusive handle on the
        file - the classic signature of antivirus mid-scan (or a
        quarantined stub). Windows returns ERROR_SHARING_VIOLATION; we
        deliberately do NOT treat ACCESS_DENIED as frozen, since that is
        normal NTFS ACL behaviour for files the user may still load.

        v8.58: checked BEFORE LoadLibrary, because WinDLL() on a
        scan-frozen file blocks inside the loader until the AV releases
        it - unbounded, on whichever thread called us."""
        try:
            k32 = ctypes.WinDLL("kernel32", use_last_error=True)
            k32.CreateFileW.restype = ctypes.c_void_p
            k32.CreateFileW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint,
                                        ctypes.c_uint, ctypes.c_void_p,
                                        ctypes.c_uint, ctypes.c_uint,
                                        ctypes.c_void_p]
            INVALID = ctypes.c_void_p(-1).value
            # GENERIC_READ(0) + FILE_SHARE_ALL + OPEN_EXISTING: pure
            # existence-of-handle probe, never reads or locks anything.
            h = k32.CreateFileW(os.path.abspath(path), 0, 7, None, 1, 0x80,
                                None)
            if h == INVALID or h is None:
                err = ctypes.get_last_error()
                return err == 32          # ERROR_SHARING_VIOLATION
            k32.CloseHandle(ctypes.c_void_p(h))
            return False
        except Exception:
            return False                  # probe failed -> assume fine

    @classmethod
    def _load_dll(cls):
        """Returns (dll_or_None, froze_flag). Called only through
        _call_with_timeout: even if this hangs inside WinDLL()/DllMain
        (wedged kernel driver answering device enumeration at load
        time), the caller gives up after its timeout and the GUI keeps
        running on Win32."""
        loaded_path = None
        for d in cls._candidate_dirs():
            p = os.path.join(d, "interception.dll") if d else \
                "interception.dll"
            try:
                if d and not os.path.isfile(p):
                    continue
                if d and cls._file_frozen(p):
                    # Do not attempt the load: it would park a thread
                    # inside the AV-suspended loader for who-knows-how
                    # long. Report honestly instead.
                    cls._loaded_path = p
                    return None, True
                dll = ctypes.WinDLL(p)
                loaded_path = p if d else "(PATH search)"
            except OSError:
                continue
            # v8.58: the image base is recorded ONLY for explicit-path
            # loads (d is truthy). For the PATH-search fallback we pass
            # 0, which makes _abi1_names() a no-op - deliberately: the
            # LoadLibraryExW probe it used could resolve api-set
            # forwards and load contract DLLs mid-startup, the exact
            # class of loader interference behind the silent-death
            # reports. The plain ctypes lookup in _has_exports() needs
            # no module handle at all and covers genuine DLLs.
            try:
                dll._snappy_module = (cls._module_handle(p) if d else 0)
            except Exception:
                dll._snappy_module = 0
            dll._snappy_path = os.path.abspath(p) if d else None
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
                return dll, False
        cls._loaded_path = loaded_path
        return None, False

    @classmethod
    def _load_dll_probe(cls):
        """Timeout-safe wrapper around _load_dll for callers that must
        never block (the GUI thread). Returns (dll_or_None, frozen);
        (None, True) also means 'the load call itself hung'. v8.61:
        timeouts now raise _Timeout instead of returning None, so the
        two cases are told apart properly."""
        if not IS_WINDOWS:
            return None, False
        try:
            return _call_with_timeout(cls._load_dll, 8.0)
        except _Timeout:
            cls._loaded_path = getattr(cls, "_loaded_path", None)
            return None, True          # hung inside loader/DllMain

    @classmethod
    def available(cls):
        """Cheap check for the GUI: DLL present AND driver devices alive.

        Safe off Windows and without the library: returns False, never
        raises. Result is cached after the first probe. v8.58: every
        kernel-facing step runs behind _call_with_timeout - this is
        called from a worker thread in gui.py but must still be unable
        to park anything forever."""
        if not IS_WINDOWS:
            return False
        cached = getattr(cls, "_avail_cache", None)
        if cached is not None:
            return cached
        ok = False
        try:
            dll, frozen = cls._load_dll_probe()
            if dll is not None and not frozen:
                dll.interception_create_context.restype = ctypes.c_void_p
                try:
                    ctx = _call_with_timeout(
                        dll.interception_create_context, 6.0)
                except _Timeout:
                    ctx = None
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

                        try:
                            ok = bool(_call_with_timeout(_walk, 6.0))
                        except _Timeout:
                            ok = False
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

    def _query_table(self):
        """v8.62 THE REAL BUG: we walked handles 1..10, but Interception
        splits them in two ranges - 1..10 are HARDWARE (observer)
        devices and 11..20 are SOFTWARE (target) devices. Every working
        example shipped with the library (mx.c, send.c) iterates
        INTERCEPTION_MAX_MOUSE = 20 and sends through the handle where
        is_mouse() is TRUE IN THE 11..20 RANGE. Our old 1..10-only walk
        therefore reported 'the driver lists no mouse' on perfectly
        healthy installs: the kernel driver DID list the mouse, just at
        handle 11+, above our blind window. That is exactly this user's
        symptom ('driver answered, table lists no mouse', probe send to
        handle 1 returning 1). Query both ranges."""
        found = []                  # [(dev, is_mouse_bool), ...]
        if not hasattr(self._dll, "interception_is_mouse"):
            return found
        is_mouse = self._dll.interception_is_mouse
        is_mouse.argtypes = [ctypes.c_int]
        is_mouse.restype = ctypes.c_int
        for dev in range(1, self._INTERCEPTION_MAX_DEVICES + 1):
            try:
                found.append((dev, bool(is_mouse(dev))))
            except Exception:
                continue
        return found

    def _find_mouse(self):
        # v8.60: EVERY branch of discovery is tried on EVERY build.
        # v8.59 gated the static-range walk behind
        # "has is_mouse AND NOT has next_handle", which assumed ABI-1
        # and ABI-10 builds are mutually exclusive - they are not. A
        # DLL that exports BOTH helper sets skipped the walk entirely,
        # fell into the ABI-10 iteration path, and when that returned
        # nothing died with "found no mouse target device" even though
        # the plain 1..10 walk would have answered instantly. The
        # ordering insight from v8.59 stands: NEVER open with a
        # blocking wait (ABI-1's first wait attaches the filter to
        # every device and blocks until real traffic arrives); wake-up
        # happens only as a bounded fallback in __init__.
        table = self._query_table()
        # v8.62: prefer the SOFTWARE (target) half of the range, 11..20 -
        # that is the handle official examples send strokes through.
        for dev, kind in table:
            if kind and dev > self._INTERCEPTION_HARDWARE_DEVICES:
                try:
                    self._dll.interception_set_filter(
                        self._context, dev, self._FILTER_ALL)
                except Exception:
                    pass
                return dev
        # Fall back to a hardware (observer) handle only if the software
        # half listed nothing - sending there still works on some
        # setups, and beats degrading outright.
        for dev, kind in table:
            if kind:
                try:
                    self._dll.interception_set_filter(
                        self._context, dev, self._FILTER_ALL)
                except Exception:
                    pass
                return dev
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
        # v8.60: the static-range walk at the TOP of this function already
        # covered every build that exports is_mouse(); there is nothing
        # left to re-walk here. Reaching this point means BOTH the table
        # walk and the ABI-10 iteration came up empty on a DLL whose
        # create_context just succeeded - so the driver IS answering but
        # genuinely reports no mouse through this context. The old tail
        # duplicate of the walk (gated on "no next_handle") could never
        # fire after the top walk ran: same inputs, same result.
        log("Input: Interception found no mouse target device - the "
            "driver answered but its device table lists no mouse. "
            "Reinstall it ('interception.exe install' from an admin "
            "prompt), reboot, and make sure the mouse is plugged in "
            "before Snappy AI starts. Using Windows injection.")
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
            be = None
        where = getattr(InterceptionBackend, "_loaded_path", None)
        reason = getattr(be, "_reason", "") if be is not None else ""
        if where is None:
            why = ("interception.dll was not found next to the program "
                   "or on PATH")
        elif reason:
            # v8.56: say exactly what failed instead of blaming the user's
            # driver install by default. The previous blanket "kernel
            # driver did not answer" message fired even when the real
            # cause was our own probe timing out or discovery finding no
            # mouse device - and after three revisions of wrong guesses it
            # was no longer trustworthy.
            why = "startup check failed: %s" % reason
        else:
            why = ("interception.dll loaded from %s and answered, but no "
                   "mouse device was found behind it - confirm the driver "
                   "is installed ('interception.exe install' from an "
                   "admin prompt, then reboot)" % where)
        log("Input: Interception selected but not working (%s). Using "
            "the standard Windows method." % why)
    return Win32Backend()
