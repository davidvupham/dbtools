
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$modulePath = Join-Path $here "../GDS.WindowsOS.psd1"

# Import the module
Import-Module $modulePath -Force

Describe 'Set-GDSSqlServiceUserRights' {

    Context 'When calling with explicit ServiceAccount' {

        It 'Calls Set-GDSWindowsUserRight with correct SQL rights' {

            # Mock Set-GDSWindowsUserRight
            Mock Set-GDSWindowsUserRight { } -Verifiable -ParameterFilter {
                $ServiceAccount -eq 'CONTOSO\svc_sql' -and
                $UserRight -contains 'Log on as a service' -and
                $UserRight -contains 'Perform volume maintenance tasks' -and
                $UserRight -contains 'Lock pages in memory' -and
                $Ensure -eq 'Present'
            }

            Set-GDSSqlServiceUserRights -ServiceAccount 'CONTOSO\svc_sql'

            Assert-MockCalled Set-GDSWindowsUserRight -Times 1
        }
    }

    Context 'When auto-detecting service account' {

        It 'Looks up service account from Win32_Service and calls Set-GDSWindowsUserRight' {

            # Mock Get-CimInstance for Win32_Service
            Mock Get-CimInstance {
                return [PSCustomObject]@{
                    Name      = 'MSSQLSERVER'
                    StartName = 'NT SERVICE\MSSQLSERVER'
                }
            } -ParameterFilter { $ClassName -eq 'Win32_Service' -and $Filter -eq "Name = 'MSSQLSERVER'" }

            # Mock Set-GDSWindowsUserRight
            Mock Set-GDSWindowsUserRight { } -Verifiable -ParameterFilter {
                $ServiceAccount -eq 'NT SERVICE\MSSQLSERVER' -and
                $Ensure -eq 'Present'
            }

            Set-GDSSqlServiceUserRights -ServiceName 'MSSQLSERVER'

            Assert-MockCalled Set-GDSWindowsUserRight -Times 1
        }

        It 'Throws error if service is not found' {
            # Mock Get-CimInstance to return null
            Mock Get-CimInstance { return $null }

            { Set-GDSSqlServiceUserRights -ServiceName 'INVALIDSERVICE' } | Should -Throw -Match "Service 'INVALIDSERVICE' not found"
        }
    }
}
