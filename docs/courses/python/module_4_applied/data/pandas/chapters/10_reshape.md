# 10 — Reshaping (pivot, melt, stack/unstack)

Reshaping changes **the shape** of your data:

- long ↔ wide
- hierarchical indices
- summary tables

## `pivot_table` (recommended)

`pivot_table` handles duplicates via an aggregation function.

```python
pivot = orders.pivot_table(
    index="customer",
    columns="category",
    values="revenue",
    aggfunc="sum",
    fill_value=0,
)
```

## `pivot` (only when you know keys are unique)

If `(customer, category)` appears more than once, `pivot` will error.

```python
# orders.pivot(index="customer", columns="category", values="revenue")  # may fail if duplicates exist
```

## `melt` (wide → long)

```python
wide = pivot.reset_index()
long = wide.melt(id_vars=["customer"], var_name="category", value_name="revenue")
```

## `stack` / `unstack` (MultiIndex reshaping)

`stack` moves a column level into the index; `unstack` does the reverse.

```python
stacked = pivot.stack()       # Series with MultiIndex
unstacked = stacked.unstack() # back to wide
```

## MultiIndex basics you’ll need here

```python
mi = orders.set_index(["customer", "category"]).sort_index()

# slice a MultiIndex
mi.loc[("Alice Smith", "avocados"), :]
```

## Summary

- Use `pivot_table` for safe reshaping when duplicates exist.
- Use `melt` to return to long format.
- `stack/unstack` are powerful once you’re comfortable with MultiIndex.

## Next

Continue to [11 — Datetime + time series](11_datetime_timeseries.md).

[← Back to course home](../README.md)
