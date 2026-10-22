"""Offline verification of captured deployment; never issues ADB operations."""
import csv
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent
BEFORE = ROOT / 'evidence/20261021T065540.654594Z'
AFTER = ROOT / 'evidence/20261021T071105.510400Z'


def package_block(path, name):
    text = (path / 'package-details.txt').read_text().split('Hidden system packages:')[0]
    return re.search(r'^  Package \[' + re.escape(name) + r'\].*?(?=^  Package \[|\Z)',
                     text, re.M | re.S).group()


class AppliedOptimizationChecks(unittest.TestCase):
    def test_new_home_and_stock_disabled(self):
        self.assertIn('local.t3l.launcher/.MainActivity', (AFTER / 'default-home.txt').read_text())
        disabled = set((AFTER / 'packages-disabled.txt').read_text().splitlines())
        original = set((BEFORE / 'packages-disabled.txt').read_text().splitlines())
        self.assertEqual(disabled - original, {'package:com.dofun.variety'})
        self.assertEqual(original - disabled, set())
        self.assertNotIn('com.dofun.variety', (AFTER / 'processes.txt').read_text())

    def test_settings_snapshots_identical(self):
        for namespace in ['system', 'secure', 'global']:
            name = 'settings-' + namespace + '.txt'
            self.assertEqual((BEFORE / name).read_bytes(), (AFTER / name).read_bytes())

    def test_hur_and_protected_packages_unchanged(self):
        for name in ['gb.xxy.hr', 'com.android.chrome', 'com.tw.service',
                     'com.tw.radio', 'com.tw.bt', 'com.tw.eq', 'com.tw.core']:
            before = package_block(BEFORE, name)
            after = package_block(AFTER, name)
            for pattern in [r'^    userId=.*$', r'^    versionCode=.*$',
                            r'^    versionName=.*$', r'^    codePath=.*$',
                            r'^    User 0:.*$']:
                self.assertEqual(re.search(pattern, before, re.M).group(),
                                 re.search(pattern, after, re.M).group(), (name, pattern))
        services = (AFTER / 'activity-services.txt').read_text()
        for component in ['com.tw.service/.TWService', 'com.tw.bt/.ATBluetoothService',
                          'com.tw.eq/.EQService', 'com.tw.core/.model.MainService']:
            self.assertIn(component, services)

    def test_build_matches_current_sources(self):
        build = json.loads((ROOT / 'launcher-proposal/build/latest.json').read_text())
        apk = Path(build['apk'])
        self.assertEqual(hashlib.sha256(apk.read_bytes()).hexdigest(), build['sha256'])
        self.assertLess(apk.stat().st_size, 1024 * 1024)
        for relative, digest in build['sources_sha256'].items():
            path = ROOT / 'launcher-proposal' / relative
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)

    def test_post_inventory_and_on_screen_recovery_route(self):
        with (ROOT / 'package-inventory-after.csv').open() as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 76)
        records = {row['package']: row for row in rows}
        self.assertEqual(records['com.dofun.variety']['enabled_state_user_0'], '3')
        self.assertEqual(records['gb.xxy.hr']['enabled_state_user_0'], '0')
        route = (ROOT / 'changes/20261021T071023.228868Z/recovery-activity.txt').read_text()
        self.assertIn('launchedFromUid=10050 launchedFromPackage=local.t3l.launcher', route)
        self.assertIn('dat=package:com.dofun.variety', route)


if __name__ == '__main__':
    unittest.main()
