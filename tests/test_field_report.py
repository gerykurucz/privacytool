import os, sys, unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


class TestPingParsing(unittest.TestCase):
    def test_locales(self):
        from measurement_utils import _parse_ping_ms
        cases = [
            ("Reply from 1.1.1.1: bytes=32 time=35ms TTL=54", 35.0),
            ("Reply from 1.1.1.1: bytes=32 time<1ms TTL=54", 1.0),
            ("Válasz ettől: 1.1.1.1: bájt=32 idő=35ms TTL=54", 35.0),
            ("Antwort von 8.8.8.8: Bytes=32 Zeit=12ms TTL=118", 12.0),
            ("64 bytes from 1.1.1.1: icmp_seq=1 ttl=54 time=0.045 ms", 0.045),
            ("Réponse de 1.1.1.1 : octets=32 temps=35,5 ms TTL=54", 35.5),
        ]
        for text, want in cases:
            self.assertEqual(_parse_ping_ms(text), want, text)

    def test_no_match_cases(self):
        from measurement_utils import _parse_ping_ms
        self.assertIsNone(_parse_ping_ms("Request timed out."))
        self.assertIsNone(_parse_ping_ms("A kérelem időtúllépés miatt lejárt."))
        self.assertIsNone(_parse_ping_ms(""))
        self.assertIsNone(_parse_ping_ms(None))
        # statistics lines alone must not produce a value with '=' + ms only
        # ... "Minimum = 35ms" DOES match by design (same value as reply),
        # but a pure loss summary must not:
        self.assertIsNone(_parse_ping_ms(
            "Packets: Sent = 1, Received = 0, Lost = 1 (100% loss)"))

    def test_ping_once_encoding_kwargs(self):
        import measurement_utils as mu

        class Proc:
            returncode = 0
            stdout = "Válasz ettől: 1.1.1.1: bájt=32 idő=35ms TTL=54"

        with mock.patch.object(mu.subprocess, "run",
                               return_value=Proc()) as m:
            got = mu._ping_once("1.1.1.1", 2.0)
        self.assertEqual(got, 35.0)
        kw = m.call_args.kwargs
        self.assertIn("encoding", kw)
        self.assertEqual(kw["errors"], "replace")


class TestPowerShellEncoding(unittest.TestCase):
    def test_backend_powershell_uses_safe_decoding(self):
        import engine as backend

        class Proc:
            returncode = 0
            stdout = "{}"
            stderr = ""

        with mock.patch.object(backend.subprocess, "run",
                               return_value=Proc()) as m:
            res = backend.RealBackend().powershell("Write-Output '{}'")
        self.assertTrue(res.ok)
        kw = m.call_args.kwargs
        self.assertEqual(kw.get("errors"), "replace")
        self.assertIn(kw.get("encoding"), ("oem", "utf-8"))

    def test_console_encoding_helper(self):
        from general_utils import console_encoding
        enc = console_encoding()
        if sys.platform.startswith("win"):
            self.assertEqual(enc, "oem")
        else:
            self.assertEqual(enc, "utf-8")


class TestSnappyThemeMapping(unittest.TestCase):
    def test_mapping_matches_host_surfaces(self):
        from input_utils import snappy_theme
        pal = {
            "bg": "#f4f5f7", "card": "#ffffff", "text": "#1b1b1b",
            "muted": "#5f6368", "entry": "#ffffff", "entry_bd": "#c8ccd0",
            "accent": "#c62828", "green": "#2e7d32", "amber": "#b26a00",
            "tab_bg": "#eceef1", "desc_bg": "#e8eaed", "status_bg": "#e8eaed",
            "light_bg": "#dfe2e6", "switch_on": "#cc2f38",
        }
        fonts = {"base": ("Segoe UI", 10), "bold": ("Segoe UI", 10, "bold"),
                 "h1": ("Segoe UI", 20, "bold"), "entry": ("Segoe UI", 10)}
        t = snappy_theme(pal, fonts)
        # pages are built on pal["card"] -> lattool root bg must equal it
        self.assertEqual(t.bg, pal["card"])
        # panels must contrast with the page, like native Snappy sections
        self.assertEqual(t.raised, pal["desc_bg"])
        self.assertEqual(t.inset, pal["desc_bg"])
        self.assertNotEqual(t.raised, t.bg)
        self.assertEqual(t.entry_bg, pal["entry"])
        self.assertEqual(t.fg, pal["text"])
        self.assertEqual(t.accent, pal["accent"])
        self.assertEqual(t.border, pal["entry_bd"])
        self.assertEqual(t.font_big[0], fonts["base"][0])


