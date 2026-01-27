# Linux core concepts

**[← Back to Explanation Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 26, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Type](https://img.shields.io/badge/Type-Explanation-orange)

> [!NOTE]
> This document explains the mental models behind Linux. For hands-on commands, see the [Bash Productivity Reference](../../reference/linux/tools/bash/reference.md) or [Linux Essentials Tutorial](../../tutorials/systems/linux/01-essentials.md).

## Table of contents

- [Introduction](#introduction)
- [Permissions](#permissions)
- [Filesystem hierarchy](#filesystem-hierarchy)
- [Processes](#processes)
- [Services](#services)
- [Logs](#logs)
- [Networking](#networking)
- [The mental shift](#the-mental-shift)
- [Further reading](#further-reading)

## Introduction

Linux can feel hostile to beginners. You type a command, follow a tutorial exactly, and the system responds with "Permission denied" or simply... silence. The instinct is to add `sudo` or reboot and hope for the best.

The problem is not that Linux is difficult. The problem is that Linux is *different*. It does not guess your intentions or hide complexity behind dialog boxes. It follows rules precisely and expects you to understand those rules.

Once you internalize a few core concepts, Linux stops feeling like an obstacle and starts feeling like a transparent, predictable system.

[↑ Back to Table of Contents](#table-of-contents)

## Permissions

Every file and directory in Linux answers three questions:

1. **Who owns it?** (user)
2. **What group has access?** (group)
3. **What can each category do?** (read, write, execute)

### Reading permission strings

When you run `ls -l`, you see output like:

```bash
ls -l backup.sh
```

```text
-rw-r--r-- 1 dpham developers 2456 Jan 26 10:09 backup.sh
```

The permission string `-rw-r--r--` breaks down as:

| Position | Meaning |
|:---------|:--------|
| 1 | File type (`-` = file, `d` = directory, `l` = symlink) |
| 2-4 | Owner permissions (read, write, execute) |
| 5-7 | Group permissions |
| 8-10 | Others (everyone else) |

In this example:
- **Owner (dpham)**: `rw-` = read and write, no execute
- **Group (developers)**: `r--` = read only
- **Others**: `r--` = read only

### Why "permission denied" happens

If you try to run a script:

```bash
./backup.sh
# bash: ./backup.sh: Permission denied
```

The issue is not that Linux is blocking you. The file lacks execute permission. Check with `ls -l` and you will see no `x` in the owner permissions.

### The solution: chmod

Add execute permission for the owner:

```bash
chmod u+x backup.sh
./backup.sh
# Now it runs
```

Understanding the syntax:
- `u` = user (owner), `g` = group, `o` = others, `a` = all
- `+` = add, `-` = remove, `=` = set exactly
- `r` = read, `w` = write, `x` = execute

### Numeric (octal) permissions

You will often see permissions expressed as numbers like `755` or `644`:

| Number | Permission |
|:-------|:-----------|
| 4 | read |
| 2 | write |
| 1 | execute |
| 0 | none |

Add them together for each category:
- `7` = 4+2+1 = read + write + execute
- `5` = 4+0+1 = read + execute
- `4` = 4+0+0 = read only

```bash
chmod 755 backup.sh  # rwxr-xr-x (owner can do everything, others can read/execute)
chmod 644 config.yml # rw-r--r-- (owner can read/write, others read only)
```

### When to use sudo

Use `sudo` when you need to:
- Modify files owned by root (system configuration in `/etc`)
- Install packages system-wide
- Manage system services
- Access protected directories

Do NOT use `sudo` just because something failed. First understand *why* it failed. Running scripts with `sudo` when they do not need it creates files owned by root in your home directory, leading to more permission problems.

> [!WARNING]
> Adding `sudo` without understanding the cause often creates bigger problems. If a script fails with "permission denied," check file ownership and permissions first.

[↑ Back to Table of Contents](#table-of-contents)

## Filesystem hierarchy

Coming from Windows, the first question is often "Where did my program install to?" Linux does not have a `C:\Program Files` equivalent. Instead, it distributes components by *purpose*.

### Standard directories

| Directory | Purpose | Example contents |
|:----------|:--------|:-----------------|
| `/` | Root of the filesystem | Everything branches from here |
| `/etc` | System configuration | `nginx.conf`, `ssh/sshd_config` |
| `/var/log` | Log files | `syslog`, `nginx/access.log` |
| `/home` | User home directories | `/home/dpham/.bashrc` |
| `/bin`, `/usr/bin` | User executables | `ls`, `grep`, `python` |
| `/sbin`, `/usr/sbin` | System executables | `systemctl`, `fdisk` |
| `/opt` | Optional/third-party software | Vendor packages |
| `/tmp` | Temporary files | Cleared on reboot |
| `/var` | Variable data | Databases, mail spools, caches |
| `/proc` | Virtual filesystem for processes | `/proc/cpuinfo`, `/proc/meminfo` |
| `/sys` | Virtual filesystem for hardware | Device information |

### Finding things

When you install software, it spreads across multiple directories:
- Binary goes to `/usr/bin/`
- Configuration goes to `/etc/`
- Logs go to `/var/log/`
- Data goes to `/var/lib/`

This seems chaotic at first, but the benefit is consistency: you always know where to look for configuration files (`/etc`), always know where to find logs (`/var/log`).

### Practical commands

```bash
# Find where a command lives
which nginx
# /usr/sbin/nginx

# Find all files related to a package
whereis nginx
# nginx: /usr/sbin/nginx /etc/nginx /usr/share/nginx

# Search for files by name
find /etc -name "*.conf" 2>/dev/null
```

[↑ Back to Table of Contents](#table-of-contents)

## Processes

When your system feels slow, the instinct is to reboot. In Linux, you can see exactly what is consuming resources and address it directly.

### Viewing processes

The `top` command shows a live view of system activity:

```bash
top
```

Key columns:
- **PID**: Process ID (unique identifier)
- **USER**: Who owns the process
- **%CPU**: CPU usage
- **%MEM**: Memory usage
- **COMMAND**: What program is running

Press `q` to quit, `k` to kill a process, `M` to sort by memory.

### Finding specific processes

```bash
# Find all Java processes
ps aux | grep java

# Better: use pgrep
pgrep -a java

# Find what is using port 8080
lsof -i :8080
```

### Killing processes

```bash
# Graceful termination (SIGTERM)
kill 12345

# Force kill (SIGKILL) - use only when necessary
kill -9 12345

# Kill by name
pkill nginx
```

### Modern alternative: htop

`htop` provides a more visual, interactive experience:

```bash
htop
```

Use arrow keys to navigate, `F9` to kill, `F6` to sort.

> [!TIP]
> Install `htop` for a better process monitoring experience: `apt install htop` (Debian/Ubuntu) or `dnf install htop` (RHEL/Fedora).

[↑ Back to Table of Contents](#table-of-contents)

## Services

A service (or daemon) is a program that runs in the background. Your web server, database, and SSH server are all services. When something "stops working," it is often a stopped service.

### systemd and systemctl

Modern Linux distributions (RHEL 7+, Ubuntu 16.04+, Debian 8+) use systemd for service management. The command is `systemctl`.

### Checking service status

```bash
systemctl status nginx
```

This tells you:
- Whether the service is running or stopped
- When it started
- Recent log entries
- The process ID

### Common operations

```bash
# Start a service
sudo systemctl start nginx

# Stop a service
sudo systemctl stop nginx

# Restart (stop then start)
sudo systemctl restart nginx

# Reload configuration without stopping
sudo systemctl reload nginx

# Enable service to start on boot
sudo systemctl enable nginx

# Disable service from starting on boot
sudo systemctl disable nginx
```

### Debugging service failures

When a service will not start:

```bash
# Check status for error messages
systemctl status nginx

# View full logs for the service
journalctl -u nginx

# View logs since last boot
journalctl -u nginx -b

# Follow logs in real time
journalctl -u nginx -f
```

The answer to "why did it break?" is almost always in the logs.

[↑ Back to Table of Contents](#table-of-contents)

## Logs

Linux does not pop up error dialogs. Instead, every crash, warning, and error is recorded in logs. Learning to read logs is learning to debug Linux.

### Where logs live

| Log type | Location | Command |
|:---------|:---------|:--------|
| System journal (systemd) | Binary format | `journalctl` |
| Traditional syslog | `/var/log/syslog` or `/var/log/messages` | `less /var/log/syslog` |
| Application-specific | `/var/log/<app>/` | Varies by application |
| Kernel messages | `dmesg` | `dmesg` |

### journalctl essentials

```bash
# View recent logs
journalctl -xe

# Follow logs in real time (like tail -f)
journalctl -f

# Logs for a specific service
journalctl -u nginx

# Logs since a specific time
journalctl --since "2026-01-26 10:00:00"

# Logs from last boot
journalctl -b

# Logs from previous boot (useful after crashes)
journalctl -b -1
```

### Traditional log files

```bash
# Follow a log file in real time
tail -f /var/log/syslog

# View last 100 lines
tail -n 100 /var/log/nginx/error.log

# Search logs for errors
grep -i error /var/log/syslog

# Search compressed rotated logs
zgrep -i error /var/log/syslog.1.gz
```

### Log rotation

Logs are automatically rotated (compressed and archived) by `logrotate` to prevent disk exhaustion. Configuration lives in `/etc/logrotate.conf` and `/etc/logrotate.d/`.

> [!TIP]
> When debugging, check both `journalctl -u <service>` and any application-specific logs in `/var/log/`. Some applications write to both.

[↑ Back to Table of Contents](#table-of-contents)

## Networking

"It works on my machine" is often a networking problem. The service is running, the port is open, but something blocks the connection.

### Diagnostic workflow

1. **Check if the service is listening**
2. **Check if you can reach the port locally**
3. **Check the firewall**
4. **Check external connectivity**

### Check listening ports

```bash
# Show all listening TCP/UDP ports
ss -tuln

# Older alternative (still common)
netstat -tuln
```

Output explanation:
- `t` = TCP, `u` = UDP
- `l` = listening
- `n` = numeric (show port numbers, not service names)

Look for your service's port in the output:
```text
LISTEN  0  128  0.0.0.0:22    0.0.0.0:*   # SSH listening on all interfaces
LISTEN  0  511  127.0.0.1:80  0.0.0.0:*   # HTTP listening only on localhost
```

If the service binds to `127.0.0.1`, it only accepts local connections.

### Check network interfaces

```bash
# Modern command
ip a

# Shows IP addresses for each interface
# Look for inet (IPv4) and inet6 (IPv6) addresses
```

### Test connectivity

```bash
# Test basic connectivity
ping google.com

# Test if a specific port is reachable
nc -zv hostname 443

# Test HTTP endpoint
curl -I https://example.com
```

### Firewall commands

Different distributions use different firewall tools:

**RHEL/CentOS/Fedora (firewalld):**
```bash
# Check firewall status
sudo firewall-cmd --state

# List allowed services and ports
sudo firewall-cmd --list-all

# Allow a port
sudo firewall-cmd --add-port=8080/tcp --permanent
sudo firewall-cmd --reload
```

**Ubuntu/Debian (ufw):**
```bash
# Check firewall status
sudo ufw status

# Allow a port
sudo ufw allow 8080/tcp
```

> [!IMPORTANT]
> If a service is running but unreachable from outside, check the firewall first. It is the most common cause of "connection refused" errors on servers.

[↑ Back to Table of Contents](#table-of-contents)

## The mental shift

Linux is not difficult. Linux is *honest*.

It does not assume what you want. It does not guess. It does not hide information to protect you from complexity.

When something fails, Linux tells you exactly why - you just need to know where to look:

| Symptom | First step |
|:--------|:-----------|
| Permission denied | `ls -l` to check permissions |
| Command not found | `which <command>` or check PATH |
| Service won't start | `systemctl status <service>` |
| Connection refused | `ss -tuln` to check if listening |
| Something broke | `journalctl -xe` or check `/var/log/` |

The transition from "Linux is fighting me" to "Linux is informing me" happens when you:

1. **Stop guessing** - Check before assuming
2. **Read error messages** - They usually tell you exactly what went wrong
3. **Check logs** - The answer is almost always recorded
4. **Understand the model** - Permissions, services, and networking follow predictable rules

Once you understand the rules, Linux becomes a transparent system where problems are solvable, not mysterious.

[↑ Back to Table of Contents](#table-of-contents)

## Further reading

### Internal documentation

- [Bash Productivity Reference](../../reference/linux/tools/bash/reference.md) - Shell shortcuts and tips
- [Linux Essentials Tutorial](../../tutorials/systems/linux/01-essentials.md) - Basic commands
- [Screen Reference](../../reference/linux/tools/screen/reference.md) - Terminal multiplexer
- [Tmux Reference](../../reference/linux/tools/tmux/reference.md) - Alternative terminal multiplexer

### External resources

- [Linux Filesystem Hierarchy Standard](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html) - Official FHS documentation
- [systemd Documentation](https://www.freedesktop.org/wiki/Software/systemd/) - Service management
- [Arch Wiki](https://wiki.archlinux.org/) - Detailed Linux documentation (applies to most distributions)

[↑ Back to Table of Contents](#table-of-contents)
