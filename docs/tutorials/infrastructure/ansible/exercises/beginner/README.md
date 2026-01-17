# Beginner Exercises - Getting Started with Ansible

These exercises are designed for those new to Ansible. Complete them in order to build foundational skills.

## Exercise 1: Your First Playbook

**Time**: 20 minutes
**Chapter**: 1 & 4
**Difficulty**: ⭐ Easy

### Objective

Create a simple playbook that displays system information.

### Requirements

- Create a playbook named `hello_ansible.yml`
- Target localhost
- Use connection: local
- Display a welcome message
- Display the hostname
- Display the current date/time

### Hints

- Use the `debug` module to display messages
- Access facts with `{{ ansible_hostname }}`
- Use `{{ ansible_date_time.iso8601 }}` for date

### Solution

See `solutions/exercise-01-solution.yml`

---

## Exercise 2: File Management

**Time**: 25 minutes
**Chapter**: 3 & 4
**Difficulty**: ⭐ Easy

### Objective

Create a playbook that manages files and directories.

### Requirements

1. Create directory `/tmp/ansible_exercise`
2. Create subdirectories: `logs`, `data`, `config`
3. Create a file `config/app.conf` with sample configuration
4. Set appropriate permissions (directories: 0755, files: 0644)
5. Create a README.txt file explaining the structure

### Hints

- Use `file` module for directories
- Use `copy` module with `content` parameter for file contents
- Use `loop` to create multiple directories efficiently

### Solution

See `solutions/exercise-02-solution.yml`

---

## Exercise 3: Package Installation

**Time**: 30 minutes
**Chapter**: 3 & 4
**Difficulty**: ⭐⭐ Medium

### Objective

Create a playbook that installs and verifies development tools.

### Requirements

1. Install packages: `git`, `vim`, `curl`, `wget`
2. Verify each package is installed
3. Display the version of each tool
4. Ensure all packages are the latest version

### Requirements

- Needs sudo privileges (`become: yes`)
- Should work on Ubuntu/Debian systems

### Hints

- Use `package` module for cross-platform compatibility
- Use `command` module to check versions
- Use `register` to capture output
- Set `changed_when: false` for check commands

### Solution

See `solutions/exercise-03-solution.yml`

---

## Exercise 4: Working with Variables

**Time**: 30 minutes
**Chapter**: 5
**Difficulty**: ⭐⭐ Medium

### Objective

Create a playbook using variables to make it flexible.

### Requirements

1. Define variables for:
   - Application name
   - Installation directory
   - Port number
   - Admin email
2. Create directory structure using variables
3. Generate a config file with variable values
4. Display all configuration at the end

### Hints

- Define variables in `vars:` section
- Reference variables with `{{ variable_name }}`
- Use Jinja2 in templates/content
- Variables can be used in paths and strings

### Solution

See `solutions/exercise-04-solution.yml`

---

## Exercise 5: Loops and Iteration

**Time**: 35 minutes
**Chapter**: 5 & future
**Difficulty**: ⭐⭐ Medium

### Objective

Use loops to perform repetitive tasks efficiently.

### Requirements

1. Create 5 user accounts (user1 through user5)
2. Create home directories for each
3. Install a list of packages
4. Create log files for each service
5. Set permissions on all created files

### Hints

- Use `loop:` with a list
- Use `loop:` with `range()` for numbered items
- Loop variable is accessed with `{{ item }}`
- Can loop over lists defined in variables

### Solution

See `solutions/exercise-05-solution.yml`

---

## Exercise 6: System Report

**Time**: 40 minutes
**Chapter**: 5
**Difficulty**: ⭐⭐⭐ Challenging

### Objective

Create a playbook that generates a comprehensive system report.

### Requirements

1. Gather system facts
2. Create a report file with:
   - Hostname and FQDN
   - Operating system details
   - CPU and memory information
   - Disk space for all mounts
   - Network interfaces and IPs
   - Running services
3. Format the report nicely
4. Save report to `/tmp/system_report_{{ ansible_hostname }}.txt`

### Hints

- Facts are already gathered by default
- Use `setup` module output as reference
- Use `copy` module with `content:` and multi-line string
- Use Jinja2 templates for formatting
- Use `shell` module for custom commands

### Extra Challenge

Make the report output in both text and JSON formats.

### Solution

See `solutions/exercise-06-solution.yml`

---

## 🎯 Completion Checklist

Mark off each exercise as you complete it:

- [ ] Exercise 1: Your First Playbook
- [ ] Exercise 2: File Management
- [ ] Exercise 3: Package Installation
- [ ] Exercise 4: Working with Variables
- [ ] Exercise 5: Loops and Iteration
- [ ] Exercise 6: System Report

## 🏆 Ready for More?

Once you've completed all beginner exercises, move on to:

**Next**: `../intermediate/README.md`

Keep practicing and experimenting with variations!
