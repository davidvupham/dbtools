# Liquibase + GitHub Actions Tutorial Series

## Overview

This tutorial series teaches you how to implement automated database CI/CD using Liquibase and GitHub Actions with Microsoft SQL Server. The tutorials are designed for beginners who have no prior experience with GitHub Actions or CI/CD concepts.

## Learning Path

Follow these tutorials in order for the best learning experience:

### 1. 📚 GitHub Actions Primer (Start Here!)

**File**: [github-actions-primer.md](../../explanation/architecture/database-change-cicd/github-actions-primer.md)
**Duration**: 45 minutes
**Prerequisites**: None

**What you'll learn:**

- What GitHub Actions is and why use it
- Core concepts: workflows, jobs, steps, runners
- Working with secrets
- Environments and protection rules
- Common workflow patterns
- Best practices and troubleshooting

**Who should read this:**

- Anyone new to GitHub Actions
- Developers wanting to understand CI/CD
- Teams implementing automation

**Key takeaway**: Understand GitHub Actions fundamentals before diving into database-specific implementations.

---

### 2. 🔍 Research Findings: Best Practices

**File**: [github-actions-liquibase-best-practices.md](../../best-practices/liquibase/github-actions.md)
**Duration**: 60 minutes
**Prerequisites**: Basic understanding of GitHub Actions

**What you'll learn:**

- Official Liquibase GitHub Actions support
- Industry best practices
- Architecture patterns for CI/CD pipelines
- Security best practices
- SQL Server specific considerations
- Performance optimization
- Error handling strategies

**Who should read this:**

- Teams planning CI/CD implementation
- Architects designing database pipelines
- DevOps engineers
- Security-conscious developers

**Key takeaway**: Learn from industry experience and avoid common pitfalls.

---

### 3. 🚀 Hands-On Tutorial: SQL Server + Liquibase + GitHub Actions

**File**: [sqlserver-liquibase-github-actions-tutorial.md](./archive/sqlserver-liquibase-github-actions-tutorial.md)
**Duration**: 4-5 hours (can be completed over multiple sessions)
**Prerequisites**:

- GitHub account
- SQL Server database (Azure SQL, local, or AWS RDS)
- Basic Git knowledge

**What you'll build:**
A complete CI/CD pipeline that automatically deploys database changes through dev → staging → production with approval gates.

**Tutorial parts:**

1. **Part 1**: Local setup and project structure
2. **Part 2**: GitHub repository setup
3. **Part 3**: Configure secrets
4. **Part 4**: Create your first workflow
5. **Part 5**: Set up environments with protection rules
6. **Part 6**: Multi-environment deployment pipeline
7. **Part 7**: Make real database changes
8. **Part 8**: Advanced workflows (PR validation, manual deployment)
9. **Part 9**: Monitoring and troubleshooting
10. **Part 10**: Production best practices

**Who should complete this:**

- Developers implementing database CI/CD
- Teams transitioning from manual deployments
- Anyone wanting hands-on experience

**Key takeaway**: Build a production-ready CI/CD pipeline from scratch.

---

### 4. ⚖️ Comparison: Local Docker vs GitHub Actions

**File**: [local-vs-github-actions-comparison.md](../../explanation/architecture/database-change-cicd/local-vs-github-actions-comparison.md)
**Duration**: 30 minutes
**Prerequisites**: Understanding of both approaches

**What you'll learn:**

- When to use local Docker development
- When to use GitHub Actions CI/CD
- Detailed feature comparison
- Transition strategy from local to CI/CD
- Hybrid approach recommendations
- Real-world scenarios by company size

**Who should read this:**

- Teams deciding on approach
- Developers wondering "which should I use?"
- Managers planning implementation
- Anyone wanting to understand trade-offs

**Key takeaway**: Make informed decisions about which approach fits your needs.

---

## Quick Start Guide

### If you're brand new to GitHub Actions

1. ✅ Start with [GitHub Actions Primer](../../explanation/architecture/database-change-cicd/github-actions-primer.md) - 45 minutes
2. ✅ Skim [Best Practices](../../best-practices/liquibase/github-actions.md) - 15 minutes
3. ✅ Follow [Hands-On Tutorial](./archive/sqlserver-liquibase-github-actions-tutorial.md) - 4-5 hours
4. ✅ Reference [Comparison Guide](../../explanation/architecture/database-change-cicd/local-vs-github-actions-comparison.md) as needed

