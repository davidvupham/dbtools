#!/usr/bin/env python3
"""Synchronize shared settings between devcontainer variants.

Copies a curated set of keys from a source devcontainer configuration to a
target configuration so that common settings stay aligned across distributions.
This script operates on JSON-with-comments files by stripping comments before
parsing. Comments are not preserved in the rewritten target file.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import OrderedDict
from collections.abc import Iterable
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEVCONTAINER_DIR = REPO_ROOT / ".devcontainer"
VARIANT_DIRS = {
    "ubuntu": DEVCONTAINER_DIR / "ubuntu",
    "redhat": DEVCONTAINER_DIR / "redhat",
}
CONFIG_FILENAME = "devcontainer.json"

SYNC_KEYS: tuple[str, ...] = (
    "remoteUser",
    "features",
    "customizations",
    "workspaceFolder",
    "forwardPorts",
    "portsAttributes",
    "runArgs",
    "postCreateCommand",
    "postStartCommand",
    "containerEnv",
    "mounts",
)


def strip_jsonc(text: str) -> str:
    """Remove // and /* */ comments from JSONC-like content."""
    result: list[str] = []
    i = 0
    length = len(text)
    in_string = False
    string_char = ""
    while i < length:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < length else ""
        if in_string:
            result.append(ch)
            if ch == "\\":
                if i + 1 < length:
                    result.append(text[i + 1])
                    i += 2
                    continue
            elif ch == string_char:
                in_string = False
            i += 1
            continue
        if ch in ('"', "'"):
            in_string = True
            string_char = ch
            result.append(ch)
            i += 1
            continue
        if ch == "/" and nxt == "/":
            i += 2
            while i < length and text[i] not in "\r\n":
                i += 1
            continue
        if ch == "/" and nxt == "*":
            i += 2
            while i + 1 < length and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2  # skip closing */
            continue
        result.append(ch)
        i += 1
    return "".join(result)


def load_config(path: Path) -> OrderedDict:
    raw = path.read_text(encoding="utf-8")
    stripped = strip_jsonc(raw)
    return json.loads(stripped, object_pairs_hook=OrderedDict)


def write_config(path: Path, data: OrderedDict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def sync_keys(source: OrderedDict, target: OrderedDict, keys: Iterable[str]) -> bool:
    modified = False
    for key in keys:
        if key in source:
            src_value = source[key]
            if target.get(key) != src_value:
                target[key] = src_value
                modified = True
    return modified


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        choices=VARIANT_DIRS.keys(),
        default="ubuntu",
        help="Variant to treat as the authoritative source (default: ubuntu)",
    )
    parser.add_argument(
        "--target",
        choices=VARIANT_DIRS.keys(),
        default="redhat",
        help="Variant that will be updated to match the source (default: redhat)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Evaluate differences without writing changes",
    )
    parser.add_argument(
        "--keys",
        nargs="*",
        help="Custom list of top-level keys to sync (overrides default set).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.source == args.target:
        print("[sync] Source and target variants are identical; nothing to do.")
        return 0
    source_dir = VARIANT_DIRS[args.source]
    target_dir = VARIANT_DIRS[args.target]
    source_path = source_dir / CONFIG_FILENAME
    target_path = target_dir / CONFIG_FILENAME
    if not source_path.is_file():
        raise SystemExit(f"Source config not found: {source_path}")
    if not target_path.is_file():
        raise SystemExit(f"Target config not found: {target_path}")

    source_config = load_config(source_path)
    target_config = load_config(target_path)

    keys_to_sync: Iterable[str] = tuple(args.keys) if args.keys else SYNC_KEYS
    modified = sync_keys(source_config, target_config, keys_to_sync)

    if not modified:
        print("[sync] Target already matches source for selected keys.")
        return 0

    if args.dry_run:
        print("[sync] Differences detected (dry run); no files updated.")
        return 0

    write_config(target_path, target_config)
    # Preserve original file permissions
    os.chmod(target_path, os.stat(source_path).st_mode)
    print(f"[sync] Updated {target_path.relative_to(REPO_ROOT)} from {args.source} -> {args.target}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
