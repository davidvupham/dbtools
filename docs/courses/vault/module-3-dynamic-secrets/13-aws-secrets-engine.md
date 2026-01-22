# AWS Secrets Engine

**[← Back to Module 3](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-3_Dynamic_Secrets-blue)
![Lesson](https://img.shields.io/badge/Lesson-13-purple)

## Learning objectives

- Configure the AWS secrets engine
- Generate IAM user credentials
- Generate STS assumed role credentials
- Understand credential types and use cases

## Overview

The AWS secrets engine generates AWS access credentials dynamically. Vault can create IAM users or assume IAM roles to provide temporary credentials.

## Credential types

| Type | Use case | Persistence |
|------|----------|-------------|
| `iam_user` | Long-running processes | Creates IAM user |
| `assumed_role` | Short tasks | STS AssumeRole |
| `federation_token` | Console access | STS GetFederationToken |

## Configuration

### Enable the engine

```bash
vault secrets enable aws
```

### Configure root credentials

```bash
vault write aws/config/root \
    access_key=AKIAIOSFODNN7EXAMPLE \
    secret_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY \
    region=us-east-1
```

### Create a role

```bash
# IAM user with inline policy
vault write aws/roles/s3-reader \
    credential_type=iam_user \
    policy_document=-<<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": ["arn:aws:s3:::my-bucket", "arn:aws:s3:::my-bucket/*"]
    }
  ]
}
EOF

# Assumed role
vault write aws/roles/deploy-role \
    credential_type=assumed_role \
    role_arns=arn:aws:iam::123456789012:role/deploy-role
```

## Generating credentials

```bash
# Generate IAM credentials
vault read aws/creds/s3-reader

# Output:
# access_key      AKIAIOSFODNN7EXAMPLE
# secret_key      wJalrXUtnFEMI/K7MDENG...
# lease_id        aws/creds/s3-reader/abc123

# Generate STS credentials
vault read aws/sts/deploy-role

# Output:
# access_key      ASIAXXX...
# secret_key      xxx...
# security_token  FwoGZXIvYXdzE...
```

## Key takeaways

1. **Two main credential types**: IAM user (persistent) vs STS (temporary)
2. **IAM user credentials** create actual users that are cleaned up on revocation
3. **STS credentials** are temporary and don't create IAM users
4. **Use STS for most cases** - shorter TTL, no IAM user management

---

[← Previous: Database Secrets](./12-database-secrets-engine.md) | [Back to Module 3](./README.md) | [Next: PKI Secrets →](./14-pki-secrets-engine.md)
