# Mock Certification Exam: EX294 RHCE Simulation

This mock exam simulates the Red Hat Certified Engineer (RHCE) EX294 exam environment and tasks.

**EXAM CONDITIONS**

- **Time Limit**: 4 hours (240 minutes)
- **Passing Score**: 70% (approximately 210/300 points)
- **Environment**: 1 control node + 4 managed nodes
- **No Internet Access**: Use only provided documentation
- **All changes must persist after reboot**

---

## Environment Specification

```text
CONTROL NODE
Hostname: control.example.com
IP: 172.25.250.254
OS: RHEL 9

MANAGED NODES
┌──────────────────┬────────────────┬─────────────┐
│ Hostname         │ IP             │ Group       │
├──────────────────┼────────────────┼─────────────┤
│ node1.example.com│ 172.25.250.11  │ dev         │
│ node2.example.com│ 172.25.250.12  │ test        │
│ node3.example.com│ 172.25.250.13  │ prod        │
│ node4.example.com│ 172.25.250.14  │ balancers   │
└──────────────────┴────────────────┴─────────────┘

ALL NODES
- User 'ansible' exists with sudo privileges
- SSH key authentication configured
- Root password: redhat
- ansible user password: redhat
```

---

## EXAM TASKS

### Task 1: Install and Configure Ansible (15 points)

On the control node, perform the following:

1. Install the `ansible-core` package
2. Create directory `/home/ansible/ansible-files/` for all exam work
3. Create `/home/ansible/ansible-files/ansible.cfg`:
   - Inventory: `/home/ansible/ansible-files/inventory`
   - Remote user: `ansible`
   - Ask for privilege escalation password: No
   - Default become method: `sudo`
   - Host key checking: disabled
   - Forks: 5
   - Roles path: `/home/ansible/ansible-files/roles`

4. Create `/home/ansible/ansible-files/inventory`:
   - Group `dev` with `node1`
   - Group `test` with `node2`
   - Group `prod` with `node3`
   - Group `balancers` with `node4`
   - Group `webservers` containing groups `dev`, `test`, `prod`

<details>
<summary>Solution</summary>

```bash
# Install ansible
sudo dnf install ansible-core -y

# Create directories
mkdir -p /home/ansible/ansible-files/roles
cd /home/ansible/ansible-files
```

`ansible.cfg`:
```ini
[defaults]
inventory = /home/ansible/ansible-files/inventory
remote_user = ansible
host_key_checking = False
forks = 5
roles_path = /home/ansible/ansible-files/roles

[privilege_escalation]
become = True
become_method = sudo
become_ask_pass = False
```

`inventory`:
```ini
[dev]
node1.example.com ansible_host=172.25.250.11

[test]
node2.example.com ansible_host=172.25.250.12

[prod]
node3.example.com ansible_host=172.25.250.13

[balancers]
node4.example.com ansible_host=172.25.250.14

[webservers:children]
dev
test
prod
```

Verify:
```bash
ansible all -m ping
```
</details>

---

### Task 2: Create Ad-Hoc Command Script (10 points)

Create a shell script `/home/ansible/ansible-files/adhoc.sh` that uses ad-hoc commands to:

1. Create group `sysadmins` on all managed nodes
2. Create user `automation` on all managed nodes:
   - Member of `sysadmins` group
   - Password: `devops` (use proper password hash)
3. Add `automation` user to sudoers with NOPASSWD on all managed nodes

Make the script executable.

<details>
<summary>Solution</summary>

```bash
#!/bin/bash
# /home/ansible/ansible-files/adhoc.sh

# Create sysadmins group
ansible all -m group -a "name=sysadmins state=present" -b

# Create automation user with password
ansible all -m user -a "name=automation groups=sysadmins password={{ 'devops' | password_hash('sha512') }}" -b

# Configure sudo access
ansible all -m copy -a "content='automation ALL=(ALL) NOPASSWD: ALL\n' dest=/etc/sudoers.d/automation mode=0440" -b
```

```bash
chmod +x /home/ansible/ansible-files/adhoc.sh
```
</details>

---

### Task 3: Create Ansible Vault Files (15 points)

1. Create a vault password file `/home/ansible/ansible-files/vault_pass` containing: `exam_password`

2. Create an encrypted file `/home/ansible/ansible-files/secret.yml` containing:
   ```yaml
   pw_developer: Imadev
   pw_manager: Imamgr
   ```

3. Configure `ansible.cfg` to automatically use the vault password file

<details>
<summary>Solution</summary>

