import os, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


class _FakeFn(object):
    def __init__(self):
        self.restype = None
        self.argtypes = None


class _FakeDll(object):
    def __init__(self, path):
        self.path = path

    def __getattr__(self, name):
        return _FakeFn()


class _FakeCtypes(object):
    """Just enough of ctypes for the two DLL loaders to run headless."""

    c_ulong = "c_ulong"
    c_void_p = "c_void_p"
    c_int = "c_int"

    def __init__(self, fail=()):
        self.fail = tuple(fail)
        self.requested = []
        outer = self

        class _Windll(object):
            def LoadLibrary(self, path):
                outer.requested.append(path)
                if path in outer.fail:
                    raise OSError("simulated load failure: %s" % path)
                return _FakeDll(path)

        self.windll = _Windll()

    def POINTER(self, item):
        return ("PTR", item)


def _write(path, data=b"dll"):
    with open(path, "wb") as handle:
        handle.write(data)
    return path


class TestDllSearchPaths(unittest.TestCase):
    def test_absolute_paths_only_and_ordered(self):
        import general_utils
        with tempfile.TemporaryDirectory() as sysdir, \
                tempfile.TemporaryDirectory() as appdir:
            _write(os.path.join(sysdir, "xinput1_4.dll"))
            _write(os.path.join(appdir, "ViGEmClient.dll"))
            _write(os.path.join(appdir, "xinput1_4.dll"))
            real_sys, real_app = general_utils.system32_dir, general_utils.app_dir
            general_utils.system32_dir = lambda: sysdir
            general_utils.app_dir = lambda: appdir
            try:
                names = ("xinput1_4.dll", "xinput1_3.dll")
                found = general_utils.dll_search_paths(names, "system32")
                self.assertEqual(found, [os.path.join(sysdir, "xinput1_4.dll")])

                found = general_utils.dll_search_paths(names, "appdir")
                self.assertEqual(found, [os.path.join(appdir, "xinput1_4.dll")])

                found = general_utils.dll_search_paths(names, "both")
                self.assertEqual(found, [os.path.join(sysdir, "xinput1_4.dll"),
                                         os.path.join(appdir, "xinput1_4.dll")])

                for path in found:
                    self.assertTrue(os.path.isabs(path),
                                    "bare name would let the launch folder "
                                    "or PATH shadow the real DLL: %r" % path)

                self.assertEqual(general_utils.dll_search_paths(
                    ("missing.dll",), "both"), [])
            finally:
                general_utils.system32_dir = real_sys
                general_utils.app_dir = real_app

    def test_app_dir_follows_the_frozen_exe(self):
        import general_utils
        real = getattr(sys, "frozen", None)
        real_exe = sys.executable
        try:
            sys.frozen = True
            sys.executable = os.path.join(tempfile.gettempdir(),
                                          "dist", "SnappyAI.exe")
            self.assertEqual(general_utils.app_dir(),
                             os.path.join(tempfile.gettempdir(), "dist"))
        finally:
            if real is None:
                del sys.frozen
            else:
                sys.frozen = real
            sys.executable = real_exe


class TestDllPin(unittest.TestCase):
    def test_pin_is_opt_in_and_exact(self):
        import build_tools, general_utils
        with tempfile.TemporaryDirectory() as tmp:
            dll = _write(os.path.join(tmp, "ViGEmClient.dll"), b"payload")
            self.assertTrue(general_utils.dll_pin_ok(dll),
                            "no sidecar must stay loadable - users drop this "
                            "DLL in by hand")

            build_tools.pin_dll(dll)
            self.assertTrue(general_utils.dll_pin_ok(dll))

            _write(dll, b"tampered")
            self.assertFalse(general_utils.dll_pin_ok(dll))

            _write(dll + ".sha256", b"not a hash at all\n")
            self.assertFalse(general_utils.dll_pin_ok(dll))


