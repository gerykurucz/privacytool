import os, sys, json, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


class TestColorspec(unittest.TestCase):
    def test_presets_and_rgb(self):
        from system_core import parse_accent, parse_accents, hsv_to_rgb, ACCENT_PRESETS
        self.assertEqual(parse_accent("blue"), ACCENT_PRESETS["blue"])
        self.assertEqual(parse_accent("BLUE "), ACCENT_PRESETS["blue"])
        self.assertIsNone(parse_accent("off"))
        self.assertIsNone(parse_accent(""))
        self.assertIsNone(parse_accent(None))
        got = parse_accent("60,120,220")
        self.assertIsNotNone(got)
        h, s, v = got
        self.assertTrue(0 <= h <= 179 and 0 <= s <= 255 and 0 <= v <= 255)
        self.assertIsNone(parse_accent("300,0,0"))
        self.assertIsNone(parse_accent("1,2"))
        self.assertEqual(parse_accents("off"), [])
        multi = parse_accents("blue; red; 60,120,220")
        self.assertEqual(len(multi), 3)
        r, g, b = hsv_to_rgb(*ACCENT_PRESETS["red"])
        self.assertTrue(all(0 <= c <= 255 for c in (r, g, b)))

    def test_vision_reexports(self):
        import vision
        from system_core import parse_accents as ca
        self.assertIs(vision._parse_accents, ca)


class TestCommonFactories(unittest.TestCase):
    def test_factories_pass_step_validation(self):
        from models import manual, ps_step, reg_set, reg_delete
        from models import StepKind
        from engine import _step_apply_block, _step_undo_block
        m = manual("do it", "1. step one\n2. step two", notes="n")
        self.assertEqual(m.kind, StepKind.MANUAL)
        self.assertTrue(m.is_manual)
        r = reg_set("HKLM", r"SYSTEM\X", "V", 1, notes="why")
        self.assertEqual(r.kind, StepKind.REGISTRY_SET)
        self.assertTrue(r.terminal)
        self.assertIn("New-ItemProperty", _step_apply_block(r))
        self.assertIn("prior", _step_undo_block(r))     # snapshot restore
        d = reg_delete("HKCU", r"Software\Y", "W")
        self.assertEqual(d.kind, StepKind.REGISTRY_DELETE)
        p = ps_step("do", "Get-Process", "Stop-Nothing", notes="n")
        self.assertEqual(p.kind, StepKind.POWERSHELL)
        self.assertEqual(len(p.undo), 1)
        self.assertIn("Get-Process", _step_apply_block(p))
        self.assertIn("Stop-Nothing", _step_undo_block(p))
        p2 = ps_step("do", "Get-Process")
        self.assertTrue(p2.terminal)                    # no undo -> terminal
        with self.assertRaises(Exception):
            manual("empty", "   ")


class TestConfig(unittest.TestCase):
    """config_dir() is the app's own folder, so patch it to a temp dir."""

    def setUp(self):
        import config as cfgmod
        self.cfgmod = cfgmod
        self.dir = tempfile.mkdtemp()
        self._orig = cfgmod.config_dir
        cfgmod.config_dir = lambda: self.dir

    def tearDown(self):
        self.cfgmod.config_dir = self._orig
        for name in os.listdir(self.dir):
            try:
                os.remove(os.path.join(self.dir, name))
            except OSError:
                pass

    def test_defaults_and_roundtrip(self):
        from config import Config, DEFAULT_CONFIG, RADIUS_STEPS, _coerce_value
        cfg = Config()
        self.assertEqual(cfg.get("mode"), DEFAULT_CONFIG["mode"])
        self.assertEqual(cfg.get("radius"), DEFAULT_CONFIG["radius"])
        cfg.set("radius", 250, save=False)
        cfg.set("glide_ms", 120)
        self.assertTrue(os.path.exists(cfg.path))
        cfg2 = Config()
        self.assertEqual(cfg2.get("radius"), 250)
        self.assertEqual(cfg2.get("glide_ms"), 120)
        self.assertEqual(dict(RADIUS_STEPS)[150], "medium")
        ok, val = _coerce_value("80", DEFAULT_CONFIG["radius"])
        self.assertTrue(ok)
        self.assertEqual(val, 80)

    def test_sanitize_repairs_role_collision(self):
        from config import Config
        cfg = Config()
        cfg.set("trigger_button", "mouse2", save=False)
        cfg.set("options_button", "mouse2", save=False)
        cfg.sanitize()
        self.assertNotEqual(cfg.get("trigger_button"), cfg.get("options_button"))

    def test_export_redacts_sensitive_and_import_skips_them(self):
        from config import Config
        import general_utils as build_secrets
        cfg = Config()
        out = os.path.join(self.dir, "exp.json")
        ok, _msg = cfg.export_to(out)
        self.assertTrue(ok)
        data = json.load(open(out))
        for k in build_secrets.SENSITIVE_KEYS:
            self.assertNotIn(k, data)
        data["glide_ms"] = 99
        data["entitlement_repo"] = "evil/repo"
        tmp = os.path.join(self.dir, "imp.json")
        with open(tmp, "w") as fh:
            json.dump(data, fh, default=str)
        ok, _msg = cfg.import_from(tmp)
        self.assertTrue(ok)
        self.assertEqual(cfg.get("glide_ms"), 99)
        self.assertNotEqual(cfg.values.get("entitlement_repo"), "evil/repo")

    def test_language_validation(self):
        from config import Config
        cfg = Config()
        cfg.values["language"] = "zz"
        cfg.sanitize()
        self.assertEqual(cfg.get("language"), "en")


