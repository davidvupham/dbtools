
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$modulePath = Join-Path $here "../GDS.Windows.psd1"

# Import the module
Import-Module $modulePath -Force

Describe 'Set-GDSWindowsUserRight' {

    Context 'When calling Invoke-DscResource successfully' {

        It 'Calls Invoke-DscResource with correct arguments for Present (using friendly name)' {
            Mock Get-Module { @{ Name = 'PSDscResources' } } -ModuleName 'GDS.Windows'
            Mock Invoke-DscResource { return @{ InDesiredState = $true } } -ModuleName 'GDS.Windows'

            Set-GDSWindowsUserRight -UserRight 'Log on as a service' -ServiceAccount 'CONTOSO\svc_sql' -Ensure 'Present'

            Should -Invoke Invoke-DscResource -Times 1 -ModuleName 'GDS.Windows' -ParameterFilter {
                $Name -eq 'UserRightsAssignment' -and
                $ModuleName -eq 'PSDscResources' -and
                $Method -eq 'Set' -and
                $Property.Policy -eq 'Log_on_as_a_service' -and
                $Property.Identity -eq 'CONTOSO\svc_sql' -and
                $Property.Ensure -eq 'Present'
            }
        }

        It 'Calls Invoke-DscResource with correct arguments for Absent (using friendly name)' {
            Mock Get-Module { @{ Name = 'PSDscResources' } } -ModuleName 'GDS.Windows'
            Mock Invoke-DscResource { return @{ InDesiredState = $true } } -ModuleName 'GDS.Windows'

            Set-GDSWindowsUserRight -UserRight 'Lock pages in memory' -ServiceAccount 'CONTOSO\svc_sql' -Ensure 'Absent'

            Should -Invoke Invoke-DscResource -Times 1 -ModuleName 'GDS.Windows' -ParameterFilter {
                $Name -eq 'UserRightsAssignment' -and
                $Property.Policy -eq 'Lock_pages_in_memory' -and
                $Property.Ensure -eq 'Absent'
            }
        }

        It 'Writes warning if InDesiredState returns false' {
            Mock Get-Module { @{ Name = 'PSDscResources' } } -ModuleName 'GDS.Windows'
            Mock Invoke-DscResource { return @{ InDesiredState = $false } } -ModuleName 'GDS.Windows'

            Set-GDSWindowsUserRight -UserRight 'SeBatchLogonRight' -ServiceAccount 'User2'

            Should -Invoke Invoke-DscResource -Times 1 -ModuleName 'GDS.Windows'
        }

        It 'Handles multiple user rights in a single call' {
            Mock Get-Module { @{ Name = 'PSDscResources' } } -ModuleName 'GDS.Windows'
            Mock Invoke-DscResource { return @{ InDesiredState = $true } } -ModuleName 'GDS.Windows'

            Set-GDSWindowsUserRight -UserRight 'Log on as a service', 'Lock pages in memory' -ServiceAccount 'CONTOSO\svc_sql'

            Should -Invoke Invoke-DscResource -Times 2 -ModuleName 'GDS.Windows'
        }

        It 'Passes through unmapped policy names directly (e.g., SeServiceLogonRight)' {
            Mock Get-Module { @{ Name = 'PSDscResources' } } -ModuleName 'GDS.Windows'
            Mock Invoke-DscResource { return @{ InDesiredState = $true } } -ModuleName 'GDS.Windows'

            Set-GDSWindowsUserRight -UserRight 'SeServiceLogonRight' -ServiceAccount 'User1'

            Should -Invoke Invoke-DscResource -Times 1 -ModuleName 'GDS.Windows' -ParameterFilter {
                $Property.Policy -eq 'SeServiceLogonRight'
            }
        }
    }
}
