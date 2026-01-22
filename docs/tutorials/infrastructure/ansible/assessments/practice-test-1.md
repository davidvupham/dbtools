# Practice Test 1: Beginner/Intermediate

This practice test covers fundamental Ansible concepts and basic automation tasks. Complete all tasks without referring to documentation to simulate exam conditions.

**Time Limit**: 90 minutes
**Passing Score**: 70%
**Environment**: 1 control node + 2 managed nodes

---

## Environment Setup

For this practice test, set up the following:

```text
Control Node: control.lab.local
Managed Nodes:
  - node1.lab.local (192.168.56.11) - Group: webservers
  - node2.lab.local (192.168.56.12) - Group: databases
```

You can use Docker, Vagrant, or VMs. Ensure SSH access is configured.

---

## Tasks

### Task 1: Ansible Installation and Configuration (10 points)

**Objective**: Configure the Ansible control node.

**Requirements**:

1. Create a working directory at `/home/ansible/practice1/`
2. Create `ansible.cfg` with the following settings:
   - Inventory file: `./inventory`
   - Remote user: `ansible`
   - Host key checking: disabled
   - Forks: 5
   - Roles path: `./roles`
3. The user `ansible` should use passwordless SSH to managed nodes
4. The user `ansible` should have passwordless sudo on managed nodes

<details>
<summary>Solution</summary>

```bash
# Create directory
mkdir -p /home/ansible/practice1
cd /home/ansible/practice1

# Create ansible.cfg
cat > ansible.cfg << 'EOF'
[defaults]
inventory = ./inventory
remote_user = ansible
host_key_checking = False
forks = 5
roles_path = ./roles

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False
EOF
```

On managed nodes (run as root):
```bash
useradd ansible
echo "ansible ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/ansible
```

On control node:
```bash
ssh-keygen -t rsa -N ""
ssh-copy-id ansible@node1.lab.local
ssh-copy-id ansible@node2.lab.local
```
</details>

---

### Task 2: Inventory Management (10 points)

**Objective**: Create a structured inventory file.

**Requirements**:

1. Create an inventory file with the following structure:
   - Group `webservers` containing `node1`
   - Group `databases` containing `node2`
   - Group `production` containing both groups as children
2. Define the following group variables for `webservers`:
   - `http_port: 80`
   - `doc_root: /var/www/html`
3. Define the following group variables for `databases`:
   - `db_port: 3306`
   - `db_root_password: secure123`

<details>
<summary>Solution</summary>

```ini
# inventory
[webservers]
node1 ansible_host=192.168.56.11

[databases]
node2 ansible_host=192.168.56.12

[production:children]
webservers
databases

[webservers:vars]
http_port=80
doc_root=/var/www/html

[databases:vars]
db_port=3306
db_root_password=secure123
```

Or using YAML:
```yaml
# inventory.yml
all:
  children:
    production:
      children:
        webservers:
          hosts:
            node1:
              ansible_host: 192.168.56.11
          vars:
            http_port: 80
            doc_root: /var/www/html
        databases:
          hosts:
            node2:
              ansible_host: 192.168.56.12
          vars:
            db_port: 3306
            db_root_password: secure123
```
</details>

---

### Task 3: Ad-Hoc Commands Script (10 points)

**Objective**: Create a script using ad-hoc commands.

**Requirements**:

Create a script `/home/ansible/practice1/adhoc.sh` that:

1. Ensures the `automation` group exists on all managed nodes
2. Creates user `automation` on all managed nodes with:
   - Primary group: `automation`
   - Shell: `/bin/bash`
   - Home directory created
3. Copies the control node's `/etc/hosts` to all managed nodes

<details>
<summary>Solution</summary>

```bash
#!/bin/bash
# /home/ansible/practice1/adhoc.sh

# Create automation group
ansible all -m group -a "name=automation state=present" -b

# Create automation user
ansible all -m user -a "name=automation group=automation shell=/bin/bash create_home=yes" -b

# Copy hosts file
ansible all -m copy -a "src=/etc/hosts dest=/etc/hosts owner=root group=root mode=0644" -b
```

Make it executable:
```bash
chmod +x /home/ansible/practice1/adhoc.sh
```
</details>

---

### Task 4: Basic Playbook - System Configuration (15 points)

**Objective**: Write a playbook for basic system configuration.

**Requirements**:

