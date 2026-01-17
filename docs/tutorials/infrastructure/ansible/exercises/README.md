# Ansible Tutorial Exercises

This directory contains hands-on exercises to practice what you've learned. Each exercise includes the problem statement, hints, and solutions.

## 📚 Exercise Structure

```text
exercises/
├── beginner/
│   ├── exercise-01-first-playbook.md
│   ├── exercise-02-inventory.md
│   ├── exercise-03-variables.md
│   └── solutions/
├── intermediate/
│   ├── exercise-01-roles.md
│   ├── exercise-02-templates.md
│   ├── exercise-03-handlers.md
│   └── solutions/
├── advanced/
│   ├── exercise-01-dynamic-inventory.md
│   ├── exercise-02-custom-modules.md
│   ├── exercise-03-performance.md
│   └── solutions/
└── projects/
    ├── project-01-web-server.md
    ├── project-02-database-cluster.md
    └── project-03-full-stack.md
```

## 🎯 How to Use Exercises

### Step 1: Choose Your Level

- **Beginner**: New to Ansible (Chapters 1-5)
- **Intermediate**: Comfortable with basics (Chapters 6-10)
- **Advanced**: Ready for complex scenarios (Chapters 11-14)
- **Projects**: Full end-to-end implementations

### Step 2: Read the Exercise

Each exercise includes:
- **Objective**: What you'll build
- **Requirements**: What must be included
- **Hints**: Tips to guide you
- **Expected Outcome**: What success looks like

### Step 3: Try It Yourself

Work on the exercise without looking at the solution first!

### Step 4: Check Your Solution

Compare your answer with the provided solution. Remember: there are often multiple correct approaches!

### Step 5: Experiment

Try variations and modifications to deepen your understanding.

## 🏆 Exercise Guidelines

### Do's ✅

- **Try first**: Attempt the exercise before checking solutions
- **Take notes**: Document what you learn
- **Experiment**: Modify examples to see what happens
- **Break things**: Learning from failures is valuable
- **Ask why**: Understand the reasoning behind solutions

### Don'ts ❌

- **Don't copy-paste**: Type code to build muscle memory
- **Don't skip**: Each exercise builds on previous ones
- **Don't rush**: Take time to understand concepts
- **Don't give up**: Check hints if stuck

## 📝 Sample Exercise Format

Here's what each exercise looks like:

---

## Exercise: Install and Configure Web Server

**Level**: Beginner
**Chapter**: 4 - Playbooks Basics
**Time**: 30 minutes

### Objective

Create a playbook that installs and configures nginx on localhost.

### Requirements

1. Install nginx package
2. Create a custom index.html page
3. Start nginx service
4. Enable nginx to start on boot
5. Verify nginx is accessible

### Hints

<details>
<summary>Hint 1: Modules to use</summary>

You'll need: `package`, `copy`, and `service` modules.

</details>

<details>
<summary>Hint 2: Index page content</summary>

Create content with `copy` module using the `content` parameter.

</details>

<details>
<summary>Hint 3: Testing</summary>

Use the `uri` module to verify nginx responds on port 80.

</details>

### Expected Outcome

When you run the playbook:
- Nginx is installed
- Custom page is visible at http://localhost
- Service is running and enabled
- All tasks show as changed or ok (idempotent on second run)

### Solution

<details>
<summary>Click to reveal solution</summary>

```yaml
---
- name: Install and configure nginx
  hosts: localhost
  connection: local
  become: yes

  tasks:
    - name: Install nginx
      package:
        name: nginx
        state: present

    - name: Create custom index page
      copy:
        content: |
          <html>
          <head><title>Welcome</title></head>
          <body>
            <h1>Hello from Ansible!</h1>
            <p>Server: {{ ansible_hostname }}</p>
          </body>
          </html>
        dest: /var/www/html/index.html
        mode: '0644'

    - name: Start and enable nginx
      service:
        name: nginx
        state: started
        enabled: yes

    - name: Verify nginx is running
      uri:
        url: http://localhost
        return_content: yes
      register: result
      failed_when: result.status != 200

    - name: Display result
      debug:
        msg: "Nginx is running and accessible!"
```

</details>

---

## 🎓 Learning Tips

### Progressive Difficulty

Exercises increase in complexity:
1. Single task playbooks
2. Multi-task playbooks
3. Multi-play playbooks
4. Playbooks with variables
5. Playbooks with roles
6. Complex multi-component projects

### Skills Practiced

Each exercise helps you practice:
- **Syntax**: Writing correct YAML and Ansible code
- **Modules**: Using the right module for the task
- **Logic**: Applying conditionals and loops
- **Organization**: Structuring playbooks and roles
- **Debugging**: Finding and fixing issues
- **Best Practices**: Writing maintainable code

## 📊 Track Your Progress

Keep a learning journal:

```markdown
## Exercise Log

### Date: 2024-01-15
**Exercise**: Beginner Exercise 01 - First Playbook
**Status**: ✅ Completed
**Time**: 25 minutes
**Notes**:
- Learned about task naming
- Understood module parameters
- Practiced YAML syntax

**Challenges**:
- Initially forgot to quote variables
- Fixed by adding quotes around strings with variables

**What I Learned**:
- Always name tasks for clarity
- Quote strings that start with variables
- Use check mode to test before running
```

## 🆘 Getting Help

If you're stuck on an exercise:

1. **Re-read the chapter** related to the exercise
2. **Check the hints** provided in the exercise
3. **Use verbose mode** to see what's happening
4. **Search documentation** for module details
5. **Review the solution** and understand why it works

## 🎯 Challenge Exercises

After completing regular exercises, try these challenges:

### Challenge 1: Speed Run
Complete all beginner exercises in under 2 hours.

### Challenge 2: No Hints
Complete intermediate exercises without using any hints.

### Challenge 3: Improve It
Take a solution and improve it with better practices.

### Challenge 4: Different Approach
Solve an exercise using a completely different method.

### Challenge 5: Teach It
Explain a solution to someone else (or write it out).

## 🏅 Completion Checklist

- [ ] All beginner exercises completed
- [ ] All intermediate exercises completed
- [ ] All advanced exercises completed
- [ ] At least one project completed
- [ ] All exercises can be run without errors
- [ ] Understood the concepts, not just copied solutions
- [ ] Experimented with variations
- [ ] Created own custom exercise

## 📖 Next Steps

After completing exercises:

1. **Build a real project** from your own use case
2. **Contribute to open source** Ansible roles
3. **Automate your workflow** at work or home
4. **Share knowledge** by teaching others
5. **Keep learning** with advanced topics

---

**Remember**: The goal is learning, not just completing exercises. Take your time and understand each concept!

**Happy Practicing!** 💪🎓
