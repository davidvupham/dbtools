# Chapter 2: Inventory Management

Understanding how to organize and manage your hosts is fundamental to effective Ansible automation. In this chapter, you'll learn everything about inventory files, from basic host definitions to advanced patterns and dynamic inventory.

## 🎯 Learning Objectives

By the end of this chapter, you will:

- Understand inventory file formats (INI and YAML)
- Organize hosts into logical groups
- Use host and group variables
- Work with inventory patterns for targeting hosts
- Understand parent/child group relationships
- Learn about dynamic inventory concepts

## 📖 What is an Inventory?

An **inventory** is a list of servers (managed nodes) that Ansible can work with. Think of it as your automation address book. It tells Ansible:

- Which servers exist
- How to connect to them
- How to group them logically
- What variables apply to each

## 📝 Inventory File Formats

Ansible supports two main formats: INI and YAML.

### INI Format (Classic)

The INI format is simple and readable:

```ini
# Single host
web1.example.com

# Host with connection details
web2.example.com ansible_host=192.168.1.20 ansible_user=admin

# Hosts in a group
[webservers]
web1.example.com
web2.example.com
web3.example.com

[databases]
db1.example.com
db2.example.com
```

### YAML Format (Modern)

YAML format offers more structure:

```yaml
all:
  hosts:
    web1.example.com:
    web2.example.com:
      ansible_host: 192.168.1.20
      ansible_user: admin
  children:
    webservers:
      hosts:
        web1.example.com:
        web2.example.com:
        web3.example.com:
    databases:
      hosts:
        db1.example.com:
        db2.example.com:
```

**Recommendation**: Start with INI format for simplicity. Switch to YAML when you need complex nested structures.

## 🏢 Organizing Hosts into Groups

Groups help you organize hosts by function, location, environment, or any logical division.

### Basic Groups

```ini
[webservers]
web1.example.com
web2.example.com

[appservers]
app1.example.com
app2.example.com

[databases]
db1.example.com
db2.example.com
```

### Using Groups in Commands

```bash
# Target all webservers
ansible webservers -m ping

# Target all databases
ansible databases -m setup -a "filter=ansible_memtotal_mb"

# Target multiple groups
ansible webservers,databases -m ping
```

## 🔢 Host Ranges and Patterns

### Numeric Ranges

Define multiple similar hosts efficiently:

```ini
[webservers]
web[01:10].example.com    # web01, web02, ... web10

[databases]
db-[a:c].example.com      # db-a, db-b, db-c
```

### Alphabetic Ranges

```ini
[servers]
server[a:z].example.com   # servera, serverb, ... serverz
```

### Mixed Patterns

```ini
[cluster]
node-[1:3]-[a:b].example.com
# Results in: node-1-a, node-1-b, node-2-a, node-2-b, node-3-a, node-3-b
```

## 🔗 Connection Variables

Tell Ansible how to connect to each host:

### Common Connection Variables

```ini
[servers]
# SSH with custom port
server1 ansible_host=192.168.1.10 ansible_port=2222

# SSH with specific user
server2 ansible_host=192.168.1.11 ansible_user=admin

# SSH with private key
server3 ansible_host=192.168.1.12 ansible_ssh_private_key_file=~/.ssh/server3_key

# SSH with password (not recommended, use vault!)
server4 ansible_host=192.168.1.13 ansible_ssh_pass=password

# Local connection (no SSH)
localhost ansible_connection=local

# Windows host
winserver ansible_host=192.168.1.20 ansible_connection=winrm ansible_user=Administrator
```

### Complete Connection Example

```ini
[production:children]
webservers
databases

[webservers]
web1 ansible_host=10.0.1.10 ansible_user=webadmin ansible_port=22
web2 ansible_host=10.0.1.11 ansible_user=webadmin ansible_port=22

[databases]
db1 ansible_host=10.0.2.10 ansible_user=dbadmin ansible_ssh_private_key_file=~/.ssh/db_key
```

## 📦 Host and Group Variables