class TestBuildSecrets(unittest.TestCase):
    def test_accessors_and_readiness(self):
        import general_utils as bs
        for fn in ("discord_client_id", "discord_client_secret",
                   "entitlement_repo", "entitlement_branch",
                   "entitlement_pubkey", "stripe_trial_link",
                   "stripe_monthly_link", "presence_webhook", "row_pepper",
                   "dispatch_pat"):
            self.assertIsInstance(getattr(bs, fn)(), str)
        fatal, advisory = bs.describe_readiness()
        self.assertIsInstance(fatal, list)
        self.assertIsInstance(advisory, list)
        self.assertIsInstance(bs.is_shippable(), bool)

    def test_env_override(self):
        import importlib
        os.environ["SNAPPYAI_ENT_BRANCH"] = "devbranch"
        try:
            import general_utils as bs
            bs._cache.pop("ENTITLEMENT_BRANCH", None)
            self.assertEqual(bs.entitlement_branch(), "devbranch")
        finally:
            os.environ.pop("SNAPPYAI_ENT_BRANCH", None)
            import general_utils as bs
            bs._cache.pop("ENTITLEMENT_BRANCH", None)


class TestPolicyGating(unittest.TestCase):
    def _fake_inv(self):
        from measurement_utils import build_fake_inventory
        return build_fake_inventory()

    def test_min_confidence_filters(self):
        import engine
        from system_core import Confidence
        from system_core import SafetyPolicy
        inv = self._fake_inv()
        low = engine.build_plan(inv, policy=SafetyPolicy(
            min_confidence=Confidence.LOW, allow_experimental=True))
        high = engine.build_plan(inv, policy=SafetyPolicy(
            min_confidence=Confidence.HIGH, allow_experimental=False))
        denied_low = [o for o in low.outcomes if o.policy and not o.policy.allowed]
        denied_high = [o for o in high.outcomes if o.policy and not o.policy.allowed]
        self.assertGreater(len(denied_high), len(denied_low))

    def test_experimental_gated(self):
        import engine
        from system_core import SafetyPolicy
        inv = self._fake_inv()
        off = engine.build_plan(inv, policy=SafetyPolicy(allow_experimental=False))
        on = engine.build_plan(inv, policy=SafetyPolicy(allow_experimental=True))
        exp_off = [o for o in off.outcomes if o.tweak.experimental]
        exp_on = [o for o in on.outcomes if o.tweak.experimental]
        self.assertEqual(exp_off, [])          # filtered at catalog level
        self.assertTrue(exp_on)                # present when enabled
        for o in exp_on:
            if o.policy and not o.policy.allowed:
                self.assertNotIn(o.tweak.id, on.actionable_ids)

    def test_refused_never_planned(self):
        import engine
        from system_core import SafetyPolicy
        from system_core import RefusedTweakError
        inv = self._fake_inv()
        res = engine.build_plan(inv, policy=SafetyPolicy(allow_experimental=True))
        refused = [o for o in res.outcomes if o.tweak.is_refused]
        self.assertTrue(refused)
        for o in refused:
            self.assertNotIn(o.tweak.id, res.actionable_ids)
            with self.assertRaises(RefusedTweakError):
                o.tweak.build_plan(inv)

    def test_plan_scripts_and_undo_exist(self):
        import engine, tempfile
        from system_core import SafetyPolicy
        from system_core import Confidence
        inv = self._fake_inv()
        res = engine.build_plan(inv, policy=SafetyPolicy(
            min_confidence=Confidence.LOW, allow_experimental=False))
        bundle = engine.render(res, generated_at="t", brand="SnappyAI")
        d = tempfile.mkdtemp()
        paths = bundle.write(d)
        apply_txt = open(paths["apply"], encoding="utf-8-sig").read()
        undo_txt = open(paths["undo"], encoding="utf-8-sig").read()
        self.assertIn("apply", apply_txt.lower())
        manifest = json.load(open(paths["manifest"], encoding="utf-8"))
        self.assertIn("generated_at", manifest)
        self.assertTrue(len(undo_txt) > 0)


