# Chapter 2 Quiz: Inventory Management

Test your understanding of Ansible inventory files, host groups, patterns, and variables.

**Time Limit**: 10 minutes
**Passing Score**: 80% (8/10 correct)

---

## Questions

### Q1. Which two inventory formats does Ansible support?

A) JSON and XML
B) INI and YAML
C) CSV and JSON
D) TOML and INI

<details>
<summary>Answer</summary>

**B) INI and YAML**

Ansible supports:
- **INI format**: Traditional, simple, widely used
- **YAML format**: More structured, supports complex data types

Both formats can define hosts, groups, and variables.
</details>

---

### Q2. In an INI inventory file, how do you define a group of hosts?

A) `group: [host1, host2]`
B) `[groupname]` followed by hostnames
C) `groupname = host1, host2`
D) `<groupname>host1</groupname>`

<details>
<summary>Answer</summary>

**B) `[groupname]` followed by hostnames**

Example:
```ini
[webservers]
web1.example.com
web2.example.com
```
</details>

---

### Q3. What does the host pattern `web[1:5]` expand to?

A) web1, web5
B) web1, web2, web3, web4, web5
C) web15
D) web1-5

<details>
<summary>Answer</summary>

**B) web1, web2, web3, web4, web5**

Numeric ranges in inventory use the syntax `[start:end]` (inclusive). This creates 5 hosts: web1, web2, web3, web4, and web5.

You can also use alphabetic ranges: `db[a:c]` expands to `dba`, `dbb`, `dbc`
</details>

---

### Q4. Which special group automatically contains all hosts in the inventory?

A) `default`
B) `all`
C) `hosts`
D) `inventory`

<details>
<summary>Answer</summary>

**B) `all`**

Ansible has two special built-in groups:
- **all**: Contains every host in the inventory
- **ungrouped**: Contains hosts that are not in any other group (except `all`)
</details>

---

### Q5. How do you create a group of groups in INI format?

A) `[parentgroup:children]`
B) `[parentgroup:groups]`
C) `[parentgroup(children)]`
D) `[parentgroup->children]`

<details>
<summary>Answer</summary>

**A) `[parentgroup:children]`**

Example:
```ini
[webservers]
web1

[dbservers]
db1

[production:children]
webservers
dbservers
```

The `production` group now contains all hosts from both `webservers` and `dbservers`.
</details>

---

### Q6. Which inventory variable specifies a different SSH port for a host?

A) `ssh_port=2222`
B) `ansible_port=2222`
C) `ansible_ssh_port=2222`
D) `port=2222`

<details>
<summary>Answer</summary>

**B) `ansible_port=2222`**

Common inventory connection variables:
- `ansible_host`: IP address or hostname to connect to
- `ansible_port`: SSH port (default 22)
- `ansible_user`: SSH username
- `ansible_ssh_private_key_file`: Path to SSH private key
- `ansible_password`: SSH password (avoid in production)
</details>

---

### Q7. What command verifies that your inventory file is syntactically correct?

A) `ansible-inventory --verify`
B) `ansible-inventory --list`
C) `ansible --check inventory`
D) `ansible-playbook --syntax-check`

<details>
<summary>Answer</summary>

**B) `ansible-inventory --list`**

`ansible-inventory --list` parses the inventory and outputs it in JSON format. If there are syntax errors, it will report them.

Options:
- `--list`: Output all hosts in JSON
- `--graph`: Output group hierarchy as ASCII tree
- `--host <hostname>`: Show variables for a specific host
</details>

---

### Q8. In YAML inventory format, how are group variables defined?

A) Under `group_vars:` key
B) Under `vars:` key within the group
C) In a separate file only
D) Using the `variables:` key

<details>
<summary>Answer</summary>

**B) Under `vars:` key within the group**

Example:
```yaml
all:
  children:
    webservers:
      hosts:
        web1:
        web2:
      vars:
        http_port: 80
        ansible_user: deploy
```
</details>

---

### Q9. Which host pattern matches all hosts in EITHER webservers OR dbservers?

A) `webservers,dbservers`
B) `webservers:dbservers`
C) `webservers+dbservers`
D) `webservers|dbservers`

<details>
<summary>Answer</summary>

**B) `webservers:dbservers`**

Inventory patterns:
- `group1:group2` - Union (OR) - hosts in either group
- `group1:&group2` - Intersection (AND) - hosts in both groups
- `group1:!group2` - Exclusion - hosts in group1 but NOT in group2
- `*` or `all` - All hosts
</details>

---

### Q10. Where should you store sensitive host variables like passwords?

A) In the inventory file directly
B) In `group_vars/` or `host_vars/` directories with Ansible Vault encryption
C) In environment variables
D) In plain text files in `/etc/ansible/`

<details>
<summary>Answer</summary>

**B) In `group_vars/` or `host_vars/` directories with Ansible Vault encryption**

Best practices for sensitive data:
1. Store variables in `group_vars/` or `host_vars/` directories
2. Encrypt files containing secrets with Ansible Vault
3. Never commit unencrypted passwords to version control
4. Use `vault_password_file` for automation
</details>

---

## Scoring

| Score | Result |
|-------|--------|
| 10/10 | Excellent! Ready for Chapter 3 |
| 8-9/10 | Good understanding, review missed topics |
| 6-7/10 | Review Chapter 2 before proceeding |
| Below 6 | Re-read Chapter 2 and redo exercises |

---

## Review Topics

If you missed questions, review these sections:

- **Q1-2**: [Inventory Format](../02-inventory.md)
- **Q3**: [Host Ranges](../02-inventory.md)
- **Q4-5**: [Groups and Children](../02-inventory.md)
- **Q6**: [Connection Variables](../02-inventory.md)
- **Q7**: [Verifying Inventory](../02-inventory.md)
- **Q8**: [YAML Inventory Format](../02-inventory.md)
- **Q9**: [Host Patterns](../02-inventory.md)
- **Q10**: [Security Best Practices](../02-inventory.md)
