# Chapter 1: Getting Started with Ansible

Welcome to your first step in mastering Ansible! In this chapter, you'll install Ansible, understand its architecture, and run your first automation commands.

## 🎯 Learning Objectives

By the end of this chapter, you will:

- Understand what Ansible is and how it works
- Install Ansible on your system
- Understand Ansible's architecture
- Run your first Ansible command
- Set up a basic lab environment

## 📖 What is Ansible?

Ansible is an **automation engine** that lets you control and configure multiple computers from a single control machine. Think of it as a way to tell many computers what to do, all at once, without logging into each one individually.

### Key Characteristics

**Agentless**: Unlike other automation tools, Ansible doesn't require installing software on the machines you want to manage. It uses SSH (on Linux/Unix) or WinRM (on Windows).

**Declarative**: You describe the desired state ("I want Apache installed"), not the steps to get there.

**Idempotent**: You can run the same Ansible automation multiple times, and it will only make changes when needed. Running it twice doesn't create duplicate results.

**Simple**: Uses YAML (a human-readable data format) instead of complex programming languages.

## 🏗️ Ansible Architecture

### The Control Node

The **control node** is the machine where Ansible is installed and from which you run your automation. This is typically your laptop or a dedicated automation server.

Requirements:
- Linux, macOS, or WSL2 on Windows
- Python 3.9 or newer

### Managed Nodes

**Managed nodes** (also called "hosts") are the servers, network devices, or other systems you want to automate. Ansible connects to these over SSH or WinRM.

Requirements:
- SSH access (for Linux/Unix)
- Python 2.7 or Python 3.5+ (for most modules)

### The Connection Flow

```text
Control Node                    Managed Nodes
┌─────────────────┐            ┌─────────────────┐
│                 │   SSH      │                 │
│   Ansible       ├───────────>│   Server 1      │
│   (Your PC)     │            │                 │
│                 │            └─────────────────┘
│                 │
│                 │            ┌─────────────────┐
│                 │   SSH      │                 │
│                 ├───────────>│   Server 2      │
│                 │            │                 │
│                 │            └─────────────────┘
│                 │
│                 │            ┌─────────────────┐
│                 │   SSH      │                 │
│                 ├───────────>│   Server 3      │
│                 │            │                 │
└─────────────────┘            └─────────────────┘
```

## 💻 Installation

### Prerequisites Check

First, verify you have Python installed:

```bash
python3 --version
```

You should see version 3.9 or higher. If not, install Python first.

### Installing Ansible

#### On Ubuntu/Debian

```bash
# Update package index
sudo apt update

# Install dependencies
sudo apt install software-properties-common

# Add Ansible repository
sudo add-apt-repository --yes --update ppa:ansible/ansible

# Install Ansible
sudo apt install ansible
```

#### On RHEL/CentOS/Fedora

```bash
# Enable EPEL repository (for RHEL/CentOS)
sudo dnf install epel-release

# Install Ansible
sudo dnf install ansible
```

#### On macOS

```bash
# Using Homebrew
brew install ansible
```

#### Using pip (All platforms)

```bash
# Install using Python pip
python3 -m pip install --user ansible

# Add to PATH if needed
export PATH="$HOME/.local/bin:$PATH"
```

### Verify Installation

```bash
ansible --version
```

You should see output similar to:

```text
ansible [core 2.15.0]
  config file = None
  configured module search path = ...
  ansible python module location = ...
  python version = 3.11.2
```

## 🔧 Initial Configuration

### Creating a Configuration File

Ansible looks for configuration in several places (in order of precedence):

1. `ANSIBLE_CONFIG` environment variable
2. `ansible.cfg` in the current directory
3. `~/.ansible.cfg` in your home directory
4. `/etc/ansible/ansible.cfg` (system-wide)

Let's create a basic configuration file:

```bash
# Create a working directory
mkdir -p ~/ansible-tutorial
cd ~/ansible-tutorial

# Create a basic ansible.cfg
cat > ansible.cfg << 'EOF'
[defaults]
# Inventory file location
inventory = ./inventory

# Don't check SSH host keys (only for testing!)
host_key_checking = False

# Show timing information
callbacks_enabled = timer

# Use color output
force_color = True

# Number of parallel processes
forks = 5
EOF
```

