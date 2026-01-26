# Check cluster node status
# Docs: https://learn.microsoft.com/en-us/powershell/module/failoverclusters/get-clusternode
Get-ClusterNode | Select-Object Name, State, NodeWeight

# Check node drain/quarantine status
# Docs: https://learn.microsoft.com/en-us/powershell/module/failoverclusters/get-clusternode
Get-ClusterNode | Select-Object Name, State, DrainStatus, QuarantineStatus
