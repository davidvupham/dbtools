# Chapter 13 Quiz: Best Practices

Test your understanding of Ansible best practices for production automation.

**Time Limit**: 10 minutes
**Passing Score**: 80% (8/10 correct)

---

## Questions

### Q1. What is the recommended directory structure for an Ansible project?

A) All playbooks and roles in a single directory
B) Separate directories: playbooks/, roles/, group_vars/, host_vars/, inventory/
C) One directory per server being managed
D) No specific structure is recommended

<details>
<summary>Answer</summary>

**B) Separate directories: playbooks/, roles/, group_vars/, host_vars/, inventory/**

Recommended structure:
```
project/
├── ansible.cfg
├── inventory/
│   ├── production
│   └── staging
├── group_vars/
│   ├── all.yml
│   └── webservers.yml
├── host_vars/
├── roles/
│   └── common/
├── playbooks/
│   └── site.yml
└── requirements.yml
```
</details>

---

### Q2. Which ansible.cfg setting improves performance by running tasks in parallel?

A) `parallel = 10`
B) `forks = 10`
C) `workers = 10`
D) `threads = 10`

<details>
<summary>Answer</summary>

**B) `forks = 10`**

The `forks` setting controls how many hosts Ansible manages simultaneously. Default is 5.

Other performance settings:
- `gathering = smart` - Cache facts
- `fact_caching = jsonfile` - Persist fact cache
- `pipelining = True` - Reduce SSH operations
- `strategy = free` - Don't wait for slowest host
</details>

---

### Q3. How should you protect sensitive data like passwords in Ansible?

A) Use environment variables
B) Store in plain text files with restricted permissions
C) Use Ansible Vault to encrypt sensitive files
D) Encode in base64

<details>
<summary>Answer</summary>

**C) Use Ansible Vault to encrypt sensitive files**

Best practices for secrets:
1. Use Ansible Vault to encrypt files containing secrets
2. Use `no_log: true` on tasks that handle secrets
3. Never commit unencrypted secrets to version control
4. Consider external secret management (HashiCorp Vault)

```yaml
- name: Create database user
  mysql_user:
    name: "{{ db_user }}"
    password: "{{ vault_db_password }}"
  no_log: true
```
</details>

---

### Q4. What is the purpose of `no_log: true` on a task?

A) Disables all logging for the playbook
B) Prevents task output from being displayed or logged
C) Skips the task if logging is disabled
D) Writes task output to a separate log file

<details>
<summary>Answer</summary>

**B) Prevents task output from being displayed or logged**

Use `no_log: true` when tasks contain sensitive data:
```yaml
- name: Set user password
  user:
    name: admin
    password: "{{ user_password | password_hash('sha512') }}"
  no_log: true  # Prevents password from appearing in logs
```

This prevents sensitive data from appearing in:
- Console output
- Log files
- Callback plugin output
</details>

---

### Q5. Which naming convention is recommended for Ansible variables?

A) camelCase (myVariable)
B) snake_case (my_variable)
C) PascalCase (MyVariable)
D) kebab-case (my-variable)

<details>
<summary>Answer</summary>

**B) snake_case (my_variable)**

Ansible conventions:
- Variables: `snake_case` (e.g., `http_port`, `app_name`)
- Role names: `snake_case` (e.g., `web_server`)
- Task names: Sentence case, describe the action (e.g., "Install nginx packages")
- File names: `kebab-case` or `snake_case` (e.g., `web-server.yml`)

Avoid starting variables with `ansible_` (reserved for facts).
</details>

---

### Q6. How do you ensure a handler runs even if a task fails?

A) Use `force_handlers: true` in the play
B) Handlers always run regardless of failures
C) Use `always_run: true` on the handler
D) Handlers cannot run after failures

<details>
<summary>Answer</summary>

**A) Use `force_handlers: true` in the play**

```yaml
- hosts: all
  force_handlers: true   # Run handlers even if tasks fail
  tasks:
    - name: Update config
      template:
        src: app.conf.j2
        dest: /etc/app.conf
      notify: Restart app
```

By default, handlers DON'T run if the play fails. `force_handlers: true` overrides this.
</details>

---

### Q7. What is the recommended way to test Ansible roles?

A) Run them directly in production
B) Use Molecule for automated testing
C) Manual testing on a single server
D) Code review only

<details>
<summary>Answer</summary>

**B) Use Molecule for automated testing**

Molecule provides:
- Automated provisioning (Docker, Vagrant, cloud)
- Linting (ansible-lint, yamllint)
- Idempotence testing
- Verification with Testinfra or Goss
- Multiple test scenarios

Testing pyramid for Ansible:
1. Linting (ansible-lint, yamllint)
2. Syntax check (`--syntax-check`)
3. Molecule tests (automated)
4. Integration tests
</details>

---

### Q8. What does `changed_when: false` do on a task?

A) Prevents the task from running
B) Forces the task to always report 'ok' instead of 'changed'
C) Skips the task if the system hasn't changed
D) Disables idempotency checking

<details>
<summary>Answer</summary>

**B) Forces the task to always report 'ok' instead of 'changed'**

Use `changed_when` to control when Ansible reports changes:

```yaml
- name: Check disk space
  command: df -h /
  register: disk_space
  changed_when: false  # Never report changed (read-only command)

- name: Run migration
  command: ./migrate.sh
  register: result
  changed_when: "'Migration complete' in result.stdout"
```

This improves accuracy of playbook reporting.
</details>

---

### Q9. What is the benefit of using tags in playbooks?

A) Tags improve performance
B) Tags allow running specific subsets of tasks
C) Tags encrypt sensitive tasks
D) Tags are required for roles

<details>
<summary>Answer</summary>

**B) Tags allow running specific subsets of tasks**

```yaml
tasks:
  - name: Install packages
    package:
      name: nginx
    tags: [install, packages]

  - name: Configure nginx
    template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    tags: [config]
```

Usage:
- `--tags install` - Only run tasks with 'install' tag
- `--skip-tags config` - Run all except 'config' tagged tasks
- `--tags all` - Run all tasks (default)
</details>

---

### Q10. Which strategy allows faster hosts to proceed without waiting for slower ones?

A) `strategy: parallel`
B) `strategy: free`
C) `strategy: async`
D) `strategy: independent`

<details>
<summary>Answer</summary>

**B) `strategy: free`**

Ansible strategies:
- `linear` (default): All hosts complete each task before moving to next
- `free`: Hosts proceed independently, faster hosts don't wait
- `debug`: Interactive debugging mode

```yaml
- hosts: all
  strategy: free   # Hosts proceed at their own pace
  tasks:
    - name: Long running task
      command: /usr/local/bin/slow_script.sh
```

Use `free` strategy when tasks are independent and order doesn't matter.
</details>

---

## Scoring

| Score | Result |
|-------|--------|
| 10/10 | Excellent! You've mastered Ansible best practices |
| 8-9/10 | Good understanding, review missed topics |
| 6-7/10 | Review Chapter 13 before proceeding |
| Below 6 | Re-read Chapter 13 and redo exercises |

---

## Review Topics

If you missed questions, review these sections:

- **Q1**: [Project Organization](../13-best-practices.md)
- **Q2**: [Performance Optimization](../13-best-practices.md)
- **Q3-4**: [Security Practices](../13-best-practices.md)
- **Q5**: [Naming Conventions](../13-best-practices.md)
- **Q6**: [Handler Best Practices](../13-best-practices.md)
- **Q7**: [Testing and Validation](../13-best-practices.md)
- **Q8**: [changed_when/failed_when](../13-best-practices.md)
- **Q9**: [Using Tags](../13-best-practices.md)
- **Q10**: [Strategies](../13-best-practices.md)
