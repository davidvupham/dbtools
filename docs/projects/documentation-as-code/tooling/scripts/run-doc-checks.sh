#!/usr/bin/env bash
set -euo pipefail

# Simple docs-as-code runner (Linux/WSL)
#
# Usage:
#   bash tooling/scripts/run-doc-checks.sh            # run all
#   bash tooling/scripts/run-doc-checks.sh --cspell   # run one

ROOT_DIR="$(pwd)"
DOCS_GLOB='docs/**/*.md'

want_markdownlint=false
want_cspell=false
want_vale=false
want_lychee=false

if [ "$#" -eq 0 ]; then
  want_markdownlint=true
  want_cspell=true
  want_vale=true
  want_lychee=true
else
  for arg in "$@"; do
    case "$arg" in
      --markdownlint) want_markdownlint=true ;;
      --cspell) want_cspell=true ;;
      --vale) want_vale=true ;;
      --lychee) want_lychee=true ;;
      *)
        echo "Unknown arg: $arg" >&2
        exit 2
        ;;
    esac
  done
fi

fail_missing() {
  local tool="$1"
  local hint="$2"
  echo "ERROR: missing required tool: $tool" >&2
  echo "Hint: $hint" >&2
  exit 1
}

if $want_markdownlint; then
  command -v npx >/dev/null 2>&1 || fail_missing "node/npm" "Install Node.js and ensure npm is on PATH"
  echo "== markdownlint =="
  npx markdownlint-cli2 "$DOCS_GLOB"
fi

if $want_cspell; then
  command -v npx >/dev/null 2>&1 || fail_missing "node/npm" "Install Node.js and ensure npm is on PATH"
  echo "== cspell =="
  npx cspell --config cspell.json "$DOCS_GLOB"
fi

if $want_vale; then
  command -v vale >/dev/null 2>&1 || fail_missing "vale" "Install Vale and ensure 'vale' is on PATH"
  echo "== vale =="
  vale --config .vale.ini docs
fi

if $want_lychee; then
  command -v lychee >/dev/null 2>&1 || fail_missing "lychee" "Install Lychee and ensure 'lychee' is on PATH"
  echo "== lychee =="
  lychee --config lychee.toml "$DOCS_GLOB"
fi

echo "OK: docs checks passed"
