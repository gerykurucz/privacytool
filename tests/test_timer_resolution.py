"""Timer-resolution feature tests.

Covers the four pieces added this round: the cross-platform runtime logic
(clamp, resident-command encoding), the Windows ctypes path (stubbed, since CI
is Linux), the scanner probe/plan for the 0.5 ms tweak, and the experimental
GlobalTimerResolutionRequests tweak.
"""
import base64
import ctypes
import os
import sys
import threading
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


# --------------------------------------------------------------------------
# ctypes stubs: let the Windows-only branches of system_core run on Linux.
# --------------------------------------------------------------------------
class _Fn:
    """Callable attribute that also accepts .argtypes/.restype assignment."""

    def __init__(self, fn):
        self._fn = fn
        self.argtypes = None
        self.restype = None

    def __call__(self, *a, **k):
        return self._fn(*a, **k)


class _Ref:
    """Stand-in for ctypes.byref that the fakes can write through and read."""

    def __init__(self, obj):
        object.__setattr__(self, "_obj", obj)

    def __getattr__(self, item):
        return getattr(object.__getattribute__(self, "_obj"), item)


def _as_int(v):
    if isinstance(v, ctypes.c_void_p):
        return v.value
    return v


class _FakeNtdll:
    _snappy_timer_typed = False

    def __init__(self, lo=5000, hi=156250, cur=156250, set_status=0,
                 query_status=0):
        self.lo, self.hi, self.cur = lo, hi, cur
        self.set_status = set_status
        self.query_status = query_status
        self.sets = []
        self.NtQueryTimerResolution = _Fn(self._query)
        self.NtSetTimerResolution = _Fn(self._set)

    def _query(self, lo, hi, cur):
        if self.query_status:
            return self.query_status
        lo._obj.value = self.lo
        hi._obj.value = self.hi
        cur._obj.value = self.cur
        return 0

    def _set(self, units, enable, cur):
        self.sets.append((units, enable))
        cur._obj.value = min(units, self.hi)
        return self.set_status


class _FakeKernel32:
    def __init__(self, ok=True, missing=False):
        self.ok = ok
        self.calls = []
        if not missing:
            self.SetProcessInformation = _Fn(self._spi)

    def _spi(self, hproc, cls, buf, size):
        self.calls.append((cls, size, buf.ControlMask, buf.StateMask,
                           buf.Version, _as_int(hproc)))
        return 1 if self.ok else 0


class _StubbedWindows:
    """Context manager: swap in fake ntdll/kernel32 + byref, force IS_WINDOWS."""

    def __init__(self, sc, ntdll, kernel32):
        self.sc = sc
        self.ntdll = ntdll
        self.kernel32 = kernel32

    def __enter__(self):
        self._was_win = self.sc.IS_WINDOWS
        self._byref = ctypes.byref
        self._windll = getattr(ctypes, "windll", None)
        self._WinDLL = getattr(ctypes, "WinDLL", None)
        self.sc.IS_WINDOWS = True
        ctypes.byref = lambda obj, offset=0: _Ref(obj)
        ctypes.windll = type("W", (), {"ntdll": self.ntdll})()
        real = self._WinDLL

        def fake_windll(name, **kw):
            if str(name).lower().startswith("kernel32"):
                return self.kernel32
            if real is None:
                raise OSError("WinDLL unavailable")
            return real(name, **kw)

        ctypes.WinDLL = fake_windll
        return self

    def __exit__(self, *exc):
        self.sc.IS_WINDOWS = self._was_win
        ctypes.byref = self._byref
        if self._windll is None:
            del ctypes.windll
        else:
            ctypes.windll = self._windll
        if self._WinDLL is None:
            if hasattr(ctypes, "WinDLL"):
                del ctypes.WinDLL
        else:
            ctypes.WinDLL = self._WinDLL
        self.sc.stop_timer_request()
        return False


