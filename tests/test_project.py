import os, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


class TestGamepadGrammar(unittest.TestCase):
    def test_parse_token_and_aliases(self):
        import input_utils as g
        self.assertEqual(g.parse_token("A"), g.PAD_BUTTONS.index("a"))
        self.assertEqual(g.parse_token("r1"), g.PAD_BUTTONS.index("rb"))
        self.assertEqual(g.parse_token("cross"), g.PAD_BUTTONS.index("a"))
        self.assertIsNone(g.parse_token("nope"))
        self.assertIsNone(g.parse_token(""))

    def test_spec_roundtrip(self):
        import input_utils as g
        spec = g.parse_spec("RB + a")
        self.assertEqual(spec, frozenset({g.PAD_BUTTONS.index("rb"),
                                          g.PAD_BUTTONS.index("a")}))
        self.assertEqual(g.format_buttons(g.spec_mask("RB + a")), "rb+a")
        self.assertIsNone(g.parse_spec(""))
        self.assertIsNone(g.parse_spec("a+a"))
        self.assertEqual(g.spec_mask("bogus"), 0)

    def test_tracker_fires_once_per_press(self):
        import input_utils as g
        t = g.PadTracker(g.parse_spec("rb+a"))
        a = 1 << g.PAD_BUTTONS.index("a")
        rb = 1 << g.PAD_BUTTONS.index("rb")
        self.assertIsNone(t.update(0))
        self.assertIsNone(t.update(a))            # partial: not matching
        self.assertEqual(t.update(a | rb), "press")
        self.assertIsNone(t.update(a | rb))       # held: no repeat
        self.assertIsNone(t.update(a))            # rb released
        self.assertEqual(t.update(a | rb), "press")  # new press

    def test_shadowing(self):
        import input_utils as g
        short = g.PadBinding("k1", "a", 1)
        long = g.PadBinding("k2", "rb+a", 2)
        buttons = g.spec_mask("rb+a")
        shadow = g.shadowed_indices([short, long], buttons)
        self.assertEqual(shadow, {id(short)})

    def test_deadzone_and_trigger(self):
        import input_utils as g
        self.assertEqual(g.apply_deadzone(0, 0, 7849), (0.0, 0.0))
        x, y = g.apply_deadzone(32767, 0, 7849)
        self.assertAlmostEqual(x, 1.0, places=3)
        self.assertEqual(y, 0.0)
        self.assertEqual(g.trigger_value(30), 0.0)
        self.assertAlmostEqual(g.trigger_value(255), 1.0, places=6)
        self.assertEqual(g.normalise_axis(0, 9999), 255)      # lt clamps
        self.assertEqual(g.normalise_axis(2, -99999), -32768)  # lx clamps

    def test_build_bindings_first_wins(self):
        import input_utils as g
        out = g.build_bindings({"k1": ("a", 1), "k2": ("a", 2),
                                "k3": ("", 3), "k4": ("zz", 4)})
        self.assertEqual([b.key for b in out], ["k1"])


class TestLogoDecoder(unittest.TestCase):
    def test_decode_embedded_png(self):
        import logo
        w, h, rgba = logo._decode_png_rgba(logo._LOGO_BYTES)
        self.assertGreater(w, 0)
        self.assertGreater(h, 0)
        self.assertEqual(len(rgba), w * h * 4)

    def test_png_bytes_and_provider(self):
        import logo
        self.assertEqual(logo.png_bytes(), logo._LOGO_BYTES)
        self.assertIn("discord", logo.PROVIDER_LOGO_B64)


class TestGeneralUtils(unittest.TestCase):
    def test_runner_non_windows(self):
        import sys
        import general_utils as gu
        if sys.platform.startswith("win"):
            self.assertIsInstance(gu.is_elevated(), bool)
        else:
            self.assertFalse(gu.is_elevated())
        kw = gu.silent_kwargs()
        self.assertIn("stdin", kw)

    def test_ps_quote(self):
        import general_utils as gu
        self.assertEqual(gu._ps_quote("a'b"), "'a''b'")


