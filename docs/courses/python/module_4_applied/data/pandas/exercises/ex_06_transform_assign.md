# Exercises — 06_transform_assign: Transformations

## Goal
Create new columns using vectorization, `assign`, and `pipe`.

## Exercises

1. Generate `orders = make_orders(n=200, seed=42)`.

2. Use `assign` to add:
   - `is_big` where `revenue >= 500`
   - `segment` using `np.where`

3. Add `tier` using `np.select` with tiers:
   - `vip` for revenue >= 1000
   - `high` for 500–999.99
   - `standard` otherwise

4. Write two small functions and chain them with `.pipe`:
   - `normalize_status(d)` to normalize `shipping_status`
   - `add_revenue(d)` to (re)compute `revenue`

## Deliverable
Paste code + `value_counts()` for `segment` and `tier`.

[← Back to course home](../README.md)
