# Database Connectivity in the Dev Container

The dev container includes comprehensive database connectivity tools for Python and PowerShell development.

## Installed Tools

### Python Database Tools
- **pyodbc** - Python ODBC connectivity library
- **unixODBC** - ODBC driver manager and development libraries
- **Local packages** - All gds_* database modules (gds_database, gds_postgres, gds_snowflake, gds_vault, gds_mongodb, gds_mssql, gds_notification, gds_snmp_receiver)

### PowerShell Database Tools
- **dbatools** - Comprehensive database administration toolkit supporting SQL Server, PostgreSQL, MySQL, MongoDB, and more
- **Pester** - PowerShell testing framework for database scripts
- **PSFramework** - Logging and configuration framework

## Verify Installation

### Check ODBC Setup
```bash
# Check ODBC installation
odbcinst -j

# List available ODBC drivers
odbcinst -q -d

# Check pyodbc
python -c "import pyodbc; print('pyodbc version:', pyodbc.version)"
```

### Check PowerShell Modules
```bash
# Check PowerShell version
pwsh -version

# List installed database modules
pwsh -NoProfile -Command "Get-Module -ListAvailable dbatools,Pester,PSFramework | Format-Table Name,Version,Description -AutoSize"

# Verify dbatools commands
pwsh -NoProfile -Command "Get-Command -Module dbatools | Measure-Object | Select-Object -ExpandProperty Count"
```

### Verify Local Database Packages
```bash
# Check that all local packages are installed
python -c "import gds_database, gds_postgres, gds_snowflake, gds_vault, gds_mongodb, gds_mssql, gds_notification, gds_snmp_receiver; print('All packages OK')"

# Check individual package versions
python -c "import gds_database; print(f'gds_database: {gds_database.__version__ if hasattr(gds_database, \"__version__\") else \"installed\"}')"
```

## Database Connectivity Examples

### Python Examples

#### PostgreSQL Connection
```python
import pyodbc
from gds_postgres import PostgresConnection

# Using pyodbc directly
conn_str = "Driver={PostgreSQL Unicode};Server=localhost;Port=5432;Database=mydb;Uid=myuser;Pwd=mypass;"
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())
conn.close()

# Using gds_postgres module
pg = PostgresConnection(host='localhost', database='mydb', user='myuser', password='mypass')
result = pg.execute_query("SELECT * FROM my_table LIMIT 10")
print(result)
```

#### Snowflake Connection
```python
from gds_snowflake import SnowflakeConnection

# Using gds_snowflake module
sf = SnowflakeConnection(
    account='myaccount',
    user='myuser',
    password='mypass',
    warehouse='COMPUTE_WH',
    database='MYDB',
    schema='PUBLIC'
)
df = sf.query_to_dataframe("SELECT * FROM my_table LIMIT 10")
print(df.head())
```

#### SQL Server Connection
```python
import pyodbc
from gds_mssql import MSSQLConnection

# Using pyodbc directly
conn_str = "Driver={ODBC Driver 18 for SQL Server};Server=localhost,1433;Database=mydb;Uid=sa;Pwd=mypass;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
cursor.execute("SELECT @@VERSION;")
print(cursor.fetchone())
conn.close()

# Using gds_mssql module
mssql = MSSQLConnection(server='localhost', database='mydb', user='sa', password='mypass')
result = mssql.execute_query("SELECT * FROM sys.tables")
print(result)
```

#### MongoDB Connection
```python
from gds_mongodb import MongoDBConnection

# Using gds_mongodb module
mongo = MongoDBConnection(
    host='localhost',
    port=27017,
    database='mydb',
    username='myuser',
    password='mypass'
)
collection = mongo.get_collection('my_collection')
docs = collection.find().limit(10)
for doc in docs:
    print(doc)
```

#### Vault Integration
```python
from gds_vault import VaultClient

# Using gds_vault to retrieve database credentials
vault = VaultClient(url='https://vault.example.com', token='mytoken')
db_creds = vault.get_secret('database/postgres/mydb')
print(f"Username: {db_creds['username']}")
print(f"Password: {db_creds['password']}")
```

### PowerShell Examples

