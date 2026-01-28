# kerberos_auth Molecule Tests

Tests for the `kerberos_auth` role with two scenarios:
1. **default** - Mock-based tests (fast, no infrastructure needed)
2. **samba-dc** - Integration tests with real Samba AD DC

## Scenarios

### default (Mock-based)

Fast tests using mock `kinit`/`klist` scripts. No Kerberos infrastructure required.

```bash
cd ansible/roles/kerberos_auth
molecule test                    # Full test
molecule converge               # Apply only
molecule test --destroy never   # Keep container for debugging
```

**Test cases:**
| Scenario | Ticket State | Expected |
|:---|:---|:---|
| 1 | Valid ticket | Skip renewal |
| 2 | Expired ticket | Renew |
| 3 | No ticket | Obtain new |
| 4 | Force renewal | Renew |

### samba-dc (Integration)

Real integration tests against Samba AD DC (Active Directory-compatible).

```bash
cd ansible/roles/kerberos_auth
molecule test -s samba-dc       # Full test (~2-3 minutes)
molecule converge -s samba-dc   # Apply only
molecule destroy -s samba-dc    # Cleanup
```

**Requirements:**
- Docker or Podman with docker-compose
- ~2GB RAM for Samba DC container
- Ports 88, 389, 445, 636 available

**Test environment:**
| Component | Value |
|:---|:---|
| Domain | TEST.LOCAL |
| DC hostname | dc1.test.local |
| Admin password | P@ssw0rd123 |
| Service account | svc_ansible@TEST.LOCAL |

## Quick Reference

```bash
# Run mock tests (fast)
molecule test

# Run integration tests (real AD)
molecule test -s samba-dc

# Debug: keep containers running
molecule test --destroy never
molecule test -s samba-dc --destroy never

# Login to container
molecule login
molecule login -s samba-dc

# Cleanup
molecule destroy
molecule destroy -s samba-dc
```

## Mock Scripts (default scenario)

| Script | Purpose |
|:---|:---|
| `/usr/local/bin/klist-mock` | Simulates `klist` based on state file |
| `/usr/local/bin/kinit-mock` | Simulates `kinit`, logs calls |
| `/usr/local/bin/set-ticket-state` | Change state (valid/expired/none) |

State file: `/tmp/kerberos-mock-state/ticket_status`

## Samba DC Architecture (samba-dc scenario)

```
┌─────────────────────────────────────────────────────┐
│                  kerberos-net (172.28.0.0/24)       │
│                                                     │
│  ┌─────────────────┐      ┌─────────────────────┐  │
│  │   samba-dc      │      │  ansible-controller │  │
│  │  172.28.0.10    │◄────►│    172.28.0.20      │  │
│  │                 │      │                     │  │
│  │  - KDC (88)     │      │  - krb5-workstation │  │
│  │  - LDAP (389)   │      │  - keytab           │  │
│  │  - DNS (53)     │      │  - kerberos_auth    │  │
│  └─────────────────┘      └─────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Debugging Samba DC

```bash
# Enter DC container
docker exec -it samba-dc bash

# Check Samba status
samba-tool domain info 127.0.0.1

# List users
samba-tool user list

# Show service account
samba-tool user show svc_ansible

# Test DNS
nslookup dc1.test.local 127.0.0.1

# View logs
docker logs samba-dc
```

## Debugging Ansible Controller

```bash
# Enter controller container
docker exec -it ansible-controller bash

# Test Kerberos manually
kinit -kt /etc/krb5/svc_ansible.keytab svc_ansible@TEST.LOCAL
klist

# View krb5.conf
cat /etc/krb5.conf

# Destroy ticket
kdestroy
```
