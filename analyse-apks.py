#!/usr/bin/env python3
"""Offline manifest/string inspection of copied APKs; never execute APK code.

This intentionally small decoder handles binary XML attribute values and DEX
strings, not Android resource resolution, bytecode decompilation or API proof.
"""

import argparse
import json
import os
from pathlib import Path
import struct
import xml.etree.ElementTree as ET
import zipfile


def u16(data, pos):
    return struct.unpack_from("<H", data, pos)[0]


def u32(data, pos):
    return struct.unpack_from("<I", data, pos)[0]


def length(data, pos, utf8):
    value = data[pos] if utf8 else u16(data, pos)
    step, mask = (1, 0x80) if utf8 else (2, 0x8000)
    pos += step
    if value & mask:
        second = data[pos] if utf8 else u16(data, pos)
        value = ((value & (mask - 1)) << (8 if utf8 else 16)) | second
        pos += step
    return value, pos


def manifest_xml(data):
    if data.lstrip().startswith(b"<"):
        return ET.fromstring(data)
    if u16(data, 0) != 3:
        raise ValueError("Not Android binary XML")
    strings, stack, root = [], [], None
    pos = u16(data, 2)
    while pos < len(data):
        kind, header, size = struct.unpack_from("<HHI", data, pos)
        if size < header or size == 0 or pos + size > len(data):
            raise ValueError("Invalid chunk bounds")
        if kind == 1:
            count = u32(data, pos + 8)
            utf8 = bool(u32(data, pos + 16) & 0x100)
            start = pos + u32(data, pos + 20)
            strings = []
            for index in range(count):
                cursor = start + u32(data, pos + header + index * 4)
                n, cursor = length(data, cursor, utf8)
                if utf8:
                    n, cursor = length(data, cursor, True)
                text = data[cursor:cursor + n * (1 if utf8 else 2)]
                strings.append(text.decode("utf-8" if utf8 else "utf-16le", errors="replace"))
        elif kind == 0x102:
            node = ET.Element(strings[u32(data, pos + 20)])
            attr_start, attr_size, count = struct.unpack_from("<HHH", data, pos + 24)
            for index in range(count):
                offset = pos + 16 + attr_start + index * attr_size
                namespace, name, raw = struct.unpack_from("<III", data, offset)
                value_type = data[offset + 15]
                value = u32(data, offset + 16)
                if raw != 0xFFFFFFFF:
                    text = strings[raw]
                elif value_type == 3:
                    text = strings[value]
                elif value_type == 0x12:
                    text = "true" if value else "false"
                elif value_type == 1:
                    text = f"@0x{value:08x}"
                elif value_type == 0x10:
                    text = str(struct.unpack_from("<i", data, offset + 16)[0])
                else:
                    text = str(value)
                key = strings[name]
                if namespace != 0xFFFFFFFF:
                    key = "{" + strings[namespace] + "}" + key
                node.set(key, text)
            if stack:
                stack[-1].append(node)
            else:
                root = node
            stack.append(node)
        elif kind == 0x103:
            stack.pop()
        pos += size
    if root is None or stack:
        raise ValueError("Incomplete manifest")
    return root


def dex_strings(data):
    if not data.startswith(b"dex\n"):
        raise ValueError("Not a DEX file")
    count, start = struct.unpack_from("<II", data, 56)
    strings = []
    for index in range(count):
        cursor = u32(data, start + index * 4)
        for _ in range(5):
            byte = data[cursor]
            cursor += 1
            if not byte & 0x80:
                break
        end = data.index(b"\0", cursor)
        strings.append(data[cursor:end].decode("utf-8", errors="replace"))
    return strings


def vendor_method_refs(data):
    strings = dex_strings(data)
    count, start = struct.unpack_from("<II", data, 64)
    types = [strings[u32(data, start + index * 4)] for index in range(count)]
    proto_start = u32(data, 76)
    count, start = struct.unpack_from("<II", data, 88)
    refs = []
    for index in range(count):
        cls, proto, name = struct.unpack_from("<HHI", data, start + index * 8)
        if not types[cls].startswith("Landroid/tw/"):
            continue
        _, ret, parameters = struct.unpack_from("<III", data, proto_start + proto * 12)
        args = [] if not parameters else [types[u16(data, parameters + 4 + i * 2)]
                                         for i in range(u32(data, parameters))]
        refs.append({"class": types[cls], "name": strings[name],
                     "parameters": args, "return": types[ret]})
    return refs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    os.umask(0o077)
    ET.register_namespace("android", "http://schemas.android.com/apk/res/android")
    for path in sorted(args.directory.glob("*.apk")):
        with zipfile.ZipFile(path) as apk:
            root = manifest_xml(apk.read("AndroidManifest.xml"))
            ET.indent(root)
            path.with_suffix(".manifest.xml").write_text(ET.tostring(root, encoding="unicode") + "\n")
            strings = set()
            vendor_refs = []
            for name in apk.namelist():
                if name.startswith("classes") and name.endswith(".dex"):
                    strings.update(dex_strings(apk.read(name)))
                    vendor_refs.extend(vendor_method_refs(apk.read(name)))
            path.with_suffix(".strings.json").write_text(json.dumps(sorted(strings), indent=2) + "\n")
            summary = {"package": root.get("package"), "dex_string_count": len(strings),
                       "native_libraries": [n for n in apk.namelist() if n.startswith("lib/")],
                       "vendor_method_references": vendor_refs,
                       "limitations": "Static strings/manifest only; no call-graph or resource resolution."}
            path.with_suffix(".summary.json").write_text(json.dumps(summary, indent=2) + "\n")
            print(path.name, summary["package"], len(strings))


if __name__ == "__main__":
    main()
