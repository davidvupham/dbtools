# Chapter 4: Playbooks Basics

Playbooks are Ansible's configuration, deployment, and orchestration language. They turn ad-hoc commands into repeatable, documented automation. In this chapter, you'll learn to write your first playbooks and understand their structure.

## 🎯 Learning Objectives

By the end of this chapter, you will:

- Understand what playbooks are and when to use them
- Learn YAML syntax essentials
- Create and structure playbooks
- Use tasks, plays, and modules in playbooks
- Run and debug playbooks
- Understand idempotency in playbooks

## 📖 What is a Playbook?

A **playbook** is a YAML file that defines automation tasks. Think of it as a recipe or script that describes the desired state of your systems.

### Playbook vs Ad-Hoc Commands

| Ad-Hoc Commands | Playbooks |
|-----------------|-----------|
| One-time tasks | Repeatable automation |
| Not saved | Version controlled |
| Single module | Multiple tasks |
| Quick fixes | Documented processes |
| No error handling | Structured error handling |

**When to use playbooks**:
- ✅ Complex multi-step operations
- ✅ Repeatable tasks
- ✅ Configuration management
- ✅ Application deployment
- ✅ Orchestrated workflows

## 📝 YAML Syntax Basics

Playbooks use YAML (YAML Ain't Markup Language), a human-readable data format.

### YAML Fundamentals

**Key-Value Pairs**:
```yaml
name: webserver
port: 80
enabled: true
```

**Lists** (arrays):
```yaml
fruits:
  - apple
  - banana
  - orange

# Or inline
fruits: [apple, banana, orange]
```

**Dictionaries** (nested structures):
```yaml
server:
  name: web01
  ip: 192.168.1.10
  ports:
    - 80
    - 443
```

**Multiline Strings**:
```yaml
# Literal block (preserves newlines)
description: |
  This is a long description
  that spans multiple lines
  and preserves newlines.

# Folded block (folds newlines into spaces)
summary: >
  This is also a long text
  but newlines will be
  converted to spaces.
```

### YAML Important Rules

1. **Indentation**: Use spaces, not tabs (2 spaces is standard)
2. **Colons**: Key-value pairs need a space after the colon
3. **Dashes**: List items start with a dash and space
4. **Case sensitive**: `Name` ≠ `name`
5. **Comments**: Use `#` for comments

### Common YAML Mistakes

```yaml
# ❌ WRONG - no space after colon
name:webserver

# ✅ CORRECT
name: webserver

# ❌ WRONG - using tabs
	name: webserver

# ✅ CORRECT - using spaces
  name: webserver

# ❌ WRONG - inconsistent indentation
tasks:
  - name: Task 1
   command: date

# ✅ CORRECT - consistent indentation
tasks:
  - name: Task 1
    command: date
```

## 📄 Playbook Structure

A basic playbook structure:

```yaml
---
- name: Playbook Name
  hosts: target_hosts
  become: yes
  vars:
    variable_name: value

  tasks:
    - name: Task description
      module_name:
        parameter1: value1
        parameter2: value2
```

**Components**:
- `---`: Document start marker (optional but recommended)
- `name`: Human-readable description
- `hosts`: Which inventory hosts/groups to target
- `become`: Whether to use privilege escalation (sudo)
- `vars`: Variables defined for this play
- `tasks`: List of actions to perform

## 🎬 Your First Playbook

Let's create a simple playbook:

**first_playbook.yml**:
```yaml
---
- name: My First Playbook
  hosts: localhost
  connection: local

  tasks:
    - name: Print hello message
      debug:
        msg: "Hello, Ansible!"

    - name: Display the date
      command: date

    - name: Create a test file
      file:
        path: /tmp/ansible-test.txt
        state: touch
```

### Running the Playbook

```bash
ansible-playbook first_playbook.yml
```

**Output**:
```text
PLAY [My First Playbook] **********************

TASK [Gathering Facts] ************************
ok: [localhost]

TASK [Print hello message] ********************
ok: [localhost] => {
    "msg": "Hello, Ansible!"
}

TASK [Display the date] ***********************
changed: [localhost]

TASK [Create a test file] *********************
changed: [localhost]

PLAY RECAP ************************************
localhost  : ok=4  changed=2  unreachable=0  failed=0
```

## 🔍 Understanding Playbook Components

### The Play

A **play** is a mapping of hosts to tasks:

```yaml
---
- name: Configure web servers
  hosts: webservers
  become: yes

  tasks:
    # Tasks go here

- name: Configure database servers
  hosts: databases
  become: yes

  tasks:
    # Different tasks for databases
```

A playbook can contain multiple plays.

### Tasks

**Tasks** are actions to execute. Each task uses a module:

```yaml
tasks:
  - name: Install nginx
    package:
      name: nginx
      state: present

  - name: Start nginx service
    service:
      name: nginx
      state: started
      enabled: yes
```

**Task anatomy**:
- `name`: Description (optional but highly recommended)
- Module name (`package`, `service`, etc.)
- Module parameters (indented under module name)

### Multiple Parameter Formats

**Format 1 - Dictionary style** (recommended):
```yaml
- name: Copy configuration file
  copy:
    src: /tmp/config.conf
    dest: /etc/app/config.conf
    owner: root
    group: root
    mode: '0644'
```

**Format 2 - Inline style**:
```yaml
- name: Copy configuration file
  copy: src=/tmp/config.conf dest=/etc/app/config.conf owner=root mode='0644'
```

Use dictionary style for better readability!

## 🎯 Practical Playbook Examples

### Example 1: System Updates

**system_update.yml**:
```yaml
---
- name: Update all systems
  hosts: all
  become: yes

  tasks:
    - name: Update apt cache (Debian/Ubuntu)
      apt:
        update_cache: yes
        cache_valid_time: 3600
      when: ansible_os_family == "Debian"

    - name: Upgrade all packages (Debian/Ubuntu)
      apt:
        upgrade: dist
      when: ansible_os_family == "Debian"

    - name: Update yum cache (RHEL/CentOS)
      yum:
        update_cache: yes
      when: ansible_os_family == "RedHat"

    - name: Upgrade all packages (RHEL/CentOS)
      yum:
        name: '*'
        state: latest
      when: ansible_os_family == "RedHat"
```

### Example 2: Web Server Setup

**webserver.yml**:
```yaml
---
- name: Configure web server
  hosts: webservers
  become: yes

  tasks:
    - name: Install nginx
      package:
        name: nginx
        state: present

    - name: Create web root directory
      file:
        path: /var/www/html
        state: directory
        owner: www-data
        group: www-data
        mode: '0755'

    - name: Deploy index page
      copy:
        content: |
          <html>
          <head><title>Welcome</title></head>
          <body>
            <h1>Hello from Ansible!</h1>
            <p>Server: {{ ansible_hostname }}</p>
          </body>
          </html>
        dest: /var/www/html/index.html
        owner: www-data
        group: www-data
        mode: '0644'

    - name: Start and enable nginx
      service:
        name: nginx
        state: started
        enabled: yes
```

### Example 3: User Management

**users.yml**:
```yaml
---
- name: Manage user accounts
  hosts: all
  become: yes

  tasks:
    - name: Create developers group
      group:
        name: developers
        gid: 1100
        state: present

    - name: Create user accounts
      user:
        name: "{{ item }}"
        groups: developers
        shell: /bin/bash
        create_home: yes
        state: present
      loop:
        - alice
        - bob
        - charlie

    - name: Set up SSH directory for users
      file:
        path: "/home/{{ item }}/.ssh"
        state: directory
        owner: "{{ item }}"
        group: "{{ item }}"
        mode: '0700'
      loop:
        - alice
        - bob
        - charlie
```

## 🏃 Running Playbooks

### Basic Execution

```bash
# Run a playbook
ansible-playbook playbook.yml

# Run with specific inventory
ansible-playbook -i inventory playbook.yml

# Limit to specific hosts
ansible-playbook playbook.yml --limit webservers

# Run with extra variables
ansible-playbook playbook.yml -e "env=production"
```

### Dry Run (Check Mode)

```bash
# Check what would change without making changes
ansible-playbook playbook.yml --check

# Check mode with diff (show differences)
ansible-playbook playbook.yml --check --diff
```

### Step-by-Step Execution

```bash
# Prompt before each task
ansible-playbook playbook.yml --step

# Start at specific task
ansible-playbook playbook.yml --start-at-task="Install nginx"
```

### Verbose Output

```bash
# Verbose output
ansible-playbook playbook.yml -v

# More verbose (shows task results)
ansible-playbook playbook.yml -vv

# Very verbose (connection debugging)
ansible-playbook playbook.yml -vvv

# Maximum verbosity
ansible-playbook playbook.yml -vvvv
```

## 🔄 Understanding Idempotency

**Idempotency** means running the same playbook multiple times produces the same result. The second run won't make unnecessary changes.

### Idempotent Task Example

```yaml
- name: Ensure nginx is installed
  package:
    name: nginx
    state: present
```

**First run**: Installs nginx (state=changed)
**Second run**: Does nothing, nginx already installed (state=ok)

### Non-Idempotent Task Example (Avoid!)

```yaml
# ❌ BAD - runs every time
- name: Add line to file
  shell: echo "some line" >> /etc/config.conf
```

**Better (Idempotent) Alternative**:
```yaml
# ✅ GOOD - idempotent
- name: Ensure line exists in file
  lineinfile:
    path: /etc/config.conf
    line: "some line"
    state: present
```

## 📊 Task Results

Each task can result in:

- **ok**: Task ran successfully, no changes made
- **changed**: Task ran successfully, made changes
- **failed**: Task failed
- **skipped**: Task was skipped (conditional)
- **unreachable**: Host couldn't be reached

### PLAY RECAP

At the end of each playbook run:

```text
PLAY RECAP ******************************************
web1    : ok=10 changed=3  unreachable=0  failed=0
web2    : ok=10 changed=3  unreachable=0  failed=0
db1     : ok=8  changed=1  unreachable=0  failed=0
```

## 🛠️ Exercises

### Exercise 4.1: Create Your First Playbook

**Task**: Create a playbook that performs basic system information gathering.

**Requirements**:
- Name it `system_info.yml`
- Target localhost
- Include at least 3 tasks
- Use the debug module to display information

**Solution**:

```yaml
---
- name: Gather system information
  hosts: localhost
  connection: local

  tasks:
    - name: Display hostname
      debug:
        msg: "Hostname: {{ ansible_hostname }}"

    - name: Display OS information
      debug:
        msg: "OS: {{ ansible_distribution }} {{ ansible_distribution_version }}"

    - name: Display memory information
      debug:
        msg: "Total Memory: {{ ansible_memtotal_mb }} MB"

    - name: Display CPU information
      debug:
        msg: "CPU Cores: {{ ansible_processor_vcpus }}"
```

**Run it**:
```bash
ansible-playbook system_info.yml
```

---

### Exercise 4.2: File and Directory Management

**Task**: Create a playbook that sets up a project directory structure.

**Requirements**:
- Create directory: `/tmp/myproject`
- Create subdirectories: `logs`, `data`, `config`
- Create an empty file: `config/app.conf`
- Create a file with content: `README.txt`

**Solution**:

```yaml
---
- name: Setup project directory structure
  hosts: localhost
  connection: local

  tasks:
    - name: Create main project directory
      file:
        path: /tmp/myproject
        state: directory
        mode: '0755'

    - name: Create subdirectories
      file:
        path: "/tmp/myproject/{{ item }}"
        state: directory
        mode: '0755'
      loop:
        - logs
        - data
        - config

    - name: Create empty config file
      file:
        path: /tmp/myproject/config/app.conf
        state: touch
        mode: '0644'

    - name: Create README file
      copy:
        content: |
          # My Project

          This project was created by Ansible.

          ## Directory Structure
          - logs/   - Application logs
          - data/   - Application data
          - config/ - Configuration files
        dest: /tmp/myproject/README.txt
        mode: '0644'

    - name: Verify structure was created
      command: tree /tmp/myproject
      register: result
      ignore_errors: yes

    - name: Display directory structure
      debug:
        var: result.stdout_lines
      when: result is succeeded
```

**Run it**:
```bash
ansible-playbook directory_setup.yml
```

---

### Exercise 4.3: Package Installation

**Task**: Create a playbook to install and configure a package.

**Requirements**:
- Install `tree` package
- Install `htop` package
- Verify installations by checking versions

**Solution**:

```yaml
---
- name: Install system utilities
  hosts: localhost
  connection: local
  become: yes

  tasks:
    - name: Install tree package
      package:
        name: tree
        state: present

    - name: Install htop package
      package:
        name: htop
        state: present

    - name: Check tree version
      command: tree --version
      register: tree_version
      changed_when: false

    - name: Display tree version
      debug:
        msg: "{{ tree_version.stdout }}"

    - name: Check htop version
      command: htop --version
      register: htop_version
      changed_when: false

    - name: Display htop version
      debug:
        msg: "{{ htop_version.stdout_lines[0] }}"
```

**Run it**:
```bash
ansible-playbook install_utils.yml
```

---

### Exercise 4.4: Multi-Play Playbook

**Task**: Create a playbook with multiple plays for different host groups.

**Inventory** (`inventory`):
```ini
[webservers]
web1 ansible_connection=local

[databases]
db1 ansible_connection=local

[monitoring]
mon1 ansible_connection=local
```

**Playbook** (`multi_play.yml`):

```yaml
---
- name: Configure web servers
  hosts: webservers
  connection: local

  tasks:
    - name: Web server message
      debug:
        msg: "Configuring web server: {{ inventory_hostname }}"

    - name: Create web directory
      file:
        path: /tmp/webserver
        state: directory

- name: Configure database servers
  hosts: databases
  connection: local

  tasks:
    - name: Database server message
      debug:
        msg: "Configuring database server: {{ inventory_hostname }}"

    - name: Create database directory
      file:
        path: /tmp/database
        state: directory

- name: Configure monitoring servers
  hosts: monitoring
  connection: local

  tasks:
    - name: Monitoring server message
      debug:
        msg: "Configuring monitoring server: {{ inventory_hostname }}"

    - name: Create monitoring directory
      file:
        path: /tmp/monitoring
        state: directory
```

**Run it**:
```bash
ansible-playbook -i inventory multi_play.yml
```

---

### Exercise 4.5: Check Mode and Diff

**Task**: Practice using check mode to preview changes.

**Create this playbook** (`webserver_config.yml`):

```yaml
---
- name: Configure web server
  hosts: localhost
  connection: local
  become: yes

  tasks:
    - name: Install nginx
      package:
        name: nginx
        state: present

    - name: Create custom nginx config
      copy:
        content: |
          server {
              listen 8080;
              server_name localhost;

              location / {
                  root /var/www/html;
                  index index.html;
              }
          }
        dest: /etc/nginx/sites-available/custom
        mode: '0644'

    - name: Enable custom site
      file:
        src: /etc/nginx/sites-available/custom
        dest: /etc/nginx/sites-enabled/custom
        state: link
```

**Practice commands**:

```bash
# Check what would change
ansible-playbook webserver_config.yml --check

# Check with diff output
ansible-playbook webserver_config.yml --check --diff

# Actually apply changes
ansible-playbook webserver_config.yml

# Run again to see idempotency (should show no changes)
ansible-playbook webserver_config.yml
```

---

### Exercise 4.6: Error Recovery

**Task**: Create a playbook that handles failures gracefully.

```yaml
---
- name: Practice error handling
  hosts: localhost
  connection: local

  tasks:
    - name: Task that might fail
      command: /bin/false
      ignore_errors: yes
      register: result

    - name: Check if previous task failed
      debug:
        msg: "Previous task failed: {{ result.failed }}"

    - name: Continue with next task
      debug:
        msg: "This task runs even if previous failed"

    - name: Task that will fail and stop playbook
      command: /usr/bin/nonexistent_command
      # This will stop the playbook

    - name: This task won't run
      debug:
        msg: "You won't see this message"
```

**Run it and observe**:
```bash
ansible-playbook error_handling.yml
```

---

## 🔧 Troubleshooting

### Problem: Syntax Error

**Error**: "ERROR! Syntax Error while loading YAML"

**Solution**: Check YAML syntax:
```bash
# Validate YAML syntax
python3 -c 'import yaml; yaml.safe_load(open("playbook.yml"))'

# Or use yamllint
yamllint playbook.yml
```

Common issues:
- Missing colons
- Wrong indentation (tabs vs spaces)
- Unmatched quotes

### Problem: Task Fails

**Error**: Task shows "failed: [host]"

**Solution**: Run with verbose output:
```bash
ansible-playbook playbook.yml -vvv
```

Check:
- Module parameters are correct
- File paths exist
- Permissions are sufficient (use `become: yes`)

### Problem: Variables Not Resolving

**Error**: Variables show as `{{ variable_name }}` instead of values

**Solution**:
- Ensure variable is defined
- Check variable scope
- Quote strings containing variables:
  ```yaml
  # ❌ WRONG
  path: /home/{{ username }}/file

  # ✅ CORRECT
  path: "/home/{{ username }}/file"
  ```

### Problem: Playbook Hangs

**Cause**: Task is waiting for input or running indefinitely

**Solution**:
- Add timeout to long-running tasks
- Use async tasks for long operations
- Check if task needs `become: yes`

## 📖 Key Takeaways

✅ Playbooks are YAML files defining automation tasks
✅ Each playbook contains one or more plays
✅ Each play maps hosts to tasks
✅ Tasks use modules to perform actions
✅ Use `--check` for dry-run before applying changes
✅ Idempotency means playbooks are safe to run multiple times
✅ Name your tasks for better readability and debugging
✅ Use proper YAML indentation (spaces, not tabs)

## 🎓 What's Next?

Now that you understand playbook basics, you're ready to make them dynamic with variables and facts.

**Next Chapter**: [Chapter 5: Variables and Facts](05-variables-facts.md)

In the next chapter, you'll learn:
- Defining and using variables
- Variable precedence
- Ansible facts
- Registering variables from task output
- Variable scope and special variables

---

**Keep Practicing!** Try modifying the example playbooks and creating your own automation tasks.
