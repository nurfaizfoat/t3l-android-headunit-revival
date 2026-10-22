#!/usr/bin/env python3
"""Collect private host-side evidence using an explicit ADB serial.

No root invocation, writes, installs, activity launches, broadcasts, Binder
transactions, device-node reads, setting changes or reboots are performed.
Some queries are unsupported or permission-denied on vendor builds; preserve
their errors rather than retrying with greater privileges.
"""

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import time


# Shell fragments here are fixed, read-only queries. Never interpolate serials
# or externally supplied paths into a device shell command.
QUERIES = [
    ("identity", "id"),
    ("properties", "getprop"),
    ("kernel", "uname -a"),
    ("cpu", "cat /proc/cpuinfo"),
    ("meminfo", "cat /proc/meminfo"),
    ("uptime", "cat /proc/uptime"),
    ("storage", "df -k"),
    ("partitions", "cat /proc/partitions"),
    ("mounts", "cat /proc/mounts"),
    ("root-paths", "ls -l /system/xbin/su /system/bin/su /sbin/su /su/bin/su"),
    ("selinux", "getenforce"),
    ("display-size", "wm size"),
    ("display-density", "wm density"),
    ("display", "dumpsys display"),
    ("graphics", "dumpsys SurfaceFlinger"),
    ("services-list", "service list"),
    ("dumpsys-list", "dumpsys -l"),
    ("users", "pm list users"),
    ("packages", "pm list packages -f"),
    ("packages-system", "pm list packages -s"),
    ("packages-user", "pm list packages -3"),
    ("packages-disabled", "pm list packages -d"),
    ("packages-enabled", "pm list packages -e"),
    ("package-help", "cmd package help"),
    ("package-details", "dumpsys package"),
    ("android-package", "dumpsys package android"),
    ("launcher-activities", "cmd package query-activities --brief -a android.intent.action.MAIN -c android.intent.category.LAUNCHER"),
    ("home-activities", "cmd package query-activities --brief -a android.intent.action.MAIN -c android.intent.category.HOME"),
    ("default-home", "cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME"),
    ("boot-receivers", "cmd package query-receivers --brief -a android.intent.action.BOOT_COMPLETED"),
    ("locked-boot-receivers", "cmd package query-receivers --brief -a android.intent.action.LOCKED_BOOT_COMPLETED"),
    ("activity-processes", "dumpsys activity processes"),
    ("activity-services", "dumpsys activity services"),
    ("activity-activities", "dumpsys activity activities"),
    ("memory", "dumpsys meminfo"),
    ("processes", "ps -A"),
    ("process-arguments", "ps -A -o PID,PPID,USER,NAME,ARGS"),
    ("cpu-load", "dumpsys cpuinfo"),
    ("swaps", "cat /proc/swaps"),
    ("vmstat", "cat /proc/vmstat"),
    ("memory-pressure", "cat /proc/pressure/memory"),
    ("zram", "for d in /sys/block/zram*; do for n in disksize mm_stat orig_data_size compr_data_size mem_used_total comp_algorithm; do f=$d/$n; if [ -r \"$f\" ]; then echo \"$f\"; cat \"$f\"; fi; done; done"),
    ("memory-policy", "for f in /proc/sys/vm/swappiness /proc/sys/vm/min_free_kbytes /sys/module/lowmemorykiller/parameters/adj /sys/module/lowmemorykiller/parameters/minfree; do if [ -r \"$f\" ]; then echo \"$f\"; cat \"$f\"; fi; done"),
    ("cpu-policy", "for d in /sys/devices/system/cpu/cpu[0-9]*/cpufreq; do for n in scaling_governor scaling_available_governors scaling_min_freq scaling_max_freq scaling_cur_freq cpuinfo_min_freq cpuinfo_max_freq; do f=$d/$n; if [ -r \"$f\" ]; then echo \"$f\"; cat \"$f\"; fi; done; done"),
    ("thermal", "for d in /sys/class/thermal/thermal_zone*; do for n in type temp; do f=$d/$n; if [ -r \"$f\" ]; then echo \"$f\"; cat \"$f\"; fi; done; done"),
    ("settings-system", "settings list system"),
    ("settings-global", "settings list global"),
    ("settings-secure", "settings list secure"),
    ("power", "dumpsys power"),
    ("device-idle", "dumpsys deviceidle"),
    ("alarm", "dumpsys alarm"),
    ("jobs", "dumpsys jobscheduler"),
    ("procstats", "dumpsys procstats --hours 3"),
    ("boot-events", "logcat -d -b events -v threadtime -t 1200"),
    ("recent-log", "logcat -d -v threadtime -t 1200"),
    ("kernel-log", "dmesg"),
    ("pstore-list", "ls -l /sys/fs/pstore /proc/last_kmsg"),
    ("init-list", "ls -l /init*.rc /system/etc/init /vendor/etc/init"),
    ("init-config", "for f in /init*.rc /system/etc/init/*.rc /vendor/etc/init/*.rc; do if [ -r \"$f\" ]; then echo \"FILE: $f\"; cat \"$f\"; fi; done"),
    ("vendor-device-names", "ls -l /dev"),
    ("audio", "dumpsys audio"),
    ("audio-policy", "dumpsys media.audio_policy"),
    ("bluetooth", "dumpsys bluetooth_manager"),
    ("camera", "dumpsys media.camera"),
    ("ending-meminfo", "cat /proc/meminfo"),
    ("ending-uptime", "cat /proc/uptime"),
    ("cpu-governor-explicit", "ls -l /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq; cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq"),
    ("thermal-trips", "for d in /sys/class/thermal/thermal_zone*; do for f in \"$d\"/trip_point_*_temp \"$d\"/trip_point_*_type; do if [ -r \"$f\" ]; then echo \"$f\"; cat \"$f\"; fi; done; done"),
    ("vendor-config-list", "ls -l /system/etc /vendor/etc /vendor/etc/init/hw /sys/class/sunxi_info /sys/class/disp /sys/class/switch /sys/class/car_reverse"),
    ("vendor-init", "for f in /vendor/etc/init/hw/*.rc; do if [ -r \"$f\" ]; then echo \"FILE: $f\"; cat \"$f\"; fi; done"),
    ("thermal-config", "cat /system/etc/thermal_sensor_config.xml /vendor/etc/thermal_sensor_config.xml /system/etc/thermal-engine.conf"),
    ("dmesg-counters", "cat /proc/vmstat"),
    ("framework-list", "ls -l /system/framework"),
    ("registered-broadcasts", "dumpsys activity broadcasts"),
    ("webview-provider", "dumpsys webviewupdate"),
    ("print-state", "dumpsys print"),
    ("boot-storage-config", "cat /vendor/etc/fstab.sun8iw11p1 /system/bin/appsdisable /system/bin/z-link.sh /system/bin/insmodlate.sh"),
    ("thermal-cooling", "for d in /sys/class/thermal/cooling_device*; do for n in type cur_state max_state; do f=$d/$n; if [ -r \"$f\" ]; then echo \"$f\"; cat \"$f\"; fi; done; done"),
    ("pm-help", "pm help"),
    ("page-size", "getconf PAGE_SIZE"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", required=True)
    parser.add_argument("--only", nargs="+", choices=[name for name, _ in QUERIES])
    args = parser.parse_args()
    os.umask(0o077)
    adb = ["adb", "-s", args.serial]
    state = subprocess.run(adb + ["get-state"], capture_output=True, text=True,
                           timeout=10)
    if state.returncode or state.stdout.strip() != "device":
        raise SystemExit("Selected ADB device is not connected/authorised: "
                         + state.stdout + state.stderr)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    destination = Path(__file__).resolve().parent / "evidence" / stamp
    destination.mkdir(parents=True, exist_ok=False, mode=0o700)
    manifest = {"serial": args.serial, "started_utc": stamp, "queries": []}
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(str(destination), flush=True)
    for name, query in QUERIES:
        if args.only and name not in args.only:
            continue
        started = time.monotonic()
        entry = {"name": name, "command": [*adb, "shell", query],
                 "exit_status": "running"}
        manifest["queries"].append(entry)
        (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        with (destination / (name + ".txt")).open("wb") as out:
            with (destination / (name + ".stderr")).open("wb") as err:
                try:
                    result = subprocess.run(adb + ["shell", query], stdout=out,
                                            stderr=err, timeout=45)
                    status = result.returncode
                except subprocess.TimeoutExpired:
                    status = "timeout"
        entry.update(exit_status=status, seconds=round(time.monotonic() - started, 3))
        (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"{name}: {status}", flush=True)
    manifest["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
