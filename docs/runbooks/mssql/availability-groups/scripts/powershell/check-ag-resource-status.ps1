# Check AG cluster resource status
# Docs: https://learn.microsoft.com/en-us/powershell/module/failoverclusters/get-clusterresource
Get-ClusterResource | Where-Object {$_.ResourceType -eq "SQL Server Availability Group"} |
    Select-Object Name, State, OwnerNode
