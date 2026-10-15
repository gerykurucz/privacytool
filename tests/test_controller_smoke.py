import os, sys, tempfile, time, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from lattool_controller import EventType, GuiController


class TestControllerSmoke(unittest.TestCase):
    """Drives the real GuiController headlessly on the fake backend through
    every workflow the GUI exposes, consuming its event stream exactly like
    SnappyAIApp.pump_once does."""

    def setUp(self):
        self.out = tempfile.mkdtemp()
        self.ctl = GuiController(backend_name="fake", out_root=self.out,
                                 brand="SnappyAI")
        self.events = []
        self._pending = []
        import input_utils
        import measurement_utils
        self._real_measure_input = input_utils.measure_input
        self._real_measure_present = measurement_utils.measure_present
        input_utils.measure_input = lambda **kw: {
            "ok": True, "error": "", "rtts_ms": [1.0],
            "one_way_ms": [0.5], "p50_one_way_ms": 0.5, "n": 1,
        }
        measurement_utils.measure_present = lambda **kw: {
            "ok": True, "error": "", "p95_ms": 2.0, "n": 1,
        }
        self.addCleanup(self._restore_chain_legs)
        import general_utils
        import lattool_controller as lc
        self._real_run_ps1 = lc.run_ps1
        self.ran_scripts = []

        def _stub_run_ps1(script, args=(), timeout=900.0, elevate=False,
                          log_path=None):
            from pathlib import Path as _P
            self.ran_scripts.append(str(script))
            if _P(script).name == "apply.ps1":
                _P(script).parent.joinpath("snapshot.json").write_text(
                    '{"stub": true}', encoding="utf-8")
            return general_utils.RunResult(code=0, output="stubbed")

        lc.run_ps1 = _stub_run_ps1
        self.addCleanup(self._restore_run_ps1)

    def _restore_chain_legs(self):
        import input_utils
        import measurement_utils
        input_utils.measure_input = self._real_measure_input
        measurement_utils.measure_present = self._real_measure_present

    def _restore_run_ps1(self):
        import lattool_controller as lc
        lc.run_ps1 = self._real_run_ps1

    def drain(self, want, timeout=30.0):
        """Consume the stream like pump_once does — batch-safe: events
        polled in the same batch as `want` are kept for later drains."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            self._pending.extend(self.ctl.poll())
            while self._pending:
                ev = self._pending.pop(0)
                self.events.append(ev)
                if ev.kind is EventType.ERROR and want is not EventType.ERROR:
                    raise AssertionError(
                        "ERROR while waiting for %s: %s"
                        % (want, ev.message))
                if ev.kind is want:
                    return ev
            time.sleep(0.02)
        kinds = [e.kind.value for e in self.events]
        raise AssertionError("timeout waiting for %s; events: %s"
                             % (want, kinds[-12:]))

    def kinds_since(self, mark):
        return [e.kind for e in self.events[mark:]]

    def test_full_workflow(self):
        # --- scan (the flow that crashed on the user's PC) ---
        mark = len(self.events)
        self.assertTrue(self.ctl.start_scan(experimental=False,
                                            with_maintenance=True,
                                            min_confidence="low"))
        ev = self.drain(EventType.SCAN_DONE)
        self.assertIn(EventType.INVENTORY, self.kinds_since(mark))
        self.assertIn(EventType.BUSY, self.kinds_since(mark))
        self.drain(EventType.IDLE)          # emitted in the task's finally
        plan = os.path.join(self.out, "plan")
        for fname in ("apply.ps1", "undo.ps1", "manifest.json",
                      "report.md", "report.html", "maintenance.ps1"):
            self.assertTrue(os.path.exists(os.path.join(plan, fname)),
                            fname + " missing")
        scan = self.ctl.last_scan
        self.assertTrue(scan.outcomes)
        self.assertEqual(sum(scan.counts.values()), len(scan.outcomes))
        self.assertEqual(scan.inventory.os_name, "Microsoft Windows 11 Pro")

        # --- apply / undo wiring (script execution is stubbed hermetic
        #     above: no PowerShell, no UAC, on any OS; the stub writes the
        #     snapshot a real apply would leave, so undo must PROCEED) ---
        self.assertTrue(self.ctl.start_apply())
        ev = self.drain(EventType.APPLY_DONE)
        self.assertTrue(ev.data["script"].endswith("apply.ps1"))
        self.assertTrue(self.ctl.start_undo())
        self.drain(EventType.UNDO_DONE)

    def test_undo_refuses_without_snapshot(self):
        # The guard contract, directly: undo.ps1 present but nothing was
        # ever applied, so undo must REFUSE rather than restore nothing.
        import pathlib
        plan = pathlib.Path(self.out) / "empty_plan"
        plan.mkdir(parents=True, exist_ok=True)
        plan.joinpath("undo.ps1").write_text("Write-Host x\n",
                                             encoding="utf-8")
        self.assertFalse(self.ctl.start_undo(plan_dir=plan))
        ev = self.drain(EventType.ERROR)
        self.assertIn("snapshot.json", ev.message)

        # --- generate every maintenance kind ---
        for kind, fname in (("cleanup", "clean.ps1"), ("redists", "redists.ps1"),
                            ("memory", "memory.ps1"), ("power", "power.ps1"),
                            ("debloat", "debloat.ps1")):
            self.assertTrue(self.ctl.start_generate(kind=kind), kind)
            self.drain(EventType.SCRIPT_DONE)
            self.assertTrue(
                os.path.exists(os.path.join(self.out, kind, fname)),
                "%s/%s missing" % (kind, fname))

        # --- memory clean (fake powershell answers "{}") ---
        self.assertTrue(self.ctl.start_memory_clean())
        self.drain(EventType.MEMORY_CLEAN_DONE)

        # --- monitor: starts, ticks, stops ---
        self.assertTrue(self.ctl.start_monitor("127.0.0.1", interval=0.2,
                                               transport="tcp", port=9))
        self.drain(EventType.MONITOR_TICK, timeout=15.0)
        self.assertTrue(self.ctl.monitoring)
        self.ctl.stop_monitor()
        self.assertFalse(self.ctl.monitoring)

        # --- measure + baseline save ---
        mpath = os.path.join(self.out, "m.json")
        self.assertTrue(self.ctl.start_measure(
            target="127.0.0.1", samples=2, interval=0.05, transport="tcp",
            port=9, save_path=mpath))
        ev = self.drain(EventType.MEASURE_DONE, timeout=30.0)
        self.assertTrue(os.path.exists(mpath))

        # --- diagnose bundle ---
        dout = os.path.join(self.out, "diag")
        self.assertTrue(self.ctl.start_diagnose(out_dir=dout))
        ev = self.drain(EventType.SCRIPT_DONE, timeout=60.0)
        self.assertTrue(os.path.exists(ev.data["path"]))
        self.assertTrue(os.path.exists(ev.data["json"]))


    def test_chain_honours_time_budget(self):
        import time as _t
        mpath = os.path.join(self.out, "chain_budget.json")
        t0 = _t.monotonic()
        self.assertTrue(self.ctl.start_chain(
            target="127.0.0.1", save_path=mpath, budget_s=2.0))
        ev = self.drain(EventType.CHAIN_DONE, timeout=30.0)
        elapsed = _t.monotonic() - t0
        # input+render legs are stubbed hermetic above; the network leg must
        # fill the budget, so the run lands just above it - never far below
        self.assertGreaterEqual(elapsed, 1.75)
        self.assertLess(elapsed, 15.0)
        self.assertGreaterEqual(ev.data["duration_s"], 1.75)
        self.assertTrue(os.path.exists(mpath))
        # no watch running -> the chain probed by itself
        self.assertEqual(ev.data["network"].get("source"), "chain-probe")

    def test_chain_consumes_the_live_watch(self):
        """ONE network measurement: with a watch running on the same target,
        the chain's network leg must report the watch's samples instead of
        pinging in parallel."""
        self.assertTrue(self.ctl.start_monitor("127.0.0.1", interval=0.1,
                                               transport="tcp", port=9))
        self.drain(EventType.MONITOR_TICK, timeout=15.0)
        snap = self.ctl.monitor_samples("127.0.0.1")
        self.assertIsNotNone(snap)
        self.assertGreater(snap["sent"], 0)
        self.assertIsNone(self.ctl.monitor_samples("8.8.8.8"))  # target-scoped
        t0 = time.monotonic()
        self.assertTrue(self.ctl.start_chain(target="127.0.0.1", budget_s=2.0))
        ev = self.drain(EventType.CHAIN_DONE, timeout=30.0)
        self.assertGreaterEqual(time.monotonic() - t0, 1.75)
        net = ev.data["network"]
        self.assertEqual(net.get("source"), "live-watch")
        self.assertGreaterEqual(net.get("sent", 0), snap["sent"])
        self.ctl.stop_monitor()

    def tearDown(self):
        try:
            self.ctl.stop_monitor()
        except Exception:
            pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
