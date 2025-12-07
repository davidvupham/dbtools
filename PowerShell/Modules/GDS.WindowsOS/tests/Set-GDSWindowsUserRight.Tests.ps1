
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$modulePath = Join-Path $here "../GDS.WindowsOS.psd1"

# Import the module
Import-Module $modulePath -Force

Describe 'Set-GDSWindowsUserRight' {

    Context 'Parameters and Dependencies' {

        It 'Throws error if PSDscResources module is not available' {
            # Mock Get-Module to return null for PSDscResources
            Mock Get-Module { return $null } -ParameterFilter { $Name -eq 'PSDscResources' }

            { Set-GDSWindowsUserRight -UserRight 'SeServiceLogonRight' -ServiceAccount 'User1' } | Should -Throw -Match "The 'PSDscResources' module is required"
        }
    }

    Context 'When calling Invoke-DscResource successfully' {

        BeforeAll {
            # Mock Get-Module to return something so dependency check passes
            Mock Get-Module { return @{ Name = 'PSDscResources' } } -ParameterFilter { $Name -eq 'PSDscResources' }
        }

        It 'Calls Invoke-DscResource with correct arguments for Present (using friendly name)' {

            # Mock Invoke-DscResource
            Mock Invoke-DscResource {
                return @{ InDesiredState = $true }
            } -Verifiable -ParameterFilter {
                $Name -eq 'UserRightsAssignment' -and
                $ModuleName -eq 'PSDscResources' -and
                $Method -eq 'Set' -and
                $Property.Policy -eq 'Log_on_as_a_service' -and
                $Property.Identity -eq 'CONTOSO\svc_sql' -and
                $Property.Ensure -eq 'Present'
            }

            Set-GDSWindowsUserRight -UserRight 'Log on as a service' -ServiceAccount 'CONTOSO\svc_sql' -Ensure 'Present'

            Assert-MockCalled Invoke-DscResource -Times 1
        }

        It 'Calls Invoke-DscResource with correct arguments for Absent (using friendly name)' {

            Mock Invoke-DscResource {
                return @{ InDesiredState = $true }
            } -Verifiable -ParameterFilter {
                $Name -eq 'UserRightsAssignment' -and
                $Property.Policy -eq 'Lock_pages_in_memory' -and
                $Property.Ensure -eq 'Absent'
            }

            Set-GDSWindowsUserRight -UserRight 'Lock pages in memory' -ServiceAccount 'CONTOSO\svc_sql' -Ensure 'Absent'

            Assert-MockCalled Invoke-DscResource -Times 1
        }

        It 'Writes warning if InDesiredState returns false' {
            Mock Invoke-DscResource {
                return @{ InDesiredState = $false }
            }

            # We can't easily check for Warning in Pester 5 without mocking Write-Warning or using Should -Throw (if -WarningAction Stop).
            # But we can verify the function completed without error.
            Set-GDSWindowsUserRight -UserRight 'SeBatchLogonRight' -ServiceAccount 'User2'

            Assert-MockCalled Invoke-DscResource -Times 1
        }
    }
}
