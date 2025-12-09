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

```python
# Use category for repeated strings
df['status'] = df['status'].astype('category')

# Read only needed columns
df = pd.read_csv('large.csv', usecols=['id', 'name'])

# Vectorized operations (fast)
df['total'] = df['a'] * df['b']  # Not loops!
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
