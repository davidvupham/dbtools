# How to test the mongodb_rhel Ansible role with Molecule

**🔗 [← Back to How-To Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 28, 2026
> **Maintainers:** Global Data Services
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Type](https://img.shields.io/badge/Type-How--To-green)

> [!IMPORTANT]
> **Related Docs:** [Role README](../../../ansible/roles/mongodb_rhel/README.md) | [RHEL Configuration Best Practices](../../best-practices/mongodb/rhel-configuration.md)

> [!NOTE]
> This guide shows you how to run Molecule tests for the `mongodb_rhel` Ansible role. The role configures RHEL for MongoDB using best-practice OS settings. If you are new to the role itself, read the [role README](../../../ansible/roles/mongodb_rhel/README.md) first.

## Table of contents

- [Prerequisites](#prerequisites)
- [Run the test suite](#run-the-test-suite)
- [Understand the test sequence](#understand-the-test-sequence)
- [What the tests verify](#what-the-tests-verify)
- [Container testing limitations](#container-testing-limitations)
    - [SELinux](#selinux)
    - [Transparent Huge Pages (THP)](#transparent-huge-pages-thp)
    - [Filesystem (XFS)](#filesystem-xfs)
    - [Firewall](#firewall)
    - [Tuned daemon](#tuned-daemon)
    - [Idempotence edge cases](#idempotence-edge-cases)
- [Debug a failing test](#debug-a-failing-test)
- [Extend testing with a VM scenario](#extend-testing-with-a-vm-scenario)
- [Troubleshooting](#troubleshooting)
- [Related guides](#related-guides)

## Prerequisites

- Docker Engine running on your workstation
- Python packages: `molecule`, `molecule-plugins[docker]`, `ansible`, `ansible-lint`
  (installed via `docker/ansible/requirements.txt` or your virtualenv)
- The `ansible.posix` and `community.general` Ansible collections

Install the collections if you have not already:

```bash
ansible-galaxy collection install -r ansible/roles/mongodb_rhel/molecule/requirements.yml
```

[↑ Back to Table of Contents](#table-of-contents)

## Run the test suite

Navigate to the role directory and run Molecule:

```bash
cd ansible/roles/mongodb_rhel
molecule test
```

This runs the full test sequence: create a Rocky Linux 9 container, apply the role, verify idempotence, assert all settings, and destroy the container.

To run individual stages:

```bash
molecule create     # Create the container only
molecule converge   # Apply the role
molecule verify     # Run verification assertions
molecule idempotence  # Re-apply and assert no changes
molecule destroy    # Remove the container
```

[↑ Back to Table of Contents](#table-of-contents)

## Understand the test sequence

The `default` scenario runs these steps in order:

| Step | Purpose |
|:---|:---|
| **dependency** | Install required Ansible collections (`ansible.posix`, `community.general`) |
| **syntax** | Validate playbook YAML syntax |
| **create** | Start a privileged Rocky Linux 9 container with systemd |
| **prepare** | Install `tuned`, `procps-ng`; create mock `mongod.service` |
| **converge** | Apply the `mongodb_rhel` role using the shared best-practices config |
| **idempotence** | Run converge again; fail if any task reports a change |
| **verify** | Assert sysctl values, config files, systemd limits, and tuned profile |
| **destroy** | Remove the container |

[↑ Back to Table of Contents](#table-of-contents)

## What the tests verify

The `verify.yml` playbook checks five categories:

1. **Sysctl parameters** — Reads all 11 kernel parameters via `sysctl -n` and asserts each value matches the expected setting (exact match or `>=` depending on the parameter).
2. **Sysctl config files** — Asserts `/etc/sysctl.d/99-mongodb.conf` and `/etc/sysctl.d/99-mongodb-net.conf` exist on disk.
3. **Systemd limits** — Asserts `/etc/systemd/system/mongod.service.d/limits.conf` exists and contains `LimitNOFILE=64000` and `LimitNPROC=64000`.
4. **THP tuned profile** — Asserts `/etc/tuned/mongodb/tuned.conf` exists and contains `transparent_hugepages=never` (for MongoDB 7.0).
5. **SELinux** — Reports status but skips assertions (SELinux is not functional in Docker containers).

[↑ Back to Table of Contents](#table-of-contents)

## Container testing limitations

Docker containers share the host kernel and lack several subsystems present on a real RHEL installation. The following sections describe each limitation and its impact on test fidelity.

### SELinux

**What happens:** SELinux is not available inside Docker containers. The `getenforce` command either returns `Disabled` or is absent entirely.

**Impact:** The role's SELinux tasks (setting enforcing mode, installing `mongodb-selinux`, applying file contexts) are skipped automatically. The verify playbook reports SELinux as "SKIPPED (container)" instead of asserting its state.

**What you cannot test:**
- Whether `mongodb-selinux` installs correctly from the MongoDB repository
- Whether custom file contexts (`mongod_var_lib_t`) are applied to non-default data paths
- Whether SELinux transitions to enforcing mode without breaking `mongod`

**Mitigation:** Test SELinux on a real RHEL 9 VM or cloud instance. You can add a Vagrant-based Molecule scenario for this purpose.

### Transparent Huge Pages (THP)

**What happens:** The THP sysfs interface at `/sys/kernel/mm/transparent_hugepage/enabled` may be read-only in containers, even in privileged mode. Writing to it can fail silently or raise a permission error.

**Impact:** The role creates the tuned profile file (`/etc/tuned/mongodb/tuned.conf`) and the verify playbook confirms the file exists and contains the correct content. However, the actual THP kernel state is not changed.

**What you cannot test:**
- Whether `tuned-adm profile mongodb` successfully disables THP at the kernel level
- Whether THP remains disabled after a reboot

**Mitigation:** The file-based verification confirms the role produces the correct configuration artifacts. Kernel-level activation requires a real RHEL host.

### Filesystem (XFS)

**What happens:** Docker containers use the overlay filesystem from the host. There is no dedicated data volume formatted as XFS.

**Impact:** The Ansible role does not format filesystems (that is an infrastructure provisioning concern). The Python validator (`RHELConfigValidator.check_filesystem()`) is what checks for XFS, and it is tested separately with mocked `/proc/mounts` data.

**What you cannot test:**
- Whether the data volume at `/var/lib/mongo` is XFS
- Whether `noatime` and `nodiratime` mount options are present

### Firewall

**What happens:** `firewalld` is not installed in the test container, and the Ansible role does not manage firewall rules.

**Impact:** No firewall testing occurs. Firewall configuration is documented in the [RHEL configuration best practices](../../best-practices/mongodb/rhel-configuration.md#security-selinux-and-firewall) as a manual step.

### Tuned daemon

**What happens:** The `tuned` package installs in the container, but the `tuned` daemon may not start because systemd services in containers can be unreliable.

**Impact:** The `Activate tuned profile` handler fires but may not achieve the desired effect. The verify playbook checks the profile file, not the daemon state.

### Idempotence edge cases

**What happens:** Molecule runs converge twice and fails if any task reports `changed` on the second run. In containers, most tasks behave identically to production, but handlers (restart mongod, activate tuned) may not fire the same way.

**Impact:** The idempotence check validates that the core tasks (sysctl, file creation, template rendering) do not report unnecessary changes. Handler behavior may differ from production.

> [!IMPORTANT]
> Container tests verify that the role **produces the correct configuration artifacts** (files, sysctl values, systemd overrides). They do not verify that all kernel-level settings take effect. For full-fidelity validation, run the role against a RHEL 9 VM.

[↑ Back to Table of Contents](#table-of-contents)

## Debug a failing test

Keep the container running after a failure to inspect its state:

```bash
molecule test --destroy never
```

Connect to the running container:

```bash
molecule login
```

Inside the container, you can inspect settings manually:

```bash
sysctl vm.swappiness
cat /etc/sysctl.d/99-mongodb.conf
cat /etc/systemd/system/mongod.service.d/limits.conf
cat /etc/tuned/mongodb/tuned.conf
```

When you are done, clean up:

```bash
molecule destroy
```

[↑ Back to Table of Contents](#table-of-contents)

## Extend testing with a VM scenario

To test SELinux, THP activation, and other kernel-level features, you can add a second Molecule scenario using the Vagrant driver with a RHEL 9 box:

```bash
mkdir -p molecule/vm
```

Create `molecule/vm/molecule.yml` with:

```yaml
driver:
  name: vagrant
platforms:
  - name: rhel9-vm
    box: generic/rocky9
    memory: 2048
    cpus: 2
```

Run the VM scenario:

```bash
molecule test -s vm
```

> [!NOTE]
> The VM scenario requires Vagrant and a hypervisor (VirtualBox or libvirt) installed on your workstation.

[↑ Back to Table of Contents](#table-of-contents)

## Troubleshooting

### Problem: `docker: Error response from daemon: cgroup2 not supported`

**Cause:** The Rocky Linux 9 container requires cgroup v2. Older Docker versions or host kernels may not support it.

**Solution:** Upgrade Docker Engine to version 20.10 or later. Verify cgroup version:

```bash
stat -fc %T /sys/fs/cgroup/
# Should output: cgroup2fs
```

### Problem: `sysctl: permission denied on key`

**Cause:** The container is not running in privileged mode, or the sysctl parameter is restricted.

**Solution:** Verify the `molecule.yml` has `privileged: true` set on the platform. Some host kernels restrict certain sysctl writes even in privileged containers.

### Problem: Molecule reports changes on idempotence run

**Cause:** A task is not idempotent — it reports `changed` every time it runs.

**Solution:** Connect to the container with `molecule login` and run the specific task manually to identify what is changing. Common causes include shell commands without `creates` or `removes` guards, and handlers that re-fire.

[↑ Back to Table of Contents](#table-of-contents)

## Related guides

- [Role README](../../../ansible/roles/mongodb_rhel/README.md) - Quick start and variable reference
- [RHEL configuration best practices](../../best-practices/mongodb/rhel-configuration.md) - The source documentation for all recommended settings
- [Shared config file](../../../config/mongodb/rhel-best-practices.yml) - Single source of truth for all values

## See also

- [Molecule documentation](https://ansible.readthedocs.io/projects/molecule/) - Official Molecule project docs
- [MongoDB production notes](https://www.mongodb.com/docs/manual/administration/production-notes/) - Official MongoDB deployment guidance

[↑ Back to Table of Contents](#table-of-contents)
