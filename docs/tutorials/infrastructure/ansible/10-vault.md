# Chapter 10: Ansible Vault

Ansible Vault provides encryption for sensitive data like passwords, API keys, and certificates. This chapter covers creating, editing, and using encrypted content securely.

## Learning Objectives

By the end of this chapter, you will:

- Understand when and why to use Ansible Vault
- Create and manage encrypted files
- Use encrypted variables in playbooks
- Configure vault password files
- Implement vault best practices

## Why Use Ansible Vault?

Sensitive data in automation:
- Database passwords
- API keys and tokens
- SSL certificates and private keys
- SSH keys
- Cloud credentials

**Never store sensitive data in plain text in version control!**

## Creating Encrypted Files

### Create a New Encrypted File

```bash
# Interactive password prompt
ansible-vault create secrets.yml

# Using a password file
ansible-vault create secrets.yml --vault-password-file=vault_pass.txt
```

This opens an editor where you can add content:

```yaml
# Content of secrets.yml
db_password: SuperSecret123!
api_key: abcd-1234-efgh-5678
admin_password: AdminP@ss!
```

### Encrypt an Existing File

```bash
# Encrypt existing file
ansible-vault encrypt vars/passwords.yml

# Encrypt multiple files
ansible-vault encrypt secrets/*.yml
```

### View Encrypted Content

```bash
# View decrypted content (output to terminal)
ansible-vault view secrets.yml

# With password file
ansible-vault view secrets.yml --vault-password-file=vault_pass.txt
```

### Edit Encrypted Files

```bash
# Edit in place
ansible-vault edit secrets.yml

# Specify editor
EDITOR=nano ansible-vault edit secrets.yml
```

### Decrypt Files

```bash
# Decrypt file (remove encryption)
ansible-vault decrypt secrets.yml

# Decrypt to different file
ansible-vault decrypt secrets.yml --output=secrets_decrypted.yml
```

### Change Vault Password

```bash
# Re-encrypt with new password
ansible-vault rekey secrets.yml

# Using password files
ansible-vault rekey secrets.yml \
  --vault-password-file=old_pass.txt \
  --new-vault-password-file=new_pass.txt
```

## Using Encrypted Variables

### Method 1: Encrypted Variable Files

Create `vars/vault.yml`:
```yaml
vault_db_password: MySecretPassword
vault_api_key: secret-api-key-12345
```

Encrypt it:
```bash
ansible-vault encrypt vars/vault.yml
```

Use in playbook:
```yaml
---
- name: Deploy application
  hosts: webservers
  become: yes
  vars_files:
    - vars/common.yml
    - vars/vault.yml  # Encrypted file

  tasks:
    - name: Configure database connection
      template:
        src: db_config.j2
        dest: /etc/app/database.yml
      # vault_db_password is available from vault.yml
```

### Method 2: Inline Encrypted Variables

Encrypt a single value:
```bash
ansible-vault encrypt_string 'MySecretPassword' --name 'db_password'
```

Output:
```yaml
db_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          61626364656667686970716b6c6d6e6f707172737475767778797a3031323334
          ...
```

Use directly in playbook or vars file:
```yaml
---
- name: Deploy with inline vault
  hosts: all
  vars:
    db_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          61626364656667686970716b6c6d6e6f707172737475767778797a3031323334
          35363738393030313233343536373839303132333435363738393031323334

  tasks:
    - name: Configure app
      template:
        src: config.j2
        dest: /etc/app/config.yml
```

## Running Playbooks with Vault

### Interactive Password Prompt

```bash
ansible-playbook site.yml --ask-vault-pass
```

### Password File

Create password file:
```bash
echo "MyVaultPassword" > ~/.vault_pass
chmod 600 ~/.vault_pass
```

Use with playbook:
```bash
ansible-playbook site.yml --vault-password-file=~/.vault_pass
```

### Configure in ansible.cfg

```ini
[defaults]
vault_password_file = ~/.vault_pass
```

Now playbooks automatically use the password file:
```bash
ansible-playbook site.yml  # No --vault-password-file needed
```

### Password from Script

Create executable script `get_vault_pass.py`:
```python
#!/usr/bin/env python3
import os
# Could fetch from environment, keychain, or secret manager
print(os.environ.get('VAULT_PASSWORD', ''))
```

```bash
chmod +x get_vault_pass.py
ansible-playbook site.yml --vault-password-file=./get_vault_pass.py
```

## Multiple Vault Passwords

For different environments or sensitivity levels:

### Using Vault IDs

Create files with different passwords:
```bash
# Development vault
ansible-vault create --vault-id dev@prompt vars/dev_secrets.yml

# Production vault
ansible-vault create --vault-id prod@~/.prod_vault_pass vars/prod_secrets.yml
```

Run with multiple vault IDs:
```bash
ansible-playbook site.yml \
  --vault-id dev@prompt \
  --vault-id prod@~/.prod_vault_pass
```

### Label Encrypted Content

```bash
# Create with label
ansible-vault encrypt_string --vault-id prod@prompt 'secret' --name 'db_pass'
```

Output shows the vault ID:
```yaml
db_pass: !vault |
          $ANSIBLE_VAULT;1.2;AES256;prod
          ...
```

## Practical Examples

### Example 1: Secure User Creation

`vars/vault.yml` (encrypted):
```yaml
user_passwords:
  alice: AliceP@ss123!
  bob: BobSecure456!
  charlie: CharlieKey789!
```

Playbook:
```yaml
---
- name: Create users with secure passwords
  hosts: all
  become: yes
  vars_files:
    - vars/vault.yml

  tasks:
    - name: Create users with passwords
      user:
        name: "{{ item.key }}"
        password: "{{ item.value | password_hash('sha512') }}"
        state: present
      loop: "{{ user_passwords | dict2items }}"
      no_log: true  # Hide password from output
```

