#!/usr/bin/env python3
"""User-requested Theme removal for user 0 only. Never remount/modify system."""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
TARGET = 'com.dofun.variety'


def own_package_block(text, package):
    match = re.search(r'^  Package \[' + re.escape(package)
                      + r'\].*?(?=^  Package \[|^Package Changes:|^Hidden system packages:|\Z)',
                      text, re.M | re.S)
    if not match:
        raise ValueError('Missing package block: ' + package)
    return match.group()


def settings_changes(before, after):
    def values(text):
        return dict(line.split('=', 1) for line in text.splitlines() if '=' in line)
    old, new = values(before), values(after)
    return {key: (old.get(key), new.get(key)) for key in old.keys() | new.keys()
            if old.get(key) != new.get(key)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial', required=True)
    args = parser.parse_args()
    os.umask(0o077)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    folder = ROOT / 'changes' / stamp
    folder.mkdir(parents=True)
    records = []

    def run(label, arguments, timeout=25):
        command = ['adb', '-s', args.serial, *arguments]
        record = {'label': label, 'command': command, 'status': 'running'}
        records.append(record)
        journal = folder / 'operations.json'
        journal.write_text(json.dumps(records, indent=2) + '\n')
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            record['status'] = 'timeout'
            journal.write_text(json.dumps(records, indent=2) + '\n')
            raise
        record.update(status=result.returncode, stdout=result.stdout, stderr=result.stderr)
        journal.write_text(json.dumps(records, indent=2) + '\n')
        (folder / (label + '.txt')).write_text(result.stdout + result.stderr)
        if result.returncode or 'Error:' in result.stdout:
            raise RuntimeError(label + ' failed: ' + result.stdout + result.stderr)
        return result.stdout

    print('Journal: ' + str(folder), flush=True)
    firmware = run('firmware', ['shell', 'getprop', 'ro.tw.version']).strip()
    if firmware != 'V8.1.1_20220823.094651_THEME1':
        raise RuntimeError('Wrong device firmware')
    if run('active-user', ['shell', 'am', 'get-current-user']).strip() != '0':
        raise RuntimeError('Active user is not the reviewed user 0')
    home_query = ['shell', 'cmd', 'package', 'resolve-activity', '--brief',
                  '-a', 'android.intent.action.MAIN', '-c', 'android.intent.category.HOME']
    if 'local.t3l.launcher/' not in run('home-before', home_query):
        raise RuntimeError('Refusing to remove stock without our launcher as HOME')
    theme = run('theme-before', ['shell', 'dumpsys', 'package', TARGET])
    active_theme = own_package_block(theme, TARGET)
    if not re.search(r'^    User 0:.* installed=true\b', active_theme, re.M) or 'versionCode=350 ' not in active_theme:
        raise RuntimeError('Theme state/version differs from reviewed installation')
    hur_before = run('hur-before', ['shell', 'dumpsys', 'package', 'gb.xxy.hr'])
    for namespace in ['system', 'secure', 'global']:
        run('settings-' + namespace + '-before', ['shell', 'settings', 'list', namespace])
    run('native-before', ['shell', 'dumpsys', 'package', 'local.t3l.launcher'])

    # Explicit user scope; deliberately no -k because the owner requested
    # removal including this app's user data. No all-user/system uninstall.
    result = run('uninstall-theme-user-0',
                 ['shell', 'pm', 'uninstall', '--user', '0', TARGET], timeout=60)
    if result.strip() != 'Success':
        raise RuntimeError('Package manager did not confirm removal: ' + result)
    print('Theme uninstall for user 0: Success', flush=True)

    listed = run('theme-installed-after', ['shell', 'pm', 'list', 'packages', '--user', '0', TARGET])
    if 'package:' + TARGET in listed:
        raise RuntimeError('Theme still installed for user 0')
    run('theme-known-after', ['shell', 'pm', 'list', 'packages', '-u', TARGET])
    run('theme-details-after', ['shell', 'dumpsys', 'package', TARGET])
    if 'local.t3l.launcher/' not in run('home-after', home_query):
        raise RuntimeError('Unexpected HOME change')
    hur_after = run('hur-after', ['shell', 'dumpsys', 'package', 'gb.xxy.hr'])
    # A targeted dumpsys also contains the global package-change sequence.
    # Compare HUR's own block, not global counters changed by Theme removal.
    if own_package_block(hur_before, 'gb.xxy.hr') != own_package_block(hur_after, 'gb.xxy.hr'):
        raise RuntimeError('HUR package snapshot unexpectedly changed; inspect without altering it')
    for namespace in ['system', 'secure', 'global']:
        after = run('settings-' + namespace + '-after', ['shell', 'settings', 'list', namespace])
        before = (folder / ('settings-' + namespace + '-before.txt')).read_text()
        differences = settings_changes(before, after)
        if namespace == 'secure' and set(differences) == {'enabled_notification_listeners'}:
            old, new = differences['enabled_notification_listeners']
            expected = ':'.join(item for item in (old or '').split(':')
                                if item and not item.startswith(TARGET + '/'))
            if new == expected:
                differences = {}  # Android's expected uninstall cleanup.
        if differences:
            raise RuntimeError('Settings difference in ' + namespace + '; inspect without writes')
    run('home-launch-after', ['shell', 'am', 'start', '-W', '-a', 'android.intent.action.MAIN',
                              '-c', 'android.intent.category.HOME'])
    print('Verified: Theme absent for user 0; new HOME, HUR and settings preserved.')
    print('Factory system-image copy is NOT erased. App data was not backed up.')


if __name__ == '__main__':
    main()
