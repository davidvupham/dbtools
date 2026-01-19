# Notification: Maintenance window starting

**🔗 [← Back to SQL Server Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 19, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Type](https://img.shields.io/badge/Type-Notification-green)

> [!IMPORTANT]
> **Related Docs:** [Backup job is running](./notification-backup-job-running.md) | [SQL Server Index](./README.md)

## Table of Contents

- [Summary](#summary)
- [Description](#description)
- [Notification contents](#notification-contents)
- [Actions required](#actions-required)
- [During the maintenance window](#during-the-maintenance-window)
- [After maintenance completes](#after-maintenance-completes)
- [Related notifications](#related-notifications)
- [Additional resources](#additional-resources)

## Summary

| Attribute | Value |
|:---|:---|
| **Type** | Notification |
| **Severity** | Info |
| **Source** | Scheduled Automation |
| **Delivery** | Email |
| **Trigger** | 30 minutes before maintenance window |

[↑ Back to Table of Contents](#table-of-contents)

## Description

Informational notification sent 30 minutes before a scheduled maintenance window begins. This is a heads-up only; no action is required unless you need to delay or cancel maintenance.

[↑ Back to Table of Contents](#table-of-contents)

## Notification contents

The notification includes:

| Field | Description |
|:---|:---|
| Maintenance window start | Scheduled start time (UTC) |
| Expected duration | Estimated time to complete |
| Affected servers | List of database servers in scope |
| Affected databases | List of databases in scope |
| Change ticket | Reference to change management ticket |
| Maintenance type | Patching, upgrade, configuration change, etc. |
| Contact | On-call engineer performing maintenance |

[↑ Back to Table of Contents](#table-of-contents)

## Actions required

| Scenario | Action |
|:---|:---|
| Proceed as planned | No action required |
| Need to delay maintenance | Reply to notification with reason, contact on-call engineer |
| Need to cancel maintenance | Contact on-call engineer immediately, update change ticket |
| Questions about impact | Contact on-call engineer listed in notification |

[↑ Back to Table of Contents](#table-of-contents)

## During the maintenance window

### What to expect

- Brief connection interruptions during failovers
- Possible increased latency during index rebuilds
- Monitoring alerts may fire temporarily (acknowledged by on-call)

### If you experience issues

1. Check the maintenance status in the change ticket
2. Contact the on-call engineer listed in the notification
3. Do not attempt to restart services unless instructed

[↑ Back to Table of Contents](#table-of-contents)

## After maintenance completes

A follow-up notification is sent when maintenance completes successfully. If you do not receive confirmation within the expected duration plus 30 minutes, contact the on-call engineer.

[↑ Back to Table of Contents](#table-of-contents)

## Related notifications

- [Backup job is running](./notification-backup-job-running.md)

[↑ Back to Table of Contents](#table-of-contents)

## Additional resources

- [Change management process](#) <!-- Update with actual link -->
- [Maintenance calendar](#) <!-- Update with actual link -->

[↑ Back to Table of Contents](#table-of-contents)
