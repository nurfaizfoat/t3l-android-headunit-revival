#!/usr/bin/env python3
"""Build package inventory offline from one explicit read-only evidence run."""

import argparse
import csv
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET


CRITICAL = "CRITICAL — DO NOT TOUCH"
INVESTIGATE = "REQUIRES INVESTIGATION"
SAFE = "SAFE TO DISABLE"
OPTIONAL_PRINT = {"com.android.printspooler", "com.android.printservice.recommendation"}
OPTIONAL_SYSTEM = {
    "com.android.dreams.basic", "com.android.wallpaper.livepicker",
    "com.android.printspooler", "com.android.printservice.recommendation",
    "com.android.bookmarkprovider", "com.android.emergency",
    "com.android.managedprovisioning", "com.android.companiondevicemanager",
    "com.android.htmlviewer", "com.android.wallpapercropper",
    "com.android.wallpaperbackup", "com.android.sharedstoragebackup",
}
A = "{http://schemas.android.com/apk/res/android}"


def first(pattern, text):
    match = re.search(pattern, text, re.M)
    return match.group(1) if match else ""


def components(text, package):
    return sorted(set(re.findall(r"(?m)^\s+(" + re.escape(package) + r"/[\w.$]+)\s*$", text)))


def classification(name, block):
    if name in OPTIONAL_PRINT:
        return SAFE, "Conditional on no printing/Print-to-PDF requirement; separate UID and print-only copied manifest; preserve data; approval required."
    if name == "com.android.chrome":
        return CRITICAL, "Active WebView provider verified by dumpsys webviewupdate; do not disable or force-stop for RAM savings."
    if name == "com.google.android.packageinstaller":
        return CRITICAL, "System package installer; preserve installation and recovery capability."
    if name.startswith("com.tw.") or name == "com.dofun.variety":
        return CRITICAL, "Protected factory/vendor stack; factory HOME, vehicle controls, persistent/shared-UID dependencies or unresolved vendor role."
    if name == "android" or name.startswith("android."):
        return CRITICAL, "Android framework or framework overlay."
    if "sharedUser=" in block and ("android.uid.system/1000" in block or "android.uid.phone/1001" in block or "android.uid.bluetooth/1002" in block):
        return CRITICAL, "Shares a protected system/telephony/Bluetooth UID; name/location is not a debloat justification."
    if name.startswith("com.android.") and name not in OPTIONAL_SYSTEM and name != "com.android.vending":
        return CRITICAL, "Conservatively preserve Android platform/provider/network/input/media/recovery infrastructure."
    return INVESTIGATE, "Optionality or dependencies not established; no approved change. Preserve existing disabled/component states."


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--output", type=Path, default=Path("package-inventory.csv"))
    args = parser.parse_args()
    p = args.evidence
    details = (p / "package-details.txt").read_text().split("Hidden system packages:")[0]
    blocks = re.split(r"^  Package \[([^\]]+)\] \([^\n]+\):\n", details, flags=re.M)
    packages = dict(zip(blocks[1::2], blocks[2::2]))
    paths = {}
    for line in (p / "packages.txt").read_text().splitlines():
        path, name = line.removeprefix("package:").rsplit("=", 1)
        paths[name] = path
    if set(paths) - set(packages):
        raise ValueError("Installed package missing from details; inspect evidence")
    for name in set(packages) - set(paths):
        # Android retains factory-package metadata after a user-0 uninstall.
        if not re.search(r"^    User 0:.* installed=false\b", packages[name], re.M):
            raise ValueError("Unexplained package list/details mismatch: " + name)
    launch = (p / "launcher-activities.txt").read_text()
    home = (p / "home-activities.txt").read_text()
    rows = []
    for name in sorted(paths):
        block = packages[name]
        uid = first(r"^    userId=(\d+)", block)
        state = first(r"^    User 0:.*? enabled=(\d+)", block)
        if not uid or not state:
            raise ValueError("Missing UID/state for " + name)
        flags = first(r"^    flags=\[ (.*?) \]", block)
        components_in_resolver = sorted(set(re.findall(re.escape(name) + r"/[\w.$]+", details.split("Packages:")[0])))
        permission_block = first(r"(?s)    requested permissions:\n(.*?)(?=\n    \S|\Z)", block)
        requested = sorted(set(re.findall(r"^\s+([\w.]+)$", permission_block, re.M)))
        manifest = p / "apks" / (name + ".manifest.xml")
        metadata_scope = "Resolver components/available requested permissions only; not a complete manifest."
        if manifest.exists():
            root = ET.parse(manifest).getroot()
            requested = sorted(n.get(A + "name") for n in root.findall("uses-permission") if n.get(A + "name"))
            app = root.find("application")
            components_in_resolver = [n.tag + ":" + n.get(A + "name", "") for n in app if n.tag in {"service", "receiver", "provider"}]
            metadata_scope = "Copied manifest inspected offline."
        category, reason = classification(name, block)
        override_lines = []
        active_section = ""
        for line in block.splitlines():
            if line.startswith("      disabledComponents:"):
                active_section = "disabled"
            elif line.startswith("      enabledComponents:"):
                active_section = "enabled"
            elif active_section and line.startswith("        "):
                override_lines.append(active_section + ":" + line.strip())
            else:
                active_section = ""
        rows.append({
            "package": name, "version_name": first(r"^    versionName=(.*)$", block),
            "version_code": first(r"^    versionCode=(\d+)", block),
            "min_sdk": first(r"minSdk=(\d+)", block), "target_sdk": first(r"targetSdk=(\d+)", block),
            "apk_path": paths[name], "uid": uid,
            "shared_uid": first(r"sharedUser=SharedUserSetting\{\S+ (.*?)\}", block),
            "enabled_state_user_0": state,
            "enabled_state_meaning": {"0": "default", "1": "enabled", "2": "disabled", "3": "disabled-user", "4": "disabled-until-used"}.get(state, "unknown"),
            "component_overrides": "; ".join(override_lines),
            "system_or_user": "updated-system" if "UPDATED_SYSTEM_APP" in flags else "system" if "SYSTEM" in flags else "user",
            "launch_activities": "; ".join(components(launch, name)),
            "home_activities": "; ".join(components(home, name)),
            "services_receivers_providers": "; ".join(components_in_resolver),
            "requested_permissions": "; ".join(requested),
            "metadata_scope": metadata_scope,
            "category": category, "classification_evidence": reason,
            "rollback_notes": "Restore recorded user-0 state and component overrides; no changes applied.",
        })
    os.umask(0o077)
    with args.output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    counts = {category: sum(row["category"] == category for row in rows) for category in [SAFE, INVESTIGATE, CRITICAL]}
    print(f"Wrote {len(rows)} packages: {counts}")


if __name__ == "__main__":
    main()
