# Chapter 9 Quiz: Roles

Test your understanding of Ansible roles, Galaxy, and role organization.

**Time Limit**: 10 minutes
**Passing Score**: 80% (8/10 correct)

---

## Questions

### Q1. What is the purpose of the `defaults/main.yml` file in a role?

A) Required default tasks that always run
B) Variables with the lowest precedence (easily overridden)
C) Default handlers for the role
D) Default templates location

<details>
<summary>Answer</summary>

**B) Variables with the lowest precedence (easily overridden)**

Role directories:
- `defaults/` - Variables meant to be overridden (lowest precedence)
- `vars/` - Internal variables (higher precedence, harder to override)
- `tasks/` - Task definitions
- `handlers/` - Handler definitions
- `templates/` - Jinja2 templates
- `files/` - Static files to copy
- `meta/` - Role metadata and dependencies
</details>

---

### Q2. Which command creates a new role with the standard directory structure?

A) `ansible-role init myrole`
B) `ansible-galaxy role init myrole`
C) `ansible-galaxy init myrole`
D) `ansible create role myrole`

<details>
<summary>Answer</summary>

**C) `ansible-galaxy init myrole`**

Or the newer syntax: `ansible-galaxy role init myrole`

This creates:
```
myrole/
├── README.md
├── defaults/
├── files/
├── handlers/
├── meta/
├── tasks/
├── templates/
├── tests/
└── vars/
```
</details>

---

### Q3. How do you specify role dependencies?

A) In `requirements.yml`
B) In `meta/main.yml` under `dependencies:`
C) In `defaults/dependencies.yml`
D) In the playbook using `depends_on:`

<details>
<summary>Answer</summary>

**B) In `meta/main.yml` under `dependencies:`**

Example:
```yaml
# meta/main.yml
---
dependencies:
  - role: common
  - role: nginx
    vars:
      nginx_port: 8080
```

Dependencies run BEFORE the role's tasks.

Note: `requirements.yml` is for installing roles, not defining dependencies.
</details>

---

### Q4. What is the correct way to pass variables to a role?

A) `- role: webserver webserver_port=8080`
B) `- { role: webserver, vars: { webserver_port: 8080 } }`
C) `- include_role: webserver vars: webserver_port=8080`
D) Both A and B are correct

<details>
<summary>Answer</summary>

**D) Both A and B are correct**

Multiple syntaxes work:

```yaml
# Simple syntax
- role: webserver
  vars:
    webserver_port: 8080

# Classic YAML dictionary
- { role: webserver, vars: { webserver_port: 8080 } }

# include_role (dynamic)
- include_role:
    name: webserver
  vars:
    webserver_port: 8080
```
</details>

---

### Q5. Where does Ansible look for roles by default?

A) `/etc/ansible/roles` only
B) `~/.ansible/roles` only
C) `./roles`, `~/.ansible/roles`, and `/usr/share/ansible/roles`
D) Current directory only

<details>
<summary>Answer</summary>

**C) `./roles`, `~/.ansible/roles`, and `/usr/share/ansible/roles`**

Ansible searches these paths in order:
1. `./roles` (relative to playbook)
2. Paths in `ANSIBLE_ROLES_PATH` environment variable
3. `roles_path` in ansible.cfg
4. `~/.ansible/roles`
5. `/usr/share/ansible/roles`
6. `/etc/ansible/roles`

You can set custom paths with `--roles-path` or in `ansible.cfg`.
</details>

---

### Q6. How do you install roles listed in a requirements.yml file?

A) `ansible-galaxy install requirements.yml`
B) `ansible-galaxy install -r requirements.yml`
C) `ansible-galaxy role import requirements.yml`
D) `ansible-playbook requirements.yml`

<details>
<summary>Answer</summary>

**B) `ansible-galaxy install -r requirements.yml`**

Example requirements.yml:
```yaml
---
- name: geerlingguy.nginx
  version: 3.1.4
- name: geerlingguy.mysql
- src: https://github.com/user/role.git
  name: custom_role
```

