# Chapter 6: Conditionals and Loops

Control flow in Ansible allows you to make decisions and repeat tasks. This chapter covers when statements, loop constructs, and combining them for powerful automation.

## Learning Objectives

By the end of this chapter, you will:

- Use `when` statements for conditional task execution
- Implement various loop types
- Combine conditionals with loops
- Use registered variables in conditionals
- Apply complex conditional logic

## Conditionals with `when`

The `when` statement allows tasks to run only when specific conditions are met.

### Basic Conditionals

```yaml
---
- name: Conditional examples
  hosts: all
  become: yes

  tasks:
    - name: Install Apache on RedHat systems
      package:
        name: httpd
        state: present
      when: ansible_os_family == "RedHat"

    - name: Install Apache on Debian systems
      package:
        name: apache2
        state: present
      when: ansible_os_family == "Debian"
```

### Comparison Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `==` | Equal | `ansible_os_family == "RedHat"` |
| `!=` | Not equal | `ansible_distribution != "Ubuntu"` |
| `>` | Greater than | `ansible_memtotal_mb > 2048` |
| `<` | Less than | `ansible_processor_vcpus < 4` |
| `>=` | Greater or equal | `ansible_distribution_major_version >= "8"` |
| `<=` | Less or equal | `item.value <= 100` |
| `in` | Contains | `"web" in group_names` |
| `not in` | Does not contain | `"test" not in inventory_hostname` |

### Multiple Conditions

```yaml
# AND - both conditions must be true
- name: Install on RHEL 8+
  package:
    name: podman
    state: present
  when:
    - ansible_distribution == "RedHat"
    - ansible_distribution_major_version | int >= 8

# OR - either condition can be true
- name: Install on RHEL or CentOS
  package:
    name: httpd
    state: present
  when: ansible_distribution == "RedHat" or ansible_distribution == "CentOS"

# Combined AND/OR with parentheses
- name: Complex condition
  debug:
    msg: "This is a production web server"
  when: >
    (inventory_hostname in groups['webservers']) and
    (inventory_hostname in groups['production'] or
     env == 'production')
```

### Testing Variables

```yaml
- name: Run if variable is defined
  debug:
    msg: "Database host is {{ db_host }}"
  when: db_host is defined

- name: Run if variable is NOT defined
  set_fact:
    db_host: localhost
  when: db_host is not defined

- name: Check if variable is empty
  debug:
    msg: "Users list is empty"
  when: users | length == 0

- name: Check boolean variable
  service:
    name: httpd
    state: started
  when: enable_webserver | bool

- name: Check if file exists (using stat)
  stat:
    path: /etc/config.yml
  register: config_file

- name: Process config if it exists
  include_tasks: process_config.yml
  when: config_file.stat.exists
```

### Using Registered Variables

```yaml
- name: Check service status
  command: systemctl is-active httpd
  register: httpd_status
  ignore_errors: yes
  changed_when: false

- name: Start httpd if not running
  service:
    name: httpd
    state: started
  when: httpd_status.rc != 0

- name: Check command output
  command: cat /etc/release
  register: release_info
  changed_when: false

- name: Show message for specific release
  debug:
    msg: "Running on CentOS"
  when: "'CentOS' in release_info.stdout"
```

## Loops

Loops allow you to repeat tasks with different values.

### Basic Loop

```yaml
- name: Create multiple users
  user:
    name: "{{ item }}"
    state: present
  loop:
    - alice
    - bob
    - charlie

- name: Install multiple packages
  package:
    name: "{{ item }}"
    state: present
  loop:
    - nginx
    - php
    - mysql-server
```

### Loop with Dictionaries

```yaml
- name: Create users with specific properties
  user:
    name: "{{ item.name }}"
    uid: "{{ item.uid }}"
    groups: "{{ item.groups }}"
    shell: "{{ item.shell | default('/bin/bash') }}"
  loop:
    - { name: 'alice', uid: 1001, groups: 'developers' }
    - { name: 'bob', uid: 1002, groups: 'admins' }
    - { name: 'charlie', uid: 1003, groups: 'developers,admins' }

# More readable YAML format
- name: Create users with properties
  user:
    name: "{{ item.name }}"
    uid: "{{ item.uid }}"
    groups: "{{ item.groups }}"
  loop:
    - name: alice
      uid: 1001
      groups: developers
    - name: bob
      uid: 1002
      groups: admins
```

### Loop with Index

```yaml
- name: Create numbered files
  copy:
    content: "File number {{ index }}: {{ item }}"
    dest: "/tmp/file_{{ index }}.txt"
  loop:
    - first
    - second
    - third
  loop_control:
    index_var: index
```

### Loop Control

```yaml
- name: Process items with control
  debug:
    msg: "Processing {{ item }}"
  loop: "{{ large_list }}"
  loop_control:
    label: "{{ item.name }}"      # Display this instead of full item
    pause: 2                       # Pause 2 seconds between iterations
    index_var: idx                 # Access loop index as 'idx'
    loop_var: server              # Rename 'item' to 'server'

# Using renamed loop variable
- name: Configure servers
  include_tasks: setup_server.yml
  loop: "{{ servers }}"
  loop_control:
    loop_var: server
```

### Looping Over Dictionaries

