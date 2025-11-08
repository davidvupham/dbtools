# GDS.Common Logging Functional Specification

## 1. Purpose

Provide a shared, PSFramework-based logging layer for all GDS PowerShell scripts and modules. The layer delivers consistent log ownership, centralised configuration, and cross-module attribution without modifying PSFramework itself.

## 2. Scope

- Public functions: `Initialize-Logging`, `Set-GDSLogging`, `Write-Log`
- Private helpers: `Resolve-GDSModuleName`, `Resolve-GDSModuleTag`, `Get-GDSLogRoot`
- Behaviour is consistent across Windows, Linux, and macOS (PowerShell 5.1+ / 7+).

## 3. High-Level Behaviour

1. **Log ownership based on scripts**
   - When a PowerShell script invokes `Initialize-Logging` or `Write-Log` without a `-ModuleName` override, the log owner defaults to the calling script name (derived from the call stack).
   - All downstream modules called by that script share the same log file: `<GDS_LOG_DIR>/<ScriptName>_<yyyyMMdd>.log`.

2. **Module attribution retained**
   - Each log entry is tagged with both the log owner (script) and the emitting module name, allowing developers to see which component produced the message without separate log files.

3. **PSFramework handles outputs**
   - File logging, console output, and (optionally) Windows Event Log are configured via [PSFramework logging providers](https://psframework.org/documentation/documents/psframework/logging.html).
   - PSFramework manages rotation, retention, and asynchronous dispatch.

4. **Cross-platform storage**
   - `GDS_LOG_DIR` environment variable defines the root log directory.
   - Windows fallback: `GDS_LOG_DIR` → `M:\GDS\Logs` (if drive exists) → `%ALLUSERSPROFILE%\GDS\Logs`; the directory is created when missing.
   - Linux/macOS fallback: `GDS_LOG_DIR` → `/gds/logs` (if the directory exists) → `/var/log/gds`.

## 4. Component Responsibilities

### 4.1 `Initialize-Logging`

- Imports PSFramework on demand.
- Determines the log owner via `Resolve-GDSModuleName` (default script name; optional override).
- Persists the minimum log level in PSFramework configuration (`GDS.Common.Logging.<Owner>.MinimumLevel`).
- Resolves the log root location (`Get-GDSLogRoot`) or custom `-LogPath`.
- Creates missing directories.
- Configures PSFramework providers:
  - `logfile` (owner-specific instance) → enabled.
  - `console` → enabled for informational output.
  - Logs an “initialized” message via `Write-PSFMessage`.
- Throws with guidance if no writable log directory is found.

### 4.2 `Set-GDSLogging`

- Shares the owner-detection and configuration logic with `Initialize-Logging`.
- Persists the minimum log level (same key as above).
- Configures providers based on switches:
  - `-EnableFileLog` → toggles `logfile` provider; enforces directory checks.
  - `-EnableConsoleLog` → toggles console provider.
  - `-EnableEventLog` → enables Windows Event Log provider when on Windows (no-op elsewhere) and writes configuration messages.
- Honors custom `-LogPath` identical to `Initialize-Logging`.

### 4.3 `Write-Log`

- Enforces the configured minimum level before invoking PSFramework.
- Defaults `-ModuleName` to the resolved log owner (calling script) while still detecting the emitting module via `Resolve-GDSModuleTag`.
- Assembles tags:
  - Log owner (script) tag.
  - Emitting module tag (if detected).
  - Any caller-provided tags.
- Builds structured metadata (`Target`):
  - Includes `Context` and `Exception` details when provided.
  - Adds `Target.Module` so PSFramework consumers can filter by module.
- Calls `Write-PSFMessage` with mapped PSFramework severity levels.
- Falls back to `Write-Warning` if PSFramework logging fails.

### 4.4 Log Owner & Configuration Scope

- The **log owner** is the canonical name used for:
  - Naming the log file (`<GDS_LOG_DIR>/<LogOwner>_<yyyyMMdd>.log`).
  - Scoping PSFramework configuration keys (`GDS.Common.Logging.<LogOwner>.*`).
- When `-ModuleName`/`-LogOwner`/`-LogFileName` is omitted, the helpers derive the log owner from the first script (`.ps1`) in the call stack. This keeps every module invoked by that script writing into a single owner-specific log file.
- Supplying the parameter explicitly allows multiple scripts to share a log folder or to redirect logs to a shared owner (e.g. a scheduled task or service name).
- Stored PSFramework configuration (e.g. minimum log level) is retrieved by that same owner name in `Write-Log`, ensuring consistent behaviour across `Initialize-Logging`, `Set-GDSLogging`, and `Write-Log`.

## 5. Helper Functions

### 5.1 `Resolve-GDSModuleName`

- Accepts an explicit name or inspects the call stack.
- Reverse-iterates frames to find the first `.ps1` script name → returns file stem (log owner).
- If no script is found, searches for modules with `GDS.*` patterns (legacy behaviour).
- Defaults to `GDS.Common` when nothing else matches.

### 5.2 `Resolve-GDSModuleTag`

- Walks the call stack in order to identify the first module path (`GDS.*`) and returns the module name for tagging.

### 5.3 `Get-GDSLogRoot`

- Checks `GDS_LOG_DIR` (process/environment).
- If undefined and on Windows:
  - Uses `M:\GDS\Logs` when `M:` exists.
  - Otherwise `%ALLUSERSPROFILE%\GDS\Logs` (falls back to `C:\ProgramData` if unset).
- If undefined and on Linux/macOS:
  - Uses `/gds/logs` when the directory exists.
  - Otherwise `/var/log/gds`.
- Creates the directory if missing and sets `GDS_LOG_DIR` for the session.
- Non-Windows without a writable fallback throws when creation fails.

## 6. Inputs & Configuration

- **Environment variables**: `GDS_LOG_DIR`, `ALLUSERSPROFILE` (Windows only), standard PSFramework configuration keys.
- **Function parameters**:
  - `ModuleName` (log owner override).
  - `LogPath` (absolute or relative).
  - `LogLevel` / `MinimumLevel`.
  - Provider toggles (`EnableFileLog`, `EnableConsoleLog`, `EnableEventLog`).
  - Contextual `Write-Log` parameters (`Message`, `Level`, `Context`, `Exception`, `Tag`).

## 7. Outputs & Side Effects

- Log files: `<LogRoot>/<Owner>_<yyyyMMdd>.log` (rolling daily).
- Console output via PSFramework console provider when enabled.
- Windows Event Log entries if enabled.
- PSFramework’s in-memory message cache populated for `Get-PSFMessage`.

## 8. Error Handling

- Missing writable log directory: `Initialize-Logging`/`Set-GDSLogging` throw with guidance.
- Event log registration issues (missing privileges): warning + skip provider.
- `Write-Log` exceptions: fallback to warnings with original message.

## 9. Security & Compliance

- Sensitive data is not automatically redacted; callers must avoid logging secrets.
- Directories inherit system defaults; deployment scripts should secure permissions as required.

## 10. Performance Considerations

- Leverages PSFramework’s asynchronous, runspace-safe logging to minimise blocking.
- Level filtering short-circuits low-priority events before calling PSFramework.

## 11. Testing

- Pester suite (`PowerShell/Modules/GDS.Common/Tests/GDS.Common.Tests.ps1`) verifies:
  - Owner detection (script default, hyphenated names).
  - Directory fallbacks (`GDS_LOG_DIR`, Windows defaults).
  - Provider configuration toggles.
  - `Write-Log` tagging and threshold enforcement.
- Tests mock PSFramework cmdlets to keep execution deterministic.

## 12. Known Limitations & Future Work

- Rotation/retention tuning still requires PSFramework config (`PSFramework.Logging.FileSystem.*`).
- No built-in masking for sensitive values.
- Does not automatically stream to external sinks (Splunk, Azure, etc.); rely on PSFramework providers if needed.
- Additional automation could inject machine- or environment-specific tags via `Write-Log`.
