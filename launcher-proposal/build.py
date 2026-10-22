#!/usr/bin/env python3
"""Build/sign API-27 APK locally; never install or contact a device."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent


def run(arguments):
    subprocess.run([str(argument) for argument in arguments], check=True, cwd=ROOT)


def main():
    os.umask(0o077)
    tools = json.loads(Path('/tmp/opencode/t3l-android-tools/tools.json').read_text())
    bt = Path(tools['build_tools'])
    platform = Path(tools['android_jar'])
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    output = ROOT / 'build' / stamp
    classes, dex = output / 'classes', output / 'dex'
    classes.mkdir(parents=True)
    dex.mkdir()
    generated = output / 'generated'
    generated.mkdir()
    run([bt / 'aapt2', 'compile', '--dir', ROOT / 'res', '-o', output / 'resources.zip'])
    unsigned = output / 'unsigned.apk'
    run([bt / 'aapt2', 'link', '-o', unsigned, '--manifest', ROOT / 'AndroidManifest.xml',
         '--java', generated, '-I', platform, output / 'resources.zip'])
    sources = sorted((ROOT / 'src').rglob('*.java'))
    run(['java', '-jar', tools['ecj'], '-1.8', '-encoding', 'UTF-8',
         '-bootclasspath', platform, '-classpath', platform, '-d', classes,
         *sources, *sorted(generated.rglob('*.java'))])
    run([bt / 'd8', '--release', '--min-api', '27', '--lib', platform,
         '--output', dex, *sorted(classes.rglob('*.class'))])
    with zipfile.ZipFile(unsigned, 'a', compression=zipfile.ZIP_DEFLATED) as apk:
        for path in dex.glob('*.dex'):
            apk.write(path, path.name)
    aligned = output / 'aligned.apk'
    run([bt / 'zipalign', '-f', '4', unsigned, aligned])
    private = ROOT.parent / '.private'
    private.mkdir(mode=0o700, exist_ok=True)
    pem, key, cert = [private / name for name in ['launcher.pem', 'launcher.pk8', 'launcher.x509.pem']]
    if not key.exists() and not cert.exists() and not pem.exists():
        run(['openssl', 'genpkey', '-algorithm', 'RSA', '-pkeyopt', 'rsa_keygen_bits:3072', '-out', pem])
        run(['openssl', 'pkcs8', '-topk8', '-nocrypt', '-in', pem, '-outform', 'DER', '-out', key])
        run(['openssl', 'req', '-new', '-x509', '-key', pem, '-out', cert,
             '-days', '10000', '-subj', '/CN=T3L Drive local launcher/'])
        for path in [pem, key, cert]:
            path.chmod(0o600)
    if not key.exists() or not cert.exists():
        raise RuntimeError('Incomplete signing identity; preserve existing files and inspect manually')
    apk = output / 't3l-drive.apk'
    run(['java', '--enable-native-access=ALL-UNNAMED', '-jar', bt / 'lib/apksigner.jar',
         'sign', '--key', key, '--cert', cert, '--out', apk, aligned])
    run(['java', '--enable-native-access=ALL-UNNAMED', '-jar', bt / 'lib/apksigner.jar',
         'verify', '--verbose', '--print-certs', '--min-sdk-version', '27', apk])
    run([bt / 'zipalign', '-c', '4', apk])
    manifest = {
        'apk': str(apk), 'sha256': hashlib.sha256(apk.read_bytes()).hexdigest(),
        'bytes': apk.stat().st_size, 'tools': tools,
        'sources_sha256': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                           for path in [ROOT / 'AndroidManifest.xml', *sources,
                                        *sorted((ROOT / 'res').rglob('*.xml'))]},
    }
    (output / 'build-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (ROOT / 'build/latest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'apk': str(apk), 'sha256': manifest['sha256'], 'bytes': manifest['bytes']}, indent=2))


if __name__ == '__main__':
    main()
