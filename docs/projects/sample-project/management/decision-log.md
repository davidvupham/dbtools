# Decision Log: Sample Project

Refer to the ADR template: [Decision Log Template](../../best-practices/technical-project-management.md#decision-log-template)

---

## ADR-001: Tooling choice – GitHub vs Jira

- **Date:** 2025-12-11
- **Status:** Accepted
- **Deciders:** Project Sponsor, Product Owner, Tech Lead
- **Context:** Team primarily collaborates via code (PRs, Actions, Ansible/AWX). Organization allows team-level choice for work tracking.
- **Decision:** Use GitHub Issues/Projects and PR governance as the primary work-tracking and approval mechanism. Link to Jira only when enterprise workflows mandate it.
- **Alternatives:**
	- Jira as primary (Pros: enterprise workflows; Cons: duplication with code-centric work)
	- Split model (Jira + GitHub equally) (Pros: flexibility; Cons: fragmented source of truth)
- **Consequences:**
	- **Positive:** Work tracking close to code; simpler automation; PR-driven governance.
	- **Negative:** Less built-in portfolio reporting vs Jira.
	- **Risks:** If enterprise mandates change, may need migration of issues to Jira.
