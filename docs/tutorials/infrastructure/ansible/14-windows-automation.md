# Chapter 14: Windows Automation with Ansible

Ansible isn't just for Linux! It has robust support for automating Windows servers. This chapter guides you through setting up Ansible to manage Windows hosts using **Kerberos** authentication, which is the standard and most secure method in Active Directory environments.

## 📋 Prerequisites

### Control Node (Linux)
- Ansible installed
- `ansible.windows` collection installed (included in full Ansible package, or run `ansible-galaxy collection install ansible.windows`)
- Python `pywinrm` library: `pip install "pywinrm[kerberos]"`
- `krb5-user` (Debian/Ubuntu) or `krb5-workstation` (RHEL/CentOS) package installed
- A valid `/etc/krb5.conf` configured for your Active Directory domain

### Managed Node (Windows)
- PowerShell 3.0 or newer (PowerShell 5.1+ recommended)
- .NET Framework 4.0 or newer
- A WinRM listener configured

## 🔧 Configuration Steps

### 1. Windows Configuration (The Managed Node)

On your Windows server, you need to enable WinRM (Windows Remote Management). The easiest way to do this for a tutorial environment is using the `ConfigureRemotingForAnsible.ps1` script provided by the Ansible team.

**Run this in PowerShell as Administrator:**

```powershell
$url = "https://raw.githubusercontent.com/ansible/ansible/devel/examples/scripts/ConfigureRemotingForAnsible.ps1"
$file = "$env:temp\ConfigureRemotingForAnsible.ps1"
(New-Object -TypeName System.Net.WebClient).DownloadFile($url, $file)
powershell.exe -ExecutionPolicy ByPass -File $file
```

> [!IMPORTANT]
> In a production environment, you should configure WinRM via Group Policy (GPO) rather than running scripts manually.

### 2. Linux Configuration (The Control Node)

Ensure your Linux machine can talk to the Windows Domain Controller.

**Edit `/etc/krb5.conf`:**
Ensure your domain is listed. It usually looks something like this:

```ini
[libdefaults]
    default_realm = EXAMPLE.COM
    dns_lookup_realm = false
    dns_lookup_kdc = false

[realms]
    EXAMPLE.COM = {
        kdc = dc01.example.com
        admin_server = dc01.example.com
    }

[domain_realm]
    .example.com = EXAMPLE.COM
    example.com = EXAMPLE.COM
```

**Test Kerberos:**
Try to get a ticket for a domain user:

```bash
kinit administrator@EXAMPLE.COM
# Enter password when prompted
klist
# You should see a valid ticket
```

## 📝 Inventory Configuration

Ansible communicates with Windows using the `winrm` connection plugin. You need to set specific variables in your inventory.

**`inventory/hosts.ini`**:

```ini
[windows]
winserver01.example.com

[windows:vars]
# User is required to match the Kerberos principal
ansible_user=administrator@EXAMPLE.COM

# Password is OPTIONAL if you have a valid Kerberos ticket (via kinit)
# ansible_password=SecretPassword123!

ansible_connection=winrm
ansible_winrm_transport=kerberos
ansible_winrm_server_cert_validation=ignore
ansible_port=5985
```

> [!NOTE]
> **Authentication Options:**
> 1.  **With Password**: If you provide `ansible_password`, Ansible will use it to obtain a Kerberos ticket automatically.
> 2.  **Without Password (Recommended)**: If you omit `ansible_password`, you **must** run `kinit user@DOMAIN.COM` on the control node before running the playbook. This is more secure as it avoids storing passwords in plain text.

## 🧪 Testing the Connection

Use the `win_ping` module to verify connectivity:

```bash
ansible windows -i inventory/hosts.ini -m win_ping
```

**Expected Output:**
```json
winserver01.example.com | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

## 💻 Example: Creating a File with an Ansible Role

Let's create a simple role to manage files on Windows.

### Directory Structure

```text
site.yml
inventory/
    hosts.ini
roles/
    win_file_demo/
        tasks/
            main.yml
```

### The Role Task (`roles/win_file_demo/tasks/main.yml`)

We use the `ansible.windows.win_file` module, which is the Windows equivalent of the `file` module.

```yaml
---
- name: Ensure a directory exists
  ansible.windows.win_file:
    path: C:\AnsibleDemo
    state: directory

- name: Create a file with content
  ansible.windows.win_file:
    path: C:\AnsibleDemo\hello.txt
    state: touch

- name: Add content to the file
  ansible.windows.win_lineinfile:
    path: C:\AnsibleDemo\hello.txt
    line: "Hello from Ansible! Managed by Kerberos."
    state: present
```

### The Playbook (`site.yml`)

```yaml
---
- name: Configure Windows Server
  hosts: windows
  roles:
    - win_file_demo
```

### Running the Playbook

```bash
ansible-playbook -i inventory/hosts.ini site.yml
```

## 🔍 Troubleshooting

- **Kerberos Error**: "Kerberos: No credentials cache found" -> Run `kinit user@DOMAIN.COM` first.
- **Time Sync**: Kerberos requires time synchronization. Ensure both Linux and Windows clocks are within 5 minutes of each other.
- **DNS**: Ansible must be able to resolve the Windows hostname to an IP address.

## 🎓 Summary

You've learned how to:
1. Configure Windows for Ansible management.
2. Set up Kerberos on Linux.
3. Configure Ansible inventory for WinRM.
4. Write a playbook to manage Windows files.

Windows automation with Ansible is powerful and follows the same principles as Linux automation—just with different modules!
