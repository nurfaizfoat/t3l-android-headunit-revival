# Applied optimisation — 2026-10-21

> **Later update:** the user subsequently requested deletion, so Theme was
> uninstalled for user 0 and its user data removed. T3L Drive is now 0.1.1, with
> About / Help replacing the factory shortcut. The disabled-state/Enable-only
> recovery instructions below are historical. See [current removal report](theme-removal.md).

## Outcome

User explicitly approved a custom launcher, removal of the chameleon/stock
launcher and standalone map functions, preservation of Headunit Reloaded and
**no change to existing ACC/cold-shutdown/standby behavior**.

- Built, signed and installed **T3L Drive 0.1.0**, package
  `local.t3l.launcher`, and selected `.MainActivity` as default HOME.
- Verified the chameleon icon belongs to **Theme / `com.dofun.variety`**.
  Disabled this package **for user 0**, not uninstalled. APK and data remain
  intact for recovery. Its foreground/background process is no longer present.
- Kept **Headunit Reloaded (`gb.xxy.hr`)** and made Android Auto the primary
  launcher tile. HUR version, enabled state and installed path are unchanged.
- No standalone Google Maps/recognisable map app was installed; both `geo:` and
  `google.navigation:` activity queries returned no handlers. **No Maps package
  was removed.** Our launcher has no map panel, location collection or map SDK.
- No Google services, GNSS/location providers, Chrome/WebView, radio, Bluetooth,
  EQ/amplifier, camera, vehicle-control packages or native services were disabled.
- No reboot, ACC cycle, standby/wake modification, root invocation, MCU/CAN
  operation, flash, data clear or uninstall was performed.

The original seven reports and `package-inventory.csv` are discovery baselines.
The current **76-package** inventory is `package-inventory-after.csv`: one new
launcher installed, no packages removed. The stock package's original critical
classification remains a warning against indiscriminate removal; this specific
user-authorised replacement is logged as an exception, not a broad debloat rule.

## Launcher implementation

Native API-27 Activity, no requested permissions, services, boot receiver,
timers, wakelocks, WebView or background polling. Six main tiles: Android Auto,
FM, Bluetooth, music, EQ and an on-demand native app picker. Settings and Factory
Home / Recovery remain available. Radio is only a shortcut to the original UI;
no private tuner protocol is used. No automatic HUR launch, hotspot or network
configuration was added.

APK: `launcher-proposal/build/20261021T070627.821153Z/t3l-drive.apk`

- Size: **16,861 bytes**.
- SHA-256: `f2bde393c2dee19d4b250b2926eb422a14f4382f90019758b8f71651af3fa04c`.
- Compiled against Android API 27; min/target 27; signed and verified with APK
  signature schemes v2/v3 and checked for alignment.
- The installed `base.apk` SHA-256 was read back and matches this exact build.
- Local signing identity is under `.private/`; keep it private and back it up
  securely for future updates. Host system Java was not changed. Build tooling
  was downloaded with upstream integrity checks to `/tmp/opencode/`.

## Observed memory comparison

Before: `evidence/20261021T065540.654594Z/`.
After: `evidence/20261021T071105.510400Z/`.

| Metric | Before | After |
| --- | ---: | ---: |
| Launcher PSS | Stock: 85,567 KiB / 83.6 MiB | Native: 7,376 KiB / 7.2 MiB |
| MemAvailable | 352,852 KiB / 344.6 MiB | 437,308 KiB / 427.1 MiB |
| SwapFree | 132,656 KiB | 167,376 KiB |
| Stock launcher process | Present | Absent |

Launcher PSS is about 76.4 MiB lower; MemAvailable rose about 82.5 MiB. These
are **uncontrolled same-session snapshots**, not guaranteed savings, a boot
benchmark or proof of the performance of navigation/audio workloads. The first
native launch returned `Status: ok`, 1097 ms Activity launch time. The captured
crash buffer contains no native-launcher crash entry. Long-term stability and
cold-boot startup have not been tested.

CPU/GPU raw readings were 94/93 before and 95/93 after. The previous thermal
warning **remains unresolved**; no governor, thermal or ZRAM tuning was applied.

## Standby and protected-state checks

All system/global/secure settings key/value pairs were identical between the
recorded before/after snapshots. Each completed deployment stage additionally
checked these values before/after:

| Setting | Unchanged value |
| --- | --- |
| `secure sleep_timeout` | `-1` |
| `system screen_off_timeout` | `2147483647` |
| `global wifi_sleep_policy` | `2` |

No standby settings were written. This preserves the configured baseline; it
does **not** measure ACC-off battery draw or prove cold shutdown. No ACC/power
cycle was requested or performed.

HUR, Chrome, radio, TW service/BT/EQ/core packages retain their original enabled
states. Core MainService/DameonService, TWService, ATBluetoothService and
EQService remain active. Removing the old launcher's client can naturally
unbind its former messaging connection; this is not proof all vehicle features
are unaffected. Physical functional checks below remain necessary.

## Recovery — no root needed

### On the head unit

Tap **Factory Home / Recovery** in T3L Drive. Because Theme is disabled, it opens
**Settings → App info → Theme**. The button route was observed as launched by
the new app UID, and the settled screen was visually verified to show
**Disabled** and **ENABLE**. No Enable/Force Stop button was pressed in this
test. The unit was returned to T3L Drive afterward.

To restore stock operation, tap **Enable**, return to T3L Drive and tap Factory
Home / Recovery again. This opens the stock UI; selecting it as default HOME is
a separate step available through the original HOME selection/ADB path.

### From this laptop

```sh
python3 launcher-proposal/deploy.py --serial <unit-ip>:5555 restore
```

The restore stage enables `com.dofun.variety`, restores its recorded HOME
component and opens it. It keeps our APK/data, so it does not delete user work.
Verify the head unit's current IP first. Individual equivalent commands:

```sh
adb -s <unit-ip>:5555 shell pm enable --user 0 com.dofun.variety
adb -s <unit-ip>:5555 shell cmd package set-home-activity --user 0 com.dofun.variety/com.dofun.overseasvariety.Launcher
adb -s <unit-ip>:5555 shell am start -n com.dofun.variety/com.dofun.overseasvariety.Launcher
```

The factory HOME setter/resolution and package-enable command were verified
before disabling stock. **Rollback is functional, not an exact metadata reset**:
original package state was default `0`; the supported re-enable path gives
explicit enabled `1`. This firmware rejected shell reset of our test component
to state `0`; no root bypass was attempted. The native app has both HOME and
LAUNCHER entries and a Settings escape path, but no launcher can guarantee
recovery if Android itself fails to boot. No firmware backup/flash is available.

## Evidence and remaining checks

Private `changes/` journals record actual commands, output and standby checks:

- `20261021T070638.159566Z`: install/start succeeded; default-state component
  check failed with SecurityException. No stock disable/HOME change at that point.
- `20261021T070940.795172Z`: supported stock enable test succeeded.
- `20261021T071004.127014Z`: factory HOME restore test and new HOME activation.
- `20261021T071023.228868Z`: stock disable, HOME success, recovery UI test,
  settled Theme Enable screenshot and final native HOME return.

**While parked, manually check:** Android Auto/HUR connection and navigation,
FM audio, Bluetooth calls/audio, EQ/amplifier output, reverse camera and
steering-wheel/vehicle controls. Software service presence is not a substitute.
Report any regression and use the recovery path. Do not change standby or
trigger ACC/reverse with broadcasts. No reboot/cold-boot or battery-draw test
has been performed; arrange such a test separately if needed.
