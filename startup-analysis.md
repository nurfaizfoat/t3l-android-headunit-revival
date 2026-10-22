# T3L Revival — Startup analysis

> Discovery baseline below. After explicit approval, T3L Drive was built,
> installed and made HOME; stock Theme was disabled-user. See
> [execution and rollback](optimization-report.md). No cold-boot, ACC or
> standby changes/tests were performed.

## Current startup and HOME chain

Evidence: main run `20261021T062836.681052Z`, vendor-init follow-up
`20261021T063125.198278Z`, boot-script/broadcast follow-up
`20261021T063500.162396Z`.

- Default HOME: **`com.dofun.variety/com.dofun.overseasvariety.Launcher`**.
  The only other returned HOME activity is Settings' `FallbackHome`, not a
  usable alternative daily launcher.
- Factory launcher version `V9.5.0.350.251216`, code 350, is an updated system
  app under `/data/app`; the immutable base also remains under system storage.
  Do not confuse the APK path with a removable, independent user app.
- Launcher has a BOOT_COMPLETED receiver and an active foreground
  `VarietyBackgroundService`; it binds `com.tw.core/.messenger.server.MessengerService`
  and Google's advertising-ID service. HOME replacement alone may not stop it.
- `com.tw.core` has `MainService`, `DameonService` (vendor spelling),
  `MessengerService` and a receiver for boot, ACC on/off, sleep and wake actions.
  It shares system UID with critical vendor services. Do not disable it.
- `com.tw.service`, `com.tw.bt` and EQ services are active; service/BT and EQ
  package flags include persistent. Native `gocsdk` and reverse-camera kernel
  paths mean an APK-only boot model is incomplete.
- 22 enabled BOOT_COMPLETED receivers and one LOCKED_BOOT_COMPLETED receiver
  were returned. Full components are in the raw evidence; none was triggered.

## Existing boot customization and logging

`appsdisable.rc` starts `/system/bin/appsdisable` after boot completion. Reading
the script revealed a four-second wait, a `start_disable` check and a loop that
disables Google BOOT_COMPLETED components before setting the flag. The current
global flag is already `1`, and several packages have component-level overrides.
This is vendor/pre-existing behavior, not an optimisation applied by this agent.
The script has **not** been executed or altered by the agent.

`logcatd` persistent logging is active, with rotated log storage configured by
init. Recent main/system/events and kernel logs were copied without clearing.
Root-level init files have limited readability; readable system/vendor init
definitions and selected scripts were captured. `z-link.sh` is boot-started
and has its own helper-launch logic; do not disable it on name alone.

Service boot-start properties place zygote near 4.0 seconds, `gocsdk` near 5.2
seconds and boot animation near 6.5 seconds. These are service-start timestamps,
**not** measured HOME-ready or boot-complete latency. Some services were
restarted later (notably network-debugging related); do not pool these timings.
Collection began at about 26.7 minutes uptime. Bounded logs do not retain a
complete boot timeline. No timed boot or ACC cycle was performed.

## Standby observations and uncertainty

At collection the device was awake, externally powered, display ON, no held
PowerManager wake locks, and display suspend blocker active. Sleep timeout is
`-1`; screen-off timeout is `2147483647` ms. Wi-Fi sleep policy is `2`.
Screensaver enabled/on-dock is set, with a DeskClock component that is not in
the current installed-package list. These settings do **not** establish the MCU
ACC-off shutdown delay, ignition behavior, real standby power or camera readiness.

Vendor `ACC_OFF`, `DO_SLEEP`, `DO_WAKEUP` strings/receivers were observed but
never sent. Vendor preferences under app-private `/data` were not accessed.
Actual standby configuration needs a normal-settings photo and a separately
approved parked-vehicle ACC test; do not open factory CAN menus or guess values.

## Native launcher proposal: API 27

See [`launcher-proposal/README.md`](launcher-proposal/README.md) and the native
Java Activity/manifest. This is **source-only**, not built, installed or selected
as HOME. One platform Activity, simple large buttons, no Compose/WebView,
network permission, boot receiver, persistent service, timer, wakelock, plugin,
root, vendor API or background polling. Shortcuts target verified FM, Bluetooth,
music, EQ, Headunit Reloaded, Settings and the factory HOME.

Initial acceptance goals: own warm PSS ≤35 MiB, APK <1 MiB, no combined
factory/new-HOME PSS increase >10 MiB. These are design targets, not results.
Do not disable the factory launcher to meet them. First approve/test as an
ordinary app; a later HOME switch needs a separately verified recovery path.

## Approved-test design, not execution

After explicit approval and thermal/recovery gates, compare at least three
cold starts and three ACC resumes separately, with identical workloads, device
temperature, network and settling intervals. Record HOME-interactive time,
audible radio readiness, Bluetooth readiness and camera/vehicle behavior.
Provisional improvement target: ≥20% median HOME-ready latency reduction with
no worsening of protected functions. Record failures and revert each unsuccessful
trial. Do not reboot, send ACC broadcasts or simulate reverse during discovery.
