# Chapter 13: Best Practices

Following best practices makes your Ansible automation more maintainable, reliable, and professional. This chapter compiles proven patterns and techniques from the Ansible community.

## 🎯 Learning Objectives

By the end of this chapter, you will:

- Write clean, maintainable playbooks
- Organize projects effectively
- Handle secrets securely
- Optimize playbook performance
- Test and validate automation
- Follow naming conventions

## 📁 Project Organization

### Recommended Directory Structure

```text
ansible-project/
├── ansible.cfg                 # Project configuration
├── inventory/
│   ├── production/
│   │   ├── hosts              # Production inventory
│   │   ├── group_vars/
│   │   └── host_vars/
│   └── staging/
│       ├── hosts              # Staging inventory
│       ├── group_vars/
│       └── host_vars/
├── playbooks/
│   ├── site.yml               # Master playbook
│   ├── webservers.yml
│   ├── databases.yml
│   └── monitoring.yml
├── roles/
│   ├── common/                # Reusable roles
│   ├── webserver/
│   ├── database/
│   └── monitoring/
├── group_vars/
│   ├── all.yml               # Variables for all hosts
│   ├── webservers.yml
│   └── databases.yml
├── host_vars/
│   ├── web1.yml
│   └── db1.yml
├── library/                   # Custom modules
├── filter_plugins/            # Custom filters
├── files/                     # Static files
├── templates/                 # Jinja2 templates
├── vars/                      # Additional variables
│   ├── common.yml
│   └── secrets.yml           # Encrypted with vault
├── tasks/                     # Reusable task files
├── handlers/                  # Reusable handlers
├── tests/                     # Test playbooks
├── docs/                      # Documentation
├── .gitignore
└── README.md
```

### ansible.cfg Best Practices

```ini
[defaults]
# Inventory
inventory = ./inventory/production/hosts

# Performance
forks = 20
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 3600

# Output
stdout_callback = yaml
callbacks_enabled = timer, profile_tasks
display_skipped_hosts = no
deprecation_warnings = True

# SSH
host_key_checking = False
remote_user = ansible
private_key_file = ~/.ssh/ansible_key

# Roles
roles_path = ./roles:/usr/share/ansible/roles

# Security
vault_password_file = ~/.ansible/vault_pass.txt

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False

[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
```

## 📝 Playbook Best Practices

### 1. Always Name Tasks and Plays

```yaml
# ❌ BAD - no names
---
- hosts: all
  tasks:
    - package:
        name: nginx
    - service:
        name: nginx
        state: started

# ✅ GOOD - descriptive names
---
- name: Configure web servers
  hosts: webservers

  tasks:
    - name: Install nginx web server
      package:
        name: nginx
        state: present

    - name: Ensure nginx is running
      service:
        name: nginx
        state: started
        enabled: yes
```

### 2. Use Descriptive Variable Names

```yaml
# ❌ BAD - unclear names
vars:
  p: 80
  n: nginx
  t: 30

# ✅ GOOD - clear, descriptive names
vars:
  http_port: 80
  web_server_package: nginx
  connection_timeout: 30
```

### 3. Group Related Tasks

```yaml
# ✅ GOOD - logical grouping with comments
---
- name: Setup web server
  hosts: webservers

  tasks:
    # Package installation
    - name: Install nginx
      package:
        name: nginx
        state: present

    - name: Install SSL packages
      package:
        name:
          - openssl
          - ca-certificates
        state: present

    # Configuration
    - name: Copy nginx configuration
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
      notify: Reload nginx

    # Service management
    - name: Start nginx service
      service:
        name: nginx
        state: started
        enabled: yes
```

### 4. Use YAML Dictionary Format

```yaml
# ❌ AVOID - inline format, hard to read
- name: Copy file
  copy: src=/tmp/file dest=/etc/file owner=root mode=0644

# ✅ GOOD - dictionary format, easy to read
- name: Copy file
  copy:
    src: /tmp/file
    dest: /etc/file
    owner: root
    mode: '0644'
```

### 5. Quote When Necessary