class TestRecordings(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "macros.json")

    def test_validate_steps(self):
        import input_utils as r
        self.assertEqual(
            r.validate_steps([(0, 2, 65, 10)]),
            [(r.STEP_KEY, 2, 65, 10)])
        self.assertEqual(
            r.validate_steps([(2, 65, 10)]),            # legacy (mods, vk, delay)
            [(r.STEP_KEY, 2, 65, 10)])
        self.assertEqual(
            r.validate_steps([(r.STEP_MOVE, 5, 6, 7000)]),
            [(r.STEP_MOVE, 5, 6, r.MAX_DELAY_MS)])
        self.assertEqual(
            r.validate_steps([(r.STEP_BUTTON, r.BTN_X2, r.PHASE_DOWN,
                               1, 2, 30)]),
            [(r.STEP_BUTTON, r.BTN_X2, r.PHASE_DOWN, 1, 2, 30)])
        self.assertEqual(
            r.validate_steps([(r.STEP_PAD_BUTTON, 10, r.PHASE_UP, 5)]),
            [(r.STEP_PAD_BUTTON, 10, r.PHASE_UP, 5)])
        self.assertIsNone(r.validate_steps([(r.STEP_BUTTON, 99, 0, 1, 2, 3)]))
        self.assertIsNone(r.validate_steps([(r.STEP_KEY, 0x1F, 65, 5)]))
        self.assertIsNone(r.validate_steps([]))

    def test_store_roundtrip_and_persistence(self):
        import input_utils as r
        st = r.RecordingStore(path=self.path)
        rec = st.add("t1", [(r.STEP_KEY, 0, 65, 10)])
        self.assertIsNotNone(rec)
        self.assertTrue(st.set_loop(rec["id"], True))
        self.assertTrue(st.set_name(rec["id"], "renamed"))
        st2 = r.RecordingStore(path=self.path)   # reload: mutations persisted
        self.assertEqual(len(st2.recordings), 1)
        self.assertEqual(st2.recordings[0]["name"], "renamed")
        self.assertTrue(st2.recordings[0]["loop"])
        self.assertTrue(st2.remove(rec["id"]))
        self.assertEqual(r.RecordingStore(path=self.path).recordings, [])

    def test_store_cap(self):
        import input_utils as r
        st = r.RecordingStore(path=self.path)
        for i in range(r.MAX_RECORDINGS + 2):
            st.add("r%d" % i, [(r.STEP_KEY, 0, 65 + i, 10)])
        self.assertEqual(len(st.recordings), r.MAX_RECORDINGS)

    def test_export_import(self):
        import input_utils as r
        st = r.RecordingStore(path=self.path)
        st.add("x", [(r.STEP_KEY, 0, 65, 10)])
        out = os.path.join(self.dir, "exp.json")
        ok, _msg = st.export_to(out)
        self.assertTrue(ok)
        st2 = r.RecordingStore(path=os.path.join(self.dir, "other.json"))
        ok, _msg = st2.import_from(out)
        self.assertTrue(ok)
        self.assertEqual(len(st2.recordings), 1)

    def test_import_bad_version_rejected_with_message(self):
        import json
        import input_utils as r
        bad = os.path.join(self.dir, "bad.json")
        with open(bad, "w") as fh:
            json.dump({"snappyai_recordings": 99, "recordings": []}, fh)
        st = r.RecordingStore(path=self.path)
        ok, msg = st.import_from(bad)
        self.assertFalse(ok)
        self.assertNotIn("rec.bad_version", str(msg))   # key must resolve


