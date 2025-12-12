# Lux Tutorial

**Level**: Beginner to Advanced
**Category**: Automated Visualization

Lux is a Python library that facilitates fast and easy data exploration by automating the visualization and data analysis process. It preserves the pandas dataframe but adds a "toggle" to view visual recommendations.

## 📦 Installation

```bash
pip install lux-api
```

*Note: If using Jupyter Lab, you may need to install the widget extension.*

## 🚀 Beginner: Automatic Recommendations

Simply import lux and view your dataframe. Lux automatically creates charts.

```python
import lux
import pandas as pd

# Load dataset
df = pd.read_csv("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv")

# Just printing the dataframe triggers the Lux widget in Jupyter
df
```

*In a Jupyter notebook, you will see a "Toggle Pandas/Lux" button. Click it to see Correlation, Distribution, and Occurrence charts automatically generated.*

## 🏃 Intermediate: Intent-Based Analysis

You can guide Lux's recommendations by specifying your "intent"—the attributes you are interested in.

```python
# I am interested in 'sepal_length' and 'species'
df.intent = ["sepal_length", "species"]

# Lux will now show visualizations relevant to these columns
df
```

Lux will prioritize charts that involve these columns, such as scatter plots of sepal_length broken down by species.

## 🧠 Advanced: Exporting to Code

Found a chart you like? You don't have to start from scratch to customize it. Export it to matplotlib or altair code.

```python
# Assume you selected a visualization in the widget and it's the first one in the list
vis = df.recommendation["Correlation"][0]

# Get the code to generate this chart
print(vis.to_code("matplotlib"))
# or
print(vis.to_code("altair"))
```

## 💡 Use Cases

1.  **Rapid Prototyping**: Quickly see distributions without writing `plt.hist()` for every column.
2.  **Data Quality Checks**: Spot skewed distributions or unexpected correlations instantly.
3.  **Guided Exploration**: Use the intent feature to drill down into specific hypotheses.
