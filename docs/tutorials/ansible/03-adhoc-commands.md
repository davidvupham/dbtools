# Chapter 3: Ad-Hoc Commands

Ad-hoc commands are Ansible's quick and powerful one-liners for immediate tasks. In this chapter, you'll learn how to execute commands efficiently without writing full playbooks.

## 🎯 Learning Objectives

By the end of this chapter, you will:

- Understand when to use ad-hoc commands vs playbooks
- Master the ad-hoc command syntax
- Use common modules for quick tasks
- Execute commands with privilege escalation
- Manage files, packages, and services from the command line

## 📖 What are Ad-Hoc Commands?

Ad-hoc commands are **one-time tasks** you execute immediately without saving them in a playbook. Think of them as the "quick fixes" of Ansible automation.

### When to Use Ad-Hoc Commands

✅ **Good for**:
- Quick checks (disk space, service status)
- One-time tasks (restarting a service, checking a file)
- Testing before writing a playbook
- Emergency fixes
- Information gathering

❌ **Not ideal for**:
- Complex multi-step tasks
- Repeatable workflows
- Tasks you'll run regularly
- Tasks needing documentation

**Rule of Thumb**: If you'll run it more than twice, write a playbook!

## 🔧 Ad-Hoc Command Syntax

```bash
ansible <host-pattern> -m <module> -a "<arguments>" [options]
```

**Components**:
- `<host-pattern>`: Which hosts to target (from inventory)
- `-m <module>`: Module to execute
- `-a "<arguments>"`: Module-specific arguments
- `[options]`: Additional flags (user, privilege, etc.)

### Simple Example

```bash
ansible webservers -m ping
```

Breaks down to:
- `webservers`: Target the webservers group
- `-m ping`: Use the ping module
- No arguments needed for ping

## 📦 Essential Modules for Ad-Hoc Commands

### 1. The Command Module

Executes commands without using a shell.

```bash
# Get hostname
ansible all -m command -a "hostname"

# Check uptime
ansible all -m command -a "uptime"

# List files
ansible all -m command -a "ls -l /tmp"

# Create directory (idempotent with file module is better)
ansible all -m command -a "mkdir -p /tmp/test"
```

**Limitations**:
- No pipes, redirects, or shell variables
- For those, use the `shell` module

### 2. The Shell Module

Executes commands through a shell (/bin/sh).

```bash
# Use pipes
ansible all -m shell -a "ps aux | grep nginx"

# Use redirects
ansible all -m shell -a "echo 'Hello' > /tmp/hello.txt"

# Use shell variables
ansible all -m shell -a "echo $HOME"

# Chain commands
ansible all -m shell -a "cd /tmp && ls -l"
```

**Warning**: Be careful with shell module - it's less secure than command module.

### 3. The Copy Module

Copy files from control node to managed nodes.

```bash
# Copy a file
ansible webservers -m copy -a "src=/tmp/test.txt dest=/tmp/test.txt"

# Copy with permissions
ansible webservers -m copy -a "src=/tmp/script.sh dest=/usr/local/bin/script.sh mode=0755"

# Copy with ownership
ansible webservers -m copy -a "src=/tmp/config dest=/etc/myapp/config owner=root group=root mode=0644"

# Create a file with content
ansible all -m copy -a "content='Hello World\n' dest=/tmp/hello.txt"
```

### 4. The File Module

Manage files, directories, and their properties.

```bash
# Create a directory
ansible all -m file -a "path=/tmp/mydir state=directory"

# Create nested directories
ansible all -m file -a "path=/tmp/a/b/c state=directory mode=0755"

# Create an empty file
ansible all -m file -a "path=/tmp/emptyfile state=touch"

# Delete a file
ansible all -m file -a "path=/tmp/oldfile state=absent"

# Delete a directory and contents
ansible all -m file -a "path=/tmp/olddir state=absent"

# Change permissions
ansible all -m file -a "path=/tmp/script.sh mode=0755"

# Change ownership
ansible all -m file -a "path=/var/www/html owner=www-data group=www-data recurse=yes"

# Create a symlink
ansible all -m file -a "src=/usr/bin/python3 dest=/usr/bin/python state=link"
```

### 5. The Package Module

Install packages (auto-detects package manager).

```bash
# Install a package
ansible webservers -m package -a "name=nginx state=present"

# Install specific version
ansible webservers -m package -a "name=nginx-1.18.0 state=present"

# Remove a package
ansible webservers -m package -a "name=apache2 state=absent"

# Update a package
ansible webservers -m package -a "name=nginx state=latest"
```

For OS-specific package managers:

