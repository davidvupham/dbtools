# Configure SSL Certificates in WSL for Corporate Environments

This guide helps developers resolve SSL certificate errors in WSL when working behind
corporate proxies or firewalls that perform SSL/TLS inspection.

## Table of Contents

- [Understanding the Problem](#understanding-the-problem)
- [Prerequisites](#prerequisites)
- [Step 1 — Identify the Corporate CA Certificate](#step-1--identify-the-corporate-ca-certificate)
- [Step 2 — Copy Certificates from Red Hat Server](#step-2--copy-certificates-from-red-hat-server)
- [Step 3 — Install Certificates in WSL (Ubuntu/Debian)](#step-3--install-certificates-in-wsl-ubuntudebian)
- [Step 4 — Configure Docker to Use Certificates](#step-4--configure-docker-to-use-certificates)
- [Step 5 — Configure Git and curl](#step-5--configure-git-and-curl)
- [Step 6 — Configure Python pip and uv](#step-6--configure-python-pip-and-uv)
- [Step 7 — Configure Node.js npm](#step-7--configure-nodejs-npm)
- [Verify All Tools](#verify-all-tools)
- [Docker Build with Corporate Certificates](#docker-build-with-corporate-certificates)
  - [Test Your Certificate Setup](#test-your-certificate-setup)
- [Troubleshooting](#troubleshooting)
- [Reference: Certificate Locations by OS](#reference-certificate-locations-by-os)

---

## Understanding the Problem

### What is SSL Inspection?

Many corporate networks use a **proxy or firewall** that intercepts HTTPS traffic to
inspect it for security threats. This is called **SSL inspection** or **TLS interception**.

```text
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Your WSL   │────▶│ Corporate Proxy  │────▶│  github.com     │
│  curl/git   │     │ (SSL Inspection) │     │  pypi.org, etc. │
└─────────────┘     └──────────────────┘     └─────────────────┘
                           │
                    Uses corporate CA
                    to re-sign traffic
```

### Why It Fails in WSL

- **Corporate Red Hat servers**: IT pre-installs the corporate CA certificate
- **Your WSL instance**: Fresh install with no corporate CA certificates

When `curl`, `git`, `pip`, or Docker tries to connect to HTTPS URLs, they see a
certificate signed by your corporate CA — which they don't trust — and fail with errors like:

```text
curl: (60) SSL certificate problem: unable to get local issuer certificate
fatal: unable to access 'https://github.com/...': SSL certificate problem
pip: SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

---

## Prerequisites

- WSL2 with Ubuntu or Debian installed
- SSH access to a working Red Hat/CentOS server in your corporate network
- Basic familiarity with the terminal

---

## Step 1 — Identify the Corporate CA Certificate

### Option A: Get Certificate Info from Red Hat Server

On a **Red Hat/CentOS server** where HTTPS connections work, list custom CA certificates:

```bash
# List all custom CA certificates
ls -la /etc/pki/ca-trust/source/anchors/

# View certificate details
for cert in /etc/pki/ca-trust/source/anchors/*.crt; do
    echo "=== $cert ==="
    openssl x509 -in "$cert" -noout -subject -issuer -dates
done
```

Common corporate CA certificate names include:

| Vendor               | Typical Filename Pattern                           |
| -------------------- | -------------------------------------------------- |
| Zscaler              | `*zscaler*.crt`, `*zscaler*.pem`                   |
| Palo Alto            | `*paloalto*.crt`, `*pan*.crt`                      |
| Blue Coat / Symantec | `*bluecoat*.crt`, `*symantec*.crt`                 |
| Cisco Umbrella       | `*umbrella*.crt`, `*cisco*.crt`                    |
| McAfee               | `*mcafee*.crt`                                     |
| Fortinet             | `*fortinet*.crt`, `*fortigate*.crt`                |
| Generic Corporate    | `*corporate*.crt`, `*internal*.crt`, `*proxy*.crt` |

### Option B: Extract Certificate from a Working Connection

If you can't find the certificate file, extract it from a live connection on the Red Hat server:

```bash
# Connect to a site and capture the certificate chain
openssl s_client -connect github.com:443 -showcerts </dev/null 2>/dev/null | \
    sed -n '/-----BEGIN CERTIFICATE-----/,/-----END CERTIFICATE-----/p' > /tmp/github-chain.pem
```

The **last certificate** in the chain is typically the root CA. Extract it:

```bash
# Extract just the root CA (last cert in chain)
csplit -z /tmp/github-chain.pem '/-----BEGIN CERTIFICATE-----/' '{*}'
mv xx02 corporate-root-ca.crt  # Usually the last file (adjust number as needed)

# Verify it's a CA certificate
openssl x509 -in corporate-root-ca.crt -noout -text | grep -A1 "Basic Constraints"
# Should show: CA:TRUE
```

### Option C: Get from Windows Certificate Store

If your Windows host has the corporate CA installed, export it:

1. Press `Win+R`, type `certmgr.msc`, press Enter
2. Navigate to **Trusted Root Certification Authorities > Certificates**
3. Find your corporate CA (look for your company name)
4. Right-click → **All Tasks → Export**
5. Choose **Base-64 encoded X.509 (.CER)**
6. Save to a location accessible from WSL

---

## Step 2 — Copy Certificates from Red Hat Server

### Create a Local Directory for Certificates

In your WSL terminal:

```bash
mkdir -p ~/corporate-certs
cd ~/corporate-certs
```

### Copy Certificates via SCP

```bash
# Copy all CA certificates from the Red Hat server
scp user@redhat-server:/etc/pki/ca-trust/source/anchors/*.crt ~/corporate-certs/

# Or copy a specific certificate
scp user@redhat-server:/etc/pki/ca-trust/source/anchors/corporate-ca.crt ~/corporate-certs/
```

### Alternative: Copy from Windows (if exported from certmgr)

```bash
# Windows paths are mounted under /mnt/c/
cp /mnt/c/Users/YourName/Downloads/corporate-ca.cer ~/corporate-certs/corporate-ca.crt
```

### Verify the Certificates

```bash
# Check certificate details
for cert in ~/corporate-certs/*.crt; do
    echo "=== $cert ==="
    openssl x509 -in "$cert" -noout -subject -issuer -dates
done
```

---

## Step 3 — Install Certificates in WSL (Ubuntu/Debian)

### Copy to System Trust Store

```bash
# Copy certificates to Ubuntu's CA directory
sudo cp ~/corporate-certs/*.crt /usr/local/share/ca-certificates/

# Update the system trust store
sudo update-ca-certificates
```

Expected output:

```text
Updating certificates in /etc/ssl/certs...
1 added, 0 removed; done.
Running hooks in /etc/ca-certificates/update.d...
done.
```

### Verify Installation

```bash
# Test with curl
curl -I https://github.com

# Should return HTTP headers, not SSL errors
# HTTP/2 200
# ...
```

---

## Step 4 — Configure Docker to Use Certificates

Docker running inside WSL needs access to the corporate CA certificates.

### For Docker Desktop (WSL2 Backend)

Docker Desktop automatically inherits the WSL trust store after you run
`update-ca-certificates`. Restart Docker Desktop if needed.

### For Docker Engine (Installed in WSL)

Create a Docker daemon configuration to use the system certificates:

```bash
# Create Docker config directory
sudo mkdir -p /etc/docker/certs.d

# Copy certificates for Docker registry access
sudo cp ~/corporate-certs/*.crt /etc/docker/certs.d/

# Restart Docker
sudo systemctl restart docker
# Or if using Docker Desktop integration, restart Docker Desktop
```

### For Docker Build Context

When building Docker images, the build context doesn't have access to host certificates.
You must inject them into the image. See [Docker Build with Corporate Certificates](#docker-build-with-corporate-certificates).

---

## Step 5 — Configure Git and curl

After running `update-ca-certificates`, both `git` and `curl` should work automatically.
If they still fail, configure them explicitly.

### Git Configuration

```bash
# Tell git to use the system CA bundle
git config --global http.sslCAInfo /etc/ssl/certs/ca-certificates.crt
```

### curl Configuration

Create or edit `~/.curlrc`:

```bash
echo 'cacert=/etc/ssl/certs/ca-certificates.crt' >> ~/.curlrc
```

### Verification

```bash
# Test git
git ls-remote https://github.com/liquibase/liquibase.git

# Test curl
curl -I https://pypi.org
```

---

## Step 6 — Configure Python pip and uv

### pip Configuration

Create or edit `~/.config/pip/pip.conf`:

```bash
mkdir -p ~/.config/pip
cat > ~/.config/pip/pip.conf << 'EOF'
[global]
cert = /etc/ssl/certs/ca-certificates.crt
EOF
```

### uv Configuration

The `uv` package manager respects the `SSL_CERT_FILE` environment variable:

```bash
# Add to ~/.bashrc
echo 'export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt' >> ~/.bashrc
echo 'export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt' >> ~/.bashrc
source ~/.bashrc
```

### Verify pip and uv

```bash
# Test pip
pip index versions requests

# Test uv
uv pip install --dry-run requests
```

---

## Step 7 — Configure Node.js npm

### npm Configuration

```bash
# Set the CA certificate for npm
npm config set cafile /etc/ssl/certs/ca-certificates.crt

# Verify
npm config get cafile
```

### Environment Variable (Alternative)

```bash
# Add to ~/.bashrc
echo 'export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt' >> ~/.bashrc
source ~/.bashrc
```

### Verify npm

```bash
npm ping
# Should return: Ping success: {...}
```

---

## Verify All Tools

Run these commands to verify all tools work correctly:

```bash
# System tools
curl -I https://github.com
wget -q --spider https://github.com && echo "wget: OK"

# Git
git ls-remote https://github.com/liquibase/liquibase.git | head -1

# Python
pip index versions pip 2>/dev/null && echo "pip: OK"

# Node (if installed)
npm ping 2>/dev/null && echo "npm: OK"

# Docker (test image pull)
docker pull hello-world
```

---

## Docker Build with Corporate Certificates

When building Docker images, `curl` and other commands inside the build context need
access to corporate CA certificates. Here are two approaches:

### Approach 1: Copy Certificates into the Image

Create a `corporate-certs/` directory next to your Dockerfile containing your `.crt` files.

**For UBI/RHEL-based images** (like the Liquibase image):

```dockerfile
# Copy corporate CA certificates
COPY corporate-certs/*.crt /etc/pki/ca-trust/source/anchors/

RUN set -eux; \
    # Update the trust store BEFORE any curl/wget commands
    update-ca-trust; \
    # Now curl will work
    curl -fsSL https://example.com/somefile.tar.gz -o /tmp/file.tar.gz
```

**For Ubuntu/Debian-based images**:

```dockerfile
# Copy corporate CA certificates
COPY corporate-certs/*.crt /usr/local/share/ca-certificates/

RUN set -eux; \
    apt-get update && apt-get install -y ca-certificates; \
    update-ca-certificates; \
    # Now curl will work
    curl -fsSL https://example.com/somefile.tar.gz -o /tmp/file.tar.gz
```

**For Alpine-based images**:

```dockerfile
# Copy corporate CA certificates
COPY corporate-certs/*.crt /usr/local/share/ca-certificates/

RUN set -eux; \
    apk add --no-cache ca-certificates; \
    update-ca-certificates; \
    # Now curl/wget will work
    wget https://example.com/somefile.tar.gz -O /tmp/file.tar.gz
```

### Approach 2: Build Argument (Inject at Build Time)

Add a build argument to optionally inject certificates:

```dockerfile
ARG CORPORATE_CA_CERT=""

RUN set -eux; \
    # Inject corporate CA if provided
    if [ -n "${CORPORATE_CA_CERT}" ]; then \
        echo "${CORPORATE_CA_CERT}" > /etc/pki/ca-trust/source/anchors/corporate-ca.crt; \
        update-ca-trust; \
    fi; \
    # Continue with downloads
    curl -fsSL https://github.com/...
```

Build with:

```bash
docker build \
    --build-arg CORPORATE_CA_CERT="$(cat ~/corporate-certs/corporate-ca.crt)" \
    -t myimage:latest .
```

### Approach 3: Multi-Stage Build (Keep Certificates Out of Final Image)

If you don't want certificates in your final production image:

```dockerfile
# Stage 1: Download with certificates
FROM eclipse-temurin:21-jre-ubi9-minimal AS downloader
COPY corporate-certs/*.crt /etc/pki/ca-trust/source/anchors/
RUN update-ca-trust
RUN curl -fsSL -o /tmp/liquibase.tar.gz https://github.com/liquibase/.../liquibase.tar.gz

# Stage 2: Final image (no certificates)
FROM eclipse-temurin:21-jre-ubi9-minimal
COPY --from=downloader /tmp/liquibase.tar.gz /tmp/
RUN tar -xzf /tmp/liquibase.tar.gz -C /opt/liquibase
```

### Test Your Certificate Setup

Before modifying your actual Dockerfile, build a minimal test image to verify your
corporate certificates work inside a container.

#### Step 1: Create Test Directory Structure

```bash
mkdir -p ~/ssl-test/corporate-certs
cd ~/ssl-test

# Copy your corporate CA certificates
cp ~/corporate-certs/*.crt corporate-certs/
```

#### Step 2: Create Test Dockerfile

Create `~/ssl-test/Dockerfile.test`:

```dockerfile
# Test Dockerfile for SSL Certificate Verification
# Usage: docker build -f Dockerfile.test -t ssl-test .

FROM eclipse-temurin:21-jre-ubi9-minimal

# Copy corporate CA certificates
COPY corporate-certs/*.crt /etc/pki/ca-trust/source/anchors/

# Install curl and update CA trust
RUN set -eux; \
    microdnf -y install curl ca-certificates; \
    update-ca-trust; \
    microdnf clean all

# Test SSL connections to common endpoints
RUN set -eux; \
    echo "=== Testing SSL Connections ===" && \
    echo "Testing github.com..." && \
    curl -fsSI https://github.com > /dev/null && echo "✓ github.com OK" && \
    echo "Testing pypi.org..." && \
    curl -fsSI https://pypi.org > /dev/null && echo "✓ pypi.org OK" && \
    echo "Testing repo1.maven.org..." && \
    curl -fsSI https://repo1.maven.org > /dev/null && echo "✓ repo1.maven.org OK" && \
    echo "=== All SSL Tests Passed ==="

CMD ["echo", "SSL certificates are configured correctly!"]
```

#### Step 3: Build and Verify

```bash
cd ~/ssl-test

# Build the test image
docker build -f Dockerfile.test -t ssl-test .

# If the build succeeds, certificates are working!
# You should see:
#   === Testing SSL Connections ===
#   Testing github.com...
#   ✓ github.com OK
#   Testing pypi.org...
#   ✓ pypi.org OK
#   Testing repo1.maven.org...
#   ✓ repo1.maven.org OK
#   === All SSL Tests Passed ===
```

#### Step 4: Interactive Debugging (If Build Fails)

If the build fails with SSL errors, debug interactively:

```bash
# Start container without running the failing RUN command
docker run --rm -it eclipse-temurin:21-jre-ubi9-minimal bash

# Inside the container, manually install curl and test
microdnf -y install curl
curl -v https://github.com 2>&1 | head -50

# Look for errors like:
#   curl: (60) SSL certificate problem: unable to get local issuer certificate
```

#### Alternative: Ubuntu/Debian Test Image

For Ubuntu/Debian-based images, use this test Dockerfile:

```dockerfile
# Test Dockerfile for SSL Certificate Verification (Ubuntu)
FROM ubuntu:22.04

# Copy corporate CA certificates
COPY corporate-certs/*.crt /usr/local/share/ca-certificates/

# Install curl and update CA trust
RUN set -eux; \
    apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Test SSL connections
RUN set -eux; \
    echo "=== Testing SSL Connections ===" && \
    curl -fsSI https://github.com > /dev/null && echo "✓ github.com OK" && \
    curl -fsSI https://pypi.org > /dev/null && echo "✓ pypi.org OK" && \
    echo "=== All SSL Tests Passed ==="

CMD ["echo", "SSL certificates are configured correctly!"]
```

#### Cleanup

After verification, remove the test artifacts:

```bash
docker rmi ssl-test
rm -rf ~/ssl-test
```

---

## Troubleshooting

### SSL Errors Persist After Installing Certificates

1. **Verify the certificate was installed**:

   ```bash
   ls -la /usr/local/share/ca-certificates/
   ls -la /etc/ssl/certs/ | grep -i corporate
   ```

2. **Re-run certificate update**:

   ```bash
   sudo update-ca-certificates --fresh
   ```

3. **Check certificate format** (must be PEM format, not DER):

   ```bash
   # Check format
   file ~/corporate-certs/corporate-ca.crt
   
   # Convert DER to PEM if needed
   openssl x509 -inform DER -in cert.cer -out cert.crt
   ```

### curl Works but Docker Build Fails

Docker builds run in an isolated environment. Certificates on the host are not available
inside the build context. Use one of the approaches in
[Docker Build with Corporate Certificates](#docker-build-with-corporate-certificates).

### "Certificate Not Trusted" Despite Being Installed

Your certificate might be an **intermediate CA**, not the **root CA**. You need the root:

```bash
# Check if it's a root (self-signed) CA
openssl x509 -in ~/corporate-certs/corporate-ca.crt -noout -text | grep -A1 "Basic Constraints"
# Root CA shows: CA:TRUE

# Check if Issuer == Subject (self-signed)
openssl x509 -in ~/corporate-certs/corporate-ca.crt -noout -subject -issuer
# Root CA: Subject and Issuer are the same
```

### Git Clone Fails with "server certificate verification failed"

```bash
# Verify the CA bundle path
git config --global http.sslCAInfo

# Should be: /etc/ssl/certs/ca-certificates.crt

# If missing, set it
git config --global http.sslCAInfo /etc/ssl/certs/ca-certificates.crt
```

### How to Bypass SSL Verification (NOT Recommended)

> [!CAUTION]
> Disabling SSL verification is a security risk. Only use temporarily for debugging.

```bash
# curl (temporary)
curl -k https://example.com

# git (temporary)
GIT_SSL_NO_VERIFY=1 git clone https://...

# pip (temporary)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org package-name
```

---

## Reference: Certificate Locations by OS

| OS / Distribution          | Custom CA Location                   | Update Command              |
| -------------------------- | ------------------------------------ | --------------------------- |
| **Ubuntu / Debian**        | `/usr/local/share/ca-certificates/`  | `update-ca-certificates`    |
| **RHEL / CentOS / Fedora** | `/etc/pki/ca-trust/source/anchors/`  | `update-ca-trust`           |
| **Alpine**                 | `/usr/local/share/ca-certificates/`  | `update-ca-certificates`    |
| **macOS**                  | Keychain Access app                  | `security add-trusted-cert` |
| **Windows**                | Certificate Manager (certmgr.msc)    | GUI or PowerShell           |

### Java Truststore Locations

For Java applications (like Liquibase), certificates must also be in the Java truststore:

| JDK Distribution    | Truststore Location               |
| ------------------- | --------------------------------- |
| Eclipse Temurin     | `$JAVA_HOME/lib/security/cacerts` |
| OpenJDK             | `$JAVA_HOME/lib/security/cacerts` |
| Amazon Corretto     | `$JAVA_HOME/lib/security/cacerts` |

**Add certificate to Java truststore**:

```bash
keytool -importcert -trustcacerts \
    -keystore $JAVA_HOME/lib/security/cacerts \
    -storepass changeit \
    -noprompt \
    -alias corporate-ca \
    -file ~/corporate-certs/corporate-ca.crt
```

---

## Related Documentation

- [Set Up WSL2](setup-wsl2.md) — WSL2 installation and configuration
- [Configure Corporate Docker Registry](configure-corporate-docker-registry.md) — Docker registry proxy setup
- [Import Certificate to Windows](import-certificate-to-windows.md) — Windows certificate management
