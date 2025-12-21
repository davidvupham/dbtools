# RACI Matrix: db-cicd

| Activity | Sponsor | Product Owner | Tech Lead | Developer | DBA Team |
|----------|---------|---------------|-----------|-----------|----------|
| **Initiation** |
| Approve project | A | R | C | I | I |
| Define requirements | I | A | R | C | C |
| **Planning** |
| Architecture design | I | A | R | C | C |
| Technology selection | I | C | A | R | C |
| Effort estimation | I | A | R | R | C |
| **Execution** |
| Implementation | I | I | A | R | I |
| Code review | I | I | A | R | I |
| Documentation | I | C | A | R | C |
| **Validation** |
| Unit testing | I | I | A | R | I |
| Integration testing | I | C | A | R | R |
| UAT | I | A | C | C | R |
| **Deployment** |
| Production rollout | A | R | A | R | R |
| Runbook approval | I | C | A | C | R |

**Legend:**

- **R** = Responsible (does the work)
- **A** = Accountable (final approval)
- **C** = Consulted (provides input)
- **I** = Informed (kept up to date)
