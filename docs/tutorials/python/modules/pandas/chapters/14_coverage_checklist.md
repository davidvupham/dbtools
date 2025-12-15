# 14 — Coverage checklist (skills map)

This chapter is a checklist you can use to self-assess pandas competency from beginner → advanced.

It’s inspired by common “what you should know” lists, but the source of truth for behavior is always the official pandas documentation.

## Beginner

- [ ] Install pandas and import with `import pandas as pd`
- [ ] Create a DataFrame from dict/list
- [ ] Inspect: `head`, `tail`, `shape`, `dtypes`, `info`, `describe`
- [ ] Select: columns, rows with `loc/iloc`
- [ ] Filter with boolean masks, `isin`, `between`
- [ ] Handle missing values: `isna`, `fillna`, `dropna`
- [ ] Basic aggregation: `groupby(...).sum()`
- [ ] Save to CSV / read from CSV

## Intermediate

- [ ] Type coercion: `pd.to_numeric`, `pd.to_datetime` + `errors="coerce"`
- [ ] String ops with `.str` (strip/lower/replace/contains)
- [ ] Named aggregations in groupby
- [ ] `transform` vs `agg` (same-size features)
- [ ] Reshaping: `pivot_table`, `melt`
- [ ] Joins: `merge`, `join`, `concat`
- [ ] Join validation: `validate="m:1"` etc.
- [ ] Time series: set DateTimeIndex, `resample`, `rolling`, `shift`

## Advanced

- [ ] MultiIndex: set/slice/sort; stack/unstack
- [ ] Window patterns: rolling + expanding + ewm
- [ ] Performance: categorical dtype, downcasting, chunking large CSV
- [ ] Avoid chained assignment; understand Copy-on-Write direction
- [ ] Build readable pipelines with `assign` + `pipe`
- [ ] Know when to use alternatives (DuckDB/Polars) for scale

## Where this content came from

- Video baseline: `https://youtu.be/EXIgjIBu4EU?si=UwcisJQy1bgW6cRC`
- Structured intro flow: `https://realpython.com/courses/introduction-pandas/?utm_source=notification_summary&utm_medium=email&utm_campaign=2025-12-02`
- Practical tasks: `https://www.howtogeek.com/my-favorite-pandas-data-manipulation-tasks-and-also-avocados/`
- Cleaning patterns: `https://www.kdnuggets.com/10-pandas-one-liners-for-data-cleaning`
- Time-series patterns: `https://machinelearningmastery.com/7-pandas-tricks-for-time-series-feature-engineering/`
- Interview-style skill coverage: `https://www.projectpro.io/article/pandas-interview-questions-and-answers/985`

[← Back to course home](../README.md)
