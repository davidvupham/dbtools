# Chapter 3 Quiz: Ad-Hoc Commands

Test your understanding of Ansible ad-hoc commands and essential modules.

**Time Limit**: 10 minutes
**Passing Score**: 80% (8/10 correct)

---

## Questions

### Q1. When should you use ad-hoc commands instead of playbooks?

A) For complex, multi-step automation
B) For quick, one-time tasks that don't need to be saved
C) For configuration management
D) For application deployment

<details>
<summary>Answer</summary>

**B) For quick, one-time tasks that don't need to be saved**

Ad-hoc commands are best for:
- Quick checks (disk space, uptime, connectivity)
- One-time operations (restart a service, kill a process)
- Exploring and testing modules before using in playbooks
- Emergency fixes

Use playbooks for: repeatable tasks, complex automation, version-controlled infrastructure.
</details>

---

### Q2. What is the difference between the `command` and `shell` modules?

A) No difference, they are aliases
B) `shell` supports piping and shell features; `command` does not
C) `command` is faster but less secure
D) `shell` only works on Linux; `command` works everywhere

<details>
<summary>Answer</summary>

**B) `shell` supports piping and shell features; `command` does not**

- **command module**: Executes commands directly, no shell processing. Cannot use pipes (`|`), redirects (`>`), or shell variables.
- **shell module**: Executes commands through a shell (`/bin/sh`). Supports pipes, redirects, and shell features.

Use `command` when possible (more secure, predictable). Use `shell` when you need shell features.
</details>

---

### Q3. Which module would you use to copy a file FROM a managed node TO the control node?

A) `copy`
B) `fetch`
C) `get_file`
D) `download`

<details>
<summary>Answer</summary>

**B) `fetch`**

- **copy**: Control node → Managed node (push files)
- **fetch**: Managed node → Control node (pull files)

Example: `ansible web1 -m fetch -a "src=/var/log/app.log dest=/tmp/logs/"`
</details>

---

### Q4. What does the `-a` flag specify in an ad-hoc command?

A) Ansible configuration file
B) Module arguments
C) Ask for password
D) All hosts

<details>
<summary>Answer</summary>

**B) Module arguments**

The `-a` or `--args` flag specifies arguments to pass to the module.

Example: `ansible all -m copy -a "src=/tmp/file dest=/opt/file"`

Here, `"src=/tmp/file dest=/opt/file"` are the arguments for the `copy` module.
</details>

---

### Q5. Which command installs the `httpd` package on all webservers?

A) `ansible webservers -m yum -a "name=httpd state=installed"`
B) `ansible webservers -m package -a "name=httpd state=present" -b`
C) `ansible webservers -m install -a "package=httpd"`
D) `ansible webservers -m apt -a "name=httpd state=latest"`

<details>
<summary>Answer</summary>

**B) `ansible webservers -m package -a "name=httpd state=present" -b`**

- The `package` module is OS-agnostic (works with yum, apt, dnf, etc.)
- `state=present` ensures the package is installed
- `-b` (become) is required for package installation (needs root/sudo)

Note: Option A uses `state=installed` which is valid but `state=present` is the standard.
</details>

---

### Q6. How do you ensure a service is running AND enabled at boot?

A) `ansible all -m service -a "name=nginx state=started enabled=yes" -b`
B) `ansible all -m systemctl -a "name=nginx running=true boot=true"`
C) `ansible all -m service -a "name=nginx state=running autostart=yes"`
D) `ansible all -m service -a "name=nginx start=yes enable=yes"`

<details>
<summary>Answer</summary>

**A) `ansible all -m service -a "name=nginx state=started enabled=yes" -b`**

Service module parameters:
- `name`: Service name
- `state`: `started`, `stopped`, `restarted`, `reloaded`
- `enabled`: `yes` or `no` (start at boot)

Both `state=started` and `enabled=yes` are needed to ensure the service runs now AND on reboot.
</details>

---

### Q7. What does `state=absent` mean when used with the `file` module?

A) The file should be empty
B) The file should be hidden
C) The file should be deleted
D) The file should not be modified

<details>
<summary>Answer</summary>

**C) The file should be deleted**

File module states:
- `absent`: Delete the file/directory
- `directory`: Create a directory
- `file`: Ensure it's a regular file (doesn't create)
- `touch`: Create empty file or update timestamp
- `link`: Create symbolic link
- `hard`: Create hard link
</details>

---

### Q8. Which command creates a user with a home directory?

A) `ansible all -m user -a "name=deploy home=/home/deploy" -b`
B) `ansible all -m user -a "name=deploy create_home=yes" -b`
C) `ansible all -m adduser -a "name=deploy homedir=yes" -b`
D) `ansible all -m account -a "user=deploy home=create" -b`

<details>
<summary>Answer</summary>

**B) `ansible all -m user -a "name=deploy create_home=yes" -b`**

User module parameters:
- `name`: Username (required)
- `state`: `present` or `absent`
- `create_home`: `yes` or `no`
- `groups`: Additional groups
- `shell`: Login shell
- `password`: Encrypted password hash
- `uid`: User ID
</details>

---

### Q9. How do you run a command on only 3 hosts at a time?

A) `ansible all -m command -a "date" --limit=3`
B) `ansible all -m command -a "date" -f 3`
C) `ansible all -m command -a "date" --parallel=3`
D) `ansible all -m command -a "date" --batch=3`

<details>
<summary>Answer</summary>

**B) `ansible all -m command -a "date" -f 3`**

The `-f` or `--forks` flag controls parallelism (default is 5).

- `-f 3`: Run on 3 hosts simultaneously
- `-f 1`: Run on 1 host at a time (serial)
- `-f 50`: Run on 50 hosts simultaneously (if you have that many)
</details>

---

### Q10. What is the output when running this command if nginx is already installed?

```bash
ansible web1 -m package -a "name=nginx state=present" -b
```

A) `web1 | FAILED` with error message
B) `web1 | CHANGED` with installation details
C) `web1 | SUCCESS` with `"changed": false`
D) `web1 | SKIPPED` because nginx exists

<details>
<summary>Answer</summary>

**C) `web1 | SUCCESS` with `"changed": false`**

This demonstrates idempotency:
- If nginx is NOT installed: `CHANGED` (installs it)
- If nginx IS already installed: `SUCCESS` with `changed: false` (no action needed)

The task succeeds but reports no changes were made.
</details>

---

## Scoring

| Score | Result |
|-------|--------|
| 10/10 | Excellent! Ready for Chapter 4 |
| 8-9/10 | Good understanding, review missed topics |
| 6-7/10 | Review Chapter 3 before proceeding |
| Below 6 | Re-read Chapter 3 and redo exercises |

---

## Review Topics

If you missed questions, review these sections:

- **Q1**: [When to use Ad-Hoc Commands](../03-adhoc-commands.md)
- **Q2**: [Command vs Shell Module](../03-adhoc-commands.md)
- **Q3-4**: [Essential Modules](../03-adhoc-commands.md)
- **Q5**: [Package Management](../03-adhoc-commands.md)
- **Q6**: [Service Management](../03-adhoc-commands.md)
- **Q7**: [File Module](../03-adhoc-commands.md)
- **Q8**: [User Module](../03-adhoc-commands.md)
- **Q9**: [Parallelism](../03-adhoc-commands.md)
- **Q10**: [Idempotency](../03-adhoc-commands.md)