```yaml
vars:
  users:
    alice:
      uid: 1001
      shell: /bin/bash
    bob:
      uid: 1002
      shell: /bin/zsh

tasks:
  - name: Create users from dictionary
    user:
      name: "{{ item.key }}"
      uid: "{{ item.value.uid }}"
      shell: "{{ item.value.shell }}"
    loop: "{{ users | dict2items }}"

  # Alternative: loop over keys only
  - name: Display usernames
    debug:
      msg: "User: {{ item }}"
    loop: "{{ users.keys() | list }}"
```

### Nested Loops

```yaml
- name: Create directories for each user
  file:
    path: "/home/{{ item.0 }}/{{ item.1 }}"
    state: directory
    owner: "{{ item.0 }}"
  loop: "{{ users | product(directories) | list }}"
  vars:
    users:
      - alice
      - bob
    directories:
      - documents
      - downloads
      - projects
```

### Loop with Sequence

```yaml
- name: Create numbered directories
  file:
    path: "/data/dir_{{ item }}"
    state: directory
  loop: "{{ range(1, 6) | list }}"  # Creates dir_1 through dir_5

# With formatting
- name: Create servers
  debug:
    msg: "Server: web{{ '%02d' | format(item) }}"
  loop: "{{ range(1, 11) | list }}"  # web01 through web10
```

### Looping Over Files

```yaml
- name: Copy all config files
  copy:
    src: "{{ item }}"
    dest: /etc/myapp/
  with_fileglob:
    - "configs/*.conf"

- name: Process template files
  template:
    src: "{{ item }}"
    dest: "/etc/myapp/{{ item | basename | regex_replace('.j2$', '') }}"
  with_fileglob:
    - "templates/*.j2"
```

## Combining Conditionals and Loops

```yaml
- name: Install packages only if needed
  package:
    name: "{{ item }}"
    state: present
  loop:
    - nginx
    - mysql-server
    - php
  when: install_webstack | bool

- name: Configure services based on type
  service:
    name: "{{ item.name }}"
    state: "{{ item.state }}"
    enabled: "{{ item.enabled }}"
  loop:
    - { name: nginx, state: started, enabled: yes, type: web }
    - { name: mysql, state: started, enabled: yes, type: db }
    - { name: redis, state: stopped, enabled: no, type: cache }
  when: item.type in enabled_services

- name: Create users on specific hosts
  user:
    name: "{{ item }}"
    state: present
  loop: "{{ admin_users }}"
  when: inventory_hostname in groups['admin_servers']
```

## Practical Examples

### Example 1: Conditional Package Installation

```yaml
---
- name: Cross-platform package installation
  hosts: all
  become: yes

  vars:
    common_packages:
      - vim
      - git
      - curl

  tasks:
    - name: Install packages on RedHat
      dnf:
        name: "{{ common_packages }}"
        state: present
      when: ansible_os_family == "RedHat"

    - name: Install packages on Debian
      apt:
        name: "{{ common_packages }}"
        state: present
        update_cache: yes
      when: ansible_os_family == "Debian"
```

### Example 2: User Management with Conditions

```yaml
---
- name: Manage users across environments
  hosts: all
  become: yes

  vars:
    users:
      - name: deploy
        groups: wheel
        state: present
        environments: [production, staging]
      - name: developer
        groups: developers
        state: present
        environments: [development, staging]
      - name: testuser
        groups: testers
        state: present
        environments: [development]

  tasks:
    - name: Create users for this environment
      user:
        name: "{{ item.name }}"
        groups: "{{ item.groups }}"
        state: "{{ item.state }}"
      loop: "{{ users }}"
      when: current_environment in item.environments
```

### Example 3: Service Configuration Based on Memory

```yaml
---
- name: Configure services based on resources
  hosts: all
  become: yes

  tasks:
    - name: Set MySQL buffer pool size
      lineinfile:
        path: /etc/mysql/my.cnf
        regexp: '^innodb_buffer_pool_size'
        line: "innodb_buffer_pool_size = {{ mysql_buffer_size }}"
      vars:
        mysql_buffer_size: "{{ '256M' if ansible_memtotal_mb < 2048 else '1G' if ansible_memtotal_mb < 8192 else '4G' }}"
      when: "'databases' in group_names"
      notify: Restart MySQL

  handlers:
    - name: Restart MySQL
      service:
        name: mysql
        state: restarted
```

## Exercises

### Exercise 6.1: Conditional Package Installation

Create a playbook that:
1. Installs `httpd` on RedHat systems and `apache2` on Debian systems
2. Installs `firewalld` only if the system has more than 1GB RAM
3. Installs development tools only on hosts in the `dev` group

### Exercise 6.2: Loop-Based User Creation

Create a playbook that:
1. Creates users from a list with name, uid, groups, and shell
2. Creates home directories only for users with `create_home: true`
3. Sets passwords only for users with passwords defined

### Exercise 6.3: Complex Conditional Logic

Create a playbook that:
1. Configures NTP differently based on OS and environment
2. Sets up monitoring agents only on production servers
3. Applies security hardening only on internet-facing servers

## Key Takeaways

- Use `when` for conditional task execution
- Conditions can test facts, variables, and registered results
- Multiple conditions can be combined with `and`/`or`
- `loop` replaces the older `with_*` constructs
- Use `loop_control` for customizing loop behavior
- Combine conditionals and loops for powerful automation
- Test conditions using `is defined`, `is not defined`, `| bool`

## What's Next?

In the next chapter, you'll learn about handlers for event-driven task execution.

**Next Chapter**: [Chapter 7: Handlers and Tasks](07-handlers.md)
