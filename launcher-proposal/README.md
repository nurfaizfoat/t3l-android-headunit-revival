# T3L Drive — native launcher

**Latest: 0.1.1 / code 2.** Theme was subsequently uninstalled for user 0, so
About / Help now replaces the obsolete factory-recovery footer. See
[current removal scope/recovery](../theme-removal.md). Earlier 0.1.0 details
below document the original rollout; the Enable-only on-screen route no longer
applies after uninstall. `build/latest.json` identifies the current signed APK.

**Built, signed, installed and selected as HOME with explicit user approval on
2026-10-21.** Stock chameleon/Theme was initially disabled-user, then uninstalled
for user 0 on the owner's further request; its old user data was removed.
Headunit Reloaded is preserved. No standby/power settings were changed.
See [execution report and recovery](../optimization-report.md).

## Implementation

- Single native Activity for the detected Android 8.1/API 27, ARMv7,
  1024×600@160dpi unit. Manifest min/target 27; platform-only Java classes,
  no native ABI libraries, third-party UI libraries or Gradle requirement.
- Android Auto/Headunit Reloaded is the primary tile; other tiles open factory
  radio, Bluetooth, music, EQ and a native app picker. No onboard map panel.
- No permissions, WebView, boot receiver, service, wakelock, polling or timer.
  App code does not set HOME, disable packages or change settings itself.
- Missing/disabled/nonexported targets and launch failures are guarded.
  Version 0.1.1 replaces the former factory shortcut with About / Help. Stock
  recovery now requires a deliberate reinstall for user 0; Enable alone no
  longer restores the removed app. The general Settings tile remains.
- Existing vehicle/audio services and radio protocol remain untouched. Physical
  radio/BT/HUR/camera/steering-wheel validation still needs the owner while parked.
- The single-device target SDK is not a current Play-distribution configuration.
  Broader distribution requires a current target-SDK and package-visibility review.

## Host-local build

```sh
python3 bootstrap-tools.py
python3 build.py
```

Bootstrap downloads verified Google build tools 35/API-27 platform and Eclipse
ECJ 3.39.0 into `/tmp/opencode/t3l-android-tools`. It uses the existing Java
runtime; no system Java/SDK configuration is changed. ECJ compiles against the
actual API-27 stubs. Explicit Android listeners avoid LambdaMetafactory bootstrap
requirements. D8 produces DEX; aapt2 links resources; zipalign/apksigner align,
sign and verify. No tool code is packaged in the app.

Each build gets its own `build/<timestamp>/` folder, tool/source hashes and APK
hash. `build/latest.json` identifies the newest build. Actual installed build:
`build/20261021T070627.821153Z/t3l-drive.apk`, **16,861 bytes**.
Signing files live in `../.private/`, are permission-restricted and Git-ignored.
**Back them up securely**: replacing the key prevents normal in-place updates.

## Explicit device stages

`deploy.py` requires an explicit serial, verifies reviewed API/firmware, logs
commands to private `../changes/`, and checks unchanged standby values.
It never invokes root, flashes, touches MCU/CAN, reboots or changes power settings.
Stage names include install, verify-stock-enable, activate, disable-stock and
restore. Do not rerun stages casually: they deliberately alter app/HOME state.

To restore stock HOME, after checking the current IP:

```sh
python3 deploy.py --serial <unit-ip>:5555 restore
```

Restore first uses `pm install-existing --user 0` if stock is uninstalled, then
re-enables it at explicit state 1 and selects its recorded HOME component
and opens it. This is functional recovery, not an exact reset to original
package state 0; that shell reset was denied by this firmware. It does not
uninstall our APK. It cannot recover the stock user data deliberately removed by
the later uninstall. The former on-device Enable-only recovery route is no
longer available; Theme itself was not reinstalled to validate that future path.

## Observed result and limits

Native launcher PSS: ~7.2 MiB versus stock ~83.6 MiB in same-session snapshots.
These are not controlled benchmarks. Stock process is absent after disable.
No synthetic stress, cold boot, ACC cycle or standby battery test was run;
thermal warnings remain unresolved. No direct radio-control protocol is used.

References: [Intent categories](https://developer.android.com/reference/android/content/Intent),
[activity manifest](https://developer.android.com/guide/topics/manifest/activity-element).
