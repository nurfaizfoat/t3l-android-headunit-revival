"""Offline regression/evidence checks. No ADB commands are executed."""

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence/20261021T062836.681052Z"
A = "{http://schemas.android.com/apk/res/android}"
spec = importlib.util.spec_from_file_location("apk_analysis", ROOT / "analyse-apks.py")
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


class ReportChecks(unittest.TestCase):
    def test_all_requested_reports_exist(self):
        for name in ["hardware-report.md", "memory-report.md", "package-inventory.csv",
                     "debloat-proposal.md", "startup-analysis.md", "radio-investigation.md",
                     "recovery-plan.md"]:
            self.assertTrue((ROOT / name).is_file(), name)

    def test_inventory_completeness_and_categories(self):
        with (ROOT / "package-inventory.csv").open() as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 75)
        self.assertEqual(len({row["package"] for row in rows}), 75)
        self.assertEqual(sum(row["category"] == "SAFE TO DISABLE" for row in rows), 2)
        self.assertEqual(sum(row["category"] == "REQUIRES INVESTIGATION" for row in rows), 20)
        self.assertEqual(sum(row["category"] == "CRITICAL — DO NOT TOUCH" for row in rows), 53)
        packages = {row["package"]: row for row in rows}
        for name in ["com.tw.carchoose", "com.android.vending", "com.google.android.webview"]:
            self.assertEqual(packages[name]["enabled_state_user_0"], "3")
        for name in ["com.android.chrome", "com.google.android.packageinstaller",
                     "com.tw.radio", "com.tw.service", "com.tw.bt", "com.tw.eq",
                     "com.tw.core", "com.dofun.variety"]:
            self.assertEqual(packages[name]["category"], "CRITICAL — DO NOT TOUCH")
        self.assertIn("com.tw.radio/.RadioActivity", packages["com.tw.radio"]["launch_activities"])
        self.assertIn("com.dofun.variety/com.dofun.overseasvariety.Launcher",
                      packages["com.dofun.variety"]["home_activities"])

    def test_copied_apk_integrity(self):
        records = json.loads((EVIDENCE / "apks/pull-manifest.json").read_text())
        self.assertEqual(len(records), 10)
        for record in records:
            self.assertEqual(record["exit_status"], 0)
            data = (EVIDENCE / "apks" / (record["package"] + ".apk")).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), record["sha256"])
            root = ET.parse(EVIDENCE / "apks" / (record["package"] + ".manifest.xml")).getroot()
            self.assertEqual(root.get("package"), record["package"])

    def test_radio_static_and_runtime_evidence(self):
        root = ET.parse(EVIDENCE / "apks/com.tw.radio.manifest.xml").getroot()
        app = root.find("application")
        self.assertEqual(len(app.findall("activity")), 1)
        self.assertEqual(app.find("activity").get(A + "name"), ".RadioActivity")
        self.assertEqual(app.findall("receiver"), [])
        self.assertEqual(app.findall("service"), [])
        summary = json.loads((EVIDENCE / "apks/com.tw.radio.summary.json").read_text())
        self.assertTrue(any(ref["class"] == "Landroid/tw/john/TWUtil;"
                            for ref in summary["vendor_method_references"]))
        broadcasts = (ROOT / "evidence/20261021T063500.162396Z/registered-broadcasts.txt").read_text()
        self.assertIn('Action: "com.txznet.launcher.radio.action.send"', broadcasts)

    def test_binary_xml_length_encoding(self):
        self.assertEqual(analysis.length(b"\x7f", 0, True), (127, 1))
        self.assertEqual(analysis.length(b"\x81\x23", 0, True), (291, 2))
        self.assertEqual(analysis.length(b"\x01\x80\x02\x00", 0, False), (65538, 4))

    def test_prototype_manifest_has_no_permissions_or_services(self):
        root = ET.parse(ROOT / "launcher-proposal/AndroidManifest.xml").getroot()
        self.assertEqual(root.find("uses-sdk").get(A + "minSdkVersion"), "27")
        self.assertEqual(root.findall("uses-permission"), [])
        app = root.find("application")
        self.assertEqual(app.findall("service"), [])
        self.assertEqual(app.findall("receiver"), [])
        categories = {node.get(A + "name") for node in app.iter("category")}
        self.assertIn("android.intent.category.HOME", categories)
        self.assertIn("android.intent.category.DEFAULT", categories)


if __name__ == "__main__":
    unittest.main()
