
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$modulePath = Join-Path $here "../GDS.Windows.psd1"

# Import the module
Import-Module $modulePath -Force

Describe 'Set-GDSSqlServiceUserRights' {

    Context 'When calling with explicit ServiceAccount' {

        It 'Calls Set-GDSWindowsUserRight with correct SQL rights' {
            Mock Set-GDSWindowsUserRight { } -ModuleName 'GDS.Windows'

            Set-GDSSqlServiceUserRights -ServiceAccount 'CONTOSO\svc_sql'

            Should -Invoke Set-GDSWindowsUserRight -Times 1 -ModuleName 'GDS.Windows' -ParameterFilter {
                $ServiceAccount -eq 'CONTOSO\svc_sql' -and
                $UserRight -contains 'Log on as a service' -and
                $UserRight -contains 'Perform volume maintenance tasks' -and
                $UserRight -contains 'Lock pages in memory' -and
                $Ensure -eq 'Present'
            }
        }
    }

    Context 'When auto-detecting service account' {

        It 'Looks up service account from Win32_Service and calls Set-GDSWindowsUserRight' {
            Mock Set-GDSWindowsUserRight { } -ModuleName 'GDS.Windows'
            Mock Get-CimInstance { 
                return [PSCustomObject]@{
                    Name      = 'MSSQLSERVER'
                    StartName = 'NT SERVICE\MSSQLSERVER'
                }
            } -ModuleName 'GDS.Windows'

            Set-GDSSqlServiceUserRights -ServiceName 'MSSQLSERVER'

            Should -Invoke Set-GDSWindowsUserRight -Times 1 -ModuleName 'GDS.Windows' -ParameterFilter {
                $ServiceAccount -eq 'NT SERVICE\MSSQLSERVER' -and
                $Ensure -eq 'Present'
            }
        }
    }

    Context 'When revoking rights with Ensure = Absent' {

        It 'Calls Set-GDSWindowsUserRight with Ensure Absent' {
            Mock Set-GDSWindowsUserRight { } -ModuleName 'GDS.Windows'

            Set-GDSSqlServiceUserRights -ServiceAccount 'CONTOSO\svc_sql' -Ensure 'Absent'

            Should -Invoke Set-GDSWindowsUserRight -Times 1 -ModuleName 'GDS.Windows' -ParameterFilter {
                $ServiceAccount -eq 'CONTOSO\svc_sql' -and
                $Ensure -eq 'Absent'
            }
        }
    }
}
