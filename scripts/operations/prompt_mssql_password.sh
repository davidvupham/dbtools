#!/usr/bin/env bash
set -euo pipefail

echo "[prompt] This will set MSSQL_SA_PASSWORD for your session."
echo "[prompt] Tip: source this script to export into your current shell:"
echo "        . scripts/prompt_mssql_password.sh"

is_sourced=false
if [[ "${BASH_SOURCE[0]:-}" != "" && "${BASH_SOURCE[0]}" != "$0" ]]; then
  is_sourced=true
fi

prompt_password() {
  local p1 p2
  while true; do
    read -s -p "Enter MSSQL_SA_PASSWORD: " p1; echo
    read -s -p "Confirm MSSQL_SA_PASSWORD: " p2; echo
    if [[ "$p1" != "$p2" ]]; then
      echo "Passwords do not match. Please try again." >&2
      continue
    fi
    if [[ ${#p1} -lt 8 ]]; then
      echo "Password must be at least 8 characters." >&2
      continue
    fi
    if ! [[ "$p1" =~ [A-Z] ]]; then
      echo "Password must contain an uppercase letter." >&2
      continue
    fi
    if ! [[ "$p1" =~ [a-z] ]]; then
      echo "Password must contain a lowercase letter." >&2
      continue
    fi
    if ! [[ "$p1" =~ [0-9] ]]; then
      echo "Password must contain a digit." >&2
      continue
    fi
    if ! [[ "$p1" =~ [^[:alnum:]] ]]; then
      echo "Password must contain a non-alphanumeric (symbol)." >&2
      continue
    fi
    if [[ "$p1" =~ [[:space:]] ]]; then
      echo "Password must not contain whitespace." >&2
      continue
    fi
    if [[ "$p1" =~ [\"] || "$p1" =~ [\'] ]]; then
      echo "Password must not contain quotes for safety." >&2
      continue
    fi
    MSSQL_SA_PASSWORD="$p1"
    export MSSQL_SA_PASSWORD
    break
  done
}

prompt_password

echo "[ok] MSSQL_SA_PASSWORD captured."

if $is_sourced; then
  export MSSQL_SA_PASSWORD
  echo "[ok] Exported to current shell (since script was sourced)."
else
  echo "[note] This script was executed, not sourced, so your current shell won't be updated automatically."
  echo "       To export into this terminal now, run:"
  echo "       export MSSQL_SA_PASSWORD='********'"
fi

persist="n"
read -r -p "Persist to ~/.bashrc for future terminals? [y/N]: " persist || true
case "$persist" in
  y|Y)
    if grep -q "^export MSSQL_SA_PASSWORD=" "$HOME/.bashrc" 2>/dev/null; then
      sed -i "s|^export MSSQL_SA_PASSWORD=.*$|export MSSQL_SA_PASSWORD='REDACTED'|" "$HOME/.bashrc" || true
      # Replace with real value safely (quotes avoided earlier)
      sed -i "s|export MSSQL_SA_PASSWORD='REDACTED'|export MSSQL_SA_PASSWORD=$MSSQL_SA_PASSWORD|" "$HOME/.bashrc"
    else
      echo "export MSSQL_SA_PASSWORD=$MSSQL_SA_PASSWORD" >> "$HOME/.bashrc"
    fi
    echo "[ok] Appended to ~/.bashrc. Open a new terminal or run: source ~/.bashrc"
    ;;
  *)
    echo "[skip] Not persisted."
    ;;
esac

test_now="n"
read -r -p "Run quick connectivity check now? [y/N]: " test_now || true
case "$test_now" in
  y|Y)
    bash scripts/verify_sqlserver.sh || true
    ;;
  *) ;;
esac
