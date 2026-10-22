# Optimization audit — 2026-10-21 (no-root)

Evidence: `evidence/20261021T083200.534162Z-optimization-audit/`
Applied-change journal: `changes/20261021T073131*-memory-audit-changes/`
(third-party re-run `20261021T084209.960191Z-memory-audit-changes/` if present).

## 1. Wins achieved so far

| Metric | Stock baseline | After 0.1.0 | Current 0.2.1 (post-audit changes) |
|---|---:|---:|---:|
| Launcher process PSS | 83.6 MiB | 7.2 MiB | ~9.9 MiB (launcher only) |
| MemAvailable | 344.6 MiB | 427.1 MiB | 401–407 MiB observed |
| SwapFree (256 MiB zram) | 129.6 MiB | 163.4 MiB | 183.5 MiB |
| Stock Theme process | running | removed for user 0 | absent |
| Launcher services/WebView | heavy | 0 | 0 |
| Package count | 75 (+later 76) | — | 75 minus Theme; Aptoide + FOTA now disabled-user |

Earlier gaps are explained, not decay: apps opened during UI verification
(Settings, Chrome, HUR, TW activities) legitimately hold RAM until they are
needed or the unit cold-boots.

## 2. Where RAM goes today (top offenders, 24 h procstats)

| Consumer | RAM | 24 h presence | Status |
|---|---:|---|---|
| GMS stack (4 procs) | ~168 MB | persistent | untouched — Android Auto / fallback risk |
| Chrome + WebView sandbox | ~98 MB | foreground-grade | untouched — `com.android.chrome` is the WebView provider |
| SystemUI/phone/IME | ~46 MB | persistent | needed |
| TW vehicle stack | ~90 MB | persistent | untouched — vehicle/MCU |
| Termux | up to 53 MB (now 15.8) | 23% of 24 h | **kept on owner request** |
| Aptoide | ~10–15 MB + jobs | system-job wakelocks | **disabled-user 0 (this audit)** |
| `com.abupdate.fota_demo_iot` | 7–12 MB | service 100% of uptime + wakelocks | **disabled-user 0 (this audit)** |
| Residuals (Settings, installer, cached HUR) | ~60 MB | transient | recede on their own / cold boot |

## 3. Applied changes (all reversible from shell, no root)

| Change | Command | Revert |
|---|---|---|
| Disable Aptoide | `pm disable-user --user 0 cm.aptoide.pt` | `pm enable --user 0 cm.aptoide.pt` |
| Disable FOTA auto-updater | `pm disable-user --user 0 com.abupdate.fota_demo_iot` | `pm enable --user 0 com.abupdate.fota_demo_iot` |
| Animation scales → 0 | `settings put global window_animation_scale 0` (+ `transition_animation_scale`, `animator_duration_scale`) | same commands with `1.0` or `settings delete` |

Verified after: `pm list packages -d` shows both new entries; visual gesture output
runs with zero animation durations; HOME still `local.t3l.launcher`; crash buffer
clean; `com.tw.*`, HUR, Chrome, GMS unchanged.

## 4. Considered but rejected / not applicable

| Item | Reason |
|---|---|
| Force-stopping Chrome | WebView provider here is `com.android.chrome`; force-stop is known to break WebView rendering until reboot on this API level |
| Touching GMS / SystemUI / TW persistent services | vehicle behavior + Play dependency live there; stability > a few MB |
| Disabling Termux | owner wants it available |
| `/system` 99% full (10 MB free) | no-root cannot shrink partitions; large TOPWAY OTA payloads are effectively blocked by this |
| Doze / battery-optimization changes for TW apps | risk of breaking vehicle wake behaviour, no measurable RAM win |
| `speed-profile` re-compile of launcher/HUR | offered 2026-10-21, owner chose A+B+C only; can be applied on request |

## 5. Actual applied package/settings state (2026-10-21 EOF)

- Third-party: `gb.xxy.hr`, `local.t3l.launcher`, `com.termux` (enabled);
  `cm.aptoide.pt` disabled-user.
- System disabled-user: `com.abupdate.fota_demo_iot` (this audit),
  `com.tw.carchoose` (pre-existing factory baseline), plus Play/WebView-stack
  fallback pair `com.android.vending`, `com.google.android.webview` (pre-existing).
- Global settings written: `window_animation_scale=0`,
  `transition_animation_scale=0`, `animator_duration_scale=0`.
- Untouched as owner-configured: `secure sleep_timeout=-1`,
  `system screen_off_timeout=2147483647`, `global wifi_sleep_policy=2`.

## 6. Remaining known issues (unchanged)

- Thermal zones still read ~93/91 °C with previous trip events in the log; this
  is hardware airflow and not fixable by software from shell.
- Installation-time dexopt for installed apps is `quicken`; `speed-profile`
  re-compile of HUR + launcher was offered but not applied in this round.
  Runtime estimate: improved app cold-start, reversible via a normal bg-dexopt.
- One-off housekeeping (`am kill-all`, `pm trim-caches`) is available as a
  manual cleanup after long sessions; processes restart on demand.
