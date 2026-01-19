# SQL Fundamentals for Python Developers

Essential SQL knowledge for working with databases in Python applications.

---

## Overview

SQL (Structured Query Language) is the standard language for relational databases. Before using ORMs like SQLAlchemy or SQLModel, understanding raw SQL helps you:

- Debug query performance issues
- Write complex queries ORMs can't easily express
- Understand what your ORM generates
- Work directly with databases when needed

### Prerequisites

- Basic Python knowledge
- No prior SQL experience required
- Access to any database (SQLite included with Python)

---

## Quick Start with SQLite

Python includes SQLite, perfect for learning:

```python
import sqlite3

# Create in-memory database
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

# Create a table
cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Insert data
cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Alice", "alice@example.com"))
conn.commit()

# Query data
cursor.execute("SELECT * FROM users")
print(cursor.fetchall())

conn.close()
```

---

## CRUD Operations

### CREATE (INSERT)

```sql
-- Insert single row
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');

-- Insert multiple rows
INSERT INTO users (name, email) VALUES
    ('Bob', 'bob@example.com'),
    ('Carol', 'carol@example.com');

-- Insert with default values
INSERT INTO users (name) VALUES ('Dave');
```

Python:

```python
# Single insert (always use parameters!)
cursor.execute(
    "INSERT INTO users (name, email) VALUES (?, ?)",
    ("Alice", "alice@example.com")
)

# Multiple inserts
users = [("Bob", "bob@example.com"), ("Carol", "carol@example.com")]
cursor.executemany("INSERT INTO users (name, email) VALUES (?, ?)", users)

conn.commit()
```

### READ (SELECT)

```sql
-- Select all columns
SELECT * FROM users;

-- Select specific columns
SELECT name, email FROM users;

-- Filter with WHERE
SELECT * FROM users WHERE name = 'Alice';

-- Multiple conditions
SELECT * FROM users WHERE name = 'Alice' AND email IS NOT NULL;
SELECT * FROM users WHERE name = 'Alice' OR name = 'Bob';

-- Pattern matching
SELECT * FROM users WHERE email LIKE '%@example.com';

-- Ordering
SELECT * FROM users ORDER BY name ASC;
SELECT * FROM users ORDER BY created_at DESC;

-- Limit results
SELECT * FROM users LIMIT 10;
SELECT * FROM users LIMIT 10 OFFSET 20;  -- Pagination
```

Python:

```python
# Fetch all results
cursor.execute("SELECT * FROM users")
all_users = cursor.fetchall()

# Fetch one result
cursor.execute("SELECT * FROM users WHERE id = ?", (1,))
user = cursor.fetchone()

# Fetch with parameters (prevents SQL injection!)
cursor.execute("SELECT * FROM users WHERE name = ?", (user_input,))

# Iterate over results
cursor.execute("SELECT name, email FROM users")
for name, email in cursor:
    print(f"{name}: {email}")
```

### UPDATE

```sql
-- Update specific rows
UPDATE users SET email = 'new@example.com' WHERE id = 1;

-- Update multiple columns
UPDATE users SET name = 'Alice Smith', email = 'alice.smith@example.com' WHERE id = 1;

-- Update with calculation
UPDATE products SET price = price * 1.10;  -- 10% price increase

-- CAUTION: Without WHERE, updates ALL rows!
UPDATE users SET active = false;  -- This updates EVERYONE
```

Python:

```python
cursor.execute(
    "UPDATE users SET email = ? WHERE id = ?",
    ("new@example.com", 1)
)
conn.commit()

# Check how many rows were affected
print(f"Updated {cursor.rowcount} rows")
```

### DELETE

```sql
-- Delete specific rows
DELETE FROM users WHERE id = 1;

-- Delete with condition
DELETE FROM users WHERE created_at < '2020-01-01';

-- CAUTION: Without WHERE, deletes ALL rows!
DELETE FROM users;  -- Deletes EVERYONE
```

Python:

```python
cursor.execute("DELETE FROM users WHERE id = ?", (1,))
conn.commit()
```

---

## Table Design

### Data Types

