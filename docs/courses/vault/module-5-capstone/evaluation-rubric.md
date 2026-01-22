# Capstone Evaluation Rubric

**[← Back to Module 5](./README.md)**

## Scoring

| Category | Points | Criteria |
|----------|--------|----------|
| **Infrastructure** | 20 | Vault deployed, TLS configured, audit enabled |
| **Authentication** | 20 | Userpass, AppRole, entities/groups configured |
| **Secrets Engines** | 20 | KV, Database, Transit configured and working |
| **Policies** | 20 | Team policies, templating, proper access control |
| **Integration** | 10 | Working application or CI/CD demo |
| **Documentation** | 10 | Clear setup instructions, architecture diagrams |
| **Total** | 100 | |

## Grade scale

| Score | Grade |
|-------|-------|
| 90-100 | Excellent |
| 80-89 | Good |
| 70-79 | Satisfactory |
| Below 70 | Needs improvement |

## Self-assessment checklist

### Infrastructure (20 points)

- [ ] Vault is running and accessible (5)
- [ ] TLS is configured (5)
- [ ] Audit logging is enabled (5)
- [ ] Health checks work (5)

### Authentication (20 points)

- [ ] Userpass auth enabled with users (5)
- [ ] AppRole auth enabled with roles (5)
- [ ] Entities created for users (5)
- [ ] Groups created for teams (5)

### Secrets Engines (20 points)

- [ ] KV v2 secrets working (7)
- [ ] Database dynamic credentials working (7)
- [ ] Transit encryption working (6)

### Policies (20 points)

- [ ] Team-specific policies (7)
- [ ] Templated user workspace policies (7)
- [ ] Proper deny rules (6)

### Integration (10 points)

- [ ] Application successfully retrieves secrets (5)
- [ ] CI/CD successfully authenticates (5)

### Documentation (10 points)

- [ ] README with setup instructions (5)
- [ ] Architecture diagram (5)

---

[← Back to Project](./project-5-capstone.md) | [Back to Course →](../README.md)
