#!/usr/bin/env python3
"""Explicit, logged launcher-only stages. Never change standby/vehicle settings."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
FACTORY = 'com.dofun.variety/com.dofun.overseasvariety.Launcher'
NEW_HOME = 'local.t3l.launcher/.MainActivity'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial', required=True)
    parser.add_argument('stage', choices=['install', 'verify-stock-enable', 'activate', 'disable-stock', 'restore'])
    args = parser.parse_args()
    os.umask(0o077)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    log = ROOT.parent / 'changes' / stamp
    log.mkdir(parents=True, mode=0o700)
    records = []
    adb = ['adb', '-s', args.serial]

    def run(arguments, timeout=25):
        record = {'command': [*adb, *arguments], 'status': 'running'}
        records.append(record)
        (log / 'operations.json').write_text(json.dumps(records, indent=2) + '\n')
        try:
            result = subprocess.run([*adb, *arguments], capture_output=True,
                                    text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            record['status'] = 'timeout'
            (log / 'operations.json').write_text(json.dumps(records, indent=2) + '\n')
            raise
        record.update(status=result.returncode, stdout=result.stdout, stderr=result.stderr)
        (log / 'operations.json').write_text(json.dumps(records, indent=2) + '\n')
        print(result.stdout + result.stderr, flush=True)
        if result.returncode or 'Error:' in result.stdout or 'Exception' in result.stderr:
            raise RuntimeError('ADB operation failed; see ' + str(log))
        return result.stdout

    sdk = run(['shell', 'getprop', 'ro.build.version.sdk']).strip()
    firmware = run(['shell', 'getprop', 'ro.tw.version']).strip()
    if sdk != '27' or firmware != 'V8.1.1_20220823.094651_THEME1':
        raise RuntimeError('Device identity does not match reviewed unit')
    before = {name: run(['shell', 'settings', 'get', namespace, key]).strip()
              for name, namespace, key in [
                  ('sleep_timeout', 'secure', 'sleep_timeout'),
                  ('screen_off_timeout', 'system', 'screen_off_timeout'),
                  ('wifi_sleep_policy', 'global', 'wifi_sleep_policy')]}
    (log / 'standby-before.json').write_text(json.dumps(before, indent=2) + '\n')

    if args.stage == 'install':
        installed = run(['shell', 'pm', 'list', 'packages', 'local.t3l.launcher'])
        if 'package:local.t3l.launcher' in installed:
            raise RuntimeError('Package already installed; inspect before replacing it')
        build = json.loads((ROOT / 'build/latest.json').read_text())
        apk = Path(build['apk'])
        if hashlib.sha256(apk.read_bytes()).hexdigest() != build['sha256']:
            raise RuntimeError('APK integrity mismatch')
        run(['install', str(apk)], timeout=60)
        run(['shell', 'am', 'start', '-W', '-n', NEW_HOME])
    elif args.stage == 'verify-stock-enable':
        # This firmware's shell cannot reset arbitrary component state to 0.
        # Functional rollback uses explicit enabled=1 rather than original
        # default=0. Both enable this manifest-enabled factory package.
        result = run(['shell', 'pm', 'enable', '--user', '0', 'com.dofun.variety'])
        if 'enabled' not in result:
            raise RuntimeError('Stock re-enable path not verified')
        (ROOT.parent / '.private/stock-reenable-verified.json').write_text(json.dumps({
            'serial': args.serial, 'firmware': firmware, 'log': str(log),
            'original_package_state': 0, 'functional_restore_state': 1,
            'exact_default_state_restore_available': False,
        }, indent=2) + '\n')
    elif args.stage == 'activate':
        # Exercise restoration while stock HOME is still enabled.
        run(['shell', 'cmd', 'package', 'set-home-activity', '--user', '0', FACTORY])
        resolved = run(['shell', 'cmd', 'package', 'resolve-activity', '--brief',
                        '-a', 'android.intent.action.MAIN', '-c', 'android.intent.category.HOME'])
        if FACTORY not in resolved:
            raise RuntimeError('Original HOME restoration did not resolve as expected')
        try:
            run(['shell', 'cmd', 'package', 'set-home-activity', '--user', '0', NEW_HOME])
            run(['shell', 'am', 'start', '-W', '-a', 'android.intent.action.MAIN',
                 '-c', 'android.intent.category.HOME'])
            resolved = run(['shell', 'cmd', 'package', 'resolve-activity', '--brief',
                            '-a', 'android.intent.action.MAIN', '-c', 'android.intent.category.HOME'])
            if 'local.t3l.launcher/' not in resolved:
                raise RuntimeError('New HOME did not resolve')
        except Exception:
            run(['shell', 'cmd', 'package', 'set-home-activity', '--user', '0', FACTORY])
            raise
    elif args.stage == 'disable-stock':
        verified = json.loads((ROOT.parent / '.private/stock-reenable-verified.json').read_text())
        if verified['serial'] != args.serial or verified['firmware'] != firmware:
            raise RuntimeError('Re-enable verification belongs to another device')
        resolved = run(['shell', 'cmd', 'package', 'resolve-activity', '--brief',
                        '-a', 'android.intent.action.MAIN', '-c', 'android.intent.category.HOME'])
        if 'local.t3l.launcher/' not in resolved:
            raise RuntimeError('Refusing to disable stock before new HOME is default')
        try:
            result = run(['shell', 'pm', 'disable-user', '--user', '0', 'com.dofun.variety'])
            if 'disabled-user' not in result:
                raise RuntimeError('Stock disable state was not confirmed')
            run(['shell', 'am', 'start', '-W', '-a', 'android.intent.action.MAIN',
                 '-c', 'android.intent.category.HOME'])
        except Exception:
            run(['shell', 'pm', 'enable', '--user', '0', 'com.dofun.variety'])
            run(['shell', 'cmd', 'package', 'set-home-activity', '--user', '0', FACTORY])
            raise
    else:
        installed = run(['shell', 'pm', 'list', 'packages', '--user', '0', 'com.dofun.variety'])
        if 'package:com.dofun.variety' not in installed:
            # The owner later requested user-0 uninstall. Enable alone cannot
            # restore an uninstalled package. This restores app availability,
            # not the user data removed by uninstall.
            run(['shell', 'pm', 'install-existing', '--user', '0', 'com.dofun.variety'])
        run(['shell', 'pm', 'enable', '--user', '0', 'com.dofun.variety'])
        run(['shell', 'cmd', 'package', 'set-home-activity', '--user', '0', FACTORY])
        run(['shell', 'am', 'start', '-W', '-n', FACTORY])
        # Keep our APK/data in place; removal requires a deliberate later step.

    after = {name: run(['shell', 'settings', 'get', namespace, key]).strip()
             for name, namespace, key in [
                 ('sleep_timeout', 'secure', 'sleep_timeout'),
                 ('screen_off_timeout', 'system', 'screen_off_timeout'),
                 ('wifi_sleep_policy', 'global', 'wifi_sleep_policy')]}
    (log / 'standby-after.json').write_text(json.dumps(after, indent=2) + '\n')
    if before != after:
        raise RuntimeError('Unexpected standby difference: inspect without writing settings')
    print('Completed ' + args.stage + '; standby settings unchanged. Log: ' + str(log))


if __name__ == '__main__':
    main()