class TestClampTimerTarget(unittest.TestCase):
    def setUp(self):
        import system_core as sc
        self.sc = sc

    def test_half_ms_on_a_half_ms_platform(self):
        R = self.sc.TimerResolution(min_us=500.0, max_us=15625.0, current_us=15625.0)
        self.assertEqual(self.sc.clamp_timer_target(500.0, R), 5000)

    def test_clamped_up_to_the_platform_floor(self):
        R = self.sc.TimerResolution(min_us=1000.0, max_us=15625.0, current_us=15625.0)
        self.assertEqual(self.sc.clamp_timer_target(500.0, R), 10000)

    def test_absurdly_fine_request_clamps_to_floor(self):
        R = self.sc.TimerResolution(min_us=500.0, max_us=15625.0, current_us=15625.0)
        self.assertEqual(self.sc.clamp_timer_target(100.0, R), 5000)

    def test_coarse_request_clamps_to_ceiling(self):
        R = self.sc.TimerResolution(min_us=500.0, max_us=15625.0, current_us=15625.0)
        self.assertEqual(self.sc.clamp_timer_target(99999.0, R), 156250)

    def test_midscale_request_passes_through(self):
        R = self.sc.TimerResolution(min_us=500.0, max_us=15625.0, current_us=15625.0)
        self.assertEqual(self.sc.clamp_timer_target(2000.0, R), 20000)

    def test_nonpositive_uses_the_default_target(self):
        R = self.sc.TimerResolution(min_us=None, max_us=None, current_us=None)
        self.assertEqual(self.sc.clamp_timer_target(0, R), 5000)

    def test_unknown_bounds_use_the_default_target(self):
        R = self.sc.TimerResolution(min_us=None, max_us=None, current_us=None)
        self.assertEqual(self.sc.clamp_timer_target(500.0, R), 5000)


