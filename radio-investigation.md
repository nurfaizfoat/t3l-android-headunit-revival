# T3L Revival — FM radio investigation

## SOLVED (2026-10-21): TXZNet protocol decoded; implemented in T3L Drive 0.3.0

The factory radio app speaks the **TXZNet launcher protocol** over two implicit broadcasts
(its manifest declares only a launcher activity; the channels are dynamic code):

- Launcher → radio: action `com.txznet.launcher.radio.action.send` + int extra `"action"`:
  - `10` = query current station · `8` = set station (float extra `"frequency"`, MHz)
    · `7` = next station · `5` = close radio UI · `4/6/9` = no-ops.
- Radio → launcher: action `com.txznet.launcher.radio.action.recv` + extras
  `"action"` (int: `1` = station update/reply, `2` = UI opened, `3` = UI closed),
  `"frequency"` (float, **MHz × 100**; live-verified `10530.0` while tuned to 105.3 MHz)
  and `"packageName"` = `com.tw.radio`.
- The radio app answers only while `RadioActivity` exists (its receiver `a/a/b` is
  registered by the activity). T3L Drive therefore sends a `action=10` query on every
  launcher resume, and keeps a lifetime receiver for live `action=1` updates while the
  radio activity exists. Last station is persisted in `SharedPreferences "state"`,
  so the tile shows it after a cold boot.

Discovery trail: (1) manifests had no receivers, (2) `dumpsys activity broadcasts`
showed `com.tw.radio` registering a dynamic filter on `…radio.action.send`
(same pattern as `com.tw.bt` on bt/btmusic/call), (3) `strings` on `classes.dex`
exposed both action names + the `"frequency"` key, (4) Androguard decompilation
(evidence in `evidence/radio-apk-inspect/`, incl. `radio-decompile.txt`) gave the
exact codes, (5) a live `--ei action 10` probe confirmed the units.

From 0.3.1 the tile resolves station names offline: `RadioStations.java` holds
the Klang Valley + Seremban FM tables (owner's list, 2026-10-21), keyed by
tenths of MHz; matched → "Name · F MHz", unmatched → "F MHz · not in saved list".
The table has no AM names (the head unit is not an SDR), so AM still shows only
"AM <kHz> kHz".

Androguard lives in `/tmp/opencode/venv/bin/python` (recreate with
`python3 -m venv /tmp/opencode/venv && /tmp/opencode/venv/bin/pip install androguard`).

Rollback-story correction surfaced by the same analysis: `com.dofun.variety` (Theme)
lived in **`/data`**, not `/system` — `pm uninstall --user 0` removed it entirely;
restoration needs the laptop-documented install procedure, there is no system copy.

## Identified factory UI

| Item | Finding |
| --- | --- |
| Package | **`com.tw.radio`** |
| Activity | **`com.tw.radio/.RadioActivity`** |
| APK | `/system/priv-app/com.tw.radio_78cc/com.tw.radio_78cc.apk` |
| Version / SDK | 1.0, code 1; min SDK 16, target 27 |
| UID / state | 10029; user-0 state 0/default; enabled |
| Manifest | One Activity with MAIN/LAUNCHER; launchMode 2 (`singleTask`); no declared service, receiver, provider or requested permission |

Evidence: package manager output plus a host-copied APK, SHA-256 recorded in
`evidence/20261021T062836.681052Z/apks/pull-manifest.json`. The offline-decoded
manifest is `com.tw.radio.manifest.xml` in the same directory. With target 27,
the activity's intent filter implies default export in the absence of an
explicit exported attribute; actual launch from a normal prototype remains
an approved future functional test. No radio activity was launched by the agent.

## Available interface evidence and confidence

| Interface | Evidence / confidence | Discovery action |
| --- | --- | --- |
| Explicit factory Activity shortcut | Manifest + enabled MAIN/LAUNCHER query, high confidence UI entry point | Query only; no launch |
| `com.txznet.launcher.radio.action.send` | **Live dynamically registered receiver** in `com.tw.radio`, UID 10029; also a DEX string | No broadcast sent |
| `com.txznet.launcher.radio.action.recv` | DEX string with `sendBroadcast`, `frequency`, `action`, `token`, `packageName` | Likely reply/status path, but direction/schema not fully established |
| `android.tw.john.TWUtil` | Radio DEX method references include constructors and `close`; additional `open`, `write`, `addHandler`, `removeHandler` names occur | Private vendor framework API; no invocation |
| MCU/tuner hardware | MCU UI names QN8035, PT2313, STM32; native `gocsdk /dev/ttyS3 500000` is running | Labels/process metadata only; no serial/device-node access |
| Standard Android radio service | Service enumeration did not reveal a usable standard broadcast-radio interface | No assumption that public Android radio APIs control this MCU tuner |

Manifest absence of receivers does not mean there is no control path: the live
radio process registers a receiver at runtime. Conversely, the receiver's
existence does not prove any guessed command/extras are safe or permission-free.
Frequency units, numeric actions, token semantics, lifecycle, audio focus,
region settings, permissions and behavior when the UI is absent remain unknown.

The offline tool decodes manifests, DEX strings and selected method references;
it is **not** a full decompiler or call-graph proof. The launcher APK uses
packing/plugin infrastructure, so its exposed strings are especially incomplete.
Framework JARs are largely preoptimised/stub-sized; no privileged runtime hooks
or deoptimisation were used to inspect private framework internals.

## Protected dependencies

- `com.tw.service`: persistent system UID, `TWService`, reverse-camera/parking
  Activities and vendor control references. Do not disable even though it has
  no normal launcher icon.
- `com.tw.bt`: persistent system UID and `ATBluetoothService`; preserve Android
  Bluetooth/HAL dependencies too.
- `com.tw.eq`: persistent EQ service and potential amplifier/audio routing.
- `com.tw.core`: system UID and ACC/sleep/wake/messaging bridge; current factory
  launcher is bound to it.
- Native `gocsdk`, audio/camera HALs, `radio_monitor`, kernel `car-reverse-wq`:
  preserve; a package inventory cannot safely replace them.

## Integration recommendation

**Version 1: launch the original RadioActivity from a small native launcher.**
Retain all factory services and the factory HOME escape path. Do not implement
direct tune/seek/preset/volume controls yet. The first approved test should verify
radio UI launch/resume, audible output and return-to-HOME without interruptions
to Bluetooth/navigation/vehicle functions.

For later direct controls, first perform further **offline** code/protocol
analysis of the copied APK/framework with a suitable tool and record exact
arguments, permissions and side effects. Any active validation requires a new,
explicitly approved parked-vehicle test. No speculative broadcasts, Binder
transactions, UART/MCU writes, CAN changes, provider calls or keyevents are
authorised by this report.
