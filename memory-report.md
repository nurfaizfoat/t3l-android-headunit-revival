# T3L Revival — Memory report

> Discovery baseline below. The [applied optimisation report](optimization-report.md)
> records the later stock-launcher → native-launcher PSS change (83.6 → 7.2 MiB)
> and measurement limitations. Thermal concerns remain unresolved.

## Baseline: observed, not a controlled idle benchmark

Source: `evidence/20261021T062836.681052Z/`. Collection lasted about 38 host
seconds, with device uptime 1604.68–1641.20 seconds. Termux was foreground;
Chrome, Settings, the keyboard and installer were present after setup. These
are not three repeatable idle samples and not predicted savings.

| Metric | Observation |
| --- | --- |
| Kernel RAM | 1,007,380 KiB / 983.8 MiB |
| MemAvailable | 336,620 → 337,892 KiB (328.7 → 330.0 MiB) |
| MemFree | 40,000 → 25,824 KiB; not a pressure diagnosis by itself |
| Android memory summary | `status normal`; accounting differs from `/proc/meminfo` |
| Swap | `/dev/block/zram0`, 262,140 KiB usable; about 133,360 KiB occupied |
| ZRAM | 256 MiB disk size, lz4; ~52 MiB physical RAM at the sampled instant |
| Swappiness | 60 |
| LMK adj | `0,100,200,300,900,906` |
| LMK minfree | `18432,23040,27648,32256,36864,46080` pages; do not mistake for KiB |
| PSI | `/proc/pressure/memory` does not exist on this kernel |
| CPU usage | Collected CPU summary: 14% total; not a controlled workload |

`ro.config.low_ram=false`; Dalvik growth limit 128m, heap size 256m. These are
observations, not permission to alter low-RAM mode, heap sizes or LMK policy.
ZRAM is already configured by vendor init/fstab; do not add a second swap setup.

## Largest application PSS observations

Values below are process PSS from one `dumpsys meminfo`, converted to MiB.

| Process/group | PSS | Interpretation |
| --- | ---: | --- |
| Factory HOME `com.dofun.variety` | 82.0 MiB | Has a foreground background service; HOME switch alone may retain it |
| Chrome main + listed sandbox | 108.3 MiB | Also the **active WebView provider**; do not disable/force-stop it |
| Three `com.google.android.gms` processes | 135.6 MiB | Location/system bindings exist; do not equate PSS with safe savings |
| Termux | 59.0 MiB | Diagnostic workload; remove from controlled baseline only through approved normal app use |
| Settings | 25.4 MiB | Cached diagnostic UI |
| `com.tw.service` | 15.3 MiB | Persistent vehicle/reverse service, critical |
| `com.tw.radio` | 13.7 MiB | Cached UI; tuner/audio may live elsewhere |
| `com.tw.bt` / `com.tw.eq` / `com.tw.core` | 8.7 / 7.8 / 7.8 MiB | Protected dependencies |
| Print spooler | 4.4 MiB | Low-risk optional feature only if printing/PDF is unused |

Other native/system processes and shared memory are substantial. Do not sum
these selected figures as exact physical RAM use, and do not claim that
disabling a package recovers its entire PSS permanently.

## Pressure and thermal limits

VM counters show historical paging/reclaim (`pswpin=7684`, `pswpout=41273`,
`pgmajfault=26526` at one instant), not rates. Available logs are bounded and
dominated by recent activity/audits; absence of a visible LMK event is not proof
that no earlier kills occurred. Need timed counter deltas during ordinary use.

CPU/GPU raw temperatures exceeded their first passive thresholds, and GPU
cooling requests produced errors. Available governors include interactive,
conservative, ondemand, userspace, powersave and performance; the selected
governor and configured maximum were permission-denied. No tuning was applied.

## Proposed measurements — approval required for workload changes

1. Address the thermal warning first; no synthetic stress tests.
2. Establish three 60-second settled samples for HOME-only, normal FM,
   Bluetooth playback and Headunit Reloaded/navigation as actually used.
   Record foreground app, temperature, total HOME-related PSS, MemAvailable,
   swap/reclaim deltas, LMK events and audio interruptions.
3. Launcher prototype target: own warm PSS ≤35 MiB and APK <1 MiB. Targets are
   unmeasured design goals. Evaluate **combined** original/new HOME processes;
   reject an additive trial that raises combined settled PSS by >10 MiB.
4. Any optional-package trial must produce repeatable improvement above sample
   variability; a stopped package may save nothing. Revert on audio, camera,
   Bluetooth, ignition, steering-wheel or navigation regression.

No task killer, cache-clearing loop, swap resize, governor/heap/LMK change or
Google-service removal is recommended from this single snapshot.
