# Dython Tutorial

**Level**: Beginner to Advanced
**Category**: Data Analysis / Correlation

Dython stands for "Data Analysis for Python". It is a set of tools particularly famous for handling **nominal (categorical) vs numerical correlations** effectively, using metrics like Cramer's V and Theil's U.

## 📦 Installation

```bash
pip install dython
```

## 🚀 Beginner: The Association Map

The standard pandas `df.corr()` omits categorical columns. Dython handles them automatically.

```python
import pandas as pd
from dython.nominal import associations

# Load a dataset with mixed types (numerical + categorical)
df = pd.read_csv("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv")

# Generate association map (correlation matrix)
# This automatically detects categorical columns and uses appropriate metrics (Cramer's V, etc.)
results = associations(df, plot=True, figsize=(10,10))
```

## 🏃 Intermediate: Understanding the Metrics

By default, `associations` uses:
- **Pearson's R** for Continuous-Continuous
- **Correlation Ratio** for Continuous-Categorical
- **Cramer's V** for Categorical-Categorical

You can change the categorical-categorical metric to **Theil's U** (which is asymmetric unlike Cramer's V).

```python
# Use Theil's U for categorical associations
# Theil's U(x,y) != Theil's U(y,x), so the heatmap will be asymmetric
results = associations(
    df,
    nom_nom_assoc='theil',
    plot=True,
    figsize=(10,10)
)
```

## 🧠 Advanced: Detailed Analysis Without Plotting

Sometimes you just want the numbers for a pipeline or report.

```python
# Compute only, do not plot
correlation_dict = associations(df, plot=False)

# Get the correlation matrix dataframe
corr_matrix = correlation_dict['corr']

# Find features highly correlated with 'tip'
high_corr = corr_matrix['tip'].sort_values(ascending=False)
print(high_corr)
```

## 💡 Use Cases

1.  **Survey Data Analysis**: Analyze correlations in datasets with many categorical answers (e.g., "Yes/No", "Region").
2.  **Feature Selection**: Accurately drop redundant categorical features that are highly correlated with each other.
3.  **Missing Value Imputation**: Identify which other columns (categorical or numerical) are most predictive of the column with missing values.