```bash
# Create vault password file
echo "exam_password" > /home/ansible/ansible-files/vault_pass
chmod 600 /home/ansible/ansible-files/vault_pass

# Create encrypted vault file
cd /home/ansible/ansible-files
ansible-vault create secret.yml --vault-password-file=vault_pass
```

Content of secret.yml:
```yaml
pw_developer: Imadev
pw_manager: Imamgr
```

Update ansible.cfg:
```ini
[defaults]
# ... existing settings ...
vault_password_file = /home/ansible/ansible-files/vault_pass
```
</details>

---

### Task 4: Create Users with Vault Passwords (15 points)

Create playbook `/home/ansible/ansible-files/users.yml` that:

1. Uses the vault file from Task 3
2. On the `dev` and `test` groups:
   - Creates user `developer` with password from vault (`pw_developer`)
   - UID: 3001
3. On the `prod` group:
   - Creates user `manager` with password from vault (`pw_manager`)
   - UID: 3002
4. Both users should have `/bin/bash` as their shell

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/ansible-files/users.yml
- name: Create developer users
  hosts: dev,test
  become: yes
  vars_files:
    - secret.yml

  tasks:
    - name: Create developer user
      user:
        name: developer
        uid: 3001
        password: "{{ pw_developer | password_hash('sha512') }}"
        shell: /bin/bash
        state: present

- name: Create manager users
  hosts: prod
  become: yes
  vars_files:
    - secret.yml

  tasks:
    - name: Create manager user
      user:
        name: manager
        uid: 3002
        password: "{{ pw_manager | password_hash('sha512') }}"
        shell: /bin/bash
        state: present
```
</details>

---

### Task 5: Configure MOTD (10 points)

Create playbook `/home/ansible/ansible-files/motd.yml` that:

Replaces `/etc/motd` on managed nodes with content based on group:

- `dev`: "This is a Development Server\n"
- `test`: "This is a Test Server\n"
- `prod`: "This is a Production Server\n"
- `balancers`: "This is a Load Balancer\n"

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/ansible-files/motd.yml
- name: Configure MOTD on dev
  hosts: dev
  become: yes
  tasks:
    - name: Set MOTD
      copy:
        content: "This is a Development Server\n"
        dest: /etc/motd

- name: Configure MOTD on test
  hosts: test
  become: yes
  tasks:
    - name: Set MOTD
      copy:
        content: "This is a Test Server\n"
        dest: /etc/motd

- name: Configure MOTD on prod
  hosts: prod
  become: yes
  tasks:
    - name: Set MOTD
      copy:
        content: "This is a Production Server\n"
        dest: /etc/motd

- name: Configure MOTD on balancers
  hosts: balancers
  become: yes
  tasks:
    - name: Set MOTD
      copy:
        content: "This is a Load Balancer\n"
        dest: /etc/motd
```
</details>

---

### Task 6: Configure SSH (10 points)

Create playbook `/home/ansible/ansible-files/sshd.yml` that configures SSH on all managed nodes:

1. Banner: `/etc/motd`
2. X11Forwarding: `no`
3. MaxAuthTries: `3`

Service must be restarted if configuration changes.

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/ansible-files/sshd.yml
- name: Configure SSH
  hosts: all
  become: yes

  tasks:
    - name: Set SSH Banner
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^#?Banner'
        line: 'Banner /etc/motd'
      notify: Restart sshd

    - name: Disable X11 Forwarding
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^#?X11Forwarding'
        line: 'X11Forwarding no'
      notify: Restart sshd

    - name: Set MaxAuthTries
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^#?MaxAuthTries'
        line: 'MaxAuthTries 3'
      notify: Restart sshd

  handlers:
    - name: Restart sshd
      service:
        name: sshd
        state: restarted
```
</details>

---

### Task 7: Create Apache Role (20 points)

Create role `/home/ansible/ansible-files/roles/apache/` that:

1. Installs `httpd` and `firewalld` packages
2. Ensures firewalld is running
3. Opens HTTP service in firewall
4. Deploys template `/var/www/html/index.html` with content:
   ```
   Welcome to {{ ansible_fqdn }} on {{ ansible_default_ipv4.address }}
   ```
5. Starts and enables httpd service
6. Includes handler to restart httpd

Then create `/home/ansible/ansible-files/apache.yml` that applies the role to `webservers` group.

<details>
<summary>Solution</summary>

```bash
mkdir -p /home/ansible/ansible-files/roles/apache/{tasks,handlers,templates}
```

`roles/apache/tasks/main.yml`:
```yaml
---
- name: Install packages
  package:
    name:
      - httpd
      - firewalld
    state: present