class TestMeasurementStats(unittest.TestCase):
    def test_distribution(self):
        from measurement_utils import Distribution
        d = Distribution(samples=[float(x) for x in range(1, 101)],
                         lost=5, sent=105)
        self.assertEqual(d.n, 100)
        self.assertAlmostEqual(d.p50, 50.5, places=1)
        self.assertEqual(d.max, 100.0)
        self.assertAlmostEqual(d.loss_pct, 100.0 * 5 / 105)
        e = Distribution()
        self.assertIsNone(e.p50)
        self.assertEqual(e.loss_pct, 0.0)

    def test_decide(self):
        from measurement_utils import Distribution, decide
        base = Distribution(samples=[50.0 + (i % 3) for i in range(60)])
        worse = Distribution(samples=[80.0 + (i % 3) for i in range(60)])
        comp = decide(base, worse, metric="p95", min_effect=1.0)
        self.assertTrue(comp.significant)
        self.assertTrue(comp.meaningful)
        self.assertIn("REVERT", comp.recommendation)
        empty = decide(base, Distribution(), metric="p95")
        self.assertFalse(empty.significant)

    def test_build_chain(self):
        from measurement_utils import build_chain
        inp = {"ok": True, "p50_one_way_ms": 2.0}
        rend = {"ok": True, "p50_ms": 5.0}
        net = {"p50": 10.0}
        ch = build_chain(inp, rend, net)
        self.assertIn("total_ms", ch)


class TestModelsAndCatalog(unittest.TestCase):
    def test_step_validation(self):
        from models import Step, StepKind
        from system_core import TweakValidationError
        with self.assertRaises(TweakValidationError):
            Step(kind=StepKind.MANUAL, description="m", text="  ")
        with self.assertRaises(TweakValidationError):
            Step(kind=StepKind.REGISTRY_SET, description="r", hive="HKLM")
        s = Step(kind=StepKind.POWERSHELL, description="p", command="x",
                 terminal=True)
        self.assertTrue(s.needs_reboot is False)

    def test_tweak_marketing_filter(self):
        from models import Tweak
        from system_core import TweakValidationError
        from system_core import BudgetComponent, Confidence, Risk
        kw = dict(component=BudgetComponent.HOST_PROCESSING,
                  confidence=Confidence.HIGH, risk=Risk.LOW,
                  summary="s", probe=lambda i: None, plan=lambda i: [])
        with self.assertRaises(TweakValidationError):
            Tweak(id="bad.id", title="t",
                  mechanism="boosts performance better faster stronger "
                            "turbo ultimate unlock superior", **kw)

    def test_full_catalog_validates(self):
        import maintenance_utils as mu
        tweaks = mu.all_tweaks()
        self.assertGreater(len(tweaks), 10)
        ids = [t.id for t in tweaks]
        self.assertEqual(len(ids), len(set(ids)))
        counts = mu.catalog_invariants()
        self.assertEqual(counts["total"], len(tweaks))
        # every applicable tweak's probe must run against the fixture
        from measurement_utils import build_fake_inventory
        fake = build_fake_inventory()
        for t in tweaks:
            f = t.evaluate(fake)
            self.assertTrue(f.verdict is not None)
        # display/network/host/gaming/experimental/refused all present
        for p in ("net", "nic", "display", "gpu", "input", "bus", "timer",
                  "sched", "cpu", "os", "kb", "capture"):
            self.assertTrue(any(t.id.startswith(p) for t in tweaks),
                            "no tweak with prefix " + p)


class TestScriptRendering(unittest.TestCase):
    def test_bundle_roundtrip(self):
        import tempfile
        from models import Step, StepKind, Tweak
        from system_core import BudgetComponent, Confidence, Risk
        from engine import PlannedChange, render_bundle, write_powershell
        t = Tweak(
            id="test.tweak", title="T", component=BudgetComponent.HOST_PROCESSING,
            mechanism="A causal sentence with well over twelve words in it "
                      "describing precisely what happens where and why.",
            confidence=Confidence.HIGH, risk=Risk.LOW, summary="s",
            probe=lambda i: None,
            plan=lambda i: [Step(kind=StepKind.POWERSHELL, description="d",
                                 command="echo hi", terminal=True)],
        )
        pc = PlannedChange(tweak=t, steps=t.plan(None), finding_summary="f")
        b = render_bundle([pc], generated_at="now", brand="latency")
        d = tempfile.mkdtemp()
        paths = b.write(d)
        for k in ("apply", "undo", "manifest"):
            self.assertTrue(os.path.exists(paths[k]))
        self.assertIn("echo hi", b.apply_ps1)


