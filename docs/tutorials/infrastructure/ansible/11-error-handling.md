# Chapter 11: Error Handling

Robust automation requires graceful error handling. This chapter covers blocks, rescue, always, and other techniques for managing failures in Ansible playbooks.

## Learning Objectives

By the end of this chapter, you will:

- Implement block/rescue/always structures
- Use ignore_errors and failed_when
- Handle errors gracefully in loops
- Implement retries for unreliable tasks
- Create robust, production-ready playbooks

## Basic Error Behavior

By default, when a task fails:
- The failed host is removed from the play
- Remaining hosts continue
- Handlers are NOT executed for the failed host

## Block/Rescue/Always

Similar to try/catch/finally in programming languages.

### Basic Structure

```yaml
- name: Error handling example
  hosts: all
  become: yes

  tasks:
    - name: Handle potential failures
      block:
        - name: Task that might fail
          package:
            name: nonexistent-package
            state: present

        - name: This won't run if above fails
          debug:
            msg: "Package installed successfully"

      rescue:
        - name: This runs if block fails
          debug:
            msg: "Package installation failed, running recovery"

        - name: Log the error
          lineinfile:
            path: /var/log/ansible_errors.log
            line: "{{ ansible_date_time.iso8601 }} - Package installation failed on {{ inventory_hostname }}"
            create: yes

      always:
        - name: This ALWAYS runs
          debug:
            msg: "Cleanup or final tasks"
```

### Practical Example: Service Deployment

```yaml
- name: Deploy application with error handling
  hosts: webservers
  become: yes

  tasks:
    - name: Deploy application
      block:
        - name: Stop application
          service:
            name: myapp
            state: stopped

        - name: Deploy new code
          copy:
            src: app/
            dest: /opt/myapp/

        - name: Run database migrations
          command: /opt/myapp/migrate.sh

        - name: Start application
          service:
            name: myapp
            state: started

        - name: Verify application health
          uri:
            url: http://localhost:8080/health
            status_code: 200
          retries: 5
          delay: 10

      rescue:
        - name: Rollback to previous version
          copy:
            src: /opt/myapp.backup/
            dest: /opt/myapp/
          when: backup_exists | default(false)

        - name: Start application with old code
          service:
            name: myapp
            state: started

        - name: Send alert
          mail:
            to: ops@example.com
            subject: "Deployment failed on {{ inventory_hostname }}"
            body: "Application deployment failed. Rolled back to previous version."

      always:
        - name: Clean up temporary files
          file:
            path: /tmp/deploy_temp
            state: absent

        - name: Record deployment attempt
          lineinfile:
            path: /var/log/deployments.log
            line: "{{ ansible_date_time.iso8601 }} - Deploy {{ 'FAILED' if ansible_failed_task is defined else 'SUCCESS' }}"
            create: yes
```

## ignore_errors

Continue execution even if a task fails.

```yaml
- name: Task that might fail
  command: /usr/bin/might-not-exist
  ignore_errors: yes

- name: This will still run
  debug:
    msg: "Previous task status doesn't matter"
```

### Better Pattern: Register and Check

```yaml
- name: Check if service exists
  command: systemctl is-active myservice
  register: service_check
  ignore_errors: yes
  changed_when: false

- name: Handle based on result
  debug:
    msg: "Service is {{ 'running' if service_check.rc == 0 else 'not running' }}"

- name: Start service if not running
  service:
    name: myservice
    state: started
  when: service_check.rc != 0
```

## failed_when

Customize when a task should be considered failed.

```yaml
- name: Run command with custom failure condition
  command: /opt/check_status.sh
  register: status_result
  failed_when: "'ERROR' in status_result.stdout"

- name: Command that returns non-zero on success
  command: /opt/special_command
  register: special_result
  failed_when: special_result.rc not in [0, 1, 2]

- name: Fail if output doesn't contain expected text
  command: cat /etc/config.yml
  register: config_content
  failed_when: "'database:' not in config_content.stdout"
```

## changed_when

Control when a task reports as "changed".

```yaml
- name: Check command (never changed)
  command: cat /etc/hostname
  register: hostname_check
  changed_when: false

- name: Command with custom changed condition
  command: /opt/update_config.sh
  register: update_result
  changed_when: "'Updated' in update_result.stdout"

- name: Set changed based on multiple conditions
  shell: |
    /opt/deploy.sh
    echo $?
  register: deploy_result
  changed_when:
    - deploy_result.rc == 0
    - "'changes applied' in deploy_result.stdout"
```

## Retries and Until

Retry tasks until a condition is met.

```yaml
- name: Wait for service to be ready
  uri:
    url: http://localhost:8080/health
    status_code: 200
  register: health_check
  until: health_check.status == 200
  retries: 10
  delay: 5  # seconds between retries

- name: Wait for file to exist
  stat:
    path: /var/run/app.pid
  register: pid_file
  until: pid_file.stat.exists
  retries: 30
  delay: 2

- name: Wait for database connection
  command: pg_isready -h {{ db_host }} -p {{ db_port }}
  register: db_ready
  until: db_ready.rc == 0
  retries: 20
  delay: 3
  changed_when: false
```

## any_errors_fatal