class TestRuntimeWindowsPath(unittest.TestCase):
    """The Windows ctypes branches, driven through stubbed ntdll/kernel32."""

    def setUp(self):
        import system_core as sc
        self.sc = sc
        sc.stop_timer_request()

    def tearDown(self):
        self.sc.IS_WINDOWS = False
        self.sc.stop_timer_request()

    def test_request_holds_a_resident_thread_and_reports_actual(self):
        k32 = _FakeKernel32()
        with _StubbedWindows(self.sc, _FakeNtdll(), k32):
            out = self.sc.request_timer_resolution(500.0)
            self.assertTrue(out["ok"])
            self.assertEqual(out["actual_us"], 500.0)
            self.assertEqual(out["requested_us"], 500.0)
            self.assertFalse(out["clamped"])
            self.assertTrue(self.sc.timer_request_active())
            holders = [t for t in threading.enumerate()
                       if t.name == "timer-resolution-holder"]
            self.assertEqual(len(holders), 1)

    def test_throttling_optout_uses_the_correct_struct_and_pseudo_handle(self):
        k32 = _FakeKernel32()
        with _StubbedWindows(self.sc, _FakeNtdll(), k32):
            out = self.sc.request_timer_resolution(500.0)
            self.assertEqual(
                out["throttling"], {"attempted": True, "ok": True, "error": ""})
            cls, size, ctlmask, statemask, version, hproc = k32.calls[0]
            w = ctypes.sizeof(ctypes.c_ulong)
            self.assertEqual(cls, 4)                 # ProcessPowerThrottling
            self.assertEqual(size, 3 * w)            # 3 ULONGs, no padding
            self.assertEqual(version, 1)             # CURRENT_VERSION
            self.assertEqual(ctlmask, 0x4)           # IGNORE_TIMER_RESOLUTION
            self.assertEqual(statemask, 0)           # 0 == always honour
            self.assertEqual(hproc, ctypes.c_void_p(-1).value)

    def test_ntsettimerresolution_gets_a_one_byte_boolean(self):
        nd = _FakeNtdll()
        with _StubbedWindows(self.sc, nd, _FakeKernel32()):
            self.sc.request_timer_resolution(500.0)
            units, enable = nd.sets[0]
            self.assertEqual(units, 5000)
            self.assertEqual(enable, 1)
            self.assertIsInstance(enable, int)
            self.assertNotIsInstance(enable, bool)

    def test_second_request_does_not_stack_a_second_holder(self):
        with _StubbedWindows(self.sc, _FakeNtdll(), _FakeKernel32()):
            self.sc.request_timer_resolution(500.0)
            again = self.sc.request_timer_resolution(900.0)
            self.assertTrue(again.get("already_active"))
            holders = [t for t in threading.enumerate()
                       if t.name == "timer-resolution-holder"]
            self.assertEqual(len(holders), 1)

    def test_stop_releases_the_holder(self):
        with _StubbedWindows(self.sc, _FakeNtdll(), _FakeKernel32()):
            self.sc.request_timer_resolution(500.0)
            stopped = self.sc.stop_timer_request()
            self.assertTrue(stopped["ok"])
            self.assertTrue(stopped["was_active"])
            self.assertFalse(self.sc.timer_request_active())
            holders = [t for t in threading.enumerate()
                       if t.name == "timer-resolution-holder"]
            self.assertEqual(len(holders), 0)

    def test_stop_when_inactive_is_a_clean_noop(self):
        with _StubbedWindows(self.sc, _FakeNtdll(), _FakeKernel32()):
            stopped = self.sc.stop_timer_request()
            self.assertFalse(stopped["ok"])
            self.assertFalse(stopped["was_active"])

    def test_request_clamps_to_a_coarser_platform_floor(self):
        with _StubbedWindows(self.sc, _FakeNtdll(lo=10000), _FakeKernel32()):
            out = self.sc.request_timer_resolution(500.0)
            self.assertTrue(out["ok"])
            self.assertEqual(out["requested_us"], 1000.0)
            self.assertTrue(out["clamped"])
            self.assertEqual(out["actual_us"], 1000.0)

    def test_ntset_failure_reports_status_and_leaves_no_holder(self):
        with _StubbedWindows(self.sc, _FakeNtdll(set_status=-1073741811),
                             _FakeKernel32()):
            out = self.sc.request_timer_resolution(500.0)
            self.assertFalse(out["ok"])
            self.assertIn("0xC000000D", out["error"])
            self.assertFalse(self.sc.timer_request_active())

    def test_throttling_refused_still_sets_the_resolution(self):
        with _StubbedWindows(self.sc, _FakeNtdll(), _FakeKernel32(ok=False)):
            out = self.sc.request_timer_resolution(500.0)
            self.assertTrue(out["ok"])
            self.assertTrue(out["throttling"]["attempted"])
            self.assertFalse(out["throttling"]["ok"])

    def test_setprocessinformation_absent_degrades_gracefully(self):
        with _StubbedWindows(self.sc, _FakeNtdll(),
                             _FakeKernel32(missing=True)):
            out = self.sc.request_timer_resolution(500.0)
            self.assertTrue(out["ok"])
            self.assertFalse(out["throttling"]["attempted"])
            self.assertIn("unavailable", out["throttling"]["error"])

    def test_optout_can_be_skipped_by_the_caller(self):
        nd = _FakeNtdll()
        k32 = _FakeKernel32()
        with _StubbedWindows(self.sc, nd, k32):
            out = self.sc.request_timer_resolution(
                500.0, power_throttling_optout=False)
            self.assertTrue(out["ok"])
            self.assertEqual(out["throttling"]["error"], "skipped")
            self.assertEqual(k32.calls, [])

    def test_query_failure_still_allows_an_unclamped_request(self):
        with _StubbedWindows(self.sc, _FakeNtdll(query_status=-1073741811),
                             _FakeKernel32()):
            self.assertEqual(self.sc.query_timer_resolution().current_us, None)
            out = self.sc.request_timer_resolution(500.0)
            self.assertTrue(out["ok"])
            self.assertEqual(out["requested_us"], 500.0)


class TestRuntimeNonWindows(unittest.TestCase):
    def setUp(self):
        import system_core as sc
        self.sc = sc
        self._was = sc.IS_WINDOWS
        sc.IS_WINDOWS = False

    def tearDown(self):
        self.sc.IS_WINDOWS = self._was

    def test_request_is_refused_off_windows(self):
        out = self.sc.request_timer_resolution(500.0)
        self.assertFalse(out["ok"])
        self.assertFalse(out["supported"])

    def test_query_returns_empty_off_windows(self):
        r = self.sc.query_timer_resolution()
        self.assertIsNone(r.current_us)
        self.assertIsNone(r.min_us)
        self.assertIsNone(r.max_us)

    def test_active_is_false_off_windows(self):
        self.assertFalse(self.sc.timer_request_active())


