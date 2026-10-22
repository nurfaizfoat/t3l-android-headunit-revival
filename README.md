# T3L Revival

Documentation and tooling for the read-only discovery and reversible
optimisation of a TOPWAY/Allwinner T3L Android 8.1 car head unit — replacing a
laggy stock launcher with a lightweight native one, measuring what actually
changed, and keeping every step rollback-safe.

> **Warning:** every device-changing command here was applied on one specific
> unit after review. A differently named or differently built unit is *not* a
> substitute for exact-device evidence. Do not flash, root or debloat a head
> unit based on this repo alone.

## What is and is not in this repo

Published: the discovery reports, package inventory CSVs, and the
[launcher proposal](launcher-proposal/README.md) (native launcher source and
deployment scripts) under the MIT license.

Not published (kept private by `.gitignore`): the timestamped `evidence/`
folders with raw device dumps and copied vendor APKs, the `changes/` journals
with screenshots, and `.private/` with the launcher signing keys. Repo readers
can regenerate their own evidence with `collect-readonly.py`.

## Current state — approved launcher optimisation applied

**T3L Drive 0.1.1 is installed/default HOME; Theme is now uninstalled for user 0,
including its user data—not merely disabled.** Headunit Reloaded is preserved.
Standby settings were not changed. The factory ROM copy was not erased.
See [current removal scope and recovery limits](theme-removal.md),
[current 75-package inventory](package-inventory-current.csv), and
[earlier launcher optimisation/measurements](optimization-report.md).
The original reports/75-package CSV below are the discovery baseline; the
[initial post-change inventory](package-inventory-after.csv) contains 76 packages
and records the earlier disabled-Theme state, before the subsequent uninstall.

## Reports

- [Hardware and security](hardware-report.md)
- [Memory and thermal observations](memory-report.md)
- [75-package inventory](package-inventory.csv)
- [Conditional debloat proposal](debloat-proposal.md)
- [Startup, standby and launcher proposal](startup-analysis.md)
- [FM radio and vendor dependencies](radio-investigation.md)
- [Recovery gates and rollback proposals](recovery-plan.md)
- [Native launcher source, build and deployment](launcher-proposal/README.md)

Evidence folders are private and timestamped. The initial blocked reports are
retained in `archive/preconnection/` as historical notes, not current findings.

## Reproduce passive collection

Confirm the intended unit's current IP/identity first; the address may change.
These commands operate on an already authorised device, copy host evidence and
perform only diagnostic queries. Dumps themselves create transient workload
and logs; they are not zero-impact idle benchmarks.

```sh
python3 collect-readonly.py --serial <unit-ip>:5555
```

The script never invokes `su`, changes permissions/settings, sends vehicle
commands, launches activities, clears logs or disables packages. Unsupported
and permission-denied queries are recorded. Some optional dumps can be slow;
do not interpret failures as absent features or retry with elevated privileges.
Copying the ten selected APKs was a separate read-only host-copy step, recorded
in the first evidence run's `apks/pull-manifest.json`.

Offline analysis/generation (no device interaction):

```sh
python3 analyse-apks.py evidence/20261021T062836.681052Z/apks
python3 generate-inventory.py evidence/20261021T062836.681052Z
python3 -m unittest -v test_reports
python3 -m unittest -v test_optimization
python3 -m unittest -v test_theme_removal
```

Only the named launcher installation/HOME/stock-disable operations were approved
and applied. Optional printing or unrelated debloat was **not** applied.
Rollback commands are deliberate device changes. No firmware/MCU/CAN changes are proposed. Never use a
similarly named T3L unit's firmware as a substitute for exact-device evidence.

Six baseline offline checks cover report presence, CSV classification/baseline states,
copied APK hashes, radio evidence, binary-XML string lengths and launcher
manifest safety. Five additional post-change checks verify HOME/stock state,
unchanged settings, protected packages, build/source hashes and the recovery
route. Three further checks validate the subsequent Theme uninstall, preserved
HUR/standby and current launcher build. **All 14 passed.** These offline tests do not themselves launch apps or
validate vehicle functions; actual compilation, signing, installation and UI
checks are recorded separately in the optimisation report and journals.
The interrupted `20261021T063740.413028Z` attempt has its own note
and is not treated as a completed evidence run.

## License

[MIT](LICENSE). Placeholders such as `<unit-ip>` and `<your-ssid>` in the docs
are yours to fill in when reproducing the collection.
