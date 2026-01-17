# HammerDB Exercises

To reinforce your learning, complete the following exercises. These range from beginner to advanced.

## Exercise 1: Establishing a Baseline (Beginner)

**Objective**: Run a standard TPC-C test on PostgreSQL to establish a performance baseline.

1. **Setup**:
    * Create a `tpcc` database on PostgreSQL.
    * Configure `shared_buffers` to 25% of RAM.
2. **Build**:
    * Build a TPC-C schema with **10 Warehouses**.
3. **Run**:
    * **GUI**: Configure the Driver Script for **2 minutes rampup** and **5 minutes testing**. Run with **2 Virtual Users**.
    * **CLI**:
        * See **[HammerDB CLI Reference](../../reference/hammerdb-cli.md)** for command definitions.

        ```tcl
        #!/bin/tclsh
        dbset db pg
        diset connection pg_host "localhost"
        diset connection pg_port "5432"
        diset tpcc pg_count_ware 10
        diset tpcc pg_num_vu 2
        diset tpcc pg_rampup 2
        diset tpcc pg_duration 5
        vuset logtotemp 1
        loadscript
        vuset vu 2
        vucreate
        vurun
        ```

    * Save as `run_tpcc.tcl` and execute: `./hammerdbcli auto run_tpcc.tcl`
4. **Record**:
    * What was your NOPM?
    * What was your TPM?
    * Save the HammerDB log file.

## Exercise 2: The Impact of Shared Buffers (Intermediate)

**Objective**: Understand how memory configuration affects database performance.

1. **Hypothesis**: Reducing `shared_buffers` significantly will decrease NOPM.
2. **Action**:
    * Edit `postgresql.conf` and set `shared_buffers` to a very low value (e.g., `128MB` or `64MB`).
    * Restart PostgreSQL.
3. **Run**:
    * Run the *exact same* test as Exercise 1 (10 Warehouses, 2 Users, 2m/5m).
4. **Analysis**:
    * Compare the NOPM with Exercise 1.
    * Did it drop? By how much?
    * Check CPU usage. Is it higher or lower? (likely higher I/O wait).

## Exercise 3: SQL Server MaxDOP and TPC-H (Advanced)

**Objective**: Optimize SQL Server for Analytical Workloads.

1. **Setup**:
    * Build a TPC-H schema on SQL Server (Scale Factor 1).
2. **Run 1 (OLTP settings)**:
    * **GUI**: Set MaxDOP to 1. Run the **TPC-H Power Test** (Single User). Record the total time.
    * **CLI**:

        ```tcl
        #!/bin/tclsh
        dbset db mssqls
        diset connection mssqls_server "localhost"
        diset tpch mssqls_scale_fact 1
        # Configure Power Test
        diset tpch mssqls_total_query_sets 1
        vuset logtotemp 1
        loadscript
        vuset vu 1
        vucreate
        vurun
        ```

3. **Run 2 (OLAP settings)**:
    * Set MaxDOP to 0 (Unlimited) or 4.
    * Run the **TPC-H Power Test** again.
4. **Analysis**:
    * Calculate the percentage improvement in execution time.
    * Explain why parallelism helps TPC-H but might hurt TPC-C.
