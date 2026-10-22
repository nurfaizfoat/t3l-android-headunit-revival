# T3L Revival

![T3L Drive 0.3.1 home launcher on the head unit](screenshots/t3l-drive-0.3.1-home.png)

*T3L Drive 0.3.1 on our head unit, captured 21 October 2026.*

A lightweight home screen for an old TOPWAY/Allwinner T3L Android car stereo,
built with an AI coding assistant. Follow the steps below to connect your unit
and create your own launcher, without writing code yourself.

> Work while parked, on a unit you own. Our unit runs Android 8.1 / API 27;
> passwords and permissions vary. Keep the stock launcher available. Do not
> root, flash firmware or change vehicle/MCU/CAN settings to follow this guide.

## Our wins

| Measurement | Before: stock | First replacement (0.1.0) | Later dashboard audit (0.2.1) |
| --- | ---: | ---: | ---: |
| Launcher RAM use, lower is better | 83.6 MiB | **7.2 MiB** | **~9.9 MiB** |
| Memory available for apps | 344.6 MiB | **427.1 MiB** | **401–407 MiB** |
| Free swap space | 129.6 MiB | **163.4 MiB** | **183.5 MiB** |
| Old launcher process | Running | **Absent** | **Absent** |

About **91% less launcher RAM initially**, and **88% less in the later audit**.
Headunit Reloaded, factory radio/Bluetooth/EQ and standby settings were preserved.