Variables let you customize behavior per host or group.

### Host Variables (Inline)

```ini
[webservers]
web1 ansible_host=10.0.1.10 http_port=8080 max_clients=200
web2 ansible_host=10.0.1.11 http_port=8080 max_clients=300
```

### Group Variables (Inline)

```ini
[webservers:vars]
ansible_user=webadmin
http_port=80
document_root=/var/www/html

[databases:vars]
ansible_user=dbadmin
db_port=5432
```

### Variables in Separate Files

For better organization, use separate variable files:

**Directory Structure**:

```text
inventory/
├── hosts                   # Main inventory file
├── group_vars/
│   ├── all.yml            # Variables for all hosts
│   ├── webservers.yml     # Variables for webservers group
│   └── databases.yml      # Variables for databases group
└── host_vars/
    ├── web1.yml           # Variables specific to web1
    └── db1.yml            # Variables specific to db1
```

**inventory/hosts**:

```ini
[webservers]
web1
web2

[databases]
db1
```

**inventory/group_vars/webservers.yml**:

```yaml
---
ansible_user: webadmin
http_port: 80
max_clients: 200
ssl_enabled: true
```

**inventory/host_vars/web1.yml**:

```yaml
---
ansible_host: 10.0.1.10
http_port: 8080
max_clients: 500
```

## 🌳 Parent and Child Groups

Create hierarchical group structures:

```ini
# Define child groups
[web_production]
web-prod1
web-prod2

[web_staging]
web-stage1

[db_production]
db-prod1

[db_staging]
db-stage1

# Define parent groups
[production:children]
web_production
db_production

[staging:children]
web_staging
db_staging

[webservers:children]
web_production
web_staging

[databases:children]
db_production
db_staging

# Parent group variables
[production:vars]
env=production
backup_enabled=true

[staging:vars]
env=staging
backup_enabled=false
```

**Visual Representation**:

```text
all
├── production
│   ├── web_production
│   │   ├── web-prod1
│   │   └── web-prod2
│   └── db_production
│       └── db-prod1
└── staging
    ├── web_staging
    │   └── web-stage1
    └── db_staging
        └── db-stage1
```

## 🎯 Host Patterns

Host patterns let you target specific hosts or groups:

### Basic Patterns

```bash
# All hosts
ansible all -m ping

# Specific host
ansible web1 -m ping

# Specific group
ansible webservers -m ping

# Multiple groups (OR)
ansible webservers,databases -m ping

# Intersection (AND) - hosts in both groups
ansible webservers:&production -m ping

# Exclusion (NOT) - webservers except those in staging
ansible webservers:!staging -m ping
```

### Advanced Patterns

```bash
# Wildcard patterns
ansible web* -m ping                    # All hosts starting with 'web'
ansible *.example.com -m ping           # All hosts in example.com domain

# Combine multiple patterns
ansible webservers:&production:!web3 -m ping
# Translation: webservers AND production BUT NOT web3

# Regex patterns
ansible ~web[0-9]+ -m ping             # Hosts matching regex

# Indexed selection
ansible webservers[0] -m ping          # First webserver
ansible webservers[-1] -m ping         # Last webserver
ansible webservers[0:2] -m ping        # First three webservers
```

## 📋 Special Groups

Ansible provides built-in groups:

### The 'all' Group

Contains every host:

```bash
ansible all -m ping
```

### The 'ungrouped' Group

Hosts not in any group:

```ini
# These hosts are ungrouped
standalone1
standalone2

[webservers]
web1
web2
```

```bash
ansible ungrouped -m ping
```

## 🔍 Inspecting Your Inventory

### List All Hosts

```bash
# Show all hosts
ansible all --list-hosts

# Show hosts in specific group
ansible webservers --list-hosts

# Show hosts matching pattern
ansible web* --list-hosts
```

### View Inventory Graph

```bash
# Show inventory structure
ansible-inventory --graph

# Output:
# @all:
#   |--@ungrouped:
#   |--@webservers:
#   |  |--web1
#   |  |--web2
#   |--@databases:
#   |  |--db1
```

