# Historical blocked radio notes — superseded by live reports

## Status: BLOCKED

The FM package, launch activity and control interfaces are unknown. No radio,
MCU, audio-routing or vehicle-control interface has been invoked.

## Photograph clues — not interface discovery

The MCU dialog supplied by the user reads
`VW(T3L.3.19, PT2313, QN8035, STM32,296)`. `QN8035` and `PT2313` are useful
radio/audio-component identifiers to investigate, but a firmware label does
not prove the fitted silicon, wiring, package identity or accessible controls.
The `VW` prefix likewise does not establish the actual vehicle or CANbus
configuration. Do not change hardware/vehicle settings based on these strings.

## Read-only investigation after connection

1. Identify candidate radio APKs from package metadata and existing foreground/
   process evidence; confirm actual activities rather than guessing names.
2. Inspect manifests for exported activities, services, receivers, providers,
   intent filters and permissions. Record shared UIDs and privileged placement.
3. Correlate running/bound services, existing logs and native service listings
   with the MCU bridge, amplifier and audio-focus/routing components.
4. If readable, copy relevant APKs to private host storage for static analysis;
   inspect native libraries, intent strings and service bindings. Do not bypass
   permissions, install hooks or alter APKs.
5. Document each candidate interface with its evidence, permission requirements,
   calling identity, expected semantics and confidence. An exported component
   or a string found in code is not proof of a safe or supported public API.

Do not send speculative broadcasts, Binder transactions, provider calls,
keyevents, UART/MCU commands or device-node writes. Do not open unknown vendor
device nodes, including for purportedly read-only probing.

## Integration preference

Prefer an explicit shortcut to the verified factory radio activity, preserving
its service lifecycle and audio routing. Direct frequency/preset control is
deferred until an interface is established and an approved test plan exists.
An Android broadcast-radio framework API may not be implemented by this unit;
do not assume standard Android APIs control its MCU-based tuner.
