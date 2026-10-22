#!/system/bin/sh
# T3L head unit: turn the network debug bridge on/off without root.
# The unit runs SELinux permissive, so a plain app UID may set system props
# (verified 2026-10-21; the same commands work from Termux).
# The setting is not persistent: after a cold boot, run this again or use the
# "Network ADB · enable" button in T3L Drive's Apps > Help / recovery dialog.
#
# Usage: sh adb_tcp5555.sh [on|off]     (default: on)
case "$1" in
  off)
    /system/bin/setprop service.adb.tcp.port -1
    ;;
  *)
    /system/bin/setprop service.adb.tcp.port 5555
    ;;
esac
/system/bin/setprop ctl.restart adbd