Create `/home/ansible/practice1/system_setup.yml` that:

1. Updates the `/etc/motd` file on all hosts with:
   - For webservers: "Welcome to Web Server"
   - For databases: "Welcome to Database Server"
2. Ensures the `chrony` package is installed on all hosts
3. Ensures the `chronyd` service is running and enabled

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/practice1/system_setup.yml
- name: Configure MOTD on webservers
  hosts: webservers
  become: yes
  tasks:
    - name: Set MOTD for webservers
      copy:
        content: "Welcome to Web Server\n"
        dest: /etc/motd
        owner: root
        group: root
        mode: '0644'

- name: Configure MOTD on databases
  hosts: databases
  become: yes
  tasks:
    - name: Set MOTD for databases
      copy:
        content: "Welcome to Database Server\n"
        dest: /etc/motd
        owner: root
        group: root
        mode: '0644'

- name: Configure time synchronization
  hosts: all
  become: yes
  tasks:
    - name: Install chrony
      package:
        name: chrony
        state: present

    - name: Ensure chronyd is running and enabled
      service:
        name: chronyd
        state: started
        enabled: yes
```
</details>

---

### Task 5: Variables and Facts Playbook (15 points)

**Objective**: Create a playbook using variables and facts.

**Requirements**:

Create `/home/ansible/practice1/system_info.yml` that:

1. Gathers system information from all hosts
2. Creates a file `/tmp/system_info.txt` on each host containing:
   - Hostname
   - IP Address
   - Total Memory (MB)
   - Operating System
   - Number of CPUs
3. Uses proper Jinja2 templating for the content

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/practice1/system_info.yml
- name: Gather and record system information
  hosts: all
  become: yes

  tasks:
    - name: Create system info file
      copy:
        content: |
          System Information Report
          ========================
          Hostname: {{ ansible_hostname }}
          IP Address: {{ ansible_default_ipv4.address }}
          Total Memory: {{ ansible_memtotal_mb }} MB
          Operating System: {{ ansible_distribution }} {{ ansible_distribution_version }}
          Number of CPUs: {{ ansible_processor_vcpus }}

          Generated: {{ ansible_date_time.iso8601 }}
        dest: /tmp/system_info.txt
        owner: root
        group: root
        mode: '0644'

    - name: Display system info
      debug:
        msg: "{{ ansible_hostname }} has {{ ansible_memtotal_mb }}MB RAM and {{ ansible_processor_vcpus }} CPUs"
```
</details>

---

### Task 6: Package and Service Management (15 points)

**Objective**: Manage packages and services with conditional logic.

**Requirements**:

Create `/home/ansible/practice1/packages.yml` that:

1. On webservers:
   - Installs `httpd` and `mod_ssl`
   - Starts and enables `httpd`
   - Opens firewall port 80 and 443
2. On databases:
   - Installs `mariadb-server`
   - Starts and enables `mariadb`
   - Opens firewall port 3306

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/practice1/packages.yml
- name: Configure web servers
  hosts: webservers
  become: yes

  tasks:
    - name: Install web server packages
      package:
        name:
          - httpd
          - mod_ssl
        state: present

    - name: Start and enable httpd
      service:
        name: httpd
        state: started
        enabled: yes

    - name: Open HTTP port
      firewalld:
        port: 80/tcp
        permanent: yes
        state: enabled
        immediate: yes

    - name: Open HTTPS port
      firewalld:
        port: 443/tcp
        permanent: yes
        state: enabled
        immediate: yes

- name: Configure database servers
  hosts: databases
  become: yes

  tasks:
    - name: Install MariaDB
      package:
        name: mariadb-server
        state: present

    - name: Start and enable MariaDB
      service:
        name: mariadb
        state: started
        enabled: yes

    - name: Open MySQL port
      firewalld:
        port: 3306/tcp
        permanent: yes
        state: enabled
        immediate: yes
