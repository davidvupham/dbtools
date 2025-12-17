# Exercises — 09_merge_join_concat: Merge / join / concat

## Goal
Combine tables safely and detect join bugs early.

## Exercises

1. Generate `orders = make_orders(n=200, seed=42)`.

2. Create a dimension table `customers` with unique customer keys
   - One row per customer.
   - Add a `country` column.

3. Merge with validation
   - Merge `orders` with `customers` on `customer`.
   - Use `validate='m:1'`.

4. Join version
   - Convert `customers` to an index on `customer`.
   - Use `orders.join(..., on='customer')`.

5. Many-to-many pitfall demo
   - Create a broken `customers_bad` by duplicating at least one customer key.
   - Merge without `validate` and show how the row count can increase.

## Deliverable
Paste code + `(len(orders), len(merged_ok), len(merged_bad))`.

[← Back to course home](../README.md)
