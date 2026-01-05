# StructuredLogger.psm1 - Structured JSON Logging for PowerShell

class StructuredLogger {
    [string]$LogPath
    [string]$MinLevel
    [string]$CorrelationId
    [string]$TraceId
    [string]$SpanId
    hidden [hashtable]$LevelPriority = @{
        Debug       = 0
        Verbose     = 1
        Information = 2
        Warning     = 3
        Error       = 4
        Critical    = 5
    }

    StructuredLogger([string]$logPath, [string]$minLevel) {
        $this.LogPath = $logPath
        $this.MinLevel = $minLevel
        $this.CorrelationId = [Guid]::NewGuid().ToString()
        $this.NewTraceContext()
    }

    [void] NewTraceContext() {
        $this.TraceId = [Guid]::NewGuid().ToString("N") + [Guid]::NewGuid().ToString("N").Substring(0, 16)
        $this.SpanId = [Guid]::NewGuid().ToString("N").Substring(0, 16)
    }

    [string] GetTraceParent() {
        return "00-$($this.TraceId)-$($this.SpanId)-01"
    }

    [void] Log([string]$level, [string]$message, [hashtable]$context) {
        if ($this.LevelPriority[$level] -lt $this.LevelPriority[$this.MinLevel]) {
            return
        }

        $entry = [ordered]@{
            timestamp     = (Get-Date).ToUniversalTime().ToString('o')
            level         = $level
            message       = $message
            correlationId = $this.CorrelationId
            traceId       = $this.TraceId
            spanId        = $this.SpanId
            context       = $context
        }

        $json = $entry | ConvertTo-Json -Compress -Depth 5

        # Write to file
        Add-Content -Path $this.LogPath -Value $json -Encoding UTF8

        # Also output to console based on level
        switch ($level) {
            'Debug'       { Write-Debug $json }
            'Verbose'     { Write-Verbose $json }
            'Information' { Write-Information $json -InformationAction Continue }
            'Warning'     { Write-Warning $json }
            'Error'       { Write-Error $json }
            'Critical'    { Write-Error $json }
        }
    }

    [void] Debug([string]$message, [hashtable]$context = @{}) {
        $this.Log('Debug', $message, $context)
    }

    [void] Verbose([string]$message, [hashtable]$context = @{}) {
        $this.Log('Verbose', $message, $context)
    }

    [void] Info([string]$message, [hashtable]$context = @{}) {
        $this.Log('Information', $message, $context)
    }

    [void] Warning([string]$message, [hashtable]$context = @{}) {
        $this.Log('Warning', $message, $context)
    }

    [void] Error([string]$message, [hashtable]$context = @{}) {
        $this.Log('Error', $message, $context)
    }

    [void] Critical([string]$message, [hashtable]$context = @{}) {
        $this.Log('Critical', $message, $context)
    }
}

# Factory function
function New-StructuredLogger {
    param(
        [Parameter(Mandatory)]
        [string]$LogPath,

        [ValidateSet('Debug', 'Verbose', 'Information', 'Warning', 'Error', 'Critical')]
        [string]$MinLevel = 'Information'
    )

    # Ensure log directory exists
    $dir = Split-Path -Parent $LogPath
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    return [StructuredLogger]::new($LogPath, $MinLevel)
}

# Sensitive data redaction
function Get-RedactedContext {
    param([hashtable]$Context)

    $sensitiveKeys = @('password', 'secret', 'token', 'apikey', 'credential', 'connectionstring')
    $redacted = @{}

    foreach ($key in $Context.Keys) {
        $value = $Context[$key]
        $keyLower = $key.ToLower()

        $isSensitive = $sensitiveKeys | Where-Object { $keyLower -like "*$_*" }

        if ($isSensitive) {
            $redacted[$key] = "[REDACTED length=$($value.Length)]"
        }
        elseif ($value -is [hashtable]) {
            $redacted[$key] = Get-RedactedContext -Context $value
        }
        else {
            $redacted[$key] = $value
        }
    }

    return $redacted
}

Export-ModuleMember -Function New-StructuredLogger, Get-RedactedContext
