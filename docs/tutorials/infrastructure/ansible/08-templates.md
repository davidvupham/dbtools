# Chapter 8: Templates

Templates allow you to create dynamic configuration files using Jinja2 templating. This chapter covers template syntax, filters, and best practices for managing configuration files.

## Learning Objectives

By the end of this chapter, you will:

- Understand Jinja2 template syntax
- Create dynamic configuration files
- Use filters to transform data
- Implement conditionals and loops in templates
- Apply template best practices

## Why Use Templates?

Templates solve common configuration challenges:
- Generate host-specific configuration files
- Create dynamic content based on variables and facts
- Maintain consistent configuration across environments
- Reduce duplication in configuration management

## Basic Template Syntax

### Variable Substitution

```jinja2
# Simple variable
ServerName {{ server_name }}

# Fact usage
Hostname {{ ansible_hostname }}
IP Address {{ ansible_default_ipv4.address }}

# Variable with default
Port {{ http_port | default(80) }}
```

### The Template Module

```yaml
- name: Deploy configuration file
  template:
    src: nginx.conf.j2       # Template in templates/ directory
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: '0644'
    backup: yes              # Create backup before overwriting
  notify: Reload nginx
```

## Jinja2 Syntax Elements

### Variables: `{{ }}`

```jinja2
# Variables
User {{ username }}
Home {{ home_dir }}

# Nested variables
Database: {{ database.name }}
Host: {{ database.host }}

# List access
First Server: {{ servers[0] }}
```

### Statements: `{% %}`

```jinja2
# Conditionals
{% if enable_ssl %}
SSLEngine On
{% endif %}

# Loops
{% for server in backend_servers %}
server {{ server.name }} {{ server.ip }}:{{ server.port }};
{% endfor %}
```

### Comments: `{# #}`

```jinja2
{# This comment won't appear in output #}
# This comment WILL appear in output
```

## Conditionals in Templates

### Basic If/Else

```jinja2
{% if ansible_os_family == "RedHat" %}
# RedHat-specific configuration
PackageManager=dnf
{% elif ansible_os_family == "Debian" %}
# Debian-specific configuration
PackageManager=apt
{% else %}
# Default configuration
PackageManager=unknown
{% endif %}
```

### Testing Variables

```jinja2
{% if database_host is defined %}
DB_HOST={{ database_host }}
{% else %}
DB_HOST=localhost
{% endif %}

{% if users is defined and users | length > 0 %}
# Users configured
{% for user in users %}
{{ user }}
{% endfor %}
{% endif %}

{% if enable_feature | default(false) %}
FEATURE_ENABLED=true
{% endif %}
```

### Complex Conditions

```jinja2
{% if (ansible_memtotal_mb > 4096) and (enable_caching | default(true)) %}
CacheSize=1024
CacheEnabled=true
{% elif ansible_memtotal_mb > 2048 %}
CacheSize=512
CacheEnabled=true
{% else %}
CacheEnabled=false
{% endif %}
```

## Loops in Templates

### Basic Loop

```jinja2
# Backend servers
{% for server in backend_servers %}
server {{ server }};
{% endfor %}
```

### Loop with Index

```jinja2
{% for host in groups['webservers'] %}
# Server {{ loop.index }} of {{ loop.length }}
{{ hostvars[host]['ansible_host'] }} {{ host }}
{% endfor %}
```

### Loop Variables

| Variable | Description |
|----------|-------------|
| `loop.index` | Current iteration (1-indexed) |
| `loop.index0` | Current iteration (0-indexed) |
| `loop.first` | True if first iteration |
| `loop.last` | True if last iteration |
| `loop.length` | Total number of items |

### Loop with Conditionals

```jinja2
{% for user in users %}
{% if user.active %}
{{ user.name }}:{{ user.uid }}:{{ user.shell }}
{% endif %}
{% endfor %}

# Combining with else for empty lists
{% for item in items %}
{{ item }}
{% else %}
No items configured
{% endfor %}
```

### Nested Loops

```jinja2
{% for vhost in virtual_hosts %}
<VirtualHost *:{{ vhost.port }}>
    ServerName {{ vhost.name }}
    {% for alias in vhost.aliases | default([]) %}
    ServerAlias {{ alias }}
    {% endfor %}
</VirtualHost>
{% endfor %}
```

