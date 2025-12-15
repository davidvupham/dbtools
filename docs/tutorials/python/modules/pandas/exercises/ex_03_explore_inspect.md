# Exercises — 03_explore_inspect: Explore + inspect

## Goal
Build a repeatable “first 60 seconds” inspection routine.

## Exercises

1. Generate `orders = make_orders(n=200, seed=42)`.

2. Run the inspection checklist:
   - `shape`, `columns`, `dtypes`, `head()`, `sample(5, random_state=0)`, `info()`

3. Categorical checks:
   - `value_counts(dropna=False)` for `category` and `shipping_status`

4. Missingness report:
   - Build a table with `missing_count` and `missing_rate` per column, sorted by missing rate.

5. Quality gates:
   - Add at least two `assert` checks (e.g., `order_id` uniqueness, non-negative `quantity`).

## Deliverable
Paste your code and the missingness table.

[← Back to course home](../README.md)
