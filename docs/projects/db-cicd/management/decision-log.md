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

---

## ADR-004: Changelog Format - Formatted SQL with Platform Folders

- **Date:** 2026-01-17
- **Status:** Proposed
- **Deciders:** Platform Engineering, DBA Team
- **Context:** We need to support 4 database platforms (SQL Server, PostgreSQL, Snowflake, MongoDB) with changelogs authored by both developers and DBAs. Must choose between Formatted SQL, XML, YAML, or JSON changelog formats.

- **Decision:** Use **Formatted SQL** as the primary format for relational databases (SQL Server, PostgreSQL, Snowflake) and **YAML** for MongoDB. Organize changelogs by platform in separate folders.

- **Rationale:**
  1. **Developer familiarity:** SQL is the native language; developers can review without learning XML/YAML
  2. **DBA preference:** DBAs can validate SQL syntax directly; no abstraction layer
  3. **IDE support:** SQL files get syntax highlighting, linting, and formatting in all editors
  4. **MongoDB exception:** MongoDB requires YAML/JSON for `ext:` change types (createCollection, createIndex)
  5. **Platform isolation:** Separate folders prevent accidental cross-platform execution

- **Project Structure:**
  ```
  database/
  ├── changelog-master.xml              # Root - includes all platforms
  ├── platforms/
  │   ├── mssql/
  │   │   ├── changelog.xml             # Platform master
  │   │   ├── baseline/
  │   │   │   └── V0000__baseline.mssql.sql
  │   │   └── changes/
  │   │       └── V0001__add_users.mssql.sql
  │   ├── postgres/
  │   │   ├── changelog.xml
  │   │   ├── baseline/
  │   │   └── changes/
  │   ├── snowflake/
  │   │   ├── changelog.xml
  │   │   ├── baseline/
  │   │   └── changes/
  │   └── mongodb/
  │       ├── changelog.yaml            # YAML for MongoDB
  │       └── changes/
  └── shared/
      └── data/                         # Reference data (CSV)
  ```

- **Alternatives Considered:**

  | Format | Pros | Cons | Decision |
  |--------|------|------|----------|
  | Formatted SQL | Native syntax, DBA-friendly, IDE support | Platform-specific | ✅ Use for RDBMS |
  | XML | Full feature support, includes | Verbose, harder to read | ❌ Reject |
  | YAML | Readable, compact | Less SQL visibility | ✅ Use for MongoDB only |
  | JSON | Machine-readable | Hard to author manually | ❌ Reject |

- **Naming Convention:**
  - Format: `V<timestamp>__<ticket>_<description>.<platform>.sql`
  - Example: `V202601171030__PROJ-123_add_users_table.mssql.sql`
  - Timestamp ensures ordering when using `includeAll`

- **Consequences:**
  - **Positive:** Clear platform separation; native SQL for review; scales to multi-database
  - **Negative:** Some duplication for cross-platform changes; MongoDB uses different format
  - **Risks:** Must ensure developers use correct folder; CI should validate platform targeting

---

## ADR-005: Baseline Strategy for Existing Databases

- **Date:** 2026-01-17
- **Status:** Proposed
- **Deciders:** DBA Team, Platform Engineering
- **Context:** We have existing production databases that need to be brought under Liquibase management. Need to decide how to capture current state and sync tracking tables.

- **Decision:** Generate baseline from **production** database, use `changelogSync` to mark as applied in all environments.

- **Approach:**
  1. **Generate baseline from production:**
     ```bash
     liquibase --url=<prod-url> generateChangeLog \
       --changelog-file=platforms/mssql/baseline/V0000__baseline.mssql.sql
     ```

  2. **Review and clean baseline:**
     - Remove system objects
     - Remove temporary/test objects
     - Add rollback statements
     - Split large baselines by schema if needed

  3. **Sync to all environments:**
     ```bash
     # For each environment (dev, stg, prd)
     liquibase --url=<env-url> changelogSync
     liquibase --url=<env-url> tag baseline
     ```

  4. **Capture post-baseline snapshot:**
     ```bash
     liquibase snapshot --output-file=snapshots/baseline-$(date +%Y%m%d).json
     ```

- **Alternatives:**
  - Generate from Dev: Risk of missing production objects
  - Manual baseline: Time-consuming, error-prone
  - Schema compare tool: Additional tooling, different format

- **Consequences:**
  - **Positive:** Accurate production state; all environments aligned; enables drift detection
  - **Negative:** One-time manual effort per database; review required
  - **Risks:** Production access required; must coordinate with DBA team

---

## ADR-006: Environment Promotion Strategy

- **Date:** 2026-01-17
- **Status:** Proposed
- **Deciders:** Tech Lead, Platform Engineering
- **Context:** Need to define how changes flow from development to production across environments. Anyone with repository permissions can author changes.

- **Decision:** Linear promotion with **CODEOWNERS-based PR approval**. No separate environment approval gates.

- **Environment Configuration:**

  | Environment | Trigger | Approval | Deployed By |
  |-------------|---------|----------|-------------|
  | Development | Auto on PR merge to `main` | CODEOWNERS review | CI |
  | Staging | Auto after Dev success | None (follows Dev) | CI |
  | Production | Auto after Stg success | None (follows Stg) | CI |

- **CODEOWNERS Strategy:**
  ```
  # .github/CODEOWNERS

  # Platform-specific owners
  /database/platforms/mssql/     @sql-server-team
  /database/platforms/postgres/  @postgres-team
  /database/platforms/snowflake/ @data-platform-team
  /database/platforms/mongodb/   @nosql-team

  # Shared resources require broader review
  /database/shared/              @dba-team @platform-engineering

  # CI/CD workflows require platform team
  /.github/workflows/            @platform-engineering
  ```

- **GitHub Branch Protection:**
  ```yaml
  branch_protection:
    main:
      required_pull_request_reviews:
        required_approving_review_count: 1
        require_code_owner_reviews: true
        dismiss_stale_reviews: true
      required_status_checks:
        strict: true
        contexts:
          - "validate-changelog"
          - "policy-check"
      restrictions:
        # Only CI can push to main after PR merge
  ```

- **Workflow:**
  1. Author creates feature branch and adds changeset
  2. Author opens PR to `main`
  3. CI runs validation and policy checks
  4. CODEOWNERS for affected platform review and approve
  5. PR merged → auto-deploy to Dev → Stg → Prod

- **Consequences:**
  - **Positive:** Fast deployment; ownership-based review; no bottlenecks; scales with team
  - **Negative:** Requires well-maintained CODEOWNERS file; no manual gate before Prod
  - **Risks:** Must ensure CODEOWNERS stays current; policy checks become critical safety net
