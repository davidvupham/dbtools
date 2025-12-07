# HammerDB Benchmarking Tutorial

HammerDB is the leading open-source benchmarking tool for SQL databases. This tutorial covers how to use it to benchmark **PostgreSQL** and **Microsoft SQL Server**.

For a deep dive into the concepts (TPC-C VS TPC-H, Virtual Users vs Cores, NOPM), see **[HammerDB Benchmarking Explanation](../../explanation/hammerdb-benchmarking.md)**.

## Prerequisites

Before starting, ensure you have:

* **Sizing**: The client must have enough CPU power to generate the load. If the client CPU hits 100%, the bottleneck is the benchmark tool, not the database.
* **HammerDB Client**: A Linux machine (or VM) to run HammerDB.
  * **Sizing**: The client must have enough CPU power to generate the load. If the client CPU hits 100%, the bottleneck is the benchmark tool, not the database.
  * **Recommendation**: 4+ vCPUs for standard testing.
    * **Rule of Thumb**: A single Virtual User can roughly drive one CPU core on the *database server* to 100% (without keying/thinking time). Ensure your client is robust enough to spawn sufficient threads.
    * For high-concurrency (hundreds of users), consider using multiple client machines or a very powerful client.
* **Target Database**:
  * PostgreSQL (v12+ recommended)
  * Microsoft SQL Server (2019+ recommended)
* **Network Access**: The HammerDB client must have network access to the target database ports (default 5432 for Postgres, 1433 for SQL Server).
  * **Proximity**: The client MUST be in close network proximity to the database (same LAN, same datacenter, or same Availability Zone). High network latency (e.g., cross-region) will severely distort benchmark results as the client waits for ACK packets instead of generating load.

## Installation Guide (Linux)

1. **Download HammerDB**:
    Visit the [HammerDB Download Page](https://www.hammerdb.com/download.html) and download the latest version for Linux (e.g., v4.10).

    ```bash
    # Example using wget (replace URL with latest version)
    wget https://github.com/TPC-Council/HammerDB/releases/download/v4.10/HammerDB-4.10-Linux.tar.gz
    ```

2. **Extract the Archive**:

    ```bash
    tar -zxvf HammerDB-4.10-Linux.tar.gz
    cd HammerDB-4.10
    ```

3. **Run HammerDB**:
    HammerDB has both a GUI and a CLI.
    * **GUI**: Run `./hammerdb`. Note: Requires a desktop environment (X11) or X forwarding.
    * **CLI**: Run `./hammerdbcli`. Useful for automated or headless testing.

    > [!NOTE]
    > This tutorial will reference GUI concepts for ease of understanding, but all actions can be scripted via the CLI (TCL scripts).

## Tutorial Modules

1. **[Database Configuration](configuration.md)**: setup PostgreSQL and SQL Server for benchmarking.
2. **[Running Workloads](running-workloads.md)**: execute TPC-C and TPC-H tests.
3. **[Analysis and Best Practices](analysis-and-best-practices.md)**: interpret results and avoid common pitfalls.
4. **[gds_hammerdb Usage](gds-hammerdb-usage.md)**: Python automation for benchmarks.
5. **[Exercises](exercises.md)**: hands-on practice tasks.

## Reference

* **[HammerDB CLI Reference](../../reference/hammerdb-cli.md)**: Command guide for automation.

[Next: Database Configuration ->](configuration.md)
