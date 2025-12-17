# 01 — Series + DataFrame fundamentals

This chapter teaches the core objects and the behaviors that make pandas powerful: labeled axes, alignment, and vectorized operations.

## Series

A `Series` is a 1D labeled array.

```python
import pandas as pd

s = pd.Series([10, 20, 30], index=["a", "b", "c"], name="points")
print(s)
print(s.index)
print(s.dtype)
```

### Alignment (the “pandas superpower”)

Operations align on labels, not positions:

```python
import pandas as pd

a = pd.Series([1, 2, 3], index=["x", "y", "z"])
b = pd.Series([10, 20, 30], index=["y", "z", "w"])

# Notice how labels align; missing labels become NaN
print(a + b)
```

## DataFrame

A `DataFrame` is a 2D table with labeled rows and columns.

```python
import pandas as pd

df = pd.DataFrame(
    {
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 30, 35],
        "country": ["US", "CA", "UK"],
    }
)

print(df)
print(df.dtypes)
```

### Columns are Series

```python
ages = df["age"]
print(type(ages))
```

### Vectorized operations

Prefer vectorized operations over loops:

```python
import pandas as pd

orders = pd.DataFrame({"quantity": [1, 2, 3], "price": [10.0, 4.5, 2.0]})
orders["revenue"] = orders["quantity"] * orders["price"]
```

### `assign` encourages readable pipelines

```python
import pandas as pd

orders = pd.DataFrame({"quantity": [1, 2, 3], "price": [10.0, 4.5, 2.0]})
orders2 = orders.assign(revenue=lambda d: d["quantity"] * d["price"])
```

## Index basics

Pandas always has an index (row labels). You can set your own meaningful index:

```python
import pandas as pd

df = pd.DataFrame({"id": ["u1", "u2"], "score": [10, 20]}).set_index("id")
print(df.loc["u1", "score"])
```

## When you see NaN

`NaN` often means “missing” (or “not applicable”). It can appear after alignment, merges, type coercion, or parsing.

```python
import pandas as pd

s = pd.Series([1, None, 3])
print(s.isna())
```

## Summary

- Series/DataFrames are **labeled**.
- Labels cause **alignment**, which is powerful but can surprise you.
- Prefer vectorized ops and pipelines.

## Next

Continue to [02 — I/O + dtypes](02_io.md).

[← Back to course home](../README.md)
