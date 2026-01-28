# mongodb_rhel — Ansible role

Configures Red Hat Enterprise Linux (RHEL) 8 and 9 for MongoDB following
production best practices. All recommended values are loaded from a shared
YAML configuration file so that the Python validator
(`gds_mongodb.rhel_validator`) and this Ansible role use the same source of
truth.

## Quick start

```bash
# Apply settings to target hosts
ansible-playbook ansible/playbooks/mongodb_rhel_configure.yml \
  -i inventory/production/hosts.ini

# Validate only (dry-run, no changes)
ansible-playbook ansible/playbooks/mongodb_rhel_configure.yml \
  -i inventory/production/hosts.ini --check --diff

# Override MongoDB version
ansible-playbook ansible/playbooks/mongodb_rhel_configure.yml \
  -e mongodb_version=8.0
```

## What the role configures

| Category | Settings applied |
|:---|:---|
| Sysctl | 11 kernel parameters (swappiness, dirty ratios, NUMA, file limits, network) |
| THP | Tuned profile for 7.x (`never`) or sysfs write for 8.0+ (`always`) |
| Systemd limits | `LimitNOFILE` and `LimitNPROC` drop-in for the mongod service |
| SELinux | Enforcing mode, `mongodb-selinux` package, custom path contexts |

## Role variables

| Variable | Default | Description |
|:---|:---|:---|
| `mongodb_rhel_config_path` | `../../config/mongodb/rhel-best-practices.yml` | Path to the shared YAML config |
| `mongodb_rhel_validate_only` | `false` | Set to `true` to run in read-only mode |

All best-practice values (sysctl, ulimits, THP, SELinux) are defined in the
shared config file and loaded at runtime. Override individual settings in
`group_vars` or `host_vars`.

## Testing with Molecule

The role includes a Molecule test scenario using Docker with Rocky Linux 9.

```bash
cd ansible/roles/mongodb_rhel
molecule test           # Full sequence: create, converge, idempotence, verify, destroy
molecule converge       # Apply the role only
molecule verify         # Run verification assertions only
molecule destroy        # Remove the container
molecule test --destroy never  # Keep the container for debugging
```

### Container testing limitations

Docker containers do not fully replicate a production RHEL environment. The
following limitations apply when testing with the `default` (Docker) scenario:

| Feature | Container behavior | Production behavior |
|:---|:---|:---|
| **Sysctl parameters** | Writable in privileged mode. Fully tested. | Writable. Fully functional. |
| **Systemd drop-ins** | Works with `/sbin/init` as PID 1. Fully tested. | Works natively. |
| **THP tuned profile** | Profile file is created and verified. The `tuned-adm` handler may not activate because the tuned daemon does not run reliably in containers. The THP sysfs path (`/sys/kernel/mm/transparent_hugepage/enabled`) may be read-only. | `tuned-adm profile mongodb` activates the profile and disables THP at the kernel level. |
| **SELinux** | Not functional. Tasks are skipped automatically when `getenforce` reports `Disabled` or is absent. | Enforcing mode is set. `mongodb-selinux` package is installed. Custom path contexts are applied. |
| **Filesystem (XFS)** | Not testable. Containers use the overlay filesystem from the host. | The role does not format filesystems, but the Python validator checks for XFS. |
| **Firewall (firewalld)** | Not tested. `firewalld` is not installed in the container. | The role does not manage firewall rules directly; see the best-practices guide. |
| **Idempotence** | Molecule runs converge twice and asserts zero changes on the second run. Some handlers (tuned, mongod restart) may not fire identically to production. | All tasks are idempotent. |

> For full-fidelity testing including SELinux, THP activation, and XFS
> validation, use a VM-based scenario (Vagrant or cloud instance) with a
> real RHEL 9 image.

## Dependencies

- `ansible.posix` collection (for `sysctl` and `selinux` modules)
- `community.general` collection (for `sefcontext` module)
