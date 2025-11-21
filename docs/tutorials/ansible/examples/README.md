# Ansible Tutorial Examples

This directory contains working examples for each chapter of the Ansible tutorial. Each example is fully functional and demonstrates the concepts covered in its corresponding chapter.

## 📁 Directory Structure

```text
examples/
├── chapter01-getting-started/
│   ├── first_playbook.yml
│   ├── inventory
│   └── README.md
├── chapter02-inventory/
│   ├── inventory-ini/
│   ├── inventory-yaml/
│   ├── group_vars/
│   └── README.md
├── chapter03-adhoc/
│   ├── commands.sh
│   └── README.md
├── chapter04-playbooks/
│   ├── basic_playbook.yml
│   ├── webserver.yml
│   ├── users.yml
│   └── README.md
├── chapter05-variables/
│   ├── variables_playbook.yml
│   ├── vars/
│   └── README.md
└── complete-examples/
    ├── lamp-stack/
    ├── docker-deployment/
    └── monitoring-setup/
```

## 🚀 How to Use These Examples

1. **Navigate to a chapter directory**:
   ```bash
   cd chapter04-playbooks
   ```

2. **Read the README** for that chapter to understand the example

3. **Run the example**:
   ```bash
   ansible-playbook basic_playbook.yml
   ```

4. **Modify and experiment** - Change values and see what happens!

## 📝 Example Conventions

All examples follow these conventions:

- **Self-contained**: Each example can run independently
- **Local testing**: Most examples use `localhost` or `connection: local`
- **Safe defaults**: Examples won't harm your system
- **Well-commented**: Code includes explanatory comments
- **Real-world inspired**: Based on actual use cases

## 🎯 Quick Start

### Example 1: Hello World

```yaml
# hello_world.yml
---
- name: My first Ansible playbook
  hosts: localhost
  connection: local

  tasks:
    - name: Say hello
      debug:
        msg: "Hello, Ansible World!"
```

Run it:
```bash
ansible-playbook hello_world.yml
```

### Example 2: System Info

```yaml
# system_info.yml
---
- name: Gather system information
  hosts: localhost
  connection: local

  tasks:
    - name: Display OS information
      debug:
        msg: "Running {{ ansible_distribution }} {{ ansible_distribution_version }}"

    - name: Display memory
      debug:
        msg: "Total RAM: {{ ansible_memtotal_mb }} MB"
```

Run it:
```bash
ansible-playbook system_info.yml
```

## 📚 Learning Path

Follow this order for progressive learning:

1. **Chapter 1**: Basic commands and setup
2. **Chapter 2**: Inventory management
3. **Chapter 3**: Ad-hoc commands
4. **Chapter 4**: First playbooks
5. **Chapter 5**: Variables and facts
6. **Complete Examples**: Real-world projects

## 🔧 Troubleshooting Examples

If an example doesn't work:

1. **Check prerequisites**: Read the example's README
2. **Verify syntax**: `ansible-playbook playbook.yml --syntax-check`
3. **Run in check mode**: `ansible-playbook playbook.yml --check`
4. **Use verbose output**: `ansible-playbook playbook.yml -vvv`

## 🤝 Contributing

Found an issue or have a better example? See the main tutorial README for contribution guidelines.

## 📖 Additional Resources

- Full tutorial: See parent directory
- Quick reference: `../QUICK_REFERENCE.md`
- Official docs: https://docs.ansible.com/

---

**Happy Learning!** 🎓✨
