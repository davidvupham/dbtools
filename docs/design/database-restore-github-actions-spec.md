# Database Restore via GitHub Actions - Design Specification

## Document Information

| Item | Value |
|------|-------|
| Version | 1.0 |
| Status | Draft |
| Author | Infrastructure Team |
| Date | 2026-01-22 |

---

## 1. Executive Summary

This document specifies a GitHub Actions-based solution for restoring SQL Server databases from production to development environments. The solution provides:

- Self-service database restore requests by developers
- Team-based approval workflows
- Point-in-time recovery support
- Automated notifications
- Post-restore script execution
- Audit trail via GitHub's native logging

---

## 2. Requirements

### 2.1 Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-01 | Developers can request a database restore via GitHub Actions workflow |
| FR-02 | Request must include: database name, source server, destination server, point-in-time, scheduled start time |
| FR-03 | Only team members designated as database owners can approve requests |
| FR-04 | Team notification upon request submission |
| FR-05 | Team notification upon request approval/rejection |
| FR-06 | Execute post-restore scripts after successful restore |
| FR-07 | Team notification upon restore completion (success or failure) |
| FR-08 | Support for multiple teams with isolated approval chains |

### 2.2 Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | Audit trail for all restore operations |
| NFR-02 | Secrets management for database credentials |
| NFR-03 | Timeout handling for long-running restores |
| NFR-04 | Retry capability for failed operations |

---

## 3. Architecture Decision: Single Repo vs Multiple Repos

### 3.1 Recommendation: Single Repository

**A single repository can handle multiple teams** using GitHub's native features:

| Feature | How It Enables Multi-Team Support |
|---------|-----------------------------------|
| **Environments** | Create one environment per team (e.g., `team-alpha-restore`, `team-beta-restore`) |
| **Environment Protection Rules** | Each environment has its own required reviewers (team-specific) |
| **GitHub Teams** | Map approval rights to GitHub Teams |
| **CODEOWNERS** | Optional: route based on paths if using issue-based triggers |

### 3.2 Comparison

| Aspect | Single Repo | Multiple Repos |
|--------|-------------|----------------|
| Maintenance | One workflow to maintain | N workflows to maintain |
| Consistency | Guaranteed | Risk of drift |
| Access Control | Via environments + teams | Via repo permissions |
| Audit | Centralized | Distributed |
| Complexity | Medium | Low per repo, high overall |
| Team Autonomy | Lower (shared ownership) | Higher (full control) |

### 3.3 When to Use Multiple Repos

Consider multiple repos if:
- Teams require significantly different restore procedures
- Regulatory requirements mandate separation
- Teams want full autonomy over their workflows
- Organization has 20+ teams (environment management becomes complex)

---

## 4. Solution Design

### 4.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        GitHub Actions Workflow                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │   Request    │───▶│   Approval   │───▶│   Execute Restore        │  │
│  │   (Input)    │    │   (Manual)   │    │   (Self-hosted Runner)   │  │
│  └──────────────┘    └──────────────┘    └──────────────────────────┘  │
│         │                   │                        │                  │
│         ▼                   ▼                        ▼                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │  Notify Team │    │  Notify Team │    │  Notify Team             │  │
│  │  (Request)   │    │  (Approved)  │    │  (Complete/Failed)       │  │
│  └──────────────┘    └──────────────┘    └──────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     Self-Hosted Runner (On-Premises)                    │
├─────────────────────────────────────────────────────────────────────────┤
│  • Network access to SQL Servers                                        │
│  • SQL Server tools (sqlcmd, RESTORE commands)                          │
│  • PowerShell with SqlServer module                                     │
│  • Access to backup storage (network share, Azure Blob, S3)             │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 GitHub Configuration

#### 4.2.1 Teams Setup

Create GitHub Teams for each database ownership group:

```
Organization
├── team-alpha-db-owners      # Can approve Team Alpha restores
├── team-beta-db-owners       # Can approve Team Beta restores
├── team-gamma-db-owners      # Can approve Team Gamma restores
└── dba-admins                # Can approve any restore (optional)
```

#### 4.2.2 Environments Setup

Create environments with protection rules:

| Environment | Required Reviewers | Description |
|-------------|-------------------|-------------|
| `team-alpha-restore` | `team-alpha-db-owners` | Team Alpha database restores |
| `team-beta-restore` | `team-beta-db-owners` | Team Beta database restores |
| `team-gamma-restore` | `team-gamma-db-owners` | Team Gamma database restores |

Environment settings:
- **Required reviewers**: The team's db-owners group
- **Wait timer**: Optional delay before deployment can proceed
- **Deployment branches**: Limit to `main` only

#### 4.2.3 Repository Secrets

| Secret | Scope | Description |
|--------|-------|-------------|
| `SQL_RESTORE_USERNAME` | Repository | Service account username |
| `SQL_RESTORE_PASSWORD` | Repository | Service account password |
| `SLACK_WEBHOOK_URL` | Repository | Slack notification webhook |
| `TEAMS_WEBHOOK_URL` | Repository | MS Teams notification webhook |

#### 4.2.4 Repository Variables

| Variable | Scope | Example | Description |
|----------|-------|---------|-------------|
| `ALLOWED_SOURCE_SERVERS` | Repository | `prod-sql01,prod-sql02` | Allowed production servers |
| `ALLOWED_DEST_SERVERS` | Repository | `dev-sql01,dev-sql02,test-sql01` | Allowed destination servers |
| `BACKUP_STORAGE_PATH` | Repository | `\\backup-server\sqlbackups` | Backup location |

---

## 5. Workflow Implementation

### 5.1 Main Workflow File

