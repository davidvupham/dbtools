# Ansible Certification Assessments

This directory contains quizzes, practice tests, and mock exams to prepare you for Red Hat Ansible certifications (EX294/EX374).

## Assessment Overview

| Assessment | Purpose | Time | Passing |
|------------|---------|------|---------|
| Chapter Quizzes | Knowledge check per chapter | 10 min | 80% |
| Practice Test 1 | Beginner/Intermediate skills | 90 min | 70% |
| Practice Test 2 | Advanced, exam-like tasks | 3 hours | 70% |
| Mock Exam | Full EX294 simulation | 4 hours | 70% |

## Recommended Progression

```text
1. Complete Chapter → Take Chapter Quiz → Review missed topics
2. Complete Chapters 1-5 → Take Practice Test 1
3. Complete Chapters 6-13 → Take Practice Test 2
4. Review all materials → Take Mock Exam
5. Score 85%+ on Mock Exam → Ready for certification
```

## Chapter Quizzes

Knowledge-check quizzes for each chapter (10 questions, 10 minutes):

| Quiz | Chapter | Topics |
|------|---------|--------|
| [Quiz 1](quizzes/quiz-chapter-01.md) | Getting Started | Installation, architecture, commands |
| [Quiz 2](quizzes/quiz-chapter-02.md) | Inventory | Groups, patterns, variables |
| [Quiz 3](quizzes/quiz-chapter-03.md) | Ad-Hoc Commands | Modules, escalation |
| [Quiz 4](quizzes/quiz-chapter-04.md) | Playbooks | YAML, tasks, idempotency |
| [Quiz 5](quizzes/quiz-chapter-05.md) | Variables/Facts | Precedence, filters, facts |
| [Quiz 9](quizzes/quiz-chapter-09.md) | Roles | Structure, Galaxy, dependencies |
| [Quiz 13](quizzes/quiz-chapter-13.md) | Best Practices | Organization, security, testing |

## Practice Tests

### [Practice Test 1](practice-test-1.md) - Beginner/Intermediate

**Time**: 90 minutes | **Points**: 100 | **Environment**: 2 nodes

Tasks cover:
- Ansible configuration
- Inventory management
- Ad-hoc commands
- Basic playbooks
- Variables and facts
- Package/service management
- User management
- File operations

**When to take**: After completing Chapters 1-5

### [Practice Test 2](practice-test-2.md) - Advanced

**Time**: 3 hours | **Points**: 100 | **Environment**: 4 nodes

Tasks cover:
- Ansible Vault
- Custom roles
- Galaxy roles
- Conditionals and loops
- Error handling (block/rescue/always)
- Jinja2 templates
- Secure user creation
- Scheduled tasks
- Repository configuration
- Custom facts

**When to take**: After completing Chapters 1-13

## Mock Certification Exam

### [Mock Exam 1](mock-exam-1.md) - EX294 Simulation

**Time**: 4 hours | **Passing**: 70% (210/300) | **Environment**: 4 nodes

Full simulation of EX294 exam conditions:
- 18 comprehensive tasks
- No internet access
- Documentation available
- All changes must persist after reboot

Task categories:
1. Installation and configuration
2. Ad-hoc commands
3. Ansible Vault
4. User management with vault
5. MOTD configuration
6. SSH configuration
7. Custom Apache role
8. Role dependencies
9. Conditional packages
10. Cron jobs
11. RHEL system roles (timesync)
12. SELinux configuration
13. LVM storage
14. Hardware reports
15. Jinja2 templates
16. Password quality
17. Archive operations
18. Site playbook

**When to take**: After completing all chapters and practice tests

## Score Tracking

Use this table to track your progress:

| Assessment | Date | Score | Pass? | Notes |
|------------|------|-------|-------|-------|
| Quiz Ch1 | | /10 | | |
| Quiz Ch2 | | /10 | | |
| Quiz Ch3 | | /10 | | |
| Quiz Ch4 | | /10 | | |
| Quiz Ch5 | | /10 | | |
| Quiz Ch9 | | /10 | | |
| Quiz Ch13 | | /10 | | |
| Practice Test 1 | | /100 | | |
| Practice Test 2 | | /100 | | |
| Mock Exam 1 | | /300 | | |

## Tips for Success

### During Quizzes
- Don't look at answers until you've tried
- Review explanations for wrong answers
- Retake after studying weak areas

### During Practice Tests
- Set up a proper lab environment
- Don't use documentation (simulate exam)
- Complete all tasks before checking solutions
- Time yourself

### During Mock Exam
- Create exam-like conditions (no interruptions)
- Use only allowed resources
- Verify all configurations persist after reboot
- Manage time (~13 minutes per task)

## Environment Setup

For hands-on assessments, set up:

**Option 1: Vagrant**
```bash
vagrant init generic/rhel9
vagrant up
```

**Option 2: Docker**
```bash
docker run -d --name node1 -p 2221:22 centos/systemd
docker run -d --name node2 -p 2222:22 centos/systemd
```

**Option 3: Cloud VMs**
- AWS EC2, Azure VM, or GCP Compute instances
- Use RHEL 9 or CentOS Stream 9

## Related Resources

- [Certification Prep Guide](../CERTIFICATION_PREP.md) - Full exam objectives mapping
- [Quick Reference](../QUICK_REFERENCE.md) - Command and syntax reference
- [Learning Guide](../LEARNING_GUIDE.md) - Study paths and tips

---

**Target**: Score 85%+ on Mock Exam before scheduling the real certification exam.

Good luck with your preparation!