```bash
# APT (Ubuntu/Debian)
ansible webservers -m apt -a "name=nginx state=present update_cache=yes"

# YUM/DNF (RHEL/CentOS)
ansible webservers -m yum -a "name=nginx state=present"

# Homebrew (macOS)
ansible webservers -m homebrew -a "name=nginx state=present"
```

### 6. The Service Module

Manage system services.

```bash
# Start a service
ansible webservers -m service -a "name=nginx state=started"

# Stop a service
ansible webservers -m service -a "name=nginx state=stopped"

# Restart a service
ansible webservers -m service -a "name=nginx state=restarted"

# Reload a service (graceful restart)
ansible webservers -m service -a "name=nginx state=reloaded"

# Enable service at boot
ansible webservers -m service -a "name=nginx enabled=yes"

# Disable service at boot
ansible webservers -m service -a "name=nginx enabled=no"

# Restart and enable
ansible webservers -m service -a "name=nginx state=restarted enabled=yes"
```

### 7. The User Module

Manage user accounts.

```bash
# Create a user
ansible all -m user -a "name=john state=present"

# Create user with specific UID and shell
ansible all -m user -a "name=john uid=1500 shell=/bin/bash state=present"

# Create user with home directory
ansible all -m user -a "name=john create_home=yes state=present"

# Add user to groups
ansible all -m user -a "name=john groups=sudo,www-data append=yes"

# Set user password (use Vault for real passwords!)
ansible all -m user -a "name=john password='$6$rounds=656000$...' update_password=always"

# Lock a user account
ansible all -m user -a "name=john state=present password_lock=yes"

# Remove a user
ansible all -m user -a "name=john state=absent remove=yes"
```

### 8. The Group Module

Manage groups.

```bash
# Create a group
ansible all -m group -a "name=developers state=present"

# Create group with specific GID
ansible all -m group -a "name=developers gid=1100 state=present"

# Remove a group
ansible all -m group -a "name=oldgroup state=absent"
```

### 9. The Git Module

Manage Git repositories.

```bash
# Clone a repository
ansible webservers -m git -a "repo=https://github.com/user/repo.git dest=/var/www/app"

# Clone specific branch
ansible webservers -m git -a "repo=https://github.com/user/repo.git dest=/var/www/app version=develop"

# Update repository
ansible webservers -m git -a "repo=https://github.com/user/repo.git dest=/var/www/app update=yes"

# Clone with specific version/tag
ansible webservers -m git -a "repo=https://github.com/user/repo.git dest=/var/www/app version=v1.2.3"
```

### 10. The Setup Module

Gather system information (facts).

```bash
# Gather all facts
ansible all -m setup

# Filter for specific facts
ansible all -m setup -a "filter=ansible_os_family"
ansible all -m setup -a "filter=ansible_distribution*"
ansible all -m setup -a "filter=ansible_mem*"
ansible all -m setup -a "filter=ansible_processor*"
ansible all -m setup -a "filter=ansible_mounts"
ansible all -m setup -a "filter=ansible_all_ipv4_addresses"

# Gather only minimal facts (faster)
ansible all -m setup -a "gather_subset=!all"

# Gather specific fact subsets
ansible all -m setup -a "gather_subset=network,virtual"
```

## 🔐 Privilege Escalation

Many tasks require elevated privileges (sudo).

### Using Become (Sudo)

```bash
# Become root (sudo)
ansible all -m package -a "name=nginx state=present" --become

# Specify become method
ansible all -m command -a "whoami" --become --become-method=sudo

# Specify become user
ansible all -m command -a "whoami" --become --become-user=postgres

# Ask for sudo password
ansible all -m package -a "name=nginx state=present" --become --ask-become-pass
```

### Shortcuts

```bash
# -b is short for --become
ansible all -m package -a "name=nginx state=present" -b

# -K is short for --ask-become-pass
ansible all -m package -a "name=nginx state=present" -b -K
```

## 🌐 Connection and Authentication Options

### SSH Authentication

```bash
# Use specific user
ansible all -m ping -u admin

# Ask for SSH password
ansible all -m ping --ask-pass

# Use specific private key
ansible all -m ping --private-key=~/.ssh/custom_key

# Combine options
ansible all -m ping -u admin --private-key=~/.ssh/admin_key
```

### Connection Types

```bash
# Local connection (no SSH)
ansible localhost -m setup --connection=local

# Specify connection type
ansible windows -m win_ping --connection=winrm
```

## 📊 Output Control

### Verbose Output

```bash
# Verbose (-v)
ansible all -m ping -v

# More verbose (-vv)
ansible all -m ping -vv

# Very verbose (-vvv) - shows SSH connection details
ansible all -m ping -vvv

# Maximum verbosity (-vvvv) - includes internal Ansible details
ansible all -m ping -vvvv
```