| SQLite | PostgreSQL | MySQL | Description |
|--------|------------|-------|-------------|
| INTEGER | INTEGER, BIGINT | INT, BIGINT | Whole numbers |
| REAL | FLOAT, DOUBLE | FLOAT, DOUBLE | Decimal numbers |
| TEXT | VARCHAR, TEXT | VARCHAR, TEXT | Strings |
| BLOB | BYTEA | BLOB | Binary data |
| NULL | NULL | NULL | No value |
| - | BOOLEAN | BOOLEAN | True/False |
| - | TIMESTAMP | DATETIME | Date and time |
| - | UUID | - | Unique identifiers |

### Constraints

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,              -- Unique identifier
    email TEXT NOT NULL UNIQUE,          -- Required and unique
    name TEXT NOT NULL,                  -- Required
    age INTEGER CHECK (age >= 0),        -- Validation
    role TEXT DEFAULT 'user',            -- Default value
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)  -- Relationship
);
```

### Indexes

Indexes speed up queries but slow down writes:

```sql
-- Create index on frequently queried column
CREATE INDEX idx_users_email ON users(email);

-- Composite index for multi-column queries
CREATE INDEX idx_posts_user_date ON posts(user_id, created_at);

-- Unique index (also enforces uniqueness)
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);
```

When to add indexes:
- Columns in WHERE clauses
- Columns in JOIN conditions
- Columns in ORDER BY
- Foreign key columns

---

## JOINs

Combine data from multiple tables.

### Sample Data

```sql
CREATE TABLE authors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE books (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author_id INTEGER,
    FOREIGN KEY (author_id) REFERENCES authors(id)
);

INSERT INTO authors VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Carol');
INSERT INTO books VALUES (1, 'Book A', 1), (2, 'Book B', 1), (3, 'Book C', NULL);
```

### INNER JOIN

Returns only matching rows from both tables:

```sql
SELECT books.title, authors.name
FROM books
INNER JOIN authors ON books.author_id = authors.id;

-- Result:
-- Book A | Alice
-- Book B | Alice
-- (Book C excluded - no matching author)
-- (Carol excluded - no books)
```

### LEFT JOIN

Returns all rows from left table, matching rows from right:

```sql
SELECT books.title, authors.name
FROM books
LEFT JOIN authors ON books.author_id = authors.id;

-- Result:
-- Book A | Alice
-- Book B | Alice
-- Book C | NULL  (included even without author)
```

### RIGHT JOIN

Returns all rows from right table, matching rows from left:

```sql
SELECT books.title, authors.name
FROM books
RIGHT JOIN authors ON books.author_id = authors.id;

-- Result:
-- Book A | Alice
-- Book B | Alice
-- NULL   | Bob   (included even without books)
-- NULL   | Carol (included even without books)
```

### FULL OUTER JOIN

Returns all rows from both tables:

```sql
-- Not supported in SQLite, but works in PostgreSQL
SELECT books.title, authors.name
FROM books
FULL OUTER JOIN authors ON books.author_id = authors.id;
```

### Join Multiple Tables

```sql
SELECT
    orders.id AS order_id,
    customers.name AS customer,
    products.name AS product,
    order_items.quantity
FROM orders
JOIN customers ON orders.customer_id = customers.id
JOIN order_items ON orders.id = order_items.order_id
JOIN products ON order_items.product_id = products.id;
```

---

## Aggregations

### Aggregate Functions

```sql
SELECT COUNT(*) FROM users;                    -- Count rows
SELECT COUNT(email) FROM users;                -- Count non-NULL values
SELECT COUNT(DISTINCT country) FROM users;     -- Count unique values

SELECT SUM(amount) FROM orders;                -- Sum
SELECT AVG(amount) FROM orders;                -- Average
SELECT MIN(amount) FROM orders;                -- Minimum
SELECT MAX(amount) FROM orders;                -- Maximum
```

### GROUP BY

Group rows and aggregate:

```sql
-- Count users per country
SELECT country, COUNT(*) as user_count
FROM users
GROUP BY country;

-- Total sales per product
SELECT product_id, SUM(quantity) as total_sold
FROM order_items
GROUP BY product_id;

