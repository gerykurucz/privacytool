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
            # v8.54c: create_context()/device discovery can BLOCK for
            # seconds inside a flaky or half-installed kernel driver.
            # This constructor runs on whatever thread first builds the
            # backend - historically the GUI main thread via the settings
            # probe and start_app(). A blocked main thread means the
            # window NEVER paints while the process sits alive in Task
            # Manager (the exact field symptom). Run the whole driver
            # handshake on a helper thread with a hard deadline; on
            # timeout we stay degraded to Win32 and the abandoned
            # daemon thread can never hurt anything.
            import queue as _q
            box = _q.Queue()
            def _handshake():
                try:
                    ctx = self._dll.interception_create_context()
                    if not ctx:
                        box.put(("ctx", None))
                        return
                    self._context = ctx
                    dev = self._find_mouse()
                    box.put(("dev", dev))
                except BaseException as e:      # incl. ctypes errors
                    box.put(("err", e))
            t = threading.Thread(target=_handshake, daemon=True,
                                 name="icpt-init")
            t.start()
            try:
                kind, val = box.get(timeout=6.0)
            except Exception:
                log("Input: Interception driver did not answer within "
                    "6 s (a wedged kernel driver? reinstall + reboot); "
                    "using Windows injection.")
                self._degraded = True
                return
            if kind == "err":
                raise val
            if kind == "ctx" or val is None:
                self._degraded = True
                return
            self._dev = val
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

    # v8.54c: optional exports this file probes with hasattr(). On a
    # WinDLL object hasattr is NOT safe (the @N-appending getter raises
    # AttributeError straight through it), so these must be bound via
    # setattr from the real export lookup - then hasattr answers False
    # honestly when absent and True when present.
    _OPTIONAL_EXPORTS = ("interception_first_target_device",
                         "interception_first_device",
                         "interception_next_handle",
                         "interception_is_mouse",
                         "interception_is_keyboard",
                         "interception_set_filter",
                         "interception_wait",
                         "interception_receive",
                         "interception_destroy_device")

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
        # v8.54c: NO hasattr on WinDLL here - its function-getter appends
        # "@N" to every lookup and raises AttributeError straight through
        # hasattr when only plain names exist (the official DLL case!).
        # kernel32.GetProcAddressA answers the real export table instead.
        try:
            k32 = ctypes.windll.kernel32
            gpa = k32.GetProcAddressA
            gpa.restype = ctypes.c_void_p
            gpa.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
            base = getattr(dll, "_handle", None) or                    ctypes.windll.kernel32.GetModuleHandleW("interception.dll")
            if base:
                for n in InterceptionBackend._REQUIRED_EXPORTS:
                    if not gpa(base, n.encode("ascii")):
                        break
                else:
                    return True
        except Exception:
            pass
        return InterceptionBackend._abi1_names(dll)

    @staticmethod
    def _bind_all_exports(dll):
        # v8.54c: THE ACTUAL BUG THAT KEPT INTERCEPTION DEAD - AND FROZE
        # THE GUI. ctypes.WinDLL is a CDLL subclass whose function-getter
        # appends "@N" to EVERY name it looks up, unconditionally. The
        # official interception.dll exports PLAIN C names (dllexport'd,
        # no decoration). So "dll.interception_create_context" raises
        # AttributeError("... not found") even though the export exists -
        # and worse, hasattr() on WinDLL calls that same getter OUTSIDE
        # its except clause, so hasattr(dll, "interception_is_mouse")
        # PROPAGATED the AttributeError out of _find_mouse(). Result:
        # every code path through _abi1_names/_build_signatures/_find_mouse
        # died with an AttributeError; on this user's machine the probe
        # ran at startup inside the GUI thread and the exception escaped
        # into Tk's callback chain - process alive, window never drawn.
        # Fix: bind ALL exports ourselves from the real export table
        # (plain-name lookup via kernel32.GetProcAddressA, PE-table scan
        # as fallback), then setattr() them so ctypes' instance-attribute
        # fast path wins over the broken dynamic getter for every name,
        # required or optional. After this, hasattr/getattr/argtypes all
        # behave like a normal cdecl DLL object.
        if getattr(dll, "_icpt_bound", False):
            return True
        if not InterceptionBackend._abi1_names(dll):
            return False
        InterceptionBackend._install_plain_lookup(dll)
        try:
            dll._icpt_bound = True
        except Exception:
            pass
        return True

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
                # C build. kernel32.GetProcAddress is a MACRO - only
                # GetProcAddressA/W actually exist; bind A explicitly so
                # the lookup is byte-exact and never lands on a wrong
                # decoration. Then stdcall decorations, for nonstandard
                # rebuilds that used the MSVC /Gz default naming.
                try:
                    gpa = k32.GetProcAddressA
                    gpa.restype = ctypes.c_void_p
                    gpa.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
                except Exception:
                    gpa = None
                cands = []
                if gpa is not None:
                    cands.append(("A", nb))
                else:
                    cands.append(("W", nb))
                cands += [("n", b"%s@%d" % (nb, sz))
                          for sz in (4, 8, 12, 16, 20, 24)]
                for kind, cand in cands:
                    try:
                        if kind == "A":
                            addr = gpa(base, cand)
                        else:
                            addr = k32.GetProcAddress(base, cand)
                    except Exception:
                        addr = None
                    if addr:
                        found[n] = int(addr)
                        break
            # v8.54c: OPTIONAL exports are NOT probed here. The earlier
            # version of this block "collected" them by calling the very
            # GetProcAddress fallback we model ourselves against - which
            # fabricated hits for helpers that do not exist in official
            # DLLs (interception_first_device etc. then wrongly entered
            # the ABI-10 device walk and found nothing). Optional names
            # come exclusively from the real export table via the PE
            # scan below; absent helpers stay absent and _find_mouse
            # honestly takes the legacy fixed-range walk.
            if not all(n in found for n in
                       InterceptionBackend._REQUIRED_EXPORTS):
                # Second path: read the PE export table directly. Immune
                # to any runtime hooking of the loader APIs. It maps
                # EVERY interception_* name (required and optional), so
                # its result stands on its own.
                return InterceptionBackend._scan_export_table(dll)
            # v8.54c: ALSO run the PE-table scan and union its FULL map
            # (it names every interception_* export, including optional
            # helpers outside the probe lists). The scan may return False
            # merely because a REQUIRED name is absent from this build -
            # that is fine here; we only harvest its address map. Probe
            # addresses win any tie.
            dll._plain_exports = found       # plain name -> abs address
            dll._plain_image_base = base     # module load address
            # v8.54c: ALSO run the PE-table scan to harvest its FULL map
            # (every interception_* export, optional helpers included)
            # and the validated code span _install_plain_lookup requires
            # before binding anything. Its True/False verdict is ignored
            # here - we already proved the required set via the probe;
            # this call only enriches. Probe addresses win any tie.
            try:
                if InterceptionBackend._scan_export_table(dll):
                    merged = getattr(dll, "_plain_exports", {})
                    scan_map = merged  # scan stored its own map there
                else:
                    scan_map = getattr(dll, "_plain_exports", None) or {}
                keep_lo = getattr(dll, "_plain_code_lo", None)
                keep_hi = getattr(dll, "_plain_code_hi", None)
                keep_base = getattr(dll, "_plain_image_base", None)
                merged2 = dict(scan_map or {})
                merged2.update(found)
                dll._plain_exports = merged2
                if keep_lo is not None:
                    dll._plain_code_lo = keep_lo
                    dll._plain_code_hi = keep_hi
                    dll._plain_image_base = keep_base or base
            except Exception:
                pass
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
                # v8.54c: no hasattr() skip - on a WinDLL object hasattr
                # RAISES through its own except clause when only plain
                # names exist, and would otherwise mis-answer False even
                # for names we just need to bind. Re-setting the same
                # address is harmless; binding is what makes later
                # hasattr/getattr calls safe.
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
                # v8.54c: cast with CFUNCTYPE (cdecl), NOT WinDLL/stdcall.
                # The official DLL is plain C dllexport'd __stdcall? No -
                # MSVC x64 has ONE calling convention (Microsoft x64, which
                # ctypes' WINFUNCTYPE models); but x86 builds of this lib
                # are __stdcall while our decorated-name fallback covers
                # those separately. For PLAIN-name hits (x64 official DLL)
                # CFUNCTYPE(restype=c_void_p) with argtypes=None is the
                # safe universal form: no stack cleanup is claimed by the
                # wrapper, and every downstream .argtypes/.restype
                # assignment re-parameterises this very object.
                f = ctypes.cast(va, ctypes.CFUNCTYPE(ctypes.c_void_p))
                try:
                    f.argtypes = None
                except Exception:
                    pass
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
            # v8.54c: bind ALL exports (required + optional) via
            # _bind_all_exports before accepting the DLL. The old form
            # trusted ctypes' own lookup, which cannot see plain-name
            # exports on a WinDLL object at all.
            if cls._bind_all_exports(dll):
                cls._loaded_path = p if d else "(PATH search)"
                return dll
            if cls._has_exports(dll) and cls._bind_all_exports(dll):
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
                # v8.54c: run the blocking driver probe on a helper
                # thread with a hard timeout. If the kernel driver ever
                # wedges interception_wait_with_timeout, the GUI must
                # still paint - a hung main thread used to leave the
                # process running with no window at all.
                import queue as _q
                box = _q.Queue()
                def _probe():
                    try:
                        box.put(cls._probe_driver(dll))
                    except Exception:
                        box.put(False)
                t = threading.Thread(target=_probe, daemon=True)
                t.start()
                try:
                    ok = bool(box.get(timeout=3.0))
                except Exception:
                    ok = False       # probe hung or died: treat as absent
        except Exception:
            ok = False
        cls._avail_cache = ok
        return ok

    @classmethod
    def _probe_driver(cls, dll):
        # v8.54c: blocking driver liveness probe - runs ONLY on the
        # helper thread inside available(), never on the GUI thread.
        ok = False
        try:
            dll.interception_create_context.restype = ctypes.c_void_p
            ctx = dll.interception_create_context()
            if ctx:
                dll.interception_destroy_context.argtypes = \
                    [ctypes.c_void_p]
                # Probe driver liveness WITHOUT requiring any device
                # input: a short blocking wait wakes idle devices too.
                # (iterate() is an ABI-10 helper absent from official
                # release DLLs, so it can't be used here.)
                dll.interception_wait_with_timeout.restype = ctypes.c_int
                dll.interception_wait_with_timeout.argtypes = \
                    [ctypes.c_void_p, ctypes.c_double]
                try:
                    # Any return >= 0 means the driver answered; the
                    # call only fails outright if no driver is there.
                    dll.interception_wait_with_timeout(ctx, 0.15)
                    ok = True
                except Exception:
                    ok = False
                dll.interception_destroy_context(ctx)
        except Exception:
            return False
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