**Note**: Disabling `host_key_checking` is convenient for learning but should not be used in production.

## 📋 Setting Up Your Lab Environment

### Option 1: Using Docker (Recommended for Beginners)

Docker provides isolated test environments without affecting your system.

```bash
# Pull a test container
docker run -d --name ansible-node1 \
  -p 2222:22 \
  --hostname node1 \
  rastasheep/ubuntu-sshd:18.04

# Get the container's IP
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ansible-node1

# Test SSH connection (password is 'root')
ssh -p 2222 root@localhost
```

### Option 2: Using Vagrant

Create a `Vagrantfile`:

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"

  (1..3).each do |i|
    config.vm.define "node#{i}" do |node|
      node.vm.hostname = "node#{i}"
      node.vm.network "private_network", ip: "192.168.56.#{10+i}"
    end
  end
end
```

Then start the VMs:

```bash
vagrant up
```

### Option 3: Using Your Own Servers

If you have test servers, ensure:
- SSH access is configured
- You have sudo privileges
- Python is installed

## 📝 Creating Your First Inventory

The **inventory** tells Ansible which hosts to manage. Create a file called `inventory`:

```ini
# Simple inventory file
[local]
localhost ansible_connection=local

[webservers]
node1 ansible_host=192.168.56.11 ansible_user=vagrant ansible_ssh_private_key_file=~/.vagrant.d/insecure_private_key

[databases]
node2 ansible_host=192.168.56.12 ansible_user=vagrant ansible_ssh_private_key_file=~/.vagrant.d/insecure_private_key

[all:children]
webservers
databases
```

**Understanding the syntax**:
- `[local]`, `[webservers]`, `[databases]` are **groups**
- `node1`, `node2` are **host names**
- `ansible_host` specifies the IP address
- `ansible_user` specifies the SSH user
- `ansible_connection=local` means run commands locally

For Docker setup:

```ini
[local]
localhost ansible_connection=local

[test_nodes]
node1 ansible_host=localhost ansible_port=2222 ansible_user=root ansible_ssh_pass=root
```

## 🚀 Your First Ansible Command

Let's verify Ansible can reach your hosts:

```bash
ansible all -m ping
```

**Breaking down this command**:
- `ansible` - The Ansible command-line tool
- `all` - Target all hosts in inventory
- `-m ping` - Use the ping module (tests connectivity)

Expected output:

```json
localhost | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
node1 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

### Understanding the Output

- `SUCCESS` - The module ran successfully
- `changed: false` - Nothing was modified
- `ping: pong` - The response from the ping module

## 🎯 Basic Ansible Commands

### Checking Host Connectivity

```bash
# Ping all hosts
ansible all -m ping

# Ping specific group
ansible webservers -m ping

# Ping specific host
ansible node1 -m ping
```

### Getting System Information

```bash
# Gather facts about all hosts
ansible all -m setup

# Get specific facts
ansible all -m setup -a "filter=ansible_os_family"

# Get memory information
ansible all -m setup -a "filter=ansible_memtotal_mb"
```

### Running Shell Commands

```bash
# Check disk space
ansible all -m shell -a "df -h"

# Check uptime
ansible all -m command -a "uptime"

# List processes
ansible all -m shell -a "ps aux | head -10"
```

## 📚 Understanding Modules

**Modules** are the units of work in Ansible. Each module does a specific task:

