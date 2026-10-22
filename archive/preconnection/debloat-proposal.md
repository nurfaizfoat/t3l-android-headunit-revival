# Historical blocked debloat notes — superseded by live reports

## Status: BLOCKED — no package-specific changes proposed

The CSV contains a header only because no package inventory was retrieved. It
does **not** mean the unit has no applications. Do not infer package identities
or safety from another T3L unit, a package name, or an APK location alone.

| Category | Current classification |
| --- | --- |
| SAFE TO DISABLE | None established |
| REQUIRES INVESTIGATION | Every unverified application, including apparent bloatware |
| CRITICAL — DO NOT TOUCH | Roles protected below; actual package identities pending |

Protect the factory launcher, radio, MCU bridge, CAN/vehicle controls, Bluetooth,
amplifier/audio routing, reverse camera, steering-wheel integration, ignition/
standby handling, System UI, Settings, package management and Android core
services. Shared UIDs, native services and implicit vendor dependencies may
extend this protection to apparently unrelated packages.

Before declaring any package safe, inspect its installed state, activities,
services, receivers, permissions, shared UID, bindings and boot participation;
establish that it is optional for the user's actual workloads. Package labels
and launch activities alone are insufficient evidence.

## Conditional optimisation sequence

1. Establish idle, workload and startup baselines without changing settings.
2. Identify optional applications and dependency evidence; obtain explicit
   approval for a specific package and an exact rollback procedure.
3. Trial one reversible per-user change, preserving APK and user data. Do not
   uninstall packages or disable any protected role.
4. Measure idle PSS/MemAvailable, LMK events, launch latency and audio stability
   against baseline. Test protected functions only in an approved safe setting.
5. Restore the original state on regression; retain a change only after review.

No disable, uninstall, tuning or reboot commands have been issued.
