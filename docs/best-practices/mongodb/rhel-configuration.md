# MongoDB on Red Hat Linux Best Practices

**[← Back to MongoDB Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 27, 2026
> **Maintainers:** Global Data Services
> **Status:** Draft

**Table of Contents**

- [Introduction](#introduction)
- [Operating System Configuration (RHEL)](#operating-system-configuration-rhel)
    - [Filesystem Configuration](#filesystem-configuration)
    - [Kernel and Memory Settings](#kernel-and-memory-settings)
    - [Systemd Resource Limits](#systemd-resource-limits)
    - [Network Tuning](#network-tuning)
    - [Security (SELinux & Firewall)](#security-selinux--firewall)
- [MongoDB Configuration](#mongodb-configuration)
    - [Storage Engine](#storage-engine)
    - [Security and Networking](#security-and-networking)
- [Validation](#validation)

## Introduction

This guide outlines the essential configuration parameters and best practices for operating MongoDB on Red Hat Enterprise Linux (RHEL) 8 and 9. These settings are critical for ensuring performance, stability, and security in production environments.

> [!IMPORTANT]
> The default RHEL configuration is optimized for general-purpose computing, not database workloads. Failure to tune these parameters can lead to performance degradation or service failures.

## Operating System Configuration (RHEL)

### Filesystem Configuration

MongoDB with the WiredTiger storage engine strongly recommends using **XFS**.

1.  **Use XFS:** Format the data volume as XFS.
2.  **Separate Volumes:** Isolate data (`/var/lib/mongo`) and logs (`/var/log/mongo`) on separate physical or logical volumes to prevent I/O contention.
3.  **Mount Options:** Mount XFS filesystems with `noatime` and `nodiratime` to reduce metadata I/O.

Example `/etc/fstab` entry:
```bash
/dev/mapper/data-vol  /var/lib/mongo  xfs  defaults,noatime,nodiratime  0 0
```

> **Verification:**
> Run `lsblk -f` to verify the filesystem type is `xfs`.
> Run `mount | grep /var/lib/mongo` to verify `noatime` and `nodiratime` are present.

### Kernel and Memory Settings

#### Transparent Huge Pages (THP)

Transparent Huge Pages (THP) must be **disabled** for MongoDB. THP can cause performance issues with database memory access patterns.

On RHEL 8/9, the recommended method is to use a custom `tuned` profile.

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

> **Verification:**
> Check the THP status directly:
> ```bash
> cat /sys/kernel/mm/transparent_hugepage/enabled
> # Output should be: always madvise [never]
> ```
> Verify the active tuned profile:
> ```bash
> tuned-adm active
> ```

#### Virtual Memory Settings

*   **Swappiness:** Set `vm.swappiness` to 1. This tells the kernel to avoid swapping unless absolutely necessary.
*   **Dirty Ratios:** Reduce dirty page ratios to prevent write stalls.
    *   `vm.dirty_ratio`: 15
    *   `vm.dirty_background_ratio`: 5

Add to `/etc/sysctl.d/99-mongodb.conf`:
```ini
vm.swappiness = 1
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
vm.max_map_count = 262144
```
Apply properly: `sysctl -p /etc/sysctl.d/99-mongodb.conf`

> **Verification:**
> Check current values:
> ```bash
> sysctl vm.swappiness vm.dirty_ratio vm.dirty_background_ratio vm.max_map_count
> ```

#### NUMA

If running on NUMA hardware, ensure `numactl` is installed and disable zone reclaim. Most modern MongoDB packages (RPMs) handle NUMA interleaving in their systemd service, but verification is recommended.

### Systemd Resource Limits

RHEL 8/9 uses systemd for process limits. `ulimit` commands in shell profiles (e.g., `.bashrc`) do not affect the `mongod` service.

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

> **Verification:**
> Check the effective limits of the running process:
> ```bash
> cat /proc/$(pgrep mongod)/limits | grep -E "Max open files|Max processes"
> ```

### Network Tuning

Optimize TCP settings for high throughput:

`/etc/sysctl.d/99-mongodb-net.conf`:
```ini
net.core.somaxconn = 4096
net.ipv4.tcp_keepalive_time = 120
net.ipv4.tcp_max_syn_backlog = 4096
```

> **Verification:**
> ```bash
> sysctl net.core.somaxconn net.ipv4.tcp_keepalive_time net.ipv4.tcp_max_syn_backlog
> ```

### Security (SELinux & Firewall)

*   **SELinux:** Recommended to keep in **Enforcing** mode. Ensure the `mongodb-selinux` package is installed if using official repositories, or properly manage contexts for custom data paths (`semanage fcontext -a -t mongod_var_lib_t "/custom/path(/.*)?"`).
*   **Firewall:** Use `firewalld` to restrict access. Only open port 27017 to trusted application subnets.

```bash
firewall-cmd --permanent --zone=public --add-rich-rule='rule family="ipv4" source address="10.0.0.0/24" port port="27017" protocol="tcp" accept'
firewall-cmd --reload
```

> **Verification:**
> *   **SELinux:** Run `sestatus` to confirm "Current mode: enforcing".
> *   **Firewall:** Run `firewall-cmd --list-all` to see active rules.


[Back to Table of Contents](#table-of-contents)

## MongoDB Configuration

Configuration usually resides in `/etc/mongod.conf` (YAML format).

### Storage Engine

Ensure **WiredTiger** is selected and configured.

```yaml
storage:
  dbPath: /var/lib/mongo
  journal:
    enabled: true
  wiredTiger:
    engineConfig:
      cacheSizeGB: <0.5 * RAM> # Default is 50% of RAM minus 1GB
```

> **Verification:**
> Connect to MongoDB and check the storage engine:
> ```javascript
> db.serverStatus().storageEngine
> // Should return "name" : "wiredTiger"
> ```

> [!TIP]
> Leave `cacheSizeGB` unset to use the default (50% of (RAM - 1GB)). Only tune if running other heavy processes on the same host (which is not recommended).

### Security and Networking

Network binding and authentication are critical.

```yaml
net:
  port: 27017
  bindIp: 0.0.0.0  # Listen on all interfaces, but restrict via Firewall!
  tls:
    mode: requireTLS
    certificateKeyFile: /etc/ssl/mongodb.pem

security:
  authorization: enabled
```

> [!WARNING]
> Never expose MongoDB directly to the public internet. Always use VPNs, VPC peering, or strict firewalls.


[Back to Table of Contents](#table-of-contents)

## Validation

Verify your complete configuration after a restart.

### 1. Unified Check Script
You can run this quick one-liner to dump relevant settings:

```bash
echo "=== THP ==="; cat /sys/kernel/mm/transparent_hugepage/enabled
echo "=== Limits ==="; cat /proc/$(pgrep mongod)/limits | grep -E "Max open files|Max processes"
echo "=== Swappiness ==="; sysctl vm.swappiness
echo "=== XFS ==="; lsblk -f | grep xfs
```

### 2. Log Analysis
Review `/var/log/mongodb/mongod.log` (or your configured log path) for any "WARNING" messages regarding startup parameters. MongoDB correctly monitors its own environment and will complain about THP, limits, or NUMA issues on startup.
