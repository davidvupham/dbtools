# MongoDB instance configuration

**[← Back to MongoDB Index](./README.md)**

> **Document Version:** 1.1
> **Last Updated:** January 27, 2026
> **Maintainers:** Global Data Services
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Topic](https://img.shields.io/badge/Topic-MongoDB-green)

> [!IMPORTANT]
> **Related Docs:** [RHEL Configuration](./rhel-configuration.md) | [Storage Engine](./storage-engine.md) | [Replica Set Architecture](./replica-set-architecture.md)

## Table of contents

- [Introduction](#introduction)
- [Logging](#logging)
- [Auditing](#auditing)
- [Process management](#process-management)
- [Network and connections](#network-and-connections)
- [Verification](#verification)

## Introduction

This guide covers the essential `mongod` instance configuration settings for logging, auditing, and process management. These settings ensure your database is observable, secure, and manageable by standard system tools.

[↑ Back to Table of Contents](#table-of-contents)

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
*   **logAppend:** Set to `true` to append to the existing log file on restart rather than overwriting.
*   **logRotate:** Set to `reopen` to allow external tools like `logrotate` to manage files without restarting the daemon. The alternative value `rename` (the default) causes MongoDB to rename the log file itself by appending a timestamp, then open a new file.

> [!TIP]
> Use `logRotate: reopen` and configure Linux `logrotate` to handle compression and retention. This prevents the MongoDB process from handling heavy file I/O during rotation. When using `reopen`, the external process must rename the file before sending the rotation signal.

**Official Reference:** [Configure log rotation](https://www.mongodb.com/docs/manual/tutorial/rotate-log-files/)

[↑ Back to Table of Contents](#table-of-contents)

## Auditing

Auditing is critical for security compliance. It tracks system activity such as schema changes, authentication attempts, and user management.

> [!NOTE]
> Auditing is an **Enterprise-only** feature. It is available in MongoDB Enterprise and MongoDB Atlas, but not in Community Edition.

### Configuration

```yaml
security:
  authorization: enabled

auditLog:
  destination: file
  format: JSON
  path: /var/log/mongodb/audit.json
  filter: '{ "atype": { "$in": [ "createUser", "dropUser", "dropDatabase" ] } }'
```

*   **format:** JSON is preferred for parsing by log aggregation tools.
*   **filter:** Explicitly define what to log to avoid performance degradation. Use the `$in` operator (with the `$` prefix) in filter expressions.

> [!WARNING]
> Enabling auditing without a filter can generate massive log volumes and impact throughput. Start with administrative actions only.

> [!TIP]
> **MongoDB 5.0+:** You can reconfigure audit filters at runtime without restarting `mongod` or `mongos` by using the `auditConfig` cluster parameter. This enables audit/admin access separation.
>
> **MongoDB 8.0+:** The `auditLog.schema` option supports Open Cybersecurity Schema Framework (OCSF) format, providing standardized audit log output compatible with modern log processors.

**Official Reference:** [Configure auditing](https://www.mongodb.com/docs/manual/tutorial/configure-auditing/)

[↑ Back to Table of Contents](#table-of-contents)

## Process management

Ensure MongoDB integrates cleanly with `systemd` and standard Linux process management.

### Configuration

```yaml
processManagement:
  pidFilePath: /var/run/mongodb/mongod.pid
  timeZoneInfo: /usr/share/zoneinfo
```

> [!WARNING]
> **Do not set `processManagement.fork`** when running MongoDB under systemd (the RHEL standard). The official MongoDB Linux packages do not expect this value to change from its default. If you modify `fork`, you must provide your own init scripts and disable the built-in service scripts.

> [!TIP]
> If you need MongoDB to run in the background outside of systemd, set the environment variable `MONGODB_CONFIG_OVERRIDE_NOFORK=true` instead of using the `fork` option.

**Official Reference:** [processManagement options](https://www.mongodb.com/docs/manual/reference/configuration-options/#process-management-options)

[↑ Back to Table of Contents](#table-of-contents)

## Network and connections

Protect your database from connection storms and ensure timeouts are reasonable.

### Configuration

```yaml
net:
  port: 27017
  bindIp: 0.0.0.0
  maxIncomingConnections: 65536
```

*   **bindIp:** The default binds to `localhost` only. Setting `0.0.0.0` listens on all IPv4 interfaces. Always enable authentication and use firewalls before binding to non-localhost addresses.
*   **maxIncomingConnections:** Default is `65536`. On Linux, the effective limit is constrained to `(RLIMIT_NOFILE / 2) * 0.8`. Ensure your systemd `LimitNOFILE` is set appropriately (see [RHEL Configuration](./rhel-configuration.md)).

> [!CAUTION]
> Never expose MongoDB directly to the public internet. Always use VPNs, VPC peering, or strict firewalls. Bind only to private or internal network interfaces.

**Official Reference:** [net options](https://www.mongodb.com/docs/manual/reference/configuration-options/#net-options) | [IP binding](https://www.mongodb.com/docs/manual/core/security-mongodb-configuration/)

[↑ Back to Table of Contents](#table-of-contents)

## Verification

### Check log rotation

Force a log rotation to verify configuration:
```javascript
db.adminCommand( { logRotate : 1 } )
```
Check if the log file was reopened or renamed in `/var/log/mongodb/`.

### Check audit logs

Perform an audited action (for example, create a test user) and search the audit log:
```bash
grep "createUser" /var/log/mongodb/audit.json
```

[↑ Back to Table of Contents](#table-of-contents)
