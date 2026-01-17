# PyOD Tutorial

**Level**: Beginner to Advanced
**Category**: Anomaly Detection

PyOD (Python Outlier Detection) is a comprehensive toolkit for detecting outlying objects in data. It unifies over 30+ algorithms under a single API similar to Sklearn.

## 📦 Installation

```bash
pip install pyod
```

## 🚀 Beginner: KNN Outlier Detection

A simple distance-based method: points far from their neighbors are outliers.

```python
from pyod.models.knn import KNN
from pyod.utils.data import generate_data
import matplotlib.pyplot as plt

# Generate toy data with 10% outliers
X_train, X_test, y_train, y_test = generate_data(n_train=200, n_test=100, contamination=0.1)

# Initialize and fit the model
clf = KNN()
clf.fit(X_train)

# Get the prediction labels (0: Inliers, 1: Outliers) and outlier scores
y_train_pred = clf.labels_
y_train_scores = clf.decision_scores_

# Get predictions on test data
y_test_pred = clf.predict(X_test)
y_test_scores = clf.decision_function(X_test)

print(f"Num outliers in test: {sum(y_test_pred)}")
```

## 🏃 Intermediate: Model Evaluation & Visualization

Evaluate performance using ROC and Precision@N.

```python
from pyod.utils.example import visualize
from sklearn.metrics import roc_auc_score

# Evaluate
print("ROC AUC score:", roc_auc_score(y_test, y_test_scores))

# Visualize decision boundary (only works for 2D data)
visualize(clf, X_train, y_train, X_test, y_test, y_train_pred, y_test_pred, show_figure=True, save_figure=False)
```

## 🧠 Advanced: SUOD and Ensembling

For large datasets, use SUOD (Scalable Unsupervised Outlier Detection) or combine multiple models (Ensembling) for robustness.

```python
from pyod.models.suod import SUOD
from pyod.models.lof import LOF
from pyod.models.iforest import IForest
from pyod.models.copod import COPOD

# Initialize a group of detectors
detectors_list = [LOF(n_neighbors=15), IForest(n_estimators=100), COPOD()]

# SUOD accelerates training and prediction by projecting data to lower dimensions
# and training models in parallel.
clf = SUOD(base_estimators=detectors_list, n_jobs=2, combination='average', verbose=True)

clf.fit(X_train)
y_test_pred = clf.predict(X_test)
```

## 💡 Use Cases

1.  **Fraud Detection**: Identify credit card transactions that deviate from normal spending patterns.
2.  **Network Security**: Detect intrusion attempts by analyzing packet logs for anomalies.
3.  **Preventive Maintenance**: Spot sensor readings that indicate impending machinery failure.
