# Historical pre-discovery memory notes — superseded by live reports

## Status: PARTIAL — UI snapshot only; process-level discovery blocked

No device is connected. There are no measured RAM, process, swap, ZRAM, pressure,
or CPU-governor results. Approximately 1 GB RAM is user-supplied, not measured.

The user subsequently supplied an About Device photograph displaying
`Avg 732 MB of 1.0GB memory used`. This supports the reported capacity only at
the UI level. The averaging interval, workloads, usable kernel RAM and memory
accounting are unknown. Do not infer current MemAvailable, reclaimable memory,
process PSS or memory pressure by subtracting these rounded UI figures.
The same screen displays `34% used - 10.57 GB free` storage; this is not a
partition inventory or independent confirmation of physical flash capacity.

## Read-only evidence to collect

- `/proc/meminfo`, `/proc/swaps`, `/proc/vmstat` and `/proc/uptime`.
- `dumpsys meminfo`, process listings and a bounded, one-shot CPU snapshot.
- `/proc/pressure/memory` if available; older kernels may not implement PSI.
- Existing ZRAM sysfs statistics and swap configuration; do not create swap,
  reset ZRAM, change swappiness or write sysfs values.
- Readable low-memory-killer parameters and lmkd configuration/logs.
- Available/current CPU governors, frequency limits and thermal state.

## Measurement plan — pending approval for active tests

Take three comparable idle samples after the same settling interval. Separately
measure normal radio, navigation and Bluetooth workloads, recording process PSS,
MemAvailable, swap activity, LMK events and foreground responsiveness. Do not
interpret low free RAM alone as memory pressure or add process PSS totals as an
exact physical-memory accounting.

Boot and ACC/standby comparisons require a separately approved, parked-vehicle
test. Do not reboot, kill processes, clear caches or switch vehicle functions
during passive discovery.

## Optimisation gate

No tuning is recommended yet. Future one-change-at-a-time trials must compare
the same workloads and show repeatable PSS/latency improvement without extra
process kills, audio interruptions or vehicle-function regressions. Revert on
regression; select numeric targets after obtaining the baseline.
