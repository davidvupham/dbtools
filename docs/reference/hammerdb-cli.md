# HammerDB CLI (Tcl) Reference

This guide provides a comprehensive reference for the HammerDB Command Line Interface (CLI) using Tcl. It covers connection, configuration, and execution commands for PostgreSQL and Microsoft SQL Server.

**Official Documentation**: [https://www.hammerdb.com/docs/](https://www.hammerdb.com/docs/)

## Core Commands

| Command | Description | Example |
| :--- | :--- | :--- |
| `dbset db [value]` | Selects the database plugin. Values: `pg`, `mssqls`, `ora`, `mysql`. | `dbset db pg` |
| `dbset bm [value]` | Selects the benchmark type. Values: `TPC-C`, `TPC-H`. | `dbset bm TPC-C` |
| `loadscript` | Generates the driver script based on current `diset` configuration and loads it into memory. | `loadscript` |
| `vucreate` | Creates the virtual users based on `vuset` configuration. | `vucreate` |
| `vurun` | Starts the benchmark run. Blocks until completion. | `vurun` |
| `vudestroy` | Destroys virtual users after a run. | `vudestroy` |
| `print dict` | Prints all current dictionary settings. | `print dict` |

## Configuration Commands (`diset`)

The `diset` command sets dictionary values. Syntax: `diset [component] [parameter] [value]`.

### PostgreSQL Settings (`dbset db pg`)

| Component | Parameter | Description |
| :--- | :--- | :--- |
| **Connection** | `pg_host` | Hostname or IP of the DB server. |
| **Connection** | `pg_port` | Port (Default: 5432). |
| **Connection** | `pg_user` | Database superuser for schema build (Default: `postgres`). |
| **Connection** | `pg_pass` | Password for the user. |
| **TPC-C** | `pg_count_ware` | Number of Warehouses (Scale Factor). |
| **TPC-C** | `pg_num_vu` | Number of Virtual Users. |
| **TPC-C** | `pg_rampup` | Ramp-up time in minutes. |
| **TPC-C** | `pg_duration` | Test duration in minutes. |
| **TPC-H** | `pg_scale_fact` | Scale Factor (1 = 1GB). |

### SQL Server Settings (`dbset db mssqls`)

| Component | Parameter | Description |
| :--- | :--- | :--- |
| **Connection** | `mssqls_server` | Hostname or IP of the DB server (e.g., `(local)` or `10.0.0.5`). |
| **Connection** | `mssqls_uid` | Login ID (Default: `sa`). |
| **Connection** | `mssqls_pass` | Login Password. |
| **TPC-C** | `mssqls_count_ware` | Number of Warehouses. |
| **TPC-C** | `mssqls_num_vu` | Number of Virtual Users. |
| **TPC-H** | `mssqls_scale_fact` | Scale Factor. |

## Virtual User Settings (`vuset`)

| Parameter | Value | Description |
| :--- | :--- | :--- |
| `logtotemp` | `1` | Disables GUI output and logs to temp (Critical for performance). |
| `vu` | `[int]` | Total number of Virtual Users to spawn. |
| `showoutput` | `0` or `1` | Show Virtual User output (Disable for performance). |

## Advanced: Autopilot (`ap`)

HammerDB Autopilot allows scheduling multiple runs with increasing user counts.

| Command | Example | Description |
| :--- | :--- | :--- |
| `aset pilot_enabled [1/0]` | `aset pilot_enabled 1` | Enables Autopilot mode. |
| `aset pilot_sequence` | `aset pilot_sequence "2 4 8"` | Space-separated list of VU counts to run. |

## Complete Example Sripts

### PostgreSQL TPC-C Automated Run

```tcl
#!/bin/tclsh
puts "SETTING CONFIGURATION"
dbset db pg
diset connection pg_host "localhost"
diset connection pg_port "5432"
diset tpcc pg_count_ware 100
diset tpcc pg_rampup 2
diset tpcc pg_duration 5
vuset logtotemp 1

puts "LOADING SCRIPT"
loadscript

puts "STARTING RUN"
vuset vu 10
vucreate
vurun
puts "RUN COMPLETE"
```
