#!/usr/bin/env bash
# Create per-user project directory for Liquibase tutorial
# Usage: sudo ./setup_user_directory.sh   OR   source this script

set -euo pipefail

TARGET_DIR="/data/${SUDO_USER:-$USER}"
TARGET_USER="${SUDO_USER:-$USER}"

echo "Creating directory: $TARGET_DIR"

if [[ ! -d "$TARGET_DIR" ]]; then
  mkdir -p "$TARGET_DIR"
  chown "$TARGET_USER" "$TARGET_DIR"
  echo "Created and set ownership to $TARGET_USER"
else
  echo "Directory already exists"
fi

# Verify
ls -ld "$TARGET_DIR"
