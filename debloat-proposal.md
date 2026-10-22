# T3L Revival — Debloat proposal

> Discovery proposal below. The user later explicitly approved stock launcher
> replacement only; see [applied changes](optimization-report.md). No printing,
> Google-service, location, HUR or vehicle-service debloat was applied. The
> protected stock HOME was replaced through a logged, reversible exception.

## Decision: no device changes applied

The live CSV inventories **75 packages**, their user-0 states, available
LAUNCHER/HOME activities, UIDs/shared UIDs, versions and dependency evidence.
Classification: **2 SAFE TO DISABLE (conditional), 20 REQUIRES INVESTIGATION,
53 CRITICAL — DO NOT TOUCH**. A classification is not approval to execute.
For packages without a copied manifest, component/permission metadata is
explicitly partial; a blank launch column means no matching enabled launch
activity was returned, not that the package is irrelevant.

## SAFE TO DISABLE — only if printing, including Print-to-PDF, is unused

| Package | Evidence | Limits |
| --- | --- | --- |
| `com.android.printservice.recommendation` | Separate UID; copied manifest exposes a print-recommendation service protected by a print binding permission | Usually little/no RAM gain when not running |
| `com.android.printspooler` | Separate UID; copied manifest is print/PDF-specific; observed PSS ~4.4 MiB | Disables printing/Save-as-PDF paths; retain data and restore default state |

These are low-risk **optional-feature candidates**, not unconditional safety
guarantees or approved actions. Confirm no needed print/PDF workflow and no
pending jobs before any trial. A diagnostic `dumpsys print` could not obtain the
remote spooler, so this session did not establish a trustworthy job-queue state.
Both package states are currently `0` (default), not explicit `1` (enabled).
Validate exact state restoration support before authorising a disable trial.

## REQUIRES INVESTIGATION

- `com.google.android.gms`, `com.google.android.gsf`, partner setup/extensions:
  location/geocoding/system bindings and shared UIDs are present. Larger PSS is
  not proof they can be removed without breaking navigation or accounts.
- `cm.aptoide.pt`: optional-store candidate, but has boot/work/root-check
  receivers. Confirm the required installation/update workflow first.
- `gb.xxy.hr`: **Headunit Reloaded V8.0.2**, user-installed, not bloat by default.
  Confirm intended Android Auto usage; preserve until requirements are known.
- `com.termux`: user-installed diagnostic tool; retain while establishing
  recovery. It adds load to the current memory snapshot.
- BasicDreams, wallpaper picker/cropper/backup, HTML viewer, bookmark provider,
  provisioning and TTS: potentially optional but feature requirements or full
  dependencies are unresolved. No blanket disable list.
- `com.android.vending` and `com.google.android.webview` are **already
  disabled-user**. Preserve their baseline; do not re-enable or further modify.

See CSV for every package and the reason for its conservative classification.

## CRITICAL — DO NOT TOUCH

| Dependency | Reason |
| --- | --- |
| `com.dofun.variety` | Factory HOME/recovery path; foreground service and boot receiver; binds `com.tw.core` |
| `com.tw.service` | Persistent system UID; MCU/vehicle coordination; reverse-camera activities |
| `com.tw.core` | System UID; boot/ACC/sleep/wake receiver and bound messaging/daemon services |
| `com.tw.radio`, `com.tw.bt`, `com.tw.eq` | FM, persistent Bluetooth and amplifier/EQ paths |
| `com.tw.keypad`, `com.tw.carchoose` | Steering-wheel/vehicle configuration; carchoose already disabled-user—leave unchanged |
| Other `com.tw.*` | Vendor media/input/recovery interactions not proven independent |
| `com.android.chrome` | **Current WebView provider**; standalone WebView is disabled |
| Framework, System UI, Settings, providers, installer, Bluetooth, input, audio/location/network stack | Platform and recovery infrastructure |
| Native `gocsdk`, camera/audio HALs, `radio_monitor`, kernel reverse worker | Outside package manager; preserve MCU/audio/camera chain |

The firmware already contains a root-run `appsdisable` boot script that can
disable Google boot-receiver components once. `start_disable=1` is already set.
Do not rerun/edit this script, reset its flag, or broadly restore components.

## Ordered, measurable optimisation proposal

1. **Thermal investigation first:** confirm vendor sensor scale and ordinary-use
   cooling behavior, with safe ventilation review. No governor or thermal edits.
2. **Controlled baseline:** three comparable samples/workload before any trial;
   see memory report. Setup/browser/Termux activity currently confounds idle RAM.
3. **Native launcher trial:** source-only proposal is in `launcher-proposal/`.
   First test as an ordinary app, without changing HOME or stopping the factory
   stack. Only after approval, recovery verification and functional checks may
   a separate default-HOME trial be considered. Combined memory may increase.
4. **Optional printing trial:** only after confirming feature nonuse, queue
   status, package state restoration and explicit package-specific approval.
   Measure actual deltas; do not promise large savings.
5. **Startup comparisons:** after cooling and recovery checks, separately approve
   three cold boots and three ACC resumes. Initial goal: ≥20% reduction in median
   HOME-ready time with no loss of radio readiness or protected functions.

Never uninstall/clear data, disable protected services, edit startup/init files,
flash similar-device firmware, modify MCU/CAN settings, or use root to bypass
read limitations as part of these proposed trials.
