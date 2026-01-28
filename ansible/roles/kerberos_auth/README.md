# kerberos_auth — Ansible role

**[Back to Roles Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 28, 2026
> **Maintainers:** Global Data Services
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Type](https://img.shields.io/badge/Type-Ansible_Role-blue)

Ensures a valid Kerberos ticket exists on the Ansible controller before
executing tasks that require Kerberos authentication. Designed for managing
Windows servers via WinRM with Kerberos authentication from a Linux controller.

## Table of contents

- [Quick start](#quick-start)
- [How it works](#how-it-works)
- [Role variables](#role-variables)
- [Usage patterns](#usage-patterns)
  - [As a role dependency](#as-a-role-dependency)
  - [In pre_tasks](#in-pre_tasks)
  - [Standalone](#standalone)
- [Security considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

## Quick start

```yaml
- name: Manage Windows servers
  hosts: windows_servers
  gather_facts: false

  roles:
    - role: kerberos_auth
      vars:
        kerberos_keytab_path: /etc/krb5/svc_ansible.keytab
        kerberos_principal: svc_ansible@DOMAIN.COM

  tasks:
    - name: Set user rights assignment
      ansible.windows.win_user_right:
        name: SeServiceLogonRight
        users:
          - DOMAIN\svc_account
        action: add
```

[Back to Table of Contents](#table-of-contents)

## How it works

The role performs the following steps:

1. **Validates configuration** - Ensures keytab path and principal are provided
2. **Locates Kerberos binaries** - Finds `kinit` and `klist` on the controller
3. **Verifies keytab exists** - Confirms the keytab file is present
4. **Checks existing ticket** - Uses `klist -s` to test for a valid ticket
5. **Calculates remaining lifetime** - Parses ticket expiration to determine time remaining
6. **Obtains new ticket if needed** - Runs `kinit -kt` only when:
   - No valid ticket exists, OR
   - Ticket expires within the threshold (`kerberos_min_remaining_lifetime`), OR
   - `kerberos_force_renewal` is set to `true`
7. **Verifies new ticket** - Confirms the ticket was obtained successfully

All tasks run on `localhost` (the Ansible controller) with `run_once: true`.

[Back to Table of Contents](#table-of-contents)

## Role variables

| Variable | Default | Description |
|:---|:---|:---|
| `kerberos_keytab_path` | `""` | **Required.** Path to keytab file on Ansible controller |
| `kerberos_principal` | `""` | **Required.** Kerberos principal (e.g., `svc_ansible@DOMAIN.COM`) |
| `kerberos_min_remaining_lifetime` | `300` | Minimum seconds before expiry to trigger renewal |
| `kerberos_force_renewal` | `false` | Set `true` to always obtain a new ticket |
| `kerberos_kinit_path` | `""` | Path to `kinit` binary (auto-detected if empty) |
| `kerberos_klist_path` | `""` | Path to `klist` binary (auto-detected if empty) |

[Back to Table of Contents](#table-of-contents)

## Usage patterns

### As a role dependency

Add to your Windows management role's `meta/main.yml`:

```yaml
dependencies:
  - role: kerberos_auth
    vars:
      kerberos_keytab_path: "{{ vault_kerberos_keytab_path }}"
      kerberos_principal: "{{ vault_kerberos_principal }}"
```

### In pre_tasks

```yaml
- name: Configure Windows servers
  hosts: windows_servers
  gather_facts: false

  pre_tasks:
    - name: Ensure Kerberos authentication
      ansible.builtin.include_role:
        name: kerberos_auth
      vars:
        kerberos_keytab_path: /etc/krb5/svc_ansible.keytab
        kerberos_principal: svc_ansible@DOMAIN.COM

  tasks:
    - name: Your Windows tasks here
      # ...
```

### Standalone

```bash
# Check/renew ticket only
ansible-playbook -i localhost, -c local playbook.yml \
  -e kerberos_keytab_path=/etc/krb5/svc_ansible.keytab \
  -e kerberos_principal=svc_ansible@DOMAIN.COM

# Force renewal regardless of current ticket status
ansible-playbook -i localhost, -c local playbook.yml \
  -e kerberos_force_renewal=true
```

[Back to Table of Contents](#table-of-contents)

## Security considerations

1. **Keytab file permissions** - Ensure the keytab is readable only by the
   Ansible user (`chmod 600`)

2. **Store credentials in Vault** - Never hardcode keytab paths or principals
   in playbooks:
   ```yaml
   vars:
     kerberos_keytab_path: "{{ vault_kerberos_keytab_path }}"
     kerberos_principal: "{{ vault_kerberos_principal }}"
   ```

3. **Principle of least privilege** - The service account in the keytab should
   have only the permissions required for Windows management tasks

4. **Audit logging** - Monitor `kinit` events on your KDC for the service
   account to detect unauthorized usage

5. **no_log enabled** - The `kinit` task uses `no_log: true` to prevent
   credential exposure in Ansible output

[Back to Table of Contents](#table-of-contents)

## Troubleshooting

### "Keytab file not found"

Verify the keytab exists and is readable:

```bash
ls -la /etc/krb5/svc_ansible.keytab
klist -kt /etc/krb5/svc_ansible.keytab
```

### "Failed to obtain Kerberos ticket"

1. Test manually on the controller:
   ```bash
   kinit -kt /etc/krb5/svc_ansible.keytab svc_ansible@DOMAIN.COM
   klist
   ```

2. Check DNS resolution for the KDC
3. Verify `/etc/krb5.conf` configuration
4. Ensure time synchronization with the KDC (Kerberos is time-sensitive)

### Ticket obtained but WinRM still fails

1. Verify the principal matches what Windows expects
2. Check SPN registration: `setspn -L svc_ansible`
3. Ensure `ansible_winrm_transport: kerberos` is set in inventory

[Back to Table of Contents](#table-of-contents)
