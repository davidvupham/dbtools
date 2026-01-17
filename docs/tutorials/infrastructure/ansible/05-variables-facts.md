# Chapter 5: Variables and Facts

Variables make your playbooks dynamic and reusable. Instead of hardcoding values, you use variables that can change based on the environment, host, or user input. In this chapter, you'll master variables and discover Ansible facts.

## 🎯 Learning Objectives

By the end of this chapter, you will:

- Define and use variables in playbooks
- Understand variable precedence
- Use Ansible facts effectively
- Register variables from task output
- Work with special variables
- Use variable files for better organization

## 📖 What are Variables?

**Variables** store values that can change. Instead of writing:

```yaml
- name: Install package
  package:
    name: nginx
```

You can write:

```yaml
- name: Install package
  package:
    name: "{{ package_name }}"
```

Now `package_name` can be different for different hosts or environments.

## 📝 Defining Variables

### In Playbooks (vars)

```yaml
---
- name: Example with variables
  hosts: localhost
  vars:
    package_name: nginx
    http_port: 80
    max_clients: 200

  tasks:
    - name: Install {{ package_name }}
      package:
        name: "{{ package_name }}"
        state: present
```

### In Separate Files (vars_files)

**playbook.yml**:
```yaml
---
- name: Example with variable files
  hosts: webservers
  vars_files:
    - vars/common.yml
    - vars/webserver.yml

  tasks:
    - name: Install {{ package_name }}
      package:
        name: "{{ package_name }}"
        state: present
```

**vars/common.yml**:
```yaml
---
ansible_user: admin
backup_enabled: true
```

**vars/webserver.yml**:
```yaml
---
package_name: nginx
http_port: 80
ssl_port: 443
```

### In Inventory

Already covered in Chapter 2, but as a reminder:

```ini
[webservers]
web1 http_port=8080
web2 http_port=8081

[webservers:vars]
package_name=nginx
max_clients=200
```

### Command Line (Extra Vars)

```bash
# Pass variables at runtime
ansible-playbook playbook.yml -e "package_name=apache2"

# Pass multiple variables
ansible-playbook playbook.yml -e "package_name=nginx http_port=8080"

# Pass JSON variables
ansible-playbook playbook.yml -e '{"package_name":"nginx","http_port":8080}'

# Pass variables from file
ansible-playbook playbook.yml -e "@vars/production.yml"
```

## 🔢 Using Variables

### Basic Syntax

```yaml
# In task parameters
- name: Create directory
  file:
    path: "{{ directory_path }}"
    state: directory

# In task names (for readability)
- name: "Install {{ package_name }} on {{ ansible_hostname }}"
  package:
    name: "{{ package_name }}"

# In strings (must quote the entire string)
- name: Create file
  copy:
    content: "Welcome to {{ server_name }}"
    dest: /tmp/welcome.txt
```

### Important Quoting Rules

```yaml
# ✅ CORRECT - quoted when starts with variable
path: "{{ base_path }}/subdir"

# ✅ CORRECT - not quoted when variable is not first
path: /home/{{ username }}/files

# ❌ WRONG - not quoted when starts with variable
path: {{ base_path }}/subdir

# ✅ CORRECT - quote entire string with variable
message: "Hello {{ name }}, welcome!"

# ❌ WRONG - unquoted string with variable
message: Hello {{ name }}, welcome!
```

## 📊 Variable Types

### Strings

```yaml
vars:
  server_name: "web01"
  message: "Hello, Ansible!"
  multiline_text: |
    Line 1
    Line 2
    Line 3
```

### Numbers

```yaml
vars:
  http_port: 80
  max_connections: 1000
  timeout: 30.5
```

### Booleans

```yaml
vars:
  ssl_enabled: true
  backup_enabled: false
  debug_mode: yes  # yes/no same as true/false
```

### Lists (Arrays)

```yaml
vars:
  packages:
    - nginx
    - git
    - vim

  ports:
    - 80
    - 443
    - 8080

# Using lists in tasks
tasks:
  - name: Install multiple packages
    package:
      name: "{{ item }}"
      state: present
    loop: "{{ packages }}"
```

### Dictionaries (Hashes)

```yaml
vars:
  database:
    host: localhost
    port: 5432
    name: myapp
    user: dbuser

  server_config:
    hostname: web01
    ip: 192.168.1.10
    services:
      - nginx
      - postgresql

# Accessing dictionary values
tasks:
  - name: "Connect to {{ database.host }}:{{ database.port }}"
    debug:
      msg: "Connecting to {{ database.host }} port {{ database.port }}"
```

## 🎯 Ansible Facts

