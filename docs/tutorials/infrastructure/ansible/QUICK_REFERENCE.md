# Ansible Quick Reference Guide

A concise reference for common Ansible commands, module syntax, and patterns. Keep this handy while writing playbooks!

## 🎯 Command Line Reference

### Ad-Hoc Commands

```bash
# Basic syntax
ansible <host-pattern> -m <module> -a "<args>" [options]

# Ping all hosts
ansible all -m ping

# Run command on hosts
ansible webservers -m command -a "uptime"

# With sudo
ansible all -m package -a "name=nginx state=present" -b

# Check mode (dry run)
ansible all -m command -a "whoami" --check
```

### Playbook Commands

```bash
# Run playbook
ansible-playbook playbook.yml

# With inventory
ansible-playbook -i inventory playbook.yml

# Limit to hosts
ansible-playbook playbook.yml --limit webservers

# With variables
ansible-playbook playbook.yml -e "var=value"

# Check mode (dry run)
ansible-playbook playbook.yml --check

# With diff
ansible-playbook playbook.yml --check --diff

# Start at task
ansible-playbook playbook.yml --start-at-task="Install nginx"

# Use tags
ansible-playbook playbook.yml --tags "config,deploy"
ansible-playbook playbook.yml --skip-tags "deploy"

# Verbose output
ansible-playbook playbook.yml -v    # verbose
ansible-playbook playbook.yml -vv   # more verbose
ansible-playbook playbook.yml -vvv  # very verbose
```

### Inventory Commands

```bash
# List hosts
ansible all --list-hosts
ansible webservers --list-hosts

# View inventory graph
ansible-inventory --graph

# Export inventory
ansible-inventory --list
ansible-inventory --list --yaml

# View host variables
ansible-inventory --host hostname
```

### Vault Commands

```bash
# Create encrypted file
ansible-vault create secrets.yml

# Edit encrypted file
ansible-vault edit secrets.yml

# Encrypt existing file
ansible-vault encrypt file.yml

# Decrypt file
ansible-vault decrypt file.yml

# View encrypted file
ansible-vault view secrets.yml

# Change password
ansible-vault rekey secrets.yml

# Use vault in playbook
ansible-playbook playbook.yml --ask-vault-pass
ansible-playbook playbook.yml --vault-password-file ~/.vault_pass
```

### Galaxy Commands

```bash
# Install role
ansible-galaxy install username.rolename

# Install from requirements
ansible-galaxy install -r requirements.yml

# List installed roles
ansible-galaxy list

# Remove role
ansible-galaxy remove username.rolename

# Initialize new role
ansible-galaxy init my_role

# Search for roles
ansible-galaxy search nginx
```

### Documentation Commands

```bash
# List modules
ansible-doc -l

# Module documentation
ansible-doc module_name

# Module examples
ansible-doc -s module_name

# Plugin documentation
ansible-doc -t callback -l
```

## 📝 Playbook Syntax Reference

### Basic Playbook Structure

```yaml
---
- name: Playbook description
  hosts: target_hosts
  become: yes
  gather_facts: yes
  vars:
    var_name: value

  tasks:
    - name: Task description
      module_name:
        parameter: value
```

### Common Play Directives

```yaml
---
- name: Play name
  hosts: webservers              # Target hosts/groups
  remote_user: admin             # SSH user
  become: yes                    # Use sudo
  become_user: root              # Become this user
  become_method: sudo            # Method: sudo, su, etc.
  gather_facts: yes              # Gather system facts
  serial: 3                      # Process N hosts at a time
  max_fail_percentage: 30        # Acceptable failure rate
  connection: ssh                # Connection type
  vars:                          # Play variables
    var: value
  vars_files:                    # Variable files
    - vars/main.yml
  handlers:                      # Event handlers
    - name: Handler name
      service: name=nginx state=restarted
  pre_tasks:                     # Run before tasks
    - debug: msg="Starting"
  tasks:                         # Main tasks
    - name: Task name
      module: params
  post_tasks:                    # Run after tasks
    - debug: msg="Complete"
  tags:                          # Play tags
    - config
```

