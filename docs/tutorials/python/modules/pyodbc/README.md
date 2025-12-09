# pyodbc Tutorial

ODBC database connectivity for Python.

## Overview

**pyodbc** is an open-source Python module for accessing ODBC databases. It implements the Python DB API 2.0 specification and works with any database that has an ODBC driver.

| | |
|---|---|
| **Package** | `pyodbc` |
| **Install** | `pip install pyodbc` |
| **Docs** | [github.com/mkleehammer/pyodbc](https://github.com/mkleehammer/pyodbc/wiki) |

---

## Installation

```bash
pip install pyodbc
```

### ODBC Drivers

Install the appropriate driver for your database:

**SQL Server (Windows):**

```
# Usually pre-installed, or download from Microsoft
```

**SQL Server (Linux/Mac):**

```bash
# Ubuntu/Debian
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
apt-get install -y msodbcsql18

# macOS
brew install unixodbc
brew install --no-sandbox msodbcsql18
```

**PostgreSQL:**

```bash
apt-get install odbc-postgresql
```

---

## Quick Start

```python
import pyodbc

# Connect to SQL Server
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'SERVER=localhost;'
    'DATABASE=mydb;'
    'UID=user;'
    'PWD=password;'
    'TrustServerCertificate=yes;'
)

# Execute query
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")

# Fetch results
for row in cursor:
    print(row.id, row.name)

# Clean up
cursor.close()
conn.close()
```

---

## Connection Strings

### SQL Server

```python
# Windows Authentication
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'SERVER=localhost;'
    'DATABASE=mydb;'
    'Trusted_Connection=yes;'
)

# SQL Server Authentication
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'SERVER=server.example.com;'
    'DATABASE=mydb;'
    'UID=username;'
    'PWD=password;'
)

# Named instance
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'SERVER=server\\INSTANCE;'
    'DATABASE=mydb;'
    'UID=username;'
    'PWD=password;'
)
```

### PostgreSQL

```python
conn = pyodbc.connect(
    'DRIVER={PostgreSQL Unicode};'
    'SERVER=localhost;'
    'PORT=5432;'
    'DATABASE=mydb;'
    'UID=username;'
    'PWD=password;'
)
```

### MySQL

```python
conn = pyodbc.connect(
    'DRIVER={MySQL ODBC 8.0 Driver};'
    'SERVER=localhost;'
    'DATABASE=mydb;'
    'UID=username;'
    'PWD=password;'
)
```

---

## Queries and Parameters

### Basic Queries

```python
cursor = conn.cursor()

# SELECT
cursor.execute("SELECT id, name FROM users")
rows = cursor.fetchall()

# Fetch one
row = cursor.fetchone()
print(row.id, row.name)

# Fetch many
rows = cursor.fetchmany(10)
```

### Parameterized Queries

```python
# Single parameter (use ? placeholder)
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# Multiple parameters
cursor.execute(
    "SELECT * FROM users WHERE age > ? AND city = ?",
    (25, 'NYC')
)

# INSERT with parameters
cursor.execute(
    "INSERT INTO users (name, email) VALUES (?, ?)",
    ('Alice', 'alice@example.com')
)
conn.commit()

# Named parameters (SQL Server)
cursor.execute(
    "EXEC sp_get_user @user_id = ?",
    (user_id,)
)
```

### Batch Insert

```python
# executemany for bulk inserts
data = [
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com'),
    ('Charlie', 'charlie@example.com'),
]

cursor.executemany(
    "INSERT INTO users (name, email) VALUES (?, ?)",
    data
)
conn.commit()
```

---

## Transactions

```python
# Auto-commit off by default
conn = pyodbc.connect(connection_string, autocommit=False)

try:
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders ...")
    cursor.execute("UPDATE inventory ...")
    conn.commit()  # Commit transaction
except Exception as e:
    conn.rollback()  # Rollback on error
    raise
```

### Auto-commit Mode

```python
# Enable auto-commit
conn.autocommit = True

# Or at connection time
conn = pyodbc.connect(connection_string, autocommit=True)
```

---

## Error Handling

```python
import pyodbc

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM non_existent_table")
except pyodbc.OperationalError as e:
    print(f"Connection error: {e}")
except pyodbc.ProgrammingError as e:
    print(f"SQL error: {e}")
except pyodbc.Error as e:
    print(f"Database error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
```

---

## Context Managers

```python
import pyodbc
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = pyodbc.connect(connection_string)
    try:
        yield conn
    finally:
        conn.close()

# Usage
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    for row in cursor:
        print(row)
```

---

## Pandas Integration

```python
import pandas as pd
import pyodbc

conn = pyodbc.connect(connection_string)

# Read to DataFrame
df = pd.read_sql("SELECT * FROM users", conn)

# Read with parameters
df = pd.read_sql(
    "SELECT * FROM users WHERE city = ?",
    conn,
    params=['NYC']
)

# Write DataFrame to table
from sqlalchemy import create_engine

# For writing, SQLAlchemy is easier
engine = create_engine('mssql+pyodbc:///?odbc_connect=' + connection_string)
df.to_sql('users', engine, if_exists='append', index=False)
```

---

## Performance Tips

### 1. Use executemany for Bulk Operations

```python
# Fast batch insert
cursor.fast_executemany = True
cursor.executemany(
    "INSERT INTO table (a, b) VALUES (?, ?)",
    data_list
)
```

### 2. Fetch in Batches

```python
# For large result sets
cursor.execute("SELECT * FROM large_table")
while True:
    rows = cursor.fetchmany(1000)
    if not rows:
        break
    process(rows)
```

### 3. Set Row Array Size

```python
# Increase fetch buffer
cursor.arraysize = 1000
```

---

## Quick Reference

### Connection

```python
conn = pyodbc.connect(connection_string)
conn.close()
conn.commit()
conn.rollback()
```

### Cursor

```python
cursor = conn.cursor()
cursor.execute(sql, params)
cursor.executemany(sql, param_list)
cursor.fetchone()
cursor.fetchall()
cursor.fetchmany(n)
cursor.close()
```

### Common Drivers

| Database | Driver Name |
|----------|-------------|
| SQL Server | `ODBC Driver 18 for SQL Server` |
| PostgreSQL | `PostgreSQL Unicode` |
| MySQL | `MySQL ODBC 8.0 Driver` |

---

## See Also

- [pyodbc Wiki](https://github.com/mkleehammer/pyodbc/wiki)
- [SQLModel Tutorial](../sqlmodel/README.md) - Type-safe ORM alternative
- [Pandas Tutorial](../pandas/README.md) - DataFrame integration

---

[← Back to Modules Index](../README.md)