class TestLatencyTabsGlue(unittest.TestCase):
    def test_surface_matches_gui_expectations(self):
        import input_utils as tabs
        for name in ("mount", "pump", "shutdown", "POLL_MS",
                     "default_out_root", "LATENCY_TABS"):
            self.assertTrue(hasattr(tabs, name), name)
        self.assertEqual(tabs.LATENCY_TABS,
                         ("latency_fix", "latency_live", "latency_tools"))
        import inspect
        sig = inspect.signature(tabs.mount)
        for p in ("root", "pages", "kit", "pal", "fonts", "out_root", "backend"):
            self.assertIn(p, sig.parameters)

    def test_gui_tab_names_cover_latency_tabs(self):
        src = open(os.path.join(ROOT, "gui.py"), encoding="utf-8").read()
        for tab in ("latency_fix", "latency_live", "latency_tools"):
            self.assertIn('"%s"' % tab, src)


class TestEdsigWiring(unittest.TestCase):
    def test_online_uses_real_edsig(self):
        import online
        import system_core as edsig
        self.assertIs(online.edsig, edsig)
        self.assertTrue(hasattr(edsig, "verify"))

    def test_entitlement_signature_rejects_tamper(self):
        import os, json, secrets
        import system_core as edsig
        sec = secrets.token_bytes(32)
        pub = edsig.public_from_secret(sec)
        doc = {"rows": {"a": 1}, "generated_at": 0}
        import online
        body = dict(doc)
        sig = edsig.sign(sec, online._canonical_bytes(body))
        self.assertTrue(edsig.verify(pub, online._canonical_bytes(body), sig))
        body["rows"] = {"a": 2}
        self.assertFalse(edsig.verify(pub, online._canonical_bytes(body), sig))




class TestModeSwitchPersistence(unittest.TestCase):
    """Regression: a mode= line in config.ini silently reverted the live
    1/2-key mode flip on every reload/Apply, so 'mode 1' was unreachable
    for anyone with a legacy ini."""

    def setUp(self):
        import config as cfgmod
        self.cfgmod = cfgmod
        self.dir = tempfile.mkdtemp()
        self._orig = cfgmod.config_dir
        cfgmod.config_dir = lambda: self.dir

    def tearDown(self):
        self.cfgmod.config_dir = self._orig

    def test_ini_sets_startup_mode_but_live_flip_survives_reload(self):
        with open(os.path.join(self.dir, "config.ini"), "w") as fh:
            fh.write("[snappyai]\nmode = 1\n")
        cfg = self.cfgmod.Config()
        self.assertEqual(int(cfg.get("mode")), 1)      # startup honours ini
        cfg.set("mode", 2)                             # live flip ("2" key)
        cfg.reload()                                   # Apply / reload hotkey
        self.assertEqual(int(cfg.get("mode")), 2)      # live intent survives

    def test_json_mode_survives_reload_without_ini(self):
        cfg = self.cfgmod.Config()
        cfg.set("mode", 1)
        cfg.reload()
        self.assertEqual(int(cfg.get("mode")), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