class TestResidentCommand(unittest.TestCase):
    def setUp(self):
        import maintenance_utils as m
        self.m = m

    def test_encodes_to_utf16_and_decodes_back(self):
        cmd = self.m.resident_timer_command(5000)
        self.assertTrue(cmd.startswith(
            "powershell -NoProfile -WindowStyle Hidden -EncodedCommand "))
        b64 = cmd.rsplit(" ", 1)[-1]
        body = base64.b64decode(b64).decode("utf-16-le")
        self.assertIn("NtSetTimerResolution", body)
        self.assertIn("$want = 5000", body)

    def test_body_carries_the_throttling_optout_and_hold_loop(self):
        body = base64.b64decode(
            self.m.resident_timer_command(5000).rsplit(" ", 1)[-1]
        ).decode("utf-16-le")
        self.assertIn("$t.ControlMask = 4", body)
        self.assertIn("$t.StateMask = 0", body)
        self.assertIn("while ($true)", body)

    def test_boolean_param_is_a_byte_not_a_bool(self):
        body = base64.b64decode(
            self.m.resident_timer_command(5000).rsplit(" ", 1)[-1]
        ).decode("utf-16-le")
        self.assertIn(
            "NtSetTimerResolution(int Desired, byte Set, ref int Current)", body)
        self.assertNotIn(
            "NtSetTimerResolution(int Desired, bool Set", body)
        self.assertIn("[byte]1", body)

    def test_body_clamps_to_the_queried_floor(self):
        body = base64.b64decode(
            self.m.resident_timer_command(5000).rsplit(" ", 1)[-1]
        ).decode("utf-16-le")
        self.assertIn("NtQueryTimerResolution", body)
        self.assertIn("if ($lo -gt 0 -and $want -lt $lo)", body)

    def test_embeds_the_requested_units(self):
        for units in (5000, 10000, 15625):
            body = base64.b64decode(
                self.m.resident_timer_command(units).rsplit(" ", 1)[-1]
            ).decode("utf-16-le")
            self.assertIn(f"$want = {units}", body)

    def test_out_of_range_units_are_rejected(self):
        for bad in (0, -1, 50, 999999):
            with self.assertRaises(ValueError):
                self.m.resident_timer_command(bad)


def _inv(**timer_kwargs):
    from system_core import Inventory, OSFamily, Timer
    build = timer_kwargs.pop("windows_build", 26200)
    return Inventory(
        os_family=OSFamily.WINDOWS, windows_build=build,
        timer=Timer(**timer_kwargs),
    )


class TestTimerProbe(unittest.TestCase):
    def setUp(self):
        import maintenance_utils as m
        self.m = m
        from system_core import Verdict
        self.V = Verdict

    def test_unreadable_tick_is_unknown(self):
        f = self.m._timer_probe(_inv(current_period_us=None))
        self.assertIs(f.verdict, self.V.UNKNOWN)

    def test_coarse_tick_on_a_fine_platform_is_a_problem(self):
        f = self.m._timer_probe(
            _inv(current_period_us=15600.0, min_period_us=500.0,
                 max_period_us=15625.0))
        self.assertIs(f.verdict, self.V.PROBLEM)
        self.assertEqual(f.measured["tick_us"], 15600.0)
        self.assertEqual(f.measured["finest_us"], 500.0)

    def test_mildly_coarse_tick_is_still_a_problem_when_finer_is_possible(self):
        f = self.m._timer_probe(
            _inv(current_period_us=1000.0, min_period_us=500.0,
                 max_period_us=15625.0))
        self.assertIs(f.verdict, self.V.PROBLEM)

    def test_already_at_the_floor_is_no_problem(self):
        f = self.m._timer_probe(
            _inv(current_period_us=500.0, min_period_us=500.0,
                 max_period_us=15625.0))
        self.assertIs(f.verdict, self.V.NO_PROBLEM)

    def test_platform_that_cannot_reach_half_ms_is_no_problem(self):
        f = self.m._timer_probe(
            _inv(current_period_us=15600.0, min_period_us=1000.0,
                 max_period_us=15625.0))
        self.assertIs(f.verdict, self.V.NO_PROBLEM)
        self.assertIn("not reachable", f.summary)

    def test_missing_floor_is_unknown(self):
        f = self.m._timer_probe(
            _inv(current_period_us=1000.0, min_period_us=None))
        self.assertIs(f.verdict, self.V.UNKNOWN)

    def test_probe_reports_the_gtrr_state(self):
        f = self.m._timer_probe(
            _inv(current_period_us=15600.0, min_period_us=500.0,
                 max_period_us=15625.0, global_timer_resolution_requests=1))
        self.assertEqual(f.measured["global_timer_requests"], 1)


