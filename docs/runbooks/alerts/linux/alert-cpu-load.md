# Alert: CPU load is critical

**🔗 [← Back to Linux Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 19, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Severity](https://img.shields.io/badge/Severity-Critical-red)

> [!IMPORTANT]
> **Related Docs:** [Linux Index](./README.md) | [Alerts Index](../README.md)

## Table of Contents

- [Summary](#summary)
- [Description](#description)
- [Impact](#impact)
- [Troubleshooting steps](#troubleshooting-steps)
- [Common causes](#common-causes)
- [Post-recovery verification](#post-recovery-verification)
- [Related alerts](#related-alerts)
- [Additional resources](#additional-resources)

## Summary

| Attribute | Value |
|:---|:---|
| **Type** | Alert |
| **Severity** | Critical |
| **Source** | Nagios / Prometheus |
| **Delivery** | Email |
| **Threshold** | Load average > CPU count for 5 minutes |

[↑ Back to Table of Contents](#table-of-contents)

## Description

This alert fires when the system load average exceeds the number of CPU cores for more than 5 consecutive minutes. High CPU load indicates the system is overloaded and processes are waiting for CPU time.

[↑ Back to Table of Contents](#table-of-contents)

## Impact

- Application response times increase
- Scheduled jobs may timeout or fail
- SSH connections may be slow or unresponsive
- Database queries running on this host may timeout

[↑ Back to Table of Contents](#table-of-contents)

## Troubleshooting steps

### 1. Connect to the server

```bash
ssh admin@<server-hostname>
```

### 2. Check current load and CPU count

```bash
# View load averages (1, 5, 15 minute)
uptime

# Check number of CPU cores
nproc

# Example: load of 8.5 on a 4-core system is overloaded
```

### 3. Identify high CPU processes

```bash
# View top processes by CPU usage
top -bn1 -o %CPU | head -20

# Alternative: ps sorted by CPU
ps aux --sort=-%cpu | head -15
```

### 4. Check for runaway processes

```bash
# Find processes using more than 50% CPU
ps aux | awk '$3 > 50 {print $0}'

# Check process details
ps -p <PID> -o pid,ppid,cmd,%cpu,%mem,etime
```

### 5. Check for zombie processes

```bash
# Count zombie processes
ps aux | grep -c Z

# List zombie processes
ps aux | awk '$8 ~ /Z/ {print $0}'
```

### 6. Review recent cron jobs

```bash
# Check cron logs
grep CRON /var/log/syslog | tail -50

# List scheduled cron jobs
crontab -l
cat /etc/crontab
```

### 7. Kill problematic process if needed

> [!WARNING]
> Only kill processes after confirming with the application team. Document the process details before terminating.

```bash
# Graceful termination
kill <PID>

# Force kill if unresponsive
kill -9 <PID>
```

### 8. Verify resolution

```bash
# Monitor load for a few minutes
watch -n 5 uptime
```

[↑ Back to Table of Contents](#table-of-contents)

## Common causes

| Cause | Resolution |
|:---|:---|
| Runaway application process | Kill process, investigate root cause |
| Too many concurrent jobs | Stagger cron job schedules |
| Resource-intensive backup | Schedule backups during off-peak hours |
| Memory pressure causing swap | Add memory or reduce workload |
| Malware/crypto mining | Investigate and remove malicious processes |
| Insufficient CPU for workload | Scale up or distribute load |

[↑ Back to Table of Contents](#table-of-contents)

## Post-recovery verification

1. Verify load has returned to normal:

   ```bash
   uptime
   # Load should be below CPU count
   ```

2. Check application health
3. Verify scheduled jobs are running normally
4. Review logs for any errors during high load period

[↑ Back to Table of Contents](#table-of-contents)

## Related alerts

- [Memory usage critical](#) <!-- Add link when created -->
- [Disk space low](#) <!-- Add link when created -->

[↑ Back to Table of Contents](#table-of-contents)

## Additional resources

- [Linux Performance Analysis](https://www.brendangregg.com/linuxperf.html)
- [Understanding Linux Load Averages](https://www.brendangregg.com/blog/2017-08-08/linux-load-averages.html)

[↑ Back to Table of Contents](#table-of-contents)