- name: Ensure firewalld is running
  service:
    name: firewalld
    state: started
    enabled: yes

- name: Open HTTP in firewall
  firewalld:
    service: http
    permanent: yes
    state: enabled
    immediate: yes

- name: Deploy index.html
  template:
    src: index.html.j2
    dest: /var/www/html/index.html
  notify: Restart httpd

- name: Start httpd
  service:
    name: httpd
    state: started
    enabled: yes
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
```
Welcome to {{ ansible_fqdn }} on {{ ansible_default_ipv4.address }}
```

`apache.yml`:
```yaml
---
- name: Apply apache role
  hosts: webservers
  become: yes
  roles:
    - apache
```
</details>

---

### Task 8: Create PHP Info Page Role (15 points)

Create role `/home/ansible/ansible-files/roles/phpinfo/` that:

1. Depends on the `apache` role
2. Installs `php` package
3. Creates `/var/www/html/info.php` containing: `<?php phpinfo(); ?>`
4. Restarts httpd after PHP installation

Create `/home/ansible/ansible-files/phpinfo.yml` that applies the role to `dev` group only.

<details>
<summary>Solution</summary>

```bash
mkdir -p /home/ansible/ansible-files/roles/phpinfo/{tasks,meta,files}
```

`roles/phpinfo/meta/main.yml`:
```yaml
---
dependencies:
  - role: apache
```

`roles/phpinfo/tasks/main.yml`:
```yaml
---
- name: Install PHP
  package:
    name: php
    state: present
  notify: Restart httpd

- name: Create PHP info page
  copy:
    content: "<?php phpinfo(); ?>"
    dest: /var/www/html/info.php
    owner: apache
    group: apache
    mode: '0644'

  handlers:
    - name: Restart httpd
      service:
        name: httpd
        state: restarted
```

Or include handler from apache role:

`roles/phpinfo/tasks/main.yml`:
```yaml
---
- name: Install PHP
  package:
    name: php
    state: present

- name: Create PHP info page
  copy:
    content: "<?php phpinfo(); ?>"
    dest: /var/www/html/info.php
    owner: apache
    group: apache
    mode: '0644'

- name: Restart httpd for PHP
  service:
    name: httpd
    state: restarted
```

`phpinfo.yml`:
```yaml
---
- name: Deploy PHP info page
  hosts: dev
  become: yes
  roles:
    - phpinfo
```
</details>

---

### Task 9: Install Packages Conditionally (15 points)

Create playbook `/home/ansible/ansible-files/packages.yml` that:

1. On `dev` group: Install `Development Tools` group
2. On `prod` group: Install `php` and `mariadb-server`
3. Uses `package` module for OS independence

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/ansible-files/packages.yml
- name: Install development tools on dev
  hosts: dev
  become: yes
  tasks:
    - name: Install Development Tools group
      dnf:
        name: "@Development Tools"
        state: present

- name: Install production packages on prod
  hosts: prod
  become: yes
  tasks:
    - name: Install PHP and MariaDB
      package:
        name:
          - php
          - mariadb-server
        state: present
```
</details>

---

### Task 10: Configure Cron Jobs (10 points)

Create playbook `/home/ansible/ansible-files/cron.yml` that:

On all managed nodes:
1. Creates a cron job for user `ansible`
2. Name: `system_check`
3. Runs every hour at minute 0
4. Executes: `date >> /home/ansible/system_check.log`

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/ansible-files/cron.yml
- name: Configure cron jobs
  hosts: all
  become: yes

  tasks:
    - name: Create hourly system check cron job
      cron:
        name: system_check
        user: ansible
        minute: "0"
        hour: "*"
        job: "date >> /home/ansible/system_check.log"
        state: present
```
</details>

---

### Task 11: Configure Time Synchronization (10 points)

Create playbook `/home/ansible/ansible-files/timesync.yml` that:

1. Uses the RHEL system role `rhel-system-roles.timesync`
2. Configures NTP server: `time.google.com`
3. Apply to all managed nodes

First install system roles:
```bash
sudo dnf install rhel-system-roles -y
```

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/ansible-files/timesync.yml
- name: Configure time synchronization
  hosts: all
  become: yes

  vars:
    timesync_ntp_servers:
      - hostname: time.google.com
        iburst: yes

  roles:
    - rhel-system-roles.timesync
