# Verify port is open on all nodes
# Docs: https://learn.microsoft.com/en-us/powershell/module/netsecurity/get-netfirewallrule
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*SQL*" -or $_.DisplayName -like "*1433*"}

# Create firewall rule if missing
# Docs: https://learn.microsoft.com/en-us/powershell/module/netsecurity/new-netfirewallrule
# New-NetFirewallRule -DisplayName "SQL Server Listener" -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow
