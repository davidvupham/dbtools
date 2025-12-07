# Operations Guide: Database Patching

## 1. Scope

This guide is intended for Database Administrators (DBAs) and Site Reliability Engineers (SREs) responsible for maintaining database engine currency.

## 2. Standard Operating Procedures (SOPs)

### SOP-001: Routine Monthly Patching

**Frequency**: Monthly.
**Procedure**:

1. Check the "Release Notes" for the target engine.
2. Update the `target_version` variable in Ansible/PowerShell.
3. Run the **Dry-Run** mode:

    ```bash
    ansible-playbook patch_db.yml -e "dry_run=true"
    ```

4. Execute in **Production** ONLY during the approved window.

### SOP-002: Emergency Security Patch

**Trigger**: CVE Announcement with CVSS > 7.0.
**Procedure**:

1. Same as SOP-001 but bypasses the standard "Wait for Monthly Window" rule.
2. Requires VP approval for "Out of Window" execution.

## 3. Troubleshooting

### 3.1 Common Errors

* **"Timeout waiting for node to rejoin"**:
  * **Cause**: Transaction log recovery is taking longer than expected.
  * **Action**: Check DB logs. If recovery is progressing, valid wait. If stuck, investigate.
* **"Disk Space Full"**:
  * **Action**: Clear old logs in `/var/log` or expand volume.

## 4. Manual Verification Steps

To verify a successful patch manually:

1. Connect to the DB: `psql` / `mongo` / `sqlcmd`.
2. Run `SELECT version();` (or equivalent).
3. Check replication lag is 0.