#### SQL Server Administration with dbatools
```powershell
# List all SQL Server instances
Get-DbaService

# Connect to SQL Server and get database info
$server = Connect-DbaInstance -SqlInstance 'localhost,1433' -SqlCredential (Get-Credential)
Get-DbaDatabase -SqlInstance $server

# Backup a database
Backup-DbaDatabase -SqlInstance $server -Database 'mydb' -Path '/tmp/backups'

# Check database integrity
Test-DbaDbCompression -SqlInstance $server -Database 'mydb'

# Get table sizes
Get-DbaDbTable -SqlInstance $server -Database 'mydb' |
    Select-Object Name, RowCount, DataSpaceMB, IndexSpaceMB |
    Sort-Object DataSpaceMB -Descending
```

#### PostgreSQL with dbatools
```powershell
# Connect to PostgreSQL
$pgServer = Connect-DbaInstance -SqlInstance 'localhost:5432' -SqlCredential (Get-Credential) -Database postgres

# Get PostgreSQL databases
Get-DbaDatabase -SqlInstance $pgServer

# Execute query on PostgreSQL
Invoke-DbaQuery -SqlInstance $pgServer -Database 'mydb' -Query 'SELECT * FROM my_table LIMIT 10'
```

#### Testing with Pester
```powershell
# Example Pester test for database connectivity
Describe "Database Connectivity Tests" {
    Context "PostgreSQL Connection" {
        It "Should connect to PostgreSQL" {
            $conn = Connect-DbaInstance -SqlInstance 'localhost:5432' -Database postgres -SqlCredential (Get-Credential)
            $conn | Should -Not -BeNullOrEmpty
        }

        It "Should query PostgreSQL" {
            $result = Invoke-DbaQuery -SqlInstance 'localhost:5432' -Database 'mydb' -Query 'SELECT 1 as test'
            $result.test | Should -Be 1
        }
    }
}

# Run the tests
Invoke-Pester -Path ./database-tests.ps1
```

## ODBC Driver Management

### List Available Drivers
```bash
# List ODBC drivers
python -c "
import pyodbc
drivers = pyodbc.drivers()
print('Available ODBC drivers:')
for driver in drivers:
    print(f'  - {driver}')
"
```

### Install Additional ODBC Drivers

To add Microsoft SQL Server ODBC driver (msodbcsql18):
```bash
# Install Microsoft ODBC Driver 18 for SQL Server (run inside container)
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Verify installation
odbcinst -q -d | grep "ODBC Driver 18 for SQL Server"
```

## Connection String Examples

### PostgreSQL
```
Driver={PostgreSQL Unicode};Server=hostname;Port=5432;Database=dbname;Uid=username;Pwd=password;
```

### SQL Server
```
Driver={ODBC Driver 18 for SQL Server};Server=hostname,1433;Database=dbname;Uid=username;Pwd=password;TrustServerCertificate=yes;
```

### MySQL
```
Driver={MySQL ODBC 8.0 Driver};Server=hostname;Port=3306;Database=dbname;User=username;Password=password;
```

## Troubleshooting

### ODBC Driver Not Found
```bash
# Check available drivers
odbcinst -q -d

# Check driver configuration
cat /etc/odbcinst.ini
```

### Connection Timeout Issues
```python
# Increase timeout in connection string
conn_str = "Driver={PostgreSQL Unicode};Server=hostname;ConnectionTimeout=30;LoginTimeout=30;"
```

### PowerShell Module Not Loading
```powershell
# Force reload module
Import-Module dbatools -Force

# Check module path
$env:PSModulePath -split ':'

# Get detailed module info
Get-Module dbatools -ListAvailable | Format-List *
```

### SSL/TLS Certificate Issues
```python
# For SQL Server, use TrustServerCertificate=yes
conn_str = "Driver={ODBC Driver 18 for SQL Server};Server=hostname;TrustServerCertificate=yes;"

# For PostgreSQL, use sslmode parameter
conn_str = "Driver={PostgreSQL Unicode};Server=hostname;sslmode=require;"
```

## Additional Resources

- [pyodbc Documentation](https://github.com/mkleehammer/pyodbc/wiki)
- [dbatools Documentation](https://dbatools.io/)
- [unixODBC Documentation](http://www.unixodbc.org/)
- [PostgreSQL ODBC Driver](https://odbc.postgresql.org/)
- [Microsoft ODBC Driver for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/)

## Notes

- Microsoft SQL Server command-line tools (sqlcmd, bcp) are **NOT** pre-installed but can be added
- The container focuses on Python and PowerShell-based database connectivity
- For production use, consider using environment variables or Vault for credentials
- Database drivers may need to be installed separately depending on your specific database needs