### Task Syntax

```yaml
# Basic task
- name: Task description
  module_name:
    parameter1: value1
    parameter2: value2

# With conditional
- name: Task description
  module_name:
    parameter: value
  when: condition

# With loop
- name: Task description
  module_name:
    parameter: "{{ item }}"
  loop: "{{ list_var }}"

# With handler notification
- name: Task description
  module_name:
    parameter: value
  notify: Handler name

# With delegation
- name: Task description
  module_name:
    parameter: value
  delegate_to: hostname

# With error handling
- name: Task description
  module_name:
    parameter: value
  ignore_errors: yes
  register: result
  failed_when: false
  changed_when: false

# With tags
- name: Task description
  module_name:
    parameter: value
  tags:
    - config
    - deploy
```

## 🔧 Common Modules Quick Reference

### File Operations

```yaml
# Copy file
- copy:
    src: /src/file
    dest: /dest/file
    owner: user
    group: group
    mode: '0644'

# Create directory
- file:
    path: /path/to/dir
    state: directory
    mode: '0755'

# Create symlink
- file:
    src: /source/file
    dest: /dest/link
    state: link

# Remove file/directory
- file:
    path: /path
    state: absent

# Template file
- template:
    src: template.j2
    dest: /etc/config
    mode: '0644'

# Ensure line in file
- lineinfile:
    path: /etc/file
    line: "text"
    state: present

# Block in file
- blockinfile:
    path: /etc/file
    block: |
      line 1
      line 2

# Fetch file from remote
- fetch:
    src: /remote/file
    dest: /local/dir/
```

### Package Management

```yaml
# Generic package
- package:
    name: package_name
    state: present

# APT (Debian/Ubuntu)
- apt:
    name: nginx
    state: present
    update_cache: yes

# YUM/DNF (RHEL/CentOS)
- yum:
    name: nginx
    state: present

# Multiple packages
- package:
    name:
      - nginx
      - git
      - vim
    state: present
```

### Service Management

```yaml
# Start service
- service:
    name: nginx
    state: started

# Stop service
- service:
    name: nginx
    state: stopped

# Restart service
- service:
    name: nginx
    state: restarted

# Reload service
- service:
    name: nginx
    state: reloaded

# Enable on boot
- service:
    name: nginx
    enabled: yes

# Using systemd
- systemd:
    name: nginx
    state: started
    enabled: yes
    daemon_reload: yes
```

### User Management

```yaml
# Create user
- user:
    name: username
    state: present
    shell: /bin/bash
    groups: sudo
    create_home: yes

# Create group
- group:
    name: groupname
    state: present
    gid: 1000
```

### Command Execution

```yaml
# Simple command
- command: /bin/command arg1 arg2
  args:
    chdir: /directory

# Shell command
- shell: echo $HOME
  environment:
    VAR: value

# Script execution
- script: /local/script.sh

# Raw command (no Python)
- raw: /bin/command
```

### Debug and Info

```yaml
# Print message
- debug:
    msg: "Message text"

# Print variable
- debug:
    var: variable_name

# Print with verbosity
- debug:
    msg: "Debug info"
    verbosity: 2

# Fail with message
- fail:
    msg: "Error message"

# Assert condition
- assert:
    that:
      - condition1
      - condition2
    fail_msg: "Failure message"
```

## 🔄 Conditionals

### Basic Conditionals

```yaml
# Simple condition
when: ansible_os_family == "Debian"

# Multiple conditions (AND)
when:
  - condition1
  - condition2

# OR conditions
when: condition1 or condition2

# NOT condition
when: not condition

# Variable defined
when: variable is defined

# Variable undefined
when: variable is not defined

# Comparison operators
when: ansible_memtotal_mb > 1024
when: version is version('2.0', '>=')

# In list
when: item in list_var

# String operations
when: "'substring' in string_var"
when: string_var is match("^pattern")
```

### Common Conditional Patterns

