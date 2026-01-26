# Test DNS resolution
# Docs: https://learn.microsoft.com/en-us/powershell/module/dnsclient/resolve-dnsname
Resolve-DnsName -Name $args[0]

# Test TCP connectivity
# Docs: https://learn.microsoft.com/en-us/powershell/module/nettcpip/test-netconnection
Test-NetConnection -ComputerName $args[0] -Port $args[1]
