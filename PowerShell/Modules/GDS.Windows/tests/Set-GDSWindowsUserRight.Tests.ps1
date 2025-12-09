
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$modulePath = Join-Path $here "../GDS.Windows.psd1"

# Import the module
Import-Module $modulePath -Force

Describe 'Set-GDSWindowsUserRight' {

    BeforeAll {
        # Mock Carbon module availability
        Mock Get-Module { @{ Name = 'Carbon' } } -ModuleName 'GDS.Windows' -ParameterFilter { $ListAvailable -and $Name -eq 'Carbon' }
        Mock Import-Module { } -ModuleName 'GDS.Windows' -ParameterFilter { $Name -eq 'Carbon' }
    }

    Context 'When granting privileges (Ensure = Present)' {

        It 'Calls Grant-CPrivilege with correct privilege constant (using friendly name)' {
            Mock Grant-CPrivilege { } -ModuleName 'GDS.Windows'

            Set-GDSWindowsUserRight -UserRight 'Log on as a service' -ServiceAccount 'CONTOSO\svc_sql' -Ensure 'Present'

            Should -Invoke Grant-CPrivilege -Times 1 -ModuleName 'GDS.Windows' -ParameterFilter {
                $Identity -eq 'CONTOSO\svc_sql' -and
                $Privilege -eq 'SeServiceLogonRight'
            }
        }

        It 'Maps "Lock pages in memory" to SeLockMemoryPrivilege' {
            Mock Grant-CPrivilege { } -ModuleName 'GDS.Windows'

            Set-GDSWindowsUserRight -UserRight 'Lock pages in memory' -ServiceAccount 'CONTOSO\svc_sql'

            Should -Invoke Grant-CPrivilege -Times 1 -ModuleName 'GDS.Windows' -ParameterFilter {
                $Privilege -eq 'SeLockMemoryPrivilege'
            }
        }

        It 'Handles multiple user rights in a single call' {
            Mock Grant-CPrivilege { } -ModuleName 'GDS.Windows'

            Set-GDSWindowsUserRight -UserRight 'Log on as a service', 'Lock pages in memory' -ServiceAccount 'CONTOSO\svc_sql'

            Should -Invoke Grant-CPrivilege -Times 2 -ModuleName 'GDS.Windows'
        }

        It 'Passes through unmapped privilege names directly' {
            Mock Grant-CPrivilege { } -ModuleName 'GDS.Windows'

            Set-GDSWindowsUserRight -UserRight 'SeServiceLogonRight' -ServiceAccount 'User1'

            Should -Invoke Grant-CPrivilege -Times 1 -ModuleName 'GDS.Windows' -ParameterFilter {
                $Privilege -eq 'SeServiceLogonRight'
            }
        }
    }

    Context 'When revoking privileges (Ensure = Absent)' {

        It 'Calls Revoke-CPrivilege when Ensure is Absent' {
            Mock Revoke-CPrivilege { } -ModuleName 'GDS.Windows'

            Set-GDSWindowsUserRight -UserRight 'Lock pages in memory' -ServiceAccount 'CONTOSO\svc_sql' -Ensure 'Absent'

            Should -Invoke Revoke-CPrivilege -Times 1 -ModuleName 'GDS.Windows' -ParameterFilter {
                $Identity -eq 'CONTOSO\svc_sql' -and
                $Privilege -eq 'SeLockMemoryPrivilege'
            }
        }
    }

    Context 'Module dependency checks' {

        It 'Throws error if Carbon module is not available' {
            Mock Get-Module { $null } -ModuleName 'GDS.Windows' -ParameterFilter { $ListAvailable -and $Name -eq 'Carbon' }

            { Set-GDSWindowsUserRight -UserRight 'SeServiceLogonRight' -ServiceAccount 'User1' } | Should -Throw -Match "Carbon"
        }
    }
}
