#!/usr/bin/env bash
set -euo pipefail

HOST=${AWX_HEALTHCHECK_HOST:-http://127.0.0.1:8052}
ENDPOINT="${HOST%/}/api/v2/ping/"

if curl --fail --silent --max-time 5 "$ENDPOINT" >/dev/null; then
  exit 0
fi

exit 1
