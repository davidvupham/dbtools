# Exercises — 07_cleaning_quality: Cleaning + data quality

## Goal
Simulate messy data, then clean it with explicit rules and validation flags.

## Exercises

1. Generate `orders = make_orders(n=200, seed=42)`.

2. Create a messy copy `dirty` and inject problems:
   - Add extra whitespace and weird casing to some `shipping_status` values.
   - Make one `price` negative.
   - Set one `customer` to missing.

3. Build a cleaning pipeline that:
   - Drops missing `customer`.
   - Normalizes `shipping_status` (strip + lower + map `in transit` → `in_transit`).
   - Coerces `price` and `quantity` to numeric.
   - Adds validation flags: `is_valid_price`, `is_valid_qty`.

4. Filter down to valid records and report:
   - counts: `(len(dirty), len(clean), len(clean2))`
   - flag rates: `mean()` of the validation columns

## Deliverable
Paste code + the before/after counts.

[← Back to course home](../README.md)