class TestTimerPlan(unittest.TestCase):
    def setUp(self):
        import maintenance_utils as m
        self.m = m

    def test_plan_emits_an_automated_powershell_step(self):
        from models import StepKind
        inv = _inv(current_period_us=15600.0, min_period_us=500.0)
        steps = self.m._timer_plan(inv)
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0].kind, StepKind.POWERSHELL)
        self.assertFalse(steps[0].is_manual)

    def test_plan_writes_the_run_key_and_starts_the_helper(self):
        inv = _inv(current_period_us=15600.0, min_period_us=500.0)
        step = self.m._timer_plan(inv)[0]
        self.assertIn("CurrentVersion\\Run", step.command)
        self.assertIn("SnappyAI Timer Resolution", step.command)
        self.assertIn("Start-Process powershell", step.command)
        self.assertIn("-EncodedCommand", step.command)

    def test_plan_targets_the_platform_floor(self):
        inv = _inv(current_period_us=15600.0, min_period_us=500.0)
        step = self.m._timer_plan(inv)[0]
        b64 = step.command.rsplit("'", 2)[-2]
        body = base64.b64decode(b64).decode("utf-16-le")
        self.assertIn("$want = 5000", body)

    def test_plan_clamps_to_a_coarser_floor(self):
        inv = _inv(current_period_us=15600.0, min_period_us=1000.0)
        step = self.m._timer_plan(inv)[0]
        b64 = step.command.rsplit("'", 2)[-2]
        body = base64.b64decode(b64).decode("utf-16-le")
        self.assertIn("$want = 10000", body)

    def test_undo_kills_the_helper_and_removes_the_run_key(self):
        inv = _inv(current_period_us=15600.0, min_period_us=500.0)
        step = self.m._timer_plan(inv)[0]
        self.assertTrue(step.undo)
        undo = step.undo[0].command
        self.assertIn("Stop-Process", undo)
        self.assertIn("Remove-ItemProperty", undo)
        self.assertIn("SnappyAI Timer Resolution", undo)

    def test_undo_matches_the_helper_by_its_encoded_payload(self):
        """The resident helper's CommandLine resolves to a full quoted exe
        path, so matching on the Run-key string with -eq would miss it. The
        undo must match on the unique base64 payload instead."""
        import re
        inv = _inv(current_period_us=15600.0, min_period_us=500.0)
        step = self.m._timer_plan(inv)[0]
        undo = step.undo[0].command
        apply_cmd = step.command
        m = re.search(r"-EncodedCommand','([A-Za-z0-9+/=]+)'", apply_cmd)
        self.assertIsNotNone(m, "could not find the encoded payload in apply")
        encoded = m.group(1)
        self.assertIn(f"-like '*{encoded}*'", undo)
        self.assertNotIn("-eq $c", undo)
        self.assertIn("Get-CimInstance Win32_Process", undo)

    def test_step_passes_model_validation(self):
        inv = _inv(current_period_us=15600.0, min_period_us=500.0)
        step = self.m._timer_plan(inv)[0]
        self.assertTrue(step.reversible)


class TestGtrrTweak(unittest.TestCase):
    def setUp(self):
        import maintenance_utils as m
        self.m = m
        from system_core import Verdict
        self.V = Verdict

    def test_registered_as_high_risk_experimental(self):
        t = self.m._TWEAK_BY_ID["timer.global_requests.experimental"]
        self.assertTrue(t.experimental)
        from system_core import Risk
        self.assertIs(t.risk, Risk.HIGH)
        self.assertTrue(t.requires_reboot)
        self.assertTrue(t.caveats)

    def test_probe_not_applicable_on_old_windows(self):
        f = self.m._gtrr_probe(_inv(windows_build=19045))
        self.assertIs(f.verdict, self.V.NOT_APPLICABLE)

    def test_probe_no_problem_when_already_enabled(self):
        f = self.m._gtrr_probe(
            _inv(windows_build=26200, global_timer_resolution_requests=1))
        self.assertIs(f.verdict, self.V.NO_PROBLEM)

    def test_probe_unknown_when_off_on_modern_windows(self):
        f = self.m._gtrr_probe(
            _inv(windows_build=26200, global_timer_resolution_requests=0))
        self.assertIs(f.verdict, self.V.UNKNOWN)

    def test_plan_sets_the_dword_under_session_manager_kernel(self):
        from models import StepKind
        steps = self.m._gtrr_plan(_inv(windows_build=26200))
        self.assertEqual(len(steps), 1)
        s = steps[0]
        self.assertEqual(s.kind, StepKind.REGISTRY_SET)
        self.assertEqual(s.hive, "HKLM")
        self.assertIn("Session Manager\\kernel", s.path)
        self.assertEqual(s.value_name, "GlobalTimerResolutionRequests")
        self.assertEqual(s.value, 1)

    def test_gtrr_is_not_in_the_default_applicable_set(self):
        ids = {t.id for t in self.m.applicable_tweaks()}
        self.assertNotIn("timer.global_requests.experimental", ids)
        ids_exp = {t.id for t in self.m.applicable_tweaks(include_experimental=True)}
        self.assertIn("timer.global_requests.experimental", ids_exp)