class TestHotkeys(unittest.TestCase):
    def test_parse_hotkey(self):
        from input_utils import _parse_hotkey, HOTKEY_MODS, HOTKEY_NOREPEAT
        mods, vk = _parse_hotkey("Ctrl+Alt+R")
        self.assertEqual(vk, ord("R"))
        self.assertTrue(mods & HOTKEY_MODS["ctrl"])
        self.assertTrue(mods & HOTKEY_NOREPEAT)
        self.assertIsNone(_parse_hotkey("ctrl+ctrl+r"))
        self.assertIsNone(_parse_hotkey("nokey"))
        mods, vk = _parse_hotkey("ctrl++")
        self.assertEqual(vk, 0xBB)

    def test_bypass_spec(self):
        from input_utils import parse_bypass_spec, describe_bypass_spec
        self.assertEqual(parse_bypass_spec("shift"), (0x0004, None))
        self.assertIsNone(parse_bypass_spec(""))
        self.assertEqual(describe_bypass_spec("SHIFT+ctrl+x"), "ctrl+shift+x")

    def test_tables(self):
        from input_utils import build_hotkey_table, build_macro_table

        class Cfg:
            def __init__(self, d): self.d = d
            def get(self, k, default=None): return self.d.get(k, default)

        cfg = Cfg({"key_launch": "ctrl+l", "key_mode1": "1,f5",
                   "key_mode2": "2", "macro1_key": "ctrl+f9",
                   "macro1_action": "ctrl+c"})
        always, local = build_hotkey_table(cfg)
        self.assertIn((10, 0x0002 | 0x4000, ord("L")), always)
        vks = [vk for _h, vk in local]
        self.assertIn(ord("1"), vks)
        macros, mmap = build_macro_table(cfg)
        self.assertEqual(len(macros), 1)
        self.assertIn((0x0002, 0x78), mmap)


class TestEnginePipeline(unittest.TestCase):
    def test_fake_backend_full_pipeline(self):
        import engine
        from engine import make_backend
        from measurement_utils import CollectOptions, collect_inventory
        from system_core import Confidence, SafetyPolicy
        be = make_backend("fake")
        inv = collect_inventory(be, CollectOptions())
        policy = SafetyPolicy(min_confidence=Confidence.LOW,
                              allow_experimental=False)
        result = engine.build_plan(inv, policy=policy)
        self.assertTrue(hasattr(result, "outcomes"))
        self.assertTrue(hasattr(result, "planned"))
        bundle = engine.render(result, generated_at="t", brand="latency")
        self.assertIn("apply_ps1", dir(bundle))
        report = engine.build_report(result, maintenance=[], generated_at="t")
        from engine import render_markdown, render_html
        md = render_markdown(report, brand="latency")
        html = render_html(report, brand="latency")
        self.assertIn("latency", md)
        self.assertTrue(html.startswith("<!DOCTYPE html") or "<html" in html)

    def test_baseline_roundtrip(self):
        import tempfile, os
        import engine
        d = tempfile.mkdtemp()
        p = os.path.join(d, "base.json")
        payload = {"idle": {"p50": 10.0}, "samples": [1.0, 2.0]}
        engine.save_baseline(p, payload)
        got = engine.load_baseline(p)
        self.assertEqual(got["samples"], [1.0, 2.0])


class TestImports(unittest.TestCase):
    def test_every_module_imports(self):
        import importlib
        mods = [
            "system_core", "config", "general_utils", "input_utils",
            "maintenance_utils", "measurement_utils", "models",
            "logo", "vision", "win32rt", "crosshair",
            "input_backend",
            "engine", "online",
            "license_client", "lattool_controller", "assist", "console",
            "main",
        ]
        failed = []
        for m in mods:
            try:
                importlib.import_module(m)
            except Exception as e:
                failed.append("%s: %r" % (m, e))
        self.assertEqual(failed, [], "import failures:\n" + "\n".join(failed))


if __name__ == "__main__":
    unittest.main(verbosity=2)
