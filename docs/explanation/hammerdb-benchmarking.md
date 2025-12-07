# HammerDB Benchmarking Concepts

## What is HammerDB?

HammerDB is the leading open-source benchmarking and load testing software for the world's most popular web databases. Ideally suited for testing database systems running on physical hardware, virtual environments, and the cloud, it mimics real-world workloads to help you understand your database's performance limits.

## Benchmark Types

HammerDB focuses on two specific industry-standard benchmarks derived from the Transaction Processing Performance Council (TPC):

### TPC-C (OLTP)

* **Purpose**: Simulates a wholesale parts supplier (Online Transaction Processing).
* **Workload**: Heavy on read/write transactions, locking, and concurrency.
* **Primary Metric**: **NOPM** (New Orders Per Minute). This metric measures the business throughput (completed orders) and is the standard for comparing different database platforms.
* **Secondary Metric**: **TPM** (Transactions Per Minute). This counts all database transactions (including internal ones). It is useful for internal relative comparisons but less useful for cross-platform comparison.

### TPC-H (OLAP)

* **Purpose**: Simulates a decision support system with ad-hoc queries (Online Analytical Processing).
* **Workload**: Complex, long-running queries that scan large datasets.
* **Primary Metric**: **QphH** (Queries per Hour).
* **Resource Usage**: Heavily dependent on memory (`work_mem`, `tempdb`) and parallel processing capabilities (MaxDOP).

## Sizing and Architecture

### Virtual Users vs. Processors

A common question in benchmarking is the relationship between the load generator's virtual users and the database's physical cores.

* **Standard Benchmarking (No Think Time)**:
  * In this mode, Virtual Users loop transactions as fast as possible.
  * **Ratio**: Typically, **1 Virtual User** can drive **1 Physical Core** on the database server to saturation.
  * **Scaling**: Exceeding the core count with VUs often leads to diminishing returns due to context switching.

* **Realistic Simulation (With Think Time)**:
  * In this mode, VUs pause ("think") between transactions, simulating human behavior.
  * **Ratio**: You can run **thousands** of VUs against a smaller number of cores. HammerDB uses asynchronous scaling to handle this efficiently.

### Client-Side Bottlenecks

For a benchmark to be valid, the bottleneck **must** be the database, not the client generating the load.

* **CPU**: If the HammerDB client CPU hits 100%, the results are invalid.
* **Network**: The client must be in the same LAN/Availability Zone as the database. Network latency (waiting for ACKs) looks like "think time" to the database, preventing it from reaching full saturation.
* **UI Overhead**: The HammerDB GUI ("Show Results") consumes significant CPU. For maximum throughput, use the CLI or disable real-time graphing.
