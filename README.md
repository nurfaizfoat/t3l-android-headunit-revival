# T3L Revival

![T3L Drive 0.3.1 home launcher on the head unit](screenshots/t3l-drive-0.3.1-home.png)

*The current T3L Drive 0.3.1 home launcher running on the unit, captured on
21 October 2026: Android Auto projection card, Radio with station names,
Music, Bluetooth, Apps, Settings and EQ tiles.*

**Want to give an old Android car stereo a simpler, lighter home screen?**
This project shows how one TOPWAY/Allwinner T3L unit was inspected and given
the launcher pictured above, with help from an AI coding assistant on a laptop.
The home screen is called a **launcher**; changing it is not flashing new firmware.

**No coding experience needed to follow the connection guide below.** You do
the taps on the head unit; your laptop's AI assistant can help with the computer
commands. Connecting is only the first stage — it does **not** install this launcher.

> **Before you start:** work only on a unit you own or have permission to service.
> Park safely, keep the unit powered without draining the car battery, and never
> work on it while driving. This project is based on **one T3L running
> Android 8.1 / API 27**; researched steps are identified below. Menu names,
> passwords and permissions vary by firmware.
> Do not flash firmware, root the unit, change MCU/CAN settings, or remove apps
> just because this unit did. Stop if a step does not match your device.

## Start here — connect your head unit to your AI laptop

**Follow in order:** head unit setup (**1–6**) → laptop connection and AI
inspection (**7–9**) → close debugging when finished (**10**).

### What you need

- Your Android head unit, with a browser and permission to install apps.
- A laptop with a **local AI coding assistant** that can work with files and
  terminal commands, not just a browser chat. Review its actions before approving.
- A trusted Wi-Fi router or phone hotspot that both devices can join. Avoid public
  and guest Wi-Fi. Some hotspots block devices from talking to each other.
- Internet access for the downloads. No GitHub account is needed to download this project.

**Two places to type:** **Termux** runs on the head unit; the **laptop terminal**
runs on your computer. Never swap their commands. Type one line, press **Enter**,
then type the next. Do not type the surrounding code-box marks.

### 1. Install Termux on the Android head unit

**Where: head unit.** Termux is an app that gives you a text-command window.

