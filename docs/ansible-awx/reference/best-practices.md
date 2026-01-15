# Ansible AWX Best Practices

**🔗 [← Back to Ansible AWX Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 15, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Best_Practices-blue)

> [!IMPORTANT]
> **Related Docs:** [Architecture](../explanation/architecture.md)

## Security Standards

### 1. Credentials Management
- **Never store credentials in Playbooks.** Use AWX Credential types to inject secrets at runtime.
- Use **Vault** for variables in Git, but prefer native AWX Credentials for authentication tokens, SSH keys, and cloud secrets.
- Implement **Least Privilege** using Teams and Roles. Give users "Execute" access to Job Templates, not "Write" access to Inventory or Projects.

### 2. Network Isolation
- Do not expose the AWX UI/API directly to the public internet. Use a VPN or internal load balancer.
- Use **Container Groups** or **Hop Nodes** to execute jobs in sensitive network zones without exposing the main cluster.

## Engineering Patterns

### 1. Automation Content as Code
- **Git is the Source of Truth.** Do not manually create Playbooks inside the AWX container.
- Use **Dynamic Inventory** plugins (e.g., `vmware_vm_inventory`, `azure_rm`) instead of static hosts whenever possible. This ensures inventory is always up-to-date with cloud state.

### 2. Execution Environments (EE)
- **Immutable Execution.** Build custom EEs for your specific toolsets (e.g., "Database EE" with `psycopg2` and `community.postgresql`).
- **Standardize EEs.** Avoid "kitchen sink" images. Create domain-specific EEs (Cloud, Network, Database) to keep image sizes small and specialized.
- **Versioning.** Tag your EE images (e.g., `my-custom-ee:1.2.0`) and pin Job Templates to specific versions to prevent regression during upgrades.

### 3. Job Templates
- Use **Surveys** to sanitize user input for ad-hoc jobs.
- Enable **Concurrent Jobs** carefully. Ensure your playbooks are idempotent and safe to run in parallel.
- Use **Fact Caching** if you have large inventories to speed up subsequent runs.

## Performance Tuning

### 1. Postgres Database
- Use an **external PostgreSQL** database for production clusters, rather than the containerized container provided by default.
- Tune `work_mem` and `maintenance_work_mem` based on your available resources.

### 2. Job Events
- Limit job event logging for high-volume jobs to prevent database bloat. Use the "Enable Job Slice" feature for massive inventories.

[↑ Back to Table of Contents](#security-standards)