```yaml
# OS-specific
when: ansible_os_family == "Debian"
when: ansible_distribution == "Ubuntu"
when: ansible_distribution_major_version == "20"

# Fact-based
when: ansible_processor_vcpus >= 4
when: ansible_memtotal_mb > 4096

# Result-based
when: result is succeeded
when: result is failed
when: result is changed
when: result is skipped

# File existence
when: file_stat.stat.exists
when: file_stat.stat.isdir
```

## 🔁 Loops

### Simple Loop

```yaml
# Loop over list
- name: Install packages
  package:
    name: "{{ item }}"
  loop:
    - nginx
    - git
    - vim

# Loop with variable
- name: Create users
  user:
    name: "{{ item }}"
  loop: "{{ user_list }}"
```

### Loop with Dictionary

```yaml
# Loop over dictionary items
- name: Create users with details
  user:
    name: "{{ item.key }}"
    uid: "{{ item.value.uid }}"
    shell: "{{ item.value.shell }}"
  loop: "{{ users | dict2items }}"

# Loop with dict list
- name: Configure services
  service:
    name: "{{ item.name }}"
    state: "{{ item.state }}"
  loop:
    - { name: nginx, state: started }
    - { name: postgresql, state: started }
```

### Loop Control

```yaml
# With index
- debug:
    msg: "{{ item }} - Index {{ ansible_loop.index }}"
  loop: "{{ list_var }}"

# Loop label (cleaner output)
- user:
    name: "{{ item.name }}"
  loop: "{{ users }}"
  loop_control:
    label: "{{ item.name }}"

# Pause between iterations
- command: /usr/bin/process {{ item }}
  loop: "{{ items }}
  loop_control:
    pause: 3
```

## 📊 Variables

### Variable Access

```yaml
# Simple variable
{{ variable_name }}

# Dictionary access
{{ dict_var.key }}
{{ dict_var['key'] }}

# List access
{{ list_var[0] }}
{{ list_var[-1] }}

# Default value
{{ variable | default('default_value') }}

# Combine strings
{{ base_path }}/{{ sub_dir }}
```

### Jinja2 Filters

```yaml
# String operations
{{ string | upper }}
{{ string | lower }}
{{ string | title }}
{{ string | replace('old', 'new') }}

# List operations
{{ list | join(', ') }}
{{ list | unique }}
{{ list | sort }}
{{ list | length }}
{{ list | first }}
{{ list | last }}

# Math operations
{{ number | int }}
{{ number | float }}
{{ numbers | sum }}
{{ numbers | min }}
{{ numbers | max }}

# JSON/YAML
{{ data | to_json }}
{{ data | to_nice_json }}
{{ data | to_yaml }}
{{ json_string | from_json }}

# File operations
{{ path | basename }}
{{ path | dirname }}

# Default and optional
{{ var | default('default') }}
{{ var | mandatory }}

# Type checks
{{ var is defined }}
{{ var is undefined }}
{{ var is number }}
{{ var is string }}
```

## 🎨 Templates

### Template Syntax

```jinja2
{# Comment #}

{{ variable }}                    # Variable output

{% if condition %}                # Conditional
  content
{% elif condition %}
  content
{% else %}
  content
{% endif %}

{% for item in list %}            # Loop
  {{ item }}
{% endfor %}

{% set var = value %}             # Set variable

{{ var | filter }}                # Apply filter
```

### Common Template Patterns

```jinja2
# Configuration file template
# /etc/nginx/nginx.conf
user {{ nginx_user }};
worker_processes {{ nginx_workers | default('auto') }};

{% if ssl_enabled %}
ssl_protocols TLSv1.2 TLSv1.3;
{% endif %}

{% for server in servers %}
server {
    listen {{ server.port }};
    server_name {{ server.name }};
}
{% endfor %}
```

## 🏷️ Tags

### Using Tags

```yaml
# Task with tags
- name: Install nginx
  package:
    name: nginx
  tags:
    - packages
    - nginx

# Play with tags
- name: Configure servers
  hosts: all
  tags: configuration
  tasks:
    - name: Task
      command: /bin/true
```

