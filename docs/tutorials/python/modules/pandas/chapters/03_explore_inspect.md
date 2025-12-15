# 03 — Explore + inspect (EDA essentials)

Before you transform data, learn to **look at it** quickly and systematically.

Throughout this chapter we’ll assume you have a DataFrame like `orders`.

## The “first 60 seconds” checklist

```python
orders.shape
orders.columns
orders.dtypes
orders.head()
orders.tail()
orders.sample(5, random_state=0)
```

### `info()` answers: what types? how many missing?

```python
orders.info()
```

### `describe()` for numeric columns

```python
orders.describe(numeric_only=True)
```

If you want percentiles:

```python
orders["revenue"].describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99])
```

## Categorical sanity checks

`value_counts` is one of the best “data smell” detectors:

```python
orders["category"].value_counts(dropna=False)
orders["shipping_status"].value_counts(dropna=False)
```

Combine with `normalize=True` to see proportions:

```python
orders["shipping_status"].value_counts(normalize=True, dropna=False)
```

## Missingness

Counts and rates per column:

```python
missing_count = orders.isna().sum()
missing_rate = orders.isna().mean()

missing = (
    missing_count
    .to_frame("missing_count")
    .join(missing_rate.to_frame("missing_rate"))
    .sort_values("missing_rate", ascending=False)
)
missing
```

## Duplicates

```python
orders.duplicated().sum()
orders.duplicated(subset=["order_id"]).sum()
```

If you need to drop duplicates:

```python
orders = orders.drop_duplicates(subset=["order_id"], keep="first")
```

## Quick “quality gates” (assertions)

For analytics pipelines, it’s common to fail fast:

```python
assert orders["order_id"].is_unique
assert orders["quantity"].ge(0).all()
assert orders["price"].ge(0).all()
```

## Memory and performance awareness

```python
orders.memory_usage(deep=True).sum()
```

If you have repeated strings, `category` can save memory and speed groupby:

```python
orders["category"] = orders["category"].astype("category")
```

## Summary

- `shape/columns/dtypes/head/info/describe/value_counts` covers most early investigation.
- Always check missingness and duplicates before interpreting aggregates.

## Next

Continue to [04 — Indexing + selection](04_indexing_selection.md).

[← Back to course home](../README.md)
