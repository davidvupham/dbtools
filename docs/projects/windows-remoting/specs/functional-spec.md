# Functional Specification: Windows Remoting

## 1. Overview

The **Windows Remoting** capability provides a secure mechanism for managing Windows servers remotely. This specification describes the functionality of the `Enable-GDSWindowsRemoting` tool, which configures the Windows Remote Management (WinRM) service to accept secure HTTPS connections.

This tool aims to standardize the configuration of WinRM across the environment, ensuring that all remote management traffic is encrypted and authenticated using industry-standard protocols, facilitating secure operations for Automation tools (like Ansible) and Systems Administrators.

**Primary Use Case**: Enabling Ansible to connect securely to Windows Servers to perform configuration tasks, such as setting **User Rights Assignments** for SQL Server service accounts.

### 1.1 Transition Strategy (Existing Environments)
-   **WinRM Service**: In all Windows Server builds delivered, the WinRM service is **already enabled** (listening on HTTP). This function respects the existing service state and configuration; it will **not** disable or modify the service if it is already running.
-   **HTTP Listener**: The tool **preserves** the existing HTTP listener (Port 5985) for backward compatibility.
-   **HTTPS Listener**: The tool's primary action is to **Enable HTTPS** (Port 5986) alongside the existing configuration to allow for secure connections.
-   **Future State**: Once migration to HTTPS is complete, insecure HTTP listeners will be disabled in a future phase.

### 1.2 Certificate Selection Logic
If no certificate is explicitly provided via parameters, the tool automatically selects the best available certificate from the `Cert:\LocalMachine\My` store using the following precedence:

1.  **Filter Candidates**: Identify all certificates that are:
    *   **Valid**: `NotAfter` date is in the future (not expired).
    *   **Purpose**: Contains "Server Authentication" EKU (OID 1.3.6.1.5.5.7.3.1).
    *   **Hostname Match**: Subject name matches the machine's hostname.
2.  **Select Best Match**:
    *   **Priority 1 (Exact Match)**: A certificate where the Subject Common Name (CN) *exactly* matches the hostname (e.g., `CN=Server01`) is selected immediately.
    *   **Priority 2 (Newest Valid)**: If no exact match is found, candidates are sorted by expiration date, and the **newest** (longest remaining validity) certificate is selected.

**Error Condition**: If no valid certificate is found in the store and no `CertificateThumbprint` is provided via parameter, the function will **throw an error** and stop execution. It will *not* attempt to generate a self-signed certificate.




## 2. Scope

### 2.1 In Scope
-   **WinRM Service Configuration**: Enabling and configuring the WinRM service.
-   **HTTPS Listener**: Creating a WinRM listener on port 5986 backed by an SSL certificate.
-   **Firewall Configuration**: Configuring Windows Firewall to allow inbound traffic on TCP port 5986.
-   **Authentication Management**: Configuring Basic and CredSSP authentication settings securely.
-   **Certificate Selection**: Auto-detecting the most appropriate "Server Authentication" certificate for the host.

### 2.2 Out of Scope
-   **Disabling HTTP**: The existing HTTP listener (Port 5985) is preserved. Disabling it is out of scope for this specific tool version.
-   **Certificate Issuance**: The tool does *not* generate self-signed certificates or request certificates from a CA. It requires a valid certificate to be present.
-   **Network Level Firewalls**: Configuration of hardware firewalls or network security groups (NSGs).
-   **Client Configuration**: Configuration of the client machine (the one initiating the connection).

## 3. User Stories

### US-001: Secure Remote Management BOOTSTRAP

> **As a** Systems Administrator,
> **I want** to bootstrap a new Windows server with secure WinRM,
> **So that** I can immediately manage it remotely without exposing sensitive credentials over cleartext HTTP.

**Acceptance Criteria:**
- [ ] WinRM service is running and set to Automatic.
- [ ] An HTTPS listener is active on port 5986.
- [ ] A valid SSL certificate matching the hostname is bound to the listener.
- [ ] Windows Firewall allows traffic on port 5986.

### US-002: Ansible Integration

> **As a** DevOps Engineer,
> **I want** to configure WinRM for Ansible integration,
> **So that** I can use Ansible playbooks to perform configuration tasks (e.g., setting User Rights Assignment for SQL Server service accounts).

**Acceptance Criteria:**
- [ ] Ability to optionally enable Basic Authentication (defaults to disabled).
- [ ] Connection verification succeeds from the automation controller.

### US-003: Idempotent Configuration

> **As an** Automation Tool (e.g., pipeline),
> **I want** to run the configuration script multiple times without side effects,
> **So that** I can enforce the desired state without resetting manual configuration changes (like re-enabled auth protocols) unnecessarily.

**Acceptance Criteria:**
- [ ] If an HTTPS listener exists, it is not recreated.
- [ ] If WinRM is already running, authentication settings are not reset to defaults unless explicitly requested.

## 4. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-001 | **Idempotency** | Putting the system in the desired state should result in no changes on subsequent runs. |
| NFR-002 | **Resilience** | The tool must handle missing prerequisites (like certificates) with clear error messages rather than partial configuration. |
| NFR-003 | **Logging** | All configuration changes must be logged to the standard output and optionally the Event Log. |

## 5. Security Requirements

| ID | Requirement |
|----|-------------|
| SEC-001 | **Transport Encryption** | All remote management traffic MUST be encrypted via HTTPS (TLS 1.2+). HTTP listeners should not be created. |
| SEC-002 | **Certificate Validation** | The bound certificate MUST be valid (not expired) and formatted for "Server Authentication". |
| SEC-003 | **Secure Defaults** | Basic Authentication MUST be disabled by default to prevent cleartext credential transmission, unless explicitly overridden. |
| SEC-004 | **Least Privilege** | Firewall rules should be scoped as narrowly as possible (Standard Windows "Public/Private/Domain" profile support). |

## 6. Constraints

1.  **Operating System**: Windows Server 2019 or later (PowerShell v3+).
2.  **Privileges**: Must be executed with Elevated Admin privileges (Run as Administrator).
3.  **Certificates**: A valid X.509 certificate must already exist in the `Cert:\LocalMachine\My` store.

## 7. Dependencies

| Dependency | Owner | Status |
|------------|-------|--------|
| **NetSecurity Module** | Microsoft | ✅ Available (Standard in modern Windows) |
| **Server Certificate** | PKI Team / Auto-Enrollment | 🟡 Required Prerequisite |