class TestControllerTimerWiring(unittest.TestCase):
    def setUp(self):
        from lattool_controller import EventType, GuiController
        self.EventType = EventType
        self.ctl = GuiController(backend_name="fake")

    def test_event_type_exists(self):
        self.assertEqual(self.EventType.TIMER_DONE.value, "timer_done")

    def test_controller_exposes_timer_api(self):
        for name in ("start_timer_request", "start_timer_stop",
                     "timer_status"):
            self.assertTrue(hasattr(self.ctl, name), name)
        self.assertIsInstance(self.ctl.timer_active, bool)

    def test_inventory_summary_carries_the_timer_floor(self):
        inv = _inv(current_period_us=15600.0, min_period_us=500.0,
                   max_period_us=15625.0)
        summary = self.ctl._inventory_summary(inv)
        self.assertEqual(summary["timer_floor_us"], 500.0)
        self.assertEqual(summary["timer_coarsest_us"], 15625.0)
        self.assertIn("global_timer_requests", summary)


class TestControllerTimerEvents(unittest.TestCase):
    """Drives the real controller headlessly and consumes its event stream.
    On this (non-Windows) host the request is refused, which is exactly the
    failure path that must still emit TIMER_DONE with an authoritative
    active=False rather than an ERROR that would leave the GUI stuck."""

    def setUp(self):
        import time
        from lattool_controller import EventType, GuiController
        self.time = time
        self.EventType = EventType
        self.ctl = GuiController(backend_name="fake")

    def _drain(self, want, timeout=10.0):
        deadline = self.time.time() + timeout
        seen = []
        while self.time.time() < deadline:
            for ev in self.ctl.poll():
                seen.append(ev)
                if ev.kind is want:
                    return ev, seen
            self.time.sleep(0.02)
        raise AssertionError(
            f"timeout waiting for {want}; got {[e.kind.value for e in seen]}")

    def test_refused_request_emits_timer_done_not_error(self):
        self.ctl.start_timer_request(500.0)
        ev, seen = self._drain(self.EventType.TIMER_DONE)
        self.assertNotIn(self.EventType.ERROR, [e.kind for e in seen])
        self.assertFalse(ev.data["active"])
        self.assertIn("error", ev.data)

    def test_stop_emits_timer_done_with_active_false(self):
        self.ctl.start_timer_stop()
        ev, _ = self._drain(self.EventType.TIMER_DONE)
        self.assertFalse(ev.data["active"])
        self.assertFalse(ev.data["was_active"])

    def test_busy_controller_refuses_a_second_operation(self):
        # First op occupies the controller; while RUNNING, a second start is
        # refused (returns False) so the GUI can revert its checkbox.
        self.ctl.state = __import__(
            "lattool_controller").TaskState.RUNNING
        self.assertFalse(self.ctl.start_timer_request(500.0))
        self.ctl.state = __import__("lattool_controller").TaskState.IDLE


