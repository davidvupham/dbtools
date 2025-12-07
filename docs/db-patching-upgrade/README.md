# Database Patching & Upgrade Methodology

## 1. Problem Statement

Currently, database patching and upgrading is a **manual, inconsistent, and high-risk process**. This leads to version drift, missed security patches, and heavy operational toil during maintenance windows.

## 2. Project Goal

The goal is to **fully automate** the patching and upgrade lifecycle for all database engines.

* **Standardization**: All new database builds MUST use the current "Approved" version.
* **Automation**: Patches are applied automatically during the defined maintenance window.
* **Cadence**: The system aligns with a strict **Monthly Patch Cycle** (3rd Saturday of the month).

## 3. Scope

The methodology covers the following engines and operating systems:

* **PostgreSQL** (Linux)
* **MongoDB** (Linux)
* **Microsoft SQL Server** (Windows)

## Documentation Structure

The project documentation is organized as follows:

* **[Architecture](architecture/)**: High-level strategy (e.g., Blue/Green, Rolling) and decision logs.
* **[Specs](specs/)**: Functional specifications defining *what* the tooling and processes must achieve.
* **[Design](design/)**: Technical design of the automation and scripts (Ansible, PowerShell, etc.).
* **[Implementation](implementation/)**: Plans and tracking for building the necessary tooling.
* **[Operations](operations/)**: Standard Operating Procedures (SOPs), Runbooks, and guides for the operations team.

### Functional Spec vs. Technical Design

| Feature | **Functional Specification** (The "What") | **Technical Design** (The "How") |
| :--- | :--- | :--- |
| **Audience** | Stakeholders, DBAs, Product Owners | Developers, Engineers |
| **Focus** | External Behavior, Inputs, Outputs, Rules | Internal Architecture, Classes, Libraries |
| **Analogy** | **Architect's Blueprint** (Room layout, usage) | **Engineering Schematics** (Wiring, plumbing, materials) |
| **In This Project** | Defines that the tool **"MUST check for replication lag"**. | Defines **"Use `rs.status()` in Python and parse the `optime` field"**. |
| **Example** | `functional-spec.md` defines the **"Canary Strategy"** rules (Patch 1, Wait 12h). | `design.md` defines that **GitHub Actions** will use a `job` with an `environment: production-canary` gate. |

## Getting Started

The recommended order of development for this methodology is:

1. **Architecture**: Define the strategy.
2. **Functional Specification**: Define the requirements.
3. **Design**: plan the technical implementation.
4. **Implementation**: Build the tools.
5. **Operations Guide**: Document the execution.
