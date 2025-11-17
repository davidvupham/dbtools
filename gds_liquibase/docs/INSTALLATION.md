# GDS Liquibase Package Installation Guide

This document provides detailed instructions for installing and using the gds_liquibase package.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Verifying Installation](#verifying-installation)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- Python 3.8 or higher
- pip (Python package installer)
- Liquibase 5.0+ (command-line tool)
- JDBC drivers for your target database(s)

### Installing Liquibase

#### On Linux/macOS

```bash
# Download and install Liquibase
wget https://github.com/liquibase/liquibase/releases/download/v5.0.1/liquibase-5.0.1.tar.gz
tar -xzf liquibase-5.0.1.tar.gz -C /opt/liquibase
export PATH=$PATH:/opt/liquibase

# Verify installation
liquibase --version
```

#### On Windows

Download from [Liquibase Downloads](https://www.liquibase.org/download) and add to PATH.

### Installing JDBC Drivers

Liquibase requires JDBC drivers for database connectivity. Install them using Liquibase Package Manager (LPM):

```bash
# PostgreSQL
liquibase lpm add postgresql --global

# Microsoft SQL Server
liquibase lpm add mssql --global

# Snowflake
liquibase lpm add snowflake --global
```

## Installation Methods

### Method 1: Install from Source (Development)

```bash
# Clone the repository
git clone https://github.com/davidvupham/dbtools.git
cd dbtools/gds_liquibase

# Install in editable mode (recommended for development)
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Method 2: Install from Built Package

```bash
# Build the package
cd dbtools/gds_liquibase
python setup.py sdist bdist_wheel

# Install the wheel
pip install dist/gds_liquibase-0.1.0-py3-none-any.whl
```

### Method 3: Install from PyPI (Future)

When published to PyPI:

```bash
pip install gds-liquibase
```

## Verifying Installation

```python
# Verify the package is installed
python -c "import gds_liquibase; print(gds_liquibase.__version__)"

# Check available modules
python -c "from gds_liquibase import LiquibaseConfig, LiquibaseMigrationRunner, ChangelogManager; print('All imports successful')"
```

## Configuration

### Environment Variables

Set these environment variables for configuration:

```bash
export LIQUIBASE_CHANGELOG_FILE="changelogs/db.changelog-master.xml"
export LIQUIBASE_URL="jdbc:postgresql://localhost:5432/mydb"
export LIQUIBASE_USERNAME="dbuser"
export LIQUIBASE_PASSWORD="dbpass"
export LIQUIBASE_CONTEXTS="dev"
export LIQUIBASE_LOG_LEVEL="INFO"
```

### Properties File

Create a `liquibase.properties` file:

```properties
changeLogFile=changelogs/db.changelog-master.xml
url=jdbc:postgresql://localhost:5432/mydb
username=dbuser
password=${DB_PASSWORD}
driver=org.postgresql.Driver
contexts=dev
logLevel=INFO
```

## Usage Examples

### Example 1: Basic Migration

```python
from gds_liquibase import LiquibaseConfig, LiquibaseMigrationRunner

# Configure from environment
config = LiquibaseConfig.from_env()

# Run migrations
runner = LiquibaseMigrationRunner(config)
result = runner.update()

print("Migration successful!")
```

### Example 2: Using with PostgreSQL

```python
from gds_liquibase import LiquibaseConfig, LiquibaseMigrationRunner

config = LiquibaseConfig(
    changelog_file="changelogs/postgres/db.changelog-master.xml",
    url="jdbc:postgresql://localhost:5432/mydb",
    username="postgres",
    password="postgres",
    contexts="dev,test",
)

runner = LiquibaseMigrationRunner(config)

# Check status
runner.status(verbose=True)

# Run update
runner.update()

# Tag the current state
runner.tag("v1.0.0")
```

### Example 3: Rollback Operations

```python
from gds_liquibase import LiquibaseConfig, LiquibaseMigrationRunner

config = LiquibaseConfig.from_env()
runner = LiquibaseMigrationRunner(config)

# Generate rollback SQL (dry-run)
runner.rollback_sql("v1.0.0", output_file="rollback.sql")
print("Review rollback.sql before executing")

# Execute rollback
runner.rollback("v1.0.0")
```

### Example 4: Changelog Management

```python
from pathlib import Path
from gds_liquibase import ChangelogManager

# Create manager
manager = ChangelogManager(Path("changelogs"))

# Create new changelog
changelog = manager.create_changelog(
    author="developer@example.com",
    description="Initial schema setup",
    output_file=Path("changelogs/db.changelog-1.0.xml"),
)

# List changesets
changesets = manager.list_changesets(changelog)
for cs in changesets:
    print(f"ID: {cs['id']}, Author: {cs['author']}")
```

### Example 5: Integration with GDS Packages

```python
from gds_postgres import PostgresConnection
from gds_liquibase import LiquibaseConfig, LiquibaseMigrationRunner

# Get connection info from gds_postgres
pg_conn = PostgresConnection(
    host="localhost",
    port=5432,
    database="mydb",
    user="postgres",
    password="postgres",
)

# Build JDBC URL for Liquibase
jdbc_url = f"jdbc:postgresql://{pg_conn.host}:{pg_conn.port}/{pg_conn.database}"

# Configure Liquibase
config = LiquibaseConfig(
    changelog_file="changelogs/db.changelog-master.xml",
    url=jdbc_url,
    username=pg_conn.user,
    password=pg_conn.password,
)

# Run migrations
runner = LiquibaseMigrationRunner(config)
runner.update()
```

## Troubleshooting

### Issue: "Liquibase executable not found"

**Solution**: Ensure Liquibase is installed and added to your PATH:

```bash
# Check if Liquibase is in PATH
which liquibase

# If not found, add to PATH
export PATH=$PATH:/path/to/liquibase
```

### Issue: "JDBC driver not found"

**Solution**: Install the required JDBC driver:

```bash
# For PostgreSQL
liquibase lpm add postgresql --global

# For SQL Server
liquibase lpm add mssql --global
```

### Issue: Import errors

**Solution**: Reinstall the package:

```bash
pip uninstall gds-liquibase
pip install -e .
```

### Issue: Missing dependencies

**Solution**: Install all dependencies:

```bash
# Install from requirements
pip install -r requirements.txt

# Or install with setup.py
pip install -e ".[dev]"
```

## Additional Resources

- [Project Plan](PROJECT_PLAN.md) - Comprehensive implementation documentation
- [Examples Directory](examples/) - Working code samples
- [Liquibase Documentation](https://docs.liquibase.com/)
- [GitHub Repository](https://github.com/davidvupham/dbtools)

## Getting Help

For issues or questions:

1. Check the [examples](examples/) directory
2. Review the [PROJECT_PLAN.md](PROJECT_PLAN.md)
3. Check Liquibase documentation
4. Open an issue on GitHub
