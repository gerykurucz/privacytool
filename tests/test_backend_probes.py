import os, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


class TestParsers(unittest.TestCase):
    def test_parse_scheme(self):
        from engine import parse_scheme
        text = ("Power Scheme GUID: 381b4222-f694-41f0-9685-ff5bb260df2e"
                "  (Balanced)\r\n")
        guid, name = parse_scheme(text)
        self.assertEqual(guid, "381b4222-f694-41f0-9685-ff5bb260df2e")
        self.assertEqual(name, "Balanced")
        self.assertEqual(parse_scheme("garbage"), ("", ""))

    def test_parse_powercfg_index(self):
        from engine import parse_powercfg_index
        text = (
            "    Power Setting Index: 0x00000001\n"
            "    Current AC Power Setting Index: 0x00000000\n"
            "    Current DC Power Setting Index: 0x00000002\n")
        self.assertEqual(parse_powercfg_index(text, "AC"), 0)
        self.assertEqual(parse_powercfg_index(text, "DC"), 2)
        self.assertIsNone(parse_powercfg_index("nothing", "AC"))

    def test_parse_nics(self):
        from engine import parse_nics
        payload = {
            "a": [
                {"InterfaceDescription": "Intel(R) Ethernet I225-V",
                 "Name": "Ethernet", "Status": "Up", "MtuSize": 1500,
                 "PhysicalMediaType": "802.3"},
                {"InterfaceDescription": "Intel(R) Wi-Fi 6 AX201",
                 "Name": "Wi-Fi", "Status": "Disconnected", "MtuSize": 1500,
                 "PhysicalMediaType": "Native 802.11"},
            ],
            "p": [{"Name": "Ethernet", "AllowComputerToTurnOffDevice": "Disabled"}],
            "m": [{"Name": "Ethernet", "DisplayValue": "Enabled"}],
        }
        nics = parse_nics(payload)
        self.assertEqual(len(nics), 2)
        eth, wifi = nics
        self.assertEqual(eth.physical, "wired")
        self.assertEqual(eth.mtu, 1500)
        self.assertIs(eth.allow_turn_off, False)
        self.assertIs(eth.interrupt_moderation, True)
        self.assertEqual(wifi.physical, "wireless")
        self.assertIsNone(wifi.allow_turn_off)       # no row -> unknown
        self.assertIsNone(wifi.interrupt_moderation)
        # single-object unwrap + missing sub-payloads
        one = parse_nics({"a": {"Name": "E2", "Status": "Up"}})
        self.assertEqual(len(one), 1)
        self.assertEqual(one[0].physical, "")
        self.assertEqual(parse_nics({"a": None}), [])

    def test_parse_gpus_displays(self):
        from engine import parse_gpus_displays
        from system_core import Vendor
        rows = [
            {"Name": "NVIDIA GeForce RTX 4070", "DriverVersion": "551.23",
             "CurrentRefreshRate": 60, "MaxRefreshRate": 165,
             "CurrentHorizontalResolution": 2560,
             "CurrentVerticalResolution": 1440},
            {"Name": "Intel(R) UHD Graphics 770", "DriverVersion": "31.0",
             "CurrentRefreshRate": None, "MaxRefreshRate": None,
             "CurrentHorizontalResolution": None,
             "CurrentVerticalResolution": None},
        ]
        gpus, displays = parse_gpus_displays(rows, hags=True)
        self.assertEqual(len(gpus), 2)
        self.assertIs(gpus[0].vendor, Vendor.NVIDIA)
        self.assertIs(gpus[0].hags, True)
        self.assertEqual(len(displays), 1)      # headless adapter has no display
        d = displays[0]
        self.assertEqual(d.resolution, "2560x1440")
        self.assertEqual(d.current_refresh_hz, 60.0)
        self.assertEqual(d.max_refresh_hz, 165.0)
        self.assertEqual(d.refresh_deficit_hz, 105.0)
        # single dict unwrap
        g2, d2 = parse_gpus_displays(rows[0], hags=None)
        self.assertEqual(len(g2), 1)
        self.assertEqual(len(d2), 1)