```

Update ansible.cfg to include system roles path:
```ini
roles_path = /home/ansible/ansible-files/roles:/usr/share/ansible/roles
```
</details>

---

### Task 12: Configure SELinux Boolean (10 points)

Create playbook `/home/ansible/ansible-files/selinux.yml` that:

1. Uses the RHEL system role for SELinux
2. Enables the `httpd_can_network_connect` boolean
3. The change must be persistent
4. Apply to `webservers` group

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/ansible-files/selinux.yml
- name: Configure SELinux boolean
  hosts: webservers
  become: yes

  vars:
    selinux_booleans:
      - name: httpd_can_network_connect
        state: on
        persistent: yes

  roles:
    - rhel-system-roles.selinux
```

Alternative using seboolean module:
```yaml
---
- name: Configure SELinux boolean
  hosts: webservers
  become: yes

  tasks:
    - name: Enable httpd_can_network_connect
      seboolean:
        name: httpd_can_network_connect
        state: yes
        persistent: yes
```
</details>

---

### Task 13: Create LVM Storage (20 points)

Create playbook `/home/ansible/ansible-files/storage.yml` that on all managed nodes:

1. Creates partition on `/dev/vdb` (if disk exists)
2. Creates volume group `vg_data`
3. Creates logical volume `lv_data` with 500MB
4. Creates XFS filesystem
5. Mounts at `/data` with persistence in fstab
6. Handles gracefully if `/dev/vdb` doesn't exist

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/ansible-files/storage.yml
- name: Configure LVM storage
  hosts: all
  become: yes

  tasks:
    - name: Check if /dev/vdb exists
      stat:
        path: /dev/vdb
      register: vdb_stat

    - name: Configure storage when disk exists
      when: vdb_stat.stat.exists
      block:
        - name: Create partition
          parted:
            device: /dev/vdb
            number: 1
            state: present
            part_type: primary
            fs_type: lvm

        - name: Create volume group
          lvg:
            vg: vg_data
            pvs: /dev/vdb1
            state: present

        - name: Create logical volume
          lvol:
            vg: vg_data
            lv: lv_data
            size: 500m
            state: present

        - name: Create XFS filesystem
          filesystem:
            fstype: xfs
            dev: /dev/vg_data/lv_data

        - name: Create mount point
          file:
            path: /data
            state: directory

        - name: Mount filesystem
          mount:
            path: /data
            src: /dev/vg_data/lv_data
            fstype: xfs
            state: mounted

    - name: Notify if disk doesn't exist
      debug:
        msg: "Disk /dev/vdb not found on {{ inventory_hostname }}"
      when: not vdb_stat.stat.exists
```
</details>

---

### Task 14: Generate Hardware Report (15 points)

Create playbook `/home/ansible/ansible-files/hwreport.yml` that:

1. Generates `/root/hwreport.txt` on each managed node
2. Contains:
   - HOST: hostname
   - MEMORY: total memory in MB
   - BIOS: BIOS version
   - CPU_VENDOR: processor vendor
   - CPU_CORES: total processor count
3. If any value cannot be determined, use "NONE"

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/ansible-files/hwreport.yml
- name: Generate hardware report
  hosts: all
  become: yes

  tasks:
    - name: Create hardware report
      copy:
        content: |
          HOST={{ ansible_hostname | default('NONE') }}
          MEMORY={{ ansible_memtotal_mb | default('NONE') }}
          BIOS={{ ansible_bios_version | default('NONE') }}
          CPU_VENDOR={{ ansible_processor[1] | default('NONE') }}
          CPU_CORES={{ ansible_processor_vcpus | default('NONE') }}
        dest: /root/hwreport.txt
        owner: root
        group: root
        mode: '0644'
```
</details>

---

### Task 15: Create Hosts Template (15 points)

Create playbook `/home/ansible/ansible-files/hostsfile.yml` that:

1. Uses a Jinja2 template to create `/etc/hosts.managed` on all nodes
2. Template contains all inventory hosts in format:
   ```
   IP_ADDRESS    SHORT_HOSTNAME    FQDN
   ```
3. File should be owned by root with mode 0644

<details>
<summary>Solution</summary>

Create `templates/hosts.j2`:
```jinja2
# Managed by Ansible - Do not edit
127.0.0.1   localhost localhost.localdomain

{% for host in groups['all'] %}
{{ hostvars[host]['ansible_host'] }}    {{ host.split('.')[0] }}    {{ host }}
{% endfor %}
```