class TestGUIToggleSync(unittest.TestCase):
    """Source-level checks for the checkbox-honesty fix: DarkCheck flips the
    var before the command runs, so the handlers must reconcile it with the
    authoritative controller state on both the busy-refusal and async-result
    paths."""

    def setUp(self):
        self.src = open(os.path.join(ROOT, "lattool_gui.py"),
                        encoding="utf-8").read()

    def test_toggle_reverts_the_checkbox_when_the_controller_is_busy(self):
        i = self.src.index("def on_timer_toggle")
        body = self.src[i:self.src.index("def _render_timer")]
        self.assertIn("started = self.ctl.start_timer_request", body)
        self.assertIn("started = self.ctl.start_timer_stop", body)
        self.assertIn("if not started:", body)
        self.assertIn("self.var_timer.set(self.ctl.timer_active)", body)

    def test_toggle_persists_only_after_a_successful_start(self):
        i = self.src.index("def on_timer_toggle")
        body = self.src[i:self.src.index("def _render_timer")]
        # persistence must come after the busy-guard return, not before
        guard = body.index("if not started:")
        persist = body.index("self._on_timer_persist(")
        self.assertGreater(persist, guard)

    def test_render_syncs_checkbox_to_authoritative_active_flag(self):
        i = self.src.index("def _render_timer")
        body = self.src[i:self.src.index("def on_gen_cleanup")]
        self.assertIn("self.var_timer.set(bool(d.get(\"active\")))", body)

    def test_timer_done_event_is_wired_to_render(self):
        self.assertIn("elif k is EventType.TIMER_DONE:", self.src)
        i = self.src.index("elif k is EventType.TIMER_DONE:")
        body = self.src[i:i + 160]
        self.assertIn("self._render_timer(ev.data or {})", body)

    def test_tools_tab_has_the_timer_toggle(self):
        self.assertIn('text="SYSTEM TIMER"', self.src)
        self.assertIn("self.var_timer = tk.BooleanVar(value=False)", self.src)
        self.assertIn("command=self.on_timer_toggle", self.src)


class TestMountStartupWiring(unittest.TestCase):
    def setUp(self):
        self.src = open(os.path.join(ROOT, "input_utils.py"),
                        encoding="utf-8").read()

    def test_mount_accepts_cfg_and_autostarts_from_config(self):
        i = self.src.index("def mount(")
        body = self.src[i:self.src.index("def pump(")]
        self.assertIn("cfg=None", body)
        self.assertIn('cfg.get("timer_resolution_us")', body)
        self.assertIn("app.var_timer.set(True)", body)
        self.assertIn("ctl.start_timer_request(float(startup_timer_us))", body)

    def test_mount_passes_a_persist_callback(self):
        i = self.src.index("def mount(")
        body = self.src[i:self.src.index("def pump(")]
        self.assertIn('cfg.set("timer_resolution_us"', body)
        self.assertIn('"on_timer_persist": on_timer_persist', body)

    def test_shutdown_releases_the_request(self):
        i = self.src.index("def shutdown(handle)")
        body = self.src[i:i + 320]
        self.assertIn("stop_timer_request()", body)

    def test_gui_passes_cfg_to_mount(self):
        gsrc = open(os.path.join(ROOT, "gui.py"), encoding="utf-8").read()
        i = gsrc.index("latency_tabs.mount(")
        call = gsrc[i:i + 320]
        self.assertIn("cfg=cfg", call)


class TestConfigKey(unittest.TestCase):
    def test_default_is_off(self):
        import config
        self.assertEqual(config.DEFAULT_CONFIG["timer_resolution_us"], 0)

    def test_range_clamps(self):
        import config
        self.assertIn("timer_resolution_us", config.Config._RANGES)
        lo, hi = config.Config._RANGES["timer_resolution_us"]
        self.assertEqual(lo, 0)
        self.assertGreaterEqual(hi, 500)

    def test_coercion(self):
        import config
        d = config.DEFAULT_CONFIG["timer_resolution_us"]
        self.assertEqual(config._coerce_value("500", d), (True, 500))
        self.assertEqual(config._coerce_value(500, d), (True, 500))
        self.assertEqual(config._coerce_value("abc", d), (False, None))


class TestShutdownReleases(unittest.TestCase):
    def test_shutdown_calls_stop_timer_request(self):
        import input_utils
        calls = []
        import system_core as sc
        orig = sc.stop_timer_request
        sc.stop_timer_request = lambda: calls.append("stop") or {"ok": True}
        try:
            class _Ctl:
                def stop_monitor(self):
                    calls.append("monitor")
            input_utils.shutdown({"ctl": _Ctl()})
        finally:
            sc.stop_timer_request = orig
        self.assertIn("stop", calls)


if __name__ == "__main__":
    unittest.main()
