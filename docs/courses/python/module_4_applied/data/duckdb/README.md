# DuckDB Tutorial

In-memory analytics database for Python.

## Overview

**DuckDB** is an embedded analytical database, often called "SQLite for analytics." It runs directly within your Python process, enabling fast OLAP queries on large datasets without a separate server.

| | |
|---|---|
| **Package** | `duckdb` |
| **Install** | `pip install duckdb` |
| **Documentation** | [duckdb.org/docs](https://duckdb.org/docs/) |
| **GitHub** | [duckdb/duckdb](https://github.com/duckdb/duckdb) |

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [In-Memory vs Persistent](#in-memory-vs-persistent)
4. [SQL Queries](#sql-queries)
5. [Reading Files](#reading-files)
6. [Pandas Integration](#pandas-integration)
7. [Window Functions](#window-functions)
8. [User-Defined Functions](#user-defined-functions)
9. [Performance Tips](#performance-tips)
10. [When to Use DuckDB](#when-to-use-duckdb)

---

## Installation

```bash
pip install duckdb
```

For additional format support:

```bash
pip install duckdb pandas pyarrow  # Pandas + Arrow
```

---

## Quick Start

```python
import duckdb

# Run a query directly
result = duckdb.sql("SELECT 42 AS answer").fetchall()
print(result)  # [(42,)]

# Query with Pandas result
df = duckdb.sql("SELECT * FROM range(10) AS t(id)").df()
print(df)

# Query files directly
df = duckdb.sql("SELECT * FROM 'data.csv' LIMIT 10").df()
```

---

## In-Memory vs Persistent

### In-Memory Database (Default)

```python
import duckdb

# Create in-memory connection
con = duckdb.connect()

# Create table
con.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name VARCHAR,
        email VARCHAR
    )
""")

# Insert data
con.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')")
con.execute("INSERT INTO users VALUES (2, 'Bob', 'bob@example.com')")

# Query
result = con.execute("SELECT * FROM users").fetchall()
print(result)

# Data is lost when connection closes
con.close()
```

### Persistent Database

```python
import duckdb

# Create persistent database file
con = duckdb.connect("my_database.duckdb")

# Create and populate tables
con.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY,
        product VARCHAR,
        amount DECIMAL(10,2),
        sale_date DATE
    )
""")

# Data persists across sessions
con.close()

# Reopen later
con = duckdb.connect("my_database.duckdb")
result = con.execute("SELECT * FROM sales").fetchall()
```

---

## SQL Queries

### Basic Queries

```python
import duckdb

# SELECT
df = duckdb.sql("SELECT * FROM 'data.csv'").df()

# WHERE
df = duckdb.sql("SELECT * FROM 'data.csv' WHERE amount > 100").df()

# ORDER BY
df = duckdb.sql("SELECT * FROM 'data.csv' ORDER BY date DESC").df()

# LIMIT
df = duckdb.sql("SELECT * FROM 'data.csv' LIMIT 10").df()
```

### Aggregations

```python
import duckdb

# Basic aggregations
df = duckdb.sql("""
    SELECT
        category,
        COUNT(*) AS count,
        SUM(amount) AS total,
        AVG(amount) AS average,
        MIN(amount) AS min_amount,
        MAX(amount) AS max_amount
    FROM 'sales.parquet'
    GROUP BY category
    ORDER BY total DESC
""").df()

# HAVING
df = duckdb.sql("""
    SELECT category, SUM(amount) AS total
    FROM 'sales.parquet'
    GROUP BY category
    HAVING SUM(amount) > 10000
""").df()
```

### Joins

```python
import duckdb

# INNER JOIN
df = duckdb.sql("""
    SELECT o.*, c.name AS customer_name
    FROM 'orders.parquet' o
    INNER JOIN 'customers.parquet' c ON o.customer_id = c.id
""").df()

# LEFT JOIN
df = duckdb.sql("""
    SELECT c.*, COUNT(o.id) AS order_count
    FROM 'customers.parquet' c
    LEFT JOIN 'orders.parquet' o ON c.id = o.customer_id
    GROUP BY c.*
""").df()
```

### Subqueries and CTEs

```python
import duckdb

# Common Table Expression (CTE)
df = duckdb.sql("""
    WITH monthly_sales AS (
        SELECT
            DATE_TRUNC('month', sale_date) AS month,
            SUM(amount) AS total
        FROM 'sales.parquet'
        GROUP BY 1
    )
    SELECT
        month,
        total,
        LAG(total) OVER (ORDER BY month) AS prev_month,
        total - LAG(total) OVER (ORDER BY month) AS growth
    FROM monthly_sales
    ORDER BY month
""").df()
```

---

## Reading Files

### CSV Files

```python
import duckdb

# Read CSV directly in query
df = duckdb.sql("SELECT * FROM 'data.csv'").df()

# With options
df = duckdb.sql("""
    SELECT * FROM read_csv('data.csv',
        header=true,
        delim=',',
        dateformat='%Y-%m-%d'
    )
""").df()

# Multiple files with glob
df = duckdb.sql("SELECT * FROM 'data/*.csv'").df()
```

### Parquet Files

```python
import duckdb

# Read Parquet (automatically detected)
df = duckdb.sql("SELECT * FROM 'data.parquet'").df()

# Read specific columns (efficient!)
df = duckdb.sql("""
    SELECT id, name, amount
    FROM 'data.parquet'
    WHERE amount > 100
""").df()

# Multiple Parquet files
df = duckdb.sql("SELECT * FROM 'data/*.parquet'").df()
```

### JSON Files

```python
import duckdb

# Read JSON
df = duckdb.sql("SELECT * FROM 'data.json'").df()

# Read JSON lines
df = duckdb.sql("SELECT * FROM read_json_auto('data.jsonl')").df()
```

### Remote Files (S3, HTTP)

```python
import duckdb

# Install and load httpfs extension
duckdb.sql("INSTALL httpfs; LOAD httpfs;")

# Read from URL
df = duckdb.sql("""
    SELECT * FROM 'https://example.com/data.parquet'
    LIMIT 1000
""").df()

# Read from S3
duckdb.sql("""
    SET s3_region='us-east-1';
    SET s3_access_key_id='YOUR_KEY';
    SET s3_secret_access_key='YOUR_SECRET';
""")

df = duckdb.sql("SELECT * FROM 's3://bucket/data.parquet'").df()
```

---

## Pandas Integration

### Query Pandas DataFrames

```python
import duckdb
import pandas as pd

# Create a Pandas DataFrame
df = pd.DataFrame({
    'id': [1, 2, 3, 4, 5],
    'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'score': [85, 92, 78, 95, 88]
})

# Query DataFrame directly with SQL
result = duckdb.sql("""
    SELECT name, score
    FROM df
    WHERE score > 80
    ORDER BY score DESC
""").df()

print(result)
```

### Join DataFrames and Files

```python
import duckdb
import pandas as pd

# In-memory DataFrame
users_df = pd.DataFrame({
    'user_id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie']
})

# Query combining DataFrame and file
result = duckdb.sql("""
    SELECT u.name, SUM(o.amount) AS total_spent
    FROM users_df u
    JOIN 'orders.parquet' o ON u.user_id = o.user_id
    GROUP BY u.name
    ORDER BY total_spent DESC
""").df()
```

### Convert Results

```python
import duckdb

# To Pandas DataFrame
df = duckdb.sql("SELECT * FROM 'data.parquet'").df()

# To Python list
rows = duckdb.sql("SELECT * FROM 'data.parquet'").fetchall()

# To Arrow Table
arrow_table = duckdb.sql("SELECT * FROM 'data.parquet'").arrow()

# To Polars DataFrame
polars_df = duckdb.sql("SELECT * FROM 'data.parquet'").pl()
```

---

## Window Functions

### Ranking Functions

```python
import duckdb

df = duckdb.sql("""
    SELECT
        name,
        department,
        salary,
        RANK() OVER (ORDER BY salary DESC) AS rank,
        DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank,
        ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num,
        NTILE(4) OVER (ORDER BY salary DESC) AS quartile
    FROM 'employees.parquet'
""").df()
```

### Aggregate Window Functions

```python
import duckdb

df = duckdb.sql("""
    SELECT
        date,
        sales,
        SUM(sales) OVER (ORDER BY date) AS running_total,
        AVG(sales) OVER (
            ORDER BY date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS moving_avg_7day,
        LAG(sales, 1) OVER (ORDER BY date) AS prev_day,
        LEAD(sales, 1) OVER (ORDER BY date) AS next_day
    FROM 'daily_sales.parquet'
""").df()
```

### Partition By

```python
import duckdb

df = duckdb.sql("""
    SELECT
        department,
        employee_name,
        salary,
        AVG(salary) OVER (PARTITION BY department) AS dept_avg,
        salary - AVG(salary) OVER (PARTITION BY department) AS vs_dept_avg,
        RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank
    FROM 'employees.parquet'
""").df()
```

---

## User-Defined Functions

### Python UDFs

```python
import duckdb

# Create connection
con = duckdb.connect()

# Register a simple UDF
def calculate_tax(amount: float) -> float:
    return amount * 0.08

con.create_function("calc_tax", calculate_tax, [duckdb.typing.DOUBLE], duckdb.typing.DOUBLE)

# Use the UDF
result = con.execute("""
    SELECT
        product,
        price,
        calc_tax(price) AS tax,
        price + calc_tax(price) AS total
    FROM products
""").df()
```

### Vectorized UDFs (Faster)

```python
import duckdb
import numpy as np

con = duckdb.connect()

# Vectorized UDF using numpy
def normalize(values):
    arr = np.array(values)
    return (arr - arr.mean()) / arr.std()

con.create_function(
    "normalize",
    normalize,
    [duckdb.typing.DOUBLE],
    duckdb.typing.DOUBLE,
    type="arrow"  # Vectorized
)
```

---

## Performance Tips

### 1. Use Parquet Format

```python
# Parquet is much faster than CSV
df = duckdb.sql("SELECT * FROM 'large_data.parquet'").df()  # Fast!
df = duckdb.sql("SELECT * FROM 'large_data.csv'").df()       # Slower

# Convert CSV to Parquet for repeated queries
duckdb.sql("""
    COPY (SELECT * FROM 'data.csv')
    TO 'data.parquet' (FORMAT PARQUET)
""")
```

### 2. Select Only Needed Columns

```python
# ✅ Select specific columns (fast)
df = duckdb.sql("""
    SELECT id, name, amount
    FROM 'large_data.parquet'
""").df()

# ❌ Select all columns (slower)
df = duckdb.sql("SELECT * FROM 'large_data.parquet'").df()
```

### 3. Push Down Filters

```python
# ✅ Filter in SQL (pushdown to Parquet)
df = duckdb.sql("""
    SELECT * FROM 'data.parquet'
    WHERE date >= '2024-01-01'
""").df()

# ❌ Filter in Python (loads all data first)
df = duckdb.sql("SELECT * FROM 'data.parquet'").df()
df = df[df['date'] >= '2024-01-01']
```

### 4. Use Persistent Database for Repeated Queries

```python
# Create persistent database with indexes
con = duckdb.connect("analytics.duckdb")

con.execute("""
    CREATE TABLE IF NOT EXISTS sales AS
    SELECT * FROM 'sales_*.parquet';

    CREATE INDEX idx_date ON sales(sale_date);
    CREATE INDEX idx_product ON sales(product_id);
""")

# Subsequent queries are faster
result = con.execute("""
    SELECT * FROM sales
    WHERE sale_date >= '2024-01-01'
""").df()
```

---

## When to Use DuckDB

### ✅ Use DuckDB When

- **Analyzing local files** (CSV, Parquet, JSON)
- **Ad-hoc data exploration** and EDA
- **ETL pipelines** processing large files
- **Embedded analytics** in applications
- **Jupyter notebook** data analysis
- **Data doesn't fit in Pandas** but fits on disk

### ❌ Consider Alternatives When

| Scenario | Better Choice |
|----------|---------------|
| Simple key-value lookups | SQLite |
| Concurrent writes needed | PostgreSQL |
| Distributed data (petabytes) | Spark, Trino |
| OLTP workloads | PostgreSQL, MySQL |
| Real-time streaming | ClickHouse, Kafka |

---

## Quick Reference

### Common Functions

```sql
-- String functions
SELECT UPPER(name), LOWER(name), LENGTH(name)

-- Date functions
SELECT DATE_TRUNC('month', date), EXTRACT(YEAR FROM date)

-- Aggregations
SELECT COUNT(*), SUM(x), AVG(x), MIN(x), MAX(x)

-- Window functions
SELECT RANK() OVER (ORDER BY x), LAG(x, 1) OVER (ORDER BY date)
```

### File Formats

| Format | Read | Write |
|--------|------|-------|
| CSV | `'file.csv'` | `COPY ... TO 'file.csv'` |
| Parquet | `'file.parquet'` | `COPY ... TO 'file.parquet'` |
| JSON | `'file.json'` | `COPY ... TO 'file.json'` |

---

## See Also

- [DuckDB Documentation](https://duckdb.org/docs/)
- [Pandas Tutorial](../pandas/README.md) - DataFrame operations
- [pyodbc Tutorial](../pyodbc/README.md) - Traditional database connectivity

---

[← Back to Modules Index](../README.md)