class TestProbeReadback(unittest.TestCase):
    def _inv(self, **kw):
        from measurement_utils import build_fake_inventory
        inv = build_fake_inventory()
        for k, v in kw.items():
            setattr(inv, k, v)
        return inv

    def test_usb_probe_reads_back(self):
        import maintenance_utils as host
        from system_core import Verdict
        self.assertIs(host._usb_probe(self._inv(usb_selective_suspend=True)).verdict,
                      Verdict.PROBLEM)
        self.assertIs(host._usb_probe(self._inv(usb_selective_suspend=False)).verdict,
                      Verdict.NO_PROBLEM)
        self.assertIs(host._usb_probe(self._inv(usb_selective_suspend=None)).verdict,
                      Verdict.UNKNOWN)

    def test_usb_plan_is_powercfg_with_undo(self):
        import maintenance_utils as host
        from models import StepKind
        steps = host._usb_plan(None)
        self.assertEqual(len(steps), 1)
        s = steps[0]
        self.assertEqual(s.kind, StepKind.POWERCFG)
        self.assertIn("setacvalueindex", s.command)
        self.assertIn("USBSELECTSUSPEND 0", s.command)
        self.assertEqual(len(s.undo), 1)
        self.assertIn("USBSELECTSUSPEND 1", s.undo[0].command)

    def test_nic_probes_read_back(self):
        import maintenance_utils as network
        from system_core import Verdict
        inv = self._inv()
        self.assertIs(network._power_probe(inv).verdict, Verdict.PROBLEM)
        self.assertIs(network._moderation_probe(inv).verdict, Verdict.PROBLEM)
        inv.primary_nic.allow_turn_off = False
        inv.primary_nic.interrupt_moderation = False
        self.assertIs(network._power_probe(inv).verdict, Verdict.NO_PROBLEM)
        self.assertIs(network._moderation_probe(inv).verdict, Verdict.NO_PROBLEM)
        inv.primary_nic.allow_turn_off = None
        self.assertIs(network._power_probe(inv).verdict, Verdict.UNKNOWN)

    def test_fixed_system_no_longer_planned(self):
        """The user-visible regression: after applying a fix, a re-scan must
        stop planning the same tweak."""
        import engine
        from system_core import SafetyPolicy
        from system_core import Confidence
        inv = self._inv()
        before = engine.build_plan(inv, policy=SafetyPolicy(
            min_confidence=Confidence.LOW))
        self.assertIn("input.usb.selective_suspend_off", before.actionable_ids)
        self.assertIn("nic.power_saving.disable", before.actionable_ids)
        self.assertIn("nic.interrupt_moderation.disable", before.actionable_ids)
        fixed = self._inv(usb_selective_suspend=False)
        fixed.primary_nic.allow_turn_off = False
        fixed.primary_nic.interrupt_moderation = False
        fixed.game_dvr_app_capture = 0
        fixed.game_dvr_enabled = 0
        after = engine.build_plan(fixed, policy=SafetyPolicy(
            min_confidence=Confidence.LOW))
        for tid in ("input.usb.selective_suspend_off", "nic.power_saving.disable",
                    "nic.interrupt_moderation.disable", "capture.game_dvr.disable"):
            self.assertNotIn(tid, after.actionable_ids,
                             "%s still planned after fix" % tid)

    def test_apply_script_defines_isadmin(self):
        """Regression #16: the preamble used $script:IsAdmin before defining it,
        so every run claimed admin was missing and manual non-elevated runs
        died on the first HKLM step."""
        import engine
        from system_core import SafetyPolicy
        from system_core import Confidence
        inv = self._inv()
        res = engine.build_plan(inv, policy=SafetyPolicy(
            min_confidence=Confidence.LOW))
        bundle = engine.render(res, generated_at="t", brand="SnappyAI")
        text = bundle.apply_ps1
        self.assertIn("$script:IsAdmin = ([Security.Principal.WindowsPrincipal]",
                      text)
        defpos = text.index("$script:IsAdmin = ")
        usepos = text.index("-not $script:IsAdmin")
        self.assertLess(defpos, usepos)

    def test_powercfg_step_renders_and_passes_policy(self):
        import maintenance_utils as host
        from system_core import SafetyPolicy
        from engine import _step_apply_block
        steps = host._usb_plan(None)
        self.assertIn("powercfg", _step_apply_block(steps[0]))
        scan = SafetyPolicy().check_plan(None, steps)
        self.assertTrue(scan.allowed, scan.reason)




