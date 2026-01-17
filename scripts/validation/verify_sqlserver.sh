#!/usr/bin/env bash
set -euo pipefail

echo "[verify_sqlserver] Starting SQL Server verification..."

SQLCMD_BIN="$(command -v sqlcmd || true)"
if [[ -z "$SQLCMD_BIN" ]]; then
  if [[ -x "/opt/mssql-tools18/bin/sqlcmd" ]]; then
    SQLCMD_BIN="/opt/mssql-tools18/bin/sqlcmd"
  elif [[ -x "/opt/mssql-tools/bin/sqlcmd" ]]; then
    SQLCMD_BIN="/opt/mssql-tools/bin/sqlcmd"
  else
    echo "sqlcmd not found; ensure mssql-tools18 is installed in the devcontainer."
  fi
fi

if [[ -n "$SQLCMD_BIN" ]]; then
  target_hosts=("mssql1" "localhost")
  for host in "${target_hosts[@]}"; do
    echo "[verify_sqlserver] Trying sqlcmd against '${host}'..."
    if [[ -z "${MSSQL_SA_PASSWORD:-}" ]]; then
      echo "MSSQL_SA_PASSWORD not set; skipping sqlcmd login test for '${host}'."
      continue
    fi
    if "$SQLCMD_BIN" -C -S "$host" -U SA -P "$MSSQL_SA_PASSWORD" -Q "SELECT @@SERVERNAME AS ServerName, DB_NAME() AS CurrentDB, GETDATE() AS CurrentTime;" -W -s "," -l 2; then
      echo "[verify_sqlserver] sqlcmd succeeded against '${host}'."
      break
    else
      echo "[verify_sqlserver] sqlcmd failed against '${host}'. Trying next..."
    fi
  done
fi

echo "[verify_sqlserver] Checking pyodbc connectivity..."
PY_BIN="${PY_BIN:-.venv/bin/python}"
if [[ ! -x "$PY_BIN" ]]; then
  PY_BIN="$(command -v python || true)"
fi
"${PY_BIN}" - <<'PY'
import os
import sys

print("Python:", sys.executable)
try:
    import pyodbc
    print("pyodbc:", pyodbc.version)
except Exception as e:
    print("ERROR: pyodbc import failed:", e)
    raise SystemExit(1)

pwd = os.environ.get("MSSQL_SA_PASSWORD")
hosts = ["mssql1", "localhost"]

if not pwd:
    print("MSSQL_SA_PASSWORD not set; skipping pyodbc connection attempts.")
    raise SystemExit(0)

for host in hosts:
    conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        f"Server={host};"
        "Encrypt=no;"
        "UID=SA;"
        f"PWD={pwd};"
        "Timeout=2;"
    )
    print(f"[pyodbc] Trying host '{host}'...")
    try:
        cn = pyodbc.connect(conn_str)
        cur = cn.cursor()
        cur.execute("SELECT @@SERVERNAME, DB_NAME(), GETDATE()")
        row = cur.fetchone()
        print("Connected. Server, DB, Time:", row)
        cn.close()
        break
    except Exception as e:
        print(f"[pyodbc] Connection to '{host}' failed:", e)
else:
    print("[pyodbc] All connection attempts failed.")
PY

echo "[verify_sqlserver] Done."
