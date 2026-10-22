# Historical pre-discovery hardware notes — superseded by live reports

## Status: PARTIAL — photographs available; ADB discovery blocked

Discovery attempted on 2026-10-21. Repeated `adb devices -l` checks returned an
empty device list, not an `unauthorized`, `offline`, or permissions-error entry.
`lsusb` showed root hubs and the laptop's camera, Bluetooth and fingerprint
devices; no identifiable head unit was present. This does not exclude a network
ADB connection, but no address was supplied or contacted.

Host ADB: `/usr/bin/adb`, Android Debug Bridge 1.0.41,
package version `37.0.0-android-tools`. Starting ADB started its host daemon;
no agent-issued device-side commands have run. See the user-side changes below.

## Network ADB follow-up

The user requested network ADB and reports both devices are on `<your-ssid>`.
Host inspection confirms the laptop is connected to `<your-ssid>` on `wlp4s0`,
with IPv4 address `<laptop-ip>/24`. The head unit's address and listening ADB
port remain unknown; no network connection attempt or subnet scan has run.
`adb mdns services` reports that mDNS is unsupported by this installed ADB build,
so automatic ADB service discovery is unavailable through that command.
Same-SSID membership does not prove peer reachability or that an ADB listener
is enabled. Obtain the head unit's IP and any displayed ADB port before trying
a targeted connection. The agent has not changed debugging or USB mode settings.

### User-side Termux and ADB changes

The user subsequently installed Termux and supplied a photograph showing:

```sh
/system/bin/setprop service.adb.tcp.port 5555
/system/bin/setprop ctl.restart adbd
```

No errors are visible immediately after those two commands in the photograph,
but this does not verify a listening socket or usable ADB connection. A later
`setprop` invocation with only the property name failed with `Need 2 arguments`;
that incomplete invocation does not demonstrate that the preceding write
failed. The final `getprop service.adb.tcp.port` result is not clearly visible.
Root and effective privileges remain unknown. The user reports port 5555 is
configured; a fresh host `adb devices -l` still has no entries, as no connection
to the head unit's still-unknown IP has been attempted. The laptop remains at
`<laptop-ip>/24`. Obtain the head-unit IP from its Wi-Fi details, then attempt
only that endpoint. Do not issue additional property writes or restarts.

| Item | User-supplied description | Device verification |
| --- | --- | --- |
| Platform | TOPWAY / Allwinner T3L | Pending |
| RAM | Approximately 1 GB | Pending |
| Storage | Approximately 16 GB | Pending |
| MCU | STM32 | Pending |
| Firmware | V8.1.1_20220823_094651_THEME1 | Pending |
| Android release / API | UI says 10; build text says 8.1.0 | Conflicting screen claims; API pending |
| Kernel / CPU / ABI / GPU | Not verified | Pending |
| Display resolution / density | Not verified | Pending |
| Partition sizes / free space | Not verified | Pending |
| Existing root | Unknown | Pending |

## Photograph evidence supplied by user

These are screen-reported values, not independently verified hardware or
runtime measurements. Photographs were supplied in chat; no image files have
been copied into this report directory.

- Android version displayed: `10`.
- Build number: `t3_p1-eng 8.1.0 OPM1.171019.026 20220823-094543 test-keys`.
- Kernel displayed: `4.9.56`, `#1137 Tue Aug 23 09:44:45 CST 2022`.
- MCU displayed on About Device: `T3L.3.19-296-10-A49305-200715(STM32)`.
- MCU detail dialog: `VW(T3L.3.19, PT2313, QN8035, STM32,296)`.
- System version displayed: `V8.1.1_20220823.094651_THEME1` (a period separates
  date and time on screen; the initial user description used an underscore).
- Memory: `Avg 732 MB of 1.0GB memory used`.
- Storage: `34% used - 10.57 GB free`.

The Android 10 label conflicts with the Android 8.1.0 build text. A vendor UI
label or a stale/custom build string can be misleading; neither establishes
the actual framework/API level. Read SDK properties and corroborate with
runtime evidence before selecting launcher APIs. API 27 corresponds to Android
8.1; API 29 corresponds to Android 10. `test-keys` and `eng` in a build string
do not prove working root access.

Both candidate Android versions meet Termux's Android 7+ fully supported
baseline. The user has now installed Termux independently. A local terminal
normally runs under its own app UID; installation alone does not grant root or
ADB shell privileges. Any vendor-specific privilege differences remain to be
verified. These local commands only read properties:

```sh
/system/bin/getprop ro.build.version.sdk
/system/bin/getprop ro.build.version.release
/system/bin/getprop ro.product.cpu.abilist
```

## Read-only checks after connection

- Record the selected serial and build identity before every discovery session.
- Read build properties, Android SDK level, kernel, `/proc/cpuinfo`,
  `/proc/meminfo`, mount information and filesystem capacity.
- Read display and graphics diagnostics; distinguish physical resolution from
  overrides. Treat vendor-reported identity as a claim, not independent proof.
- Check shell `id`, adbd properties and visible `su` paths. A `su` binary alone
  does not establish working root. Do not run `adb root` or invoke `su` during
  this initial passive check.
- Record permission denials and unsupported commands as unknowns, not absence.

Use a known USB device/OTG connection with a data-capable cable, or supply an
already configured network ADB endpoint. Do not use an unverified USB-A-to-A
connection between two powered host ports. Enabling debugging or changing USB
mode requires approval because it changes device configuration.
