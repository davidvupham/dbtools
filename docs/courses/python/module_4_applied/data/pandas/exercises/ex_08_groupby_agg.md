# Exercises — 08_groupby_agg: GroupBy + aggregations

## Goal
Use groupby to produce clear, correct summaries.

## Exercises

1. Generate `orders = make_orders(n=500, seed=42)`.

2. Category summary
   - Revenue total by category (descending).

3. Named aggregations
   - Produce a table with:
     - `revenue_total` (sum)
     - `revenue_avg` (mean)
     - `orders_count` (nunique order_id)

4. Multi-key groupby
   - Group by `(customer, category)` and compute total revenue.

5. Transform
   - Add `customer_avg_revenue` back onto each row using `transform('mean')`.

6. Top-N per customer
   - Rank orders by revenue per customer and keep top 2 per customer.

## Deliverable
Paste code + the final “top 2 per customer” output.

[← Back to course home](../README.md)
