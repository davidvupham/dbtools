# Solutions — 01_series_dataframe: Series + DataFrame fundamentals

## What this solution demonstrates

- Series is 1D with labels.
- Operations align by labels (index), not by position.
- Vectorized column operations beat Python loops.

## Why this pattern

Most “weird” pandas behavior is actually alignment; understanding this prevents subtle bugs.

## Common pitfalls

- Assuming Series addition is positional like Python lists.
- Mixing numeric + strings without checking dtypes.

## One useful variant

Try `.add(other, fill_value=0)` to control how missing labels are handled.

## Expected output (example)

- Series prints with your custom index labels.
- Adding misaligned Series produces `NaN` for labels that don’t overlap.
- `revenue` column equals `quantity * price` for each row.

## Reference implementation

```python
import pandas as pd

s = pd.Series([10, 20, 30], index=["a", "b", "c"], name="points")
print(s)
print(s.index)
print(s.dtype)

a = pd.Series([1, 2, 3], index=["x", "y", "z"])
b = pd.Series([10, 20, 30], index=["y", "z", "w"])
print(a + b)  # alignment by labels; missing labels produce NaN

df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35], "country": ["US", "CA", "UK"]})
print(type(df["age"]))
print(type(df[["name", "age"]]))

orders = pd.DataFrame({"quantity": [1, 2, 3], "price": [10.0, 4.5, 2.0]})
orders["revenue"] = orders["quantity"] * orders["price"]
print(orders)
```


[← Back to course home](../README.md)