```yaml
# ✅ GOOD - proper quoting
vars:
  # Quote strings starting with variables
  full_path: "{{ base_dir }}/subdir"

  # Quote octal numbers
  file_mode: '0644'

  # Quote special characters
  password: "p@ssw0rd!"

  # Quote yes/no when not boolean
  answer: "yes"  # String "yes", not boolean true
```

## 🔐 Security Best Practices

### 1. Use Ansible Vault for Secrets

```bash
# Create encrypted file
ansible-vault create secrets.yml

# Edit encrypted file
ansible-vault edit secrets.yml

# Encrypt existing file
ansible-vault encrypt vars/passwords.yml

# Use in playbook
ansible-playbook playbook.yml --ask-vault-pass
```

**secrets.yml** (encrypted):
```yaml
---
database_password: "super_secret_password"
api_key: "abc123def456"
ssl_private_key: |
  -----BEGIN PRIVATE KEY-----
  ...
  -----END PRIVATE KEY-----
```

### 2. Never Commit Secrets

**.gitignore**:
```text
# Sensitive files
**/secrets.yml
**/vault_pass.txt
**/*secret*
**/*password*
*.pem
*.key

# Vault password files
.vault_pass
.vault_password

# Temporary files
*.retry
*.pyc
__pycache__/
```

### 3. Use Separate Credentials Per Environment

```text
vars/
├── production_secrets.yml     # Encrypted
├── staging_secrets.yml        # Encrypted
└── development_secrets.yml    # Encrypted (different passwords)
```

### 4. Limit Privilege Escalation

```yaml
# ✅ GOOD - only escalate when needed
---
- name: Mixed privilege tasks
  hosts: all

  tasks:
    - name: Check status (no sudo needed)
      command: systemctl status nginx
      become: no

    - name: Install package (needs sudo)
      package:
        name: nginx
        state: present
      become: yes

    - name: Create user file (no sudo needed)
      copy:
        content: "data"
        dest: ~/file.txt
      become: no
```

## ⚡ Performance Optimization

### 1. Disable Fact Gathering When Not Needed

```yaml
---
- name: Quick tasks
  hosts: all
  gather_facts: no  # Skip fact gathering

  tasks:
    - name: Ping hosts
      ping:
```

### 2. Use Fact Caching

**ansible.cfg**:
```ini
[defaults]
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 86400
```

### 3. Increase Parallelism

```ini
[defaults]
forks = 50  # Default is 5
```

Or per playbook:
```yaml
---
- name: Parallel execution
  hosts: all
  serial: 10  # Process 10 hosts at a time
```

### 4. Use Async for Long-Running Tasks

```yaml
- name: Long-running task
  command: /usr/bin/long_task.sh
  async: 3600        # Max time to wait (seconds)
  poll: 0            # Fire and forget
  register: long_task

- name: Check on long-running task later
  async_status:
    jid: "{{ long_task.ansible_job_id }}"
  register: job_result
  until: job_result.finished
  retries: 30
  delay: 10
```

### 5. Optimize Loops

```yaml
# ❌ SLOW - one package at a time
- name: Install packages
  package:
    name: "{{ item }}"
    state: present
  loop:
    - nginx
    - git
    - vim

# ✅ FAST - all packages in one transaction
- name: Install packages
  package:
    name:
      - nginx
      - git
      - vim
    state: present
```

## 🧪 Testing and Validation

### 1. Use Check Mode

```bash
# Dry run - show what would change
ansible-playbook playbook.yml --check

# With diff to see changes
ansible-playbook playbook.yml --check --diff
```

### 2. Syntax Validation

```bash
# Check playbook syntax
ansible-playbook playbook.yml --syntax-check

# Validate YAML
yamllint playbook.yml
```

### 3. Lint Your Playbooks

```bash
# Install ansible-lint
pip install ansible-lint

# Run linter
ansible-lint playbook.yml

# Run on all playbooks
ansible-lint playbooks/
```

### 4. Test in Stages

```yaml
---
- name: Staged deployment
  hosts: webservers
  serial:
    - 1           # Test on 1 server first
    - 25%         # Then 25% of remaining
    - 100%        # Then all remaining

  tasks:
    - name: Deploy application
      # deployment tasks
```