- `ping` - Tests connectivity
- `command` - Runs commands (doesn't use shell)
- `shell` - Runs commands using shell
- `copy` - Copies files
- `file` - Manages files and directories
- `package` - Installs packages
- `service` - Manages services

We'll explore many more in upcoming chapters!

## 🔍 Command Structure

Ansible ad-hoc commands follow this pattern:

```bash
ansible <host-pattern> [options]

Common options:
  -m MODULE     Specify the module to use
  -a ARGS       Module arguments
  -i INVENTORY  Specify inventory file
  -u USER       Connect as this user
  -b            Become (sudo)
  --ask-pass    Prompt for SSH password
  --ask-become-pass  Prompt for sudo password
```

## 🛠️ Exercises

### Exercise 1.1: Installation Verification

**Task**: Verify your Ansible installation and check the version.

**Steps**:

```bash
# Check Ansible version
ansible --version

# Check Ansible configuration
ansible-config dump --only-changed
```

**Expected Result**: You should see version information and any custom configuration.

---

### Exercise 1.2: Create an Inventory

**Task**: Create an inventory file with your test systems.

**Steps**:

1. Create `inventory` file
2. Add at least one host (can be localhost)
3. Create at least two groups

**Example Solution**:

```ini
[local]
localhost ansible_connection=local

[test]
testhost ansible_host=127.0.0.1 ansible_connection=local
```

---

### Exercise 1.3: Test Connectivity

**Task**: Use Ansible to verify you can reach all hosts.

**Steps**:

```bash
# Test all hosts
ansible all -m ping -i inventory

# Test specific group
ansible local -m ping
```

**Expected Result**: All hosts should return `SUCCESS` with `"ping": "pong"`.

---

### Exercise 1.4: Gather System Facts

**Task**: Collect and display information about your hosts.

**Steps**:

```bash
# Get all facts
ansible localhost -m setup

# Get hostname
ansible localhost -m setup -a "filter=ansible_hostname"

# Get IP addresses
ansible localhost -m setup -a "filter=ansible_all_ipv4_addresses"

# Get OS information
ansible localhost -m setup -a "filter=ansible_distribution*"
```

**Questions to Answer**:
1. What is the hostname of your control node?
2. How much memory does it have?
3. What operating system is it running?

---

### Exercise 1.5: Run Your First Command

**Task**: Use Ansible to execute system commands on your hosts.

**Steps**:

```bash
# Check current date/time
ansible all -m command -a "date"

# Check disk usage
ansible all -m shell -a "df -h /"

# Check who is logged in
ansible all -m command -a "whoami"
```

**Challenge**: Run a command that creates a file called `/tmp/ansible-test.txt` with the content "Hello Ansible!".

**Hint**: Use the `shell` module with echo and redirection.

<details>
<summary>Solution</summary>

```bash
ansible all -m shell -a "echo 'Hello Ansible!' > /tmp/ansible-test.txt"

# Verify it was created
ansible all -m command -a "cat /tmp/ansible-test.txt"
```

</details>

---

## 🔧 Troubleshooting

### Problem: "ansible: command not found"

**Solution**: Ansible is not in your PATH. Try:

```bash
# Find where Ansible was installed
python3 -m pip show ansible

# Add to PATH (for pip user install)
export PATH="$HOME/.local/bin:$PATH"

# Make it permanent (add to ~/.bashrc)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### Problem: "Permission denied (publickey)"

**Solution**: SSH keys are not set up properly.

```bash
# Generate SSH key if you don't have one
ssh-keygen -t rsa -b 4096

# Copy key to remote host
ssh-copy-id user@hostname

# Or use password authentication
ansible all -m ping --ask-pass
```

### Problem: "Failed to connect to the host via ssh"

**Solution**: Check your inventory file settings.

```bash
# Verify SSH manually first
ssh user@hostname

# Check Ansible inventory syntax
ansible-inventory --list -i inventory

# Test with verbose output
ansible all -m ping -vvv
```

### Problem: Module not found

**Solution**: Update Ansible or check module name.

```bash
# List all available modules
ansible-doc -l

# Get help for specific module
ansible-doc ping
```

## 📖 Key Takeaways

✅ Ansible is agentless and uses SSH for communication
✅ The control node runs Ansible; managed nodes are the targets
✅ Inventory files define which hosts Ansible manages
✅ Modules are the units of work in Ansible
✅ Ad-hoc commands are quick one-liners for immediate tasks
✅ The `-m` flag specifies the module, `-a` provides arguments

## 🎓 What's Next?

Now that you have Ansible installed and have run your first commands, you're ready to learn about **inventory management** in depth.

**Next Chapter**: [Chapter 2: Inventory Management](02-inventory.md)

In the next chapter, you'll learn:
- How to organize hosts into groups
- Using variables in inventory
- Dynamic inventory
- Inventory patterns and host selection

---

**Questions or Issues?** Review the troubleshooting section or consult the [Ansible documentation](https://docs.ansible.com/ansible/latest/getting_started/).
