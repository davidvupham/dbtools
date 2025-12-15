# 11 — Datetime + time series (parse, resample, rolling, features)

Time series work in pandas is powerful when you have:

- a real datetime column
- a sorted DateTimeIndex
- clear frequency assumptions

## Parsing datetimes

```python
import pandas as pd

orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")
```

If you care about time zones:

```python
orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce", utc=True)
```

## DateTimeIndex basics

```python
ts = orders.set_index("order_date").sort_index()
```

## Resampling

Resampling aggregates time windows.

```python
monthly_rev = ts["revenue"].resample("MS").sum()  # month-start
weekly_rev = ts["revenue"].resample("W").sum()    # weekly
```

## Rolling windows

Rolling windows compute statistics over a moving window.

```python
ts["rev_ma_7d"] = ts["revenue"].rolling("7D").mean()      # time-based window
ts["rev_ma_7"] = ts["revenue"].rolling(7, min_periods=1).mean()  # row-based window
```

## Expanding windows

```python
ts["rev_cum"] = ts["revenue"].expanding().sum()
```

## Lag features (shift)

```python
ts["rev_lag_1"] = ts["revenue"].shift(1)
ts["rev_lag_7"] = ts["revenue"].shift(7)
```

## Extract datetime components

Useful for grouping and seasonality:

```python
idx = ts.index

ts = ts.assign(
    dow=idx.dayofweek,
    month=idx.month,
    day=idx.day,
    week=idx.isocalendar().week.astype("int64"),
)
```

## Time between events

For irregular series, time deltas can be informative:

```python
ts["days_since_prev"] = ts.index.to_series().diff().dt.days
```

## Cyclical encoding (advanced ML feature engineering)

If you use day-of-week/month as numeric features in ML models, consider sine/cosine encoding:

```python
import numpy as np

ts["dow_sin"] = np.sin(2 * np.pi * ts["dow"] / 7)
ts["dow_cos"] = np.cos(2 * np.pi * ts["dow"] / 7)
```

## Summary

- Parse datetimes explicitly.
- Set a DateTimeIndex and sort it.
- Use `resample` for aggregates and `rolling/expanding/shift` for time-based features.

## Next

Continue to [12 — Performance + memory + CoW](12_performance_memory.md).

[← Back to course home](../README.md)
