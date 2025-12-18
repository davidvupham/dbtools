#!/usr/bin/env bash
set -euo pipefail

echo "[verify_pyodbc] Starting verification..."

PY_BIN="${PY_BIN:-.venv/bin/python}"
if [[ ! -x "$PY_BIN" ]]; then
    PY_BIN="$(command -v python || true)"
fi
echo "[verify_pyodbc] Python executable: ${PY_BIN}"
"${PY_BIN}" --version || true

echo "[verify_pyodbc] Importing pyodbc and printing version..."
"${PY_BIN}" - <<'PY'
import sys
try:
    import pyodbc
    print(f"pyodbc version: {pyodbc.version}")
    print(f"Python: {sys.executable}")
except Exception as e:
    print("ERROR: pyodbc import failed:", e)
    sys.exit(1)
PY

echo "[verify_pyodbc] Installed ODBC drivers:"
if command -v odbcinst >/dev/null 2>&1; then
  odbcinst -q -d || true
else
  echo "odbcinst not found"
fi

echo "[verify_pyodbc] Optional: attempting quick pyodbc connection if MSSQL_SA_PASSWORD is set..."
"${PY_BIN}" - <<'PY'
import os
try:
    import pyodbc
except Exception as e:
    print("pyodbc not available, skipping connection test:", e)
    raise SystemExit(0)

pwd = os.environ.get("MSSQL_SA_PASSWORD")
if not pwd:
    print("MSSQL_SA_PASSWORD not set; skipping connection attempt.")
    raise SystemExit(0)

conn_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=localhost;"
    "Encrypt=no;"
    "UID=SA;"
    f"PWD={pwd};"
    "Timeout=2;"
)
try:
    cn = pyodbc.connect(conn_str)
    cur = cn.cursor()
    cur.execute("SELECT @@VERSION")
    row = cur.fetchone()
    print("Connection OK. @@VERSION:")
    print(row[0] if row else "(no row)")
    cn.close()
except Exception as e:
    print("Connection attempt failed (this can be expected if SQL Server isn't running or creds are wrong):")
    print(e)
PY

echo "[verify_pyodbc] Done."