-- Average order value per customer
SELECT customer_id, AVG(total) as avg_order
FROM orders
GROUP BY customer_id
ORDER BY avg_order DESC;
```

### HAVING

Filter groups (WHERE filters rows, HAVING filters groups):

```sql
-- Countries with more than 100 users
SELECT country, COUNT(*) as user_count
FROM users
GROUP BY country
HAVING COUNT(*) > 100;

-- Products sold more than 1000 times
SELECT product_id, SUM(quantity) as total
FROM order_items
GROUP BY product_id
HAVING SUM(quantity) > 1000;
```

### Query Order

```sql
SELECT column           -- 5. Select columns
FROM table              -- 1. From table
WHERE condition         -- 2. Filter rows
GROUP BY column         -- 3. Group rows
HAVING condition        -- 4. Filter groups
ORDER BY column         -- 6. Sort results
LIMIT n;                -- 7. Limit results
```

---

## Subqueries

### Scalar Subquery (Returns Single Value)

```sql
-- Users with above-average orders
SELECT name
FROM customers
WHERE total_orders > (SELECT AVG(total_orders) FROM customers);
```

### Table Subquery (Returns Rows)

```sql
-- Products that have been ordered
SELECT * FROM products
WHERE id IN (SELECT DISTINCT product_id FROM order_items);

-- Products that have NEVER been ordered
SELECT * FROM products
WHERE id NOT IN (SELECT DISTINCT product_id FROM order_items);
```

### Correlated Subquery

References outer query (runs once per row):

```sql
-- Customers with their latest order date
SELECT
    name,
    (SELECT MAX(created_at)
     FROM orders
     WHERE orders.customer_id = customers.id) as last_order
FROM customers;
```

### Common Table Expressions (CTEs)

More readable alternative to subqueries:

```sql
-- Find top customers and their orders
WITH top_customers AS (
    SELECT customer_id, SUM(total) as lifetime_value
    FROM orders
    GROUP BY customer_id
    ORDER BY lifetime_value DESC
    LIMIT 10
)
SELECT
    customers.name,
    top_customers.lifetime_value
FROM top_customers
JOIN customers ON top_customers.customer_id = customers.id;
```

---

## Transactions

Ensure data consistency by grouping operations:

```python
import sqlite3

conn = sqlite3.connect("bank.db")
cursor = conn.cursor()

try:
    # Start transaction (implicit in Python)

    # Withdraw from account A
    cursor.execute(
        "UPDATE accounts SET balance = balance - ? WHERE id = ?",
        (100, account_a_id)
    )

    # Check balance didn't go negative
    cursor.execute("SELECT balance FROM accounts WHERE id = ?", (account_a_id,))
    if cursor.fetchone()[0] < 0:
        raise ValueError("Insufficient funds")

    # Deposit to account B
    cursor.execute(
        "UPDATE accounts SET balance = balance + ? WHERE id = ?",
        (100, account_b_id)
    )

    # Commit transaction
    conn.commit()

except Exception as e:
    # Rollback on any error
    conn.rollback()
    raise

finally:
    conn.close()
```

### Context Manager Pattern

```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def transaction(conn):
    try:
        yield conn.cursor()
        conn.commit()
    except Exception:
        conn.rollback()
        raise

# Usage
conn = sqlite3.connect("database.db")
with transaction(conn) as cursor:
    cursor.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
    cursor.execute("INSERT INTO users (name) VALUES (?)", ("Bob",))
# Auto-commit if no exception, auto-rollback if exception
```

---

## SQL Injection Prevention

Never concatenate user input into SQL:

```python
# DANGEROUS - SQL injection vulnerability!
user_input = "'; DROP TABLE users; --"
cursor.execute(f"SELECT * FROM users WHERE name = '{user_input}'")

# SAFE - Use parameterized queries
cursor.execute("SELECT * FROM users WHERE name = ?", (user_input,))
```

### Parameterized Queries by Database

```python
# SQLite - ? placeholders
cursor.execute("SELECT * FROM users WHERE name = ?", (name,))

# PostgreSQL (psycopg2) - %s placeholders
cursor.execute("SELECT * FROM users WHERE name = %s", (name,))

