# Analysis and Best Practices

Running the benchmark is only half the battle. Interpreting the results correctly is key.

## Interpreting Results

### TPM vs. NOPM

HammerDB reports two main metrics for TPC-C: **TPM** and **NOPM**.

* **Key Insight**: Always use **NOPM (New Orders Per Minute)** for cross-platform comparisons.
* **Learn More**: See **[TPM vs NOPM](../../explanation/hammerdb-benchmarking.md#benchmark-types)** for the full definition of these metrics.

### Latency

While throughput (NOPM) is important, **latency** is critical for user experience.

* Check the HammerDB log or database logs for query latency.
* A system pushing 1 million NOPM is useless if each transaction takes 5 seconds. Ideally, you want 90% of transactions < 1s.

## Establishing a Baseline

A baseline is a known "good" state performance record.

1. **Record Everything**: Hardware stats, DB config, OS version.
2. **Steady State**: Ensure your graph flattens out. If performance is jittery or declining, you haven't reached steady state or you are hitting a bottleneck (thermal throttling, cache fills, etc.).
3. **Cache Invalidation**:
    * **Scenario A: Max Throughput (Steady State)**: Do **NOT** restart the DB. Allow the system to warm up (rampup time) until it hits steady state. Clearing the cache just prolongs the rampup time.
    * **Scenario B: Comparative Baselines (A/B Testing)**: If you are comparing two configurations (e.g., `shared_buffers=1GB` vs `shared_buffers=2GB`), you must ensure the starting state is identical.
        * **Recommendation**: **Restart the Database Service** and (optionally) drop OS caches (`sync; echo 3 > /proc/sys/vm/drop_caches`) between runs. This resets the RAM state.
        * **Recreation**: You do **not** need to Drop/Create the database unless the previous run significantly bloated the table size or fragmented indexes. For standard runs, a service restart is sufficient to clear the "Data Cache" (Buffer Pool).
    * **TPC-H (Analytics)**:
        * **Power Test**: Often run on a **cold cache** (restart DB) to test raw I/O speed.
        * **Data Integrity**: If you use TPC-H "Refresh Functions", you **MUST** restore from backup.
4. **Save Your Results**: Store the HammerDB log files and an autopilot summary in a version-controlled repo or a shared location.

## Dos and Don'ts

### Dos

* **DO** Monitor system metrics. Run `htop`, `iostat -kx 1`, or `vmstat 1` on the database server during the run.
  * If CPU < 100% and I/O is saturated -> **Disk Bottleneck**.
  * If CPU is 100% and I/O is low -> **CPU Bottleneck** (this is ideal for TPC-C).
  * **CRITICAL**: Monitor the **HammerDB Client** CPU as well. If the client is at 100%, your results are invalid because the generator is too slow.
    * **Tip**: Disable the HammerDB GUI "Show Results" or run via CLI (`hammerdbcli`) to save significant client CPU cycles.
* **DO** Configure `Huge Pages` on Linux for large memory instances.

### Don'ts

* **DON'T** Run benchmarks across high-latency networks (e.g., Laptop -> Cloud DB, or US-East -> US-West). The time spent on "network round trip" essentially becomes "think time," preventing the database from being fully stressed.
* **DON'T** Compare specific NOPM numbers to official TPC-C results. HammerDB is a "Derived" TPC-C workload, not an audited official run.

## Troubleshooting Common Issues

* **"Connection Refused"**: Check firewall (port 5432/1433) and listen addresses (`listen_addresses = '*'` in Postgres).
* **Low Performance**: Did you run standard defaults? Check your cache sizes (`shared_buffers` / `Max Server Memory`).
* **High I/O Wait**: Your transaction log (WAL or tlog) is likely on a slow disk. Move it to NVMe/SSD.

[Next: Exercises ->](exercises.md)