class TestNoAutoStartMonitor(unittest.TestCase):
    def test_build_monitor_does_not_autostart(self):
        """The monitor pinged the hardcoded default target at startup,
        showing values before the user asked for any measurement."""
        import ast
        src = open(os.path.join(ROOT, "lattool_gui.py"),
                   encoding="utf-8").read()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_build_monitor":
                # a bare `self._restart_watch()` statement (not inside a
                # lambda/binding) would auto-start pinging at build time
                bare = [st for st in ast.walk(node)
                        if isinstance(st, ast.Expr)
                        and isinstance(st.value, ast.Call)
                        and isinstance(st.value.func, ast.Attribute)
                        and st.value.func.attr == "_restart_watch"]
                self.assertEqual(bare, [],
                                 "_build_monitor must not auto-start the watch")
                break
        else:
            self.fail("_build_monitor not found")




class TestViGemSignatures(unittest.TestCase):
    """The official ViGEmClient API takes the client handle in
    vigem_target_x360_alloc, and 64-bit pointers must be marshalled as
    c_void_p when argtypes are undeclared (close path)."""

    def test_target_alloc_declared_with_client_arg(self):
        src = open(os.path.join(ROOT, "input_backend.py"),
                   encoding="utf-8").read()
        self.assertIn(
            "dll.vigem_target_x360_alloc.argtypes = [ctypes.c_void_p]", src)
        self.assertIn(
            "self._target = dll.vigem_target_x360_alloc(self._client)", src)

    def test_close_marshals_pointers(self):
        src = open(os.path.join(ROOT, "input_backend.py"),
                   encoding="utf-8").read()
        for call in ("vigem_target_remove", "vigem_target_free",
                     "vigem_disconnect", "vigem_free"):
            i = src.index("dll." + call + "(")
            snippet = src[i:i + 220]
            self.assertIn("ctypes.c_void_p(", snippet,
                          call + " must wrap pointer args in c_void_p")


class TestConfigSaveAtomic(unittest.TestCase):
    def test_save_leaves_no_tmp_and_valid_json(self):
        import json as _json
        import config as cfgmod
        import tempfile
        d = tempfile.mkdtemp()
        orig = cfgmod.config_dir
        cfgmod.config_dir = lambda: d
        try:
            cfg = cfgmod.Config()
            cfg.set("glide_ms", 77)
            self.assertTrue(os.path.exists(cfg.path))
            self.assertFalse(os.path.exists(cfg.path + ".tmp"))
            data = _json.load(open(cfg.path, encoding="utf-8"))
            self.assertEqual(data["glide_ms"], 77)
        finally:
            cfgmod.config_dir = orig


