"""Offline checks of the later user-authorised Theme uninstall."""
import csv
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
CHANGE = ROOT / 'changes/20261021T073012.783622Z'
FINAL = ROOT / 'evidence/20261021T073514.036152Z'
spec = importlib.util.spec_from_file_location('theme_removal', ROOT / 'uninstall-theme.py')
removal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(removal)


class ThemeRemovalChecks(unittest.TestCase):
    def test_removed_for_user_but_known_factory_metadata_retained(self):
        with (ROOT / 'package-inventory-current.csv').open() as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 75)
        packages = {row['package'] for row in rows}
        self.assertNotIn('com.dofun.variety', packages)
        self.assertIn('gb.xxy.hr', packages)
        self.assertIn('local.t3l.launcher', packages)
        self.assertEqual((CHANGE / 'theme-installed-after.txt').read_text().strip(), '')
        self.assertIn('package:com.dofun.variety', (CHANGE / 'theme-known-after.txt').read_text())
        block = removal.own_package_block((CHANGE / 'theme-details-after.txt').read_text(),
                                          'com.dofun.variety')
        self.assertRegex(block, r'User 0: ceDataInode=0 installed=false')

    def test_hur_and_standby_preserved_with_only_expected_listener_cleanup(self):
        before = removal.own_package_block((CHANGE / 'hur-before.txt').read_text(), 'gb.xxy.hr')
        after = removal.own_package_block((CHANGE / 'hur-after.txt').read_text(), 'gb.xxy.hr')
        self.assertEqual(before, after)
        for namespace in ['system', 'global']:
            old = (CHANGE / ('settings-' + namespace + '-before.txt')).read_text()
            new = (FINAL / ('settings-' + namespace + '.txt')).read_text()
            self.assertEqual(removal.settings_changes(old, new), {})
        old = (CHANGE / 'settings-secure-before.txt').read_text()
        new = (FINAL / 'settings-secure.txt').read_text()
        self.assertEqual(removal.settings_changes(old, new), {
            'enabled_notification_listeners':
                ('com.dofun.variety/cn.cardoor.basic.media.NotifyService', '')})

    def test_updated_launcher_default_and_installed_hash_verified(self):
        self.assertIn('local.t3l.launcher/.MainActivity', (FINAL / 'default-home.txt').read_text())
        block = removal.own_package_block((FINAL / 'package-details.txt').read_text(),
                                          'local.t3l.launcher')
        self.assertIn('versionCode=2 ', block)
        self.assertIn('versionName=0.1.1', block)
        self.assertRegex(block, r'User 0:.* installed=true')
        check = json.loads((CHANGE / 'final-installed-apk-check.json').read_text())
        build = json.loads((ROOT / 'launcher-proposal/build/latest.json').read_text())
        self.assertTrue(check['matched'])
        self.assertEqual(check['sha256'], build['sha256'])
        source = (ROOT / 'launcher-proposal/src/local/t3l/launcher/MainActivity.java').read_text()
        self.assertIn('ABOUT / HELP', source)
        self.assertNotIn('FACTORY HOME / RECOVERY', source)


if __name__ == '__main__':
    unittest.main()
