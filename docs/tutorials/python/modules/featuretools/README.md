# Featuretools Tutorial

**Level**: Beginner to Advanced
**Category**: Automated Feature Engineering

Featuretools is a framework to perform automated feature engineering. It excels at transforming relational datasets (multiple related tables) into a single feature matrix for machine learning.

## 📦 Installation

```bash
pip install featuretools
```

## 🚀 Beginner: Deep Feature Synthesis (DFS)

The core usage involves creating an `EntitySet` and running `dfs`.

```python
import featuretools as ft
import pandas as pd

# Load sample mock data provided by the library
data = ft.demo.load_mock_customer()
customers_df = data["customers"]
sessions_df = data["sessions"]
transactions_df = data["transactions"]

# 1. Create an EntitySet
es = ft.EntitySet(id="customer_data")

# 2. Add dataframes (Entities)
es = es.add_dataframe(dataframe_name="customers", dataframe=customers_df, index="customer_id")
es = es.add_dataframe(dataframe_name="sessions", dataframe=sessions_df, index="session_id")
es = es.add_dataframe(dataframe_name="transactions", dataframe=transactions_df, index="transaction_id", time_index="transaction_time")

# 3. Add relationships (Parent -> Child)
es = es.add_relationship("customers", "customer_id", "sessions", "customer_id")
es = es.add_relationship("sessions", "session_id", "transactions", "session_id")

# 4. Run Deep Feature Synthesis (DFS)
# Target entity: 'customers' (we want one row per customer with many features)
feature_matrix, feature_defs = ft.dfs(entityset=es, target_dataframe_name="customers")

print(feature_matrix.head())
```

**Result**: You get columns like `sessions.MEAN(transactions.amount)` (average transaction amount across all sessions for a customer) automatically!

## 🏃 Intermediate: Customizing Primitives

You can control *how* features are built using "Primitives" (Aggregations and Transformations).

```python
# Only use specific aggregation functions
feature_matrix, feature_defs = ft.dfs(
    entityset=es,
    target_dataframe_name="customers",
    agg_primitives=["mean", "sum", "mode"],
    trans_primitives=["year", "month"]
)

# Check one of the generated features
print([f.get_name() for f in feature_defs[-5:]])
```

## 🧠 Advanced: Time-Aware Feature Engineering

Avoid "data leakage" by using cutoff times. This ensures you only calculate features using data available *before* a specific label date.

```python
# Define cutoff times: for each customer, when do we want to make a prediction?
cutoff_times = pd.DataFrame({
    'customer_id': [1, 2, 3],
    'time': pd.to_datetime(['2014-01-01', '2014-01-01', '2014-01-01']),
    'label': [True, False, True] # The target variable we want to predict
})

feature_matrix, feature_defs = ft.dfs(
    entityset=es,
    target_dataframe_name="customers",
    cutoff_time=cutoff_times,
    cutoff_time_in_index=True
)

# Now features for customer 1 are strictly calculated using data before 2014-01-01.
```

## 💡 Use Cases

1.  **Churn Prediction**: Automatically generate "recency, frequency, monetary" (RFM) features from raw transaction logs.
2.  **Relational Databases**: Flatten a complex SQL schema into a single table for Scikit-Learn.
3.  **Kaggle Competitions**: Rapidly generate baseline features to test model viability.
