#!/usr/bin/env python3
"""Fetch verified host-local Android tools; no system installs/device access."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import urllib.request
import zipfile

CACHE = Path('/tmp/opencode/t3l-android-tools')
ARTIFACTS = [
    ('build-tools.zip', 'https://dl.google.com/android/repository/build-tools_r35_linux.zip',
     '2cfaa0bbb2336e9ec18ed3ecea84fa2e2af607bc'),
    ('platform-27.zip', 'https://dl.google.com/android/repository/platform-27_r03.zip',
     '35f747e7e70b2d16e0e4246876be28d15ea1c353'),
    ('ecj.jar', 'https://repo.maven.apache.org/maven2/org/eclipse/jdt/ecj/3.39.0/ecj-3.39.0.jar', None),
]


def download(artifact):
    name, url, expected = artifact
    if expected is None:
        with urllib.request.urlopen(url + '.sha1', timeout=30) as response:
            expected = response.read().decode().split()[0].lower()
    destination = CACHE / name
    if not destination.exists() or hashlib.sha1(destination.read_bytes()).hexdigest() != expected:
        with urllib.request.urlopen(url, timeout=90) as response:
            data = response.read()
        if hashlib.sha1(data).hexdigest() != expected:
            raise ValueError('Upstream integrity check failed: ' + name)
        destination.write_bytes(data)
    data = destination.read_bytes()
    return {'name': name, 'url': url, 'sha1': expected,
            'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def main():
    os.umask(0o077)
    CACHE.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        records = list(pool.map(download, ARTIFACTS))
    for name, _, _ in ARTIFACTS:
        if not name.endswith('.zip'):
            continue
        root = CACHE / name.removesuffix('.zip')
        root.mkdir(exist_ok=True)
        with zipfile.ZipFile(CACHE / name) as archive:
            for entry in archive.infolist():
                target = (root / entry.filename).resolve()
                if not target.is_relative_to(root.resolve()):
                    raise ValueError('Unsafe archive path')
            archive.extractall(root)
            for entry in archive.infolist():
                target = root / entry.filename
                mode = (entry.external_attr >> 16) & 0o777
                if mode & 0o111 and target.is_file():
                    target.chmod(0o700)
    tools = {
        'build_tools': str(next((CACHE / 'build-tools').rglob('aapt2')).parent),
        'android_jar': str(next((CACHE / 'platform-27').rglob('android.jar'))),
        'ecj': str(CACHE / 'ecj.jar'),
        'artifacts': records,
    }
    (CACHE / 'tools.json').write_text(json.dumps(tools, indent=2) + '\n')
    print(json.dumps(tools, indent=2))


if __name__ == '__main__':
    main()