class TestXInputLoader(unittest.TestCase):
    def _load(self, sysdir, appdir=None, fail=()):
        import general_utils, input_utils
        fake = _FakeCtypes(fail=fail)
        appdir = appdir or sysdir
        real = (input_utils.ctypes, input_utils.IS_WINDOWS,
                general_utils.system32_dir, general_utils.app_dir,
                input_utils._dll, input_utils._dll_tried)
        input_utils.ctypes = fake
        input_utils.IS_WINDOWS = True
        general_utils.system32_dir = lambda: sysdir
        general_utils.app_dir = lambda: appdir
        input_utils._dll = None
        input_utils._dll_tried = False
        try:
            dll = input_utils._load_dll()
        finally:
            (input_utils.ctypes, input_utils.IS_WINDOWS,
             general_utils.system32_dir, general_utils.app_dir,
             input_utils._dll, input_utils._dll_tried) = real
        return dll, fake.requested

    def test_loads_from_system32_by_absolute_path(self):
        with tempfile.TemporaryDirectory() as sysdir, \
                tempfile.TemporaryDirectory() as appdir:
            _write(os.path.join(sysdir, "xinput1_4.dll"))
            dll, requested = self._load(sysdir, appdir)
            self.assertIsNotNone(dll)
            self.assertEqual(requested, [os.path.join(sysdir,
                                                      "xinput1_4.dll")])

    def test_a_dll_beside_the_exe_is_still_used(self):
        with tempfile.TemporaryDirectory() as sysdir, \
                tempfile.TemporaryDirectory() as appdir:
            path = _write(os.path.join(appdir, "xinput1_3.dll"))
            dll, requested = self._load(sysdir, appdir)
            self.assertIsNotNone(dll)
            self.assertEqual(requested, [path])

    def test_the_system32_copy_wins_over_the_local_one(self):
        with tempfile.TemporaryDirectory() as sysdir, \
                tempfile.TemporaryDirectory() as appdir:
            _write(os.path.join(appdir, "xinput1_4.dll"))
            good = _write(os.path.join(sysdir, "xinput1_4.dll"))
            dll, requested = self._load(sysdir, appdir)
            self.assertEqual(requested, [good])

    def test_falls_through_to_the_next_xinput(self):
        with tempfile.TemporaryDirectory() as sysdir, \
                tempfile.TemporaryDirectory() as appdir:
            _write(os.path.join(sysdir, "xinput1_4.dll"))
            _write(os.path.join(sysdir, "xinput1_3.dll"))
            dll, requested = self._load(
                sysdir, appdir, fail=[os.path.join(sysdir, "xinput1_4.dll")])
            self.assertIsNotNone(dll)
            self.assertEqual(requested[-1], os.path.join(sysdir,
                                                         "xinput1_3.dll"))

    def test_no_xinput_returns_none_without_raising(self):
        with tempfile.TemporaryDirectory() as sysdir, \
                tempfile.TemporaryDirectory() as appdir:
            dll, requested = self._load(sysdir, appdir)
            self.assertIsNone(dll)
            self.assertEqual(requested, [])


class TestViGemLoader(unittest.TestCase):
    def _load(self, appdir, sysdir=None):
        import general_utils, input_backend
        fake = _FakeCtypes()
        sysdir = sysdir or appdir
        real = (input_backend.ctypes, input_backend.IS_WINDOWS,
                general_utils.app_dir, general_utils.system32_dir,
                input_backend._vigem_dll, input_backend._vigem_tried)
        input_backend.ctypes = fake
        input_backend.IS_WINDOWS = True
        general_utils.app_dir = lambda: appdir
        general_utils.system32_dir = lambda: sysdir
        input_backend._vigem_dll = None
        input_backend._vigem_tried = False
        try:
            dll = input_backend._load_vigem()
        finally:
            (input_backend.ctypes, input_backend.IS_WINDOWS,
             general_utils.app_dir, general_utils.system32_dir,
             input_backend._vigem_dll, input_backend._vigem_tried) = real
        return dll, fake.requested

    def test_unpinned_dll_still_loads_from_the_app_folder(self):
        with tempfile.TemporaryDirectory() as appdir, \
                tempfile.TemporaryDirectory() as sysdir:
            path = _write(os.path.join(appdir, "ViGEmClient.dll"))
            dll, requested = self._load(appdir, sysdir)
            self.assertIsNotNone(dll)
            self.assertEqual(requested, [path])

    def test_a_system32_install_is_still_found(self):
        with tempfile.TemporaryDirectory() as appdir, \
                tempfile.TemporaryDirectory() as sysdir:
            path = _write(os.path.join(sysdir, "ViGEmClient.dll"))
            dll, requested = self._load(appdir, sysdir)
            self.assertIsNotNone(dll)
            self.assertEqual(requested, [path])

    def test_dll_that_fails_its_pin_is_refused(self):
        import build_tools
        with tempfile.TemporaryDirectory() as appdir, \
                tempfile.TemporaryDirectory() as sysdir:
            path = _write(os.path.join(appdir, "ViGEmClient.dll"), b"real")
            build_tools.pin_dll(path)
            _write(path, b"planted")
            dll, requested = self._load(appdir, sysdir)
            self.assertIsNone(dll)
            self.assertEqual(requested, [],
                             "a DLL that fails its pin must never be mapped "
                             "into the process")

    def test_dll_that_matches_its_pin_loads(self):
        import build_tools
        with tempfile.TemporaryDirectory() as appdir, \
                tempfile.TemporaryDirectory() as sysdir:
            path = _write(os.path.join(appdir, "ViGEmClient.dll"), b"real")
            build_tools.pin_dll(path)
            dll, requested = self._load(appdir, sysdir)
            self.assertIsNotNone(dll)
            self.assertEqual(requested, [path])