### Run with Tags

```bash
# Run only tagged tasks
ansible-playbook playbook.yml --tags "config"

# Run multiple tags
ansible-playbook playbook.yml --tags "config,deploy"

# Skip tags
ansible-playbook playbook.yml --skip-tags "deploy"

# List tags
ansible-playbook playbook.yml --list-tags
```

### Special Tags

```yaml
# Always run (even with --tags)
tags: always

# Never run (unless specifically requested)
tags: never

# Tagged tasks
tags: tagged

# Untagged tasks
tags: untagged
```

## 🎯 Host Patterns

```bash
# All hosts
ansible all -m ping

# Single host
ansible hostname -m ping

# Single group
ansible webservers -m ping

# Multiple groups (OR)
ansible webservers,databases -m ping

# Intersection (AND)
ansible webservers:&production -m ping

# Exclusion (NOT)
ansible webservers:!staging -m ping

# Wildcard
ansible web* -m ping
ansible *.example.com -m ping

# Regex
ansible ~web[0-9]+ -m ping

# Index
ansible webservers[0] -m ping       # First
ansible webservers[-1] -m ping      # Last
ansible webservers[0:2] -m ping     # Range

# Complex
ansible webservers:&production:!web3 -m ping
```

## 📖 Facts Reference

### Common Facts

```yaml
# System
ansible_hostname
ansible_fqdn
ansible_domain
ansible_nodename

# OS
ansible_os_family              # Debian, RedHat, etc.
ansible_distribution           # Ubuntu, CentOS, etc.
ansible_distribution_version   # 20.04, 8.3, etc.
ansible_distribution_major_version
ansible_kernel
ansible_architecture

# Hardware
ansible_processor_vcpus
ansible_processor_cores
ansible_memtotal_mb
ansible_memfree_mb
ansible_swaptotal_mb

# Network
ansible_default_ipv4.address
ansible_default_ipv4.interface
ansible_all_ipv4_addresses
ansible_all_ipv6_addresses
ansible_interfaces

# Storage
ansible_mounts
ansible_devices

# Date/Time
ansible_date_time.iso8601
ansible_date_time.epoch

# Environment
ansible_env
ansible_user_id
ansible_user_dir
```

## 🚀 Performance Tips

```yaml
# Disable facts when not needed
gather_facts: no

# Increase parallelism
forks = 50

# Use async for long tasks
async: 3600
poll: 0

# Batch package installation
package:
  name:
    - pkg1
    - pkg2
    - pkg3

# Enable pipelining (ansible.cfg)
pipelining = True

# Use fact caching
gathering = smart
fact_caching = jsonfile
```

## 📚 Common Patterns

### Error Handling

```yaml
# Ignore errors
ignore_errors: yes

# Custom failure condition
failed_when: "'error' in result.stdout"

# Block/Rescue/Always
block:
  - name: Task
    command: /bin/task
rescue:
  - name: On failure
    command: /bin/recover
always:
  - name: Always run
    command: /bin/cleanup
```

### Retry Logic

```yaml
# Retry until success
- name: Wait for service
  uri:
    url: http://localhost
  register: result
  until: result.status == 200
  retries: 10
  delay: 5
```

### Delegation

```yaml
# Run on different host
delegate_to: localhost

# Run once for all hosts
run_once: yes

# Local action
local_action:
  module: command
  cmd: /usr/bin/local_command
```

## 🔐 Security Patterns

```yaml
# Vault encrypted variable
database_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          ...

# Prompt for variable
vars_prompt:
  - name: username
    prompt: "Enter username"
    private: no
  - name: password
    prompt: "Enter password"
    private: yes

# No log (hide sensitive output)
- name: Set password
  user:
    name: user
    password: "{{ password }}"
  no_log: true
```

---

**Quick Tip**: Bookmark this page or keep it open in a browser tab while working with Ansible!

For detailed information on any topic, refer back to the relevant chapter in the full tutorial.
