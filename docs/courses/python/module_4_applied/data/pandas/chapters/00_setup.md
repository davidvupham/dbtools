# 00 — Setup + mental model

This chapter gets your environment ready and gives you the minimum mental model you need to be productive in pandas.

## Install

```bash
python -m pip install pandas
```

Optional (recommended for notebooks):

```bash
python -m pip install jupyterlab
```

## Import conventions

Use the standard alias:

```python
import pandas as pd
```

## Check versions

```python
import pandas as pd

print(pd.__version__)
```

## Display options (quality of life)

These settings make DataFrames easier to read while learning:

```python
import pandas as pd

pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 120)
pd.set_option("display.max_rows", 30)
```

## Your first DataFrame

```python
import pandas as pd

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35],
    "city": ["NYC", "LA", "NYC"],
})

print(df)
```

## A reusable dataset for the course

To make every chapter runnable and consistent, we’ll generate a small synthetic dataset.

```python
import numpy as np
import pandas as pd


def make_orders(n: int = 200, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    customers = np.array([
        "Alice Smith",
        "Bob Jones",
        "Charlie Zhang",
        "Diana Lopez",
        "Evan Kim",
        "Fatima Ali",
    ])
    categories = np.array(["avocados", "bananas", "laptops", "phones", "tablets"])
    shipping_status = np.array(["delivered", "shipped", "in transit", "pending"])

    base = pd.Timestamp("2025-01-01")
    order_date = base + pd.to_timedelta(rng.integers(0, 180, size=n), unit="D")

    df = pd.DataFrame(
        {
            "order_id": np.arange(1, n + 1),
            "order_date": order_date,
            "customer": rng.choice(customers, size=n),
            "category": rng.choice(categories, size=n, p=[0.25, 0.15, 0.2, 0.2, 0.2]),
            "quantity": rng.integers(1, 8, size=n),
            "price": rng.choice([0.99, 1.49, 2.99, 399.0, 499.0, 999.0], size=n),
            "shipping_status": rng.choice(shipping_status, size=n, p=[0.55, 0.25, 0.15, 0.05]),
        }
    )

    df["revenue"] = df["quantity"] * df["price"]
    return df


orders = make_orders()
orders.head()
```

## The mental model (one paragraph)

- A **DataFrame** is a table: columns are variables, rows are observations.
- A **Series** is a single labeled column (or row) with an index.
- Most pandas power comes from **vectorized operations** and **label alignment**.

## Pitfalls to avoid early

- Avoid chained assignment like `df[mask]["col"] = ...`. Prefer `df.loc[mask, "col"] = ...`.
- Avoid `DataFrame.append()` (deprecated). Prefer `pd.concat([...], ignore_index=True)`.

## Next

Continue to [01 — Series + DataFrame fundamentals](01_series_dataframe.md).

[← Back to course home](../README.md)
