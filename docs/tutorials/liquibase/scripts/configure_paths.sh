#!/usr/bin/env bash
set -euo pipefail

echo "[DEPRECATED] configure_paths.sh has been replaced by setup_environment.sh" >&2
echo "Please run: \n  $(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/setup_environment.sh" >&2
echo "This new helper prompts for MSSQL password and paths, then prints export lines." >&2
exit 1
