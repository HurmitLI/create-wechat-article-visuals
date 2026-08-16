#!/usr/bin/env python3
"""Audit dimensions and aspect ratios for WeChat article visual assets."""

from __future__ import annotations

import argparse
import re
import struct
import sys
from pathlib import Path


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n" or len(header) < 24:
        raise ValueError("invalid PNG")
    return struct.unpack(">II", header[16:24])


def jpeg_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if not data.startswith(b"\xff\xd8"):
        raise ValueError("invalid JPEG")
    offset = 2
    while offset + 9 < len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        marker = data[offset + 1]
        offset += 2
        if marker in (0xD8, 0xD9):
            continue
        if offset + 2 > len(data):
            break
        length = struct.unpack(">H", data[offset : offset + 2])[0]
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            if offset + 7 > len(data):
                break
            height, width = struct.unpack(">HH", data[offset + 3 : offset + 7])
            return width, height
        offset += length
    raise ValueError("JPEG dimensions not found")


def number(value: str) -> float:
    match = re.match(r"\s*([0-9.]+)", value)
    if not match:
        raise ValueError(f"invalid dimension: {value}")
    return float(match.group(1))


def svg_size(path: Path) -> tuple[int, int]:
    head = path.read_text(encoding="utf-8")[:8192]
    viewbox = re.search(r"viewBox=[\"']\s*[+-]?[0-9.]+\s+[+-]?[0-9.]+\s+([0-9.]+)\s+([0-9.]+)", head, re.I)
    if viewbox:
        return round(float(viewbox.group(1))), round(float(viewbox.group(2)))
    width = re.search(r"\bwidth=[\"']([^\"']+)", head, re.I)
    height = re.search(r"\bheight=[\"']([^\"']+)", head, re.I)
    if width and height:
        return round(number(width.group(1))), round(number(height.group(1)))
    raise ValueError("SVG width/height or viewBox not found")


def dimensions(path: Path) -> tuple[int, int]:
    suffix = path.suffix.lower()
    if suffix == ".png":
        return png_size(path)
    if suffix in {".jpg", ".jpeg"}:
        return jpeg_size(path)
    if suffix == ".svg":
        return svg_size(path)
    raise ValueError(f"unsupported format: {suffix or 'none'}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--cover", type=Path, help="File to validate as the wide cover")
    parser.add_argument("--strict", action="store_true", help="Return non-zero for warnings")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    cover = args.cover.resolve() if args.cover else None
    paths = list(args.files)
    if args.cover and args.cover not in paths:
        paths.insert(0, args.cover)

    for path in paths:
        try:
            if not path.is_file():
                raise ValueError("file not found")
            width, height = dimensions(path)
            ratio = width / height
            is_cover = cover == path.resolve()
            role = "COVER" if is_cover else "BODY"
            print(f"{role:5} {width}x{height} ratio={ratio:.2f} {path}")
            if width < 1200:
                warnings.append(f"{path}: width {width}px is below the recommended 1200px")
            if is_cover and not 1.9 <= ratio <= 2.6:
                warnings.append(f"{path}: cover ratio {ratio:.2f} is outside 1.9-2.6")
            if not is_cover and not 1.2 <= ratio <= 2.2:
                warnings.append(f"{path}: body ratio {ratio:.2f} is outside 1.2-2.2")
            if path.stat().st_size > 10 * 1024 * 1024:
                warnings.append(f"{path}: file is larger than 10 MB")
        except Exception as exc:
            errors.append(f"{path}: {exc}")

    for item in warnings:
        print(f"WARN: {item}", file=sys.stderr)
    for item in errors:
        print(f"ERROR: {item}", file=sys.stderr)
    if errors:
        return 1
    if warnings and args.strict:
        return 2
    print(f"PASS: checked {len(paths)} visual asset(s); visual inspection is still required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
