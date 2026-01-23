# Configure JFrog Docker authentication

**[← Back to How-To Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

This guide walks you through generating an API token in JFrog Artifactory and configuring Docker to authenticate with the corporate registry for pulling container images.

## Table of contents

- [Prerequisites](#prerequisites)
- [Generate a JFrog API token](#generate-a-jfrog-api-token)
- [Configure Docker authentication](#configure-docker-authentication)
  - [Option 1: Use docker login (recommended)](#option-1-use-docker-login-recommended)
  - [Option 2: Manually edit config.json](#option-2-manually-edit-configjson)
- [Verify authentication](#verify-authentication)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have:

- A JFrog Artifactory account with access to the Docker registry
- Docker installed and running on your machine
- Network access to the corporate JFrog instance

[↑ Back to Table of Contents](#table-of-contents)

## Generate a JFrog API token

1. Open your web browser and navigate to your JFrog Artifactory instance:

   ```text
   https://<your-company>.jfrog.io
   ```

2. Log in with your corporate credentials.

3. Click your **username** in the top-right corner and select **Edit Profile**.

4. In the left sidebar, click **Identity Tokens** (or **Access Tokens** in older versions).

5. Click **Generate Token**.

6. Configure your token:
   - **Token Description**: Enter a meaningful name (e.g., `docker-cli-workstation`)
   - **Expiration**: Select an appropriate expiration period based on your security requirements

7. Click **Generate**.

8. **Copy the token immediately**. You cannot view it again after closing the dialog.

> [!WARNING]
> Store your token securely. Treat it like a password. Do not commit it to version control or share it in plain text.

[↑ Back to Table of Contents](#table-of-contents)

## Configure Docker authentication

Docker stores registry credentials in a configuration file located at:

| Operating System | Path |
|:---|:---|
| Linux/macOS | `~/.docker/config.json` |
| Windows | `%USERPROFILE%\.docker\config.json` |

### Option 1: Use docker login (recommended)

The `docker login` command automatically creates and updates your `config.json` file.

1. Open a terminal and run:

   ```bash
   docker login <your-company>.jfrog.io
   ```

2. When prompted, enter your credentials:
   - **Username**: Your JFrog username (usually your email or corporate ID)
   - **Password**: Paste the API token you generated

   ```text
   Username: john.doe@company.com
   Password: <paste-your-token-here>
   Login Succeeded
   ```

> [!TIP]
> If your organization uses a specific Docker virtual repository, include it in the URL:
> ```bash
> docker login <your-company>.jfrog.io/docker-virtual
> ```

[↑ Back to Table of Contents](#table-of-contents)

### Option 2: Manually edit config.json

If you need to configure Docker without running `docker login` (for example, in CI/CD pipelines or automated setups), you can edit the configuration file directly.

1. Create the Docker configuration directory if it does not exist:

   ```bash
   mkdir -p ~/.docker
   ```

2. Create or edit `~/.docker/config.json`:

   ```bash
   nano ~/.docker/config.json
   ```

3. Add your registry authentication. The `auth` value is a Base64-encoded string of `username:token`:

   ```json
   {
     "auths": {
       "<your-company>.jfrog.io": {
         "auth": "<base64-encoded-credentials>"
       }
     }
   }
   ```

4. Generate the Base64-encoded credentials:

   ```bash
   echo -n 'username:your-api-token' | base64
   ```

   Example output:
   ```text
   dXNlcm5hbWU6eW91ci1hcGktdG9rZW4=
   ```

5. Replace `<base64-encoded-credentials>` with the output from the previous command.

**Complete example:**

```json
{
  "auths": {
    "mycompany.jfrog.io": {
      "auth": "am9obi5kb2VAY29tcGFueS5jb206Y21WaGJHeDVYMnB6ZEdGMGIydGxiZz09"
    }
  }
}
```

> [!IMPORTANT]
> Set appropriate file permissions to protect your credentials:
> ```bash
> chmod 600 ~/.docker/config.json
> ```

[↑ Back to Table of Contents](#table-of-contents)

## Verify authentication

After configuring Docker, verify that authentication works correctly.

1. Pull a test image from your JFrog registry:

   ```bash
   docker pull <your-company>.jfrog.io/docker-virtual/alpine:latest
   ```

2. If successful, you see output similar to:

   ```text
   latest: Pulling from docker-virtual/alpine
   Digest: sha256:...
   Status: Downloaded newer image for mycompany.jfrog.io/docker-virtual/alpine:latest
   ```

3. Confirm the image is available locally:

   ```bash
   docker images | grep alpine
   ```

[↑ Back to Table of Contents](#table-of-contents)

## Troubleshooting

### Error: unauthorized: authentication required

**Cause**: Invalid credentials or expired token.

**Solution**:
1. Verify your token has not expired in JFrog.
2. Regenerate a new token and run `docker login` again.
3. Check that you are using the correct username format.

### Error: certificate signed by unknown authority

**Cause**: Your system does not trust the corporate Certificate Authority (CA).

**Solution**:
1. Import the corporate CA certificate into your system trust store.
2. For Docker Desktop, add the certificate via Settings → Docker Engine → insecure-registries (not recommended for production).

See [Configure SSL Certificates in WSL](configure-ssl-certificates-wsl.md) for detailed instructions.

### Error: no basic auth credentials

**Cause**: Docker cannot find credentials for the registry.

**Solution**:
1. Verify `~/.docker/config.json` exists and contains the correct registry URL.
2. Ensure the registry URL matches exactly (including any repository path).
3. Run `docker login` again.

### config.json has incorrect permissions

**Cause**: Other users can read your credentials file.

**Solution**:

```bash
chmod 600 ~/.docker/config.json
```

### Multiple registries

If you need to authenticate with multiple JFrog repositories or registries, add each one to the `auths` section:

```json
{
  "auths": {
    "mycompany.jfrog.io": {
      "auth": "<base64-credentials-1>"
    },
    "mycompany.jfrog.io/docker-prod": {
      "auth": "<base64-credentials-2>"
    }
  }
}
```

[↑ Back to Table of Contents](#table-of-contents)
