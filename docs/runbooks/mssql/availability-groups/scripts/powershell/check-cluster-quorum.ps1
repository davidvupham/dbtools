# Check cluster quorum status
# Docs: https://learn.microsoft.com/en-us/powershell/module/failoverclusters/get-clusterquorum
Get-ClusterQuorum | Select-Object Cluster, QuorumResource, QuorumType

# Check cluster health
# Docs: https://learn.microsoft.com/en-us/powershell/module/failoverclusters/get-cluster
Get-Cluster | Select-Object Name, QuorumType, CrossSiteThreshold
