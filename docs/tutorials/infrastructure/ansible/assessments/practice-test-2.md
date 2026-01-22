# Practice Test 2: Advanced/Exam-Like

This practice test covers advanced Ansible topics and closely simulates the EX294 exam format. Complete without documentation.

**Time Limit**: 3 hours
**Passing Score**: 70%
**Environment**: 1 control node + 4 managed nodes

---

## Environment Setup

```text
Control Node: control.lab.local

Managed Nodes:
  - node1.lab.local (192.168.56.11) - Group: webservers
  - node2.lab.local (192.168.56.12) - Group: webservers
  - node3.lab.local (192.168.56.13) - Group: databases
  - node4.lab.local (192.168.56.14) - Group: proxy

All nodes: RHEL 8/9 or CentOS Stream
User: ansible with sudo privileges
```

---

## Tasks

### Task 1: Control Node Configuration (5 points)

**Objective**: Set up the Ansible control node environment.

Create directory `/home/ansible/exam/` with:

1. `ansible.cfg` with:
   - Inventory: `./inventory`
   - Roles path: `./roles`
   - Remote user: `ansible`
   - Forks: 10
   - Host key checking: disabled
   - Gathering: smart

2. Create the inventory with groups: webservers, databases, proxy, and production (children of all)

<details>
<summary>Solution</summary>

```bash
mkdir -p /home/ansible/exam
cd /home/ansible/exam
```

```ini
# ansible.cfg
[defaults]
inventory = ./inventory
roles_path = ./roles
remote_user = ansible
forks = 10
host_key_checking = False
gathering = smart

[privilege_escalation]
become = True
become_method = sudo
become_ask_pass = False
```

```ini
# inventory
[webservers]
node1 ansible_host=192.168.56.11
node2 ansible_host=192.168.56.12

[databases]
node3 ansible_host=192.168.56.13

[proxy]
node4 ansible_host=192.168.56.14

[production:children]
webservers
databases
proxy
```
</details>

---

### Task 2: Ansible Vault (10 points)

**Objective**: Secure sensitive data with Ansible Vault.

**Requirements**:

1. Create a vault password file at `/home/ansible/exam/vault_pass.txt` containing: `redhat`
2. Create encrypted file `/home/ansible/exam/vars/vault.yml` containing:
   ```yaml
   vault_db_password: SecureP@ss123
   vault_api_key: abcd-1234-efgh-5678
   ```
3. Configure `ansible.cfg` to use the vault password file automatically

<details>
<summary>Solution</summary>

```bash
# Create vault password file
echo "redhat" > /home/ansible/exam/vault_pass.txt
chmod 600 /home/ansible/exam/vault_pass.txt

# Create vars directory
mkdir -p /home/ansible/exam/vars

# Create encrypted vault file
ansible-vault create /home/ansible/exam/vars/vault.yml --vault-password-file=/home/ansible/exam/vault_pass.txt
```

Content of vault.yml (before encryption):
```yaml
vault_db_password: SecureP@ss123
vault_api_key: abcd-1234-efgh-5678
```

Update ansible.cfg:
```ini
[defaults]
# ... existing settings ...
vault_password_file = ./vault_pass.txt
```
</details>

---

### Task 3: Create a Custom Role (15 points)

**Objective**: Build a reusable Apache role.

**Requirements**:

Create role `apache` at `/home/ansible/exam/roles/apache/` that:

1. Installs `httpd` and `mod_ssl` packages
2. Deploys a template `index.html.j2` to `/var/www/html/index.html` containing:
   - Server hostname
   - Server IP address
   - Current date/time
3. Creates configuration file from template with customizable port (default: 80)
4. Starts and enables httpd service
5. Opens firewall port for HTTP
6. Includes a handler to restart httpd when config changes

<details>
<summary>Solution</summary>

```bash
cd /home/ansible/exam
mkdir -p roles/apache/{tasks,handlers,templates,defaults}
```

`roles/apache/defaults/main.yml`:
```yaml
---
apache_port: 80
apache_doc_root: /var/www/html
```

`roles/apache/tasks/main.yml`:
```yaml
---
- name: Install Apache packages
  package:
    name:
      - httpd
      - mod_ssl
    state: present

- name: Deploy index.html
  template:
    src: index.html.j2
    dest: "{{ apache_doc_root }}/index.html"
    owner: apache
    group: apache
    mode: '0644'

- name: Configure Apache port
  template:
    src: httpd.conf.j2
    dest: /etc/httpd/conf.d/custom.conf
    owner: root
    group: root
    mode: '0644'
  notify: Restart httpd

- name: Ensure httpd is running
  service:
    name: httpd
    state: started
    enabled: yes

- name: Open firewall port
  firewalld:
    port: "{{ apache_port }}/tcp"
    permanent: yes
    state: enabled
    immediate: yes
```