```yaml
# .github/workflows/database-restore.yml
name: Database Restore Request

on:
  workflow_dispatch:
    inputs:
      team:
        description: 'Team requesting the restore'
        required: true
        type: choice
        options:
          - team-alpha
          - team-beta
          - team-gamma
      database_name:
        description: 'Name of the database to restore'
        required: true
        type: string
      source_server:
        description: 'Source SQL Server (production)'
        required: true
        type: choice
        options:
          - prod-sql01
          - prod-sql02
      destination_server:
        description: 'Destination SQL Server (development)'
        required: true
        type: choice
        options:
          - dev-sql01
          - dev-sql02
          - test-sql01
      point_in_time:
        description: 'Point-in-time recovery (ISO 8601 format, e.g., 2026-01-22T14:30:00)'
        required: false
        type: string
        default: 'latest'
      scheduled_start:
        description: 'When to start restore (ISO 8601 format, or "now")'
        required: true
        type: string
        default: 'now'
      post_restore_script:
        description: 'Post-restore script to run (path in repo)'
        required: false
        type: string
        default: 'scripts/post-restore/default.sql'
      justification:
        description: 'Business justification for the restore'
        required: true
        type: string

env:
  RESTORE_REQUEST_ID: ${{ github.run_id }}-${{ github.run_number }}

jobs:
  # ==========================================================================
  # Job 1: Validate Request and Notify Team
  # ==========================================================================
  validate-and-notify:
    runs-on: ubuntu-latest
    outputs:
      environment: ${{ steps.set-env.outputs.environment }}
      is_valid: ${{ steps.validate.outputs.is_valid }}

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set target environment
        id: set-env
        run: |
          echo "environment=${{ inputs.team }}-restore" >> $GITHUB_OUTPUT

      - name: Validate inputs
        id: validate
        run: |
          # Validate database name format
          if [[ ! "${{ inputs.database_name }}" =~ ^[a-zA-Z][a-zA-Z0-9_]{0,127}$ ]]; then
            echo "::error::Invalid database name format"
            exit 1
          fi

          # Validate point-in-time format if provided
          if [[ "${{ inputs.point_in_time }}" != "latest" ]]; then
            if ! date -d "${{ inputs.point_in_time }}" &>/dev/null; then
              echo "::error::Invalid point-in-time format. Use ISO 8601."
              exit 1
            fi
          fi

          # Validate scheduled start
          if [[ "${{ inputs.scheduled_start }}" != "now" ]]; then
            if ! date -d "${{ inputs.scheduled_start }}" &>/dev/null; then
              echo "::error::Invalid scheduled_start format. Use ISO 8601 or 'now'."
              exit 1
            fi
          fi

          echo "is_valid=true" >> $GITHUB_OUTPUT

      - name: Send request notification to team
        uses: slackapi/slack-github-action@v1
        with:
          webhook: ${{ secrets.SLACK_WEBHOOK_URL }}
          webhook-type: incoming-webhook
          payload: |
            {
              "blocks": [
                {
                  "type": "header",
                  "text": {
                    "type": "plain_text",
                    "text": "🔄 Database Restore Request #${{ env.RESTORE_REQUEST_ID }}"
                  }
                },
                {
                  "type": "section",
                  "fields": [
                    { "type": "mrkdwn", "text": "*Team:*\n${{ inputs.team }}" },
                    { "type": "mrkdwn", "text": "*Requestor:*\n${{ github.actor }}" },
                    { "type": "mrkdwn", "text": "*Database:*\n${{ inputs.database_name }}" },
                    { "type": "mrkdwn", "text": "*Source:*\n${{ inputs.source_server }}" },
                    { "type": "mrkdwn", "text": "*Destination:*\n${{ inputs.destination_server }}" },
                    { "type": "mrkdwn", "text": "*Point-in-Time:*\n${{ inputs.point_in_time }}" }
                  ]
                },
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Justification:*\n${{ inputs.justification }}"
                  }
                },
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "⏳ *Awaiting approval from ${{ inputs.team }}-db-owners*\n<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View and Approve Request>"
                  }
                }
              ]
            }

  # ==========================================================================
  # Job 2: Wait for Approval (Environment Protection Rules)
  # ==========================================================================
  approval-gate:
    needs: validate-and-notify
    runs-on: ubuntu-latest
    environment: ${{ needs.validate-and-notify.outputs.environment }}

    steps:
      - name: Approval received
        run: |
          echo "✅ Restore request approved by environment reviewers"
          echo "Proceeding with restore operation..."

      - name: Send approval notification
        uses: slackapi/slack-github-action@v1
        with:
          webhook: ${{ secrets.SLACK_WEBHOOK_URL }}
          webhook-type: incoming-webhook
          payload: |
            {
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "✅ *Database Restore Request #${{ env.RESTORE_REQUEST_ID }} APPROVED*\nDatabase `${{ inputs.database_name }}` restore has been approved and will begin shortly."
                  }
                }
              ]
            }

  # ==========================================================================
  # Job 3: Wait for Scheduled Time (if applicable)
  # ==========================================================================
  wait-for-schedule:
    needs: approval-gate
    runs-on: ubuntu-latest
    if: ${{ inputs.scheduled_start != 'now' }}

    steps:
      - name: Wait until scheduled time
        run: |
          SCHEDULED=$(date -d "${{ inputs.scheduled_start }}" +%s)
          NOW=$(date +%s)
          WAIT_SECONDS=$((SCHEDULED - NOW))

          if [ $WAIT_SECONDS -gt 0 ]; then
            echo "Waiting $WAIT_SECONDS seconds until scheduled start time..."
            # GitHub Actions has a 6-hour job limit, so for longer waits
            # consider using a scheduled workflow or external scheduler
            if [ $WAIT_SECONDS -gt 21000 ]; then
              echo "::warning::Wait time exceeds safe limit. Consider using scheduled workflows."
            fi
            sleep $WAIT_SECONDS
          else
            echo "Scheduled time has passed, proceeding immediately."
          fi

  # ==========================================================================
  # Job 4: Execute Database Restore
  # ==========================================================================
  execute-restore:
    needs: [approval-gate, wait-for-schedule]
    if: always() && needs.approval-gate.result == 'success'
    runs-on: [self-hosted, sql-restore]  # Must run on self-hosted runner with SQL access
    timeout-minutes: 360  # 6-hour timeout for large databases

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Send restore started notification
        uses: slackapi/slack-github-action@v1
        with:
          webhook: ${{ secrets.SLACK_WEBHOOK_URL }}
          webhook-type: incoming-webhook
          payload: |
            {
              "text": "🚀 Database restore #${{ env.RESTORE_REQUEST_ID }} has STARTED for `${{ inputs.database_name }}`"
            }

      - name: Execute SQL Server Restore
        id: restore
        shell: pwsh
        env:
          SQL_USERNAME: ${{ secrets.SQL_RESTORE_USERNAME }}
          SQL_PASSWORD: ${{ secrets.SQL_RESTORE_PASSWORD }}
        run: |
          $ErrorActionPreference = 'Stop'

          # Parameters
          $params = @{
              DatabaseName      = '${{ inputs.database_name }}'
              SourceServer      = '${{ inputs.source_server }}'
              DestinationServer = '${{ inputs.destination_server }}'
              PointInTime       = '${{ inputs.point_in_time }}'
              BackupPath        = '${{ vars.BACKUP_STORAGE_PATH }}'
          }

          Write-Host "Starting restore operation with parameters:"
          $params | Format-Table -AutoSize

          # Import restore module (assumes you have this in your repo)
          Import-Module ./PowerShell/Modules/GDS.MSSQL.Restore/GDS.MSSQL.Restore.psd1

          # Execute restore
          try {
              $result = Invoke-DatabaseRestore @params -Credential (
                  New-Object PSCredential($env:SQL_USERNAME, (ConvertTo-SecureString $env:SQL_PASSWORD -AsPlainText -Force))
              )

              Write-Host "Restore completed successfully"
              "restore_status=success" >> $env:GITHUB_OUTPUT
              "restore_duration=$($result.Duration)" >> $env:GITHUB_OUTPUT
          }
          catch {
              Write-Error "Restore failed: $_"
              "restore_status=failed" >> $env:GITHUB_OUTPUT
              "restore_error=$($_.Exception.Message)" >> $env:GITHUB_OUTPUT
              exit 1
          }

      - name: Run post-restore scripts
        if: steps.restore.outputs.restore_status == 'success'
        shell: pwsh
        env:
          SQL_USERNAME: ${{ secrets.SQL_RESTORE_USERNAME }}
          SQL_PASSWORD: ${{ secrets.SQL_RESTORE_PASSWORD }}
        run: |
          $ErrorActionPreference = 'Stop'

          $scriptPath = '${{ inputs.post_restore_script }}'

          if (Test-Path $scriptPath) {
              Write-Host "Executing post-restore script: $scriptPath"

              $connectionString = "Server=${{ inputs.destination_server }};Database=${{ inputs.database_name }};User Id=$env:SQL_USERNAME;Password=$env:SQL_PASSWORD;TrustServerCertificate=True"

              Invoke-Sqlcmd -ConnectionString $connectionString -InputFile $scriptPath -Verbose

              Write-Host "Post-restore script completed successfully"
          }
          else {
              Write-Host "No post-restore script found at: $scriptPath"
          }

      - name: Send completion notification (Success)
        if: success()
        uses: slackapi/slack-github-action@v1
        with:
          webhook: ${{ secrets.SLACK_WEBHOOK_URL }}
          webhook-type: incoming-webhook
          payload: |
            {
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "✅ *Database Restore #${{ env.RESTORE_REQUEST_ID }} COMPLETED*"
                  }
                },
                {
                  "type": "section",
                  "fields": [
                    { "type": "mrkdwn", "text": "*Database:*\n${{ inputs.database_name }}" },
                    { "type": "mrkdwn", "text": "*Destination:*\n${{ inputs.destination_server }}" },
                    { "type": "mrkdwn", "text": "*Requestor:*\n${{ github.actor }}" },
                    { "type": "mrkdwn", "text": "*Duration:*\n${{ steps.restore.outputs.restore_duration }}" }
                  ]
                },
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Run Details>"
                  }
                }
              ]
            }

      - name: Send completion notification (Failure)
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          webhook: ${{ secrets.SLACK_WEBHOOK_URL }}
          webhook-type: incoming-webhook
          payload: |
            {
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "❌ *Database Restore #${{ env.RESTORE_REQUEST_ID }} FAILED*"
                  }
                },
                {
                  "type": "section",
                  "fields": [
                    { "type": "mrkdwn", "text": "*Database:*\n${{ inputs.database_name }}" },
                    { "type": "mrkdwn", "text": "*Error:*\n${{ steps.restore.outputs.restore_error }}" }
                  ]
                },
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Run Details>"
                  }
                }
              ]
            }
```

