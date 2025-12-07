# PowerShell DSC v3: The Next Generation

## Introduction

PowerShell Desired State Configuration (DSC) v3 is a major departure from the classic Windows PowerShell DSC (v1/v2). It has been re-architected as a standalone, cross-platform command-line tool (`dsc.exe`) that doesn't rely on the Windows Local Configuration Manager (LCM).

### Key Differences

| Feature | DSC v1/v2 (Classic) | DSC v3 (Modern) |
| :--- | :--- | :--- |
| **Engine** | PowerShell & WMI based (LCM) | Standalone CLI (`dsc.exe`) written in Rust |
| **Platform** | Windows only (mostly) | Cross-platform (Windows, Linux, macOS) |
| **Configuration** | MOF (Managed Object Format) | JSON or YAML |
| **Resources** | PowerShell Modules only | Any language (PowerShell, Python, C#, Bash) |
| **Mode** | Push or Pull Service | Command-line invocation (Push only, effectively) |

> [!NOTE]
> **Does DSC need to run locally?**
> Yes, `dsc.exe` applies configuration *locally* to the machine where it is executed. To manage remote machines, you must use an orchestration tool (like Ansible, a CI/CD agent, or `Invoke-Command`) to run `dsc.exe` on that remote target. It does not have built-in remote management like classic PowerShell DSC's Push mode.

> [!TIP]
> **Can DSC perform all steps for SQL Server (Install -> Patch -> AG)?**
> **Yes.** By chaining resources with `dependsOn`, you can orchestrate the entire lifecycle:
>
> 1. **Cluster**: Install Windows Failover Clustering (`WindowsFeature` or `xCluster`).
> 2. **Install**: Install SQL Server (`SqlSetup`), optionally enabling updates during install (`UpdateEnabled`).
> 3. **Patch**: Apply specific post-install patches (`Package` resource).
> 4. **AG**: Enable AlwaysOn (`SqlAlwaysOnService`) and create the Group (`SqlAG`).
>
> See the [Full Stack Example](examples/sql_full_stack.dsc.json).

> [!TIP]
> **Can it handle more than 2 Replicas?**
> **Yes.** SQL Server Enterprise supports up to **9 Replicas** (1 Primary + 8 Secondaries).
> You can easily define this in DSC by keeping the main `SqlAG` resource and adding multiple `SqlAGReplica` resources (one for each additional node).
> See the [Multi-Replica Example](examples/sql_ag_multi_replica.dsc.json).

> [!TIP]
> **Does it support Multi-Site (Multi-Subnet) AGs?**
> **Yes.** You can configure a multi-subnet listener by providing multiple IP addresses to the `SqlAGListener` resource.
>
> ```json
> "Settings": {
>   "Name": "MyListener",
>   "IpAddress": ["10.0.1.50/255.255.255.0", "192.168.2.50/255.255.255.0"]
> }
> ```
>
> Clients should simply use `MultiSubnetFailover=True` in their connection strings.

---

## Foundations: Getting Started

### 1. Installation

DSC v3 is distributed as a command-line tool.

* **Windows**: `winget install Microsoft.DSC`
* **Linux/macOS**: Download from GitHub releases.

### 2. The `dsc` Command

The core interaction is through the `dsc` CLI.

```bash
dsc --help
```

Common commands:

* `dsc resource list`: List available resources.
* `dsc resource get`: Get the current state of a resource.
* `dsc resource set`: Enforce the desired state.
* `dsc resource test`: Test if the current state matches the desired state.
* `dsc config get/set/test`: Apply a full configuration document.

### 3. Your First Configuration

Configurations are now JSON or YAML files.
**File**: `examples/simple_file.dsc.json`

```json
{
  "$schema": "https://raw.githubusercontent.com/PowerShell/DSC/main/schemas/2024/04/config/document.json",
  "resources": [
    {
      "name": "MyTestFile",
      "type": "File",
      "properties": {
        "destinationPath": "/tmp/testfile.txt",
        "contents": "Hello from DSC v3!"
      }
    }
  ]
}
```

Run it:

```bash
cat examples/simple_file.dsc.json | dsc config set
```

---

## Intermediate: Adapters and Legacy Resources

DSC v3 allows you to use "Classic" PowerShell DSC resources via the `Microsoft.Windows/PSDsc` adapter. This is crucial for Windows administration.

### Using the PSDsc Adapter

To use a resource like `UserRightsAssignment` from the `SecurityPolicyDsc` module, you wrap it in the adapter.

**Prerequisite**:
You must have the PowerShell module installed:

```powershell
Install-Module -Name SecurityPolicyDsc -Force
```

**Configuration Structure**:

```json
{
  "resources": [
    {
      "type": "Microsoft.Windows/PSDsc",
      "name": "LogOnAsServiceRight",
      "properties": {
        "PSDscResource": {
          "ModuleName": "SecurityPolicyDsc",
          "Name": "UserRightsAssignment",
          "Settings": {
            "Policy": "Log_on_as_a_service",
            "Identity": "MyDomain\\MyServiceAccount"
          }
        }
      }
    }
  ]
}
```

---

## Advanced: Complex Configurations

### 1. Parameters

You can parameterize your configurations using the `parameters` section in the JSON/YAML.

```json
{
  "parameters": {
    "UserName": { "type": "string" }
  },
  "resources": [...]
}
```

Inject values at runtime using `--parameters` or a parameters file.

### 2. Exporting Existing State

DSC v3 can reverse-engineer the current state into a configuration.

```bash
dsc resource export Microsoft.Windows/Registry > current_registry.dsc.json
```

---

## Use Cases

1. **Bootstrapping**: Initial server setup (installing packages, setting base configs) via simple JSON files committed to git.
2. **Compliance Audit**: Run `dsc config test` in a scheduled task or CI pipeline to report on drift without auto-remediating.
3. **Golden Image Creation**: Use DSC v3 in Packer builds to configure images before baking.
4. **Cross-Platform Mgmt**: Manage Linux and Windows nodes with a unified tool and config format.

---

## Integration: Ansible

While Ansible has a `win_dsc` module for classic DSC, for DSC v3 (`dsc.exe`), you use the `win_command` or `win_shell` module to invoke the CLI directly.

**Example Playbook**: [examples/ansible_dsc_v3.yml](examples/ansible_dsc_v3.yml)

```yaml
- name: Apply DSC v3 Configuration
  ansible.windows.win_command: |
    dsc.exe config set --file C:\Temp\my_config.dsc.json
```

---

## SQL Server and Availability Groups

You can use the powerful `SqlServerDsc` module with DSC v3 via the `PSDsc` adapter to manage SQL Server installations and AlwaysOn Availability Groups.

### 1. Installation

The `SqlSetup` resource allows you to install SQL Server instances, specifying features and admin accounts.
**Example**: [examples/sql_server_install.dsc.json](examples/sql_server_install.dsc.json)

### 2. Availability Groups

You can manage the entire AG stack, from the Failover Cluster to the Availability Group Listener.
**Example**: [examples/sql_ag.dsc.json](examples/sql_ag.dsc.json)

### 3. Full Stack: Cluster, Install, Patch, AG

This comprehensive example demonstrates the entire sequence:

1. Install Failover Clustering feature.
2. Install SQL Server (with `UpdateEnabled`).
3. Apply a specific Cumulative Update (Patch) using the generic `Package` resource.
4. Enable AlwaysOn and create the Availability Group.

**Example**: [examples/sql_full_stack.dsc.json](examples/sql_full_stack.dsc.json)

### 4. High Scale: Multi-Replica AGs

DSC handles massive Availability Groups (up to 9 replicas in Enterprise Edition) by defining a `SqlAGReplica` resource for each secondary node.
**Example**: [examples/sql_ag_multi_replica.dsc.json](examples/sql_ag_multi_replica.dsc.json)

> [!NOTE]
> Ensure the `SqlServerDsc` module is installed on the target node (PowerShell 5.1+ required for some resources).

---

## Exercises

1. **Hello World**: Create a `file.dsc.json` that creates a text file with your name in it. Apply it using `dsc config set`.
2. **Drift Detection**: Modify the file manually. Run `dsc config test` to see if it detects the change. Run `dsc config set` to fix it.
3. **Legacy Power**: Install a classic DSC module (e.g., `ComputerManagementDsc`) and use the `PSDsc` adapter to change the TimeZone.

---

## Examples

* [Simple File](examples/simple_file.dsc.json)
* [Legacy Adapter](examples/legacy_adapter.dsc.json)
* [User Rights Assignment](examples/user_rights_assignment.dsc.json)
* [Ansible Playbook](examples/ansible_dsc_v3.yml)
* [SQL Server Install](examples/sql_server_install.dsc.json)
* [SQL Availability Group](examples/sql_ag.dsc.json)
* [SQL Multi-Replica AG](examples/sql_ag_multi_replica.dsc.json)
* [SQL Full Stack (Cluster+Install+Patch+AG)](examples/sql_full_stack.dsc.json)
