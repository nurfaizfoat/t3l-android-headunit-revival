# T3L Revival — Recovery plan

> **Latest:** Theme is now uninstalled for user 0, not just disabled. Re-enable
> alone is insufficient; the existing package must first be reinstalled for that
> user. Deleted user data cannot be recovered from these backups. See
> [current removal and recovery limits](theme-removal.md).

> **Execution update:** the user subsequently approved launcher replacement.
> T3L Drive is now default HOME and Theme is disabled-user with data retained.
> See [current tested recovery route and supported commands](optimization-report.md#recovery--no-root-needed).
> The remainder below records the earlier discovery baseline and pre-change gates.
> No standby settings were changed. `pm enable` is the verified functional
> stock restore (state 1); exact original state 0 reset is not claimed.

## Preserved baseline and limitations

ADB target: `<unit-ip>:5555`; network address may change. Factory HOME:
**`com.dofun.variety/com.dofun.overseasvariety.Launcher`**. No optimisation was
applied by the agent. The user independently installed Termux/iproute2 and set
up TCP ADB; its original property value was not recorded.

Private evidence contains all 75 package paths/versions/user-0 states, shared
UIDs, existing component overrides, HOME resolution, settings and readable
boot/init definitions. Ten relevant APKs were copied, including the active
factory launcher, vendor core/service/radio/BT/EQ/keypad/AUX and print packages;
their hashes and source paths are in `apks/pull-manifest.json`.

**This is not a complete backup.** No app-private data, permissions database,
partition image, bootloader, recovery, MCU firmware, CANbus configuration or
tested full-device restore is available. APK copies alone cannot reconstruct
privileged installation context, app data or an entire failed unit. Do not
assume Android backup support or similar-device firmware compatibility.

## Before any change

1. Recheck identity, IP, ADB authorisation and the current package/component
   baseline. Save a fresh timestamped snapshot; do not overwrite old evidence.
2. Resolve the thermal warning sufficiently for ordinary functional testing.
3. Keep the original launcher installed/enabled and physically reachable. A
   shortcut in an untested replacement is not a proven recovery mechanism.
4. Verify a recovery command/path on the actual firmware **before** changing
   HOME. `cmd package` help advertises `set-home-activity`; this operation has
   not been exercised. A later `pm help` query timed out; no setting was changed.
5. Present a named change, initial state, intended measurement, exact rollback,
   recovery limitations and test environment; obtain explicit approval.

## HOME rollback — proposal only, not executed

After a separately approved recovery test, the expected restoration is:

```sh
adb -s <unit-ip>:5555 shell cmd package set-home-activity --user 0 com.dofun.variety/com.dofun.overseasvariety.Launcher
adb -s <unit-ip>:5555 shell am start -n com.dofun.variety/com.dofun.overseasvariety.Launcher
```

These commands **change device state** and must not be run as passive discovery.
Verify the original HOME is restored, returns normally and all protected
functions work before considering removal of the replacement app. Network-only
ADB recovery may be unavailable after a bad boot; do not select a new default
until an acceptable additional recovery path is established.

## Optional-package rollback gate

The two printing candidates are user-0 state `0` (**default**), not `1`
(explicitly enabled). Before a disable trial, verify firmware support for an
exact default-state restoration operation and record component overrides.
`pm enable` alone changes state to `1`, so it is not an exact baseline rollback.
No printing trial should proceed until this restoration path and queue/feature
requirements are resolved. Preserve APKs and data; do not uninstall or clear.

Do not touch the three **pre-existing disabled-user** packages:
`com.tw.carchoose`, `com.android.vending`, `com.google.android.webview`.
Do not broadly enable/disable Google receivers: `appsdisable` and
`start_disable=1` are part of the captured baseline. Chrome must remain enabled
as the active WebView provider. Do not use root to get around these gates.

## TCP ADB cleanup — later approval required

Keep port 5555 confined to the trusted LAN; no router port forwarding. ADB
authentication is enabled, but the device has a very old security baseline
and permissive SELinux. Disconnecting the host is not the same as closing the
device listener. Propose a firmware-appropriate closure only after confirming
how access will be recovered. Do not guess the original property value, assume
a reboot restores it, revoke every host key, or stop adbd during discovery.

## Validation and stop conditions

For each approved reversible trial, keep a change log and restore immediately
on boot loops, audio dropouts, lost FM/BT, camera failure, steering-wheel/vehicle
control regression or standby abnormality. Test vehicle functions only in an
approved parked setting; do not simulate ACC/reverse by speculative broadcasts.
If ADB is lost, do not escalate to reset/flashing. Return to the known working
physical UI or request model-specific recovery guidance backed by exact-device
evidence. Factory reset, partition edits and MCU/CAN changes are not rollback.

Evidence may contain account/location/device information, tokens and identifiers.
Keep raw files/APKs private, redact before sharing, and never publish copied
vendor software as part of a public report bundle.