---

## 6. Database-Team Mapping

### 6.1 Configuration File Approach

Create a YAML configuration file to map databases to teams:

```yaml
# config/database-ownership.yml
databases:
  # Team Alpha databases
  CustomerDB:
    team: team-alpha
    allowed_destinations:
      - dev-sql01
      - test-sql01
    post_restore_script: scripts/post-restore/customer-db.sql

  OrdersDB:
    team: team-alpha
    allowed_destinations:
      - dev-sql01
    post_restore_script: scripts/post-restore/orders-db.sql

  # Team Beta databases
  InventoryDB:
    team: team-beta
    allowed_destinations:
      - dev-sql02
    post_restore_script: scripts/post-restore/inventory-db.sql

  ShippingDB:
    team: team-beta
    allowed_destinations:
      - dev-sql02
      - test-sql02
    post_restore_script: scripts/post-restore/shipping-db.sql

  # Team Gamma databases
  AnalyticsDB:
    team: team-gamma
    allowed_destinations:
      - dev-sql01
      - dev-sql02
    max_restore_size_gb: 500
    post_restore_script: scripts/post-restore/analytics-db.sql
```

### 6.2 Validation Step Enhancement

Add this validation to the workflow:

```yaml
      - name: Validate database ownership
        id: validate-ownership
        run: |
          # Read ownership config
          TEAM=$(yq '.databases.${{ inputs.database_name }}.team' config/database-ownership.yml)

          if [ "$TEAM" != "${{ inputs.team }}" ]; then
            echo "::error::Database '${{ inputs.database_name }}' is owned by '$TEAM', not '${{ inputs.team }}'"
            exit 1
          fi

          # Validate destination is allowed
          ALLOWED=$(yq '.databases.${{ inputs.database_name }}.allowed_destinations[]' config/database-ownership.yml | grep -c "${{ inputs.destination_server }}" || true)

          if [ "$ALLOWED" -eq 0 ]; then
            echo "::error::Destination '${{ inputs.destination_server }}' is not allowed for this database"
            exit 1
          fi

          echo "✅ Ownership and destination validated"
```

