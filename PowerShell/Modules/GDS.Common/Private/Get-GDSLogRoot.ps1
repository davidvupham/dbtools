function Get-GDSLogRoot {
    [CmdletBinding()]
    param()

    $logDirectoryValue = $env:GDS_LOG_DIR
    if ([string]::IsNullOrWhiteSpace($logDirectoryValue)) {
        $logDirectoryValue = [Environment]::GetEnvironmentVariable('GDS_LOG_DIR', 'Process')
    }

    if (-not [string]::IsNullOrWhiteSpace($logDirectoryValue)) {
        return [Environment]::ExpandEnvironmentVariables($logDirectoryValue)
    }

    $isWindows = $false
    if (Get-Variable -Name IsWindows -ErrorAction SilentlyContinue) {
        $isWindows = $IsWindows
    }
    else {
        $isWindows = [System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform([System.Runtime.InteropServices.OSPlatform]::Windows)
    }

    if (-not $isWindows) {
        $linuxPath = $null

        if (Test-Path -LiteralPath '/gds/log') {
            $linuxPath = '/gds/log'
        }
        else {
            $linuxPath = '/var/log/gds'
        }

        try {
            if (-not (Test-Path -LiteralPath $linuxPath)) {
                New-Item -ItemType Directory -Path $linuxPath -Force | Out-Null
            }
        }
        catch {
            throw "Failed to create or access log directory '$linuxPath' on Linux/macOS: $_"
        }

        return $linuxPath
    }

    $candidatePath = $null
    if (Test-Path -LiteralPath 'M:\') {
        $candidatePath = Join-Path -Path 'M:\' -ChildPath 'GDS\Logs'
    }
    else {
        $allUsersProfile = $env:ALLUSERSPROFILE
        if ([string]::IsNullOrWhiteSpace($allUsersProfile)) {
            $allUsersProfile = [Environment]::GetEnvironmentVariable('ALLUSERSPROFILE', 'Machine')
        }
        if ([string]::IsNullOrWhiteSpace($allUsersProfile)) {
            $allUsersProfile = 'C:\ProgramData'
        }

        $candidatePath = Join-Path -Path $allUsersProfile -ChildPath 'GDS\Logs'
    }

    try {
        $expandedCandidate = [Environment]::ExpandEnvironmentVariables($candidatePath)
        if (-not (Test-Path -LiteralPath $expandedCandidate)) {
            New-Item -ItemType Directory -Path $expandedCandidate -Force | Out-Null
        }

        if ([string]::IsNullOrWhiteSpace($env:GDS_LOG_DIR)) {
            $env:GDS_LOG_DIR = $expandedCandidate
        }

        return $expandedCandidate
    }
    catch {
        return $candidatePath
    }
}
