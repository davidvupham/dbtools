# Linux server alerts, reports, and notifications

**🔗 [← Back to Alerts Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 19, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Platform](https://img.shields.io/badge/Platform-Linux-orange)

> [!IMPORTANT]
> **On-Call Contact:** Infrastructure On-Call (PagerDuty) | **Escalation:** Platform Engineering Team

## Table of Contents

- [Prerequisites](#prerequisites)
- [Alerts](#alerts)
- [Reports](#reports)
- [Notifications](#notifications)
- [Common diagnostic commands](#common-diagnostic-commands)
- [Useful links](#useful-links)

## Prerequisites

Before troubleshooting Linux alerts, ensure you have:

- [ ] SSH access to the target server
- [ ] Appropriate sudo permissions
- [ ] Access to monitoring dashboards (Grafana/Prometheus/Nagios)

[↑ Back to Table of Contents](#table-of-contents)

## Alerts

| Name | Severity | File |
|:---|:---|:---|
| CPU load is critical | Critical | [alert-cpu-load.md](./alert-cpu-load.md) |

[↑ Back to Table of Contents](#table-of-contents)

## Reports

| Name | Schedule | File |
|:---|:---|:---|
| *No reports documented yet* | | |

[↑ Back to Table of Contents](#table-of-contents)

## Notifications

| Name | Trigger | File |
|:---|:---|:---|
| *No notifications documented yet* | | |

[↑ Back to Table of Contents](#table-of-contents)

## Common diagnostic commands

### Check system load

```bash
# View current load averages
uptime

# View load with process info
top -bn1 | head -20
```

### Check memory usage

```bash
# View memory usage
free -h

# Detailed memory info
cat /proc/meminfo | head -10
```

### Check disk space

```bash
# View disk usage
df -h

# Find large directories
du -sh /* 2>/dev/null | sort -hr | head -10
```

### Check running processes

```bash
# View processes by CPU usage
ps aux --sort=-%cpu | head -20

# View processes by memory usage
ps aux --sort=-%mem | head -20
```

### Check network connections

```bash
# View listening ports
ss -tlnp

# View established connections
ss -tnp | grep ESTAB
```

[↑ Back to Table of Contents](#table-of-contents)

## Useful links

- [Grafana Linux dashboard](#) <!-- Update with actual link -->
- [Nagios monitoring](#) <!-- Update with actual link -->
- [Internal wiki - Linux runbooks](#) <!-- Update with actual link -->

[↑ Back to Table of Contents](#table-of-contents)