---

## 7. Alternative: Issue-Based Workflow

For better UX, consider using GitHub Issues as the request mechanism:

### 7.1 Issue Template

```yaml
# .github/ISSUE_TEMPLATE/database-restore-request.yml
name: Database Restore Request
description: Request a database restore from production to development
title: "[DB-RESTORE] "
labels: ["database-restore", "pending-approval"]
assignees: []

body:
  - type: dropdown
    id: team
    attributes:
      label: Team
      description: Which team owns this database?
      options:
        - team-alpha
        - team-beta
        - team-gamma
    validations:
      required: true

  - type: input
    id: database
    attributes:
      label: Database Name
      description: Name of the database to restore
      placeholder: CustomerDB
    validations:
      required: true

  - type: dropdown
    id: source
    attributes:
      label: Source Server
      options:
        - prod-sql01
        - prod-sql02
    validations:
      required: true

  - type: dropdown
    id: destination
    attributes:
      label: Destination Server
      options:
        - dev-sql01
        - dev-sql02
        - test-sql01
    validations:
      required: true

  - type: input
    id: point-in-time
    attributes:
      label: Point-in-Time Recovery
      description: ISO 8601 format or 'latest'
      placeholder: "2026-01-22T14:30:00 or latest"
      value: latest
    validations:
      required: true

  - type: input
    id: scheduled-start
    attributes:
      label: Scheduled Start Time
      description: When should the restore begin?
      placeholder: "2026-01-22T18:00:00 or now"
      value: now
    validations:
      required: true

  - type: textarea
    id: justification
    attributes:
      label: Business Justification
      description: Why do you need this restore?
    validations:
      required: true
```

### 7.2 Issue-Triggered Workflow

```yaml
# .github/workflows/database-restore-issue.yml
name: Database Restore (Issue-Based)

on:
  issue_comment:
    types: [created]

jobs:
  process-approval:
    if: |
      contains(github.event.issue.labels.*.name, 'database-restore') &&
      contains(github.event.comment.body, '/approve-restore')
    runs-on: ubuntu-latest

    steps:
      - name: Check approver authorization
        uses: actions/github-script@v7
        with:
          script: |
            // Parse issue body for team
            const issueBody = context.payload.issue.body;
            const teamMatch = issueBody.match(/Team:\s*(\S+)/);
            const team = teamMatch ? teamMatch[1] : null;

            // Check if commenter is in the team's db-owners group
            const approver = context.payload.comment.user.login;

            const { data: membership } = await github.rest.teams.getMembershipForUserInOrg({
              org: context.repo.owner,
              team_slug: `${team}-db-owners`,
              username: approver
            }).catch(() => ({ data: null }));

            if (!membership || membership.state !== 'active') {
              core.setFailed(`User ${approver} is not authorized to approve ${team} restores`);
              return;
            }

            core.info(`Approval verified from ${approver}`);

      - name: Trigger restore workflow
        uses: actions/github-script@v7
        with:
          script: |
            // Parse issue body and trigger the main restore workflow
            await github.rest.actions.createWorkflowDispatch({
              owner: context.repo.owner,
              repo: context.repo.repo,
              workflow_id: 'database-restore.yml',
              ref: 'main',
              inputs: {
                // ... parsed inputs from issue body
              }
            });
```

---

## 8. Security Considerations

### 8.1 Access Control Matrix

| Role | Can Request | Can Approve | Can View Logs |
|------|-------------|-------------|---------------|
| Team Developer | Own team's DBs | No | Own team's runs |
| Team DB Owner | Own team's DBs | Own team's DBs | Own team's runs |
| DBA Admin | Any DB | Any DB | All runs |
| Repository Admin | Any DB | Any DB | All runs |

### 8.2 Secret Management

```yaml
# Use GitHub's built-in secrets encryption
# Consider using OIDC for cloud credential federation

- name: Configure Azure credentials (OIDC)
  uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

### 8.3 Network Security

- Self-hosted runners MUST be on a network with access to SQL Servers
- Use private networking (VNet/VPC) for runner-to-database communication
- SQL credentials should use least-privilege accounts
- Consider Just-In-Time (JIT) access for restore operations

### 8.4 Data Protection

```yaml
# Post-restore script should include data masking
# scripts/post-restore/default.sql

-- Mask PII in development environments
UPDATE Customers SET
    Email = CONCAT('user', CustomerID, '@example.com'),
    Phone = '555-000-0000',
    SSN = 'XXX-XX-XXXX'
WHERE 1=1;

-- Remove payment information
TRUNCATE TABLE PaymentMethods;

-- Reset passwords
UPDATE Users SET PasswordHash = 'RESET_REQUIRED';

PRINT 'Data masking completed';
```

---

## 9. Monitoring and Observability

### 9.1 Workflow Run Summary

```yaml
      - name: Generate run summary
        if: always()
        run: |
          cat >> $GITHUB_STEP_SUMMARY << 'EOF'
          ## Database Restore Summary

          | Parameter | Value |
          |-----------|-------|
          | Request ID | ${{ env.RESTORE_REQUEST_ID }} |
          | Database | ${{ inputs.database_name }} |
          | Source | ${{ inputs.source_server }} |
          | Destination | ${{ inputs.destination_server }} |
          | Point-in-Time | ${{ inputs.point_in_time }} |
          | Requestor | ${{ github.actor }} |
          | Status | ${{ job.status }} |

          EOF
```

### 9.2 Audit Log Export

Consider exporting workflow runs to your SIEM:

```yaml
      - name: Send audit event
        run: |
          curl -X POST "${{ secrets.AUDIT_ENDPOINT }}" \
            -H "Content-Type: application/json" \
            -d '{
              "event_type": "database_restore",
              "request_id": "${{ env.RESTORE_REQUEST_ID }}",
              "database": "${{ inputs.database_name }}",
              "requestor": "${{ github.actor }}",
              "status": "${{ job.status }}",
              "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
            }'