## Filters

Filters transform data in templates.

### String Filters

```jinja2
# Case conversion
{{ username | upper }}           # JOHN
{{ hostname | lower }}           # webserver
{{ title | capitalize }}         # Hello world
{{ name | title }}               # Hello World

# String manipulation
{{ path | basename }}            # file.txt from /path/to/file.txt
{{ path | dirname }}             # /path/to from /path/to/file.txt
{{ text | trim }}                # Remove whitespace
{{ text | replace("old", "new") }}
```

### List Filters

```jinja2
# Join list elements
{{ servers | join(", ") }}       # server1, server2, server3

# List operations
{{ items | first }}              # First element
{{ items | last }}               # Last element
{{ items | length }}             # Number of elements
{{ items | sort }}               # Sorted list
{{ items | unique }}             # Remove duplicates
{{ items | reverse | list }}     # Reversed list
```

### Default Values

```jinja2
# Provide default if undefined
{{ port | default(8080) }}

# Default if empty or false
{{ value | default("none", true) }}

# Omit parameter if undefined
{% if optional_param is defined %}
param={{ optional_param }}
{% endif %}
```

### Numeric Filters

```jinja2
{{ value | int }}                # Convert to integer
{{ value | float }}              # Convert to float
{{ value | abs }}                # Absolute value
{{ value | round(2) }}           # Round to 2 decimal places
```

### Data Structure Filters

```jinja2
# Convert to JSON/YAML
{{ data | to_json }}
{{ data | to_nice_json(indent=2) }}
{{ data | to_yaml }}

# Parse JSON/YAML
{{ json_string | from_json }}

# Dictionary operations
{{ dict | dict2items }}          # Convert to list of {key, value}
{{ list | items2dict }}          # Convert back to dict
```

### Password and Hash Filters

```jinja2
# Password hashing
{{ password | password_hash('sha512') }}

# Base64
{{ string | b64encode }}
{{ encoded | b64decode }}

# MD5/SHA
{{ value | hash('md5') }}
{{ value | hash('sha256') }}
```

## Practical Examples

### Example 1: Nginx Configuration

`templates/nginx.conf.j2`:
```jinja2
# Nginx Configuration - Managed by Ansible
# Generated: {{ ansible_date_time.iso8601 }}

user {{ nginx_user | default('nginx') }};
worker_processes {{ ansible_processor_vcpus }};
error_log /var/log/nginx/error.log;

events {
    worker_connections {{ nginx_worker_connections | default(1024) }};
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

{% if nginx_gzip_enabled | default(true) %}
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
{% endif %}

{% for vhost in nginx_vhosts | default([]) %}
    server {
        listen {{ vhost.port | default(80) }};
        server_name {{ vhost.server_name }};
        root {{ vhost.document_root }};

{% if vhost.ssl | default(false) %}
        listen 443 ssl;
        ssl_certificate {{ vhost.ssl_cert }};
        ssl_certificate_key {{ vhost.ssl_key }};
{% endif %}

{% for location in vhost.locations | default([]) %}
        location {{ location.path }} {
{% if location.proxy_pass is defined %}
            proxy_pass {{ location.proxy_pass }};
{% else %}
            try_files $uri $uri/ =404;
{% endif %}
        }
{% endfor %}
    }

{% endfor %}
}
```

### Example 2: SSH Configuration

`templates/sshd_config.j2`:
```jinja2
# SSH Server Configuration
# Managed by Ansible - Do not edit manually

Port {{ ssh_port | default(22) }}
ListenAddress {{ ssh_listen_address | default('0.0.0.0') }}

Protocol 2
HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_ecdsa_key
HostKey /etc/ssh/ssh_host_ed25519_key

# Authentication
PermitRootLogin {{ 'yes' if ssh_permit_root | default(false) else 'no' }}
PasswordAuthentication {{ 'yes' if ssh_password_auth | default(false) else 'no' }}
PubkeyAuthentication yes
MaxAuthTries {{ ssh_max_auth_tries | default(3) }}

{% if ssh_allowed_users is defined and ssh_allowed_users | length > 0 %}
AllowUsers {{ ssh_allowed_users | join(' ') }}
{% endif %}

{% if ssh_allowed_groups is defined and ssh_allowed_groups | length > 0 %}
AllowGroups {{ ssh_allowed_groups | join(' ') }}
{% endif %}

# Security
X11Forwarding {{ 'yes' if ssh_x11_forwarding | default(false) else 'no' }}
UseDNS no
Banner {{ ssh_banner | default('/etc/issue.net') }}
```

