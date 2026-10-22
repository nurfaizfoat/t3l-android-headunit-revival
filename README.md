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

## Our wins — before and after

Here is what we observed on **our unit**, not a promise for every head unit.
The screenshot above is **0.3.1**; the measurements below were taken at earlier,
explicitly named stages. We have not recorded an equivalent 0.3.1 comparison.

| What changed | Before: stock launcher | After: first launcher (0.1.0) | Later: dashboard + audit (0.2.1) |
| --- | ---: | ---: | ---: |
| **Launcher RAM use** (PSS; lower is better) | 83.6 MiB | **7.2 MiB** | **~9.9 MiB** |
| **Memory available to Android/apps** (higher is better) | 344.6 MiB | **427.1 MiB** | **401–407 MiB observed** |
| **Unused swap space** (SwapFree; higher means less swap occupied) | 129.6 MiB | **163.4 MiB** | **183.5 MiB** |
| Old Theme launcher process | Running | **Absent** — disabled for user 0 | **Absent** — later uninstalled for user 0 |

**In plain English:** the first replacement used about **91% less launcher RAM**
(~76.4 MiB less). The later dashboard sample was still about **88% lower** than
stock. More memory was available for other apps in the recorded snapshots.
MiB is a unit of memory; PSS estimates the launcher's share of physical RAM.
Swap is Android's overflow/compressed-memory area, **not extra physical RAM**.

**What we kept:** Headunit Reloaded (the Android Auto projection app) and the
factory radio/Bluetooth/EQ/vehicle stack. Existing standby settings were preserved;
there was no firmware flash or root invocation.

