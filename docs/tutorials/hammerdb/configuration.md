# Database Configuration for Benchmarking

Proper database configuration is critical for getting meaningful benchmark results. A default database installation is often optimized for compatibility, not performance.

## PostgreSQL Configuration

### 1. User and Database Setup

Create a dedicated user and database for the benchmark.

```sql
CREATE USER hammerdb WITH PASSWORD 'password';
CREATE DATABASE tpcc WITH OWNER hammerdb;
GRANT ALL PRIVILEGES ON DATABASE tpcc TO hammerdb;
```

### 2. Performance Tuning (Essential)

Edit your `postgresql.conf` or use `ALTER SYSTEM` to adjust these key parameters. These are starting points; usually, you want to tune these based on your RAM.

* **`shared_buffers`**: Set to ~25% of system RAM.
* **`work_mem`**: Increase for TPC-H complex queries (e.g., `64MB` or more depending on concurrent users).
* **`maintenance_work_mem`**: Increase to speed up index creation during schema build (e.g., `1GB`).
* **`checkpoint_completion_target`**: Set to `0.9` to spread out checkpoint I/O.
* **`wal_buffers`**: Set to `16MB`.
* **`max_wal_size`**: Increase to `4GB` or higher to reduce checkpoint frequency.

### 3. Huge Pages (Linux Only)

For high-performance Postgres benchmarks, **Huge Pages** are strongly recommended to reduce TLB misses.

1. Check current setting: `cat /proc/meminfo | grep Huge`
2. Calculate needed pages based on `shared_buffers`.
3. Enable in OS (`sysctl -w vm.nr_hugepages=X`) and set `huge_pages = on` in `postgresql.conf`.

---

## Microsoft SQL Server Configuration

### 1. maximize Performance

* **MaxDOP (Maximum Degree of Parallelism)**: For TPC-C (OLTP), set MaxDOP to 1 or up to the number of generic processors per NUMA node. For TPC-H (OLAP), higher parallelism is desired.

    ```sql
    EXEC sp_configure 'show advanced options', 1;
    RECONFIGURE;
    EXEC sp_configure 'max degree of parallelism', 1; -- For TPC-C
    RECONFIGURE;
    ```

* **Memory**: Ensure SQL Server has "Lock Pages in Memory" privilege to prevent paging to disk.

### 2. TempDB Optimization

HammerDB (especially TPC-H) uses TempDB heavily.

* Ensure **TempDB** is on fast storage (NVMe/SSD).
* Pre-size TempDB files and create multiple data files (one per CPU core, up to 8) to reduce allocation contention.

### 3. Log and Data File Sizing

**CRITICAL**: Pre-size your transaction log and data files *before* the benchmark run. If the database has to auto-grow files during the run, your results will be skewed by file system operations.

* Set `Autogrowth` to a managed size (e.g., 512MB or 1GB) rather than a percentage, but try to size files so they don't grow at all.

---

## HammerDB Schema Build

Before running any workload, you must build the schema.

1. Open HammerDB.
2. Select **Benchmark** -> **[DB Type]** -> **TPC-C** -> **Schema Build**.
3. **Options**:
    * **Virtual Users**: Number of threads to use for building (set to match your client CPU cores).
    * **Warehouses**: The scale factor.
        * **10 Warehouses** ~ 1GB (Good for quick functional test)
        * **1000 Warehouses** ~ 100GB (Good baseline for production-grade hardware)
4. Click **Build**. This will create the tables and populate them with data.
    > [!WARNING]
    > This process can take a significant amount of time depending on the number of warehouses.

[Next: Running Workloads ->](running-workloads.md)
