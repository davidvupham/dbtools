$ErrorActionPreference = 'Stop'

BeforeAll {
    Import-Module Pester -MinimumVersion 5.0.0

    # Create stub functions for ActiveDirectory cmdlets that don't exist on Linux
    # These stubs allow Pester to mock them
    function global:Get-ADPrincipalGroupMembership {
        param([string]$Identity)
        throw "This is a stub function - should be mocked"
    }

    function global:Remove-ADGroupMember {
        param(
            [string]$Identity,
            [string]$Members,
            [switch]$Confirm,
            [string]$ErrorAction
        )
        throw "This is a stub function - should be mocked"
    }

    # Dot-source the functions directly instead of importing the module
    # This avoids the GDS.Logging dependency for unit testing
    . "$PSScriptRoot/../Public/Get-GdsUserGroupMembership.ps1"
    . "$PSScriptRoot/../Public/Remove-GdsUserGroupMembership.ps1"
}

AfterAll {
    # Clean up global stub functions
    Remove-Item -Path Function:\Get-ADPrincipalGroupMembership -ErrorAction SilentlyContinue
    Remove-Item -Path Function:\Remove-ADGroupMember -ErrorAction SilentlyContinue
}

Describe "User Group Membership Functions" {

    Context "Get-GdsUserGroupMembership" {
        BeforeEach {
            Mock Get-ADPrincipalGroupMembership {
                return @(
                    [PSCustomObject]@{ Name = 'SQL_Admin'; GroupCategory = 'Security'; DistinguishedName = 'CN=SQL_Admin,DC=com' },
                    [PSCustomObject]@{ Name = 'HR_User'; GroupCategory = 'Security'; DistinguishedName = 'CN=HR_User,DC=com' }
                )
            }
        }

        It "Should list all security groups for a user" {
            $result = Get-GdsUserGroupMembership -UserName 'jvaughn'
            $result.Count | Should -Be 2
            $result.Name | Should -Contain 'SQL_Admin'
            $result.Name | Should -Contain 'HR_User'
        }

        It "Should filter groups by name" {
            $result = Get-GdsUserGroupMembership -UserName 'jvaughn' -Filter 'SQL*'
            $result.Count | Should -Be 1
            $result.Name | Should -Be 'SQL_Admin'
        }

        It "Should return empty when no groups match filter" {
            $result = Get-GdsUserGroupMembership -UserName 'jvaughn' -Filter 'NonExistent*'
            $result | Should -BeNullOrEmpty
        }

        It "Should handle errors gracefully" {
            Mock Get-ADPrincipalGroupMembership { throw "User not found" }

            $result = Get-GdsUserGroupMembership -UserName 'invalid' -ErrorAction SilentlyContinue -ErrorVariable err
            $result | Should -BeNullOrEmpty
            $err | Should -Not -BeNullOrEmpty
            # Write-Error creates an ErrorRecord - check the full error string contains our message
            ($err | Out-String) | Should -Match "Failed to retrieve groups for user 'invalid'"
        }

        It "Should filter out Distribution groups" {
            Mock Get-ADPrincipalGroupMembership {
                return @(
                    [PSCustomObject]@{ Name = 'SQL_Admin'; GroupCategory = 'Security' },
                    [PSCustomObject]@{ Name = 'All_Staff'; GroupCategory = 'Distribution' }
                )
            }

            $result = Get-GdsUserGroupMembership -UserName 'jvaughn'
            $result.Count | Should -Be 1
            $result.Name | Should -Be 'SQL_Admin'
        }
    }

    Context "Remove-GdsUserGroupMembership" {
        BeforeEach {
            Mock Remove-ADGroupMember { }
        }

        It "Should remove user from group specified by parameter" {
            Remove-GdsUserGroupMembership -UserName 'jvaughn' -Group 'SQL_Admin'

            Should -Invoke Remove-ADGroupMember -Times 1 -ParameterFilter { $Identity -eq 'SQL_Admin' -and $Members -eq 'jvaughn' }
        }

        It "Should remove user from multiple groups via string array" {
            Remove-GdsUserGroupMembership -UserName 'jvaughn' -Group 'SQL_Admin', 'SQL_Reader'

            Should -Invoke Remove-ADGroupMember -Times 2
            Should -Invoke Remove-ADGroupMember -ParameterFilter { $Identity -eq 'SQL_Admin' }
            Should -Invoke Remove-ADGroupMember -ParameterFilter { $Identity -eq 'SQL_Reader' }
        }

        It "Should remove user from groups via pipeline" {
            'SQL_Admin', 'SQL_Reader' | Remove-GdsUserGroupMembership -UserName 'jvaughn'

            Should -Invoke Remove-ADGroupMember -Times 2
            Should -Invoke Remove-ADGroupMember -ParameterFilter { $Identity -eq 'SQL_Admin' }
            Should -Invoke Remove-ADGroupMember -ParameterFilter { $Identity -eq 'SQL_Reader' }
        }

        It "Should accept ADGroup objects via pipeline" {
            $groups = @(
                [PSCustomObject]@{ Name = 'SQL_Admin'; GroupCategory = 'Security' },
                [PSCustomObject]@{ Name = 'SQL_Reader'; GroupCategory = 'Security' }
            )

            $groups | Remove-GdsUserGroupMembership -UserName 'jvaughn'

            Should -Invoke Remove-ADGroupMember -Times 2
            Should -Invoke Remove-ADGroupMember -ParameterFilter { $Identity -eq 'SQL_Admin' }
        }

        It "Should support -WhatIf without making changes" {
            Remove-GdsUserGroupMembership -UserName 'jvaughn' -Group 'SQL_Admin' -WhatIf

            Should -Invoke Remove-ADGroupMember -Times 0
        }

        It "Should handle errors gracefully" {
            Mock Remove-ADGroupMember { throw "Access denied" }

            Remove-GdsUserGroupMembership -UserName 'jvaughn' -Group 'SQL_Admin' -ErrorAction SilentlyContinue -ErrorVariable err

            $err | Should -Not -BeNullOrEmpty
            # Write-Error creates an ErrorRecord - check the full error string contains our message
            ($err | Out-String) | Should -Match "Failed to remove user 'jvaughn' from group 'SQL_Admin'"
        }
    }

    Context "Integration Flow" {
        It "Should allow Get output to be piped to Remove" {
            Mock Get-ADPrincipalGroupMembership {
                return @(
                    [PSCustomObject]@{ Name = 'SQL_RemoveMe'; GroupCategory = 'Security' }
                )
            }
            Mock Remove-ADGroupMember { }

            Get-GdsUserGroupMembership -UserName 'jvaughn' -Filter 'SQL*' | Remove-GdsUserGroupMembership -UserName 'jvaughn'

            Should -Invoke Remove-ADGroupMember -Times 1 -ParameterFilter { $Identity -eq 'SQL_RemoveMe' }
        }

        It "Should handle empty Get results gracefully in pipeline" {
            Mock Get-ADPrincipalGroupMembership {
                return @(
                    [PSCustomObject]@{ Name = 'HR_Group'; GroupCategory = 'Security' }
                )
            }
            Mock Remove-ADGroupMember { }

            # Filter that matches nothing
            Get-GdsUserGroupMembership -UserName 'jvaughn' -Filter 'NonExistent*' | Remove-GdsUserGroupMembership -UserName 'jvaughn' -ErrorAction SilentlyContinue

            Should -Invoke Remove-ADGroupMember -Times 0
        }
    }
}