```
</details>

---

### Task 7: User Management Playbook (15 points)

**Objective**: Manage users with loops and variables.

**Requirements**:

Create `/home/ansible/practice1/users.yml` that:

1. Creates the following users on all hosts:
   - `devuser1` with UID 2001
   - `devuser2` with UID 2002
   - `devuser3` with UID 2003
2. All users should:
   - Be members of the `developers` group
   - Have their home directories created
   - Have bash as their shell
3. Uses a loop (not separate tasks for each user)

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/practice1/users.yml
- name: Manage developer users
  hosts: all
  become: yes

  vars:
    dev_users:
      - name: devuser1
        uid: 2001
      - name: devuser2
        uid: 2002
      - name: devuser3
        uid: 2003

  tasks:
    - name: Ensure developers group exists
      group:
        name: developers
        state: present

    - name: Create developer users
      user:
        name: "{{ item.name }}"
        uid: "{{ item.uid }}"
        groups: developers
        shell: /bin/bash
        create_home: yes
        state: present
      loop: "{{ dev_users }}"

    - name: Verify users were created
      command: "id {{ item.name }}"
      loop: "{{ dev_users }}"
      changed_when: false
      register: user_check

    - name: Display user info
      debug:
        msg: "{{ item.stdout }}"
      loop: "{{ user_check.results }}"
```
</details>

---

### Task 8: File Operations Playbook (10 points)

**Objective**: Perform various file operations.

**Requirements**:

Create `/home/ansible/practice1/files.yml` that:

1. Creates directory `/opt/backup` with mode 0755
2. Creates an empty file `/opt/backup/README` with owner `root`
3. Creates a symbolic link `/tmp/backup` pointing to `/opt/backup`
4. Archives `/etc/hosts` and `/etc/resolv.conf` to `/opt/backup/config_backup.tar.gz`

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/practice1/files.yml
- name: File operations
  hosts: all
  become: yes

  tasks:
    - name: Create backup directory
      file:
        path: /opt/backup
        state: directory
        mode: '0755'
        owner: root
        group: root

    - name: Create README file
      file:
        path: /opt/backup/README
        state: touch
        owner: root
        group: root
        mode: '0644'

    - name: Create symbolic link
      file:
        src: /opt/backup
        dest: /tmp/backup
        state: link

    - name: Archive configuration files
      archive:
        path:
          - /etc/hosts
          - /etc/resolv.conf
        dest: /opt/backup/config_backup.tar.gz
        format: gz

    - name: Verify archive was created
      stat:
        path: /opt/backup/config_backup.tar.gz
      register: archive_stat

    - name: Display archive info
      debug:
        msg: "Archive size: {{ archive_stat.stat.size }} bytes"
```
</details>

---

## Scoring Guide

| Task | Points | Criteria |
|------|--------|----------|
| Task 1 | 10 | ansible.cfg correct (5), SSH/sudo configured (5) |
| Task 2 | 10 | Inventory structure (5), variables correct (5) |
| Task 3 | 10 | Script works (5), all operations correct (5) |
| Task 4 | 15 | MOTD correct (5), chrony installed (5), service running (5) |
| Task 5 | 15 | Fact gathering (5), file created (5), template correct (5) |
| Task 6 | 15 | Packages installed (5), services running (5), firewall (5) |
| Task 7 | 15 | Users created (5), loop used (5), groups correct (5) |
| Task 8 | 10 | Directory/files created (5), archive correct (5) |
| **Total** | **100** | |

---

## Verification Commands

Run these to verify your work:

```bash
# Task 1: Verify configuration
ansible --version
ansible-config dump --only-changed

# Task 2: Verify inventory
ansible-inventory --list

# Task 3: Run ad-hoc script and verify
./adhoc.sh
ansible all -m shell -a "id automation"

# Task 4: Run playbook and verify
ansible-playbook system_setup.yml
ansible all -m shell -a "cat /etc/motd"
ansible all -m shell -a "systemctl status chronyd"

# Task 5: Run playbook and verify
ansible-playbook system_info.yml
ansible all -m shell -a "cat /tmp/system_info.txt"

# Task 6: Run playbook and verify
ansible-playbook packages.yml
ansible webservers -m shell -a "systemctl status httpd"
ansible databases -m shell -a "systemctl status mariadb"

# Task 7: Run playbook and verify
ansible-playbook users.yml
ansible all -m shell -a "getent passwd devuser1 devuser2 devuser3"

# Task 8: Run playbook and verify
ansible-playbook files.yml
ansible all -m shell -a "ls -la /opt/backup/"
```

---

## After the Test

1. Review tasks you couldn't complete
2. Study the solutions and understand why they work
3. Practice the weak areas before taking Practice Test 2
4. Target 80% or higher before attempting the Mock Exam