```

---

## 10. Implementation Checklist

### Phase 1: Foundation
- [ ] Create GitHub Teams for each database ownership group
- [ ] Configure GitHub Environments with protection rules
- [ ] Set up self-hosted runner with SQL Server access
- [ ] Configure repository secrets and variables
- [ ] Create basic workflow file

### Phase 2: Core Functionality
- [ ] Implement database restore PowerShell module
- [ ] Create post-restore script templates
- [ ] Add notification integrations (Slack/Teams)
- [ ] Test end-to-end with one team

### Phase 3: Multi-Team Rollout
- [ ] Create database-ownership.yml configuration
- [ ] Add ownership validation to workflow
- [ ] Onboard additional teams
- [ ] Create documentation for requestors

### Phase 4: Enhancements
- [ ] Add issue-based request option
- [ ] Implement scheduled restore queue
- [ ] Add restore size estimation
- [ ] Create dashboard for restore history

---

## 11. FAQ

**Q: What if a restore takes longer than 6 hours?**
A: GitHub Actions jobs have a 6-hour limit. For very large databases, consider:
- Using Azure DevOps (72-hour limit) for the actual restore step
- Breaking into multiple steps with artifacts
- Running the restore outside GitHub and using Actions for orchestration only

**Q: Can we restrict which databases can be restored?**
A: Yes, use the `database-ownership.yml` file to explicitly list allowed databases and validate in the workflow.

**Q: What about restore to production?**
A: This workflow is specifically for prod-to-dev restores. Production restores should have a separate, more restrictive workflow with additional approvals (change management, etc.).

**Q: How do we handle backup storage authentication?**
A: For Azure Blob: Use OIDC federation. For network shares: Use service account credentials stored in secrets. For S3: Use IAM roles with OIDC.

---

## 12. Self-Hosted Runner Architecture

### 12.1 Runner Concurrency

**Each runner processes ONE job at a time.** When a runner is executing a restore, it cannot pick up another job.

### 12.2 Recommended Architecture

| Configuration | Runners | Use Case |
|---------------|---------|----------|
| **Minimum** | 2 runners | Basic availability, handles 1 concurrent restore + 1 queued |
| **Recommended** | 3-4 runners | Handles typical workload with buffer for peak times |
| **High Volume** | 5+ runners | Many teams, frequent restores |

### 12.3 Dedicated vs Shared Runners

| Aspect | Dedicated Restore Runners | Shared Runners |
|--------|---------------------------|----------------|
| **Isolation** | Full - only run restore jobs | May compete with other workflows |
| **Cost** | Higher (dedicated VMs) | Lower (shared resources) |
| **Availability** | Guaranteed for restores | May be busy with other jobs |
| **Recommendation** | **Recommended for production** | OK for low-volume environments |

**Recommendation: Use dedicated runners with a specific label (e.g., `sql-restore`)**

```yaml
# Workflow targets only restore-capable runners
runs-on: [self-hosted, sql-restore]
```

### 12.4 Runner Sizing

| Database Size | Runner Specs | Notes |
|---------------|--------------|-------|
| < 100 GB | 4 CPU, 8 GB RAM | Standard Windows Server |
| 100-500 GB | 8 CPU, 16 GB RAM | More I/O bandwidth helpful |
| 500+ GB | 8+ CPU, 32 GB RAM | Consider dedicated storage network |

The runner doesn't do the heavy lifting - it just calls your existing restore process. The SQL Server does the work.

### 12.5 Runner Setup Script

```powershell
# setup-runner.ps1 - Run on Windows Server

# 1. Download runner
$runnerVersion = "2.320.0"  # Check latest at github.com/actions/runner
$url = "https://github.com/actions/runner/releases/download/v$runnerVersion/actions-runner-win-x64-$runnerVersion.zip"
Invoke-WebRequest -Uri $url -OutFile runner.zip
Expand-Archive -Path runner.zip -DestinationPath C:\actions-runner

# 2. Configure runner (get token from GitHub Settings > Actions > Runners)
cd C:\actions-runner
.\config.cmd --url https://github.com/YOUR_ORG/YOUR_REPO `
             --token YOUR_TOKEN `
             --name "sql-restore-runner-01" `
             --labels "self-hosted,sql-restore,windows" `
             --work "_work" `
             --runasservice

# 3. Install required PowerShell modules
Install-Module -Name SqlServer -Force -AllowClobber
Install-Module -Name dbatools -Force -AllowClobber  # Optional but excellent

# 4. Verify network access
Test-NetConnection -ComputerName prod-sql01 -Port 1433
Test-NetConnection -ComputerName dev-sql01 -Port 1433
Test-Path "\\backup-server\sqlbackups"
```

---

## 13. SQL Server Restore Status Monitoring

### 13.1 Status Query

Use this query to check restore progress and estimated completion time:

```sql
-- Query to monitor active restore operations
SELECT
    r.session_id AS SPID,
    r.command,
    r.status,
    r.start_time,
    r.percent_complete,
    CAST(r.percent_complete AS DECIMAL(5,2)) AS [Percent Complete],
    DATEADD(SECOND, r.estimated_completion_time / 1000, GETDATE()) AS [Estimated Completion],
    CAST(r.total_elapsed_time / 1000.0 / 60.0 AS DECIMAL(10,2)) AS [Elapsed Minutes],
    CAST(r.estimated_completion_time / 1000.0 / 60.0 AS DECIMAL(10,2)) AS [Remaining Minutes],
    DB_NAME(r.database_id) AS [Database],
    t.text AS [SQL Command]
FROM sys.dm_exec_requests r
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t
WHERE r.command IN ('RESTORE DATABASE', 'RESTORE LOG', 'RESTORE HEADERONLY', 'RESTORE FILELISTONLY')
ORDER BY r.start_time DESC;
```

### 13.2 Simplified Status Check (for automation)

```sql
-- Returns: RUNNING, COMPLETED, or NOT_FOUND
-- Used by the polling workflow
DECLARE @DatabaseName NVARCHAR(128) = 'CustomerDB';
DECLARE @DestinationServer NVARCHAR(128) = 'dev-sql01';

