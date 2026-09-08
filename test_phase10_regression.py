"""Regression checks for Phase 10 production-readiness helpers and UI contracts."""
from pathlib import Path
import unittest

from axishell_runtime import APP_RELEASE, APP_VERSION, SUPPORT_BOUNDARIES, build_operational_snapshot


APP_PATH = Path(__file__).with_name("Uniexcel.py")


class Phase10RegressionTests(unittest.TestCase):
    def test_operational_snapshot_is_session_safe_and_bounded(self):
        snapshot = build_operational_snapshot(-4, None, -2, -1, -3, True)
        self.assertEqual(snapshot[0]["Status"], "Awaiting data")
        self.assertIn("Focus Mode", snapshot[0]["Detail"])
        self.assertIn("0 rows", snapshot[1]["Status"])
        self.assertIn("Session-only", snapshot[3]["Status"])

    def test_operational_snapshot_reports_loaded_scope(self):
        snapshot = build_operational_snapshot(120, 8, 2, 1, 3.2, False)
        self.assertEqual(snapshot[0]["Status"], "Ready")
        self.assertIn("120 rows", snapshot[1]["Status"])
        self.assertIn("2 source table", snapshot[1]["Detail"])

    def test_support_boundary_and_release_metadata_are_present(self):
        self.assertEqual(APP_RELEASE, "Phase 10")
        self.assertRegex(APP_VERSION, r"^\d+\.\d+\.\d+$")
        self.assertGreaterEqual(len(SUPPORT_BOUNDARIES), 4)

    def test_app_exposes_focus_and_operational_accessibility_contracts(self):
        source = APP_PATH.read_text(encoding="utf-8")
        self.assertIn("Focus Mode", source)
        self.assertIn("Operational Status & Support Boundary", source)
        self.assertIn(":focus-visible", source)
        self.assertIn("prefers-reduced-motion", source)


if __name__ == "__main__":
    unittest.main()
