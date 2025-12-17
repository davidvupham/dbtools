# Exercises — 12_performance_memory: Performance + memory + CoW

## Goal
Reduce memory usage and practice safe assignment.

## Exercises

1. Generate `orders = make_orders(n=2000, seed=42)`.

2. Measure baseline memory
   - `orders.memory_usage(deep=True).sum()`

3. Optimize dtypes
   - Convert repeated string columns to `category`.
   - Downcast `quantity` and `price`.

4. Compare memory
   - Show the baseline vs optimized memory totals.

5. Safe assignment
   - Create a mask (e.g., `revenue >= 500`) and assign `segment` using `.loc`.

6. (Optional) Copy-on-Write
   - If you want, set `pd.options.mode.copy_on_write = True` and confirm your code still works.

## Deliverable
Paste code + a small output showing memory totals and the `segment` column.

[← Back to course home](../README.md)
