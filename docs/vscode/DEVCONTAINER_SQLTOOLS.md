# SQL tools in the Dev Container

The dev container includes basic ODBC tooling for database connectivity:

- unixODBC and unixODBC-dev (ODBC driver manager and development libraries)
- pyodbc (Python ODBC connectivity library)

## Verify tools

```bash
# Check ODBC installation
odbcinst -j

# Check pyodbc
python -c "import pyodbc; print('pyodbc version:', pyodbc.version)"
```

## Verify local database packages

```bash
# Check that local packages are installed
python -c "import gds_database, gds_postgres, gds_snowflake, gds_vault; print('Local packages OK')"
```

## Example usage

```bash
# Test basic ODBC functionality
python -c "
import pyodbc
# List available drivers
drivers = pyodbc.drivers()
print('Available ODBC drivers:')
for driver in drivers:
    print(f'  - {driver}')
"
```

Notes:
- Microsoft SQL Server drivers (msodbcsql18) and tools (sqlcmd, bcp) are NOT included
- For Microsoft SQL Server connectivity, you would need to install additional drivers separately
- The container focuses on Python-based database connectivity rather than command-line SQL tools
