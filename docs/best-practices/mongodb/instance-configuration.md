# MongoDB Instance Configuration

**[← Back to MongoDB Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 27, 2026
> **Maintainers:** Database Reliability Engineering
> **Status:** Draft

**Table of Contents**

- [Introduction](#introduction)
- [Logging](#logging)
- [Auditing](#auditing)
- [Process Management](#process-management)
- [Network and Connections](#network-and-connections)
- [Verification](#verification)

## Introduction

This guide covers the essential `mongod` instance configuration settings for logging, auditing, and process management. These settings ensure your database is observable, secure, and manageable by standard system tools.

## Logging

MongoDB supports structured JSON logging, which is recommended for modern observability stacks.

### Configuration
```yaml
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log
  logRotate: reopen
```

*   **destination:** Always use `file` for production.
*   **logRotate:** Set to `reopen` to allow external tools like `logrotate` to manage files without restarting the daemon.

> [!TIP]
> Use `logRotate: reopen` and configure Linux `logrotate` to handle compression and retention. This prevents the MongoDB process from handling heavy file I/O during rotation.

**Official Reference:** [Configure Log Rotation](https://www.mongodb.com/docs/manual/tutorial/rotate-log-files/)

## Auditing

Auditing is critical for security compliance. It tracks system activity such as schema changes, authentication attempts, and user management.

### Configuration
```yaml
security:
  authorization: enabled

auditLog:
  destination: file
  format: JSON
  path: /var/log/mongodb/audit.json
  filter: '{ "atype": { $in: [ "createUser", "dropUser", "dropDatabase" ] } }'
```

*   **format:** JSON is preferred for parsing.
*   **filter:** Explicitly define what to log to avoid performance degradation.

> [!WARNING]
> Enabling auditing without a filter can generate massive log volumes and impact throughput. Start with administrative actions only.

**Official Reference:** [Configure Auditing](https://www.mongodb.com/docs/manual/tutorial/configure-auditing/)

## Process Management

Ensure MongoDB integrates cleanly with `systemd` and standard Linux process management.

### Configuration
```yaml
processManagement:
  fork: true  # Set to false if managed by systemd with Type=notify/simple
  pidFilePath: /var/run/mongodb/mongod.pid
  timeZoneInfo: /usr/share/zoneinfo
```

> [!NOTE]
> If using `systemd` (RHEL standard), `fork` is often managed by the service file type. If `Type=forking`, set `fork: true`. If `Type=simple`, set `fork: false`.

**Official Reference:** [processManagement Options](https://www.mongodb.com/docs/manual/reference/configuration-options/#process-management-options)

## Network and Connections

Protect your database from connection storms and ensure timeouts are reasonable.

### Configuration
```yaml
net:
  port: 27017
  bindIp: 0.0.0.0
  maxIncomingConnections: 65536
```

**Official Reference:** [net Options](https://www.mongodb.com/docs/manual/reference/configuration-options/#net-options)

## Verification

### Check Log Rotation
Force a log rotation to verify configuration:
```javascript
db.adminCommand( { logRotate : 1 } )
```
Check if the log file was reopened/renamed in `/var/log/mongodb/`.

### Check Audit Logs
Perform an audited action (e.g., create a test user) and grep the audit log:
```bash
grep "createUser" /var/log/mongodb/audit.json
```
