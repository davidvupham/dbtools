# Running Workloads

Once your schema is built, you are ready to run tests.

## Running TPC-C Workloads

TPC-C is the standard for measuring Order-Entry performance (OLTP).

### 1. Driver Script

1. **Driver Script**: Go to **Benchmark** -> **[DB Type]** -> **TPC-C** -> **Driver Script**.
2. **Settings**:
    * **Total Transactions per User**: Leave automatic or set a high number.
    * **Rampup Time**: **CRITICAL**. Set this to `2` to `5` minutes. This allows the database cache to warm up before measurement begins.
    * **Test Duration**: Standard runs are 10-20 minutes.
    * **Use All Warehouses**: Check this to ensure load is distributed.
3. Click **Load** to load the Tcl script into the window.

### 2. Virtual Users

1. **Virtual Users**: Go to **Virtual Users**.
2. **Options**:
    * **Virtual Users**: The number of concurrent connections.
    * **Create Virtual Users**: Click to spawn the threads.
3. **Run**: Click the **Run** button (green arrow) to start the test.

### Virtual Users vs. Processors

A common question is: "How many users should I run?"

* **Rule of Thumb**: For standard Max-Throughput testing (No Think Time), start with 1 Virtual User.
* **Deep Dive**: See **[Virtual Users vs Processors](../../explanation/hammerdb-benchmarking.md#virtual-users-vs-processors)** in the explanation guide for details on scaling and think time.

> [!TIP]
> Start with 1 Virtual User to verify connectivity and basic functionality before ramping up.

### 3. Using Autopilot (Recommended)

For serious benchmarking, you want to find the "peak" performance curve. Autopilot automates this by running the test multiple times with increasing virtual users (e.g., 2, 4, 8, 16, 32, 64...).

1. Enable **Autopilot** in the menu.
2. Configure the intervals (e.g., `2 4 8 16 32 64`).
3. Set the run time per interval (e.g., 5 mins rampup, 15 mins test).
4. Start the Autopilot run and go grab a coffee.

---

## Running TPC-H Workloads

TPC-H measures analytical query performance (OLAP).

### 1. The Power Test

The Power Test measures the execution time of 22 complex queries run sequentially by a single user.

1. **Driver Script**: Select **TPC-H** -> **Driver Script**.
2. **Load**: Load the script.
3. **Virtual Users**: Create 1 Virtual User.
4. **Run**: Execute. The result is the total time taken to complete all 22 queries.

### 2. The Throughput Test

This runs multiple streams of queries concurrently.

1. **Driver Script**: Select **Throughput Test**.
2. **Virtual Users**: Create multiple users (e.g., 4, 8, etc.).
3. **Run**: Execute.
4. **Result**: The metric is "Queries Per Hour" (QphH).

> [!IMPORTANT]
> TPC-H queries are extremely resource-intensive. Ensure your database `work_mem` (Postgres) or memory grants (SQL Server) are sufficient, otherwise queries will spill to disk and destroy performance.

[Next: Analysis and Best Practices ->](analysis-and-best-practices.md)