`roles/apache/handlers/main.yml`:
```yaml
---
- name: Restart httpd
  service:
    name: httpd
    state: restarted
```

`roles/apache/templates/index.html.j2`:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Welcome to {{ ansible_hostname }}</title>
</head>
<body>
    <h1>Server Information</h1>
    <ul>
        <li>Hostname: {{ ansible_hostname }}</li>
        <li>IP Address: {{ ansible_default_ipv4.address }}</li>
        <li>Generated: {{ ansible_date_time.iso8601 }}</li>
    </ul>
</body>
</html>
```

`roles/apache/templates/httpd.conf.j2`:
```apache
Listen {{ apache_port }}

<VirtualHost *:{{ apache_port }}>
    DocumentRoot {{ apache_doc_root }}
    ServerName {{ ansible_hostname }}
</VirtualHost>
```
</details>

---

### Task 4: Use Galaxy Role for HAProxy (10 points)

**Objective**: Install and use a community role.

**Requirements**:

1. Create `requirements.yml` to install `geerlingguy.haproxy` role
2. Install the role using ansible-galaxy
3. Create playbook `loadbalancer.yml` that:
   - Uses the haproxy role on the proxy group
   - Configures backend servers as the webservers group
   - Uses round-robin load balancing

<details>
<summary>Solution</summary>

`requirements.yml`:
```yaml
---
roles:
  - name: geerlingguy.haproxy
    version: "1.12.0"
```

Install:
```bash
ansible-galaxy install -r requirements.yml -p ./roles/
```

`loadbalancer.yml`:
```yaml
---
- name: Configure HAProxy load balancer
  hosts: proxy
  become: yes

  vars:
    haproxy_frontend_name: 'hafrontend'
    haproxy_frontend_bind_address: '*'
    haproxy_frontend_port: 80
    haproxy_frontend_mode: 'http'
    haproxy_backend_name: 'habackend'
    haproxy_backend_mode: 'http'
    haproxy_backend_balance_method: 'roundrobin'
    haproxy_backend_servers:
      - name: node1
        address: 192.168.56.11:80
      - name: node2
        address: 192.168.56.12:80

  roles:
    - geerlingguy.haproxy
```
</details>

---

### Task 5: Conditional Tasks and Loops (10 points)

**Objective**: Use conditionals based on system facts.

**Requirements**:

Create `/home/ansible/exam/sysctl.yml` that:

1. Sets `vm.swappiness = 10` if system has < 2GB RAM
2. Sets `vm.swappiness = 5` if system has >= 2GB RAM
3. The setting must persist across reboots
4. Uses a single task with conditional logic (not multiple tasks)

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/exam/sysctl.yml
- name: Configure system swappiness
  hosts: all
  become: yes

  tasks:
    - name: Set vm.swappiness based on memory
      sysctl:
        name: vm.swappiness
        value: "{{ '10' if ansible_memtotal_mb < 2048 else '5' }}"
        sysctl_file: /etc/sysctl.d/99-swappiness.conf
        state: present
        reload: yes

    - name: Display current swappiness setting
      command: cat /proc/sys/vm/swappiness
      register: swappiness_result
      changed_when: false

    - name: Show swappiness value
      debug:
        msg: "{{ inventory_hostname }} ({{ ansible_memtotal_mb }}MB RAM): swappiness = {{ swappiness_result.stdout }}"
```
</details>

---

### Task 6: Error Handling with Blocks (10 points)

**Objective**: Implement error handling.

**Requirements**:

Create `/home/ansible/exam/error_handling.yml` that:

1. Attempts to install a non-existent package `fake-package`
2. If installation fails, logs the error to `/var/log/ansible_errors.log`
3. Always records the completion time to `/var/log/ansible_completion.log`
4. Playbook should complete successfully even if the package installation fails

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/exam/error_handling.yml
- name: Demonstrate error handling
  hosts: all
  become: yes

  tasks:
    - name: Package installation with error handling
      block:
        - name: Attempt to install non-existent package
          package:
            name: fake-package
            state: present

      rescue:
        - name: Log error message
          lineinfile:
            path: /var/log/ansible_errors.log
            line: "{{ ansible_date_time.iso8601 }} - Failed to install fake-package on {{ inventory_hostname }}"
            create: yes
            mode: '0644'

        - name: Display error message
          debug:
            msg: "Package installation failed, error logged"

      always:
        - name: Record completion time
          lineinfile:
            path: /var/log/ansible_completion.log
            line: "{{ ansible_date_time.iso8601 }} - Playbook completed on {{ inventory_hostname }}"
            create: yes
            mode: '0644'
