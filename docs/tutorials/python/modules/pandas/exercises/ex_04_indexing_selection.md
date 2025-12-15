# Exercises — 04_indexing_selection: Indexing + selection

## Goal
Practice correct selection and safe assignment.

## Exercises

1. Generate `orders = make_orders(n=200, seed=42)`.

2. `loc` vs `iloc`
   - Show the first row with `iloc`.
   - Show the first 5 rows with `iloc` slicing.

3. Meaningful index
   - Create `by_id = orders.set_index('order_id')`.
   - Select `order_id == 10` and return `customer` + `revenue`.

4. MultiIndex
   - Create `mi = orders.set_index(['customer','category']).sort_index()`.
   - Select all rows for one customer.
   - Select one `(customer, category)` pair.

5. Safe assignment
   - Create a boolean mask (e.g., revenue >= 500) and set `segment='high'` using `.loc`.

## Deliverable
Paste code + a small output sample. Explain (1 sentence) why chained indexing is risky.

[← Back to course home](../README.md)
