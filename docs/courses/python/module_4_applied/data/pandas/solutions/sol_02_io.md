# Solutions — 02_io: I/O + dtypes

## What this solution demonstrates

- Read data, then inspect dtypes.
- Parse dates and numerics explicitly with `errors="coerce"`.
- Use `dtype=` where it is safe, then coerce the rest.

## Why this pattern

CSV is untyped; explicit parsing makes your pipeline predictable and debuggable.

## Common pitfalls

- Letting pandas guess types for large files (slow, inconsistent).
- Treating parse failures as exceptions instead of tracking resulting NaNs.

## One useful variant

For large CSVs, add `usecols=` and consider chunking with `chunksize=`.

## Expected output (example)

- Initial `dtypes` show `order_date` and `price` as object/string-like.
- After parsing: `order_date` becomes datetime64 and `price` becomes float; the bad price (`oops`) becomes `NaN`.
- Exported CSV prints without an index column.

## Reference implementation

```python
import io
import pandas as pd

csv_text = (
    "order_id,order_date,customer,price\\n"
    "1,2025-01-01,Alice Smith,9.99\\n"
    "2,2025-01-02,Bob Jones,oops\\n"
    "3,2025-01-03,Charlie Zhang,10.50\\n"
)

buf = io.StringIO(csv_text)
df = pd.read_csv(buf)
print(df.dtypes)

# Explicit parsing

df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
df["price"] = pd.to_numeric(df["price"], errors="coerce")
print(df)
print(df.dtypes)

# Schema enforcement where possible

buf2 = io.StringIO(csv_text)
df2 = pd.read_csv(buf2, dtype={"order_id": "int64", "customer": "string"})
df2["order_date"] = pd.to_datetime(df2["order_date"], errors="coerce")
df2["price"] = pd.to_numeric(df2["price"], errors="coerce")

out_buf = io.StringIO()
df2.to_csv(out_buf, index=False)
print(out_buf.getvalue())
```


[← Back to course home](../README.md)
