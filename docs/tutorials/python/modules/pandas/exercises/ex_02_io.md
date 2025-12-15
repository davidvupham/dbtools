# Exercises — 02_io: I/O + dtypes

## Goal
Practice reading/writing with correct dtypes and safe parsing.

## Exercises

1. **Read CSV from an in-memory string**
   - Use `io.StringIO` to create a CSV string with columns:
     - `order_id` (integers)
     - `order_date` (YYYY-MM-DD)
     - `customer` (strings)
     - `price` (some numeric strings, include one bad value like `oops`)
   - Read it with `pd.read_csv`.

2. **Fix types explicitly**
   - Convert `order_date` with `pd.to_datetime(..., errors='coerce')`.
   - Convert `price` with `pd.to_numeric(..., errors='coerce')`.
   - Show `dtypes` and highlight where `NaN` appears.

3. **Schema enforcement**
   - Read the CSV again, but this time pass `dtype={...}` for columns you can enforce directly.

4. **Write**
   - Write to CSV (string/buffer is fine) with `index=False`.

## Deliverable
Paste your code and outputs.

[← Back to course home](../README.md)