SELECT
    CASE
        WHEN EXISTS (
            SELECT 1 FROM sys.dm_exec_requests
            WHERE command LIKE 'RESTORE%'
            AND database_id = DB_ID(@DatabaseName)
        ) THEN 'RUNNING'
        WHEN EXISTS (
            SELECT 1 FROM sys.databases
            WHERE name = @DatabaseName
            AND state = 0  -- ONLINE
        ) THEN 'COMPLETED'
        ELSE 'NOT_FOUND'
    END AS restore_status,
    (
        SELECT percent_complete
        FROM sys.dm_exec_requests
        WHERE command LIKE 'RESTORE%'
        AND database_id = DB_ID(@DatabaseName)
    ) AS percent_complete,
    (
        SELECT DATEADD(SECOND, estimated_completion_time / 1000, GETDATE())
        FROM sys.dm_exec_requests
        WHERE command LIKE 'RESTORE%'
        AND database_id = DB_ID(@DatabaseName)
    ) AS estimated_completion;
```

### 13.3 Important Notes on Status Monitoring

| Phase | Percent Complete Shows | Notes |
|-------|----------------------|-------|
| **Data Copy** | 0-100% accurately | Main restore phase |
| **Redo Phase** | Stuck at ~99-100% | Replaying transaction logs |
| **Undo Phase** | Stuck at 100% | Rolling back uncommitted transactions |
| **Recovery** | Not visible | Can take hours for large DBs |

**Warning:** A restore showing 100% may still be running the recovery phase. Always verify the database is ONLINE before declaring complete.

---

## 14. Async Polling Pattern for Long Restores

For restores exceeding 6 hours, use a "fire and forget" pattern with status polling.

### 14.1 Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                     ASYNC RESTORE PATTERN                                  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Workflow 1: database-restore.yml                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────────────────────┐  │
│  │   Approve    │───▶│   Start      │───▶│  Exit (restore running)     │  │
│  │              │    │   Restore    │    │  Save tracking info         │  │
│  └──────────────┘    └──────────────┘    └─────────────────────────────┘  │
│                                                    │                       │
│                                                    ▼                       │
│                                          ┌─────────────────┐               │
│                                          │  tracking.json  │               │
│                                          │  (artifact)     │               │
│                                          └─────────────────┘               │
│                                                    │                       │
│  Workflow 2: restore-monitor.yml (runs every 5 min)                        │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────────────────────┐  │
│  │   Load       │───▶│   Check      │───▶│  If complete: notify + post │  │
│  │   Tracking   │    │   Status     │    │  If running: continue       │  │
│  └──────────────┘    └──────────────┘    └─────────────────────────────┘  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### 14.2 Main Restore Workflow (Fire and Forget)

```yaml
# .github/workflows/database-restore-async.yml
name: Database Restore (Async)

on:
  workflow_dispatch:
    inputs:
      team:
        description: 'Team'
        required: true
        type: choice
        options: [team-alpha, team-beta, team-gamma]
      database_name:
        description: 'Database name'
        required: true
        type: string
      source_server:
        description: 'Source server'
        required: true
        type: string
      destination_server:
        description: 'Destination server'
        required: true
        type: string
      point_in_time:
        description: 'Point-in-time (ISO 8601 or latest)'
        default: 'latest'
        type: string

jobs:
  validate-and-approve:
    runs-on: ubuntu-latest
    environment: ${{ inputs.team }}-restore
    steps:
      - run: echo "Approved"

  start-restore:
    needs: validate-and-approve
    runs-on: [self-hosted, sql-restore]

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Start restore process (async)
        id: start
        shell: pwsh
        run: |
          # Call your existing restore process
          # This should START the restore and return immediately
          # The restore runs as a SQL Server job or background process

          $params = @{
              DatabaseName = '${{ inputs.database_name }}'
              SourceServer = '${{ inputs.source_server }}'
              DestinationServer = '${{ inputs.destination_server }}'
              PointInTime = '${{ inputs.point_in_time }}'
              BackupPath = '${{ vars.BACKUP_STORAGE_PATH }}'
              Async = $true  # Important: don't wait for completion
          }

          # Example: Start restore via SQL Agent job
          $result = Start-DatabaseRestoreJob @params

          # Output tracking info
          "job_id=$($result.JobId)" >> $env:GITHUB_OUTPUT
          "start_time=$(Get-Date -Format 'o')" >> $env:GITHUB_OUTPUT

      - name: Save tracking information
        shell: pwsh
        run: |
          $tracking = @{
              run_id = '${{ github.run_id }}'
              database_name = '${{ inputs.database_name }}'
              destination_server = '${{ inputs.destination_server }}'
              team = '${{ inputs.team }}'
              requestor = '${{ github.actor }}'
              job_id = '${{ steps.start.outputs.job_id }}'
              start_time = '${{ steps.start.outputs.start_time }}'
              status = 'RUNNING'
              point_in_time = '${{ inputs.point_in_time }}'
              post_restore_script = 'scripts/post-restore/default.sql'
          }

          # Save to a known location that the monitor can read
          $trackingPath = "tracking/${{ github.run_id }}.json"
          New-Item -ItemType Directory -Path "tracking" -Force | Out-Null
          $tracking | ConvertTo-Json | Set-Content $trackingPath

          # Commit to repo (or use artifact/external storage)
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add $trackingPath
          git commit -m "Add restore tracking for ${{ inputs.database_name }}"
          git push

      - name: Send started notification
        uses: aliencube/microsoft-teams-actions@v0.8.0
        with:
          webhook_uri: ${{ secrets.TEAMS_WEBHOOK_URL }}
          title: "Database Restore Started"
          summary: "Restore of ${{ inputs.database_name }} has started"
          text: |
            **Database Restore Started**

            | Field | Value |
            |-------|-------|
            | Database | ${{ inputs.database_name }} |
            | Destination | ${{ inputs.destination_server }} |
            | Requestor | ${{ github.actor }} |
            | Team | ${{ inputs.team }} |
            | Point-in-Time | ${{ inputs.point_in_time }} |

            The restore is running. You will be notified when complete.
```

### 14.3 Monitor Workflow (Scheduled Polling)

```yaml
# .github/workflows/restore-monitor.yml
name: Restore Monitor