# PostgreSQL (psycopg3) - %s or $1 placeholders
cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
cursor.execute("SELECT * FROM users WHERE name = $1", (name,))

# MySQL - %s placeholders
cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
```

---

## Python Database Libraries

### SQLite (Built-in)

```python
import sqlite3

conn = sqlite3.connect("database.db")
conn.row_factory = sqlite3.Row  # Access columns by name
cursor = conn.cursor()

cursor.execute("SELECT * FROM users WHERE id = ?", (1,))
user = cursor.fetchone()
print(user["name"])  # Access by column name

conn.close()
```

### PostgreSQL (psycopg)

```bash
uv add psycopg[binary]
```

```python
import psycopg

with psycopg.connect("postgresql://user:pass@localhost/mydb") as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE id = %s", (1,))
        user = cursor.fetchone()
        print(user)
```

### Connection Pooling

```python
from psycopg_pool import ConnectionPool

pool = ConnectionPool(
    "postgresql://user:pass@localhost/mydb",
    min_size=5,
    max_size=20
)

with pool.connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
```

---

## Common Patterns

### Upsert (Insert or Update)

```sql
-- SQLite
INSERT INTO users (email, name) VALUES ('alice@example.com', 'Alice')
ON CONFLICT(email) DO UPDATE SET name = excluded.name;

-- PostgreSQL
INSERT INTO users (email, name) VALUES ('alice@example.com', 'Alice')
ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name;
```

### Pagination

```sql
-- Offset-based (simple but slow for large offsets)
SELECT * FROM posts ORDER BY created_at DESC LIMIT 20 OFFSET 40;

-- Cursor-based (better performance)
SELECT * FROM posts
WHERE created_at < '2024-01-15 10:30:00'
ORDER BY created_at DESC
LIMIT 20;
```

### Soft Delete

```sql
-- Add deleted_at column
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP;

-- "Delete" by setting timestamp
UPDATE users SET deleted_at = CURRENT_TIMESTAMP WHERE id = 1;

-- Query only active users
SELECT * FROM users WHERE deleted_at IS NULL;
```

### Audit Columns

```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    -- ... other columns ...
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    updated_at TIMESTAMP,
    updated_by INTEGER REFERENCES users(id)
);
```

---

## Quick Reference

### Query Cheat Sheet

```sql
-- Select
SELECT columns FROM table WHERE condition ORDER BY column LIMIT n;

-- Insert
INSERT INTO table (columns) VALUES (values);

-- Update
UPDATE table SET column = value WHERE condition;

-- Delete
DELETE FROM table WHERE condition;

-- Join
SELECT * FROM a JOIN b ON a.id = b.a_id;

-- Aggregate
SELECT column, COUNT(*) FROM table GROUP BY column HAVING count > n;

-- Subquery
SELECT * FROM table WHERE column IN (SELECT column FROM other);
```

### Common Functions

```sql
-- String
UPPER(text), LOWER(text), LENGTH(text), TRIM(text)
CONCAT(a, b), SUBSTRING(text, start, length)

-- Numeric
ABS(n), ROUND(n, decimals), FLOOR(n), CEIL(n)

-- Date (varies by database)
CURRENT_DATE, CURRENT_TIMESTAMP
DATE(timestamp), EXTRACT(YEAR FROM date)

-- NULL handling
COALESCE(a, b, c)  -- Returns first non-NULL
NULLIF(a, b)       -- Returns NULL if a = b
IFNULL(a, b)       -- Returns b if a is NULL (SQLite/MySQL)
```

---

## See Also

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [PostgreSQL Tutorial](https://www.postgresql.org/docs/current/tutorial.html)
- [SQLModel →](../../backend/sqlmodel/README.md) - Python ORM built on SQLAlchemy
- [pyodbc →](../../backend/pyodbc/README.md) - Database connectivity for Python
- [Mode SQL Tutorial](https://mode.com/sql-tutorial/)
- [SQLBolt Interactive Lessons](https://sqlbolt.com/)

---

[← Docker](../docker/README.md) | [← Back to Module 4](../../README.md)
