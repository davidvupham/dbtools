# Red Hat Ansible Certification Preparation Guide

This guide prepares you for the **Red Hat Certified Engineer (RHCE) EX294** exam and the **Red Hat Certified Specialist in Developing Automation with Ansible Automation Platform (EX374)** exam.

## Exam Overview

### EX294 - Red Hat Certified Engineer (RHCE)

| Attribute | Details |
|-----------|---------|
| Duration | 4 hours (240 minutes) |
| Format | Performance-based (hands-on) |
| Passing Score | 210/300 (70%) |
| Prerequisites | Valid RHCSA certification |
| Validity | 3 years |
| Cost | ~$400 USD |

**Key Characteristics:**
- No internet access during exam
- Must use Red Hat documentation provided
- All configurations must persist after reboot
- Real-world tasks on multiple virtual systems

### EX374 - Developing Automation with Ansible Automation Platform

| Attribute | Details |
|-----------|---------|
| Duration | 4 hours (240 minutes) |
| Format | Performance-based (hands-on) |
| Focus | Advanced automation, AAP, content development |
| Prerequisites | EX294 recommended |

---

## EX294 Exam Objectives Mapping

This section maps each exam objective to the course chapter that covers it.

### 1. Understand Core Components of Ansible

| Objective | Course Coverage | Chapter |
|-----------|-----------------|---------|
| Inventories | Comprehensive | [Chapter 2](02-inventory.md) |
| Modules | Comprehensive | [Chapter 3](03-adhoc-commands.md), [Chapter 4](04-playbooks-basics.md) |
| Variables | Comprehensive | [Chapter 5](05-variables-facts.md) |
| Facts | Comprehensive | [Chapter 5](05-variables-facts.md) |
| Loops | Comprehensive | [Chapter 6](06-conditionals-loops.md) |
| Conditional tasks | Comprehensive | [Chapter 6](06-conditionals-loops.md) |
| Plays | Comprehensive | [Chapter 4](04-playbooks-basics.md) |
| Handling task failure | Comprehensive | [Chapter 11](11-error-handling.md) |
| Playbooks | Comprehensive | [Chapter 4](04-playbooks-basics.md) |
| Configuration files | Comprehensive | [Chapter 1](01-getting-started.md) |
| Roles | Comprehensive | [Chapter 9](09-roles.md) |
| Use provided documentation | Reference | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |

### 2. Use Roles and Ansible Content Collections

| Objective | Course Coverage | Chapter |
|-----------|-----------------|---------|
| Create roles | Comprehensive | [Chapter 9](09-roles.md) |
| Download roles from Ansible Galaxy | Comprehensive | [Chapter 9](09-roles.md) |
| Use roles in playbooks | Comprehensive | [Chapter 9](09-roles.md) |
| Install Content Collections | Comprehensive | [Chapter 12](12-collections.md) |
| Use modules from Content Collections | Comprehensive | [Chapter 12](12-collections.md) |

### 3. Install and Configure an Ansible Control Node

| Objective | Course Coverage | Chapter |
|-----------|-----------------|---------|
| Install required packages | Comprehensive | [Chapter 1](01-getting-started.md) |
| Create static host inventory | Comprehensive | [Chapter 2](02-inventory.md) |
| Create configuration file | Comprehensive | [Chapter 1](01-getting-started.md) |
| Create and use static inventories | Comprehensive | [Chapter 2](02-inventory.md) |
| Manage parallelism | Covered | [Chapter 13](13-best-practices.md) |

### 4. Configure Ansible Managed Nodes

| Objective | Course Coverage | Chapter |
|-----------|-----------------|---------|
| Create and distribute SSH keys | Covered | [Chapter 1](01-getting-started.md) |
| Configure privilege escalation | Covered | [Chapter 3](03-adhoc-commands.md) |
| Deploy files to managed nodes | Comprehensive | [Chapter 4](04-playbooks-basics.md) |
| Collect system information | Comprehensive | [Chapter 5](05-variables-facts.md) |

### 5. Run Playbooks with Automation Content Navigator

| Objective | Course Coverage | Chapter |
|-----------|-----------------|---------|
| Run playbooks | Comprehensive | [Chapter 4](04-playbooks-basics.md) |
| Use ansible-navigator | Covered | [Chapter 16](16-automation-navigator.md) |
| Find modules in content collections | Covered | [Chapter 12](12-collections.md) |
| Use VS Code for playbook development | Reference | [Chapter 1](01-getting-started.md) |