### Export Inventory

```bash
# Export to JSON
ansible-inventory --list

# Export specific group
ansible-inventory --graph webservers

# Export with variables
ansible-inventory --list --yaml
```

## 🔄 Dynamic Inventory

Dynamic inventory generates the host list programmatically, useful for cloud environments.

### What is Dynamic Inventory?

Instead of a static file, dynamic inventory:
- Queries cloud providers (AWS, Azure, GCP)
- Pulls from CMDBs or databases
- Integrates with orchestration tools
- Updates automatically as infrastructure changes

### Using Dynamic Inventory Scripts

```bash
# Using an inventory script
ansible all -i aws_ec2.py -m ping

# Using an inventory plugin
ansible all -i aws_ec2.yml -m ping
```

### Example: AWS EC2 Dynamic Inventory

**aws_ec2.yml**:

```yaml
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1
  - us-west-2
keyed_groups:
  - key: tags.Environment
    prefix: env
  - key: tags.Role
    prefix: role
hostnames:
  - private-ip-address
```

This automatically discovers EC2 instances and groups them by tags.

### Example: Custom Dynamic Inventory Script

**dynamic_inventory.py**:

```python
#!/usr/bin/env python3
import json

inventory = {
    "webservers": {
        "hosts": ["web1", "web2"],
        "vars": {
            "http_port": 80
        }
    },
    "databases": {
        "hosts": ["db1"],
        "vars": {
            "db_port": 5432
        }
    },
    "_meta": {
        "hostvars": {
            "web1": {"ansible_host": "10.0.1.10"},
            "web2": {"ansible_host": "10.0.1.11"},
            "db1": {"ansible_host": "10.0.2.10"}
        }
    }
}

print(json.dumps(inventory))
```

Make it executable and use it:

```bash
chmod +x dynamic_inventory.py
ansible all -i dynamic_inventory.py -m ping
```

## 🛠️ Exercises

### Exercise 2.1: Create a Basic Inventory

**Task**: Create an inventory with multiple groups.

**Requirements**:
- At least 3 hosts
- At least 2 groups
- Use localhost for testing

**Example Solution**:

```ini
[webservers]
web1 ansible_connection=local
web2 ansible_connection=local

[databases]
db1 ansible_connection=local

[all:vars]
ansible_python_interpreter=/usr/bin/python3
```

**Verify**:

```bash
ansible all --list-hosts
ansible webservers --list-hosts
```

---

### Exercise 2.2: Use Host Ranges

**Task**: Define 10 web servers using range notation.

**Solution**:

```ini
[webservers]
web[01:10] ansible_connection=local

[webservers:vars]
http_port=80
```

**Verify**:

```bash
ansible webservers --list-hosts
```

**Expected Output**: Should show web01 through web10.

---

### Exercise 2.3: Create Parent and Child Groups

**Task**: Organize hosts into a production/staging hierarchy.

**Create this structure**:

```ini
[web_prod]
web-prod1 ansible_connection=local
web-prod2 ansible_connection=local

[web_staging]
web-stage1 ansible_connection=local

[db_prod]
db-prod1 ansible_connection=local

[db_staging]
db-stage1 ansible_connection=local

[production:children]
web_prod
db_prod

[staging:children]
web_staging
db_staging

[allweb:children]
web_prod
web_staging

[production:vars]
environment=production
backup=true

[staging:vars]
environment=staging
backup=false
```

**Verify**:

```bash
ansible-inventory --graph
ansible production --list-hosts
ansible staging --list-hosts
ansible allweb --list-hosts
```

---

### Exercise 2.4: Use Host Patterns

**Task**: Practice targeting hosts with different patterns.

Using the inventory from Exercise 2.3:

```bash
# Target all production hosts
ansible production -m ping

# Target web servers only (both prod and staging)
ansible allweb -m ping

# Target production web servers (intersection)
ansible web_prod:&production -m ping

# Target all hosts except staging
ansible all:!staging -m ping

# Target specific hosts with wildcards
ansible 'web-*' -m ping
```

