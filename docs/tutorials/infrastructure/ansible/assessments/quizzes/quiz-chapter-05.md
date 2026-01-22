# Chapter 5 Quiz: Variables and Facts

Test your understanding of Ansible variables, facts, and variable precedence.

**Time Limit**: 10 minutes
**Passing Score**: 80% (8/10 correct)

---

## Questions

### Q1. Which of the following has the HIGHEST variable precedence?

A) Role defaults (`defaults/main.yml`)
B) Playbook vars (`vars:` section)
C) Extra vars (`-e` on command line)
D) Inventory group_vars

<details>
<summary>Answer</summary>

**C) Extra vars (`-e` on command line)**

Variable precedence (simplified, low to high):
1. Role defaults (lowest)
2. Inventory group_vars/host_vars
3. Playbook vars
4. Role vars
5. Block vars
6. Task vars
7. Extra vars (-e) (highest)

Extra vars ALWAYS win because they're explicitly set at runtime.
</details>

---

### Q2. How do you access the IP address of the current host using Ansible facts?

A) `{{ ip_address }}`
B) `{{ ansible_facts['default_ipv4']['address'] }}`
C) `{{ host.ip }}`
D) `{{ network.ipv4 }}`

<details>
<summary>Answer</summary>

**B) `{{ ansible_facts['default_ipv4']['address'] }}`**

Or the legacy syntax: `{{ ansible_default_ipv4.address }}`

Ansible gathers facts automatically (unless disabled). Common facts:
- `ansible_hostname` - Hostname
- `ansible_os_family` - OS family (Debian, RedHat)
- `ansible_memtotal_mb` - Total memory
- `ansible_processor_vcpus` - CPU count
</details>

---

### Q3. What does the `register` keyword do?

A) Creates a new variable file
B) Stores the result of a task in a variable
C) Registers a callback plugin
D) Saves variables to disk

<details>
<summary>Answer</summary>

**B) Stores the result of a task in a variable**

Example:
```yaml
- name: Get uptime
  command: uptime
  register: uptime_result

- debug:
    msg: "{{ uptime_result.stdout }}"
```

Registered variables contain:
- `stdout`, `stderr` - Command output
- `rc` - Return code
- `changed` - Whether task made changes
- `failed` - Whether task failed
</details>

---

### Q4. How do you disable automatic fact gathering in a playbook?

A) `facts: false`
B) `gather_facts: false`
C) `no_facts: true`
D) `skip_facts: yes`

<details>
<summary>Answer</summary>

**B) `gather_facts: false`**

Example:
```yaml
- hosts: all
  gather_facts: false
  tasks:
    - name: This runs without gathering facts
      debug:
        msg: "No facts collected"
```

Disabling facts improves performance when you don't need system information.
</details>

---

### Q5. Where should you define variables that apply to all hosts in the `webservers` group?

A) `host_vars/webservers.yml`
B) `group_vars/webservers.yml` or `group_vars/webservers/`
C) `vars/webservers.yml`
D) `inventory/webservers.yml`

<details>
<summary>Answer</summary>

**B) `group_vars/webservers.yml` or `group_vars/webservers/`**

Variable file locations:
- `group_vars/all.yml` - All hosts
- `group_vars/groupname.yml` - Specific group
- `group_vars/groupname/` - Directory with multiple files
- `host_vars/hostname.yml` - Specific host

Ansible automatically loads these files when running playbooks.
</details>

---

### Q6. What is the output of `{{ "Hello" | upper }}`?

A) `Hello`
B) `HELLO`
C) `hello`
D) `"HELLO"`

<details>
<summary>Answer</summary>

**B) `HELLO`**

Jinja2 filters transform variable values:
- `| upper` - Uppercase
- `| lower` - Lowercase
- `| default('value')` - Default if undefined
- `| trim` - Remove whitespace
- `| length` - Get length
- `| join(',')` - Join list elements
</details>

---

### Q7. How do you provide a default value if a variable is undefined?

A) `{{ variable or 'default' }}`
B) `{{ variable | default('default_value') }}`
C) `{{ variable ?? 'default' }}`
D) `{{ variable else 'default' }}`

<details>
<summary>Answer</summary>

**B) `{{ variable | default('default_value') }}`**

Examples:
```yaml
# Use 'anonymous' if username is undefined
user: "{{ username | default('anonymous') }}"

# Use omit to skip parameter entirely if undefined
shell: "{{ user_shell | default(omit) }}"

# Fail if not defined
required_var: "{{ must_exist | mandatory }}"
```
</details>

---

### Q8. What is the difference between `vars` and `vars_files` in a playbook?

A) No difference, they are aliases
B) `vars` defines inline; `vars_files` loads from external files
C) `vars_files` supports encryption; `vars` does not
D) `vars` is for strings; `vars_files` is for lists

<details>
<summary>Answer</summary>

**B) `vars` defines inline; `vars_files` loads from external files**

```yaml
- hosts: all
  vars:                    # Inline variables
    app_port: 8080
    app_name: myapp

  vars_files:             # External files
    - vars/common.yml
    - vars/secrets.yml
```

Both can be used together in the same playbook.
</details>

---

### Q9. Which special variable contains the hostname as configured in the inventory?

A) `{{ hostname }}`
B) `{{ ansible_hostname }}`
C) `{{ inventory_hostname }}`
D) `{{ host }}`

<details>
<summary>Answer</summary>

**C) `{{ inventory_hostname }}`**

Important distinction:
- `inventory_hostname` - The name as defined in inventory
- `ansible_hostname` - The actual hostname from the system (fact)

Example: If inventory has `web1 ansible_host=192.168.1.10`, then:
- `inventory_hostname` = "web1"
- `ansible_hostname` = actual system hostname (might be different)
</details>

---

### Q10. How do you create a custom fact that persists on the managed node?

A) Add to `ansible.cfg`
B) Create a file in `/etc/ansible/facts.d/` with `.fact` extension
C) Set `ansible_local` variable
D) Use the `set_fact` module with `cacheable: yes`

<details>
<summary>Answer</summary>

**B) Create a file in `/etc/ansible/facts.d/` with `.fact` extension**

Custom facts (local facts):
1. Create `/etc/ansible/facts.d/` directory on managed node
2. Add `.fact` files (INI, JSON, or executable scripts)
3. Access via `ansible_local.factname`

Example `/etc/ansible/facts.d/custom.fact`:
```ini
[general]
app_version=1.2.3
environment=production
```

Access: `{{ ansible_local.custom.general.app_version }}`
</details>

---

## Scoring

| Score | Result |
|-------|--------|
| 10/10 | Excellent! Ready for Chapter 6 |
| 8-9/10 | Good understanding, review missed topics |
| 6-7/10 | Review Chapter 5 before proceeding |
| Below 6 | Re-read Chapter 5 and redo exercises |

---

## Review Topics

If you missed questions, review these sections:

- **Q1**: [Variable Precedence](../05-variables-facts.md)
- **Q2, Q4**: [Ansible Facts](../05-variables-facts.md)
- **Q3**: [Registering Variables](../05-variables-facts.md)
- **Q5**: [Group and Host Variables](../05-variables-facts.md)
- **Q6-7**: [Jinja2 Filters](../05-variables-facts.md)
- **Q8**: [Variable Files](../05-variables-facts.md)
- **Q9**: [Special Variables](../05-variables-facts.md)
- **Q10**: [Custom Facts](../05-variables-facts.md)