### Example 3: Hosts File Generation

`templates/hosts.j2`:
```jinja2
# /etc/hosts - Managed by Ansible
# Last updated: {{ ansible_date_time.date }}

127.0.0.1   localhost localhost.localdomain
::1         localhost localhost.localdomain

# Ansible managed hosts
{% for host in groups['all'] | sort %}
{% if hostvars[host]['ansible_host'] is defined %}
{{ hostvars[host]['ansible_host'] }}    {{ host.split('.')[0] }}    {{ host }}
{% elif hostvars[host]['ansible_default_ipv4'] is defined %}
{{ hostvars[host]['ansible_default_ipv4']['address'] }}    {{ host.split('.')[0] }}    {{ host }}
{% endif %}
{% endfor %}

{% if extra_hosts is defined %}
# Additional hosts
{% for entry in extra_hosts %}
{{ entry.ip }}    {{ entry.names | join(' ') }}
{% endfor %}
{% endif %}
```

### Example 4: Application Configuration

`templates/app_config.yml.j2`:
```jinja2
# Application Configuration
# Environment: {{ app_environment | default('development') }}

application:
  name: {{ app_name }}
  version: {{ app_version }}
  debug: {{ app_debug | default(false) | lower }}

server:
  host: {{ app_host | default('0.0.0.0') }}
  port: {{ app_port | default(8080) }}
{% if app_workers is defined %}
  workers: {{ app_workers }}
{% else %}
  workers: {{ ansible_processor_vcpus }}
{% endif %}

database:
  driver: {{ db_driver | default('postgresql') }}
  host: {{ db_host }}
  port: {{ db_port | default(5432) }}
  name: {{ db_name }}
  user: {{ db_user }}
  # Password should be in environment variable DB_PASSWORD

{% if redis_host is defined %}
cache:
  driver: redis
  host: {{ redis_host }}
  port: {{ redis_port | default(6379) }}
{% endif %}

logging:
  level: {{ log_level | default('INFO') }}
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
{% if log_file is defined %}
  file: {{ log_file }}
{% endif %}
```

## Template Best Practices

### 1. Add Header Comments

```jinja2
{#
  Template: nginx.conf.j2
  Purpose: Main Nginx configuration
  Variables required:
    - nginx_user
    - nginx_vhosts (list)
#}
# Managed by Ansible - DO NOT EDIT MANUALLY
# Last generated: {{ ansible_date_time.iso8601 }}
# Source: {{ template_path | default('unknown') }}
```

### 2. Use Defaults for Optional Variables

```jinja2
Port {{ http_port | default(80) }}
MaxConnections {{ max_conn | default(1000) }}
```

### 3. Handle Empty Lists

```jinja2
{% if servers is defined and servers | length > 0 %}
{% for server in servers %}
{{ server }}
{% endfor %}
{% else %}
# No servers configured
{% endif %}
```

### 4. Validate Before Using

```yaml
- name: Validate template syntax
  template:
    src: config.j2
    dest: /tmp/config.test
    validate: '/usr/bin/nginx -t -c %s'
```

## Exercises

### Exercise 8.1: Create Virtual Host Template

Create a template for Apache virtual hosts that supports multiple domains and SSL.

### Exercise 8.2: Dynamic Hosts File

Create a template that generates `/etc/hosts` from inventory with proper grouping.

### Exercise 8.3: Application Environment File

Create a template for a `.env` file with database, cache, and API configurations.

## Key Takeaways

- Templates use Jinja2 syntax: `{{ }}` for variables, `{% %}` for logic
- Use filters to transform data: `| default()`, `| join()`, `| to_json`
- Conditionals and loops make templates dynamic
- Always use defaults for optional variables
- Add comments to document required variables
- Validate generated configuration files when possible
- Keep templates in a `templates/` directory

## What's Next?

Now that you understand templates, learn about organizing automation with roles.

**Next Chapter**: [Chapter 9: Roles](09-roles.md)