class TestCallerVisibleBoundaries(unittest.TestCase):
    """The GUI and assist engine never call the private loaders directly."""

    def test_available_reports_the_system32_probe(self):
        import general_utils, input_utils
        fake = _FakeCtypes()
        real = (input_utils.ctypes, input_utils.IS_WINDOWS,
                general_utils.system32_dir, general_utils.app_dir,
                input_utils._dll, input_utils._dll_tried)
        with tempfile.TemporaryDirectory() as sysdir, \
                tempfile.TemporaryDirectory() as appdir:
            input_utils.ctypes = fake
            input_utils.IS_WINDOWS = True
            general_utils.system32_dir = lambda: sysdir
            general_utils.app_dir = lambda: appdir
            try:
                input_utils._dll, input_utils._dll_tried = None, False
                self.assertFalse(input_utils.available())

                _write(os.path.join(sysdir, "xinput1_4.dll"))
                input_utils._dll, input_utils._dll_tried = None, False
                self.assertTrue(input_utils.available())
            finally:
                (input_utils.ctypes, input_utils.IS_WINDOWS,
                 general_utils.system32_dir, general_utils.app_dir,
                 input_utils._dll, input_utils._dll_tried) = real

    def test_a_tampered_vigem_dll_degrades_to_emulation(self):
        import build_tools, general_utils, input_backend
        fake = _FakeCtypes()
        real = (input_backend.ctypes, input_backend.IS_WINDOWS,
                general_utils.app_dir, general_utils.system32_dir,
                input_backend._vigem_dll, input_backend._vigem_tried)
        with tempfile.TemporaryDirectory() as appdir, \
                tempfile.TemporaryDirectory() as sysdir:
            path = _write(os.path.join(appdir, "ViGEmClient.dll"), b"real")
            build_tools.pin_dll(path)
            _write(path, b"planted")
            input_backend.ctypes = fake
            input_backend.IS_WINDOWS = True
            general_utils.app_dir = lambda: appdir
            general_utils.system32_dir = lambda: sysdir
            input_backend._vigem_dll = None
            input_backend._vigem_tried = False
            try:
                backend = input_backend.make_pad_backend(None)
            finally:
                (input_backend.ctypes, input_backend.IS_WINDOWS,
                 general_utils.app_dir, general_utils.system32_dir,
                 input_backend._vigem_dll, input_backend._vigem_tried) = real
            self.assertIsInstance(backend, input_backend.EmulatedPadBackend)
            self.assertEqual(fake.requested, [])


