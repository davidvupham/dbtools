# Pandas Course (Beginner → Intermediate → Advanced, Pandas 2.x)

This is a progressive pandas course: **read the chapters in order**, run the **companion notebooks**, then do the **exercises** (solutions included).

| | |
|---|---|
| **Package** | `pandas` |
| **Install** | `python -m pip install pandas` |
| **Official docs** | [pandas.pydata.org](https://pandas.pydata.org/docs/) |

### How to use this course

- **Read**: `chapters/*.md`
- **Run**: `notebooks/*.ipynb` (same examples, runnable top-to-bottom)
- **Practice**: `exercises/*` then check `solutions/*`

### Running the notebooks

Common options:

- **JupyterLab**: `python -m pip install jupyterlab` then `jupyter lab`
- **VS Code**: install the Python + Jupyter extensions and open the notebook

### Sources we intentionally incorporated (for topic coverage + example themes)

We used these to ensure the course covers common real-world pandas workflows, while validating APIs and recommendations against official pandas docs:

- Video baseline: [Learn Pandas in 30 Minutes - Python Pandas Tutorial](https://youtu.be/EXIgjIBu4EU?si=UwcisJQy1bgW6cRC) (+ companion repo: `https://github.com/techwithtim/PanadasTutorial`)
- Real Python (structured beginner flow): `https://realpython.com/courses/introduction-pandas/?utm_source=notification_summary&utm_medium=email&utm_campaign=2025-12-02`
- Task-oriented manipulation examples (avocados): `https://www.howtogeek.com/my-favorite-pandas-data-manipulation-tasks-and-also-avocados/`
- Cleaning one-liners (used carefully; not all are “one-size-fits-all”): `https://www.kdnuggets.com/10-pandas-one-liners-for-data-cleaning`
- Time-series feature engineering patterns: `https://machinelearningmastery.com/7-pandas-tricks-for-time-series-feature-engineering/`
- Coverage checklist inspiration (what people are expected to know): `https://www.projectpro.io/article/pandas-interview-questions-and-answers/985`

---

## Course map (chapters, notebooks, exercises)

| Chapter | Notebook | Exercises | Solutions |
|---|---|---|---|
| 00. Setup + mental model | [`notebooks/00_setup.ipynb`](notebooks/00_setup.ipynb) | [`exercises/ex_00_setup.md`](exercises/ex_00_setup.md) | [`solutions/sol_00_setup.md`](solutions/sol_00_setup.md) |
| 01. Series + DataFrame fundamentals | [`notebooks/01_series_dataframe.ipynb`](notebooks/01_series_dataframe.ipynb) | [`exercises/ex_01_series_dataframe.md`](exercises/ex_01_series_dataframe.md) | [`solutions/sol_01_series_dataframe.md`](solutions/sol_01_series_dataframe.md) |
| 02. I/O (CSV/Excel/Parquet/JSON/SQL) + dtypes | [`notebooks/02_io.ipynb`](notebooks/02_io.ipynb) | [`exercises/ex_02_io.md`](exercises/ex_02_io.md) | [`solutions/sol_02_io.md`](solutions/sol_02_io.md) |
| 03. Explore + inspect (EDA essentials) | [`notebooks/03_explore_inspect.ipynb`](notebooks/03_explore_inspect.ipynb) | [`exercises/ex_03_explore_inspect.md`](exercises/ex_03_explore_inspect.md) | [`solutions/sol_03_explore_inspect.md`](solutions/sol_03_explore_inspect.md) |
| 04. Indexing + selection (`loc/iloc/at/iat`, MultiIndex) | [`notebooks/04_indexing_selection.ipynb`](notebooks/04_indexing_selection.ipynb) | [`exercises/ex_04_indexing_selection.md`](exercises/ex_04_indexing_selection.md) | [`solutions/sol_04_indexing_selection.md`](solutions/sol_04_indexing_selection.md) |
| 05. Filtering + `query()` | [`notebooks/05_filtering_query.ipynb`](notebooks/05_filtering_query.ipynb) | [`exercises/ex_05_filtering_query.md`](exercises/ex_05_filtering_query.md) | [`solutions/sol_05_filtering_query.md`](solutions/sol_05_filtering_query.md) |
| 06. Transformations (`assign`, vectorization, `pipe`) | [`notebooks/06_transform_assign.ipynb`](notebooks/06_transform_assign.ipynb) | [`exercises/ex_06_transform_assign.md`](exercises/ex_06_transform_assign.md) | [`solutions/sol_06_transform_assign.md`](solutions/sol_06_transform_assign.md) |
| 07. Cleaning + data quality | [`notebooks/07_cleaning_quality.ipynb`](notebooks/07_cleaning_quality.ipynb) | [`exercises/ex_07_cleaning_quality.md`](exercises/ex_07_cleaning_quality.md) | [`solutions/sol_07_cleaning_quality.md`](solutions/sol_07_cleaning_quality.md) |
| 08. `groupby` + aggregations | [`notebooks/08_groupby_agg.ipynb`](notebooks/08_groupby_agg.ipynb) | [`exercises/ex_08_groupby_agg.md`](exercises/ex_08_groupby_agg.md) | [`solutions/sol_08_groupby_agg.md`](solutions/sol_08_groupby_agg.md) |
| 09. `merge/join/concat` | [`notebooks/09_merge_join_concat.ipynb`](notebooks/09_merge_join_concat.ipynb) | [`exercises/ex_09_merge_join_concat.md`](exercises/ex_09_merge_join_concat.md) | [`solutions/sol_09_merge_join_concat.md`](solutions/sol_09_merge_join_concat.md) |
| 10. Reshaping (`pivot`, `melt`, `stack/unstack`) | [`notebooks/10_reshape.ipynb`](notebooks/10_reshape.ipynb) | [`exercises/ex_10_reshape.md`](exercises/ex_10_reshape.md) | [`solutions/sol_10_reshape.md`](solutions/sol_10_reshape.md) |
| 11. Datetime + time series (resample/rolling/features) | [`notebooks/11_datetime_timeseries.ipynb`](notebooks/11_datetime_timeseries.ipynb) | [`exercises/ex_11_datetime_timeseries.md`](exercises/ex_11_datetime_timeseries.md) | [`solutions/sol_11_datetime_timeseries.md`](solutions/sol_11_datetime_timeseries.md) |
| 12. Performance + memory + Copy-on-Write | [`notebooks/12_performance_memory.ipynb`](notebooks/12_performance_memory.ipynb) | [`exercises/ex_12_performance_memory.md`](exercises/ex_12_performance_memory.md) | [`solutions/sol_12_performance_memory.md`](solutions/sol_12_performance_memory.md) |
| 13. Case studies (task-first workflows) | [`notebooks/13_case_studies.ipynb`](notebooks/13_case_studies.ipynb) | [`exercises/ex_13_case_studies.md`](exercises/ex_13_case_studies.md) | [`solutions/sol_13_case_studies.md`](solutions/sol_13_case_studies.md) |

### Capstone

- Capstone notebook: [`notebooks/99_capstone.ipynb`](notebooks/99_capstone.ipynb)

---

## Chapters (reading order)

1. [`chapters/00_setup.md`](chapters/00_setup.md)
2. [`chapters/01_series_dataframe.md`](chapters/01_series_dataframe.md)
3. [`chapters/02_io.md`](chapters/02_io.md)
4. [`chapters/03_explore_inspect.md`](chapters/03_explore_inspect.md)
5. [`chapters/04_indexing_selection.md`](chapters/04_indexing_selection.md)
6. [`chapters/05_filtering_query.md`](chapters/05_filtering_query.md)
7. [`chapters/06_transform_assign.md`](chapters/06_transform_assign.md)
8. [`chapters/07_cleaning_quality.md`](chapters/07_cleaning_quality.md)
9. [`chapters/08_groupby_agg.md`](chapters/08_groupby_agg.md)
10. [`chapters/09_merge_join_concat.md`](chapters/09_merge_join_concat.md)
11. [`chapters/10_reshape.md`](chapters/10_reshape.md)
12. [`chapters/11_datetime_timeseries.md`](chapters/11_datetime_timeseries.md)
13. [`chapters/12_performance_memory.md`](chapters/12_performance_memory.md)
14. [`chapters/13_case_studies.md`](chapters/13_case_studies.md)
15. [`chapters/14_coverage_checklist.md`](chapters/14_coverage_checklist.md)

---

[← Back to Modules Index](../README.md)
