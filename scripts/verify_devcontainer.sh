#!/usr/bin/env bash
# Unified verification for the dbtools dev container
# Fails fast on critical issues but continues to collect diagnostics
set -uo pipefail

FAILS=0
WARN=0
LOG() { echo -e "[$(date +%H:%M:%S)] $*"; }
PASS() { LOG "PASS: $*"; }
FAIL() { LOG "FAIL: $*"; FAILS=$((FAILS+1)); }
SKIP() { LOG "SKIP: $*"; }
NOTE() { LOG "NOTE: $*"; }

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$ROOT_DIR" || exit 1

VENV_PY="${VENV_PY:-$ROOT_DIR/.venv/bin/python}"

if [[ -x "$VENV_PY" ]]; then
  PYTHON_BIN="$VENV_PY"
else
  PYTHON_BIN="${PYTHON_BIN:-python3}"
  if [[ ! -x "$(command -v "$PYTHON_BIN" || true)" ]]; then
    PYTHON_BIN="$(command -v python || true)"
  fi
fi

LOG "Starting devcontainer verification..."

# 1) Python version
"$PYTHON_BIN" --version && PASS "Python version reported" || FAIL "Python not runnable"

# 2) ipykernel and kernelspec
"$PYTHON_BIN" - <<'PY'
import sys
try:
    import ipykernel
    print("ipykernel:", getattr(ipykernel, "__version__", "unknown"))
except Exception as e:
    print("ERROR: ipykernel import failed:", e)
    raise SystemExit(2)
PY
case $? in
  0) PASS "ipykernel import ok";;
  *) FAIL "ipykernel not available in Python env";;
esac

KERNEL_SPEC="$HOME/.local/share/jupyter/kernels/gds/kernel.json"
if [[ -f "$KERNEL_SPEC" ]]; then
  PASS "Found kernelspec: $KERNEL_SPEC"
else
  FAIL "Missing kernelspec 'gds'. Run: $VENV_PY -m ipykernel install --user --name gds --display-name 'Python (gds)'"
fi

# 3) pyodbc import and ODBC driver listing
"$PYTHON_BIN" - <<'PY'
try:
    import pyodbc
    print("pyodbc:", pyodbc.version)
except Exception as e:
    print("ERROR: pyodbc import failed:", e)
    raise SystemExit(3)
PY
case $? in
  0) PASS "pyodbc import ok";;
  *) FAIL "pyodbc not importable";;
esac

if command -v odbcinst >/dev/null 2>&1; then
  if odbcinst -q -d | grep -qi "ODBC Driver 18"; then
    PASS "ODBC Driver 18 present"
  else
    WARN=$((WARN+1)); NOTE "ODBC Driver 18 not listed by odbcinst (check msodbcsql18 install)"
  fi
else
  FAIL "odbcinst not found; unixodbc not installed?"
fi

# 4) sqlcmd availability
if command -v sqlcmd >/dev/null 2>&1 || [[ -x /opt/mssql-tools18/bin/sqlcmd ]] || [[ -x /opt/mssql-tools/bin/sqlcmd ]]; then
  PASS "sqlcmd available"
else
  FAIL "sqlcmd not found; ensure mssql-tools18 installed"
fi

# 5) PowerShell 7
if command -v pwsh >/dev/null 2>&1; then
  if pwsh -NoLogo -NoProfile -Command '$PSVersionTable.PSVersion.ToString()' >/dev/null 2>&1; then
    PASS "PowerShell 7 available"
  else
    FAIL "pwsh present but failed to run"
  fi
else
  FAIL "pwsh not found"
fi

# 6) Optional: JupyterLab
if [[ "${ENABLE_JUPYTERLAB:-0}" == "1" ]] || command -v jupyter-lab >/dev/null 2>&1; then
  "$PYTHON_BIN" - <<'PY'
try:
    import jupyterlab
    print("jupyterlab:", jupyterlab.__version__)
except Exception as e:
    print("ERROR: jupyterlab import failed:", e)
    raise SystemExit(4)
PY
  case $? in
    0) PASS "JupyterLab import ok";;
    *) WARN=$((WARN+1)); NOTE "JupyterLab expected but import failed";;
  esac
else
  SKIP "JupyterLab check (flag disabled and binary not found)"
fi

# 7) Optional: run existing verifications
if bash scripts/verify_pyodbc.sh; then
  PASS "verify_pyodbc.sh succeeded"
else
  FAIL "verify_pyodbc.sh failed"
fi

if [[ -n "${MSSQL_SA_PASSWORD:-}" ]]; then
  if bash scripts/verify_sqlserver.sh; then
    PASS "verify_sqlserver.sh succeeded"
  else
    WARN=$((WARN+1)); NOTE "SQL Server verification failed (server may be down or creds invalid)"
  fi
else
  SKIP "SQL Server checks (MSSQL_SA_PASSWORD not set)"
fi

LOG "Verification complete. Failures: $FAILS, Warnings: $WARN"
exit $(( FAILS > 0 ? 1 : 0 ))