### 5. Create Test Playbooks

```yaml
---
# tests/test_webserver.yml
- name: Test web server configuration
  hosts: webservers
  gather_facts: no

  tasks:
    - name: Check nginx is installed
      command: nginx -v
      register: result
      failed_when: result.rc != 0

    - name: Check nginx is running
      service:
        name: nginx
        state: started
      check_mode: yes
      register: result
      failed_when: result.changed

    - name: Check port 80 is listening
      wait_for:
        port: 80
        timeout: 5

    - name: Test HTTP response
      uri:
        url: http://{{ inventory_hostname }}
        return_content: yes
      register: result
      failed_when: result.status != 200
```

## 📋 Naming Conventions

### File Names

```text
# Playbooks - use descriptive names
deploy_application.yml
configure_webservers.yml
backup_databases.yml

# Roles - use lowercase with underscores
roles/web_server/
roles/database_backup/
roles/monitoring_agent/

# Variables files - match group/host names
group_vars/webservers.yml
host_vars/web01.yml

# Templates - end with .j2
templates/nginx.conf.j2
templates/database.cnf.j2
```

### Variable Names

```yaml
# Use snake_case
database_host: localhost
max_connections: 100
ssl_enabled: true

# Prefix related variables
mysql_host: localhost
mysql_port: 3306
mysql_database: myapp

nginx_worker_processes: 4
nginx_worker_connections: 1024

# Boolean variables - use is_ or has_ prefix
is_production: true
has_ssl: true
enable_monitoring: true
```

### Task Names

```text
# Use imperatives (command form)
"Install nginx package"
"Start nginx service"
"Copy configuration file"

# Not
"Installing nginx"
"Nginx service"
"Configuration file"
```

## 🔄 Idempotency

### Ensure All Tasks Are Idempotent

```yaml
# ❌ BAD - not idempotent
- name: Add line to file
  shell: echo "setting=value" >> /etc/config

# ✅ GOOD - idempotent
- name: Ensure line in file
  lineinfile:
    path: /etc/config
    line: "setting=value"
    state: present

# ❌ BAD - creates directory every time
- name: Create directory
  command: mkdir /opt/app

# ✅ GOOD - idempotent
- name: Ensure directory exists
  file:
    path: /opt/app
    state: directory
```

### Use Changed_when for Command Tasks

```yaml
# Commands always show 'changed', control this:
- name: Check service status
  command: systemctl is-active nginx
  register: result
  changed_when: false        # Never shows changed
  failed_when: result.rc not in [0, 3]

- name: Add user to group
  command: usermod -aG docker {{ username }}
  register: result
  changed_when: "'no changes' not in result.stderr"
```

## 📚 Documentation

### 1. Document Your Playbooks

```yaml
---
# playbooks/deploy_app.yml
#
# Deploy application to web servers
#
# Usage:
#   ansible-playbook playbooks/deploy_app.yml -e "version=2.1.0"
#
# Required variables:
#   - version: Application version to deploy
#
# Optional variables:
#   - rollback: Set to 'yes' to rollback (default: no)
#
# Tags:
#   - download: Only download artifacts
#   - deploy: Only deploy application
#   - verify: Only run verification tests

- name: Deploy application
  hosts: webservers

  tasks:
    # tasks here
```

### 2. Create a README

**README.md**:
```markdown
# Ansible Automation Project

## Overview
This project manages our web and database infrastructure.

## Prerequisites
- Ansible 2.10+
- SSH access to managed hosts
- Vault password file

## Quick Start
1. Install dependencies: `ansible-galaxy install -r requirements.yml`
2. Run playbook: `ansible-playbook playbooks/site.yml`

## Playbooks
- `site.yml` - Master playbook for all servers
- `webservers.yml` - Configure web servers
- `databases.yml` - Configure databases

## Inventory
- `inventory/production/` - Production environment
- `inventory/staging/` - Staging environment

## Tags
- `config` - Configuration tasks
- `deploy` - Deployment tasks
- `verify` - Verification tasks
```

