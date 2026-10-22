# T3L Revival — Hardware report

> This is the discovery baseline. The user later approved launcher replacement;
> see [applied optimisation and current state](optimization-report.md). No root,
> firmware, MCU/CAN or standby changes were involved in that deployment.

## Status and evidence

Read-only ADB discovery succeeded on **2026-10-21** at
`<unit-ip>:5555`. Laptop: `<laptop-ip>/24`, SSID `<your-ssid>`.
The initial authentication error was followed by an authorised `device` state.
All agent-issued device operations were diagnostic queries or copying readable
APKs to the host. No root invocation, package changes, launches, broadcasts,
flashing, MCU/CAN commands, setting writes or reboot occurred.

Main evidence: [`evidence/20261021T062836.681052Z/`](evidence/20261021T062836.681052Z/).
Follow-ups: `20261021T063125.198278Z` and `20261021T063500.162396Z`.
Each completed run has a command/exit-status/timing manifest. Raw evidence is
private host-local data; do not publish it without redaction.

| Item | Observed result | Evidence |
| --- | --- | --- |
| Android compatibility | **Android 8.1 / API 27** | SDK property 27; `android` package versionCode 27, versionName 8.1.0; build fingerprint 8.1.0 |
| Misleading release labels | Settings UI: 10; release property: 9 | User photos; `properties.txt` |
| Build | `t3_p1-eng 8.1.0 OPM1.171019.026 20220823-094543 test-keys` | Properties |
| Firmware | `V8.1.1_20220823.094651_THEME1` | `ro.tw.version` |
| Platform | Allwinner T3, `sun8iw11p1` / `sun8iw11` | Properties and CPU identification |
| CPU / ABI | Four Cortex-A7 cores (ARM part 0xc07); ARMv7, 32-bit `armeabi-v7a,armeabi` | `cpu.txt`, properties |
| Frequency | Hardware range reported 480–1600 MHz; sampled at 1200 MHz | `cpu-policy.txt`; governor/current configured ceiling unreadable |
| GPU | ARM Mali-400 MP, OpenGL ES 2.0, Linux-r8p1-00rel0 | `graphics.txt` |
| Kernel | 4.9.56, SMP PREEMPT, #1137, 2022-08-23, armv7l | `kernel.txt` |
| Display | Physical 1024×600; 160 dpi; no override shown | `display-size.txt`, `display-density.txt` |
| Usable kernel RAM | 1,007,380 KiB = 983.8 MiB | `/proc/meminfo` |
| Main flash block device | 15,106,048 KiB ≈ 14.41 GiB / 15.47 GB | `partitions.txt`; device-reported capacity, not a destructive capacity test |
| `/data` filesystem | 11,685,788 KiB total; 9,839,012 KiB available (≈9.38 GiB), 16% used | `storage.txt` |
| `/system` filesystem | 99% used, 10,164 KiB available, mounted read-only | `storage.txt`, `mounts.txt`; not the same as low user-data space |
| MCU | Photo reports STM32, `T3L.3.19-296-10-A49305-200715(STM32)` | Screen-reported; no firmware query/command sent to MCU |
| MCU detail | `VW(T3L.3.19, PT2313, QN8035, STM32,296)` | Photo; identifiers are clues, not independent silicon/vehicle verification |

The user-photo storage figure (34% used, 10.57 GB free) differs from live `df`.
Different accounting and collection times may contribute; do not treat either
as a physical flash test or silently reconcile them.

## Root and security

- ADB shell is **UID 2000**, SELinux context `u:r:shell:s0`, not UID 0.
- `/system/xbin/su` exists, root-owned, mode `0755` (not setuid). It was **not
  executed**. Existing usable root access remains unconfirmed; binary presence
  is not proof. Root-owned system processes are normal and not proof either.
- SELinux reports **Permissive**; `ro.debuggable=1`, `ro.secure=1`,
  `ro.adb.secure=1`; security patch label is `2018-09-05`.
- TCP ADB is confirmed at 5555. The user installed Termux/iproute2 and attempted
  the enabling property writes before this collection. Do not expose this port
  outside the trusted LAN. Closure requires a separately approved recovery plan.
- Firmware advertises USB gadget support and controller
  `1c13000.udc-controller`. This does not prove the external socket used is
  device-capable; the earlier host-only-USB explanation remains a hypothesis.

## Thermal warning and gaps

Raw CPU/GPU readings were **96 / 94**, above first passive trips **95 / 90**.
The vendor uses nonstandard units (trip values reach 120), consistent with
whole degrees but not independently calibrated. GPU cooling state was 1/3;
kernel logs include failed GPU cooling-frequency requests at 240 and 312.
This is a meaningful thermal-management warning, not proof of a precise
temperature or a particular cooling fault. Do not stress-test, force a
performance governor or defeat thermal controls. Investigate safe ventilation
and temperature behavior before performance trials.

Governor and configured maximum-frequency reads were denied by ordinary file
permissions (`0660 system:system`). Some root init files were unreadable. No
permissions were bypassed. Actual ACC sleep delay, usable root and full private
radio protocol remain open questions. No firmware from another unit is approved.
