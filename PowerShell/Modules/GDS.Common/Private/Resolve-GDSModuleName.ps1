function Resolve-GDSModuleName {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [string]$ExplicitName,

        [Parameter(Mandatory = $false)]
        [object[]]$CallStack,

        [Parameter(Mandatory = $false)]
        [string]$DefaultName = 'GDS.Common'
    )

    if (-not [string]::IsNullOrWhiteSpace($ExplicitName)) {
        return $ExplicitName
    }

    if (-not $CallStack) {
        $CallStack = @()
    }

    $skipFunctions = @('Resolve-GDSModuleName', 'Initialize-Logging', 'Set-GDSLogging', 'Write-Log')

    foreach ($frame in $CallStack) {
        if (-not $frame) { continue }

        $functionName = $frame | Select-Object -ExpandProperty FunctionName -ErrorAction SilentlyContinue
        if ($functionName -and $skipFunctions -contains $functionName) { continue }

        $scriptPath = $frame | Select-Object -ExpandProperty ScriptName -ErrorAction SilentlyContinue
        if ([string]::IsNullOrWhiteSpace($scriptPath)) { continue }

        $candidate = Get-GDSModuleNameFromPath -Path $scriptPath
        if (-not [string]::IsNullOrWhiteSpace($candidate)) {
            return $candidate
        }
    }

    return $DefaultName
}

function Get-GDSModuleNameFromPath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [string]$Path
    )

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return $null
    }

    $segments = $Path -split '[\\/]+'
    for ($index = $segments.Length - 1; $index -ge 0; $index--) {
        $segment = $segments[$index]
        if ([string]::IsNullOrWhiteSpace($segment)) { continue }
        if ($segment -like 'GDS.*') {
            if ($segment.Length -gt 4 -and $segment.StartsWith('GDS.')) {
                return $segment.Substring(4)
            }
            return $segment
        }
    }

    return $null
}