### 3. Comment Complex Logic

```yaml
# For complex conditionals or logic, add explanatory comments
tasks:
  # Only run on Ubuntu 20.04+ or CentOS 8+
  # because older versions lack required packages
  - name: Install modern package
    package:
      name: modern-package
    when: >
      (ansible_distribution == "Ubuntu" and
       ansible_distribution_version is version('20.04', '>=')) or
      (ansible_distribution == "CentOS" and
       ansible_distribution_major_version | int >= 8)
```

## 🎯 Role Best Practices

### 1. Keep Roles Focused

Each role should have a single responsibility:

```text
✅ GOOD
roles/
├── nginx/          # Just nginx
├── php_fpm/        # Just PHP-FPM
└── mysql/          # Just MySQL

❌ BAD
roles/
└── webstack/       # Everything bundled together
```

### 2. Use Role Dependencies

**roles/webserver/meta/main.yml**:
```yaml
---
dependencies:
  - role: common
  - role: firewall
    vars:
      firewall_allowed_ports:
        - 80
        - 443
```

### 3. Provide Sensible Defaults

**roles/nginx/defaults/main.yml**:
```yaml
---
nginx_worker_processes: auto
nginx_worker_connections: 1024
nginx_keepalive_timeout: 65
nginx_client_max_body_size: 10m
nginx_ssl_protocols: "TLSv1.2 TLSv1.3"
```

## 🔍 Error Handling

### 1. Handle Failures Gracefully

```yaml
- name: Task that might fail
  command: /usr/bin/risky_command
  ignore_errors: yes
  register: result

- name: Take action on failure
  debug:
    msg: "Command failed, but we're continuing"
  when: result.failed

- name: Alternative approach with block
  block:
    - name: Try something
      command: /usr/bin/command
  rescue:
    - name: Handle failure
      debug:
        msg: "Command failed, running alternative"
    - command: /usr/bin/alternative
  always:
    - name: Cleanup
      file:
        path: /tmp/tempfile
        state: absent
```

### 2. Validate Prerequisites

```yaml
- name: Validate environment
  hosts: all

  tasks:
    - name: Ensure required variables are defined
      assert:
        that:
          - database_host is defined
          - database_port is defined
          - admin_email is defined
        fail_msg: "Required variables not defined"

    - name: Check minimum Ansible version
      assert:
        that:
          - ansible_version.full is version('2.10', '>=')
        fail_msg: "Ansible 2.10+ required"

    - name: Verify OS compatibility
      assert:
        that:
          - ansible_os_family in ['Debian', 'RedHat']
        fail_msg: "Unsupported OS: {{ ansible_os_family }}"
```

## 📊 Logging and Monitoring

### 1. Log Playbook Runs

**ansible.cfg**:
```ini
[defaults]
log_path = /var/log/ansible/ansible.log
```

### 2. Track Changes

```yaml
- name: Log configuration changes
  lineinfile:
    path: /var/log/ansible-changes.log
    line: "{{ ansible_date_time.iso8601 }} - {{ inventory_hostname }} - {{ ansible_play_name }}"
    create: yes
  delegate_to: localhost
  run_once: yes
```

## 📖 Key Takeaways

✅ Organize projects with clear directory structure
✅ Always name tasks and plays descriptively
✅ Use Ansible Vault for all secrets
✅ Optimize with fact caching and increased forks
✅ Test with check mode and ansible-lint
✅ Follow naming conventions consistently
✅ Ensure all tasks are idempotent
✅ Document playbooks and create READMEs
✅ Keep roles focused and reusable
✅ Handle errors gracefully with blocks

## 🎓 What's Next?

Now that you know the best practices, you're ready to tackle real-world projects with confidence!

**Next Chapter**: [Chapter 14: Real-World Projects](14-real-world-projects.md)

In the next chapter, you'll apply everything you've learned to complete automation projects:
- Deploy a full web application stack
- Automate database backups
- Configure monitoring systems
- Implement disaster recovery

---

**Remember**: Best practices evolve, keep learning and adapting!