```
</details>

---

### Task 7: Jinja2 Templates (10 points)

**Objective**: Create dynamic configuration files.

**Requirements**:

Create `/home/ansible/exam/hosts_file.yml` that:

1. Generates `/etc/hosts.ansible` on all hosts
2. The file should contain entries for ALL inventory hosts
3. Use a Jinja2 template with a loop
4. Format: `IP_ADDRESS    HOSTNAME    FQDN`

<details>
<summary>Solution</summary>

Create template `templates/hosts.j2`:
```jinja2
# Managed by Ansible - Do not edit manually
# Generated: {{ ansible_date_time.iso8601 }}

127.0.0.1   localhost localhost.localdomain

# Inventory hosts
{% for host in groups['all'] %}
{{ hostvars[host]['ansible_host'] | default(hostvars[host]['ansible_default_ipv4']['address']) }}    {{ host }}    {{ host }}.lab.local
{% endfor %}
```

Playbook `hosts_file.yml`:
```yaml
---
# /home/ansible/exam/hosts_file.yml
- name: Generate hosts file from inventory
  hosts: all
  become: yes

  tasks:
    - name: Deploy hosts file template
      template:
        src: templates/hosts.j2
        dest: /etc/hosts.ansible
        owner: root
        group: root
        mode: '0644'

    - name: Display generated hosts file
      command: cat /etc/hosts.ansible
      register: hosts_content
      changed_when: false

    - name: Show content
      debug:
        var: hosts_content.stdout_lines
```
</details>

---

### Task 8: Users with Vault-Encrypted Passwords (10 points)

**Objective**: Create users with secure passwords.

**Requirements**:

Create `/home/ansible/exam/secure_users.yml` that:

1. Uses the vault-encrypted password from Task 2
2. Creates user `dbadmin` on database servers only
3. User should have:
   - Password set from vault
   - Home directory
   - Bash shell
   - Member of `wheel` group
4. Task should use `no_log: true` to hide sensitive output

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/exam/secure_users.yml
- name: Create secure users
  hosts: databases
  become: yes
  vars_files:
    - vars/vault.yml

  tasks:
    - name: Ensure wheel group exists
      group:
        name: wheel
        state: present

    - name: Create dbadmin user
      user:
        name: dbadmin
        password: "{{ vault_db_password | password_hash('sha512') }}"
        groups: wheel
        shell: /bin/bash
        create_home: yes
        state: present
      no_log: true

    - name: Verify user was created
      command: id dbadmin
      register: user_info
      changed_when: false

    - name: Display user info
      debug:
        var: user_info.stdout
```
</details>

---

### Task 9: Scheduled Tasks (5 points)

**Objective**: Configure cron jobs.

**Requirements**:

Create `/home/ansible/exam/cron.yml` that:

1. Creates a cron job on all hosts
2. Job runs every 15 minutes
3. Executes: `date >> /var/log/date_log.txt`
4. Job name: `log_date`

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/exam/cron.yml
- name: Configure scheduled tasks
  hosts: all
  become: yes

  tasks:
    - name: Create date logging cron job
      cron:
        name: log_date
        minute: "*/15"
        job: "date >> /var/log/date_log.txt"
        state: present

    - name: Verify cron job exists
      command: crontab -l
      register: cron_list
      changed_when: false

    - name: Display cron jobs
      debug:
        var: cron_list.stdout_lines
```
</details>

---

### Task 10: Software Repositories (5 points)

**Objective**: Configure YUM repositories.

**Requirements**:

Create `/home/ansible/exam/repos.yml` that:

1. Configures an EPEL repository on all hosts
2. Repository settings:
   - Name: `epel`
   - Description: `Extra Packages for Enterprise Linux`
   - Base URL: `https://dl.fedoraproject.org/pub/epel/$releasever/Everything/$basearch/`
   - GPG check: enabled
   - GPG key: `https://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-$releasever`

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/exam/repos.yml
- name: Configure EPEL repository
  hosts: all
  become: yes

  tasks:
    - name: Add EPEL repository
      yum_repository:
        name: epel
        description: Extra Packages for Enterprise Linux
        baseurl: https://dl.fedoraproject.org/pub/epel/$releasever/Everything/$basearch/
        gpgcheck: yes
        gpgkey: https://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-$releasever
        enabled: yes
        state: present

    - name: Verify repository
      command: yum repolist epel
      register: repo_list
      changed_when: false

    - name: Display repository info
      debug:
        var: repo_list.stdout_lines
