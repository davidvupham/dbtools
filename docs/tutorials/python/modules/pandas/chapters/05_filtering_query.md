# 05 — Filtering (boolean masks, `isin`, `between`, `query`)

Filtering is the workhorse of pandas analysis. This chapter shows readable, correct patterns.

## Boolean masks

```python
mask = (orders["customer"] == "Alice Smith") & (orders["revenue"] >= 500)
orders.loc[mask]
```

### Parentheses matter

Use parentheses around each condition when combining with `&` / `|`.

## `isin` for membership

```python
orders.loc[orders["category"].isin(["avocados", "bananas"])]
```

## `between` for ranges

```python
orders.loc[orders["revenue"].between(100, 500, inclusive="both")]
```

## String filtering

Case-insensitive contains, safe with missing values:

```python
mask = orders["customer"].str.contains("ali", case=False, na=False)
orders.loc[mask]
```

## `query()`

`query()` can be cleaner for complex filters:

```python
orders.query("revenue >= 500 and category in ['laptops', 'phones']")
```

Tips:

- Column names become variables.
- Strings inside the query need quotes.

## Filtering + selecting columns

```python
cols = ["order_id", "order_date", "customer", "category", "revenue"]
orders.loc[orders["revenue"].ge(500), cols]
```

## Common pitfall: NaN in boolean logic

Comparisons with `NaN` produce `False` (or `NaN` in some contexts). If a column can contain missing values, decide whether missing should be treated as `False`, `True`, or excluded.

## Summary

- Build a `mask`, then apply `df.loc[mask, ...]`.
- Use `isin`, `between`, and `.str.contains(..., na=False)` for common patterns.

## Next

Continue to [06 — Transformations](06_transform_assign.md).

[← Back to course home](../README.md)