**Total time**: 1 day

---

### If you already know GitHub Actions

1. ⏭️ Skip the primer
2. ✅ Review [Best Practices](../../best-practices/liquibase/github-actions.md) - 30 minutes
3. ✅ Complete [Hands-On Tutorial](./archive/sqlserver-liquibase-github-actions-tutorial.md) - 3-4 hours
4. ✅ Reference [Comparison Guide](../../explanation/architecture/database-change-cicd/local-vs-github-actions-comparison.md) for team discussions

**Total time**: Half day

---

### If you're planning team implementation

1. ✅ Read [Comparison Guide](../../explanation/architecture/database-change-cicd/local-vs-github-actions-comparison.md) first - 30 minutes
2. ✅ Review [Best Practices](../../best-practices/liquibase/github-actions.md) - 60 minutes
3. ✅ Complete [Hands-On Tutorial](./archive/sqlserver-liquibase-github-actions-tutorial.md) - 4-5 hours
4. ✅ Share [GitHub Actions Primer](../../explanation/architecture/database-change-cicd/github-actions-primer.md) with team

**Total time**: 1-2 days (individual), 1 week (team)

---

## Tutorial Comparison

| Tutorial | Difficulty | Duration | Hands-On | Prerequisites |
|----------|-----------|----------|----------|---------------|
| GitHub Actions Primer | Beginner | 45 min | No | None |
| Best Practices | Intermediate | 60 min | No | Basic GitHub Actions |
| Hands-On Tutorial | Beginner | 4-5 hours | Yes | GitHub account, SQL Server |
| Comparison Guide | Beginner | 30 min | No | None |

## What You Need

### For Reading/Learning

- ✅ Web browser
- ✅ Text editor (for taking notes)
- ❌ No setup required

### For Hands-On Tutorial

- ✅ GitHub account (free)
- ✅ SQL Server database:
  - Azure SQL Database (free tier available)
  - Local SQL Server (Docker or installed)
  - AWS RDS SQL Server
  - On-premises SQL Server with internet access
- ✅ Git installed locally
- ✅ Text editor (VS Code recommended)
- ✅ Basic Git knowledge (commit, push, pull)

### Optional but Helpful

- Docker Desktop (for local testing)
- SQL Server Management Studio (SSMS) or Azure Data Studio
- Azure account (if using Azure SQL)

## Related Documentation

### Also in this Repository

- **[Local Docker Tutorial](./sqlserver-liquibase-tutorial.md)**: Original comprehensive tutorial using local Docker development
- **[Liquibase Implementation Guide](../../architecture/liquibase/liquibase-implementation-guide.md)**: Architectural decisions and guidance

### External Resources

- **GitHub Actions**: <https://docs.github.com/en/actions>
- **Liquibase**: <https://docs.liquibase.com/>
- **Liquibase GitHub Actions**: <https://github.com/liquibase/setup-liquibase>
- **SQL Server on Azure**: <https://learn.microsoft.com/en-us/azure/azure-sql/>

## Frequently Asked Questions

### Q: Should I learn the local Docker approach first?

**A**: It depends on your goals:

- **If you're new to Liquibase**: Yes, start with [local Docker tutorial](./sqlserver-liquibase-tutorial.md) to learn Liquibase basics
- **If you already know Liquibase**: You can start directly with GitHub Actions tutorials
- **If you're implementing for a team**: Learn both approaches and use hybrid model

See the [Comparison Guide](../../explanation/architecture/database-change-cicd/local-vs-github-actions-comparison.md) for detailed decision framework.

### Q: Can I use both local Docker and GitHub Actions?

**A**: Absolutely! Most teams use a hybrid approach:

- **Local Docker**: For rapid development and testing
- **GitHub Actions**: For deployments to shared environments

