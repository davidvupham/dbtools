# Understanding data engineering design patterns

**[← Back to Explanation Index](./README.md)**

> **Document Version:** 2.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Data Engineering Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Type](https://img.shields.io/badge/Type-Explanation-orange)

> [!NOTE]
> This document explains the 8 foundational design patterns that every modern data stack is built on. Understanding these patterns helps you design systems that scale, remain reliable, and deliver trustworthy data.

## Table of contents

- [Introduction](#introduction)
- [Why patterns matter](#why-patterns-matter)
- [Pattern 1: Ingestion](#pattern-1-ingestion)
- [Pattern 2: Storage](#pattern-2-storage)
- [Pattern 3: Transformation](#pattern-3-transformation)
- [Pattern 4: Orchestration](#pattern-4-orchestration)
- [Pattern 5: Reliability](#pattern-5-reliability)
- [Pattern 6: Quality and governance](#pattern-6-quality-and-governance)
- [Pattern 7: Serving](#pattern-7-serving)
- [Pattern 8: Performance](#pattern-8-performance)
- [Decision framework](#decision-framework)
- [Further reading](#further-reading)

## Introduction

Most data engineers start by learning tools—Spark, Airflow, Kafka, Iceberg—and then spend years trying to understand why systems fail. Tools show you how to write pipelines, but they do not explain why pipelines break when a late file arrives, a schema changes overnight, or two dashboards show different numbers.

Research shows that 60 to 73 percent of enterprise data never gets used for analytics. Huge volumes of data are collected, stored, and processed, but never become decisions, dashboards, or models. These are not failures of Spark or Kafka—they are failures of architecture.

Every production data stack, regardless of whether it is built on Spark, Flink, Snowflake, BigQuery, Iceberg, Delta, or custom pipelines, uses the same core design patterns. These patterns determine:

- How data enters the system
- How it is stored and versioned
- How it is transformed safely
- How pipelines recover from failures
- How data is served and consumed

[↑ Back to Table of Contents](#table-of-contents)

## Why patterns matter

Pattern mismatches cause most of the damage in data systems. Teams build batch systems for real-time use cases. They treat data lakes like warehouses. They push full reloads into environments that require incremental change. Each of these choices creates hidden risk that shows up later as broken dashboards, expensive backfills, or lost trust.

In 2026, data engineers who stand out are not the ones collecting tools on their resume. They are the ones who can examine a pipeline and identify where latency occurs, where data is lost, and where the system fails under load. These skills come from understanding how data moves through storage, compute, and failure states—not from memorizing APIs.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                     8 Data Engineering Design Patterns                       │
├──────────────┬──────────────┬────────────────┬──────────────────────────────┤
│  Ingestion   │   Storage    │ Transformation │       Orchestration          │
│              │              │                │                              │
│  - Batch     │  - Lake      │  - ETL         │  - DAG-based                 │
│  - Streaming │  - Warehouse │  - ELT         │  - Event-driven              │
│  - CDC       │  - Lakehouse │  - Incremental │                              │
├──────────────┼──────────────┼────────────────┼──────────────────────────────┤
│ Reliability  │   Quality &  │    Serving     │        Performance           │
│              │  Governance  │                │                              │
│  - Idempotent│  - Validation│  - Semantic    │  - Partitioning              │
│  - Retries   │  - Schema    │    Layer       │  - Caching                   │
│  - Backfills │  - Lineage   │  - APIs        │  - Tiered Storage            │
└──────────────┴──────────────┴────────────────┴──────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

## Pattern 1: Ingestion

*Ingestion patterns decide your system's tempo.*

Ingestion controls how fast the data platform can react to reality. Every pipeline makes an implicit choice about time. Some systems are designed to observe the world in snapshots. Others are designed to observe it as a continuous stream of events. Most production failures happen when those two models get mixed.

### Batch

Batch systems treat data as periodic shipments. Data arrives in large chunks on a schedule. Downstream systems only see the world at those checkpoints.

**Use batch when:**

- Business reports update hourly or daily
- Source systems can only export files or database dumps
- Cost predictability matters more than freshness

**How it fails:** Batch breaks when teams try to force it into real-time workloads. A daily job that pulls a 200 GB table never supports a dashboard that refreshes every five minutes, no matter how much Spark you throw at it. The bottleneck is not compute—it is the ingestion pattern.

**Implementation patterns:**

```sql
-- Batch load with partition overwrite (idempotent)
INSERT OVERWRITE TABLE target_table PARTITION (date_key)
SELECT * FROM staging_table
WHERE date_key = '2026-01-22';
```

### Streaming

Streaming treats every record as an event. Data flows continuously through the system, allowing downstream consumers to react in seconds instead of hours.

**Use streaming when:**

- Latency needs to be measured in seconds or minutes
- Alerts, fraud detection, or live metrics depend on freshness
- Event-driven services subscribe to data changes

**How it fails:** Streaming fails when it is used for data nobody needs in real time. Many teams run Kafka and Flink pipelines for tables that are only queried once per day. That creates operational cost, state management complexity, and failure modes with no business upside.

**Tools:** Apache Kafka, Apache Flink, Apache Pulsar, AWS Kinesis, Google Pub/Sub

### Change data capture (CDC)

Change Data Capture moves only what changed. Instead of copying whole tables, CDC streams inserts, updates, and deletes directly from database logs.

**Use CDC when:**

- Operational databases are the system of record
- Tables are large but change slowly
- Production load must stay minimal

**How it fails:** CDC breaks when teams ignore deletes, schema changes, and ordering guarantees. A CDC feed without correct primary keys, log retention, or schema evolution is worse than a batch job because it silently corrupts downstream state.

**Tools:** Debezium, AWS DMS, Fivetran, Airbyte, Striim

### Hybrid architectures

Most production systems combine multiple ingestion patterns. Two architectures dominate:

**Lambda architecture** combines batch and streaming in parallel:

```text
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Source    │────▶│  Batch Layer │────▶│             │
│   Systems   │     └─────────────┘     │   Serving   │
│             │     ┌─────────────┐     │    Layer    │
│             │────▶│ Speed Layer  │────▶│             │
└─────────────┘     └─────────────┘     └─────────────┘
```

- Batch layer provides complete, accurate historical processing
- Speed layer provides low-latency updates for recent data
- Serving layer merges both views for queries

**Kappa architecture** uses streaming for everything:

```text
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Source    │────▶│   Stream    │────▶│   Serving   │
│   Systems   │     │  Processor  │     │    Layer    │
└─────────────┘     └─────────────┘     └─────────────┘
```

- All data flows through a single streaming pipeline
- Historical reprocessing replays the stream
- Simpler architecture, but requires mature streaming infrastructure

> [!IMPORTANT]
> **The thumb rule:** Choose ingestion based on latency and change rate, not hype. If you get this decision wrong, everything built on top fights reality.

**Pattern selection guide:**

| Scenario | Recommended Pattern |
|:---------|:--------------------|
| Multi-table database replication | CDC (Debezium + Kafka) |
| API data that updates every 6 hours | Batch (scheduled polling) |
| Real-time fraud detection | Streaming |
| Data warehouse refresh | Batch or CDC |
| Event-driven microservices | Streaming |

[↑ Back to Table of Contents](#table-of-contents)

## Pattern 2: Storage

*Storage patterns shape everything downstream.*

Storage is not where data rests—it is where behavior gets locked in. The moment data is written, you have already decided how it is queried, how it is governed, how expensive it is to scan, and how painful it is to change. Teams treat storage as a neutral layer. It is not. Storage is the most opinionated part of the stack.

### Data lake

Data lakes store files, not tables. Everything is written in open file formats like Parquet or JSON into object storage. There is no built-in transaction layer and no enforced schema beyond what tools agree on.

**Use a data lake when:**

- You ingest raw, structured, and unstructured data
- Data science and machine learning need a full history
- Storage cost must be as low as possible

**How it fails:** Lakes fail when multiple pipelines write to the same folders without coordination. One job overwrites files while another reads them. Partitions drift. Old files remain. Queries return inconsistent results. People call it a swamp, but the real problem is missing transaction control.

### Data warehouse

Warehouses store tables with strong contracts. Every insert, update, and query runs through a central engine that enforces schemas, indexes, and constraints.

**Use a warehouse when:**

- Business reporting needs predictable performance
- Data models are stable
- Governance and access control matter

**How it fails:** Warehouses fail when they are used as raw data stores. Dumping semi-structured logs and CDC feeds into rigid schemas creates endless ingestion failures and expensive compute. Teams end up fighting the model instead of using it.

**Tools:** Snowflake, BigQuery, Redshift, Azure Synapse, Databricks SQL

### Lakehouse

Lakehouses combine open files with database rules. They store data in object storage but add a transaction log, schema enforcement, and versioning on top. Delta Lake and Apache Iceberg are examples of this pattern.

**Use a lakehouse when:**

- You need both raw and curated data in one place
- Streaming, batch, and ML share the same data
- You need time travel, ACID transactions, and schema evolution

**How it fails:** Lakehouses fail when teams ignore file management and table design. Without compaction, partitioning, and retention, query plans degrade and metadata explodes. The format does not save you from bad engineering.

**Tools:** Delta Lake, Apache Iceberg, Apache Hudi

### Medallion architecture

The medallion architecture (bronze/silver/gold) organizes lakehouse data into layers of increasing quality:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Medallion Architecture                               │
├─────────────────────┬─────────────────────┬─────────────────────────────────┤
│       Bronze        │       Silver        │             Gold                │
│       (Raw)         │     (Cleansed)      │        (Business)               │
├─────────────────────┼─────────────────────┼─────────────────────────────────┤
│ • Raw source data   │ • Deduplicated      │ • Aggregated metrics            │
│ • Append-only       │ • Schema enforced   │ • Business KPIs                 │
│ • Full history      │ • Data quality      │ • Domain-specific               │
│ • Minimal transform │   validated         │ • Query-optimized               │
│                     │ • Conformed types   │                                 │
├─────────────────────┼─────────────────────┼─────────────────────────────────┤
│ Add: ingestion_ts,  │ Apply: SCD logic,   │ Build: star schemas,            │
│ source_system,      │ deduplication,      │ aggregations, feature           │
│ batch_id            │ joins               │ stores                          │
└─────────────────────┴─────────────────────┴─────────────────────────────────┘
```

**Best practices:**

- **Bronze**: Add metadata columns (ingestion timestamp, source system, batch ID)
- **Silver**: Implement slowly changing dimensions (SCD) logic, apply data quality checks
- **Gold**: Optimize for query patterns with proper partitioning and clustering

> [!IMPORTANT]
> **The thumb rule:** The storage pattern decides whether your data behaves like files or like tables. If you get it wrong, every pipeline above it becomes fragile.

[↑ Back to Table of Contents](#table-of-contents)

## Pattern 3: Transformation

*Transformations decide how much damage a bad record can cause.*

Most teams think transformation is just SQL or Spark jobs. In reality, transformation is where raw data becomes trusted data. The pattern you choose decides whether one broken row fails a single model or corrupts your entire warehouse.

### ETL (Extract, Transform, Load)

Transform before loading. Data is cleaned, validated, and shaped before it ever touches analytical storage.

**Use ETL when:**

- Regulatory or financial data must be validated first
- Source systems have strong contracts
- Storage is expensive
- Data needs to be cleaned or standardized before entering storage

**How it fails:** ETL fails when business logic changes. Every new column or rule requires rebuilding upstream jobs. Teams end up reprocessing terabytes of data just to add one metric.

### ELT (Extract, Load, Transform)

Load first, transform later. Raw data is stored, then transformed inside the analytical engine.

**Use ELT when:**

- You run on cloud warehouses or lakehouses
- Multiple teams need the same raw data
- Models change often
- You have high volumes of unstructured data

**How it fails:** ELT fails when raw data becomes a dumping ground. Without strong models and tests, broken upstream data leaks into production dashboards.

**Best practice:** Copy source data as-is. Do not pre-manipulate it, cleanse it, mask it, or convert data types. Simply copy the raw data set exactly as it is in the source.

**Tools:** dbt (data build tool), SQLMesh, Coalesce

### Incremental processing

Only process what changed. Instead of recomputing everything, the pipeline updates only new or modified records.

**Use incremental processing when:**

- Data volumes grow faster than compute budgets
- Late-arriving data is normal
- Backfills must be cheap

**How it fails:** Incremental pipelines fail when keys are unstable or when timestamps are wrong. Bad change tracking creates silent duplication or data loss.

**Implementation patterns:**

```sql
-- Incremental with MERGE/UPSERT (idempotent)
MERGE INTO target_table AS t
USING source_table AS s
ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

```sql
-- dbt incremental model
{{ config(materialized='incremental', unique_key='id') }}

SELECT * FROM {{ source('raw', 'events') }}
{% if is_incremental() %}
WHERE event_time > (SELECT MAX(event_time) FROM {{ this }})
{% endif %}
```

### Watermarking with clock skew tolerance

Clock drift in distributed systems means if you are too aggressive with watermark logic, you might miss records. Add a small buffer to catch records from clock skew:

```sql
-- Buffer for clock skew (e.g., 5 minutes)
WHERE event_time > (SELECT MAX(event_time) - INTERVAL '5 minutes' FROM {{ this }})
```

> [!TIP]
> It is better to load potential duplicates than risk missing critical data. Your downstream layers handle deduplication.

> [!IMPORTANT]
> **The thumb rule:** Transformation patterns define how the state is updated over time. Full refresh models recompute history. Incremental models mutate it. In 2026, only systems designed to track and apply change can scale without breaking cost, latency, or data correctness.

[↑ Back to Table of Contents](#table-of-contents)

## Pattern 4: Orchestration

*Orchestration patterns define system behavior.*

Orchestration is not scheduling—it is how the data system decides what runs, when, and why. Two pipelines can run the same code and still behave completely differently based on how they are orchestrated. One is predictable. The other is fragile under load, retries, and partial failures.

### DAG-based orchestration

Explicit control flow. Each task runs only after its dependencies succeed. Tools like Airflow, Prefect, and Dagster follow this model.

**Use DAGs when:**

- Data must be processed in a strict order
- Backfills and re-runs are common
- Failures must be traceable to a specific step

**How it fails:** DAGs break when they try to model event-driven systems. A single late file can block the entire graph. Teams add sensors, waits, and branching logic until the pipeline becomes unmaintainable.

**Airflow best practices:**

- Avoid top-level imports to prevent issues during DAG parsing
- Treat tasks as transactions where each task performs one specific unit of work
- Partition data to handle larger datasets efficiently
- Avoid using `datetime.now()` in tasks—use Airflow's `execution_date` instead

### Event-driven orchestration

Reactive control flow. Jobs start when data arrives or when another system emits an event. Kafka, pub/sub, and webhooks drive execution.

**Use events when:**

- Data arrives unpredictably
- Systems need to scale independently
- Streaming or microservices are involved

**How it fails:** Event-driven systems fail when observability is weak. Without traceability, a missing event can silently drop data with no obvious error.

### Task-centric vs. asset-centric

Modern orchestrators differ in their fundamental model:

| Approach | Description | Tools |
|:---------|:------------|:------|
| **Task-centric** | Focus on *what runs* (tasks, operators, dependencies) | Airflow, Prefect |
| **Asset-centric** | Focus on *what data is produced* (assets, datasets, lineage) | Dagster, dbt |

**Asset-centric benefits:**

- Data lineage is first-class
- Easier to reason about what data exists
- Better support for incremental computation
- Built-in data quality integration

```text
Task-centric:                    Asset-centric:
┌──────┐   ┌──────┐             ┌──────────┐   ┌──────────┐
│Task A│──▶│Task B│             │ Asset A  │──▶│ Asset B  │
└──────┘   └──────┘             │ (table)  │   │ (table)  │
     │          │               └──────────┘   └──────────┘
     ▼          ▼                    │              │
 "Did it    "Did it              "What data    "What data
  run?"      run?"                exists?"      exists?"
```

> [!IMPORTANT]
> **The thumb rule:** DAGs give you control over order. Events give you control over time. Most modern data platforms need both because some workflows depend on strict ordering, while others depend on responding to data as it arrives. Systems that use only one pattern either miss data or block it.

[↑ Back to Table of Contents](#table-of-contents)

## Pattern 5: Reliability

*Reliability patterns decide if your data survives reality.*

Every data system fails. The only question is whether it fails safely or silently. Most data pipelines work on good days. The real test happens when jobs retry, files arrive twice, networks glitch, or backfills collide with live traffic. Reliability patterns determine whether those events produce clean data or quiet corruption.

> [!NOTE]
> "A healthy pipeline isn't the one that never fails; it's the one you can re-run safely."

### Idempotent jobs

Same input. Same result. An idempotent pipeline can run twice and still produce one correct output. Idempotency is the property where an operation can be applied multiple times without changing the result beyond the initial application.

**Use idempotency when:**

- Jobs can be retried
- Events can be duplicated
- Backfills overlap with live data

**How it fails:** Non-idempotent jobs double count records, overwrite correct data, or produce inconsistent results when retries occur.

**Implementation patterns:**

1. **Delete-Write / INSERT OVERWRITE**: Overwrite specific partitions rather than append

```sql
-- Safe to run multiple times
INSERT OVERWRITE TABLE target PARTITION (date_key = '2026-01-22')
SELECT DISTINCT * FROM staging
WHERE date_key = '2026-01-22';
```

2. **MERGE/UPSERT**: Update if exists, insert if new

```sql
MERGE INTO target t USING source s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

3. **Deterministic logic**: Avoid non-deterministic functions like `CURRENT_TIMESTAMP` or `UUID()` that produce different results on retry

### Retries and dead letter queues

Failures must go somewhere. Retries handle transient issues. Dead letter queues (DLQs) capture records that cannot be processed so they can be inspected and fixed.

**Use them when:**

- Sources are unreliable
- Data quality varies
- Systems depend on upstream APIs

**How it fails:** Without dead letter queues, bad data disappears. Teams only discover the problem when metrics drift weeks later.

**Implementation pattern:**

```text
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Source  │────▶│ Process │────▶│ Target  │
└─────────┘     └────┬────┘     └─────────┘
                     │
                     ▼ (failures)
               ┌─────────┐     ┌─────────┐
               │ Retry   │────▶│  DLQ    │
               │ Queue   │     │(inspect)│
               └─────────┘     └─────────┘
```

**Retry best practices:**

- Implement exponential backoff for transient failures
- Set maximum retry limits to avoid infinite loops
- Log all failures with context for debugging
- Route persistent failures to DLQ after retry exhaustion

### Backfills

Replaying history safely. Backfills allow you to recompute past data without breaking production.

**Use backfills when:**

- Logic changes
- Bugs are fixed
- Late data arrives

**How it fails:** Backfills fail when they overwrite newer data or run with different logic than production pipelines.

**Safe backfill practices:**

1. **Batch schema changes**: If you need to add three fields over the next quarter, add them all at once to avoid multiple historical loads

2. **Protect source systems**: Source systems are optimized for operational workloads, not analytical workloads. Process backfills in manageable time ranges with throttling

3. **Use the same code path**: Backfills must use the same transformation logic as production to avoid inconsistency

4. **Partition-level operations**: Reprocess one partition at a time to limit blast radius

> [!WARNING]
> These patterns add 20-30% upfront complexity but save 10x the debugging time. Skip them, and your 2 AM PagerDuty shift becomes a weekly ritual.

> [!IMPORTANT]
> **The thumb rule:** Production data systems operate in an environment where retries, duplicate events, late data, and partial failures are guaranteed. Pipelines must be designed to converge to the same correct state, regardless of how many times data is processed or replayed. If a pipeline only works when everything runs once and in order, it corrupts data the first time reality deviates.

[↑ Back to Table of Contents](#table-of-contents)

## Pattern 6: Quality and governance

*Quality patterns make data defensible.*

Raw data is cheap. Trusted data is expensive. Most organizations do not lose trust in data because of one bad record. They lose it because nobody can explain where the numbers came from, why they changed, or whether they are safe to use. Quality and governance patterns exist to make data defensible.

### Data quality dimensions

Practitioners commonly track five core dimensions:

| Dimension | Definition | Example Check |
|:----------|:-----------|:--------------|
| **Accuracy** | Data correctly represents reality | Revenue matches source system |
| **Completeness** | No missing values where required | Customer email is not null |
| **Consistency** | Same value across systems | Order status matches in all tables |
| **Timeliness** | Data is fresh enough for use | Dashboard updated within SLA |
| **Validity** | Data conforms to format/range | Date is valid ISO format |
| **Uniqueness** | No duplicate records | One row per order ID |

### Validation

Fail fast at the boundary. Data should be checked as it enters the system, not weeks later in a dashboard.

**Use validation when:**

- Data feeds come from external systems
- Business-critical metrics depend on accuracy
- Schema drift is expected

**How it fails:** Without validation, bad data flows through every downstream table. By the time someone notices, the error has already been copied into reports, ML models, and exports.

**Tools:** Great Expectations, Soda, dbt tests, Apache Deequ, Monte Carlo

**Example validation rules:**

```yaml
# Great Expectations example
expectations:
  - expect_column_values_to_not_be_null:
      column: customer_id
  - expect_column_values_to_be_between:
      column: order_amount
      min_value: 0
      max_value: 1000000
  - expect_column_values_to_be_unique:
      column: order_id
```

### Schema evolution

Change without breaking consumers. Schemas must change, but changes must be controlled.

**Use schema evolution when:**

- New fields are added frequently
- Data contracts evolve
- Backward compatibility matters

**How it fails:** Hard schema enforcement causes ingestion failures. No schema enforcement causes silent corruption. Good systems track versions and apply rules for compatibility.

**Compatibility rules:**

| Type | Definition | Safe Changes |
|:-----|:-----------|:-------------|
| **Backward** | New schema can read old data | Add optional fields, remove fields |
| **Forward** | Old schema can read new data | Add fields, remove optional fields |
| **Full** | Both directions work | Add/remove optional fields only |

**Tools:** Confluent Schema Registry, AWS Glue Schema Registry, Apicurio

### Data contracts

Data contracts are formal agreements between data producers and consumers defining:

- Schema definitions (fields, types, constraints)
- Data quality expectations (SLAs, freshness)
- Ownership and contact information
- Update policies and deprecation timelines
- Breaking vs. non-breaking change rules

```yaml
# Example data contract
name: orders
version: 2.1.0
owner: commerce-team@company.com
schema:
  - name: order_id
    type: string
    required: true
    unique: true
  - name: customer_id
    type: string
    required: true
  - name: order_total
    type: decimal(10,2)
    required: true
    constraints:
      - min: 0
quality:
  freshness: 1 hour
  completeness: 99.9%
```

### Lineage

Trace every number back to its source. Lineage shows how data moved, changed, and was used.

**Use lineage when:**

- Audits or compliance exist
- Metrics are business-critical
- Multiple teams share data

**How it fails:** Without lineage, every data issue becomes a guessing game. Teams argue instead of debugging. Without these patterns, the team wastes days trying to figure out which pipeline caused the error.

**Lineage approaches:**

| Type | Description | Pros/Cons |
|:-----|:------------|:----------|
| **Pattern-based** | Infers lineage from naming conventions | Lightweight, but less accurate |
| **Parse-based** | Analyzes SQL/code to extract lineage | Accurate, but compute-intensive |
| **Runtime** | Captures lineage during execution | Most accurate, but adds overhead |

**Tools:** Apache Atlas, DataHub, Marquez, OpenLineage, Atlan

> [!TIP]
> Prioritize high-value lineage—cover critical reports, regulatory datasets, and business-essential pipelines. It is better to have precise lineage for fewer assets than incomplete mappings for everything.

> [!IMPORTANT]
> **The thumb rule:** Data quality and governance must operate at the same layer where data changes. Validation, schema control, and lineage should be part of the data flow itself. When governance is added after the fact, errors have already propagated, and trust is already lost.

[↑ Back to Table of Contents](#table-of-contents)

## Pattern 7: Serving

*Serving patterns decide whether data creates value.*

A perfect pipeline that nobody can use is a failure. Most data platforms break at the last mile. Data lands in storage, models run, and then consumers struggle to get consistent answers. Serving patterns decide how data is exposed, controlled, and trusted by the rest of the company.

### Semantic layer

One definition of truth. The semantic layer defines metrics, dimensions, and business logic once so every dashboard and query uses the same rules.

**Use a semantic layer when:**

- Multiple BI tools exist
- Metrics must be consistent
- Business users query data directly

**How it fails:** Without a semantic layer, every team writes its own SQL. Revenue, churn, and growth end up with multiple definitions.

**Architecture patterns (2025-2026):**

| Pattern | Description | Examples |
|:--------|:------------|:---------|
| **Warehouse-native** | Semantic metadata as database objects | Snowflake Semantic Views, Databricks Metric Views |
| **Transformation-layer** | Semantic models as code in dbt | dbt Semantic Layer + MetricFlow |
| **OLAP-acceleration** | Intelligent caching with pre-aggregations | Cube.dev |

**dbt Semantic Layer example:**

```yaml
# metrics.yml
semantic_models:
  - name: orders
    defaults:
      agg_time_dimension: order_date
    entities:
      - name: order_id
        type: primary
    measures:
      - name: order_total
        agg: sum
        expr: order_amount
    dimensions:
      - name: order_date
        type: time

metrics:
  - name: revenue
    type: simple
    type_params:
      measure: order_total
```

**Open Semantic Interchange (OSI):** In 2025, dbt Labs, Snowflake, Salesforce, and others launched an effort to standardize semantic layer definitions. The goal: define a metric once in vendor-neutral YAML, and have every tool consume it. Expect meaningful interoperability in 2026-2027.

### APIs

Data as a product. APIs expose data to applications, ML models, and external systems with controlled access and rate limits.

**Use APIs when:**

- Data powers products
- Machine learning needs features
- External partners consume data

**How it fails:** Direct database access creates tight coupling. One heavy query can take down production.

**API patterns for data:**

| Pattern | Use Case | Characteristics |
|:--------|:---------|:----------------|
| **REST API** | General data access | Simple, widely supported, cacheable |
| **GraphQL** | Flexible queries | Client specifies fields, reduces over-fetching |
| **gRPC** | High-performance internal | Binary protocol, streaming support |
| **Feature Store** | ML features | Versioned, low-latency, batch + online |

**Feature store architecture:**

```text
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Batch     │────▶│   Feature   │────▶│   Offline   │
│  Pipeline   │     │   Store     │     │   Store     │
└─────────────┘     │             │     │  (training) │
                    │             │     └─────────────┘
┌─────────────┐     │             │     ┌─────────────┐
│  Streaming  │────▶│             │────▶│   Online    │
│  Pipeline   │     │             │     │   Store     │
└─────────────┘     └─────────────┘     │ (inference) │
                                        └─────────────┘
```

**Tools:** Feast, Tecton, Amazon SageMaker Feature Store

> [!IMPORTANT]
> **The thumb rule:** Data should be exposed through stable contracts that match how it is consumed. Analytical users need governed metrics, while applications need low-latency APIs. When all consumers hit raw tables, performance, cost, and correctness collapse.

[↑ Back to Table of Contents](#table-of-contents)

## Pattern 8: Performance

*Performance patterns decide what your platform costs.*

Every data platform looks fast in a demo. The bill shows up in production. Performance patterns determine how much data you scan, how often you recompute, and how much infrastructure stays idle. Most teams do not overspend because their queries are slow—they overspend because their systems are designed to move and process far more data than necessary.

### Partitioning

Query less data. Partitioning physically organizes data so queries only scan what they need.

**Use partitioning when:**

- Tables are large
- Queries filter on time, region, or customer
- Backfills are common

**How it fails:** Bad partitioning forces full table scans. One dashboard query can read terabytes of data and drive massive compute costs.

**Partitioning methods:**

| Method | Description | Best For |
|:-------|:------------|:---------|
| **Range** | Partition by value ranges (dates, IDs) | Time-series data, historical queries |
| **Hash** | Partition by hash of key | Even distribution, point lookups |
| **List** | Partition by explicit values | Categorical data (region, status) |

**Best practices:**

- Align partition keys with common query filters
- Avoid over-partitioning (too many small files)
- Monitor partition skew (uneven data distribution)
- Use clustering/sorting within partitions for additional pruning

```sql
-- Partitioned table with clustering
CREATE TABLE events (
    event_id STRING,
    user_id STRING,
    event_time TIMESTAMP,
    event_type STRING
)
PARTITIONED BY (DATE(event_time))
CLUSTERED BY (user_id) INTO 256 BUCKETS;
```

### Caching

Do not compute the same answer twice. Caching stores results close to users so repeated queries return instantly.

**Use caching when:**

- Dashboards refresh often
- Many users run similar queries
- Data changes slowly

**How it fails:** Caching fails when freshness rules are unclear. Stale data quietly breaks trust.

**Caching strategies:**

| Strategy | Description | Use Case |
|:---------|:------------|:---------|
| **Query result cache** | Cache full query results | Identical repeated queries |
| **Materialized views** | Pre-computed aggregations | Common aggregations |
| **Distributed cache** | External cache layer (Redis) | Application-level caching |
| **Semantic layer cache** | Cache at metrics layer | BI tool queries |

**Cache invalidation patterns:**

- **Time-based (TTL)**: Expire after fixed duration
- **Event-based**: Invalidate when source data changes
- **Version-based**: Include data version in cache key

> [!WARNING]
> Industry statistics show that, on average, only 15-20% of a company's data benefits from high-performance storage. The rest is largely dormant.

### Tiered storage and on-demand compute

Pay for use, not capacity. Hot data stays on fast storage. Cold data moves to cheap storage. Compute spins up only when queries run.

**Use this when:**

- Workloads spike
- Historical data is large
- Cost control matters

**How it fails:** Without lifecycle rules and monitoring, old data piles up on expensive storage, and compute never scales down.

**Storage tier mapping:**

| Tier | Storage Type | Use Case | Access Pattern |
|:-----|:-------------|:---------|:---------------|
| **Hot (Tier 0/1)** | NVMe SSD, in-memory | Real-time analytics, OLTP | Sub-second access |
| **Warm (Tier 2)** | Standard SSD, high-throughput object | Recent data, ad-hoc queries | Seconds to minutes |
| **Cold (Tier 3)** | Infrequent-access S3, Glacier | Compliance, rare access | Minutes to hours |

**Automated tiering:**

```text
┌─────────────┐   30 days   ┌─────────────┐   90 days   ┌─────────────┐
│    Hot      │────────────▶│    Warm     │────────────▶│    Cold     │
│   (SSD)     │             │  (Standard) │             │  (Archive)  │
└─────────────┘             └─────────────┘             └─────────────┘
     $$$                         $$                          $
```

**Caching vs. tiering:**

| Aspect | Caching | Tiering |
|:-------|:--------|:--------|
| **Purpose** | Speed up short-term access | Optimize long-term storage costs |
| **Data location** | Temporary copy | Permanent relocation |
| **Trigger** | Access frequency | Policy/time-based |
| **Use case** | Repetitive queries | Large data lifecycle |

> [!IMPORTANT]
> **The thumb rule:** Data platform cost and reliability are controlled by how much data is scanned, recomputed, and kept hot. Partitioning limits what gets read, caching limits what gets recomputed, and tiered storage limits what stays expensive. When these patterns are missing, performance problems turn into cost problems.

[↑ Back to Table of Contents](#table-of-contents)

## Decision framework

Use this framework to select appropriate patterns for your use case:

### Ingestion decision tree

```text
                    ┌─────────────────────┐
                    │ What is your latency │
                    │    requirement?      │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │  Hours/  │        │ Minutes  │        │ Seconds  │
    │  Days    │        │          │        │          │
    └────┬─────┘        └────┬─────┘        └────┬─────┘
         │                   │                   │
         ▼                   ▼                   ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │  BATCH   │        │   CDC    │        │ STREAMING│
    └──────────┘        └──────────┘        └──────────┘
```

### Storage decision tree

```text
                    ┌─────────────────────┐
                    │  What are your      │
                    │  primary workloads? │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │ Raw data │        │ Mixed    │        │ BI/SQL   │
    │ ML/DS    │        │ workloads│        │ reporting│
    └────┬─────┘        └────┬─────┘        └────┬─────┘
         │                   │                   │
         ▼                   ▼                   ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │   LAKE   │        │ LAKEHOUSE│        │WAREHOUSE │
    └──────────┘        └──────────┘        └──────────┘
```

### Pattern compatibility matrix

| Pattern | Works Well With | Conflicts With |
|:--------|:----------------|:---------------|
| Batch ingestion | Warehouse, ETL, DAG orchestration | Real-time serving |
| Streaming | Lakehouse, event-driven, CDC | Batch-only storage |
| CDC | Incremental processing, lakehouse | Full refresh ETL |
| Lakehouse | All transformation patterns | Legacy BI tools |
| Incremental | CDC, lakehouse, idempotent jobs | Simple batch scripts |
| Semantic layer | Warehouse, lakehouse | Direct table access |

[↑ Back to Table of Contents](#table-of-contents)

## Further reading

### Internal documentation

- [How-To: Configure Kafka producers and consumers](../how-to/kafka/README.md)
- [Tutorial: Liquibase for database change management](../tutorials/liquibase/README.md)
- [Reference: gds_database package](../reference/gds-database/README.md)

### External resources

**Books and courses:**

- [Data Engineering Design Patterns Book](https://www.dedp.online/) - Bartosz Konieczny
- [Data Engineering Design Patterns (O'Reilly)](https://www.oreilly.com/library/view/data-engineering-design/9781098165826/)

**Tools documentation:**

- [Apache Iceberg](https://iceberg.apache.org/) - Open table format for lakehouses
- [Delta Lake](https://delta.io/) - Open-source lakehouse storage layer
- [dbt Semantic Layer](https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl) - Metrics layer
- [Great Expectations](https://greatexpectations.io/) - Data quality
- [Dagster](https://dagster.io/) - Asset-centric orchestration

**Architecture patterns:**

- [Medallion Architecture (Databricks)](https://www.databricks.com/glossary/medallion-architecture)
- [Kappa Architecture](https://www.kai-waehner.de/blog/2021/09/23/real-time-kappa-architecture-mainstream-replacing-batch-lambda/)

### Sources

This document synthesizes information from:

- "Data Engineering Design Patterns You Must Learn in 2026" by Khushbu Shah, AWS in Plain English (January 2026)
- [Data Ingestion Best Practices](https://www.integrate.io/blog/data-ingestion-best-practices-a-comprehensive-guide-for-2025/) - Integrate.io
- [ETL vs ELT](https://aws.amazon.com/compare/the-difference-between-etl-and-elt/) - AWS
- [Building Idempotent Data Pipelines](https://medium.com/towards-data-engineering/building-idempotent-data-pipelines-a-practical-guide-to-reliability-at-scale-2afc1dcb7251) - Towards Data Engineering
- [Data Pipeline Orchestration Tools](https://dagster.io/learn/data-pipeline-orchestration-tools) - Dagster
- [Semantic Layer 2025](https://www.typedef.ai/resources/semantic-layer-metricflow-vs-snowflake-vs-databricks) - TypeDef
- [Data Partitioning](https://airbyte.com/data-engineering-resources/what-is-data-partitioning) - Airbyte
- [Reliable Reprocessing and Dead Letter Queues](https://www.uber.com/blog/reliable-reprocessing/) - Uber Engineering

[↑ Back to Table of Contents](#table-of-contents)
