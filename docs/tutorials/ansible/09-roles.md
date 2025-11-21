# Chapter 9: Roles - Organizing Reusable Automation

Roles are Ansible's way of organizing and reusing automation code. Think of them as pre-packaged automation modules that can be shared and reused across projects. This chapter teaches you to create, use, and share roles effectively.

## 🎯 Learning Objectives

By the end of this chapter, you will:

- Understand what roles are and why they're important
- Create your own custom roles
- Use roles from Ansible Galaxy
- Organize roles with proper structure
- Pass variables to roles
- Handle role dependencies

## 📖 What are Roles?

A **role** is a collection of tasks, variables, files, templates, and handlers organized in a standardized directory structure. Roles make your automation:

- **Reusable**: Use the same role across multiple playbooks
- **Shareable**: Share roles with others via Ansible Galaxy
- **Organized**: Keep related files together
- **Testable**: Test roles independently
- **Maintainable**: Easier to update and debug

## 🏗️ Role Directory Structure

A complete role has this structure:

```text
roles/
└── rolename/
    ├── README.md           # Documentation
    ├── defaults/
    │   └── main.yml       # Default variables (lowest precedence)
    ├── vars/
    │   └── main.yml       # Role variables (higher precedence)
    ├── tasks/
    │   └── main.yml       # Main task list
    ├── handlers/
    │   └── main.yml       # Handler definitions
    ├── templates/
    │   └── config.j2      # Jinja2 templates
    ├── files/
    │   └── script.sh      # Static files to copy
    ├── meta/
    │   └── main.yml       # Role metadata and dependencies
    └── tests/
        ├── inventory      # Test inventory
        └── test.yml       # Test playbook
```

**Not all directories are required** - only create what you need!

## 🎬 Creating Your First Role

### Using ansible-galaxy

The easiest way to create a role:

```bash
# Create role skeleton
ansible-galaxy init my_role

# Creates this structure:
# my_role/
# ├── README.md
# ├── defaults/
# ├── files/
# ├── handlers/
# ├── meta/
# ├── tasks/
# ├── templates/
# ├── tests/
# └── vars/
```

### Manual Role Creation

Create a simple webserver role:

```bash
mkdir -p roles/webserver/{tasks,handlers,templates,files,vars,defaults}
```

**roles/webserver/tasks/main.yml**:

```yaml
---
# Main task file for webserver role
- name: Install nginx
  package:
    name: nginx
    state: present

- name: Copy nginx configuration
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: '0644'
  notify: Reload nginx

- name: Ensure nginx is running
  service:
    name: nginx
    state: started
    enabled: yes
```

**roles/webserver/handlers/main.yml**:

```yaml
---
# Handlers for webserver role
- name: Reload nginx
  service:
    name: nginx
    state: reloaded

- name: Restart nginx
  service:
    name: nginx
    state: restarted
```

**roles/webserver/defaults/main.yml**:

```yaml
---
# Default variables for webserver role
webserver_port: 80
webserver_user: www-data
webserver_worker_processes: auto
webserver_worker_connections: 1024
```

**roles/webserver/templates/nginx.conf.j2**:

```jinja2
user {{ webserver_user }};
worker_processes {{ webserver_worker_processes }};

events {
    worker_connections {{ webserver_worker_connections }};
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    server {
        listen {{ webserver_port }};
        server_name _;

        location / {
            root /var/www/html;
            index index.html;
        }
    }
}
```

## 📝 Using Roles in Playbooks

### Basic Usage

```yaml
---
- name: Configure web servers
  hosts: webservers
  become: yes

  roles:
    - webserver
```

### With Variables

```yaml
---
- name: Configure web servers
  hosts: webservers
  become: yes

  roles:
    - role: webserver
      vars:
        webserver_port: 8080
        webserver_worker_processes: 4
```

### Multiple Roles

```yaml
---
- name: Configure application stack
  hosts: appservers
  become: yes

  roles:
    - common
    - firewall
    - webserver
    - php
    - mysql
```

### Mixing Roles with Tasks

```yaml
---
- name: Setup server
  hosts: all
  become: yes

  pre_tasks:
    - name: Update package cache
      apt:
        update_cache: yes

  roles:
    - common
    - webserver

  tasks:
    - name: Deploy application
      copy:
        src: app/
        dest: /var/www/html/

  post_tasks:
    - name: Verify deployment
      uri:
        url: http://localhost
        status_code: 200
```

