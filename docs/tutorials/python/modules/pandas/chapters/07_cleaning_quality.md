# 07 — Cleaning + data quality

Cleaning is not “one-liners” — it’s making **explicit, documented decisions** about:

- missing values
- inconsistent categories
- bad types
- duplicates
- outliers
- invalid records

This chapter uses common real-world patterns inspired by practical cleaning guides (e.g. one-liner style recipes), but framed with correctness and maintainability.

## A repeatable cleaning workflow

1. **Profile**: what’s missing, what’s invalid, what’s inconsistent?
2. **Define rules**: what is allowed? what gets dropped? what gets imputed?
3. **Apply transforms** (vectorized)
4. **Validate** with assertions / summary checks

## Missing values

### Count + rate

```python
missing = (
    orders.isna().sum().to_frame("missing_count")
    .join(orders.isna().mean().to_frame("missing_rate"))
    .sort_values("missing_rate", ascending=False)
)
missing
```

### Drop vs fill

Be explicit about why a column can’t be missing.

```python
orders = orders.dropna(subset=["customer"])  # required
```

Common fill strategies:

```python
orders["price"] = orders["price"].fillna(0)
orders["price"] = orders["price"].fillna(orders["price"].median())
```

## Standardize text (case + whitespace)

```python
orders["shipping_status"] = (
    orders["shipping_status"].astype("string").str.strip().str.lower()
)
```

### Normalize categories with mapping

```python
status_map = {
    "in transit": "in_transit",
    "in-transit": "in_transit",
    "shipped": "shipped",
    "delivered": "delivered",
    "pending": "pending",
}
orders["shipping_status"] = orders["shipping_status"].replace(status_map)
```

## Fix types safely

### Numeric coercion

```python
import pandas as pd

orders["price"] = pd.to_numeric(orders["price"], errors="coerce")
orders["quantity"] = pd.to_numeric(orders["quantity"], errors="coerce").astype("Int64")
```

### Datetime coercion

```python
import pandas as pd

orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")
```

## Duplicates

### Identify

```python
orders.duplicated().sum()
orders.duplicated(subset=["order_id"]).sum()
```

### Drop

```python
orders = orders.drop_duplicates(subset=["order_id"], keep="first")
```

## Outliers

Outliers are domain-specific; you can cap values if appropriate.

```python
q1 = orders["quantity"].quantile(0.25)
q3 = orders["quantity"].quantile(0.75)
iqr = q3 - q1
upper = q3 + 1.5 * iqr
orders["quantity_capped"] = orders["quantity"].clip(upper=upper)
```

## Data quality flags (don’t silently drop)

Flags help you measure quality instead of guessing.

```python
orders = orders.assign(
    is_valid_price=orders["price"].ge(0) & orders["price"].notna(),
    is_valid_qty=orders["quantity"].ge(0) & orders["quantity"].notna(),
)

orders[["is_valid_price", "is_valid_qty"]].mean()
```

Then decide what to do:

```python
orders = orders.loc[orders["is_valid_price"] & orders["is_valid_qty"]].copy()
```

## The most common pandas pitfall: chained assignment

Bad:

```python
# orders[orders["price"].gt(100)]["segment"] = "premium"  # avoid
```

Good:

```python
orders.loc[orders["price"].gt(100), "segment"] = "premium"
```

## Summary

- Use `.str.strip().str.lower()` to standardize text.
- Use `pd.to_numeric(..., errors="coerce")` and `pd.to_datetime(..., errors="coerce")` to handle messy sources.
- Prefer flags + explicit filters over silent dropping.
- Avoid chained indexing.

## Next

Continue to [08 — GroupBy + aggregations](08_groupby_agg.md).

[← Back to course home](../README.md)