```
</details>

---

### Task 11: Custom Facts (5 points)

**Objective**: Deploy and use custom facts.

**Requirements**:

Create `/home/ansible/exam/custom_facts.yml` that:

1. Creates `/etc/ansible/facts.d/` directory on all hosts
2. Deploys a custom fact file `server_role.fact` containing:
   - For webservers: `[general]\nrole=webserver`
   - For databases: `[general]\nrole=database`
   - For proxy: `[general]\nrole=proxy`
3. Re-gathers facts and displays the custom fact

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/exam/custom_facts.yml
- name: Deploy and use custom facts
  hosts: all
  become: yes

  tasks:
    - name: Create facts directory
      file:
        path: /etc/ansible/facts.d
        state: directory
        mode: '0755'

    - name: Deploy custom fact for webservers
      copy:
        content: |
          [general]
          role=webserver
        dest: /etc/ansible/facts.d/server_role.fact
        mode: '0644'
      when: inventory_hostname in groups['webservers']

    - name: Deploy custom fact for databases
      copy:
        content: |
          [general]
          role=database
        dest: /etc/ansible/facts.d/server_role.fact
        mode: '0644'
      when: inventory_hostname in groups['databases']

    - name: Deploy custom fact for proxy
      copy:
        content: |
          [general]
          role=proxy
        dest: /etc/ansible/facts.d/server_role.fact
        mode: '0644'
      when: inventory_hostname in groups['proxy']

    - name: Re-gather facts
      setup:

    - name: Display custom fact
      debug:
        msg: "Server {{ inventory_hostname }} role: {{ ansible_local.server_role.general.role }}"
```
</details>

---

### Task 12: Site Playbook (5 points)

**Objective**: Create a master playbook.

**Requirements**:

Create `/home/ansible/exam/site.yml` that:

1. Imports all the playbooks created in previous tasks
2. Can be run with `ansible-playbook site.yml` to configure the entire infrastructure
3. Uses `import_playbook` for static inclusion

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/exam/site.yml
# Master playbook for complete infrastructure setup

- name: Configure system settings
  import_playbook: sysctl.yml

- name: Configure repositories
  import_playbook: repos.yml

- name: Deploy custom facts
  import_playbook: custom_facts.yml

- name: Configure cron jobs
  import_playbook: cron.yml

- name: Create secure users
  import_playbook: secure_users.yml

- name: Generate hosts file
  import_playbook: hosts_file.yml

- name: Configure web servers
  hosts: webservers
  become: yes
  roles:
    - apache

- name: Configure load balancer
  import_playbook: loadbalancer.yml
```
</details>

---

## Scoring Guide

| Task | Points | Key Criteria |
|------|--------|--------------|
| Task 1 | 5 | ansible.cfg, inventory correct |
| Task 2 | 10 | Vault encrypted, password file works |
| Task 3 | 15 | Role complete, templates work, handler fires |
| Task 4 | 10 | Galaxy role installed and configured |
| Task 5 | 10 | Conditional logic works, sysctl persists |
| Task 6 | 10 | block/rescue/always correct, logs created |
| Task 7 | 10 | Template loops through all hosts |
| Task 8 | 10 | Vault password used, no_log set |
| Task 9 | 5 | Cron job runs every 15 min |
| Task 10 | 5 | Repository configured correctly |
| Task 11 | 5 | Custom facts deploy and can be read |
| Task 12 | 5 | Site playbook runs all tasks |
| **Total** | **100** | |

---

## Verification

```bash
# Run site playbook
ansible-playbook site.yml

# Verify web servers
curl http://192.168.56.11
curl http://192.168.56.12

# Verify load balancer
curl http://192.168.56.14

# Verify custom facts
ansible all -m setup -a "filter=ansible_local"

# Verify cron
ansible all -m shell -a "crontab -l"

# Verify vault user
ansible databases -m shell -a "id dbadmin"
```

Target: **85%** or higher before attempting Mock Exam