**Facts** are variables automatically discovered by Ansible about managed hosts.

### Gathering Facts

Ansible automatically gathers facts at the start of each play:

```yaml
---
- name: Example play
  hosts: all

  tasks:
    - name: Display OS
      debug:
        msg: "This is {{ ansible_distribution }} {{ ansible_distribution_version }}"
```

### Viewing All Facts

```bash
# View all facts for a host
ansible hostname -m setup

# View specific facts
ansible hostname -m setup -a "filter=ansible_os_family"
ansible hostname -m setup -a "filter=ansible_all_ipv4_addresses"
```

### Common Facts

```yaml
# System Facts
ansible_hostname          # Short hostname
ansible_fqdn             # Fully qualified domain name
ansible_os_family        # Debian, RedHat, etc.
ansible_distribution     # Ubuntu, CentOS, etc.
ansible_distribution_version  # 20.04, 8.3, etc.
ansible_kernel           # Kernel version

# Hardware Facts
ansible_processor_vcpus  # Number of CPU cores
ansible_memtotal_mb      # Total RAM in MB
ansible_architecture     # x86_64, arm64, etc.

# Network Facts
ansible_default_ipv4.address      # Primary IP address
ansible_all_ipv4_addresses        # All IP addresses
ansible_interfaces                # Network interfaces
ansible_hostname                  # Hostname

# Storage Facts
ansible_mounts           # Mounted filesystems
ansible_devices          # Block devices

# Environment
ansible_env              # Environment variables
ansible_user_id          # Current user
```

### Using Facts in Tasks

```yaml
---
- name: Example using facts
  hosts: all

  tasks:
    - name: Display system info
      debug:
        msg: |
          Hostname: {{ ansible_hostname }}
          OS: {{ ansible_distribution }} {{ ansible_distribution_version }}
          IP: {{ ansible_default_ipv4.address }}
          RAM: {{ ansible_memtotal_mb }} MB
          CPUs: {{ ansible_processor_vcpus }}

    - name: Install package based on OS
      package:
        name: "{{ 'httpd' if ansible_os_family == 'RedHat' else 'apache2' }}"
        state: present
      become: yes
```

### Disabling Fact Gathering

For faster playbook runs when facts aren't needed:

```yaml
---
- name: Playbook without facts
  hosts: all
  gather_facts: no

  tasks:
    - name: Simple task
      debug:
        msg: "No facts gathered"
```

### Custom Facts

Create custom facts by placing JSON/INI files in `/etc/ansible/facts.d/`:

**/etc/ansible/facts.d/app.fact**:
```json
{
  "app_version": "2.1.0",
  "environment": "production"
}
```

Access in playbooks:
```yaml
- name: Display custom fact
  debug:
    msg: "App version: {{ ansible_local.app.app_version }}"
```

## 📝 Registering Variables

Capture output from tasks using `register`:

```yaml
---
- name: Register variables example
  hosts: localhost

  tasks:
    - name: Get current date
      command: date
      register: current_date

    - name: Display date
      debug:
        msg: "The date is: {{ current_date.stdout }}"

    - name: Check if file exists
      stat:
        path: /etc/passwd
      register: file_status

    - name: Display file info
      debug:
        msg: "File exists: {{ file_status.stat.exists }}"

    - name: Run command and capture
      shell: "df -h /"
      register: disk_space

    - name: Show disk space
      debug:
        var: disk_space.stdout_lines
```

### Registered Variable Structure

```yaml
registered_var:
  changed: true/false
  failed: true/false
  rc: 0                  # Return code
  stdout: "output"       # Standard output
  stderr: "errors"       # Standard error
  stdout_lines: []       # Output as list
  stderr_lines: []       # Errors as list
```

## 🎚️ Variable Precedence

When the same variable is defined in multiple places, Ansible uses this precedence (from lowest to highest):

