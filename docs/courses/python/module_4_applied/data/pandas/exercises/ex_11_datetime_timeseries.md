# Exercises — 11_datetime_timeseries: Datetime + time series

## Goal
Practice time-based indexing, resampling, and feature engineering.

## Exercises

1. Generate `orders = make_orders(n=500, seed=42)`.

2. Parse and index
   - Ensure `order_date` is datetime.
   - Set it as index and sort.

3. Resample
   - Compute monthly revenue totals (`'MS'`).

4. Rolling + lag
   - Add a 7-day rolling mean of revenue (`rolling('7D')`).
   - Add a 1-step lag feature (`shift(1)`).

5. Datetime components
   - Add `dow` (day of week) and `month` columns.

## Deliverable
Paste code + `monthly_rev.tail()`.

[← Back to course home](../README.md)