1. Open the unit's web browser and visit
   [Termux on F-Droid](https://f-droid.org/en/packages/com.termux/).
   If it needs internet first, join your trusted Wi-Fi now.
2. Scroll to the latest compatible version and tap **Download APK**.
   An APK is an Android app installer. You do **not** need to install the
   F-Droid store itself.
3. Open the downloaded file. If Android asks, allow this browser/file manager
   to **Install unknown apps** for this installation only, then tap **Install**.
   On older menus the switch may be called **Unknown sources**. Turn that
   permission back off afterward.
4. Open **Termux** and wait for its first-time setup. You should see a text
   window with a prompt, often ending in `$`, where you can type.

Use the official source above, not an APK from a random video or file-sharing
site. The fully supported Termux app/package environment requires Android 7+;
our unit is actually Android 8.1 despite higher version labels in its menus.
If Termux is already installed, do not mix F-Droid and GitHub versions/plugins
or uninstall it without backing up its data. See the
[official installation notes](https://github.com/termux/termux-app#installation).

**Checkpoint:** Termux opens and lets you type. You do not need to install
extra Termux packages to run the commands in step 5.

### 2. Connect the head unit and laptop to the same Wi-Fi

**Where: both devices.** Open Wi-Fi settings on each and select the **same
network name**. A private phone hotspot can work if it allows connected devices
to communicate. Keep the laptop on this network throughout the session.

**Checkpoint:** both show a connection to the same trusted network. Internet
working on both devices alone does not prove they can reach each other.
Never forward port 5555 on your router or expose it to the internet.

### 3. Enable Developer options on the head unit

**Where: head unit, Settings app — not Termux.** This reveals Android's
maintenance switches; it does not mean you need to write code.

1. Open **Settings → About device / About tablet / About machine**.
   Some units put this under **System** or a separate Android settings screen.
2. Find **Build number** and tap it **seven times**, until Android says
   **You are now a developer** (or says it is already enabled).
3. Go back and open **Developer options**, sometimes under **System**.
   If there is a master switch, turn it on.
4. Find **USB debugging**. You will turn this on in step 4, even though the
   connection will ultimately use Wi-Fi.

If your manufacturer already shows a password-protected **Developer options**
entry, use that entry and read step 4. Do not enter Factory reset or change
unrelated car settings to look for it.

### 4. If asked for a password, distinguish the two prompts

**Where: head unit, Settings app.** Some firmware has separate passwords for
opening Developer options and enabling USB debugging.

| Prompt | Community-reported value — not a universal password |
| --- | --- |
| **USB debugging** password | `john@tw-desktop` — lowercase, no spaces, ordinary hyphen |
| **Developer options** entry password, on some firmware | `7890` followed by the **two-digit hour on the head unit's clock**, in 24-hour time. At 8:28 PM, this is `789020`; at 2:07 AM, `789002`. |

These values are reported in an
[XDA discussion, post #4](https://xdaforums.com/t/im-looking-for-developer-mode-password.4022651/post-81268331),
with a follow-up success report for an ISUDAR H53/TS9 unit. **They are not
independently verified passwords for every T3L, or documented as tested on our
exact unit.** Use them only at the matching prompt on your own device. If
rejected, stop and ask your seller for the correct code for your model/firmware.
Do not cycle through random factory/reset codes — some can erase settings.

If no password is requested, skip the password entry. Turn **USB debugging ON**
and accept Android's warning. Leave other developer settings alone.

**Checkpoint:** USB debugging is visibly enabled.

### 5. Enable the head unit's network connection on TCP port 5555

**Where: Termux on the head unit.** Open Termux and enter these two lines:

```sh
/system/bin/setprop service.adb.tcp.port 5555
/system/bin/setprop ctl.restart adbd
```

This tells **ADB (Android Debug Bridge)**, Android's maintenance connection,
to listen for your laptop on port **5555**, then restarts that connection
service. It is **not** a broadcast, and it does not restart the whole head unit.
Normally the commands return to the prompt without a success message.

> **Firmware-specific:** this no-root method worked on our unit's permissive
> vendor firmware, as recorded in [the helper script](launcher-proposal/adb_tcp5555.sh).
> Normal Android builds usually block an ordinary app from doing this. If you
> see **Permission denied**, **Failed to set property**, or a similar error,
> **stop**. Do not use `su`, root the unit, or disable security protections to
> force it. Ask the seller about a supported network-debugging method, or use
> [Android's documented USB-first ADB method](https://developer.android.com/tools/adb#wireless)
> if your unit actually has a supported USB device/debug port. Not every
> head-unit USB socket supports that.

You do not need `adb pair` or a QR code for this Android 8.1 method.
**Checkpoint:** no command errors. This is not proof the port is reachable yet;
step 8 checks the actual laptop connection.

### 6. Find and write down the head unit's IP address

**Where: head unit.** Open **Settings → Wi-Fi**, tap the connected network
(or its details/gear icon), and find **IP address**. Some units show it under
**About device → Status** instead.

Write down the head unit's address, **not** the laptop's address or the router's
gateway. For the examples below, pretend it is **192.168.1.50**.

**Replace `192.168.1.50` in every command below with the address you actually
see.** Keep `:5555` at the end. The example is not our real device address.
Check it again after reconnecting Wi-Fi or rebooting; it may change.

### 7. Prepare the laptop and open this project in your AI assistant

**Where: laptop.** On this GitHub page, click **Code → Download ZIP**, extract
the ZIP, and open the extracted project folder in your local AI coding assistant.
You do not have to create a repository or publish anything.

Paste this into your assistant:

> I am a beginner setting up my own Android head unit. This folder is the
> T3L Revival project. Help me install Android SDK Platform-Tools (adb) and
> Python 3 for my laptop's operating system, using official/trusted sources.
> Explain any installation or PATH changes and ask before making them.
> Check that adb and Python run in the terminal this project uses. Do not
> change anything on the head unit yet.

The official download is
[Android SDK Platform-Tools](https://developer.android.com/tools/releases/platform-tools).
You do not need the full Android Studio application. **PATH** just means the
laptop knows where to find a command such as `adb`. Ask the assistant to fix
that if the terminal says **command not found** or **not recognized**.

**Checkpoint:** `adb version` prints a version on the laptop. Python 3 is
available too; its command may be `python3`, `python`, or `py -3` on Windows.

### 8. Connect from the laptop and approve it on the head unit

**Where: laptop terminal** (your assistant can run these with your approval).
Replace the example IP first:

```sh
adb connect 192.168.1.50:5555
adb devices -l
```

Watch the **head unit screen** for **Allow USB debugging?**. Despite its name,
this also authorizes this network ADB connection. Approve only the connection
you just initiated from your trusted laptop. Select **Always allow from this
computer** only if it is your own trusted laptop.

Run `adb devices -l` again on the laptop. Success looks like:

```text
List of devices attached
192.168.1.50:5555    device
```

**Checkpoint:** the address is followed by **device**, not **unauthorized** or
**offline**. A `connected to ...` message alone is not enough.

| What you see | What to do next |
| --- | --- |
| `unauthorized` / authentication failure | Check the head unit for the approval prompt, approve your laptop, then reconnect. If no prompt appears, stop and ask your assistant/seller; do not bypass authorization. |
| Connection refused | Recheck the IP and step 5. The ADB listener may not have started. |
| Timed out / no route to host | Recheck both Wi-Fi connections. Guest networks, hotspot client isolation, VPNs or firewall rules may block the connection; do not disable your firewall wholesale. |
| `offline` | Try `adb disconnect 192.168.1.50:5555`, then reconnect. |
| Property commands failed in Termux | Your firmware does not allow this method. Stop rather than trying root workarounds. |

### 9. Ask your AI assistant to inspect first — not debloat or install

**Where: your laptop's AI assistant.** Replace the example IP, then paste:

> My own head unit is connected through ADB at 192.168.1.50:5555. Read this
> project's README, hardware-report.md and recovery-plan.md first. Verify the
> connected device's identity, actual Android API, firmware and current launcher;
> do not assume it matches the example unit. Use this explicit address for all
> device commands. Inspect collect-readonly.py and explain what it collects.
> Ask before collecting logs: they can contain identifiers, account or location
> data, and I want to review/redact them before sharing with an AI service.
> Start with read-only diagnostics only. Do not root, flash, uninstall, disable
> apps, change HOME, broadcast vehicle commands or change MCU/CAN/standby settings.
> Summarize what you find in plain English and propose reversible next steps
> with a recovery plan. Wait for my approval before any device change.

If you approve collection, the assistant can run this **from the extracted
project folder on the laptop** (with your real IP and Python 3 command):

```sh
python3 collect-readonly.py --serial 192.168.1.50:5555
```

This saves a timestamped private folder under `evidence/` on the laptop.
Some queries can be slow or permission-denied; do not retry with elevated
privileges. This is a diagnostic snapshot, **not a complete device backup**.

**Want the launcher in the picture?** After reviewing your device's report,
ask your assistant to review the [launcher source/build guide](launcher-proposal/README.md)
and [recovery plan](recovery-plan.md). The public repo is source-only: it has
no ready-to-install APK and no original signing key. Building, testing,
installing and changing the default home screen are **separate, approval-gated
steps**, not automatic consequences of connecting. Keep the stock launcher
available until you have verified a way back; do not copy this unit's Theme
uninstall as a beginner step.

### 10. Turn network debugging off when finished

**Where: Termux on the head unit**, once you no longer need the laptop connection:

```sh
/system/bin/setprop service.adb.tcp.port -1
/system/bin/setprop ctl.restart adbd
```

Then turn **USB debugging OFF** in Developer options. If you no longer want
the laptop trusted, use **Revoke USB debugging authorizations** too; this
revokes all previously trusted computers, not just this one.

**Verify from the laptop:** disconnect its saved connection, then try connecting
again using your actual head-unit address:

```sh
adb disconnect 192.168.1.50:5555
adb connect 192.168.1.50:5555
adb devices -l
```

While both devices remain on the same reachable Wi-Fi, the reconnect should
fail (normally **Connection refused**) and there should be no `device`
connection for that address. If it still responds as **unauthorized**, the
listener is still exposed — that is not successful closure. A timeout or lost
Wi-Fi alone also does not prove the port is closed.
**`adb disconnect` alone does not close the head unit's port.**
If the off commands fail or the listener still responds, keep the unit off
untrusted networks and get help verifying closure. Do not assume a reboot closes it on
every firmware. On our tested unit the enable setting is not persistent across
a cold boot; a later session may require steps 5, 6 and 8 again.

### Sources and compatibility notes

- [Official Termux installation guidance](https://github.com/termux/termux-app#installation)
  — supported versions and download sources.
- [Android Developer options](https://developer.android.com/studio/debug/dev-options#enable)
  — build-number taps and USB debugging; vendor menu layouts may differ.
- [Community password report](https://xdaforums.com/t/im-looking-for-developer-mode-password.4022651/post-81268331)
  — model-specific reports, not a manufacturer guarantee for T3L.
- [Official ADB guide](https://developer.android.com/tools/adb)
  — authorization, connection states and standard USB-first network debugging.
- [Our unit's TCP toggle helper](launcher-proposal/adb_tcp5555.sh) and
  [hardware/security findings](hardware-report.md) — why the Termux method
  worked here; this is not standard permission behavior on all Android units.

---

## Project records — optional reading after setup

Everything below records **our unit's** results, not a to-do list for yours.
For publishing your own project to GitHub instead, see [PUBLISHING.md](PUBLISHING.md).

### What is and is not in this repo

Published: the discovery reports, package inventory CSVs, and the
[launcher proposal](launcher-proposal/README.md) (native launcher source and
deployment scripts) under the MIT license.

Not published (kept private by `.gitignore`): the timestamped `evidence/`
folders with raw device dumps and copied vendor APKs, the `changes/` journals,
and `.private/` with the launcher signing keys — only the single final
launcher screenshot above was copied out as `screenshots/`. Repo readers
can regenerate their own evidence with `collect-readonly.py`.

### Current state — approved launcher optimisation applied

**T3L Drive 0.3.1 is installed/default HOME; Theme is now uninstalled for user 0,
including its user data—not merely disabled.** Headunit Reloaded is preserved.
Standby settings were not changed. The factory ROM copy was not erased.
See [current removal scope and recovery limits](theme-removal.md),
[current 75-package inventory](package-inventory-current.csv), and
[earlier launcher optimisation/measurements](optimization-report.md).
The original reports/75-package CSV below are the discovery baseline; the
[initial post-change inventory](package-inventory-after.csv) contains 76 packages
and records the earlier disabled-Theme state, before the subsequent uninstall.

### Reports

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

<details>
<summary>Technical notes: collection, historical evidence and offline tests</summary>

Collection instructions are in step 9 above. Diagnostic dumps themselves create
transient workload and logs; they are not zero-impact idle benchmarks.

The script never invokes `su`, changes permissions/settings, sends vehicle
commands, launches activities, clears logs or disables packages. Unsupported
and permission-denied queries are recorded. Some optional dumps can be slow;
do not interpret failures as absent features or retry with elevated privileges.
Copying the ten selected APKs was a separate read-only host-copy step, recorded
in the first evidence run's `apks/pull-manifest.json`.

The commands below describe our original offline analysis (no device interaction).
**The timestamped folders are private and are not in a public download.** The
historical evidence tests depend on those original files and some local build
artifacts; a fresh clone cannot reproduce all 14 checks. New device evidence
must be assessed separately rather than treated as the original test fixture.

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
HUR/standby and the launcher build at that stage. **All 14 passed at that stage.**
These offline tests do not themselves launch apps or
validate vehicle functions; actual compilation, signing, installation and UI
checks are recorded separately in the optimisation report and journals.
The interrupted `20261021T063740.413028Z` attempt has its own note
and is not treated as a completed evidence run.

</details>

## License

[MIT](LICENSE). Placeholders such as `<unit-ip>` and `<your-ssid>` in the docs
are yours to fill in when reproducing the collection.
