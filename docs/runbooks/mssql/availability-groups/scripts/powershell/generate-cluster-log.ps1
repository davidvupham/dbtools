# Generate cluster log for troubleshooting
# Docs: https://learn.microsoft.com/en-us/powershell/module/failoverclusters/get-clusterlog
Get-ClusterLog -Destination C:\Temp -TimeSpan 60 -UseLocalTime

# Search for relevant events
# Select-String -Path "C:\Temp\*.log" -Pattern "lease|timeout|quorum|heartbeat" -Context 2,2
