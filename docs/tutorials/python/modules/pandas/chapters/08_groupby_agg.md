# 08 — GroupBy + aggregations

GroupBy is how you answer questions like:

- “Revenue by category?”
- “Average order size per customer?”
- “Top customers per month?”

## The pattern

1. Choose **keys** (what you group by)
2. Choose **values** (what you aggregate)
3. Choose **aggregation** (sum/mean/count/…)

## Basic aggregations

```python
orders.groupby("category")["revenue"].sum().sort_values(ascending=False)
```

Multiple aggregations:

```python
orders.groupby("category")["revenue"].agg(["sum", "mean", "count"]).sort_values("sum", ascending=False)
```

## Named aggregations (recommended)

Named aggregations produce clearer column names:

```python
out = orders.groupby("category").agg(
    revenue_total=("revenue", "sum"),
    revenue_avg=("revenue", "mean"),
    orders_count=("order_id", "nunique"),
)
```

## GroupBy with multiple keys

```python
out = orders.groupby(["customer", "category"]).agg(
    revenue_total=("revenue", "sum"),
    items=("quantity", "sum"),
)
```

## `transform` vs `agg`

- `agg` reduces rows (one row per group)
- `transform` returns the same number of rows (adds group-level context back to each row)

```python
orders["customer_avg_revenue"] = orders.groupby("customer")["revenue"].transform("mean")
```

## Ranking within groups (top-N per group)

```python
ranked = orders.assign(
    rank_in_customer=orders.groupby("customer")["revenue"].rank(method="dense", ascending=False)
)

top2_each = ranked.loc[ranked["rank_in_customer"].le(2)].sort_values(["customer", "rank_in_customer"])
```

## `groupby(..., observed=...)` with categoricals

If your group keys are categorical, consider `observed=True` to avoid showing unused categories:

```python
orders["category"] = orders["category"].astype("category")
orders.groupby("category", observed=True)["revenue"].sum()
```

## Common pitfall: `apply`

`groupby.apply` is powerful but can be slow and harder to reason about.
Prefer `agg`, `transform`, or `filter` when possible.

## Summary

- Use named aggregations for readability.
- Use `transform` to create per-row features based on group statistics.
- Use ranking to build “top-N per group” outputs.

## Next

Continue to [09 — Merge/Join/Concat](09_merge_join_concat.md).

[← Back to course home](../README.md)
