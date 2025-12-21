# Operational Procedures: db-cicd

## Routine Operations

### Daily Drift Check Review

1. Review drift check results in GitHub Actions
2. Investigate any detected drift
3. Either sync changelog or revert unauthorized changes

### Policy Rule Updates

1. Edit `.github/policy-rules.yaml`
2. Test locally: `db-cicd policy check --changelog test.yaml`
3. Submit PR for review
4. Merge to main

## Deployment Procedures

### Standard Deployment

1. Push changelog changes to main
2. Validate workflow runs automatically
3. Approve stage deployment (1 reviewer)
4. Verify stage deployment succeeded
5. Approve prod deployment (2 reviewers)
6. Monitor for errors

### Emergency Deployment

1. Create hotfix branch
2. Add changelog changes
3. Submit PR with "HOTFIX" label
4. Request expedited review
5. Follow standard approval process

## Maintenance

### Quarterly Tasks

- [ ] Review and update policy rules
- [ ] Audit approval logs
- [ ] Update dependencies
- [ ] Review alert thresholds