This is actually the recommended approach. See [Hybrid Approach section](./local-vs-github-actions-comparison.md#hybrid-approach).

### Q: Do I need Liquibase Pro for this?

**A**: No! All tutorials use **Liquibase Community Edition** (free, open source). The tutorials focus on tables, views, indexes, and constraints which are fully supported by the Community edition.

### Q: What if my database isn't accessible from the internet?

**A**: You have two options:

1. **Self-hosted GitHub Actions runners**: Run workflows on your own infrastructure within your private network (covered in Advanced section)
2. **Use local Docker approach**: Deploy from within your network

See [Best Practices - Network Security](../../best-practices/liquibase/github-actions.md#3-network-security) for details.

### Q: How long does it take to implement this for my team?

**A**: Typical timeline:

- **Week 1-2**: Team learning and initial setup
- **Week 3-4**: Implement basic pipeline (dev → staging)
- **Week 5-6**: Add production with approvals
- **Week 6-8**: Refinement and optimization

Total: **6-8 weeks** for full implementation

See [Transition Strategy](../../explanation/architecture/database-change-cicd/local-vs-github-actions-comparison.md#transition-strategy) for detailed phased approach.

### Q: Is this secure enough for production?

**A**: Yes, when properly configured! The tutorials cover production best practices including:

- ✅ Encrypted secrets
- ✅ Approval workflows
- ✅ Least privilege database access
- ✅ Audit trails
- ✅ Environment protection rules

See [Part 10: Production Best Practices](./archive/sqlserver-liquibase-github-actions-tutorial.md#part-10-production-best-practices) for comprehensive security guidance.

### Q: What about costs?

**A**: GitHub Actions costs:

- **Free tier**: 2,000 minutes/month for private repos
- **Public repos**: Unlimited free
- **Typical deployment**: 2-5 minutes
- **50 deployments/month**: ~250 minutes (well within free tier)

See [Cost Comparison](../../explanation/architecture/database-change-cicd/local-vs-github-actions-comparison.md#cost-comparison) for detailed analysis.

### Q: Can I use this with other databases (not SQL Server)?

**A**: The concepts and workflows apply to any database! You'll just need to:

- Change the JDBC connection string
- Use appropriate database driver
- Adjust SQL syntax for your database

Liquibase supports: PostgreSQL, MySQL, Oracle, DB2, and many others.

### Q: What if I get stuck?

**A**: Resources for help:

- **Tutorial troubleshooting sections**: Each tutorial has extensive troubleshooting
- **GitHub Actions logs**: Detailed logs for each workflow run
- **Community forums**:
  - [Liquibase Forum](https://forum.liquibase.org/)
  - [GitHub Community](https://github.com/orgs/community/discussions)
- **Stack Overflow**: Use tags `github-actions` and `liquibase`

## Success Stories

### Small Startup (3 developers)

**Before**: Manual deployments, frequent errors, 2 hours per release
**After**: Automated pipeline, zero errors, 10 minutes per release
**Time saved**: 90% reduction in deployment time
**Approach**: Hybrid (local dev + GitHub Actions for prod)

### Medium Company (15 developers)

**Before**: Coordination nightmares, conflicting changes, manual approvals
**After**: Automated dev→staging→prod, built-in approvals, audit trail
**Benefits**: Compliance-ready, fewer incidents, faster releases
**Approach**: GitHub Actions for all shared environments

### Enterprise (50+ developers)

**Before**: 2-week release cycles, change control board bottleneck
**After**: Daily releases, automated compliance checks, clear audit trail
**Benefits**: 14x faster releases, reduced risk, auditor-approved
**Approach**: Full GitHub Actions CI/CD with self-hosted runners

## Contributing

Found an issue or have suggestions?

- Open an issue in the repository
- Submit a pull request
- Contact the database DevOps team

## Document Information

**Version**: 1.0
**Last Updated**: November 2025
**Maintained By**: Database DevOps Team
**Related Tutorials**: All Liquibase documentation in this repository

---

## Ready to Start?

Choose your path:

🎯 **Beginner (Never used GitHub Actions)**
→ Start with [GitHub Actions Primer](../../explanation/architecture/database-change-cicd/github-actions-primer.md)

🚀 **Intermediate (Some GitHub Actions experience)**
→ Jump to [Hands-On Tutorial](./archive/sqlserver-liquibase-github-actions-tutorial.md)

🏢 **Team Lead (Planning implementation)**
→ Read [Comparison Guide](../../explanation/architecture/database-change-cicd/local-vs-github-actions-comparison.md) and [Best Practices](../../best-practices/liquibase/github-actions.md)

📖 **Want to understand best practices first**
→ Review [Best Practices](../../best-practices/liquibase/github-actions.md)

---

**Happy Learning! 🎉**
