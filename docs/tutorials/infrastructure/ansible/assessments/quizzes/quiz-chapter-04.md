# Chapter 4 Quiz: Playbooks Basics

Test your understanding of Ansible playbooks, YAML syntax, and playbook execution.

**Time Limit**: 10 minutes
**Passing Score**: 80% (8/10 correct)

---

## Questions

### Q1. What does the `---` at the beginning of a YAML file indicate?

A) A comment
B) Document start marker
C) Required header for Ansible
D) Version declaration

<details>
<summary>Answer</summary>

**B) Document start marker**

The `---` is a YAML document start marker. While optional, it's recommended as a best practice in Ansible playbooks. It indicates the beginning of a YAML document.

Note: `...` (three dots) marks the end of a document.
</details>

---

### Q2. What is wrong with this YAML?

```yaml
tasks:
  - name: Install package
	package:
      name: nginx
```

A) Missing `state` parameter
B) Using tabs instead of spaces for indentation
C) `package` should be on the same line as `-`
D) Missing `become: yes`

<details>
<summary>Answer</summary>

**B) Using tabs instead of spaces for indentation**

YAML requires spaces for indentation, never tabs. The line with `package:` appears to use a tab character, which will cause a syntax error.

Always configure your editor to:
- Use spaces instead of tabs
- Set indentation to 2 spaces
- Show whitespace characters
</details>

---

### Q3. In a playbook, what does `become: yes` do?

A) Enables verbose output
B) Runs tasks with privilege escalation (sudo)
C) Allows the playbook to modify system files
D) Enables fact gathering

<details>
<summary>Answer</summary>

**B) Runs tasks with privilege escalation (sudo)**

`become: yes` tells Ansible to use privilege escalation (sudo by default) when running tasks. Required for:
- Installing packages
- Managing services
- Modifying system files
- Creating system users

Related options:
- `become_user`: Which user to become (default: root)
- `become_method`: How to escalate (default: sudo)
</details>

---

### Q4. Which command runs a playbook in "check mode" (dry run)?

A) `ansible-playbook playbook.yml --dry-run`
B) `ansible-playbook playbook.yml --check`
C) `ansible-playbook playbook.yml --test`
D) `ansible-playbook playbook.yml --preview`

<details>
<summary>Answer</summary>

**B) `ansible-playbook playbook.yml --check`**

Check mode (`--check`) simulates the playbook run without making changes. It shows what WOULD change.

Additional useful flags:
- `--diff`: Show differences in file changes
- `--check --diff`: Preview changes with file diffs
- `--syntax-check`: Only check YAML syntax
</details>

---

### Q5. What is a "play" in Ansible terminology?

A) A single task execution
B) A mapping of hosts to a list of tasks
C) A collection of playbooks
D) An inventory group

<details>
<summary>Answer</summary>

**B) A mapping of hosts to a list of tasks**

A play defines:
- Which hosts to target (`hosts:`)
- What tasks to run on them (`tasks:`)
- How to connect and execute (`become:`, `vars:`, etc.)

A playbook can contain multiple plays, each targeting different hosts with different tasks.
</details>

---

### Q6. What is the result of running this playbook twice?

```yaml
- hosts: localhost
  tasks:
    - name: Create file
      file:
        path: /tmp/test.txt
        state: touch
```

A) Error on second run (file exists)
B) File is overwritten
C) File timestamp is updated both times
D) Second run is skipped (file exists)

<details>
<summary>Answer</summary>

**C) File timestamp is updated both times**

The `state: touch` always updates the file's modification timestamp, so:
- First run: Creates file, reports `changed`
- Second run: Updates timestamp, reports `changed`

This is NOT idempotent behavior. For true idempotency, use `state: file` (doesn't create) or check if file exists first.
</details>

---

### Q7. How do you limit playbook execution to specific hosts?

A) `ansible-playbook playbook.yml --hosts webservers`
B) `ansible-playbook playbook.yml --limit webservers`
C) `ansible-playbook playbook.yml --target webservers`
D) `ansible-playbook playbook.yml --only webservers`

<details>
<summary>Answer</summary>

**B) `ansible-playbook playbook.yml --limit webservers`**

The `--limit` flag restricts execution to matching hosts/groups.

Examples:
- `--limit webservers` - Only webservers group
- `--limit web1,web2` - Only specific hosts
- `--limit 'webservers:&production'` - Intersection pattern
- `--limit @failed_hosts.txt` - Hosts from file
</details>

---

### Q8. What does "idempotent" mean for an Ansible task?

A) The task runs faster each time
B) The task produces the same result regardless of how many times it runs
C) The task can be undone
D) The task runs on all hosts simultaneously

<details>
<summary>Answer</summary>

**B) The task produces the same result regardless of how many times it runs**

An idempotent task:
- Checks current state before acting
- Only makes changes if needed
- Is safe to run multiple times
- Reports `ok` when no change needed, `changed` when state was modified

Example: `package: name=nginx state=present` is idempotent (checks if installed first).
</details>

---

### Q9. What is the correct syntax for using variables in a playbook task?

A) `dest: /home/${username}/file`
B) `dest: /home/{{ username }}/file`
C) `dest: /home/%{username}/file`
D) `dest: /home/[username]/file`

<details>
<summary>Answer</summary>

**B) `dest: /home/{{ username }}/file`**

Ansible uses Jinja2 templating syntax:
- Variables: `{{ variable_name }}`
- Filters: `{{ variable | filter }}`
- Conditionals: `{% if condition %}...{% endif %}`

Important: When a value starts with `{{`, quote the entire string:
```yaml
dest: "{{ username }}"  # Correct
dest: {{ username }}    # Will cause YAML error
```
</details>

---

### Q10. What happens when a task fails in a playbook?

A) All subsequent tasks continue
B) Playbook stops for that host, continues on others
C) Playbook stops completely for all hosts
D) The task is automatically retried 3 times

<details>
<summary>Answer</summary>

**B) Playbook stops for that host, continues on others**

Default behavior on task failure:
- The failing host is removed from the play
- Remaining hosts continue
- Subsequent tasks don't run on the failed host

To change this behavior:
- `ignore_errors: yes` - Continue on failure
- `any_errors_fatal: true` - Stop all hosts on any failure
- `block/rescue/always` - Error handling structure
</details>

---

## Scoring

| Score | Result |
|-------|--------|
| 10/10 | Excellent! Ready for Chapter 5 |
| 8-9/10 | Good understanding, review missed topics |
| 6-7/10 | Review Chapter 4 before proceeding |
| Below 6 | Re-read Chapter 4 and redo exercises |

---

## Review Topics

If you missed questions, review these sections:

- **Q1-2**: [YAML Syntax Basics](../04-playbooks-basics.md#-yaml-syntax-basics)
- **Q3**: [Playbook Structure](../04-playbooks-basics.md#-playbook-structure)
- **Q4**: [Running Playbooks](../04-playbooks-basics.md#-running-playbooks)
- **Q5**: [Understanding Playbook Components](../04-playbooks-basics.md#-understanding-playbook-components)
- **Q6, Q8**: [Understanding Idempotency](../04-playbooks-basics.md#-understanding-idempotency)
- **Q7**: [Running Playbooks](../04-playbooks-basics.md#basic-execution)
- **Q9**: [Variables in Playbooks](../04-playbooks-basics.md#-practical-playbook-examples)
- **Q10**: [Troubleshooting](../04-playbooks-basics.md#-troubleshooting)
