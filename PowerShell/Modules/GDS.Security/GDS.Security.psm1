# GDS.Security Module

# Load private functions
$privateFunctions = Get-ChildItem -Path "$PSScriptRoot\Private" -Filter "*.ps1" -Recurse
foreach ($function in $privateFunctions) {
    . $function.FullName
}

# Load public functions
$publicFunctions = Get-ChildItem -Path "$PSScriptRoot\Public" -Filter "*.ps1" -Recurse
foreach ($function in $publicFunctions) {
    . $function.FullName
}