`hostsfile.yml`:
```yaml
---
# /home/ansible/ansible-files/hostsfile.yml
- name: Generate managed hosts file
  hosts: all
  become: yes

  tasks:
    - name: Deploy hosts file template
      template:
        src: templates/hosts.j2
        dest: /etc/hosts.managed
        owner: root
        group: root
        mode: '0644'
```
</details>

---

### Task 16: Configure Password Quality (10 points)

Create playbook `/home/ansible/ansible-files/pwquality.yml` that on all managed nodes:

1. Sets minimum password length to 12
2. Requires at least 1 uppercase letter
3. Requires at least 1 digit
4. Configuration file: `/etc/security/pwquality.conf`

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/ansible-files/pwquality.yml
- name: Configure password quality
  hosts: all
  become: yes

  tasks:
    - name: Set minimum password length
      lineinfile:
        path: /etc/security/pwquality.conf
        regexp: '^#?\s*minlen'
        line: 'minlen = 12'

    - name: Require uppercase letters
      lineinfile:
        path: /etc/security/pwquality.conf
        regexp: '^#?\s*ucredit'
        line: 'ucredit = -1'

    - name: Require digits
      lineinfile:
        path: /etc/security/pwquality.conf
        regexp: '^#?\s*dcredit'
        line: 'dcredit = -1'
```
</details>

---

### Task 17: Create Archive Playbook (10 points)

Create playbook `/home/ansible/ansible-files/archive.yml` that on `prod` group:

1. Creates directory `/backup`
2. Archives `/etc` directory to `/backup/etc_backup.tar.gz`
3. Archive should be compressed with gzip

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/ansible-files/archive.yml
- name: Create backup archive
  hosts: prod
  become: yes

  tasks:
    - name: Create backup directory
      file:
        path: /backup
        state: directory
        mode: '0755'

    - name: Archive /etc directory
      archive:
        path: /etc
        dest: /backup/etc_backup.tar.gz
        format: gz
        mode: '0644'
```
</details>

---

### Task 18: Create Site Playbook (15 points)

Create `/home/ansible/ansible-files/site.yml` that imports all playbooks in the correct order:

1. Configure MOTD
2. Configure SSH
3. Create users
4. Configure packages
5. Apply Apache role
6. Configure cron
7. Generate hardware report

The site playbook should be able to configure the entire infrastructure with a single command.

<details>
<summary>Solution</summary>

```yaml
---
# /home/ansible/ansible-files/site.yml
# Master playbook for complete infrastructure configuration

- name: Configure MOTD
  import_playbook: motd.yml

- name: Configure SSH
  import_playbook: sshd.yml

- name: Create users
  import_playbook: users.yml

- name: Install packages
  import_playbook: packages.yml

- name: Deploy Apache
  import_playbook: apache.yml

- name: Configure cron
  import_playbook: cron.yml

- name: Generate hardware report
  import_playbook: hwreport.yml
```

Run with:
```bash
ansible-playbook site.yml
```
</details>

---

## Scoring Summary

| Task | Points | Description |
|------|--------|-------------|
| 1 | 15 | Install and configure Ansible |
| 2 | 10 | Ad-hoc command script |
| 3 | 15 | Ansible Vault configuration |
| 4 | 15 | Users with vault passwords |
| 5 | 10 | Configure MOTD |
| 6 | 10 | Configure SSH |
| 7 | 20 | Apache role |
| 8 | 15 | PHP info role with dependencies |
| 9 | 15 | Conditional package installation |
| 10 | 10 | Cron jobs |
| 11 | 10 | Time synchronization (system role) |
| 12 | 10 | SELinux boolean (system role) |
| 13 | 20 | LVM storage configuration |
| 14 | 15 | Hardware report |
| 15 | 15 | Hosts template |
| 16 | 10 | Password quality |
| 17 | 10 | Archive backup |
| 18 | 15 | Site playbook |
| **Total** | **240** | Scaled to 300 for exam |

**Passing Score**: 168/240 (70%) = 210/300 on actual exam

---

## Post-Exam Checklist

Verify before ending:

- [ ] All playbooks execute without errors
- [ ] Configurations persist after reboot
- [ ] All files have correct permissions
- [ ] Services are enabled and running
- [ ] Vault files are encrypted
- [ ] Templates generate correct content

---

## Key Tips

1. **Time Management**: ~13 minutes per task average
2. **Use ansible-doc**: `ansible-doc <module>` for syntax help
3. **Test incrementally**: Run playbooks after each task
4. **Check persistence**: Reboot a node to verify
5. **Read carefully**: Note which groups tasks apply to

Good luck!
