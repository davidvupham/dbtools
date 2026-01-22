# Chapter 1 Quiz: Getting Started with Ansible

Test your understanding of Ansible fundamentals, installation, and basic commands.

**Time Limit**: 10 minutes
**Passing Score**: 80% (8/10 correct)

---

## Questions

### Q1. What is the primary communication protocol Ansible uses to connect to Linux managed nodes?

A) HTTP/HTTPS
B) SSH
C) WinRM
D) SNMP

<details>
<summary>Answer</summary>

**B) SSH**

Ansible is agentless and uses SSH to connect to Linux/Unix managed nodes. For Windows, it uses WinRM.
</details>

---

### Q2. Which of the following is NOT a characteristic of Ansible?

A) Agentless
B) Declarative
C) Requires agents on managed nodes
D) Idempotent

<details>
<summary>Answer</summary>

**C) Requires agents on managed nodes**

Ansible is agentless - it doesn't require any software to be installed on managed nodes (other than Python for most modules).
</details>

---

### Q3. What is the correct order of precedence for Ansible configuration files (highest to lowest)?

A) `/etc/ansible/ansible.cfg` → `~/.ansible.cfg` → `./ansible.cfg` → `ANSIBLE_CONFIG`
B) `ANSIBLE_CONFIG` → `./ansible.cfg` → `~/.ansible.cfg` → `/etc/ansible/ansible.cfg`
C) `./ansible.cfg` → `~/.ansible.cfg` → `ANSIBLE_CONFIG` → `/etc/ansible/ansible.cfg`
D) `~/.ansible.cfg` → `./ansible.cfg` → `/etc/ansible/ansible.cfg` → `ANSIBLE_CONFIG`

<details>
<summary>Answer</summary>

**B) `ANSIBLE_CONFIG` → `./ansible.cfg` → `~/.ansible.cfg` → `/etc/ansible/ansible.cfg`**

Ansible checks these locations in order:
1. ANSIBLE_CONFIG environment variable (highest precedence)
2. ansible.cfg in current directory
3. ~/.ansible.cfg in home directory
4. /etc/ansible/ansible.cfg (lowest precedence)
</details>

---

### Q4. What does the following command do?

```bash
ansible all -m ping
```

A) Sends ICMP ping packets to all hosts
B) Tests Ansible connectivity to all hosts in inventory
C) Installs ping utility on all hosts
D) Checks network latency to all hosts

<details>
<summary>Answer</summary>

**B) Tests Ansible connectivity to all hosts in inventory**

The `ping` module is NOT an ICMP ping. It tests whether Ansible can:
- Connect to the host via SSH
- Execute Python on the managed node
- Return a response
</details>

---

### Q5. Which command displays information about all hosts and their variables in your inventory?

A) `ansible --list-hosts all`
B) `ansible-inventory --list`
C) `ansible all -m setup`
D) `ansible-doc -l`

<details>
<summary>Answer</summary>

**B) `ansible-inventory --list`**

- `ansible-inventory --list` shows inventory structure with all hosts and variables (JSON format)
- `ansible --list-hosts all` only shows hostnames
- `ansible all -m setup` gathers facts from hosts (requires connectivity)
- `ansible-doc -l` lists available modules
</details>

---

### Q6. In an inventory file, what does `ansible_connection=local` specify?

A) Connect to the host using local network only
B) Execute commands locally without SSH
C) Use localhost as a jump host
D) Disable remote connections

<details>
<summary>Answer</summary>

**B) Execute commands locally without SSH**

`ansible_connection=local` tells Ansible to run commands directly on the control node without using SSH. This is useful for managing the Ansible control node itself.
</details>

---

### Q7. What is the purpose of the `setup` module?

A) Install Ansible on managed nodes
B) Configure SSH connections
C) Gather system facts from managed nodes
D) Create initial inventory files

<details>
<summary>Answer</summary>

**C) Gather system facts from managed nodes**

The `setup` module collects detailed information (facts) about managed nodes including:
- Operating system details
- Network configuration
- Hardware information
- Installed packages
</details>

---

### Q8. Which command would you use to run an ad-hoc command with sudo privileges?

A) `ansible all -m command -a "whoami" --sudo`
B) `ansible all -m command -a "whoami" -b`
C) `ansible all -m command -a "whoami" --root`
D) `ansible all -m command -a "whoami" -p`

<details>
<summary>Answer</summary>

**B) `ansible all -m command -a "whoami" -b`**

The `-b` or `--become` flag enables privilege escalation (sudo by default). The old `--sudo` flag is deprecated.

To specify the sudo password: `--ask-become-pass` or `-K`
</details>

---

### Q9. What is the minimum Python version required on the Ansible control node?

A) Python 2.7
B) Python 3.5
C) Python 3.8
D) Python 3.9

<details>
<summary>Answer</summary>

**D) Python 3.9**

As of Ansible core 2.15+, Python 3.9 or newer is required on the control node. Managed nodes can use Python 2.7 or Python 3.5+ for most modules.
</details>

---

### Q10. What does "idempotent" mean in the context of Ansible?

A) Tasks run in parallel across all hosts
B) Running the same automation multiple times produces the same result
C) Tasks can be reverted if they fail
D) Ansible can detect configuration drift

<details>
<summary>Answer</summary>

**B) Running the same automation multiple times produces the same result**

Idempotency means:
- First run: Makes changes if needed (changed)
- Subsequent runs: No changes if system is already in desired state (ok)
- Safe to run repeatedly without unintended side effects
</details>

---

## Scoring

| Score | Result |
|-------|--------|
| 10/10 | Excellent! Ready for Chapter 2 |
| 8-9/10 | Good understanding, review missed topics |
| 6-7/10 | Review Chapter 1 before proceeding |
| Below 6 | Re-read Chapter 1 and redo exercises |

---

## Review Topics

If you missed questions, review these sections:

- **Q1-2**: [What is Ansible?](../01-getting-started.md#-what-is-ansible)
- **Q3**: [Initial Configuration](../01-getting-started.md#-initial-configuration)
- **Q4-5, Q7-8**: [Basic Ansible Commands](../01-getting-started.md#-basic-ansible-commands)
- **Q6**: [Creating Your First Inventory](../01-getting-started.md#-creating-your-first-inventory)
- **Q9**: [Installation Prerequisites](../01-getting-started.md#prerequisites-check)
- **Q10**: [Key Characteristics](../01-getting-started.md#key-characteristics)
