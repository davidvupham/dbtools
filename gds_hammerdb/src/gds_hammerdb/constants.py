import os

# Default Paths
DEFAULT_HAMMERDB_CLI_PATH = os.getenv("HAMMERDB_CLI_PATH", "./hammerdbcli")

# Database Options
DB_POSTGRES = "pg"
DB_MSSQL_LINUX = "mssqls"  # mssqls for SQL Server on Linux/Windows

# Benchmarks
BM_TPCC = "TPC-C"
BM_TPCH = "TPC-H"

# Defaults
DEFAULT_RAMPUP_MINUTES = 2
DEFAULT_DURATION_MINUTES = 5
DEFAULT_VIRTUAL_USERS = 1
DEFAULT_TPCH_SCALE_FACTOR = 1
