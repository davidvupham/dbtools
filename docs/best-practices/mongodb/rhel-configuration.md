# MongoDB on RHEL best practices

**[← Back to MongoDB Index](./README.md)**

> **Document Version:** 1.1
> **Last Updated:** January 27, 2026
> **Maintainers:** Global Data Services
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Topic](https://img.shields.io/badge/Topic-MongoDB-green)

> [!IMPORTANT]
> **Related Docs:** [Instance Configuration](./instance-configuration.md) | [Storage Engine](./storage-engine.md) | [Replica Set Architecture](./replica-set-architecture.md)

## Table of contents

- [Introduction](#introduction)
- [Operating system configuration (RHEL)](#operating-system-configuration-rhel)
    - [Filesystem configuration](#filesystem-configuration)
    - [Kernel and memory settings](#kernel-and-memory-settings)
    - [Systemd resource limits](#systemd-resource-limits)
    - [Network tuning](#network-tuning)
    - [Security (SELinux and firewall)](#security-selinux-and-firewall)
- [MongoDB configuration](#mongodb-configuration)
    - [Storage engine](#storage-engine)
    - [Security and networking](#security-and-networking)
- [Validation](#validation)

## Introduction

This guide outlines the essential configuration parameters and best practices for operating MongoDB on Red Hat Enterprise Linux (RHEL) 8 and 9. These settings are critical for ensuring performance, stability, and security in production environments.

> [!IMPORTANT]
> The default RHEL configuration is optimized for general-purpose computing, not database workloads. Failure to tune these parameters can lead to performance degradation or service failures.

[↑ Back to Table of Contents](#table-of-contents)

## Operating system configuration (RHEL)

### Filesystem configuration

MongoDB with the WiredTiger storage engine strongly recommends using **XFS**. The official documentation states that EXT4 can cause performance issues with WiredTiger.

1.  **Use XFS:** Format the data volume as XFS.
2.  **Separate volumes:** Isolate data (`/var/lib/mongo`) and logs (`/var/log/mongo`) on separate physical or logical volumes to prevent I/O contention.
3.  **Mount options:** Mount XFS filesystems with `noatime` and `nodiratime` to reduce metadata I/O.

Example `/etc/fstab` entry:
```bash
/dev/mapper/data-vol  /var/lib/mongo  xfs  defaults,noatime,nodiratime  0 0
```

> [!TIP]
> **Verification:** Run `lsblk -f` to verify the filesystem type is `xfs`. Run `mount | grep /var/lib/mongo` to verify `noatime` and `nodiratime` are present.

**Official Reference:** [Production notes — filesystem](https://www.mongodb.com/docs/manual/administration/production-notes/#kernel-and-file-systems)

[↑ Back to Table of Contents](#table-of-contents)

### Kernel and memory settings

#### Transparent Huge Pages (THP)

The Transparent Huge Pages (THP) recommendation depends on your MongoDB version:

| MongoDB version | THP recommendation | Reason |
| :--- | :--- | :--- |
| **8.0 and later** | **Enable** | Updated TCMalloc benefits from THP. |
| **7.0 and earlier** | **Disable** | THP causes performance issues with database memory access patterns. |

> [!WARNING]
> **Exceptions for MongoDB 8.0:** RHEL 8 / Oracle 8 on PPC64LE and s390x, and RHEL 9 / CentOS 9 / Oracle 9 on PPC64LE still use legacy TCMalloc and should **disable** THP even on 8.0.

**For MongoDB 7.0 and earlier** on RHEL 8/9, the recommended method is to use a custom `tuned` profile:

1.  Create a custom profile directory:
    ```bash
    mkdir /etc/tuned/no-thp
    ```
2.  Create `/etc/tuned/no-thp/tuned.conf`:
    ```ini
    [main]
    include=throughput-performance

    [vm]
    transparent_hugepages=never
    ```
3.  Activate the profile:
    ```bash
    tuned-adm profile no-thp
    ```

> [!TIP]
> **Verification:** Check the THP status directly:
> ```bash
> cat /sys/kernel/mm/transparent_hugepage/enabled
> # MongoDB 7.0 and earlier: Output should be: always madvise [never]
> # MongoDB 8.0 and later: Output should be: [always] madvise never
> ```
> Verify the active tuned profile: `tuned-adm active`

**Official Reference:** [Transparent Huge Pages](https://www.mongodb.com/docs/manual/tutorial/transparent-huge-pages/)

#### Virtual memory settings

*   **Swappiness:** Set `vm.swappiness` to `1`. This tells the kernel to avoid swapping unless absolutely necessary. A value of `0` can trigger the OOM killer more aggressively on some kernels, so `1` is the safer choice.
*   **Dirty ratios:** Reduce dirty page ratios to prevent write stalls on large-memory servers (64 GB+).
    *   `vm.dirty_ratio`: `15` (default is 20-30%)
    *   `vm.dirty_background_ratio`: `5` (default is 10-15%)
*   **Max map count:** Set `vm.max_map_count` to at least `128000`. The value should be at least 2x your maximum expected connections.

Add to `/etc/sysctl.d/99-mongodb.conf`:
```ini
vm.swappiness = 1
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
vm.max_map_count = 128000
```
Apply: `sysctl -p /etc/sysctl.d/99-mongodb.conf`

> [!TIP]
> **Verification:** Check current values:
> ```bash
> sysctl vm.swappiness vm.dirty_ratio vm.dirty_background_ratio vm.max_map_count
> ```

**Official Reference:** [Production notes](https://www.mongodb.com/docs/manual/administration/production-notes/)

#### NUMA

If running on Non-Uniform Memory Access (NUMA) hardware, you must configure **both** of the following. Performing only one is insufficient:

1.  **Disable zone reclaim:** Set `vm.zone_reclaim_mode` to `0` in `/etc/sysctl.d/99-mongodb.conf`.
2.  **Use memory interleaving:** Start `mongod` with `numactl --interleave=all`, or verify that the official MongoDB RPM systemd service file handles NUMA interleaving automatically.

> [!WARNING]
> Running MongoDB on NUMA hardware without these settings can cause slow performance for extended periods and high system process usage. MongoDB checks NUMA settings on startup and logs a warning if misconfigured.

**Official Reference:** [Production notes — NUMA](https://www.mongodb.com/docs/manual/administration/production-notes/#configuring-numa-on-linux)

[↑ Back to Table of Contents](#table-of-contents)

### Systemd resource limits

RHEL 8/9 uses systemd for process limits. `ulimit` commands in shell profiles (for example, `.bashrc`) do not affect the `mongod` service.

Create a drop-in override for the service:
```bash
systemctl edit mongod
```

Add the following configuration:
```ini
[Service]
# File descriptors
LimitNOFILE=64000
# Processes/Threads
LimitNPROC=64000
```
Reload systemd: `systemctl daemon-reload && systemctl restart mongod`.

> [!NOTE]
> MongoDB generates a **startup warning** if the ulimit for open files is under 64000. Each systemd limit directive sets both the "hard" and "soft" limits to the specified value.

> [!TIP]
> **Verification:** Check the effective limits of the running process:
> ```bash
> cat /proc/$(pgrep mongod)/limits | grep -E "Max open files|Max processes"
> ```

For large systems, also configure these kernel parameters in `/etc/sysctl.d/99-mongodb.conf`:
```ini
fs.file-max = 98000
kernel.pid_max = 64000
kernel.threads-max = 64000
```

**Official Reference:** [UNIX ulimit settings](https://www.mongodb.com/docs/manual/reference/ulimit/) | [Operations checklist](https://www.mongodb.com/docs/manual/administration/production-checklist-operations/)

[↑ Back to Table of Contents](#table-of-contents)

### Network tuning

Optimize TCP settings for high throughput and replica set health.

Add to `/etc/sysctl.d/99-mongodb-net.conf`:
```ini
net.core.somaxconn = 65535
net.ipv4.tcp_keepalive_time = 120
net.ipv4.tcp_max_syn_backlog = 4096
```

*   **somaxconn:** Increase from the default of `128` to handle connection bursts.
*   **tcp_keepalive_time:** MongoDB recommends a value of `120` seconds. Keepalive values at or above 600,000 milliseconds (10 minutes) are ignored by `mongod` and `mongos`.

> [!TIP]
> **Verification:**
> ```bash
> sysctl net.core.somaxconn net.ipv4.tcp_keepalive_time net.ipv4.tcp_max_syn_backlog
> ```

**Official Reference:** [Production notes — TCP keepalive](https://www.mongodb.com/docs/manual/administration/production-notes/)

[↑ Back to Table of Contents](#table-of-contents)

### Security (SELinux and firewall)

*   **SELinux:** Keep in **Enforcing** mode. Ensure the `mongodb-selinux` package is installed if using official repositories (available since MongoDB 5.0 for RHEL 7+). For custom data paths, manage contexts manually:
    ```bash
    semanage fcontext -a -t mongod_var_lib_t "/custom/path(/.*)?"
    restorecon -Rv /custom/path
    ```

*   **Firewall:** Use `firewalld` to restrict access. Only open port 27017 to trusted application subnets.
    ```bash
    firewall-cmd --permanent --zone=public --add-rich-rule='rule family="ipv4" source address="10.0.0.0/24" port port="27017" protocol="tcp" accept'
    firewall-cmd --reload
    ```

> [!TIP]
> **Verification:**
> *   **SELinux:** Run `sestatus` to confirm "Current mode: enforcing".
> *   **Firewall:** Run `firewall-cmd --list-all` to see active rules.

**Official Reference:** [Install MongoDB on Red Hat](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-enterprise-on-red-hat/)

[↑ Back to Table of Contents](#table-of-contents)

## MongoDB configuration

Configuration usually resides in `/etc/mongod.conf` (YAML format).

### Storage engine

Ensure **WiredTiger** is selected and configured. See the [Storage Engine guide](./storage-engine.md) for detailed tuning.

```yaml
storage:
  dbPath: /var/lib/mongo
  journal:
    enabled: true
  wiredTiger:
    engineConfig:
      cacheSizeGB: <calculated>  # Default: 50% of (RAM - 1GB), minimum 256 MB
```

> [!TIP]
> **Verification:** Connect to MongoDB and check the storage engine:
> ```javascript
> db.serverStatus().storageEngine
> // Should return "name" : "wiredTiger"
> ```

> [!NOTE]
> Leave `cacheSizeGB` unset to use the default formula: `max(0.5 * (RAM - 1GB), 256 MB)`. Only tune if running other heavy processes on the same host (which is not recommended) or in containerized environments. See [Storage Engine](./storage-engine.md) for container guidance.

### Security and networking

Network binding and authentication are critical.

```yaml
net:
  port: 27017
  bindIp: 0.0.0.0  # Listen on all interfaces, but restrict via firewall
  tls:
    mode: requireTLS
    certificateKeyFile: /etc/ssl/mongodb.pem

security:
  authorization: enabled
```

> [!WARNING]
> Never expose MongoDB directly to the public internet. Always use VPNs, VPC peering, or strict firewalls. The default `bindIp` is `localhost` only — binding to `0.0.0.0` requires authentication and firewall hardening.

**Official Reference:** [IP binding](https://www.mongodb.com/docs/manual/core/security-mongodb-configuration/) | [TLS/SSL configuration](https://www.mongodb.com/docs/manual/tutorial/configure-ssl/)

[↑ Back to Table of Contents](#table-of-contents)

## Validation

Verify your complete configuration after a restart.

### 1. Unified check script

Run this script to dump relevant settings:

```bash
echo "=== THP ==="; cat /sys/kernel/mm/transparent_hugepage/enabled
echo "=== Limits ==="; cat /proc/$(pgrep mongod)/limits | grep -E "Max open files|Max processes"
echo "=== Swappiness ==="; sysctl vm.swappiness
echo "=== XFS ==="; lsblk -f | grep xfs
echo "=== NUMA ==="; sysctl vm.zone_reclaim_mode
echo "=== Max Map Count ==="; sysctl vm.max_map_count
```

### 2. Log analysis

Review `/var/log/mongodb/mongod.log` (or your configured log path) for any "WARNING" messages regarding startup parameters. MongoDB monitors its own environment and logs warnings about THP, limits, or NUMA issues on startup.

[↑ Back to Table of Contents](#table-of-contents)
