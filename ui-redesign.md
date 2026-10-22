# T3L Drive — reference dashboard redesign

## Phase A: inspected baseline

This is an in-place update to **`local.t3l.launcher`**, not a new application.
Live inspection reconfirmed Android SDK **27**, physical **1024×600**, **160 dpi**.
The existing 0.1.1 APK, Java source, manifest, HOME, three settings namespaces,
memory/status diagnostics and screenshot were backed up in
`changes/20261021T074820.653622Z-ui-redesign/` before changes.

| Tile | Preserved destination |
| --- | --- |
| Android Auto | `gb.xxy.hr/.activities.DispatcherActivity` (Headunit Reloaded) |
| Radio | `com.tw.radio/.RadioActivity` |
| Music | `com.tw.music/.MusicActivity` |
| Bluetooth | `com.tw.bt/.ATBluetoothActivity` |
| Apps | Existing native sorted app picker; no external package |
| Settings | `com.android.settings/.Settings` |
| EQ / Audio | `com.tw.eq/.EQActivity` |

The hero never launches Google Maps. Theme was previously uninstalled for user
0 by the owner; this update must not reinstall it. Settings, a Help / Recovery
entry and the previous APK rollback remain accessible. The factory destination
is retained as a conditional recovery option only if the owner later restores
it; otherwise it explains the existing laptop recovery procedure.

## Phase B: native design

Charcoal `#15191F`, cards `#242A33`, cyan `#27C8E8`, text `#F5F7FA`, secondary
`#9EAABA`, 15dp corners, subtle 1dp borders, no shadows or animations. A weighted
39:61 main layout contains a two-row Android Auto hero, static vector mountains/
road/projection arrow, four equal right cards and two full-width utility cards.
Compact sizing adapts to smaller landscape configurations; no resolution override
or scrolling. Native window insets retain the head unit's system controls.

The header shows actual Android-adapter Bluetooth and Wi-Fi association state.
Bluetooth currently reports OFF in Android; the vendor MCU Bluetooth app uses a
separate stack. The icon does not invent a vendor connection state. Tapping a
status icon explains its observed state without toggling anything.

Only normal read-only `BLUETOOTH` and `ACCESS_WIFI_STATE` permissions are added.
No Bluetooth-admin, location, Internet, privileged permissions or runtime grants.

## Clock/lifecycle

Device-local time: `h:mm a`; date: `dd/ MMMM /yyyy`, both `Locale.ENGLISH`.
Formatters are reused. System `TIME_TICK` provides minute-boundary updates only
while a dynamically registered Activity receiver is active. Resume refreshes
immediately; time-set, timezone and date broadcasts refresh values. Pause and
destroy unregister the receiver. No timer, scheduled service or background
clock callback is introduced.

## 0.2.1 bugfix (2026-10-21)

- Removed the launcher's own header row (T3L DRIVE brand, in-app Bluetooth
  and Wi-Fi icons, in-app clock): the head unit's native system bar already
  provides navigation, Bluetooth, Wi-Fi and the clock, so the row was
  duplicated. Content now starts at y≈72 in the launcher, giving each main
  card ~208dp height. Help/recovery remains reachable from the Apps drawer
  ("HELP / RECOVERY"), and the About dialog now reports the observed
  Android Bluetooth/Wi-Fi state in text. The header's tap targets
  (`help`, `bluetooth-status`, `wifi-status`) no longer exist; the state
  strings are still refreshed passively for diagnostics (`T3L_STATUS`).
- Hero date format changed from `dd/ MMMM /yyyy` to `dd MMMM yyyy`, e.g.
  `21 October 2026`, on-device verified, no slashes.
- Built, installed and verified on the unit (versionCode 4, sha256
  8238ffe4…): no launcher crash lines, no clipped labels, Android Auto tap
  rechecked (`gb.xxy.hr` gains focus). Screenshot:
  `changes/0.2.1-final.png`.

## Validation and deployment (2026-10-21, all on device <unit-ip>:5555)

Session artifacts: `changes/20261021T074820.653622Z-ui-redesign/`
(`inspection.json`, `redesign-operations.json`, `rollback-test.json`,
`tile-tests.json`, `tile-results.json`, plus screenshots).

- Build: 0.2.0 (versionCode 3), 29,874 bytes, v2+v3 signed with the preserved
  local RSA key; same-key update over the working 0.1.1 install.
- Rollback proven: `pm install -r -d` returned the device to 0.1.1
  (versionName verified in `dumpsys package`), HOME still resolved, then 0.2.0
  was re-applied. No uninstall at any point. First streamed-install attempt
  failed on a flaky Wi-Fi ADB link; the push + `pm install` path is the
  reliable fallback.
- All tiles pass actual `input tap` tests at measured bounds: auto →
  `gb.xxy.hr/.activities.MainActivity`, radio → `com.tw.radio`,
  music → `com.tw.music`, bluetooth → `com.tw.bt`, settings →
  `com.android.settings`, EQ → `com.tw.eq/.eq.activity.PT2313Activity`
  (factory equalizer), apps → sorted installed-apps dialog with
  Help/Recovery. Status icon taps stay on the launcher and only explain
  state. Zero launcher lines in the crash buffer.
- Clock: verified live; hero showed `4:17 PM` / `21/ October /2026`
  matching `date`. A clean no-interaction session with the launcher visible
  across a minute boundary incremented `clockRefreshes` by exactly 1
  (`time_tick_clean` in `tile-results.json`), proving system TIME_TICK
  delivery with the receiver registered only while visible.
  Note: `dumpsys activity <activity>` can briefly serve stale lifecycle
  lines after a process restart — re-check the foreground record before
  concluding a receiver failed.
- Memory/idle: TOTAL PSS 10,051 KB, Java heap 2.4 MB, 59 views, 1 Activity,
  AppContexts 3, WebViews 0, no SQL. Earlier pass: 10,447 KB total, 0
  WebViews. `layout-final` shows every touch target ≥ 48dp and no clipped
  labels at 1024×600 (content height 540 under the system bars).
- HOME remains `local.t3l.launcher/.MainActivity`; permissions granted are
  read-only install-time `BLUETOOTH` and `ACCESS_WIFI_STATE`; no runtime
  prompts, no background services, no network calls.
- Owner device is on the UI 0.2.0 build. Physical verification still
  required by the owner while parked: AA projection on the phone, FM audio
  via speakers, Bluetooth calls, reverse camera, steering controls. None
  of these were altered; involves no MCU/CAN/power changes.
