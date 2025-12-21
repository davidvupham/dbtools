# Test Plan: db-cicd

## Overview

This test plan covers unit, integration, and end-to-end testing for the db-cicd platform.

## Test Categories

| Category | Scope | Tools |
|----------|-------|-------|
| Unit | Individual functions | pytest |
| Integration | Component interactions | pytest + test databases |
| E2E | Full workflow | GitHub Actions + test environments |

## Unit Tests

| Component | Test Coverage Target |
|-----------|---------------------|
| Policy Engine | 90% |
| Drift Detector | 85% |
| Log Transformer | 90% |
| Report Generator | 80% |

## Integration Tests

### Policy Engine

- [ ] Parse YAML changelog correctly
- [ ] Parse XML changelog correctly
- [ ] Evaluate rules against changesets
- [ ] Generate HTML report

### Drift Detector

- [ ] Connect to PostgreSQL
- [ ] Connect to SQL Server
- [ ] Generate diff report
- [ ] Detect missing objects
- [ ] Detect unexpected objects

## E2E Test Scenarios

| Scenario | Expected Result |
|----------|-----------------|
| PR with valid changelog | Check passes, PR green |
| PR with DROP TABLE | Check fails, PR blocked |
| Deploy to dev (no approval) | Deploys immediately |
| Deploy to prod (with approval) | Waits for approval |
| Drift detected | Alert sent to Slack |

## Test Environments

| Environment | Purpose | Database |
|-------------|---------|----------|
| test | Unit/integration tests | Docker containers |
| dev | E2E testing | Shared dev databases |

## CI Integration

Tests run automatically on:

- Every PR
- Every push to main
- Nightly (full suite)
