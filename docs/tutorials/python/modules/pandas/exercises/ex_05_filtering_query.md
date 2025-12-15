# Exercises — 05_filtering_query: Filtering + query

## Goal
Write readable filters and verify they match.

## Exercises

1. Generate `orders = make_orders(n=200, seed=42)`.

2. Boolean mask filter
   - Filter for a specific customer and `revenue >= 500`.

3. Membership + range
   - Filter where `category` is in `['avocados','bananas']`.
   - Filter where `revenue` is between 100 and 500 (inclusive).

4. `query` equivalence
   - Write a `query()` that selects `revenue >= 500` and category in `['laptops','phones']`.
   - Confirm the result matches your boolean-mask version (same row count).

5. String contains
   - Filter where `customer` contains `ali` case-insensitively.

## Deliverable
Paste code + counts of rows returned for each filter.

[← Back to course home](../README.md)
