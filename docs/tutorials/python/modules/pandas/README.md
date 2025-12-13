# Pandas Tutorial

Data manipulation and analysis for Python.

## Overview

**Pandas** provides DataFrames for tabular data, powerful I/O, and expressive operations for data analysis.

| | |
|---|---|
| **Package** | `pandas` |
| **Install** | `pip install pandas` |
| **Docs** | [pandas.pydata.org](https://pandas.pydata.org/docs/) |

---

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Reading Data](#reading-data)
- [Selection](#selection)
- [Data Cleaning](#data-cleaning)
- [Transformations](#transformations)
- [GroupBy](#groupby)
- [Merging](#merging)
- [Time Series](#time-series)
- [Performance Tips](#performance-tips)
- [Quick Reference](#quick-reference)

---

## Quick Start

```python
import pandas as pd

df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
})

print(df.head())
print(df.describe())
```

---

## Reading Data

```python
# CSV
df = pd.read_csv('data.csv')
df.to_csv('output.csv', index=False)

# Excel
df = pd.read_excel('data.xlsx')
df.to_excel('output.xlsx', index=False)

# Parquet
df = pd.read_parquet('data.parquet')
df.to_parquet('output.parquet')

# SQL
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:pass@localhost/db')
df = pd.read_sql('SELECT * FROM users', engine)
df.to_sql('users', engine, if_exists='replace', index=False)
```

---

## Selection

```python
# Columns
df['name']              # Series
df[['name', 'age']]     # DataFrame

# Rows by position
df.iloc[0]              # First row
df.iloc[0:5]            # First 5 rows

# Rows by label
df.loc[0, 'name']       # Single value
df.loc[df['age'] > 25]  # Filter

# Boolean filtering
df[df['age'] > 25]
df[(df['age'] > 25) & (df['city'] == 'NYC')]
df[df['city'].isin(['NYC', 'LA'])]
```

---

## Data Cleaning

```python
# Missing values
df.isna().sum()                  # Count missing
df.dropna()                      # Drop rows with NaN
df.fillna(0)                     # Fill with value
df['col'].fillna(df['col'].mean())  # Fill with mean

# Duplicates
df.drop_duplicates()

# Data types
df['age'] = df['age'].astype(int)
df['date'] = pd.to_datetime(df['date'])

# String cleaning
df['name'] = df['name'].str.strip().str.lower()
```

---

## Transformations

```python
# New columns
df['total'] = df['price'] * df['quantity']

# Apply function
df['age_group'] = df['age'].apply(lambda x: 'senior' if x > 60 else 'adult')

# Conditional
import numpy as np
df['status'] = np.where(df['age'] >= 18, 'adult', 'minor')

# Rename
df = df.rename(columns={'old': 'new'})

# Sort
df = df.sort_values('age', ascending=False)
```

---

## GroupBy

```python
# Basic aggregation
df.groupby('city')['sales'].sum()
df.groupby('city')['sales'].agg(['sum', 'mean', 'count'])

# Named aggregations
df.groupby('city').agg(
    total=('sales', 'sum'),
    average=('sales', 'mean'),
)

# Transform (same-size output)
df['city_avg'] = df.groupby('city')['sales'].transform('mean')
```

---

## Merging

```python
# Merge (SQL-style join)
merged = pd.merge(df1, df2, on='id', how='left')

# Concat
combined = pd.concat([df1, df2], ignore_index=True)
```

---

## Time Series

```python
# DateTime index
df['date'] = pd.to_datetime(df['date'])
df = df.set_index('date')

# Resample
monthly = df.resample('M').sum()

# Rolling average
df['ma_7'] = df['value'].rolling(7).mean()
```

---

## Performance Tips

Optimizing pandas for speed and memory efficiency is critical for larger datasets.

### 1. Speed Up read_csv
- **Specify dtypes**: Helps pandas avoid scanning the whole file to guess types.
- **Use `usecols`**: Load only what you need.
- **Chunking**: Process massive files in pieces.

```python
# Efficient loading
df = pd.read_csv('large_data.csv',
    usecols=['date', 'store_id', 'sales'],
    dtype={'store_id': 'int32', 'sales': 'float32'},
    chunksize=50_000
)
```

### 2. Efficient Data Types
Downcast numeric types and use `category` for low-cardinality string columns to save memory.

```python
df['id'] = df['id'].astype('int32')          # vs int64
df['price'] = df['price'].astype('float32')  # vs float64
df['status'] = df['status'].astype('category') # Awesome for repeated strings
```

### 3. Vectorization (Stop Looping)
Avoid `for` loops and `.apply()` when possible. Pandas vectorized operations run in C and are much faster.

```python
# SLOW
df['tax'] = df['price'].apply(lambda x: x * 0.1)

# FAST (Vectorized)
df['tax'] = df['price'] * 0.1
```

### 4. Proper Indexing
- **`loc`**: Label-based (safer, clearer).
- **`iloc`**: Position-based.
- Avoid chained indexing `df[mask]['col'] = 1` which causes `SettingWithCopyWarning`.

```python
# Good
df.loc[df['price'] > 100, 'category'] = 'premium'
```

### 5. Query for Clean Filtering
`query()` allows for SQL-like syntax which is often cleaner and can be optimized.

```python
# Complex boolean indexing
df_high = df[(df['price'] > 100) & (df['quantity'] < 5)]

# Clean query
df_high = df.query('price > 100 and quantity < 5')
```

### 6. Aggregations (Categoricals)
Converting strings to categories speeds up GroupBy operations significantly because pandas groups by the underlying integer codes, not the strings.

### 7. Process in Chunks
For files larger than memory, process row-by-row or chunk-by-chunk.

```python
total_sales = 0
for chunk in pd.read_csv('massive_log.csv', chunksize=100000):
    total_sales += chunk['sales'].sum()
```


---

## Quick Reference

| Operation | Code |
|-----------|------|
| Shape | `df.shape` |
| Columns | `df.columns` |
| Types | `df.dtypes` |
| First N | `df.head(n)` |
| Stats | `df.describe()` |
| Missing | `df.isna().sum()` |
| Unique | `df['col'].nunique()` |

---

[← Back to Modules Index](../README.md)
