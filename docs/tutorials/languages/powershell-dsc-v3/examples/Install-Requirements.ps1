# Install-Requirements.ps1
# Helper script to install dependencies for the DSC v3 examples

Write-Host "Installing required modules for DSC v3 Adapter examples..." -ForegroundColor Cyan

# Check for SecurityPolicyDsc (used in user_rights_assignment.dsc.json)
if (-not (Get-Module -ListAvailable -Name SecurityPolicyDsc)) {
    Write-Host "Installing SecurityPolicyDsc..."
    Install-Module -Name SecurityPolicyDsc -Force -Scope CurrentUser
}
else {
    Write-Host "SecurityPolicyDsc is already installed." -ForegroundColor Green
}

# Check for ComputerManagementDsc (used in legacy_adapter.dsc.json)
if (-not (Get-Module -ListAvailable -Name ComputerManagementDsc)) {
    Write-Host "Installing ComputerManagementDsc..."
    Install-Module -Name ComputerManagementDsc -Force -Scope CurrentUser
}
else {
    Write-Host "ComputerManagementDsc is already installed." -ForegroundColor Green
}

# Check for SqlServerDsc (used in sql examples)
if (-not (Get-Module -ListAvailable -Name SqlServerDsc)) {
    Write-Host "Installing SqlServerDsc..."
    Install-Module -Name SqlServerDsc -Force -Scope CurrentUser
}
else {
    Write-Host "SqlServerDsc is already installed." -ForegroundColor Green
}

Write-Host "Done. You can now use 'dsc config set' with the example JSON files." -ForegroundColor Green
