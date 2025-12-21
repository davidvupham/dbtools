# Decision Log: db-cicd

## ADR-001: Project Scope and Approach

- **Date:** 2025-12-20
- **Status:** Proposed
- **Deciders:** TBD
- **Context:** Liquibase Pro license cost is prohibitive. We need equivalent functionality using open-source tooling and custom development.
- **Decision:** Build a custom platform (db-cicd) that wraps Liquibase Community with additional capabilities: policy checks, drift detection, structured logging, approval workflows, and GitHub Actions integration.
- **Alternatives:**
  - Purchase Liquibase Pro license (~$15,000-50,000/year)
  - Use Liquibase Community as-is without enhancements
  - Evaluate alternative tools (Flyway, Atlas)
- **Consequences:**
  - **Positive:** No licensing cost; full customization; integrated with existing GitHub workflows
  - **Negative:** ~680 hours development effort; ongoing maintenance burden
  - **Risks:** Some Pro features (stored logic extraction) may have limited parity

---

## ADR-002: No API - CLI and GitHub Actions Only

- **Date:** 2025-12-20
- **Status:** Proposed
- **Deciders:** TBD
- **Context:** Need to decide whether to build an API layer for the platform.
- **Decision:** Use CLI tools orchestrated by GitHub Actions only; no REST API.
- **Alternatives:**
  - Lightweight REST API for status/reports
  - Full API with web dashboard
- **Consequences:**
  - **Positive:** Simpler architecture; no additional infrastructure; faster delivery
  - **Negative:** No real-time dashboard; all interaction via GitHub UI
  - **Risks:** May need API later if requirements change

---

## ADR-003: GitHub Environment Protection for Approvals

- **Date:** 2025-12-20
- **Status:** Proposed
- **Deciders:** TBD
- **Context:** Need approval workflow for production deployments.
- **Decision:** Use GitHub Environment protection rules with required reviewers and CODEOWNERS.
- **Alternatives:**
  - Custom approval service
  - ServiceNow/Jira integration
- **Consequences:**
  - **Positive:** Native GitHub integration; no additional tooling; audit via GitHub
  - **Negative:** Limited to GitHub users; no complex approval chains