### Example 2: Database Configuration

`vars/vault.yml` (encrypted):
```yaml
vault_mysql_root_password: SuperSecretRoot123!
vault_mysql_app_password: AppDBPass456!
```

`vars/database.yml`:
```yaml
mysql_databases:
  - name: appdb
    encoding: utf8mb4
mysql_users:
  - name: appuser
    password: "{{ vault_mysql_app_password }}"
    priv: "appdb.*:ALL"
```

Playbook:
```yaml
---
- name: Configure MySQL
  hosts: databases
  become: yes
  vars_files:
    - vars/database.yml
    - vars/vault.yml

  tasks:
    - name: Set MySQL root password
      mysql_user:
        name: root
        password: "{{ vault_mysql_root_password }}"
        login_unix_socket: /var/run/mysqld/mysqld.sock
      no_log: true

    - name: Create application database
      mysql_db:
        name: "{{ item.name }}"
        encoding: "{{ item.encoding }}"
        state: present
      loop: "{{ mysql_databases }}"

    - name: Create application user
      mysql_user:
        name: "{{ item.name }}"
        password: "{{ item.password }}"
        priv: "{{ item.priv }}"
        state: present
      loop: "{{ mysql_users }}"
      no_log: true
```

### Example 3: API Configuration with Vault

`vars/vault.yml` (encrypted):
```yaml
vault_api_keys:
  slack: xoxb-1234567890-abcdefghijk
  datadog: dd-api-key-1234567890
  pagerduty: pd-key-abcdefghijk
```

Template `templates/api_config.yml.j2`:
```yaml
# API Configuration - Managed by Ansible
integrations:
  slack:
    enabled: true
    token: {{ vault_api_keys.slack }}
  datadog:
    enabled: {{ enable_monitoring | default(true) }}
    api_key: {{ vault_api_keys.datadog }}
  pagerduty:
    enabled: {{ enable_alerting | default(true) }}
    api_key: {{ vault_api_keys.pagerduty }}
```

## Best Practices

### 1. Separate Encrypted and Plain Variables

```text
vars/
├── common.yml           # Non-sensitive variables
├── vault.yml           # Encrypted sensitive variables
└── all.yml             # Variable that references both
```

### 2. Use Consistent Naming

Prefix vault variables:
```yaml
# vars/vault.yml
vault_db_password: secret123
vault_api_key: abcd1234
vault_ssl_key: |
  -----BEGIN PRIVATE KEY-----
  ...
```

Reference in main vars:
```yaml
# vars/main.yml
db_password: "{{ vault_db_password }}"
api_key: "{{ vault_api_key }}"
```

### 3. Never Commit Vault Passwords

`.gitignore`:
```
# Vault password files
.vault_pass*
vault_pass*
*.vault_pass

# Decrypted files
*_decrypted.yml
```

### 4. Use no_log for Sensitive Tasks

```yaml
- name: Set API key
  uri:
    url: https://api.example.com/config
    method: POST
    body:
      api_key: "{{ vault_api_key }}"
    body_format: json
  no_log: true  # Prevents API key from appearing in logs
```

### 5. Rotate Vault Passwords Regularly

```bash
# Re-key all vault files with new password
find . -name "*.yml" -exec grep -l "ANSIBLE_VAULT" {} \; | \
  xargs ansible-vault rekey --vault-password-file=old_pass --new-vault-password-file=new_pass
```

### 6. Use Environment-Specific Vaults

```text
inventory/
├── production/
│   ├── hosts
│   └── group_vars/
│       └── all/
│           ├── vars.yml
│           └── vault.yml     # Production secrets
├── staging/
│   ├── hosts
│   └── group_vars/
│       └── all/
│           ├── vars.yml
│           └── vault.yml     # Staging secrets
```

## Troubleshooting

### "Decryption failed"

```bash
# Check if file is encrypted
head -1 secrets.yml
# Should show: $ANSIBLE_VAULT;1.1;AES256

# Verify password
ansible-vault view secrets.yml --ask-vault-pass
```

### "ERROR! Attempting to decrypt but no vault secrets found"

```bash
# Provide vault password
ansible-playbook site.yml --ask-vault-pass

# Or configure password file in ansible.cfg
```

### View Encrypted Variables in Debug

```yaml
- name: Debug (DO NOT USE IN PRODUCTION)
  debug:
    var: vault_password
  # This will show the decrypted value - security risk!
```

## Exercises

### Exercise 10.1: Create Encrypted Variables

1. Create a vault password file
2. Create encrypted file with database credentials
3. Use credentials in a playbook to configure an application

### Exercise 10.2: Multiple Vault IDs

1. Create separate vaults for dev and prod
2. Store different passwords in each
3. Run a playbook that uses both vaults

### Exercise 10.3: Inline Encrypted Strings

1. Encrypt individual passwords as inline strings
2. Add them to a vars file
3. Use them to create users with secure passwords

## Key Takeaways

- Ansible Vault encrypts sensitive data at rest
- Use `ansible-vault create/edit/view/decrypt` commands
- Configure vault password file in ansible.cfg for convenience
- Use `no_log: true` to hide sensitive task output
- Prefix vault variables with `vault_` for clarity
- Never commit vault passwords to version control
- Use multiple vault IDs for different environments
- Rotate vault passwords regularly

## What's Next?

In the next chapter, you'll learn about error handling with blocks, rescue, and always.

**Next Chapter**: [Chapter 11: Error Handling](11-error-handling.md)