## 🔗 Role Dependencies

Roles can depend on other roles using `meta/main.yml`:

**roles/wordpress/meta/main.yml**:

```yaml
---
dependencies:
  - role: common

  - role: mysql
    vars:
      mysql_databases:
        - name: wordpress
      mysql_users:
        - name: wpuser
          password: "{{ wp_db_password }}"
          priv: "wordpress.*:ALL"

  - role: php
    vars:
      php_packages:
        - php-mysql
        - php-gd
        - php-xml

  - role: nginx
    vars:
      nginx_sites:
        - name: wordpress
          template: wordpress.conf.j2
```

When you use the `wordpress` role, all dependencies are automatically applied first.

## 🎯 Role Variables

### Variable Precedence (Low to High)

1. **defaults/main.yml** - Default values (easily overridden)
2. **vars/main.yml** - Role vars (harder to override)
3. **Playbook vars** - Variables in playbook
4. **Extra vars** - Command line `-e`

### Best Practices

**Use defaults/** for:

- User-configurable options
- Values you expect users to change
- Sensible default settings

```yaml
# roles/app/defaults/main.yml
---
app_port: 8080
app_workers: 2
app_log_level: info
```

**Use vars/** for:

- Internal role logic
- Values that shouldn't change
- Constants

```yaml
# roles/app/vars/main.yml
---
app_config_dir: /etc/myapp
app_data_dir: /var/lib/myapp
app_required_packages:
  - python3
  - python3-pip
```

## 📦 Ansible Galaxy

[Ansible Galaxy](https://galaxy.ansible.com/) is a repository of community roles.

### Finding Roles

```bash
# Search for roles
ansible-galaxy search nginx

# Get role info
ansible-galaxy info geerlingguy.nginx
```

### Installing Roles

```bash
# Install a role
ansible-galaxy install geerlingguy.nginx

# Install to specific directory
ansible-galaxy install geerlingguy.nginx -p ./roles

# Install specific version
ansible-galaxy install geerlingguy.nginx,3.1.4
```

### Using requirements.yml

**requirements.yml**:

```yaml
---
# From Galaxy
- name: geerlingguy.nginx
  version: 3.1.4

- name: geerlingguy.mysql
  version: 4.3.3

# From Git repository
- src: https://github.com/user/role.git
  name: custom_role
  version: main

# From local path
- src: ./local_roles/my_role
  name: my_role
```

Install all roles:

```bash
ansible-galaxy install -r requirements.yml
```

## 🎨 Advanced Role Patterns

### Include Tasks Conditionally

**roles/app/tasks/main.yml**:

```yaml
---
- name: Include OS-specific tasks
  include_tasks: "{{ ansible_os_family }}.yml"

- name: Include environment-specific config
  include_tasks: "{{ env }}.yml"
  when: env is defined
```

**roles/app/tasks/Debian.yml**:

```yaml
---
- name: Install packages (Debian)
  apt:
    name: "{{ app_packages }}"
    state: present
```

**roles/app/tasks/RedHat.yml**:

```yaml
---
- name: Install packages (RedHat)
  yum:
    name: "{{ app_packages }}"
    state: present
```

### Parameterized Roles

Make roles highly configurable:

```yaml
---
- name: Deploy multiple applications
  hosts: appservers

  roles:
    - role: webapp
      vars:
        app_name: frontend
        app_port: 3000
        app_repo: https://github.com/company/frontend.git

    - role: webapp
      vars:
        app_name: backend
        app_port: 8000
        app_repo: https://github.com/company/backend.git
```

### Role Tagging

```yaml
# roles/webserver/tasks/main.yml
---
- name: Install packages
  package:
    name: nginx
  tags:
    - install
    - packages

- name: Configure nginx
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
  tags:
    - config

- name: Start service
  service:
    name: nginx
    state: started
  tags:
    - service
```

Use with:

```bash
# Only run config tasks
ansible-playbook site.yml --tags config

# Skip package installation
ansible-playbook site.yml --skip-tags install
```

## 🛠️ Exercises

### Exercise 9.1: Create a Basic Role

**Task**: Create a role that sets up a basic web server.

**Requirements**:

1. Create role named `simple_web`
2. Install nginx
3. Create custom index.html
4. Start and enable nginx
5. Include a handler to restart nginx

**Solution**:

```bash
# Create role structure
ansible-galaxy init roles/simple_web

# Edit roles/simple_web/tasks/main.yml
```

```yaml
---
- name: Install nginx
  package:
    name: nginx
    state: present

- name: Deploy index page
  copy:
    content: |
      <h1>Hello from {{ inventory_hostname }}</h1>
      <p>Managed by Ansible role: simple_web</p>
    dest: /var/www/html/index.html
  notify: Restart nginx

- name: Ensure nginx is running
  service:
    name: nginx
    state: started
    enabled: yes
```

**Test playbook**:

```yaml
---
- name: Test simple_web role
  hosts: localhost
  connection: local
  become: yes

  roles:
    - simple_web
```

---

### Exercise 9.2: Role with Variables

**Task**: Enhance the simple_web role with variables.

**Add to roles/simple_web/defaults/main.yml**:

```yaml
---
simple_web_port: 80
simple_web_title: "Welcome"
simple_web_message: "This server is managed by Ansible"
```

**Update tasks to use variables**:

```yaml
---
- name: Deploy index page
  copy:
    content: |
      <h1>{{ simple_web_title }}</h1>
      <p>{{ simple_web_message }}</p>
      <p>Server: {{ inventory_hostname }}</p>
    dest: /var/www/html/index.html
  notify: Restart nginx
```

**Use with custom variables**:

```yaml
---
- name: Deploy custom site
  hosts: localhost
  become: yes

  roles:
    - role: simple_web
      vars:
        simple_web_title: "My Custom Site"
        simple_web_message: "Welcome to my awesome website!"
```

---

### Exercise 9.3: Role Dependencies

**Task**: Create a WordPress role with dependencies.

**roles/wordpress/meta/main.yml**:

```yaml
---
dependencies:
  - role: nginx
  - role: php
  - role: mysql
```

**roles/wordpress/defaults/main.yml**:

```yaml
---
wp_version: "6.3.1"
wp_db_name: wordpress
wp_db_user: wpuser
wp_db_password: changeme
wp_install_dir: /var/www/wordpress
```

---

### Exercise 9.4: Use Galaxy Role

**Task**: Install and use a community role from Galaxy.

```bash
# Install role
ansible-galaxy install geerlingguy.docker

# Create playbook
```

```yaml
---
- name: Install Docker using Galaxy role
  hosts: localhost
  become: yes

  roles:
    - role: geerlingguy.docker
      vars:
        docker_users:
          - "{{ ansible_user }}"
```

---

## 🔧 Troubleshooting

### Problem: Role not found

**Error**: "the role 'rolename' was not found"

**Solutions**:

```bash
# Check role path
ansible-config dump | grep ROLES_PATH

# Verify role exists
ls -la roles/rolename

# Specify role path in playbook
ansible-playbook -i inventory playbook.yml --roles-path=./roles
```

### Problem: Variables not working

**Check precedence**:

```bash
# Debug variables
ansible-playbook playbook.yml -e "debug_vars=true" -v

# Check what variables are set
- debug:
    var: hostvars[inventory_hostname]
```

### Problem: Dependency issues

**Ensure proper order**:

```yaml
# meta/main.yml must be valid YAML
# Dependencies run before role tasks
# Check for circular dependencies
```

## 📖 Key Takeaways

✅ Roles organize automation into reusable units
✅ Use ansible-galaxy to create role skeleton
✅ defaults/ for user-configurable variables
✅ vars/ for internal role variables
✅ meta/main.yml defines dependencies
✅ Ansible Galaxy provides thousands of ready-to-use roles
✅ requirements.yml manages role dependencies
✅ Roles make playbooks cleaner and more maintainable

## 🎓 What's Next?

Now that you understand roles, you're ready to secure your automation with Ansible Vault.

**Next Chapter**: [Chapter 10: Ansible Vault](10-vault.md)

In the next chapter, you'll learn:
- Encrypting sensitive data
- Managing secrets securely
- Vault best practices
- Working with multiple vaults

---

**Remember**: Good roles are focused, reusable, and well-documented!
