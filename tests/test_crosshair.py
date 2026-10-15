import math
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import crosshair


class TestParseColor(unittest.TestCase):
    def test_rgb(self):
        self.assertEqual(crosshair.parse_color("0,255,0"), (0, 255, 0))

    def test_hex(self):
        self.assertEqual(crosshair.parse_color("#ff0080"), (255, 0, 128))

    def test_clamp(self):
        self.assertEqual(crosshair.parse_color("300,-5,0"), (255, 0, 0))

    def test_fallback(self):
        for bad in ("", "off", "red", "1,2", None, "zzzzzz"):
            self.assertEqual(crosshair.parse_color(bad),
                             crosshair.DEFAULT_COLOR)

    def test_hex_roundtrip(self):
        self.assertEqual(crosshair.to_hex((0, 255, 0)), "#00ff00")


class TestGeometry(unittest.TestCase):
    def test_cross_symmetry(self):
        geo = crosshair.shape_geometry("cross", 24, 6, 2, 0)
        self.assertEqual(len(geo["lines"]), 4)
        xs = [x for seg in geo["lines"] for x in (seg[0], seg[2])]
        ys = [y for seg in geo["lines"] for y in (seg[1], seg[3])]
        self.assertAlmostEqual(sum(xs) / len(xs), 0.0, places=6)
        self.assertAlmostEqual(sum(ys) / len(ys), 0.0, places=6)

    def test_cross_extent(self):
        geo = crosshair.shape_geometry("cross", 24, 6, 2, 0)
        reach = max(abs(v) for seg in geo["lines"] for v in seg)
        self.assertAlmostEqual(reach, 6 + 12, places=6)

    def test_plus_no_gap(self):
        geo = crosshair.shape_geometry("plus", 24, 6, 2, 0)
        inner = min(
            min(abs(seg[0]), abs(seg[2]), abs(seg[1]), abs(seg[3]))
            for seg in geo["lines"])
        self.assertAlmostEqual(inner, 0.0, places=6)

    def test_dot_and_circle(self):
        dot = crosshair.shape_geometry("dot", 24, 6, 2, 0)
        self.assertEqual(dot["lines"], [])
        self.assertEqual(len(dot["ovals"]), 1)
        circ = crosshair.shape_geometry("circle", 24, 6, 2, 0)
        self.assertEqual(len(circ["ovals"]), 2)
        self.assertAlmostEqual(circ["ovals"][0][2], 12.0, places=6)

    def test_x_diagonal(self):
        geo = crosshair.shape_geometry("x", 20, 4, 2, 0)
        self.assertEqual(len(geo["lines"]), 4)
        for x1, y1, x2, y2 in geo["lines"]:
            self.assertAlmostEqual(abs(x1), abs(y1), places=4)
            self.assertAlmostEqual(abs(x2), abs(y2), places=4)

    def test_rotation_90(self):
        a = crosshair.shape_geometry("cross", 24, 6, 2, 0)["lines"]
        b = crosshair.shape_geometry("cross", 24, 6, 2, 90)["lines"]
        sa = sorted((round(x1, 4), round(y1, 4), round(x2, 4), round(y2, 4))
                    for x1, y1, x2, y2 in a)
        sb = sorted((round(-y1, 4), round(x1, 4), round(-y2, 4), round(x2, 4))
                    for x1, y1, x2, y2 in b)
        for pa, pb in zip(sa, sb):
            for va, vb in zip(pa, pb):
                self.assertAlmostEqual(va, vb, places=3)

    def test_bad_shape_falls_back(self):
        geo = crosshair.shape_geometry("nope", 24, 6, 2, 0)
        self.assertEqual(len(geo["lines"]), 4)


class TestPresets(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def test_roundtrip(self):
        vals = {"crosshair_shape": "dot", "crosshair_size": 30,
                "other": "dropped"}
        crosshair.save_preset("snipe", vals, self.dir)
        self.assertEqual(sorted(crosshair.list_presets(self.dir)), ["snipe"])
        back = crosshair.load_preset("snipe", self.dir)
        self.assertEqual(back["crosshair_shape"], "dot")
        self.assertNotIn("other", back)
        self.assertTrue(crosshair.delete_preset("snipe", self.dir))
        self.assertFalse(crosshair.delete_preset("snipe", self.dir))

    def test_empty_name_rejected(self):
        with self.assertRaises(ValueError):
            crosshair.save_preset("  ", {}, self.dir)


class TestConfig(unittest.TestCase):
    def setUp(self):
        import config as cfgmod
        self.cfgmod = cfgmod
        self.dir = tempfile.mkdtemp()
        self._orig = cfgmod.config_dir
        cfgmod.config_dir = lambda: self.dir

    def tearDown(self):
        self.cfgmod.config_dir = self._orig

    def test_defaults(self):
        from config import DEFAULT_CONFIG, Config
        self.assertFalse(DEFAULT_CONFIG["crosshair_enabled"])
        self.assertEqual(DEFAULT_CONFIG["crosshair_shape"], "cross")
        self.assertEqual(DEFAULT_CONFIG["crosshair_mode"], "center")
        cfg = Config()
        self.assertEqual(cfg.get("crosshair_opacity"), 90)

    def test_ranges_and_choices(self):
        from config import Config
        cfg = Config()
        cfg.set("crosshair_size", 500, save=False)
        self.assertEqual(cfg.get("crosshair_size"), 96)
        cfg.set("crosshair_shape", "banana", save=False)
        self.assertEqual(cfg.get("crosshair_shape"), "cross")
        cfg.set("crosshair_mode", "CENTER", save=False)
        self.assertEqual(cfg.get("crosshair_mode"), "center")


if __name__ == "__main__":
    unittest.main(verbosity=2)