1. Command line values (lowest)
2. Role defaults
3. Inventory file or script group vars
4. Inventory group_vars/all
5. Playbook group_vars/all
6. Inventory group_vars/*
7. Playbook group_vars/*
8. Inventory file or script host vars
9. Inventory host_vars/*
10. Playbook host_vars/*
11. Host facts / cached set_facts
12. Play vars
13. Play vars_prompt
14. Play vars_files
15. Role vars (defined in role/vars/main.yml)
16. Block vars (only for tasks in block)
17. Task vars (only for the task)
18. Include_vars
19. Set_facts / registered vars
20. Role (and include_role) params
21. Include params
22. Extra vars (highest - always win, `-e`)

**Key Points**:
- Extra vars (`-e`) always win
- Task vars override play vars
- Host vars override group vars

## 🔒 Special Variables

Ansible provides special variables you can use:

### Inventory Variables

```yaml
inventory_hostname        # Hostname as defined in inventory
inventory_hostname_short  # Short hostname
group_names              # List of groups this host is in
groups                   # All groups and hosts in inventory
play_hosts              # List of hosts in current play
```

### Magic Variables

```yaml
hostvars                 # Access facts/vars of other hosts
ansible_play_hosts      # All hosts in current play
ansible_play_batch      # Hosts in current batch
ansible_version         # Ansible version info
```

### Example Using Special Variables

```yaml
---
- name: Special variables example
  hosts: all

  tasks:
    - name: Display inventory hostname
      debug:
        msg: "I am {{ inventory_hostname }}"

    - name: Display groups
      debug:
        msg: "I belong to: {{ group_names }}"

    - name: Access another host's IP
      debug:
        msg: "Web server IP is {{ hostvars['webserver1']['ansible_default_ipv4']['address'] }}"
      when: inventory_hostname != 'webserver1'

    - name: List all webservers
      debug:
        msg: "Webservers: {{ groups['webservers'] }}"
```

## 🛠️ Exercises

### Exercise 5.1: Basic Variables

**Task**: Create a playbook using variables for package installation.

```yaml
---
- name: Install packages with variables
  hosts: localhost
  connection: local
  become: yes
  vars:
    packages_to_install:
      - curl
      - wget
      - vim
    install_location: /usr/local/bin

  tasks:
    - name: Install packages
      package:
        name: "{{ item }}"
        state: present
      loop: "{{ packages_to_install }}"

    - name: Display installation location
      debug:
        msg: "Packages installed, binaries typically in {{ install_location }}"
```

---

### Exercise 5.2: Variable Files

**Task**: Organize variables in separate files.

**Directory structure**:
```text
.
├── playbook.yml
└── vars/
    ├── common.yml
    └── webserver.yml
```

**vars/common.yml**:
```yaml
---
app_name: myapp
app_version: "1.0.0"
log_level: info
```

**vars/webserver.yml**:
```yaml
---
http_port: 8080
https_port: 8443
worker_processes: 4
```

**playbook.yml**:
```yaml
---
- name: Deploy application
  hosts: localhost
  connection: local
  vars_files:
    - vars/common.yml
    - vars/webserver.yml

  tasks:
    - name: Display configuration
      debug:
        msg: |
          Application: {{ app_name }} v{{ app_version }}
          HTTP Port: {{ http_port }}
          HTTPS Port: {{ https_port }}
          Workers: {{ worker_processes }}
          Log Level: {{ log_level }}
```

---

### Exercise 5.3: Using Facts

**Task**: Create a playbook that uses Ansible facts.

```yaml
---
- name: System information report
  hosts: localhost
  connection: local

  tasks:
    - name: Create system report
      copy:
        content: |
          System Information Report
          ========================

          Hostname: {{ ansible_hostname }}
          FQDN: {{ ansible_fqdn }}
          Operating System: {{ ansible_distribution }} {{ ansible_distribution_version }}
          Kernel: {{ ansible_kernel }}
          Architecture: {{ ansible_architecture }}

          Hardware:
          - CPUs: {{ ansible_processor_vcpus }}
          - RAM: {{ ansible_memtotal_mb }} MB

          Network:
          - Primary IP: {{ ansible_default_ipv4.address }}
          - All IPs: {{ ansible_all_ipv4_addresses | join(', ') }}

          Generated on: {{ ansible_date_time.iso8601 }}
        dest: /tmp/system_report.txt

    - name: Display report location
      debug:
        msg: "Report created at /tmp/system_report.txt"
```

---

### Exercise 5.4: Registered Variables

**Task**: Use registered variables to make decisions.

```yaml
---
- name: Check and report disk space
  hosts: localhost
  connection: local

  tasks:
    - name: Check disk usage of root partition
      shell: df -h / | tail -1 | awk '{print $5}' | sed 's/%//'
      register: disk_usage
      changed_when: false

    - name: Display disk usage
      debug:
        msg: "Root partition is {{ disk_usage.stdout }}% full"

    - name: Warning if disk is over 80%
      debug:
        msg: "⚠️ WARNING: Disk usage is high!"
      when: disk_usage.stdout | int > 80

    - name: OK message if disk under 80%
      debug:
        msg: "✓ Disk usage is within normal range"
      when: disk_usage.stdout | int <= 80

    - name: Get list of large files
      shell: "find /var/log -type f -size +10M -exec ls -lh {} \\; 2>/dev/null | awk '{print $9, $5}'"
      register: large_files
      changed_when: false
      when: disk_usage.stdout | int > 80

    - name: Display large files
      debug:
        msg: "Large files:\n{{ large_files.stdout }}"
      when:
        - disk_usage.stdout | int > 80
        - large_files.stdout != ""
```

---

### Exercise 5.5: Dictionary Variables

**Task**: Work with complex dictionary variables.

```yaml
---
- name: Configure multiple applications
  hosts: localhost
  connection: local
  vars:
    applications:
      web:
        name: nginx
        port: 80
        ssl_port: 443
        enabled: true
      database:
        name: postgresql
        port: 5432
        enabled: true
      cache:
        name: redis
        port: 6379
        enabled: false

  tasks:
    - name: Display application info
      debug:
        msg: |
          Application: {{ item.value.name }}
          Port: {{ item.value.port }}
          Enabled: {{ item.value.enabled }}
      loop: "{{ applications | dict2items }}"

    - name: Create config files for enabled apps
      copy:
        content: |
          # Configuration for {{ item.value.name }}
          Port={{ item.value.port }}
          {% if item.value.ssl_port is defined %}
          SSL_Port={{ item.value.ssl_port }}
          {% endif %}
        dest: "/tmp/{{ item.value.name }}.conf"
      loop: "{{ applications | dict2items }}"
      when: item.value.enabled
```

---

### Exercise 5.6: Variable Precedence

**Task**: Understand variable precedence by testing different sources.

**inventory**:
```ini
[testservers]
test1 ansible_connection=local my_var="from_inventory_host"

[testservers:vars]
my_var="from_inventory_group"
```

**group_vars/testservers.yml**:
```yaml
---
my_var: "from_group_vars"
```

**playbook.yml**:
```yaml
---
- name: Variable precedence test
  hosts: testservers
  vars:
    my_var: "from_play_vars"

  tasks:
    - name: Display variable (will be from play vars)
      debug:
        msg: "my_var = {{ my_var }}"

    - name: Override with task var
      debug:
        msg: "my_var = {{ my_var }}"
      vars:
        my_var: "from_task_vars"

    - name: Override with set_fact
      set_fact:
        my_var: "from_set_fact"

    - name: Display after set_fact
      debug:
        msg: "my_var = {{ my_var }}"

- name: Run with extra vars
  hosts: testservers

  tasks:
    - name: Display variable (try with -e)
      debug:
        msg: "my_var = {{ my_var | default('not set') }}"
```

**Run tests**:
```bash
# Test with different precedence levels
ansible-playbook -i inventory playbook.yml

# Extra vars win over everything
ansible-playbook -i inventory playbook.yml -e "my_var=from_extra_vars"
```

---

## 🔧 Troubleshooting

### Problem: Variable Not Defined

**Error**: "The task includes an option with an undefined variable"

**Solutions**:
```yaml
# Use default value
- debug:
    msg: "{{ my_var | default('default_value') }}"

# Check if variable is defined
- debug:
    msg: "{{ my_var }}"
  when: my_var is defined

# Define variable with default
vars:
  my_var: "{{ my_var | default('default') }}"
```

### Problem: Variable Not Expanding

**Error**: Shows `{{ variable }}` instead of value

**Solution**: Quote the string properly:
```yaml
# ❌ WRONG
path: {{ base_dir }}/file

# ✅ CORRECT
path: "{{ base_dir }}/file"
```

### Problem: Dictionary Key Error

**Error**: "dict object has no attribute 'key'"

**Solution**: Check if key exists:
```yaml
# Use default
- debug:
    msg: "{{ my_dict.key | default('not found') }}"

# Check existence
- debug:
    msg: "{{ my_dict.key }}"
  when: my_dict.key is defined
```

## 📖 Key Takeaways

✅ Variables make playbooks dynamic and reusable
✅ Use `{{ variable }}` syntax to reference variables
✅ Quote strings that start with variables
✅ Facts are automatically discovered system information
✅ Use `register` to capture task output
✅ Variable precedence: extra vars always win
✅ Special variables provide context about hosts and inventory
✅ Organize variables in separate files for better management

## 🎓 What's Next?

Now that you understand variables, you're ready to add logic to your playbooks with conditionals and loops.

**Next Chapter**: [Chapter 6: Conditionals and Loops](06-conditionals-loops.md)

In the next chapter, you'll learn:
- Using when conditions
- Different types of loops
- Combining conditionals and loops
- Until loops for retrying tasks

---

**Practice Makes Perfect!** Experiment with different variable types and see how they interact.