class TestSingleButtonChainAndWatch(unittest.TestCase):
    """One button does everything: 'Measure full chain' starts the live
    watch (top values + graph) AND the chain snapshot, then becomes the
    Stop for the sustained measurement. No second watch button."""

    def setUp(self):
        self.src = open(os.path.join(ROOT, "lattool_gui.py"),
                        encoding="utf-8").read()

    def test_no_separate_watch_button(self):
        self.assertNotIn("btn_watch", self.src)
        self.assertNotIn("_toggle_watch", self.src)

    def test_chain_button_is_the_only_control(self):
        self.assertIn('self.btn_chain = self._button(', self.src)
        self.assertIn('"Measure full chain", self.on_measure_chain', self.src)

    def test_button_starts_watch_and_chain_together(self):
        i = self.src.index("def on_measure_chain")
        body = self.src[i:i + 1100]
        self.assertIn("self._start_watch(target)", body)
        self.assertIn("self.ctl.start_chain(target=target", body)
        # pressing while watching stops the live measurement
        self.assertIn("if self.ctl.monitoring:", body)
        self.assertIn("self._stop_watch()", body)

    def test_start_watch_drives_monitor(self):
        i = self.src.index("def _start_watch")
        body = self.src[i:i + 500]
        self.assertIn("self.ctl.start_monitor(target, interval=0.1)", body)

    def test_watch_is_timed_to_20_seconds(self):
        self.assertIn("WATCH_SECONDS = 20.0", self.src)
        i = self.src.index("def _start_watch")
        body = self.src[i:self.src.index("def _finish_watch")]
        self.assertIn("int(WATCH_SECONDS * 1000)", body)
        self.assertIn("self._finish_watch(sess, timed_out=True)", body)
        # a fresh run clears the previous result before sampling
        self.assertIn("self._draw_spark([])", body)

    def test_finish_keeps_results_and_guards_sessions(self):
        i = self.src.index("def _finish_watch")
        body = self.src[i:self.src.index("def _stop_watch")]
        self.assertIn("sess != self._watch_session", body)   # stale timer no-op
        self.assertIn("self.ctl.stop_monitor()", body)
        self.assertIn("measured %.0fs", body)
        self.assertNotIn("_draw_spark([])", body)            # results preserved

    def test_stop_button_delegates_to_finish(self):
        i = self.src.index("def _stop_watch")
        body = self.src[i:i + 200]
        self.assertIn("self._finish_watch(self._watch_session, timed_out=False)",
                      body)

    def test_button_label_tracks_state(self):
        self.assertIn('"Stop" if self.ctl.monitoring else "Measure full chain"',
                      self.src)

    def test_build_monitor_does_not_autostart(self):
        import ast
        tree = ast.parse(self.src)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_build_monitor":
                bare = [st for st in ast.walk(node)
                        if isinstance(st, ast.Expr)
                        and isinstance(st.value, ast.Call)
                        and isinstance(st.value.func, ast.Attribute)
                        and st.value.func.attr in ("_restart_watch",
                                                   "_start_watch")]
                self.assertEqual(bare, [],
                                 "_build_monitor must not auto-start the watch")
                break
        else:
            self.fail("_build_monitor not found")



class TestChainTileLabels(unittest.TestCase):
    """Each chain tile must name the statistic it shows: input is p50
    one-way, render and network are p95 - the field user confusion
    ('network 17 ms vs ms-now 13 ms, is it the average?') came from the
    tiles being unlabeled while the big watch number is the LAST ping."""

    def setUp(self):
        self.src = open(os.path.join(ROOT, "lattool_gui.py"),
                        encoding="utf-8").read()

    def test_labels_match_the_fields_rendered(self):
        self.assertIn('"input": "INPUT (p50 one-way)"', self.src)
        self.assertIn('"render": "RENDER (p95)"', self.src)
        self.assertIn('"network": "NETWORK (p95)"', self.src)
        self.assertIn("text=CHAIN_TILE_LABELS[key]", self.src)
        # the values behind those labels
        self.assertIn('one = iv.get("p50_one_way_ms")', self.src)
        self.assertIn('rp = rv.get("p95_ms")', self.src)
        self.assertIn('np_ = nv.get("p95")', self.src)

    def test_watch_big_number_is_last_sample(self):
        ctl = open(os.path.join(ROOT, "lattool_controller.py"),
                   encoding="utf-8").read()
        self.assertIn('"current": window[-1]', ctl)


class TestUnifiedNetworkMeasurement(unittest.TestCase):
    """The watch is the only pinger during a combined run; the chain tile
    reports the watch's own samples (user request: one measurement, shown
    in both places)."""

    def setUp(self):
        self.gui = open(os.path.join(ROOT, "lattool_gui.py"),
                        encoding="utf-8").read()
        self.ctl = open(os.path.join(ROOT, "lattool_controller.py"),
                        encoding="utf-8").read()

    def test_watch_runs_at_dense_interval(self):
        self.assertIn("self.ctl.start_monitor(target, interval=0.1)", self.gui)

    def test_pump_coalesces_ticks(self):
        i = self.gui.index("def pump_once")
        body = self.gui[i:i + 900]
        self.assertIn("last_tick", body)
        self.assertIn("if ev.kind is EventType.MONITOR_TICK and i != last_tick:",
                      body)

    def test_controller_exposes_watch_samples(self):
        self.assertIn("def monitor_samples", self.ctl)
        self.assertIn('"source": None' if False else '"source"] = "live-watch"',
                      self.ctl)
        self.assertIn('payload["network"]["source"] = "chain-probe"', self.ctl)

    def test_unified_leg_does_not_probe_in_parallel(self):
        i = self.ctl.index("ONE network measurement")
        leg = self.ctl[i:i + 1600]
        # the unified branch waits on the watch; probe() only in the fallback
        self.assertNotIn("res = probe(", leg.split("else:")[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
