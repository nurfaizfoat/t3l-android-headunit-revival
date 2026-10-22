# Theme/chameleon removal — current state

On the user's explicit deletion request, **`com.dofun.variety` was uninstalled
for Android user 0**, not merely disabled:

```sh
adb -s <unit-ip>:5555 shell pm uninstall --user 0 com.dofun.variety
```

Package manager returned **Success**. No `-k` was supplied: standard uninstall
removed its user data/cache. The active package record shows `installed=false`,
`ceDataInode=0`; normal user-0 package listing is empty for Theme. This is not a
forensic wipe, and no backup of its former user data exists.

## What “removed” means

The read-only **factory system-image copy remains**, as does package-manager
knowledge of it and potentially retained updated APK files. `pm list packages
-u` can still show it. It is **not installed or launchable for user 0**. No
system remount, root, partition edit, firmware, MCU/CAN operation or reboot was
performed. A factory reset, firmware restore or vendor provisioning could bring
it back. This is **not permanent erasure from the ROM**.

T3L Drive remains default HOME. It was updated to **0.1.1 / code 2**, using the
same signing key. The obsolete Factory Home / Recovery footer was replaced by
**About / Help**, so it no longer opens a missing app's Settings screen.

APK: `launcher-proposal/build/20261021T073402.013493Z/t3l-drive.apk`, 16,861 bytes.
SHA-256: `def1939c2f71181f616238d4f8a5006603dd911f832b28e003f7ba01e994cfee`.

## Preserved state and expected Android cleanup

- Headunit Reloaded's own package block is unchanged.
- System/global settings were unchanged at the uninstall check. Android removed
  Theme's `enabled_notification_listeners` entry automatically; that expected
  cleanup was not a direct settings write by the agent.
- Sleep timeout `-1`, screen-off timeout `2147483647` and Wi-Fi sleep policy `2`
  remained unchanged. No hot-standby/ACC, HUR, map/location or protected vehicle
  package changes were requested or applied in this step.
- No physical radio/BT/camera/steering/HUR, cold-boot or battery-draw test was run.
  Previous thermal concerns remain unresolved.

The uninstall script's initial complete-HUR-dump comparison stopped after
successful removal because the dump also includes the **global package-change
counter**. Follow-up confirmed the only HUR-dump differences were that counter
and Theme's change-log entry; HUR itself was unchanged. Comparison now scopes
to the actual package block and permits only Theme's notification cleanup.

Evidence: `changes/20261021T073012.783622Z/` and
`evidence/20261021T073514.036152Z/`. The older optimisation report, screenshots,
76-package inventory and Enable-only recovery instructions describe the earlier
disabled state and are superseded here. Current inventory:
`package-inventory-current.csv`.

All **14 offline checks** passed, including three checks specific to this later
uninstall. The installed 0.1.1 APK SHA-256 matches the verified host build. These
checks do not substitute for physical vehicle-function or cold-boot testing.

## Only if the owner later asks to restore stock

Do **not** run these as verification of removal; they would restore the app:

```sh
adb -s <unit-ip>:5555 shell pm install-existing --user 0 com.dofun.variety
adb -s <unit-ip>:5555 shell pm enable --user 0 com.dofun.variety
```

The deliberate `launcher-proposal/deploy.py ... restore` stage now reinstalls
the existing package for user 0 before enabling/selecting factory HOME if it
is absent. Theme itself has **not** been reinstalled to test this path. A host
copy of its previous APK remains in private evidence as an additional recovery
artifact. Reinstallation does not recover deleted user preferences/accounts or
make a firmware backup. Check the current IP, firmware and available package
before any future restoration.