class TestDualGpuLaptop(unittest.TestCase):
    """Field report: a laptop with Intel UHD 630 (iGPU, listed first by WMI)
    + GTX 1050 (dGPU, renders the games) had the low-latency tweak flagged
    against the INTEL adapter, and HAGS reported UNKNOWN ('could not be
    read') although Pascal GPUs do not support it at all."""

    def _laptop(self):
        from system_core import (CPU, DNS, GPU, NIC, Display, Inventory,
                                 OSFamily, Power, Timer, Vendor)
        return Inventory(
            os_name="Microsoft Windows 11 Pro", os_family=OSFamily.WINDOWS,
            windows_build=26200, is_elevated=True,
            nics=[NIC(interface_description="Intel(R) Wireless-AC 9462",
                      name="Wi-Fi", physical="wireless", status="Up",
                      mtu=1500)],
            gpus=[
                GPU(name="Intel(R) UHD Graphics 630", vendor=Vendor.INTEL,
                    driver_version="31.0.101.2115", hags=None),
                GPU(name="NVIDIA GeForce GTX 1050", vendor=Vendor.NVIDIA,
                    driver_version="551.23", hags=None),
            ],
            displays=[Display(name="Intel(R) UHD Graphics 630",
                              resolution="1920x1080",
                              current_refresh_hz=60.0, max_refresh_hz=60.0)],
            cpu=CPU(name="Intel(R) Core(TM) i7-8750H CPU @ 2.20GHz",
                    logical_processors=12, l3_domains=1),
            power=Power(active_scheme_name="Balanced"),
            dns=DNS(server_addresses=["192.168.1.1"], resolve_ms=12.0),
            timer=Timer(current_period_us=1000.0, mmcss_responsiveness="High"),
            foreground_process="game.exe",
            usb_selective_suspend=False,
        )

    def test_primary_gpu_prefers_discrete(self):
        inv = self._laptop()
        self.assertEqual(inv.primary_gpu.name, "NVIDIA GeForce GTX 1050")
        self.assertTrue(inv.uses_wifi_for_primary)

    def test_ranking_variants(self):
        from system_core import GPU, Inventory, Vendor
        def prim(*gpus):
            return Inventory(gpus=list(gpus)).primary_gpu
        intel = GPU(name="Intel(R) UHD Graphics 770", vendor=Vendor.INTEL)
        arc = GPU(name="Intel(R) Arc(TM) A770 Graphics", vendor=Vendor.INTEL)
        amd_igpu = GPU(name="AMD Radeon(TM) Graphics", vendor=Vendor.AMD)
        rx = GPU(name="AMD Radeon RX 6600M", vendor=Vendor.AMD)
        vega_igpu = GPU(name="Radeon Vega 8 Graphics", vendor=Vendor.AMD)
        self.assertEqual(prim(intel, arc).name, arc.name)
        self.assertEqual(prim(amd_igpu, rx).name, rx.name)
        self.assertEqual(prim(vega_igpu, rx).name, rx.name)
        self.assertEqual(prim(intel).name, intel.name)       # single iGPU kept
        self.assertEqual(prim(amd_igpu).name, amd_igpu.name)
        self.assertEqual(prim(rx, intel).name, rx.name)      # order-independent

    def test_low_latency_probe_names_the_discrete_gpu(self):
        import input_utils as iu
        f = iu._low_latency_probe(self._laptop())
        self.assertEqual(f.measured["gpu"], "NVIDIA GeForce GTX 1050")

    def test_hags_unsupported_is_not_applicable(self):
        import input_utils as iu
        from system_core import Verdict
        f = iu._hags_probe(self._laptop())
        self.assertIs(f.verdict, Verdict.NOT_APPLICABLE)
        self.assertIn("does not offer", f.summary)
        # a readable state stays an A/B suggestion
        inv = self._laptop()
        inv.primary_gpu.hags = True
        self.assertIs(iu._hags_probe(inv).verdict, Verdict.NO_PROBLEM)

    def test_plan_targets_the_right_gpu_end_to_end(self):
        import engine
        from system_core import Confidence, SafetyPolicy, Verdict
        inv = self._laptop()
        res = engine.build_plan(inv, policy=SafetyPolicy(
            min_confidence=Confidence.LOW))
        by_id = {o.tweak.id: o for o in res.outcomes}
        ll = by_id["gpu.vendor.low_latency_mode"]
        self.assertEqual(ll.measured.get("gpu"), "NVIDIA GeForce GTX 1050")
        hags = by_id["gpu.hags.ab_test"]
        self.assertIs(hags.verdict, Verdict.NOT_APPLICABLE)
        self.assertNotIn("gpu.hags.ab_test", res.actionable_ids)
        wifi = by_id["net.wifi.prefer_wired"]
        self.assertIs(wifi.verdict, Verdict.PROBLEM)   # user IS on wifi
        usb = by_id["input.usb.selective_suspend_off"]
        self.assertIs(usb.verdict, Verdict.NO_PROBLEM)  # already disabled


if __name__ == "__main__":
    unittest.main(verbosity=2)
