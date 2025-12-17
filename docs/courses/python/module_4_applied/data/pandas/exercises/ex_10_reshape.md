# Exercises — 10_reshape: Reshaping

## Goal
Move between long and wide formats and verify totals remain consistent.

## Exercises

1. Generate `orders = make_orders(n=500, seed=42)`.

2. Create a pivot table
   - `index='customer'`, `columns='category'`, `values='revenue'`, `aggfunc='sum'`, `fill_value=0`.

3. Melt back to long
   - Convert the pivot result back to long with `melt`.

4. Verify totals
   - Confirm total revenue in the pivot equals total revenue in the original data (within floating tolerance).

5. Stack/unstack
   - `stack()` the pivot to a Series, then `unstack()` it back.

## Deliverable
Paste code + the total revenue comparison.

[← Back to course home](../README.md)
