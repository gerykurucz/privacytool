import os, sys, json, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def _tmp_cfg():
    import config as cfgmod
    d = tempfile.mkdtemp()
    orig = cfgmod.config_dir
    cfgmod.config_dir = lambda: d
    cfg = cfgmod.Config()
    return cfg, cfgmod, orig


class TestMaintenanceFlows(unittest.TestCase):
    def setUp(self):
        from measurement_utils import build_fake_inventory
        self.inv = build_fake_inventory()

    def _render(self, steps, title):
        from engine import render_maintenance_script
        self.assertTrue(steps, title + ": no steps")
        text = render_maintenance_script(steps, title=title,
                                         generated_at="t", brand="SnappyAI")
        self.assertIn(title, text)
        self.assertGreater(len(text), 200)
        return text

    def test_cleanup_survey_and_execute(self):
        from maintenance_utils import build_cleanup_steps
        survey = build_cleanup_steps(survey_only=True)
        self._render(survey, "survey")
        full = build_cleanup_steps(survey_only=False)
        self._render(full, "cleanup")

    def test_redists(self):
        from maintenance_utils import build_redist_steps
        self._render(build_redist_steps(), "redists")
        self._render(build_redist_steps(include_optional=True), "redists-opt")

    def test_memory_and_power(self):
        from maintenance_utils import build_memory_steps, build_power_steps
        self._render(build_memory_steps(), "memory")
        self._render(build_memory_steps(("memory.measure",),
                                        process_names=("game.exe",)), "memory-proc")
        self._render(build_power_steps(), "power")
        with self.assertRaises(ValueError):
            build_memory_steps(("memory.does_not_exist",))

    def test_debloat_default_selection(self):
        from maintenance_utils import build_selected, DEBLOAT_OPERATIONS
        steps = build_selected(None, self.inv)
        text = self._render(steps, "debloat")
        self.assertIn("gpupdate", text)
        with self.assertRaises(ValueError):
            build_selected(("policy.not_real",), self.inv)
        reversible_ids = tuple(o.id for o in DEBLOAT_OPERATIONS if o.reversible)
        self._render(build_selected(reversible_ids, self.inv), "debloat-rev")

    def test_registry_payload_roundtrip(self):
        from maintenance_utils import load_registry_payload, registry_steps
        d = tempfile.mkdtemp()
        p = os.path.join(d, "payload.json")
        with open(p, "w") as fh:
            json.dump([{"hive": "HKCU", "key_path": r"Software\Test",
                        "name": "V", "value": 1, "value_type": "DWord"}], fh)
        changes = load_registry_payload(p)
        steps = registry_steps(changes)
        self._render(steps, "registry")

    def test_cleanup_report_shapes(self):
        from maintenance_utils import (cleanup_report, memory_report,
                                       redist_report, catalog_report,
                                       catalog_invariants)
        for rep in (cleanup_report(), memory_report(), redist_report(),
                    catalog_report()):
            self.assertIsInstance(rep, list)
            for item in rep:
                self.assertIn("id", item)
        inv = catalog_invariants()
        self.assertEqual(inv["total"],
                         inv["applicable"] + inv["experimental"] + inv["refused"]
                         - len([1 for _ in ()]))  # applicable excludes exp/refused
        self.assertGreater(inv["total"], 10)


class TestDefaultConfigTables(unittest.TestCase):
    def test_hotkey_table_from_defaults(self):
        cfg, cfgmod, orig = _tmp_cfg()
        try:
            from input_utils import build_hotkey_table, build_macro_table, ACTION_IDS
            always, local = build_hotkey_table(cfg)
            ids = {h for h, _m, _v in always} | {h for h, _v in local}
            self.assertIn(10, ids)          # launch
            self.assertIn(11, ids)          # pause
            self.assertEqual(ACTION_IDS[10], "launch")
            macros, mmap = build_macro_table(cfg)
            self.assertIsInstance(macros, list)
        finally:
            cfgmod.config_dir = orig

    def test_pad_bindings_from_defaults(self):
        cfg, cfgmod, orig = _tmp_cfg()
        try:
            import input_utils as gamepad
            bindings = gamepad.build_action_bindings(cfg)
            self.assertTrue(bindings)
            for b in bindings:
                self.assertTrue(b.valid, b.key)
            macros = gamepad.build_pad_macro_table(cfg)
            self.assertIsInstance(macros, list)
            ids = gamepad.action_ids()
            for _key, name in gamepad.ACTION_KEYS:
                self.assertIn(name, ids)
        finally:
            cfgmod.config_dir = orig

    def test_app_defaults_sane(self):
        cfg, cfgmod, orig = _tmp_cfg()
        try:
            self.assertIn(cfg.get("mode"), (1, 2, "1", "2"))
            self.assertIn(cfg.get("trigger_button"), ("mouse1", "mouse2",
                                                      "mouse3", "mouse4",
                                                      "mouse5"))
            self.assertNotEqual(cfg.get("trigger_button"),
                                cfg.get("options_button"))
            from system_core import parse_accents
            acc = cfg.get("accent_color")
            parse_accents(acc)   # must not raise for the shipped default
        finally:
            cfgmod.config_dir = orig


class TestScriptUndoSafety(unittest.TestCase):
    def test_apply_snapshots_registry_state(self):
        import engine
        from system_core import SafetyPolicy
        from system_core import Confidence
        from measurement_utils import build_fake_inventory
        res = engine.build_plan(build_fake_inventory(),
                                policy=SafetyPolicy(min_confidence=Confidence.LOW))
        bundle = engine.render(res, generated_at="t", brand="SnappyAI")
        self.assertIn("prior", bundle.apply_ps1)      # snapshot capture
        self.assertIn("prior", bundle.undo_ps1)       # restore from snapshot
        manifest = bundle.manifest
        self.assertTrue(manifest)


if __name__ == "__main__":
    unittest.main(verbosity=2)