on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes
  workflow_dispatch:  # Allow manual trigger

jobs:
  check-active-restores:
    runs-on: [self-hosted, sql-restore]

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Pull latest tracking files
        run: git pull origin main

      - name: Check restore status for all active restores
        id: check
        shell: pwsh
        env:
          SQL_USERNAME: ${{ secrets.SQL_RESTORE_USERNAME }}
          SQL_PASSWORD: ${{ secrets.SQL_RESTORE_PASSWORD }}
        run: |
          $trackingFiles = Get-ChildItem -Path "tracking/*.json" -ErrorAction SilentlyContinue

          if (-not $trackingFiles) {
              Write-Host "No active restores to monitor"
              exit 0
          }

          foreach ($file in $trackingFiles) {
              $tracking = Get-Content $file.FullName | ConvertFrom-Json

              if ($tracking.status -ne 'RUNNING') {
                  continue
              }

              Write-Host "Checking restore: $($tracking.database_name) on $($tracking.destination_server)"

              # Query restore status
              $statusQuery = @"
              SELECT
                  CASE
                      WHEN EXISTS (
                          SELECT 1 FROM sys.dm_exec_requests
                          WHERE command LIKE 'RESTORE%'
                      ) THEN 'RUNNING'
                      WHEN EXISTS (
                          SELECT 1 FROM sys.databases
                          WHERE name = '$($tracking.database_name)'
                          AND state = 0
                      ) THEN 'COMPLETED'
                      ELSE 'UNKNOWN'
                  END AS status,
                  (
                      SELECT percent_complete
                      FROM sys.dm_exec_requests
                      WHERE command LIKE 'RESTORE%'
                  ) AS percent_complete,
                  (
                      SELECT DATEADD(SECOND, estimated_completion_time / 1000, GETDATE())
                      FROM sys.dm_exec_requests
                      WHERE command LIKE 'RESTORE%'
                  ) AS estimated_completion
"@

              $cred = New-Object PSCredential($env:SQL_USERNAME, (ConvertTo-SecureString $env:SQL_PASSWORD -AsPlainText -Force))
              $result = Invoke-Sqlcmd -ServerInstance $tracking.destination_server -Query $statusQuery -Credential $cred

              Write-Host "Status: $($result.status), Progress: $($result.percent_complete)%"

              if ($result.status -eq 'COMPLETED') {
                  Write-Host "Restore completed! Running post-restore scripts..."

                  # Run post-restore script
                  if (Test-Path $tracking.post_restore_script) {
                      Invoke-Sqlcmd -ServerInstance $tracking.destination_server `
                                    -Database $tracking.database_name `
                                    -InputFile $tracking.post_restore_script `
                                    -Credential $cred
                  }

                  # Update tracking file
                  $tracking.status = 'COMPLETED'
                  $tracking.completed_time = (Get-Date -Format 'o')
                  $tracking | ConvertTo-Json | Set-Content $file.FullName

                  # Output for notification step
                  "completed_$($tracking.run_id)=true" >> $env:GITHUB_OUTPUT
                  "database_$($tracking.run_id)=$($tracking.database_name)" >> $env:GITHUB_OUTPUT
                  "team_$($tracking.run_id)=$($tracking.team)" >> $env:GITHUB_OUTPUT
                  "requestor_$($tracking.run_id)=$($tracking.requestor)" >> $env:GITHUB_OUTPUT
              }
              elseif ($result.status -eq 'RUNNING') {
                  Write-Host "Still running... ETA: $($result.estimated_completion)"
                  # Optionally send progress notification every N checks
              }
              else {
                  Write-Host "::warning::Unknown status for $($tracking.database_name)"
              }
          }

      - name: Commit tracking updates
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add tracking/*.json
          git diff --staged --quiet || git commit -m "Update restore tracking status"
          git push

      - name: Send completion notifications
        if: contains(steps.check.outputs.*, 'completed_')
        uses: aliencube/microsoft-teams-actions@v0.8.0
        with:
          webhook_uri: ${{ secrets.TEAMS_WEBHOOK_URL }}
          title: "Database Restore Completed"
          summary: "Database restore has completed successfully"
          theme_color: "00FF00"
          text: |
            **Database Restore Completed Successfully**

            The database has been restored and post-restore scripts have been executed.

            Check the workflow run for details.
```

### 14.4 Alternative: Status Tracking via Repository Dispatch

Instead of polling, the restore process can trigger completion:

```yaml
# When restore completes (called from SQL Agent job or your restore script)
# POST https://api.github.com/repos/{owner}/{repo}/dispatches
# {
#   "event_type": "restore_completed",
#   "client_payload": {
#     "database_name": "CustomerDB",
#     "destination_server": "dev-sql01",
#     "run_id": "12345",
#     "status": "success"
#   }
# }
```

```yaml
# .github/workflows/restore-completed.yml
name: Restore Completed Handler

on:
  repository_dispatch:
    types: [restore_completed]

jobs:
  handle-completion:
    runs-on: [self-hosted, sql-restore]
    steps:
      - name: Run post-restore scripts
        # ... post-restore logic

      - name: Send notification
        # ... Teams notification
```

---

## 15. Microsoft Teams Notifications

### 15.1 Teams Webhook Setup

1. In MS Teams, go to the channel > Connectors > Incoming Webhook
2. Create webhook and copy the URL
3. Store URL in GitHub Secrets as `TEAMS_WEBHOOK_URL`

### 15.2 Notification Templates

#### Request Submitted

```yaml
      - name: Notify Teams - Request Submitted
        shell: pwsh
        run: |
          $body = @{
              "@type" = "MessageCard"
              "@context" = "http://schema.org/extensions"
              "themeColor" = "0076D7"
              "summary" = "Database Restore Request"
              "sections" = @(
                  @{
                      "activityTitle" = "Database Restore Request #${{ github.run_id }}"
                      "activitySubtitle" = "Submitted by ${{ github.actor }}"
                      "activityImage" = "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
                      "facts" = @(
                          @{ "name" = "Database"; "value" = "${{ inputs.database_name }}" }
                          @{ "name" = "Source"; "value" = "${{ inputs.source_server }}" }
                          @{ "name" = "Destination"; "value" = "${{ inputs.destination_server }}" }
                          @{ "name" = "Team"; "value" = "${{ inputs.team }}" }
                          @{ "name" = "Point-in-Time"; "value" = "${{ inputs.point_in_time }}" }
                      )
                      "markdown" = $true
                  }
              )
              "potentialAction" = @(
                  @{
                      "@type" = "OpenUri"
                      "name" = "View & Approve Request"
                      "targets" = @(
                          @{ "os" = "default"; "uri" = "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}" }
                      )
                  }
              )
          } | ConvertTo-Json -Depth 10

          Invoke-RestMethod -Uri "${{ secrets.TEAMS_WEBHOOK_URL }}" -Method Post -Body $body -ContentType "application/json"

      # Alternative using the Teams action
      - name: Notify Teams - Using Action
        uses: jdcargile/ms-teams-notification@v1.4
        with:
          github-token: ${{ github.token }}
          ms-teams-webhook-uri: ${{ secrets.TEAMS_WEBHOOK_URL }}
          notification-summary: "Database Restore Request for ${{ inputs.database_name }}"
          notification-color: "0076D7"
          timezone: America/New_York
```

#### Request Approved

```yaml
      - name: Notify Teams - Approved
        shell: pwsh
        run: |
          $body = @{
              "@type" = "MessageCard"
              "@context" = "http://schema.org/extensions"
              "themeColor" = "28A745"  # Green
              "summary" = "Restore Approved"
              "sections" = @(
                  @{
                      "activityTitle" = "✅ Database Restore APPROVED"
                      "activitySubtitle" = "${{ inputs.database_name }} → ${{ inputs.destination_server }}"
                      "text" = "The restore will begin shortly."
                      "markdown" = $true
                  }
              )
          } | ConvertTo-Json -Depth 10

          Invoke-RestMethod -Uri "${{ secrets.TEAMS_WEBHOOK_URL }}" -Method Post -Body $body -ContentType "application/json"
```

#### Restore Completed

```yaml
      - name: Notify Teams - Completed
        shell: pwsh
        run: |
          $body = @{
              "@type" = "MessageCard"
              "@context" = "http://schema.org/extensions"
              "themeColor" = "28A745"  # Green
              "summary" = "Restore Completed"
              "sections" = @(
                  @{
                      "activityTitle" = "✅ Database Restore COMPLETED"
                      "facts" = @(
                          @{ "name" = "Database"; "value" = "${{ inputs.database_name }}" }
                          @{ "name" = "Server"; "value" = "${{ inputs.destination_server }}" }
                          @{ "name" = "Duration"; "value" = "${{ steps.restore.outputs.duration }}" }
                          @{ "name" = "Requestor"; "value" = "${{ github.actor }}" }
                      )
                      "text" = "Post-restore scripts have been executed. Database is ready for use."
                      "markdown" = $true
                  }
              )
              "potentialAction" = @(
                  @{
                      "@type" = "OpenUri"
                      "name" = "View Run Details"
                      "targets" = @(
                          @{ "os" = "default"; "uri" = "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}" }
                      )
                  }
              )
          } | ConvertTo-Json -Depth 10

          Invoke-RestMethod -Uri "${{ secrets.TEAMS_WEBHOOK_URL }}" -Method Post -Body $body -ContentType "application/json"
```

#### Restore Failed

```yaml
      - name: Notify Teams - Failed
        if: failure()
        shell: pwsh
        run: |
          $body = @{
              "@type" = "MessageCard"
              "@context" = "http://schema.org/extensions"
              "themeColor" = "DC3545"  # Red
              "summary" = "Restore Failed"
              "sections" = @(
                  @{
                      "activityTitle" = "❌ Database Restore FAILED"
                      "facts" = @(
                          @{ "name" = "Database"; "value" = "${{ inputs.database_name }}" }
                          @{ "name" = "Server"; "value" = "${{ inputs.destination_server }}" }
                          @{ "name" = "Error"; "value" = "${{ steps.restore.outputs.error }}" }
                      )
                      "text" = "Please check the workflow run for details."
                      "markdown" = $true
                  }
              )
              "potentialAction" = @(
                  @{
                      "@type" = "OpenUri"
                      "name" = "View Error Details"
                      "targets" = @(
                          @{ "os" = "default"; "uri" = "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}" }
                      )
                  }
              )
          } | ConvertTo-Json -Depth 10

          Invoke-RestMethod -Uri "${{ secrets.TEAMS_WEBHOOK_URL }}" -Method Post -Body $body -ContentType "application/json"
```

### 15.3 Email Notifications (Alternative)

For email notifications, use GitHub's built-in email on workflow failure, or:

```yaml
      - name: Send Email Notification
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: smtp.office365.com
          server_port: 587
          username: ${{ secrets.EMAIL_USERNAME }}
          password: ${{ secrets.EMAIL_PASSWORD }}
          subject: "Database Restore Completed - ${{ inputs.database_name }}"
          to: ${{ inputs.team }}@company.com
          from: noreply@company.com
          body: |
            Database restore has completed.

            Database: ${{ inputs.database_name }}
            Destination: ${{ inputs.destination_server }}
            Requestor: ${{ github.actor }}

            View details: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
```

---

## 16. Appendix

### A. Sample Post-Restore Scripts

See `scripts/post-restore/` directory for examples:
- `default.sql` - Basic data masking
- `customer-db.sql` - Customer database specific
- `reset-integrations.sql` - Reset third-party integration configs

### B. Self-Hosted Runner Setup

```powershell
# Install runner on Windows Server with SQL access
# See: https://docs.github.com/en/actions/hosting-your-own-runners

# Required software:
# - PowerShell 7+
# - SqlServer PowerShell module
# - SQL Server Management Objects (SMO)
# - Network access to SQL Servers and backup storage
```

### C. Environment Protection Rules API

```bash
# Create environment via API
gh api -X PUT repos/{owner}/{repo}/environments/team-alpha-restore \
  -f wait_timer=0 \
  -f reviewers='[{"type":"Team","id":12345}]'
```
