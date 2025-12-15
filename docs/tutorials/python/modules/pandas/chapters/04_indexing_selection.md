# 04 — Indexing + selection (`loc/iloc/at/iat`, MultiIndex)

Indexing is where many pandas bugs come from. This chapter focuses on **getting correct results** and avoiding ambiguous assignment.

Official reference: `https://pandas.pydata.org/pandas-docs/version/2.2.0/user_guide/indexing.html`

## The core accessors

- `loc`: label-based (row/column labels)
- `iloc`: position-based (integer positions)
- `at`: fast scalar label-based
- `iat`: fast scalar position-based

### Column selection

```python
orders["customer"]                 # Series
orders[["customer", "revenue"]]   # DataFrame
```

### Row selection

```python
orders.iloc[0]
orders.iloc[:5]
```

### Label-based selection

If your index is the default 0..n-1:

```python
orders.loc[0, "customer"]
```

If you set a meaningful index:

```python
by_id = orders.set_index("order_id")
by_id.loc[10, ["customer", "revenue"]]
```

## Slicing rules that commonly bite people

- `iloc` slicing is **end-exclusive**: `df.iloc[0:3]` returns rows 0,1,2.
- `loc` slicing is **label-inclusive** when the index is sorted: `df.loc["a":"c"]` includes the end label.

## Selecting rows and columns together

```python
mask = orders["revenue"].ge(500)
out = orders.loc[mask, ["order_id", "customer", "category", "revenue"]]
```

## Assignment: avoid chained indexing

Bad:

```python
# orders[mask]["flag"] = True  # avoid
```

Good:

```python
orders.loc[mask, "flag"] = True
```

If you intentionally want a separate object you can mutate freely:

```python
big = orders.loc[mask].copy()
big["flag"] = True
```

## Index management

### Set/reset index

```python
orders = orders.set_index("order_id")
orders = orders.reset_index()
```

### Sort by index for efficient range slicing

```python
orders = orders.set_index("order_date").sort_index()
jan = orders.loc["2025-01-01":"2025-01-31"]
```

## MultiIndex basics

MultiIndex is useful for hierarchical keys (e.g., customer + category).

```python
mi = orders.set_index(["customer", "category"]).sort_index()

# select all categories for one customer
mi.loc["Alice Smith"]

# select a specific (customer, category)
mi.loc[("Alice Smith", "avocados"), :]
```

## Summary

- Prefer `loc/iloc` explicitly.
- Prefer `.loc[mask, col] = value` for assignment.
- Use meaningful indices intentionally; don’t “accidentally” depend on default indices.

## Next

Continue to [05 — Filtering + query](05_filtering_query.md).

[← Back to course home](../README.md)
