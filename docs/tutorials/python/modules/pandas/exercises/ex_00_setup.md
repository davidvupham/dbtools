# Exercises — 00_setup: Setup + mental model

## Goal
Get your environment ready and produce a reproducible starter dataset you’ll reuse in later chapters.

## Exercises

1. **Environment sanity check**
   - Import pandas as `pd`.
   - Print `pd.__version__`.

2. **Display options (quality of life)**
   - Set:
     - `display.max_columns` to 50
     - `display.width` to 120
     - `display.max_rows` to 30

3. **Create a tiny DataFrame by hand**
   - Create a DataFrame with columns `name`, `age`, `city` and at least 3 rows.
   - Show `head()` and `dtypes`.

4. **Course dataset**
   - Implement `make_orders(n=200, seed=42)` (or copy it from chapter 00).
   - Generate `orders = make_orders()`.
   - Show `orders.head()`, `orders.shape`, and `orders.dtypes`.

## Deliverable
Paste your code and the outputs (tables + `dtypes`).

[← Back to course home](../README.md)