class TestSecretScanner(unittest.TestCase):
    def test_scanner_decodes_exactly_what_the_app_decodes(self):
        import build_tools, general_utils
        key, blob = build_tools.read_secret_blob(ROOT)
        self.assertEqual(key, general_utils._KEY)
        decoded = build_tools.decode_blob(key, blob)
        self.assertTrue(decoded)
        for name in decoded:
            self.assertEqual(decoded[name], general_utils._decode(blob[name]),
                             "scanner and app disagree on %s" % name)

    def test_scan_flags_a_planted_secret_and_a_clean_file(self):
        import build_tools
        key, blob = build_tools.read_secret_blob(ROOT)
        decoded = build_tools.decode_blob(key, blob)
        target = next(v for k, v in sorted(decoded.items())
                      if k == "ENTITLEMENT_REPO")
        with tempfile.TemporaryDirectory() as tmp:
            dirty = os.path.join(tmp, "dirty.exe")
            with open(dirty, "wb") as handle:
                handle.write(b"\x00" * 32 + key + target.encode("utf-8"))
            self.assertEqual(build_tools.scan_binary(dirty, ROOT), 1)

            clean = os.path.join(tmp, "clean.exe")
            with open(clean, "wb") as handle:
                handle.write(b"\x00" * 64)
            self.assertEqual(build_tools.scan_binary(clean, ROOT), 0)

    def test_manifest_detects_a_swapped_file(self):
        import build_tools
        with tempfile.TemporaryDirectory() as tmp:
            _write(os.path.join(tmp, "SnappyAI.exe"), b"one")
            os.mkdir(os.path.join(tmp, "sub"))
            _write(os.path.join(tmp, "sub", "python3.dll"), b"two")
            build_tools.write_manifest(tmp)
            self.assertEqual(build_tools.verify_manifest(tmp), 0)

            _write(os.path.join(tmp, "sub", "python3.dll"), b"swapped")
            self.assertEqual(build_tools.verify_manifest(tmp), 1)

            os.remove(os.path.join(tmp, "SnappyAI.exe"))
            self.assertEqual(build_tools.verify_manifest(tmp), 1)

    def test_scan_output_is_safe_to_paste(self):
        import build_tools, io, contextlib
        key, blob = build_tools.read_secret_blob(ROOT)
        decoded = build_tools.decode_blob(key, blob)
        secret = decoded.get("DISCORD_CLIENT_SEC", "")
        if not secret:
            self.skipTest("no client secret in the blob")
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "SnappyAI.exe")
            with open(target, "wb") as handle:
                handle.write(key + secret.encode("utf-8"))
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                build_tools.scan_binary(target, ROOT)
            printed = buffer.getvalue()
            self.assertNotIn(secret, printed,
                             "the default report must not echo credentials")
            self.assertIn("RECOVERABLE", printed)
            self.assertIn("Release blockers", printed)


class TestBuildScript(unittest.TestCase):
    def test_hardening_flags_are_present_and_the_traps_are_not(self):
        path = os.path.join(ROOT, "build_nuitka.cmd")
        with open(path, "r", encoding="utf-8") as handle:
            text = handle.read()
        start = text.index("python -m nuitka ^")
        end = text.index("\n    main.py", start)
        command = text[start:end]
        for flag in ("--standalone", "--deployment", "no_asserts",
                     "no_docstrings", "no_warnings", "isolated", "safe_path",
                     "--enable-plugin=tk-inter", "--windows-console-mode=attach",
                     "--noinclude-pydoc-mode=nofollow",
                     "--noinclude-unittest-mode=nofollow",
                     "--noinclude-setuptools-mode=nofollow",
                     "--lto=%SNAPPYAI_LTO%"):
            self.assertIn(flag, command, "missing %s" % flag)
        for trap in ("static_hashes", "no_annotations", "windows-uac-admin",
                     "onefile"):
            self.assertNotIn(trap, command,
                             "%s must not be an active build flag" % trap)
        for step in ("build_tools.py manifest", "build_tools.py scan",
                     "build_tools.py sign", "build_tools.py pin"):
            self.assertIn(step, text)
        for note in ("windows-uac-admin", "static_hashes", "no_annotations",
                     "onefile"):
            self.assertIn(note, text,
                          "the reason for skipping %s must stay documented"
                          % note)

    def test_script_is_crlf_and_its_gotos_resolve(self):
        import re
        path = os.path.join(ROOT, "build_nuitka.cmd")
        raw = open(path, "rb").read()
        self.assertEqual(raw.count(b"\n"), raw.count(b"\r\n"),
                         "a .cmd with bare LF endings can misparse labels")
        labels, gotos = set(), []
        for line in raw.decode("utf-8").splitlines():
            match = re.match(r"^:([A-Za-z_]\w*)\s*$", line.strip())
            if match:
                labels.add(match.group(1).lower())
            gotos += [g.lower() for g in
                      re.findall(r"\bgoto\s+:?(\w+)", line, re.I)]
        self.assertEqual([g for g in gotos if g not in labels], [])


if __name__ == "__main__":
    unittest.main()