### 6. Create Ansible Plays and Playbooks

| Objective | Course Coverage | Chapter |
|-----------|-----------------|---------|
| Use common modules | Comprehensive | [Chapter 3](03-adhoc-commands.md), [Chapter 4](04-playbooks-basics.md) |
| Use variables with command output | Comprehensive | [Chapter 5](05-variables-facts.md) |
| Conditionals for task execution | Comprehensive | [Chapter 6](06-conditionals-loops.md) |
| Error handling in playbooks | Comprehensive | [Chapter 11](11-error-handling.md) |
| Selectively run tasks with tags | Covered | [Chapter 9](09-roles.md) |

### 7. Automate Standard RHCSA Tasks

| Objective | Course Coverage | Chapter |
|-----------|-----------------|---------|
| Manage software packages and repositories | Comprehensive | [Chapter 3](03-adhoc-commands.md), [Chapter 4](04-playbooks-basics.md) |
| Manage services | Comprehensive | [Chapter 3](03-adhoc-commands.md), [Chapter 4](04-playbooks-basics.md) |
| Manage firewall rules | Covered | [Chapter 4](04-playbooks-basics.md) |
| Manage file systems | Covered | [Practice Exam](assessments/mock-exam-1.md) |
| Manage storage devices | Covered | [Practice Exam](assessments/mock-exam-1.md) |
| Manage file content | Comprehensive | [Chapter 4](04-playbooks-basics.md) |
| Archive files | Covered | [Chapter 3](03-adhoc-commands.md) |
| Schedule tasks (cron, at) | Covered | [Practice Exam](assessments/mock-exam-1.md) |
| Manage users and groups | Comprehensive | [Chapter 4](04-playbooks-basics.md) |
| Manage SELinux | Covered | [Chapter 17](17-system-roles.md) |

### 8. Manage Content

| Objective | Course Coverage | Chapter |
|-----------|-----------------|---------|
| Create templates | Comprehensive | [Chapter 8](08-templates.md) |
| Use Ansible Vault | Comprehensive | [Chapter 10](10-vault.md) |

---

## Study Plan by Experience Level

### Beginner Path (6-8 weeks)

**Week 1-2: Foundations**
- [ ] Complete Chapter 1: Getting Started
- [ ] Complete Chapter 2: Inventory Management
- [ ] Complete Chapter 3: Ad-Hoc Commands
- [ ] Take Quiz 1-3

**Week 3-4: Core Skills**
- [ ] Complete Chapter 4: Playbooks Basics
- [ ] Complete Chapter 5: Variables and Facts
- [ ] Complete Chapter 6: Conditionals and Loops
- [ ] Take Quiz 4-6
- [ ] Complete Practice Test 1

**Week 5-6: Advanced Topics**
- [ ] Complete Chapter 7: Handlers
- [ ] Complete Chapter 8: Templates
- [ ] Complete Chapter 9: Roles
- [ ] Complete Chapter 10: Ansible Vault
- [ ] Take Quiz 7-10

**Week 7-8: Exam Preparation**
- [ ] Complete Chapter 11-13
- [ ] Complete Practice Test 2
- [ ] Complete Mock Certification Exam
- [ ] Review weak areas
- [ ] Retake practice exams

### Experienced Path (2-3 weeks)

**Week 1: Review and Gaps**
- [ ] Skim Chapters 1-5 (review)
- [ ] Deep dive into Chapters 6-10
- [ ] Take all chapter quizzes
- [ ] Complete Practice Test 1

**Week 2: Advanced and Practice**
- [ ] Complete Chapters 11-13
- [ ] Complete Chapter 16-17 (Navigator, System Roles)
- [ ] Complete Practice Test 2
- [ ] Complete Mock Certification Exam

**Week 3: Intensive Practice**
- [ ] Repeat Mock Exam until 90%+ score
- [ ] Build 3 complete automation projects
- [ ] Review all failed quiz questions

---

## Critical Topics for EX294

Based on exam objectives and feedback, these topics are ESSENTIAL:

### Must Master (High Weight)

1. **Ansible Vault** - Encrypting/decrypting, vault passwords, encrypted variables
2. **Roles** - Creating, using, Galaxy, dependencies
3. **Conditionals and Loops** - when statements, loop types, registered variables
4. **Templates (Jinja2)** - Variable substitution, filters, conditionals in templates
5. **Error Handling** - block/rescue/always, ignore_errors, failed_when