### One-Line Output

```bash
# Compact output
ansible all -m command -a "uptime" --one-line
```

## 🎯 Practical Ad-Hoc Command Patterns

### System Administration

```bash
# Check disk space across all servers
ansible all -m shell -a "df -h"

# Check memory usage
ansible all -m shell -a "free -h"

# Check running processes
ansible all -m shell -a "ps aux | head -20"

# Check system uptime
ansible all -m command -a "uptime"

# Check kernel version
ansible all -m command -a "uname -r"

# Reboot servers (be careful!)
ansible webservers -m reboot --become

# Check if reboot is required (Ubuntu/Debian)
ansible all -m stat -a "path=/var/run/reboot-required"
```

### File Management

```bash
# Find large files
ansible all -m shell -a "find /var/log -type f -size +100M"

# Check file permissions
ansible all -m command -a "ls -l /etc/passwd"

# Find files modified in last 24 hours
ansible all -m shell -a "find /var/log -type f -mtime -1"

# Count files in directory
ansible all -m shell -a "ls -l /tmp | wc -l"

# Check disk space for specific mount
ansible all -m shell -a "df -h /var"
```

### Service Management

```bash
# Check service status
ansible webservers -m service -a "name=nginx" -b

# Check if service is running
ansible webservers -m shell -a "systemctl is-active nginx"

# Check enabled services
ansible all -m shell -a "systemctl list-unit-files --type=service --state=enabled"

# View service logs
ansible webservers -m shell -a "journalctl -u nginx -n 50"
```

### Package Management

```bash
# List installed packages
ansible all -m shell -a "dpkg -l | grep nginx"

# Check for available updates (Ubuntu/Debian)
ansible all -m apt -a "update_cache=yes" -b

# Check package version
ansible all -m shell -a "nginx -v"
```

### Network Operations

```bash
# Test connectivity to external host
ansible all -m command -a "ping -c 3 google.com"

# Check open ports
ansible all -m shell -a "netstat -tuln | grep LISTEN"

# Check DNS resolution
ansible all -m command -a "nslookup example.com"

# Get public IP
ansible all -m shell -a "curl -s ifconfig.me"

# Check network interfaces
ansible all -m command -a "ip addr show"
```

### User Management

```bash
# List all users
ansible all -m command -a "cat /etc/passwd"

# Check who is logged in
ansible all -m command -a "who"

# Check last logins
ansible all -m command -a "last -n 10"

# Check sudo access
ansible all -m shell -a "sudo -l" -b
```

## 🛠️ Exercises

### Exercise 3.1: Basic Commands

**Task**: Execute basic system commands on localhost.

```bash
# Check system information
ansible localhost -m command -a "hostname" --connection=local
ansible localhost -m command -a "uptime" --connection=local
ansible localhost -m command -a "date" --connection=local

# Use shell for complex commands
ansible localhost -m shell -a "ps aux | grep ssh" --connection=local
```

---

### Exercise 3.2: File Operations

**Task**: Practice file and directory management.

```bash
# Create a directory
ansible localhost -m file -a "path=/tmp/ansible-test state=directory" --connection=local

# Create a file with content
ansible localhost -m copy -a "content='Hello Ansible!\n' dest=/tmp/ansible-test/hello.txt" --connection=local

# Check file was created
ansible localhost -m command -a "cat /tmp/ansible-test/hello.txt" --connection=local

# Change file permissions
ansible localhost -m file -a "path=/tmp/ansible-test/hello.txt mode=0600" --connection=local

# Verify permissions
ansible localhost -m command -a "ls -l /tmp/ansible-test/hello.txt" --connection=local

# Clean up
ansible localhost -m file -a "path=/tmp/ansible-test state=absent" --connection=local
```

---

### Exercise 3.3: Package Management

**Task**: Install and manage a package (using nginx as an example).

**Note**: Requires sudo privileges.

```bash
# Install nginx
ansible localhost -m package -a "name=nginx state=present" --connection=local -b

# Check nginx version
ansible localhost -m command -a "nginx -v" --connection=local

# Check if nginx is running
ansible localhost -m service -a "name=nginx" --connection=local -b

# Start nginx if not running
ansible localhost -m service -a "name=nginx state=started" --connection=local -b

# Stop nginx
ansible localhost -m service -a "name=nginx state=stopped" --connection=local -b

# Remove nginx (optional - cleanup)
ansible localhost -m package -a "name=nginx state=absent" --connection=local -b
```

---

### Exercise 3.4: Gather Facts

