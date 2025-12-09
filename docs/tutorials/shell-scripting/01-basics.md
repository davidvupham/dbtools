# Shell Scripting for DevOps

## Introduction
Automation starts with the shell. Bash scripting is a fundamental skill for gluing tools together.

## Key Concepts

### Variables
```bash
NAME="DevOps"
echo "Hello, $NAME"
```

### Control Structures
**Loops:**
```bash
for i in {1..5}; do
  echo "Count: $i"
done
```

**Conditionals:**
```bash
if [ -f "/etc/passwd" ]; then
  echo "File exists"
fi
```

### Functions
Organize your code into reusable blocks.
```bash
check_status() {
  systemctl status nginx
}
```

### Cron Jobs
Scheduling tasks using `crontab`.
- Format: `* * * * * command_to_execute`
