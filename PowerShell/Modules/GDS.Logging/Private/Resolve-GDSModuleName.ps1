function Resolve-GDSModuleName {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [string]$ExplicitName,

        [Parameter(Mandatory = $false)]
        [object[]]$CallStack,

        [Parameter(Mandatory = $false)]
        [string]$DefaultName = 'GDS.Logging'
    )

    if (-not [string]::IsNullOrWhiteSpace($ExplicitName)) {
        return $ExplicitName
    }

    if (-not $CallStack) {
        $CallStack = @()
    }

    $frames = @($CallStack)
    if ($frames.Count -gt 0) {
        for ($index = $frames.Count - 1; $index -ge 0; $index--) {
            $frame = $frames[$index]
            if (-not $frame) { continue }

            $scriptPath = $frame | Select-Object -ExpandProperty ScriptName -ErrorAction SilentlyContinue
            if ([string]::IsNullOrWhiteSpace($scriptPath)) { continue }

            if ($scriptPath -like '*.ps1') {
                $scriptName = [System.IO.Path]::GetFileNameWithoutExtension($scriptPath)
                if (-not [string]::IsNullOrWhiteSpace($scriptName)) {
                    return $scriptName
                }
            }
        }

        foreach ($frame in $frames) {
            if (-not $frame) { continue }

            $scriptPath = $frame | Select-Object -ExpandProperty ScriptName -ErrorAction SilentlyContinue
            if ([string]::IsNullOrWhiteSpace($scriptPath)) { continue }

            $candidate = Get-GDSModuleNameFromPath -Path $scriptPath
            if (-not [string]::IsNullOrWhiteSpace($candidate)) {
                return $candidate
            }
        }
    }

    return $DefaultName
}

function Resolve-GDSModuleTag {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [object[]]$CallStack
    )

    if (-not $CallStack) {
        return $null
    }

    foreach ($frame in $CallStack) {
        if (-not $frame) { continue }

        $scriptPath = $frame | Select-Object -ExpandProperty ScriptName -ErrorAction SilentlyContinue
        if ([string]::IsNullOrWhiteSpace($scriptPath)) { continue }

        $candidate = Get-GDSModuleNameFromPath -Path $scriptPath
        if (-not [string]::IsNullOrWhiteSpace($candidate)) {
            return $candidate
        }
    }

    return $null
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
