# Comparative Analysis: Orchestration Tools

## 1. Executive Summary

For the specific use case of **Database Patching & Upgrades**—which involves high-risk, stateful operations, approval gates, and tight integration with version control—**GitHub Actions** is the recommended choice.

* **GitHub Actions**: Best for GitOps, Approval Gates, and simplicity.
* **Temporal.io**: Best for extremely long-running (days/months) or complex logic flows where "durable execution" is critical.
* **Apache Airflow**: Best for Data Engineering pipelines (ETL) and strictly time-based schedules.

## 2. Detailed Comparison

| Feature | GitHub Actions | Temporal.io | Apache Airflow |
| :--- | :--- | :--- | :--- |
| **Primary Domain** | CI/CD & Ops Automation | Durable Execution / Microservices | Data Engineering (ETL) |
| **Paradigm** | YAML (Declarative) | Code (Imperative - Python/Go/Java) | Python (DAGs) |
| **State Management** | Ephemeral (Logs preserved) | **Persistent** (Event History) | Database Backend (Task State) |
| **Approval Gates** | **Native** (Environments / Reviewers) | Custom (Signals / Human-in-the-loop patterns) | Weak (Sensors / UI Plugins) |
| **Infrastructure** | Minimal (SaaS or pure Runners) | Heavy (Server + DB + ES + Workers) | Medium (Scheduler + Webserver + Workers) |
| **Learning Curve** | Low | High (New paradigm) | Medium |

## 3. Tool-Specific Analysis

### 3.1 GitHub Actions (Recommended)

**Why it fits:**

* **GitOps Native**: The "Version Registry" (`db_versions.yml`) lives in Git. Accessing it is native.
* **Approvals**: Deployment Protection Rules allow us to pause a workflow until a DBA approves the "Deploy" job in the UI. reliable and auditable.
* **Inventory Access**: Self-Hosted Runners inside the VPC provide direct access to Ansible/PowerShell without complex tunnels.

**Drawbacks:**

* **Workflow Limits**: Workflows cannot run forever (max 72 hours usually, significantly less on free tier). Not suitable if a patch takes 4 days.

### 3.2 Temporal.io

**Pros:**

* **Invincibility**: If the orchestration server crashes, the workflow resumes exactly where it left off.
* **Code-First**: You write logic in Python/Go, allowing complex branching and error handling that YAML can't match.

**Cons:**

* **Operational Overhead**: Requires maintaining a production-grade Temporal Cluster (or paying for Cloud).
* **Overkill**: Database patching is usually atomic per node. We rely on the underlying tool (Ansible) for idempotency, effectively mitigating the need for Temporal's granular state recovery.

### 3.3 Apache Airflow

**Pros:**

* **Visibility**: Excellent UI for visualizing dependencies (DAGs).
* **Scheduling**: Powerful cron-like capabilities and "backfill".

**Cons:**

* **"Task" focus, not "Event" focus**: Airflow is designed to run a job at 2 AM every day. It is clunky for "Trigger a patch because a PR was merged".
* **Static DAGs**: Dynamic fleet inventory changes can be harder to manage in static Python DAG files compared to dynamic Ansible inventories.

## 4. Conclusion

We will proceed with **GitHub Actions**. detailed in the [Design Document](../design/design.md). It provides the best balance of "Auditability" (for security) and "Simplicity" (for maintenance).