### Important Topics (Medium Weight)

6. **Inventory Management** - Groups, variables, patterns
7. **Playbook Structure** - Multiple plays, pre/post tasks, handlers
8. **Variables and Facts** - Precedence, magic variables, custom facts
9. **RHCSA Tasks** - Package management, services, users, firewall

### Know Well (Lower Weight)

10. **Collections** - Installing, using modules from collections
11. **System Roles** - rhel-system-roles usage
12. **Automation Navigator** - Basic usage (ansible-navigator)

---

## Exam Day Tips

### Before the Exam

1. **Get RHCSA first** - Required prerequisite for RHCE certification
2. **Practice time management** - 4 hours goes fast with 15-20 tasks
3. **Know the documentation** - Red Hat docs are available during exam
4. **Set up your environment** - Practice with similar RHEL versions

### During the Exam

1. **Read all questions first** - Identify dependencies between tasks
2. **Start with what you know** - Build confidence and save time
3. **Use ansible-doc** - `ansible-doc <module>` for syntax help
4. **Check your work** - Run playbooks, verify configurations
5. **Ensure persistence** - Configurations must survive reboot

### Common Mistakes to Avoid

- Forgetting `become: yes` for privileged operations
- YAML indentation errors (use spaces, not tabs)
- Not testing playbooks before moving on
- Forgetting to start/enable services
- Not using handlers for service restarts
- Hardcoding values instead of using variables

---

## Practice Resources

### This Course

| Resource | Description | Location |
|----------|-------------|----------|
| Chapter Quizzes | Knowledge checks per chapter | [assessments/quizzes/](assessments/quizzes/) |
| Practice Test 1 | Beginner/Intermediate scenarios | [assessments/practice-test-1.md](assessments/practice-test-1.md) |
| Practice Test 2 | Advanced exam-like scenarios | [assessments/practice-test-2.md](assessments/practice-test-2.md) |
| Mock Exam | Full EX294 simulation | [assessments/mock-exam-1.md](assessments/mock-exam-1.md) |

### External Resources

| Resource | Type | Link |
|----------|------|------|
| Red Hat Training | Official courses | [redhat.com/training](https://www.redhat.com/en/services/training) |
| Ansible Documentation | Reference | [docs.ansible.com](https://docs.ansible.com/) |
| Pluralsight | Video courses | [pluralsight.com](https://www.pluralsight.com/) |
| Udemy | Practice exams | Search "RHCE EX294" |
| Sander van Vugt | RHCE book & videos | [sandervanvugt.com](https://www.sandervanvugt.com/) |

### Recommended Books

1. **RHCE EX294 Cert Guide** by Sander van Vugt (Pearson)
2. **Red Hat Certified Engineer (RHCE) Study Guide** by Andrew Mallett (Apress)
3. **Ansible for DevOps** by Jeff Geerling (free online)

---

## Self-Assessment Checklist

Rate your confidence (1-5) on each skill:

### Core Skills
- [ ] Create and manage inventory files (INI and YAML)
- [ ] Write playbooks with multiple plays
- [ ] Use variables and facts effectively
- [ ] Implement conditionals and loops
- [ ] Create and use roles
- [ ] Encrypt data with Ansible Vault
- [ ] Handle errors with blocks and rescue

### RHCSA Automation
- [ ] Manage packages and repositories
- [ ] Configure and manage services
- [ ] Manage users and groups
- [ ] Configure firewall rules
- [ ] Manage file permissions and content
- [ ] Schedule tasks with cron

### Advanced Topics
- [ ] Create and use Jinja2 templates
- [ ] Use Ansible Galaxy roles
- [ ] Install and use Content Collections
- [ ] Configure SELinux with system roles
- [ ] Use ansible-navigator

### Scoring
- **35-50 points**: Ready for exam
- **25-34 points**: More practice needed
- **Below 25 points**: Review course materials

---

## Next Steps

1. **Start with the [Learning Guide](LEARNING_GUIDE.md)** to understand the course structure
2. **Complete chapters sequentially** or use the certification path
3. **Take chapter quizzes** after each chapter
4. **Complete practice tests** before attempting mock exam
5. **Schedule the exam** when consistently scoring 85%+ on mock exams

Good luck with your certification journey!

---

**Last Updated**: 2024
**Exam Versions**: EX294 (RHEL 9), EX374