**Task**: Explore system facts about your hosts.

```bash
# Get all facts
ansible localhost -m setup --connection=local > /tmp/facts.json

# Get specific facts
ansible localhost -m setup -a "filter=ansible_distribution*" --connection=local
ansible localhost -m setup -a "filter=ansible_memtotal_mb" --connection=local
ansible localhost -m setup -a "filter=ansible_processor_count" --connection=local
ansible localhost -m setup -a "filter=ansible_default_ipv4" --connection=local

# Answer these questions using facts:
# 1. What OS are you running?
# 2. How much RAM do you have?
# 3. How many CPU cores?
# 4. What's your IP address?
```

---

### Exercise 3.5: Multi-Server Operations

**Task**: Execute commands across multiple hosts.

**Setup**: Create an inventory with multiple test hosts (using localhost with aliases).

```ini
# inventory
[testservers]
test1 ansible_connection=local
test2 ansible_connection=local
test3 ansible_connection=local
```

**Commands**:

```bash
# Ping all test servers
ansible testservers -m ping -i inventory

# Create directories on all servers
ansible testservers -m file -a "path=/tmp/test-{{inventory_hostname}} state=directory" -i inventory

# Check created directories
ansible testservers -m command -a "ls -ld /tmp/test-*" -i inventory

# Clean up
ansible testservers -m shell -a "rm -rf /tmp/test-*" -i inventory
```

---

### Exercise 3.6: Real-World Scenario

**Task**: Debug a "slow server" using ad-hoc commands.

**Scenario**: A server is reported to be slow. Investigate using Ansible.

```bash
# Check system load
ansible slow_server -m command -a "uptime"

# Check memory usage
ansible slow_server -m shell -a "free -h"

# Check disk space
ansible slow_server -m shell -a "df -h"

# Check top processes
ansible slow_server -m shell -a "ps aux --sort=-%cpu | head -10"

# Check disk I/O
ansible slow_server -m shell -a "iostat -x 1 3"

# Check network connections
ansible slow_server -m shell -a "netstat -tuln | wc -l"

# Check system logs for errors
ansible slow_server -m shell -a "journalctl -p err -n 20"
```

**Challenge**: Create a single shell command that outputs a "health report" with all the above information.

<details>
<summary>Solution</summary>

```bash
ansible slow_server -m shell -a "echo '=== System Health Report ===' && \
  echo '=== Uptime ===' && uptime && \
  echo '=== Memory ===' && free -h && \
  echo '=== Disk Space ===' && df -h && \
  echo '=== Top Processes ===' && ps aux --sort=-%cpu | head -10"
```

</details>

---

## 🔧 Troubleshooting

### Problem: "Permission denied"

**Solution**: Use `--become` or `-b` for privilege escalation:

```bash
ansible all -m package -a "name=nginx state=present" -b
```

### Problem: Module not found

**Solution**: Check module name spelling:

```bash
# List available modules
ansible-doc -l | grep <keyword>

# Get module documentation
ansible-doc <module_name>
```

### Problem: "Failed to connect"

**Solution**: Check connectivity and credentials:

```bash
# Test SSH manually
ssh user@hostname

# Use verbose mode
ansible all -m ping -vvv

# Try different connection method
ansible all -m ping --connection=local
```

### Problem: Command output truncated

**Solution**: Use shell module with proper output handling:

```bash
# Instead of command module
ansible all -m shell -a "your-command 2>&1"
```

## 📚 Module Documentation

Get help for any module:

```bash
# List all modules
ansible-doc -l

# Search for modules
ansible-doc -l | grep file

# Get detailed help for a module
ansible-doc file
ansible-doc copy
ansible-doc service

# Get examples for a module
ansible-doc -s package
```

## 📖 Key Takeaways

✅ Ad-hoc commands are for quick, one-off tasks
✅ Use `command` module for simple commands without shell features
✅ Use `shell` module when you need pipes, redirects, or variables
✅ Common modules: copy, file, package, service, user, group
✅ Use `--become` or `-b` for privilege escalation
✅ Check `ansible-doc` for module documentation
✅ If you run a command more than twice, write a playbook!

## 🎓 What's Next?

Now that you can execute quick tasks with ad-hoc commands, you're ready to learn about **playbooks** - Ansible's way of creating reusable, documented automation.

**Next Chapter**: [Chapter 4: Playbooks Basics](04-playbooks-basics.md)

In the next chapter, you'll learn:
- What playbooks are and why they're important
- YAML syntax for playbooks
- Creating your first playbook
- Running and debugging playbooks

---

**Keep Practicing!** The more ad-hoc commands you run, the more comfortable you'll become with Ansible modules.
