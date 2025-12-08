# GDS.Logging Module

# Load private functions
$privatePath = Join-Path -Path $PSScriptRoot -ChildPath 'Private'
if (Test-Path -Path $privatePath) {
    Get-ChildItem -Path $privatePath -Filter '*.ps1' -Recurse -ErrorAction SilentlyContinue |
        ForEach-Object { . $_.FullName }
}

# Load public functions
$publicPath = Join-Path -Path $PSScriptRoot -ChildPath 'Public'
$publicFunctions = @()
if (Test-Path -Path $publicPath) {
    $publicFunctions = Get-ChildItem -Path $publicPath -Filter '*.ps1' -Recurse -ErrorAction SilentlyContinue
    foreach ($function in $publicFunctions) {
        . $function.FullName
    }
}

# Export public functions
$publicFunctions | ForEach-Object {
    $functionName = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
    Export-ModuleMember -Function $functionName
}
