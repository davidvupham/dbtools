# 13 — Case studies (task-first workflows)

These mini-projects are designed to feel like real work. Each case study emphasizes:

- exploration
- cleaning
- analysis
- a “deliverable” table/summary

## Case study A — Avocado-style analysis (category focus)

Goal: “Which categories drive revenue, and how does it change over time?”

### 1) Prepare

```python
import pandas as pd

# assume you have `orders` from chapter 00
orders = orders.copy()
orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")
orders = orders.dropna(subset=["order_date"])
```

### 2) Revenue by category

```python
rev_by_cat = (
    orders.groupby("category").agg(
        revenue_total=("revenue", "sum"),
        orders=("order_id", "nunique"),
        items=("quantity", "sum"),
    )
    .sort_values("revenue_total", ascending=False)
)
rev_by_cat
```

### 3) Monthly revenue pivot

```python
ts = orders.set_index("order_date").sort_index()
monthly = (
    ts.groupby("category")["revenue"]
    .resample("MS")
    .sum()
    .reset_index()
)

pivot = monthly.pivot_table(
    index="order_date",
    columns="category",
    values="revenue",
    aggfunc="sum",
    fill_value=0,
)

pivot.tail()
```

## Case study B — Data cleaning checklist (one-liner ideas, but production framing)

Goal: standardize status strings, fix types, and create validation flags.

```python
import pandas as pd

clean = (
    orders
    .assign(
        shipping_status=lambda d: d["shipping_status"].astype("string").str.strip().str.lower(),
        price=lambda d: pd.to_numeric(d["price"], errors="coerce"),
        quantity=lambda d: pd.to_numeric(d["quantity"], errors="coerce"),
    )
    .assign(
        is_valid_price=lambda d: d["price"].ge(0) & d["price"].notna(),
        is_valid_qty=lambda d: d["quantity"].ge(0) & d["quantity"].notna(),
    )
)

quality = clean[["is_valid_price", "is_valid_qty"]].mean()
quality
```

Decide what to do with invalid records:

```python
clean2 = clean.loc[clean["is_valid_price"] & clean["is_valid_qty"]].copy()
```

## Case study C — Top customers report

Goal: produce a table of top customers by revenue.

```python
top_customers = (
    orders.groupby("customer").agg(
        revenue_total=("revenue", "sum"),
        orders=("order_id", "nunique"),
        avg_order=("revenue", "mean"),
    )
    .sort_values("revenue_total", ascending=False)
    .head(10)
)

top_customers
```

## Summary

- Case studies are where you practice chaining multiple skills together.
- When in doubt: explore → clean → validate → aggregate → reshape.

[← Back to course home](../README.md)
