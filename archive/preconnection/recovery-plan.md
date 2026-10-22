# Historical pre-discovery recovery notes — superseded by live reports

## Current state

No device is connected and no agent-issued device-side commands have run.
The user has independently installed Termux and attempted to set
`service.adb.tcp.port` to `5555` and restart `adbd`; the prior property value,
command success and actual listener state have not been verified. The original
no-change baseline no longer describes the user-modified device.

No device backup has been made. These reports are not a firmware, partition,
application-data or MCU backup. Do not infer that a reboot would restore the
original debugging state. Before a later approved rollback, inspect current
properties and boot/init handling; the original value was not captured.

Keep any network ADB listener confined to the trusted local network; do not
configure router port forwarding. After discovery, propose and seek approval
for closing the listener using a verified, firmware-appropriate method without
losing the needed recovery path. Do not change the listener during discovery.

## Gates before any future change

1. Verify serial, hardware/build identity, Android API and current package/user
   state. Do not assume firmware compatibility with another T3L device.
2. Save private host-side evidence of package paths/versions/enabled states,
   HOME handlers, relevant settings and permissions. Record factory-launcher
   and radio components explicitly.
3. Determine what can actually be backed up without rooting. APK copies do not
   preserve application data, privileged signatures, partition contents, MCU
   firmware or CAN configuration. Android backup support is not guaranteed.
4. Establish a tested ADB recovery connection, a reachable factory launcher and
   the exact version-supported restoration method before altering HOME.
5. Present the named change, expected measurements, exact original state,
   rollback steps and recovery limitations. Obtain explicit approval.

## Rollback requirements

- Package-state trial: restore the recorded per-user enabled/default state,
  not a guessed universal value. Never target protected packages.
- Launcher trial: restore the recorded factory HOME handler first, verify it
  launches normally, then remove only the approved replacement if necessary.
- Settings trial: restore the exact original value; distinguish an absent key
  from an empty string. Do not trial bootloader, partition, MCU or CAN changes.
- Validate radio/audio, Bluetooth, reverse camera, steering-wheel/vehicle
  controls, startup and standby in a separately approved, parked-vehicle test.

No executable rollback commands are specified yet: package names, Android
command support and original states have not been discovered. A factory reset
or an unverified firmware flash is not an acceptable routine rollback.

## Handling evidence

Keep future raw logs and APKs in private host storage. They can contain device
identifiers, paired-device details, locations or account information; redact
before sharing. Keep separate timestamped evidence for every discovery run.