These are uncontrolled snapshots, not guaranteed speed or battery gains. The
later audit included other changes; 0.3.1 has no equivalent comparison. Thermal
warnings remain unresolved. [Initial results](optimization-report.md#observed-memory-comparison)
and [later audit](optimization-audit.md#1-wins-achieved-so-far).

## Android Auto: our setup

For my setup, I removed the stock map apps, then installed **Headunit Reloaded
(HUR)** to use Android Auto. This was separate from the launcher work documented
here: HUR was already installed and no standalone map app remained when we
[audited the unit](optimization-report.md#outcome).

**What is HUR?** [Headunit Reloaded Emulator HUR](https://play.google.com/store/apps/details?id=gb.xxy.hr)
is a paid Android app, listed under AAWireless, that turns an Android head unit
or tablet into an **Android Auto receiver**. Your Android phone provides the
Android Auto experience, including compatible navigation, music and calling
apps, on the stereo's screen. It is not a map app or our custom launcher.

To try it on your own unit, while parked:

1. **Install HUR on the head unit** from the official Google Play listing above.
   Check compatibility and the current price before buying.
2. **Set up Android Auto on your Android phone.** Keep your navigation and
   music apps on the phone; they do not need to be installed on the head unit.
3. **Start with USB:** open HUR, connect the phone to a compatible head-unit
   USB port with a data-capable cable, and approve the connection prompts.
4. **For wireless**, follow the instructions in your installed HUR version.
   Support depends on your phone and app versions. The current release notes
   warn that Android Auto 17.4 broke older wireless startup methods.
5. **Open the Android Auto tile in T3L Drive** to launch HUR. The tile is a
   shortcut, not a built-in Android Auto implementation.

Removing stock map apps is **optional cleanup, not required for Android Auto**.
Keep a recovery path before removing anything, and leave Google services,
location providers and vehicle-control apps alone. For help, use the
[developer's support thread](https://xdaforums.com/t/android-4-1-headunit-reloaded-for-android-auto-with-wifi.3432348/).

## What you need

- An Android head unit with internet access and permission to install apps.
- A laptop with a local AI coding assistant that can use files and a terminal.
- Trusted Wi-Fi or a private hotspot that allows both devices to communicate.

**Termux commands go on the head unit. Laptop commands go on the laptop.**
Enter one line at a time, pressing Enter after each. Review your assistant's actions.

## Step by step

### 1. Install Termux

**On the head unit:**

1. Open [Termux on F-Droid](https://f-droid.org/en/packages/com.termux/) in its browser.
2. Tap **Download APK** for a compatible version, then open the downloaded installer.
3. If asked, allow **Install unknown apps**, install Termux, then turn that permission off.
4. Open Termux and wait until its text-command prompt appears.

Use this official source, not random APK sites. Full Termux support requires
Android 7+. If already installed, do not mix F-Droid and GitHub versions.

### 2. Join the same Wi-Fi

**On both devices:** connect the head unit and laptop to the **same network name**.
Avoid public or guest Wi-Fi. Never expose port 5555 to the internet.

### 3. Enable Developer options

**On the head unit, in Settings:**

1. Open **About device / About tablet / About machine**.
2. Tap **Build number seven times** until developer mode is enabled.
3. Go back and open **Developer options**, sometimes under **System**.

If the manufacturer already shows a protected Developer options entry, open it
and continue below. Do not enter Factory reset.

### 4. Enable USB debugging

**On the head unit:** turn **USB debugging ON**, even though you will use Wi-Fi.
If prompted for a password:

| Prompt | Community-reported password |
| --- | --- |
| USB debugging | `john@tw-desktop` (lowercase, no spaces) |
| Developer options, on some firmware | `7890` + the head unit's current two-digit hour in 24-hour time. At 8 PM: `789020`. |

These [community reports](https://xdaforums.com/t/im-looking-for-developer-mode-password.4022651/post-81268331)
are **not verified for our exact T3L or universal**. If rejected, ask your seller;
do not try random factory/reset codes. If no password is requested, skip it.

### 5. Enable network ADB on port 5555

**In Termux on the head unit:**

```sh
/system/bin/setprop service.adb.tcp.port 5555
/system/bin/setprop ctl.restart adbd
```

This enables ADB, Android's maintenance connection, to listen on port 5555.
No output is normal. **This method depends on our unit's permissive firmware.**
If you see permission/property errors, stop and ask your seller about supported
ADB access. Do not use root workarounds. Step 9 checks whether it actually connects.

### 6. Find the head unit's IP address

**On the head unit:** open **Settings → Wi-Fi → connected network → details**
and write down its **IP address**. It may also appear under **About → Status**.

Below, `192.168.1.50` is only an example. **Replace it in every command and
prompt with your head unit's actual IP**, keeping `:5555`. It can change after reconnecting.

### 7. Prepare your laptop

**On the laptop:** click this page's **Code → Download ZIP**, extract it, and open
the project folder in your AI coding assistant. No GitHub account is needed.
Paste this:

> Help me install official Android SDK Platform-Tools (adb) and Python 3 for
> my laptop. Ask before installing or changing anything. Check that adb and
> Python run in this project's terminal. Do not change the head unit yet.

Check that `adb version` prints a version. The official download is
[Platform-Tools](https://developer.android.com/tools/releases/platform-tools).

### 8. Create your own launcher

**On the laptop:** describe your colours, layout and buttons to the assistant.
Use our screenshot or your own sketch. Paste this and replace the design description:

> Create a lightweight native Android launcher from this project in a separate
> working copy. My design is: [describe colours, layout and buttons]. Show me
> the layout before coding. Keep Settings, an app picker and a route back to
> stock. Use simple app shortcuts, a distinct app identity and minimal
> permissions. No ads, tracking or background services. Leave vendor radio
> commands and the network-ADB toggle out pending compatibility review.
> Ask before editing, downloading tools or building. Build only on the laptop;
> do not install anything yet. Verify device compatibility after step 10.

After approving the design, ask it to build an **APK**, the Android installer.
The supplied scripts use **Linux tools and paths**. On Windows/macOS, ask the
assistant to adapt the toolchain first.

On compatible Linux, have it check Python 3.9+, Java and OpenSSL, then run these
**inside your working copy's `launcher-proposal/` folder**:

```sh
python3 bootstrap-tools.py
python3 build.py
```

Ask for the APK path from `build/latest.json` and confirmation that signing
verification passed. **Back up `.private/` securely**; its signing keys are needed
for updates and must never be published. Your key cannot update our original
signed installation. Do not install or make the app your home screen yet.

### 9. Connect and authorize your laptop

**In the laptop terminal**, with your actual IP:

```sh
adb connect 192.168.1.50:5555
adb devices -l
```

**On the head unit:** approve **Allow USB debugging?** for your trusted laptop.
Run `adb devices -l` again. You want:

```text
192.168.1.50:5555    device
```

If it says **unauthorized**, check the approval prompt. If refused, recheck
step 5 and the IP. If it times out, check shared Wi-Fi and hotspot isolation.
Do not bypass authorization or disable your firewall wholesale.

### 10. Inspect, test, then choose your launcher

**In your laptop's AI assistant**, paste this with your actual IP:

> Inspect my unit at 192.168.1.50:5555 using read-only checks first. Verify its
> Android API, firmware, screen size, installed apps and current home screen.
> Read recovery-plan.md and the current launcher source/manifest. Ask before
> collecting logs, which may contain private data. Adapt my launcher to this
> device and explain recovery before installation. Do not root, flash, remove
> apps or change vehicle/standby settings. Ask separately before installing
> and before changing the default home screen.

Then approve these stages one at a time:

1. **Review and rebuild** for your actual device. Review/redact logs before sharing.
2. **Confirm a way back** to stock. Keep the stock launcher installed and enabled.
3. **Install and open as a normal app first.** Test buttons, Settings escape,
   crashes, audio, Android Auto, camera and vehicle controls while parked.
4. **Choose it as the default home screen only after testing**, with a clear rollback plan.

Do not blindly run `deploy.py`; it targets our specific unit. Removing Theme
is not required. See the [build guide](launcher-proposal/README.md) and
[recovery plan](recovery-plan.md) for details; older release notes are historical.

### 11. Turn network debugging off

**In Termux on the head unit:**

```sh
/system/bin/setprop service.adb.tcp.port -1
/system/bin/setprop ctl.restart adbd
```

Turn **USB debugging OFF** in Settings. **On the laptop**, using your actual IP:

```sh
adb disconnect 192.168.1.50:5555
adb connect 192.168.1.50:5555
```

While both remain on reachable Wi-Fi, reconnection should fail, normally with
**Connection refused**. An `unauthorized` response means the port is still open;
a timeout alone does not prove closure. If it still responds, get help and keep
the unit off untrusted networks. Disconnecting the laptop alone does not close the port.

## More details

- [Hardware and security](hardware-report.md)
- [Launcher source and build](launcher-proposal/README.md)
- [Recovery plan](recovery-plan.md)
- [Applied changes and measurements](optimization-report.md)
- [Later optimization audit](optimization-audit.md)

Raw device evidence, vendor APKs and signing keys are not included in this repo.

## License

[MIT](LICENSE).
