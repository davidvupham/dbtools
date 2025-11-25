# MongoDB Keyfile Security - Best Practices

## ⚠️ CRITICAL SECURITY ISSUE

**The `mongodb-keyfile` in this repository should be REMOVED and NEVER committed to source control!**

---

## Security Risks

### Why Keyfiles Should NOT Be in Git:

1. **Public Exposure** - GitHub repos can become public
2. **History Permanence** - Even if deleted, keyfiles remain in Git history
3. **Credential Leakage** - Anyone with repo access has production credentials
4. **Attack Surface** - Compromised keyfile = compromised entire replica set
5. **Compliance Violations** - SOC2, PCI-DSS, HIPAA violations

---

## Best Practices

### ✅ Secure Approach

#### 1. **Generate at Build Time** (Docker)
```dockerfile
# Generate unique keyfile during build
RUN openssl rand -base64 756 > /tmp/mongodb-keyfile.template && \
    chmod 400 /tmp/mongodb-keyfile.template && \
    chown mongodb:mongodb /tmp/mongodb-keyfile.template
```

#### 2. **Mount at Runtime** (Per Environment)
```bash
# Generate environment-specific keyfile
openssl rand -base64 756 > /secrets/mongodb-keyfile
chmod 400 /secrets/mongodb-keyfile

# Mount as Docker secret
docker run -d \
    --name auscl090041 \
    -v /secrets/mongodb-keyfile:/data/mongodb/mongodb-keyfile:ro \
    gds-mongodb-8.0.1:1.0.1
```

#### 3. **Use Docker Secrets** (Swarm)
```bash
# Create Docker secret
openssl rand -base64 756 | docker secret create mongodb-keyfile -

# Use in service
docker service create \
    --name mongo1 \
    --secret mongodb-keyfile \
    gds-mongodb-8.0.1:1.0.1
```

#### 4. **Use Kubernetes Secrets**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mongodb-keyfile
type: Opaque
data:
  keyfile: <base64-encoded-keyfile>
---
apiVersion: v1
kind: Pod
metadata:
  name: mongo1
spec:
  containers:
  - name: mongodb
    image: gds-mongodb-8.0.1:1.0.1
    volumeMounts:
    - name: keyfile
      mountPath: /data/mongodb/mongodb-keyfile
      subPath: keyfile
      readOnly: true
  volumes:
  - name: keyfile
    secret:
      secretName: mongodb-keyfile
      defaultMode: 0400
```

---

## Implementation Steps

### 1. Remove Keyfile from Git

```bash
# Remove from repo
git rm docker/mongodb/mongodb-keyfile

# Remove from history (CAREFUL!)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch docker/mongodb/mongodb-keyfile' \
  --prune-empty --tag-name-filter cat -- --all

# Force push (only if safe!)
git push origin --force --all
```

### 2. Add to .gitignore

```gitignore
# MongoDB Security - DO NOT COMMIT
mongodb-keyfile
*.key
*.pem
```

### 3. Generate Per Environment

```bash
#!/bin/bash
# generate-mongodb-keyfile.sh

ENVIRONMENT=${1:-dev}
KEYFILE_PATH="/secrets/${ENVIRONMENT}/mongodb-keyfile"

# Create directory
mkdir -p "$(dirname "$KEYFILE_PATH")"

# Generate keyfile (756 bytes of base64, ~1024 bytes before encoding)
openssl rand -base64 756 > "$KEYFILE_PATH"

# Set permissions (MongoDB requires 400 or 600)
chmod 400 "$KEYFILE_PATH"

echo "✅ Generated keyfile: $KEYFILE_PATH"
echo "⚠️  NEVER commit this file to source control!"
```

---

## Environment-Specific Keyfiles

**Each environment should have its own unique keyfile:**

```
/secrets/
├── dev/mongodb-keyfile          # Development
├── staging/mongodb-keyfile      # Staging
└── production/mongodb-keyfile   # Production
```

**Never use the same keyfile across environments!**

---

## Replica Set Keyfile Requirements

### MongoDB Keyfile Rules:

1. **Length**: 6 to 1024 bytes
2. **Characters**: Base64 characters only (a-z, A-Z, 0-9, +, /)
3. **Permissions**: Must be 400 (read-only by owner) or 600
4. **Ownership**: Must be owned by MongoDB user
5. **Identical**: Same keyfile on all replica set members

### Generate Compliant Keyfile:

```bash
# Generate 756 bytes of base64 (recommended)
openssl rand -base64 756 > mongodb-keyfile

# Set correct permissions
chmod 400 mongodb-keyfile
chown mongodb:mongodb mongodb-keyfile
```

---

## Python OOP Integration

```python
from gds_mongodb import MongoDBEngine

# Keyfile path is environment-specific
engine = MongoDBEngine(
    connection=conn,
    name="auscl090041",
    keyfile_path="/secrets/production/mongodb-keyfile"  # Per environment
)

# Build with mounted keyfile
result = engine.build(
    mongodb_version="8.0.1",
    keyfile_volume="/secrets/production/mongodb-keyfile:/data/mongodb/mongodb-keyfile:ro"
)
```

---

## Summary

| Approach | Security | Recommended |
|----------|----------|-------------|
| ❌ Keyfile in Git | **CRITICAL RISK** | Never |
| ⚠️ Same keyfile all envs | High risk | No |
| ✅ Generated at build | Medium (same in all containers from image) | Development only |
| ✅ Mounted at runtime | High (per environment) | Yes |
| ✅ Docker/K8s secrets | Very High (encrypted, rotatable) | Production |

**Bottom Line:**
- ❌ **NEVER** commit keyfiles to Git
- ✅ Generate unique keyfiles per environment
- ✅ Mount at runtime or use secrets managers
- ✅ Rotate keyfiles regularly (requires replica set restart)

---

## Immediate Action Required

1. ✅ Remove `mongodb-keyfile` from repository
2. ✅ Update Dockerfile to generate at build time
3. ✅ Add `.gitignore` to prevent future commits
4. ✅ Generate environment-specific keyfiles
5. ✅ Update deployment scripts to mount keyfiles
6. ⚠️  Consider rotating production keyfiles if previously committed