**Challenge**: Write a pattern that targets all databases except those in staging.

<details>
<summary>Solution</summary>

```bash
ansible 'db_*:!staging' -m ping
# or
ansible 'db_prod' -m ping
```

</details>

---

### Exercise 2.5: Organize Variables

**Task**: Create a proper variable file structure.

**Steps**:

1. Create the directory structure:

```bash
mkdir -p inventory/group_vars inventory/host_vars
```

2. Create **inventory/hosts**:

```ini
[webservers]
web1
web2

[databases]
db1
```

3. Create **inventory/group_vars/all.yml**:

```yaml
---
ansible_connection: local
ansible_python_interpreter: /usr/bin/python3
```

4. Create **inventory/group_vars/webservers.yml**:

```yaml
---
http_port: 80
document_root: /var/www/html
max_clients: 200
```

5. Create **inventory/host_vars/web1.yml**:

```yaml
---
http_port: 8080
max_clients: 500
```

**Verify Variables**:

```bash
# Check what variables are set for web1
ansible-inventory -i inventory/hosts --host web1

# Run a debug playbook
ansible webservers -i inventory/hosts -m debug -a "var=http_port"
```

**Expected Result**: web1 should show `http_port: 8080`, web2 should show `http_port: 80`.

---

### Exercise 2.6: Inventory Inspection

**Task**: Explore your inventory using Ansible commands.

**Commands to Try**:

```bash
# List all groups
ansible-inventory --graph

# List all hosts
ansible all --list-hosts

# Show inventory as JSON
ansible-inventory --list

# Show variables for specific host
ansible-inventory --host web1

# Count hosts in each group
ansible webservers --list-hosts | wc -l
```

**Questions**:
1. How many hosts are in your inventory?
2. What groups exist?
3. What variables are defined for the webservers group?

---

## 🔧 Troubleshooting

### Problem: "No hosts matched"

**Cause**: The pattern doesn't match any hosts in inventory.

**Solution**:

```bash
# Verify hosts exist
ansible-inventory --list-hosts

# Check your pattern
ansible-inventory --graph

# Try a simpler pattern
ansible all --list-hosts
```

### Problem: Variables not applied

**Cause**: Variable precedence or incorrect file names.

**Solution**:

```bash
# Check variable precedence
ansible-inventory --host hostname

# Ensure file names match group/host names exactly
# group_vars/webservers.yml (not webserver.yml)
# host_vars/web1.yml (not web1.yaml or web-1.yml)
```

### Problem: Cannot connect to hosts

**Cause**: Wrong connection settings in inventory.

**Solution**:

```bash
# Test connection manually
ssh user@hostname

# Check inventory connection vars
ansible-inventory --host hostname

# Try with verbose output
ansible hostname -m ping -vvv
```

### Problem: Child group not inheriting variables

**Cause**: Variable files not set up correctly.

**Solution**:

```bash
# Check if group_vars directory exists
ls -la inventory/group_vars/

# Ensure parent group variables are in correct file
# For [production:children], vars go in production.yml, not children.yml
```

## 📖 Key Takeaways

✅ Inventory files define which hosts Ansible manages
✅ Use groups to organize hosts logically
✅ Host patterns provide flexible targeting
✅ Variables can be set at host, group, or global level
✅ Parent/child groups create hierarchies
✅ Dynamic inventory integrates with cloud providers
✅ Use `ansible-inventory` commands to inspect inventory

## 🎓 What's Next?

Now that you understand inventory management, you're ready to execute commands across your infrastructure.

**Next Chapter**: [Chapter 3: Ad-Hoc Commands](03-adhoc-commands.md)

In the next chapter, you'll learn:
- How to execute quick one-off tasks
- Common ad-hoc command patterns
- When to use ad-hoc vs playbooks
- Working with different modules

---

**Practice Makes Perfect!** The more you work with inventory files, the more natural it becomes.
