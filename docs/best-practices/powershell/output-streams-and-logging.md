# PowerShell Best Practices: Output, Streams, and Logging

In PowerShell, effectively managing how your scripts output information is critical for creating tools that are both user-friendly and automation-compatible.

## The Golden Rule: Separate Status from Data

The single most important principle in PowerShell scripting is: **Do not mix human-readable status messages with machine-readable data output.**

*   **Status Messages** (e.g., "Starting...", "Connected to X", "Success") are for the **User Interface**.
*   **Data** (e.g., File objects, Database rows, Server configs) is for the **Pipeline**.

If you send "Starting..." text to the pipeline along with your data objects, you pollute the output, causing downstream automation to fail or behave unpredictably.

## Understanding the Streams

PowerShell provides different streams for different purposes. Using them correctly is key to following the Golden Rule.

### 1. The Output Stream (Pipeline)
*   **Command**: `Write-Output` (or mostly just implicit output)
*   **Purpose**: **Data Payload**. This is what your function *returns*.
*   **Target**: The next command in the pipeline (`|`), a variable assignment (`$x = ...`), or the console if not captured.
*   **Best Practice**: Only put clean, structured objects here.

### 2. The Information Stream (Host)
*   **Command**: `Write-Host`
*   **Purpose**: **User Interface**. Status updates, start/stop banners, simple progress indicators.
*   **Target**: The Console Host directly. It **bypasses the pipeline**.
*   **Best Practice**: Use this for message you strictly want the *operator* to see, but perfectly safe to ignore for automation.

### 3. The Verbose Stream
*   **Command**: `Write-Verbose`
*   **Purpose**: **Debugging / Detailed tracing**.
*   **Target**: Hidden by default. Visible only when `-Verbose` switch is used.
*   **Best Practice**: Use liberally for internal logic steps ("Checking registry key...", "Calculating hash...").

## Implementation Patterns

### The Anti-Pattern (What NOT to do)
Sending status text to the pipeline creates "mixed" arrays that break code.

```powershell
# BAD PRACTICE
function Get-ServerInfo {
    Write-Output "Starting search..."      # <--- POLLUTION

    $info = @{ Name = "Server01"; IP = "10.0.0.1" }

    Write-Output "Found server!"           # <--- POLLUTION
    return $info
}

# The consequence:
$result = Get-ServerInfo
# $result is now an array: ["Starting search...", "Found server!", @{Name="Server01"...}]
# $result.Name will be null or error because the first item is a string!
```

### The Best Practice Pattern
Use `Write-Host` for status to keep the pipeline pure for data.

```powershell
# BEST PRACTICE
function Get-ServerInfo {
    # 1. Status goes to Host (Bypasses Pipeline)
    Write-Host "Starting search..." -ForegroundColor Cyan

    $info = @{ Name = "Server01"; IP = "10.0.0.1" }

    # 2. Detailed tracing goes to Verbose (Hidden by default)
    Write-Verbose "Database query completed in 2ms."

    # 3. Status goes to Host
    Write-Host "Found server!" -ForegroundColor Green

    # 4. ONLY Data goes to Pipeline
    return $info
}

# The result:
$result = Get-ServerInfo
# Console shows: "Starting search..." then "Found server!"
# $result contains ONLY: @{Name="Server01"; IP="10.0.0.1"}
# $result.Name works perfectly.
```

## Summary Recommendation

When writing "Controller" scripts or Functions:

1.  Use `Write-Host` for "Start", "Success", and critical "Warning" messages meant for the human operator.
2.  Use `Write-Verbose` for all technical step-by-step logging.
3.  Use `Write-Output` (or implicit return) **only** for the actual objects/data your tool is designed to produce.
