#!/usr/bin/env bash
set -euo pipefail

# This script clones additional Git repositories into the shared /workspaces
# directory based on configuration in additional-repos.json.
#
# It is safe to run multiple times:
# - Existing repositories (with a .git directory) are skipped.
# - New entries in the JSON file will be cloned on the next run.
#
# Usage (inside dev container):
#   bash .devcontainer/scripts/clone-additional-repos.sh
#
# Configuration file format (.devcontainer/additional-repos.json):
# {
#   "repos": [
#     "git@github.com:your-org/one-repo.git",
#     {
#       "url": "git@github.com:your-org/another-repo.git",
#       "directory": "custom-folder-name"
#     }
#   ]
# }

ROOT="/workspaces"
# Use the current workspace folder generically
CONFIG="$(pwd)/.devcontainer/additional-repos.json"

if [ ! -f "$CONFIG" ]; then
  echo "[clone-additional-repos] No config file found at $CONFIG; nothing to do."
  exit 0
fi

echo "[clone-additional-repos] Using config: $CONFIG"

python - << 'PY' "$ROOT" "$CONFIG"
import json
import os
import subprocess
import sys

root, config_path = sys.argv[1], sys.argv[2]

with open(config_path, "r", encoding="utf-8") as f:
    data = json.load(f)

repos = data.get("repos", [])
if not isinstance(repos, list):
    print("[clone-additional-repos] 'repos' must be a list in additional-repos.json")
    sys.exit(1)

for entry in repos:
    if isinstance(entry, str):
        url = entry
        name = os.path.splitext(os.path.basename(url))[0]
    elif isinstance(entry, dict):
        url = entry.get("url")
        if not url:
            print("[clone-additional-repos] Skipping entry without 'url':", entry)
            continue
        directory = entry.get("directory")
        if directory:
            name = directory
        else:
            name = os.path.splitext(os.path.basename(url))[0]
    else:
        print("[clone-additional-repos] Skipping unsupported entry type:", entry)
        continue

    dest = os.path.join(root, name)
    git_dir = os.path.join(dest, ".git")

    if os.path.isdir(git_dir):
        print(f"[clone-additional-repos] Repo '{name}' already exists at {dest}; skipping.")
        continue

    print(f"[clone-additional-repos] Cloning {url} -> {dest}")
    subprocess.run(["git", "clone", url, dest], check=True)

print("[clone-additional-repos] Done.")
PY