Stop ALL hosts if ANY host fails.

```yaml
- name: Critical deployment
  hosts: all
  any_errors_fatal: true  # Stop everything if any host fails

  tasks:
    - name: Critical task
      package:
        name: critical-package
        state: present
```

### Selective Fatal Errors

```yaml
- name: Mixed criticality tasks
  hosts: all

  tasks:
    - name: Non-critical task
      package:
        name: optional-package
        state: present
      ignore_errors: yes

    - name: Critical section
      block:
        - name: Must succeed on all hosts
          command: /opt/critical.sh
      any_errors_fatal: true

    - name: Continue with other tasks
      debug:
        msg: "Continuing..."
```

## Error Handling in Loops

```yaml
- name: Handle errors in loops
  hosts: all

  tasks:
    - name: Process items with individual error handling
      block:
        - name: Process single item
          command: /opt/process.sh {{ item }}
          register: process_result
      rescue:
        - name: Log failed item
          debug:
            msg: "Failed to process {{ item }}"
      loop:
        - item1
        - item2
        - item3

    # Alternative: ignore_errors in loop
    - name: Process with ignore_errors
      command: /opt/process.sh {{ item }}
      loop:
        - item1
        - item2
        - item3
      register: results
      ignore_errors: yes

    - name: Report failures
      debug:
        msg: "Failed: {{ item.item }}"
      loop: "{{ results.results }}"
      when: item.failed
```

## force_handlers

Run handlers even if play fails.

```yaml
- name: Deploy with handler guarantee
  hosts: all
  force_handlers: true

  tasks:
    - name: Update configuration
      template:
        src: config.j2
        dest: /etc/app/config.yml
      notify: Restart app

    - name: Task that might fail
      command: /opt/risky_command.sh

  handlers:
    - name: Restart app
      service:
        name: app
        state: restarted
```

## Practical Examples

### Example 1: Database Migration with Rollback

```yaml
---
- name: Database migration with rollback
  hosts: databases
  become: yes

  vars:
    backup_dir: /var/backups/db
    migration_script: /opt/migrations/migrate.sql

  tasks:
    - name: Database migration
      block:
        - name: Create backup
          command: "pg_dump mydb > {{ backup_dir }}/pre_migration_{{ ansible_date_time.epoch }}.sql"

        - name: Run migration
          postgresql_query:
            db: mydb
            path_to_script: "{{ migration_script }}"
          register: migration_result

        - name: Verify migration
          postgresql_query:
            db: mydb
            query: "SELECT version FROM schema_versions ORDER BY id DESC LIMIT 1"
          register: version_check
          failed_when: version_check.query_result[0].version != expected_version

      rescue:
        - name: Restore from backup
          shell: "psql mydb < $(ls -t {{ backup_dir }}/pre_migration_*.sql | head -1)"

        - name: Notify failure
          debug:
            msg: "Migration failed and rolled back on {{ inventory_hostname }}"

      always:
        - name: Clean old backups (keep last 5)
          shell: "ls -t {{ backup_dir }}/pre_migration_*.sql | tail -n +6 | xargs rm -f"
```

### Example 2: Service Health Check with Recovery

```yaml
---
- name: Service health check and recovery
  hosts: webservers
  become: yes

  tasks:
    - name: Check and recover services
      block:
        - name: Check service health
          uri:
            url: "http://localhost:{{ app_port }}/health"
            status_code: 200
          register: health

      rescue:
        - name: Attempt service restart
          service:
            name: "{{ app_service }}"
            state: restarted

        - name: Wait for service recovery
          uri:
            url: "http://localhost:{{ app_port }}/health"
            status_code: 200
          register: health_after_restart
          until: health_after_restart.status == 200
          retries: 5
          delay: 10

      always:
        - name: Record health status
          lineinfile:
            path: /var/log/health_checks.log
            line: "{{ ansible_date_time.iso8601 }} {{ inventory_hostname }} {{ 'HEALTHY' if (health.status | default(0)) == 200 else 'RECOVERED' if (health_after_restart.status | default(0)) == 200 else 'UNHEALTHY' }}"
            create: yes
```

## Exercises

### Exercise 11.1: Implement Deployment Rollback

Create a playbook that:
1. Backs up current application
2. Deploys new version
3. Runs health check
4. Rolls back if health check fails

### Exercise 11.2: Graceful Service Migration

Create a playbook that:
1. Drains connections from load balancer
2. Performs maintenance
3. Restores service to load balancer
4. Handles failures at each step

### Exercise 11.3: Batch Processing with Error Tracking

Create a playbook that:
1. Processes a list of items
2. Continues on individual failures
3. Reports all failures at the end

## Key Takeaways

- `block/rescue/always` provides structured error handling
- `ignore_errors: yes` continues on failure (use sparingly)
- `failed_when` and `changed_when` customize task status
- `until/retries/delay` handle transient failures
- `any_errors_fatal: true` stops all hosts on any failure
- `force_handlers: true` ensures handlers run despite failures
- Always log errors and implement recovery procedures

## What's Next?

In the next chapter, you'll learn about Collections and Ansible Galaxy for extending Ansible capabilities.

**Next Chapter**: [Chapter 12: Collections and Galaxy](12-collections.md)
