# 09 — Combine tables (`merge`, `join`, `concat`)

Combining datasets is where correctness issues hide. This chapter focuses on **join semantics**, **key uniqueness**, and **validation**.

## `concat` (stack rows or columns)

### Stack rows (same schema)

```python
import pandas as pd

combined = pd.concat([df1, df2], ignore_index=True)
```

### Stack columns (same index)

```python
wide = pd.concat([left, right], axis=1)
```

## `merge` (SQL-style joins)

### Basic join

```python
customers = orders[["customer"]].drop_duplicates().assign(country="US")
merged = orders.merge(customers, on="customer", how="left")
```

### Use `validate=` to catch silent duplication bugs

If each customer should appear once in `customers`, declare it:

```python
merged = orders.merge(customers, on="customer", how="left", validate="m:1")
```

Common validate values:

- `"1:1"`: unique keys on both sides
- `"1:m"`: left unique, right can repeat
- `"m:1"`: right unique, left can repeat
- `"m:m"`: many-to-many (allowed but dangerous)

### Join on different column names

```python
dims = pd.DataFrame({"customer_name": ["Alice Smith"], "segment": ["gold"]})
merged = orders.merge(dims, left_on="customer", right_on="customer_name", how="left")
```

## `join` (index-based)

`join` is convenient when the right-hand side is indexed by the join key.

```python
customers_ix = customers.set_index("customer")
merged = orders.join(customers_ix, on="customer", how="left")
```

## Pitfalls + best practices

### 1) Missing keys

```python
orders["customer"].isna().mean()
```

Decide whether to drop or fill before joining.

### 2) Dtype mismatch

If one side has `int` keys and the other has `string` keys, you may get no matches.

### 3) Many-to-many explosion

If both sides contain duplicates on the join key, the result can multiply rows.
Use `validate=` and check row counts:

```python
before = len(orders)
after = len(merged)
print(before, after)
```

## Summary

- `concat` stacks; `merge` joins on columns; `join` joins on indices.
- Use `validate=` on merges whenever you can.
- Always sanity-check row counts after joins.

## Next

Continue to [10 — Reshaping](10_reshape.md).

[← Back to course home](../README.md)
