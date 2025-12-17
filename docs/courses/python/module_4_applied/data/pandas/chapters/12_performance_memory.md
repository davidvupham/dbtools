# 12 — Performance + memory + Copy-on-Write

Pandas can be very fast, but performance depends on:

- dtype choices
- vectorization
- avoiding Python loops
- avoiding repeated expensive operations

## Measure before optimizing

Start with quick checks:

```python
orders.memory_usage(deep=True).sum()
orders.dtypes
```

## Dtypes: biggest lever

### Categoricals for repeated strings

```python
orders["category"] = orders["category"].astype("category")
orders["shipping_status"] = orders["shipping_status"].astype("category")
```

### Downcast numerics

```python
import pandas as pd

orders["quantity"] = pd.to_numeric(orders["quantity"], downcast="integer")
orders["price"] = pd.to_numeric(orders["price"], downcast="float")
```

## Avoid `apply` (most of the time)

Prefer:

- `+`, `-`, `*`, `/`
- `np.where`, `np.select`
- `.str` for strings
- `.dt` for datetimes

## Chunking for large CSV

```python
import pandas as pd

total = 0.0
for chunk in pd.read_csv("massive.csv", usecols=["sales"], chunksize=200_000):
    total += chunk["sales"].sum()
```

## Copy-on-Write (CoW)

Pandas has an evolving Copy-on-Write model. In pandas 2.2 it is opt-in and planned to become the default in pandas 3.0.

Official docs: `https://pandas.pydata.org/pandas-docs/version/2.2/user_guide/copy_on_write.html`

Enable CoW:

```python
import pandas as pd

pd.options.mode.copy_on_write = True
```

Or enable warning mode while migrating:

```python
import pandas as pd

pd.options.mode.copy_on_write = "warn"
```

## SettingWithCopyWarning: what to do

The best habit is: **do assignments with `.loc[...] = ...`**.

```python
mask = orders["revenue"].ge(500)
orders.loc[mask, "segment"] = "high"
```

## When pandas might not be the best tool

If you need out-of-core processing, SQL-heavy analytics, or very large joins:

- DuckDB (SQL engine) can be a better fit
- Polars can be faster for some workloads

(We keep this course pandas-centered, but it’s helpful to know the boundary.)

## Summary

- Fix dtypes early.
- Prefer vectorized ops.
- Use chunking for huge CSV.
- Understand CoW and avoid chained assignment.

## Next

Continue to [13 — Case studies](13_case_studies.md).

[← Back to course home](../README.md)