Command: `ansible-galaxy install -r requirements.yml -p ./roles/`

The `-p` flag specifies the installation path.
</details>

---

### Q7. What is the difference between `include_role` and `roles:`?

A) No difference, they are aliases
B) `include_role` is dynamic (runtime); `roles:` is static (parse time)
C) `include_role` is deprecated
D) `roles:` only works with Galaxy roles

<details>
<summary>Answer</summary>

**B) `include_role` is dynamic (runtime); `roles:` is static (parse time)**

- **`roles:`** - Evaluated at playbook parse time, runs before tasks
- **`include_role:`** - Evaluated at runtime, can use variables and conditionals

```yaml
# Static (parsed before execution)
roles:
  - webserver

# Dynamic (evaluated at runtime)
tasks:
  - include_role:
      name: "{{ role_name }}"
    when: install_webserver
```
</details>

---

### Q8. How do you reference a file from the role's `files/` directory in a task?

A) `src: files/myfile.txt`
B) `src: {{ role_path }}/files/myfile.txt`
C) `src: myfile.txt`
D) `src: /roles/rolename/files/myfile.txt`

<details>
<summary>Answer</summary>

**C) `src: myfile.txt`**

Ansible automatically looks in the role's `files/` directory for the `copy` module and `templates/` directory for the `template` module.

```yaml
# tasks/main.yml
- name: Copy config file
  copy:
    src: app.conf        # Looks in files/app.conf
    dest: /etc/app.conf

- name: Deploy template
  template:
    src: config.j2       # Looks in templates/config.j2
    dest: /etc/config
```
</details>

---

### Q9. What runs first in a playbook with pre_tasks, roles, and tasks?

A) roles → pre_tasks → tasks
B) tasks → roles → pre_tasks
C) pre_tasks → roles → tasks
D) All run in parallel

<details>
<summary>Answer</summary>

**C) pre_tasks → roles → tasks**

Execution order:
1. `pre_tasks` - Run before anything else
2. `roles` - Run after pre_tasks
3. `tasks` - Run after roles
4. `post_tasks` - Run last

Handlers triggered by each section run at the end of that section.
</details>

---

### Q10. How do you prevent a role from running multiple times if it appears in dependencies?

A) Set `allow_duplicates: false` in meta/main.yml
B) Dependencies never run multiple times by default
C) Use `run_once: true` in the role tasks
D) Set `unique: true` in the role

<details>
<summary>Answer</summary>

**B) Dependencies never run multiple times by default**

By default, Ansible will only run a role once, even if it's listed multiple times as a dependency. This prevents infinite loops and redundant execution.

To allow running the role multiple times:
```yaml
# meta/main.yml
---
allow_duplicates: true
```

This is useful for roles that should run multiple times with different variables.
</details>

---

## Scoring

| Score | Result |
|-------|--------|
| 10/10 | Excellent! Ready for Chapter 10 |
| 8-9/10 | Good understanding, review missed topics |
| 6-7/10 | Review Chapter 9 before proceeding |
| Below 6 | Re-read Chapter 9 and redo exercises |

---

## Review Topics

If you missed questions, review these sections:

- **Q1**: [Role Directory Structure](../09-roles.md#-role-directory-structure)
- **Q2**: [Creating Roles](../09-roles.md#using-ansible-galaxy)
- **Q3**: [Role Dependencies](../09-roles.md#-role-dependencies)
- **Q4**: [Using Roles with Variables](../09-roles.md#with-variables)
- **Q5**: [Role Search Path](../09-roles.md)
- **Q6**: [Ansible Galaxy](../09-roles.md#-ansible-galaxy)
- **Q7**: [include_role vs roles](../09-roles.md#-advanced-role-patterns)
- **Q8**: [Role Files and Templates](../09-roles.md#manual-role-creation)
- **Q9**: [Execution Order](../09-roles.md#mixing-roles-with-tasks)
- **Q10**: [Role Duplicates](../09-roles.md#-role-dependencies)
