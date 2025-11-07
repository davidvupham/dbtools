# GDS.Common Module

# Load private functions
$privateFunctions = Get-ChildItem -Path "$PSScriptRoot\private" -Filter "*.ps1" -Recurse -ErrorAction SilentlyContinue
foreach ($function in $privateFunctions) {
    . $function.FullName
}

# Load public functions
$publicFunctions = Get-ChildItem -Path "$PSScriptRoot\public" -Filter "*.ps1" -Recurse -ErrorAction SilentlyContinue
foreach ($function in $publicFunctions) {
    . $function.FullName
}

# Export public functions
$publicFunctions | ForEach-Object {
    $functionName = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
    Export-ModuleMember -Function $functionName
}