**Limits:** these are uncontrolled snapshots with different apps/background
activity, not a speed, cold-boot, battery-life or long-term stability benchmark.
The later audit also included other approved changes, so its differences cannot
all be attributed to the launcher. Thermal warnings remain unresolved. Physical
audio, camera and vehicle-control checks still need the owner while parked.
Sources: [initial before/after report](optimization-report.md#observed-memory-comparison)
and [later wins audit](optimization-audit.md#1-wins-achieved-so-far).

## Start here — connect your head unit to your AI laptop

**Follow in order:** head unit setup (**1–6**) → prepare the laptop and draft
your launcher (**7–8**) → connect and inspect before any installation (**9–10**)
→ close debugging when finished (**11**).

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
step 9 checks the actual laptop connection.

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

### 8. Create your own launcher with your AI assistant — on the laptop first

**Where: laptop, in the extracted project folder.** You describe the home screen
you want in everyday language; the assistant writes the code. **Designing and
building an app does not require a connection to the head unit.** At this stage
you are making a candidate app, not replacing the working home screen.

#### A. Describe what you want

Use our screenshot as a starting point, or give the assistant your own sketch.
Tell it:

- **Look:** colours, large readable text, day/night style, and tile arrangement.
- **Buttons:** Android Auto, Radio, Music, Bluetooth, Apps, Settings and EQ.
- **Behaviour:** open the existing apps when tapped; handle missing apps politely.
- **Escape route:** always keep Settings and a way back to the stock launcher.

For example: “A dark dashboard with cyan highlights, one big Android Auto tile
on the left, four smaller tiles on the right, and large Settings/EQ buttons.”
Use your own screen size when known; ours is **1024×600**.

#### B. Give your assistant this starter prompt

> Help me create my own lightweight Android car launcher using this project as
> a starting point. I do not know how to code. Work in a separate copy so the
> original source stays intact. First show me a proposed layout and explain
> which files you would change; wait for my approval before editing or building.
> My design is: [replace this with your colours, layout and buttons].
> Keep it native and lightweight: no WebView, background service, ads, tracking
> or unnecessary permissions. Keep Settings, an app picker and a recovery route.
> Start with ordinary shortcuts to existing apps. Do not carry over this unit's
> private radio protocol or network-ADB toggle without a separate compatibility
> and safety review. Use a distinct app identity for my new launcher so it cannot
> overwrite an existing launcher; update all affected source/manifest references.
> Read the actual current source and AndroidManifest.xml, not just historical
> version notes. Use this repo's API-27/1024×600 setup only as a provisional
> starting point until we inspect my device in step 10. Review the build scripts,
> check my laptop's prerequisites and explain downloads before running anything.
> Do not connect to, install on, or change the head unit during this step.

You do not need to edit Java yourself. For reference, the main files are:

| File in `launcher-proposal/` | What your assistant changes there |
| --- | --- |
| `src/local/t3l/launcher/DashboardView.java` | Layout, colours, text and touch targets |
| `src/local/t3l/launcher/MainActivity.java` | What happens when a button is tapped |
| `src/local/t3l/launcher/AppTargets.java` | Which existing app each shortcut opens — verify these on your own device later |
| `res/drawable/` | Icons and artwork |
| `AndroidManifest.xml` | App identity, Android compatibility, permissions and home-screen entry |

#### C. Approve a local build and keep your signing key

Once you like the proposed design, ask the assistant to build an **APK** — the
Android app installer — **on the laptop only**. The supplied build path was used
on Linux; it downloads **Linux build tools** and uses Linux paths. On Windows
or macOS, ask the assistant to propose an adapted toolchain or compatible Linux
environment first. Do not assume the commands below work unchanged there.

On a compatible Linux laptop, after the assistant checks **Python 3.9+**, a
compatible **Java runtime**, **OpenSSL** and the downloaded tools' host requirements,
these commands run **inside your working copy's `launcher-proposal/` folder**:

```sh
python3 bootstrap-tools.py
python3 build.py
```

The first downloads and checks the build tools. The second compiles and signs
the app. Neither script installs it or contacts the head unit. Stop if a command
fails and ask the assistant to explain the error rather than skipping checks.

Ask the assistant to show you:

- The APK path recorded in `launcher-proposal/build/latest.json`; the actual
  file is in `launcher-proposal/build/<timestamp>/t3l-drive.apk`.
- Its size, hash, signature-verification result and requested permissions.
- Where your signing files are kept: `.private/` at the project root. On a clean
  copy, the build creates a new identity if no signing files exist. **Back these
  up privately and never overwrite or publish them.** Future updates need the
  same identity; your key cannot update our original signed installation.
- A preview, if a compatible emulator is available. Treat a proposed layout
  or mockup as a design aid, not proof it works on the actual head unit.

**Checkpoint:** you have a locally built candidate APK and a backed-up signing
identity. **Do not install or select it as HOME yet.** Continue with steps 9–10
to check device compatibility, map its actual apps and plan recovery. If you
only want to inspect your device for now, you can skip this optional creation
step and come back after step 10.

### 9. Connect from the laptop and approve it on the head unit

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

### 10. Inspect the device, then review your launcher before installing

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

**Ready to try your launcher from step 8?** After reviewing the device report,
ask your assistant to review the [launcher source/build guide](launcher-proposal/README.md),
the **current source/manifest**, and [recovery plan](recovery-plan.md). Some build
guide prose describes earlier releases; the manifest currently identifies 0.3.1.
The public repo has no ready-made APK or original signing key. Ask the assistant
to walk through these gates, **one approval at a time**:

1. **Adapt and rebuild:** match your actual Android API, screen size and installed
   app destinations. Remove unsupported/vendor-specific features. Check the
   final APK's identity, permissions and signing key.
2. **Plan recovery before installation:** record the existing HOME app and a
   verified route back to it through Settings/ADB. Keep the stock launcher
   installed, enabled and available. Do not blindly run `deploy.py` stages:
   they were written for our specific firmware, package and recovery records.
3. **Install only after approval:** open the candidate as a normal app first,
   without making it the default home screen. Check its layout, every shortcut,
   Settings escape, crashes and RAM use. A shortcut opening an app does not
   prove the speakers, camera or vehicle controls still work — check while parked.
4. **Choose it as HOME only after testing:** ask the assistant to explain your
   device's default-home selection and rollback procedure, then approve that
   separate change. Keep the old launcher available while validating daily use.

**Checkpoint:** either you stop safely at inspection, or you have tested your
own launcher and know how to return to stock. Removing Theme is **not required**
to create or try a launcher; do not copy our later uninstall as a beginner step.

### 11. Turn network debugging off when finished

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
a cold boot; a later session may require steps 5, 6 and 9 again.

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

Collection instructions are in step 10 above. Diagnostic dumps themselves create
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
