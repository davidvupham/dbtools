# Sweetviz Tutorial

**Level**: Beginner to Advanced
**Category**: Exploratory Data Analysis (EDA)

Sweetviz is an open-source Python library that generates beautiful, high-density visualizations to kickstart EDA (Exploratory Data Analysis) with just two lines of code.

## 📦 Installation

```bash
pip install sweetviz
```

## 🚀 Beginner: Your First Report

The most common use case is analyzing a single dataframe to understand your data distribution.

```python
import sweetviz as sv
import pandas as pd

# Load a sample dataset
df = pd.read_csv("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv")

# Generate the report
report = sv.analyze(df)

# Show the report (saves as HTML and opens in browser)
report.show_html("titanic_report.html")
```

**What you get**: A comprehensive HTML file showing:
- Missing values
- Unique values
- Histograms/Distributions
- Correlations

## 🏃 Intermediate: Comparing Datasets

A powerful feature is comparing "training" vs "testing" data, or two different time periods (e.g., "2023 data" vs "2024 data").

```python
from sklearn.model_selection import train_test_split

# Split data to simulate train/test
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# Analyze with comparison
# syntax: analyze([dataframe, "Label"], target_feat=None)
report = sv.compare(
    [train_df, "Training Data"],
    [test_df, "Test Data"],
    target_feat="survived"  # Optional: visualize everything relative to this target
)

report.show_html("comparison_report.html")
```

## 🧠 Advanced: Customization & Config

You can customize the layout, scale, and specific features to ignore or force as categorical.

```python
# Create a custom config
feature_config = sv.FeatureConfig(
    skip="embarked",           # Skip specific columns
    force_text=["sex"]         # Force specific columns to be treated as text/categorical
)

# Analyze with target variable and custom config
report = sv.analyze(
    df,
    target_feat="survived",
    feat_cfg=feature_config
)

# Render with custom layout options
report.show_html(
    filepath="advanced_report.html",
    layout="widescreen",
    scale=0.8
)
```

## 💡 Use Cases

1.  **Initial Data Audit**: Instantly spot missing data and outliers in a new dataset.
2.  **Dataset Drift Monitoring**: Compare this month's data to last month's to see if distributions have shifted.
3.  **Target Analysis**: Quickly understand which features correlate strongly with your target variable (e.g., "survived").
