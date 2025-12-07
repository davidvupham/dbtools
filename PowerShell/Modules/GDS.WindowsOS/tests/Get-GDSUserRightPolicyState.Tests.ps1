
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$modulePath = Join-Path $here "../GDS.WindowsOS.psd1"

# Import the module
Import-Module $modulePath -Force

Describe 'Get-GDSUserRightPolicyState' {

  # Mock System.IO.Path to return a consistent temp file name we can mock against
  # Note: Mocking .NET static methods requires exact signature matching or broad mocks if supported.
  # Pester 5 mocks PowerShell commands easily.
  # The function calls: $tempFile = [System.IO.Path]::GetTempFileName()
  # Pester cannot easily mock .NET methods.
  # Workaround: valid temp file will be created by the system. We just need to mock Test-Path and Get-Content.

  InModuleScope 'GDS.WindowsOS' {
    Context 'When gpresult runs successfully' {

      It 'Returns managed=true when User Right is present in GPO' {
        # Mock Start-Process to return Success
        Mock Start-Process {
          return [PSCustomObject]@{ ExitCode = 0 }
        }

        # Mock Test-Path to simulate file existence
        Mock Test-Path { return $true }

        # Mock Get-Content to return valid XML with the right
        Mock Get-Content {
          return @"
<Rsop>
  <ComputerResults>
    <ExtensionData>
      <Name>Security</Name>
      <Extension>
        <UserRightsAssignment>
          <Name>SeServiceLogonRight</Name>
          <Member>S-1-5-20</Member>
        </UserRightsAssignment>
      </Extension>
    </ExtensionData>
  </ComputerResults>
</Rsop>
"@
        }

        # Mock Remove-Item to do nothing
        Mock Remove-Item { }

        $result = Get-GDSUserRightPolicyState -UserRight 'SeServiceLogonRight'

        $result.UserRight | Should -Be 'SeServiceLogonRight'
        $result.IsManagedByGPO | Should -Be $true
      }

      It 'Returns managed=false when User Right is NOT present in GPO' {
        # Mock Start-Process to return Success
        Mock Start-Process {
          return [PSCustomObject]@{ ExitCode = 0 }
        }

        # Mock Test-Path
        Mock Test-Path { return $true }

        # Mock Get-Content to return valid XML WITHOUT the right
        Mock Get-Content {
          return @"
<Rsop>
  <ComputerResults>
    <ExtensionData>
      <Name>Security</Name>
      <Extension>
        <UserRightsAssignment>
          <Name>SeOtherRight</Name>
          <Member>S-1-5-20</Member>
        </UserRightsAssignment>
      </Extension>
    </ExtensionData>
  </ComputerResults>
</Rsop>
"@
        }

        Mock Remove-Item { }

        $result = Get-GDSUserRightPolicyState -UserRight 'SeServiceLogonRight'

        $result.UserRight | Should -Be 'SeServiceLogonRight'
        $result.IsManagedByGPO | Should -Be $false
      }

      It 'Correctly handles multiple User Rights' {
        Mock Start-Process { return [PSCustomObject]@{ ExitCode = 0 } }
        Mock Test-Path { return $true }

        Mock Get-Content {
          return @"
<Rsop>
  <ComputerResults>
    <ExtensionData>
      <Name>Security</Name>
      <Extension>
        <UserRightsAssignment>
          <Name>SeServiceLogonRight</Name>
          <Member>S-1-5-20</Member>
        </UserRightsAssignment>
      </Extension>
    </ExtensionData>
  </ComputerResults>
</Rsop>
"@
        }
        Mock Remove-Item { }

        $results = Get-GDSUserRightPolicyState -UserRight 'SeServiceLogonRight', 'SeLockMemoryPrivilege'

        $results.Count | Should -Be 2

        $results[0].UserRight | Should -Be 'SeServiceLogonRight'
        $results[0].IsManagedByGPO | Should -Be $true

        $results[1].UserRight | Should -Be 'SeLockMemoryPrivilege'
        $results[1].IsManagedByGPO | Should -Be $false
      }
    }

    Context 'Failure Scenarios' {

      It 'Throws error when gpresult returns non-zero exit code' {
        Mock Start-Process {
          return [PSCustomObject]@{ ExitCode = 1 }
        }

        Mock Test-Path { return $false }

        { Get-GDSUserRightPolicyState -UserRight 'SeServiceLogonRight' -ErrorAction Stop } | Should -Throw -ExpectedMessage '*Error retrieving GPO policy state: gpresult failed with exit code 1*'
      }

      It 'Throws error when report file is missing after execution' {
        Mock Start-Process {
          return [PSCustomObject]@{ ExitCode = 0 }
        }

        # Simulate file check failure
        Mock Test-Path { return $false }

        { Get-GDSUserRightPolicyState -UserRight 'SeServiceLogonRight' -ErrorAction Stop } | Should -Throw -ExpectedMessage '*Error retrieving GPO policy state: gpresult failed to generate the report file*'
      }

      It 'Handles missing Security extension gracefully' {
        Mock Start-Process { return [PSCustomObject]@{ ExitCode = 0 } }
        Mock Test-Path { return $true }
        Mock Remove-Item { }

        # XML without Security extension
        Mock Get-Content {
          return @"
<Rsop>
  <ComputerResults>
    <ExtensionData>
      <Name>OtherExtension</Name>
    </ExtensionData>
  </ComputerResults>
</Rsop>
"@
        }

        # Should verify Write-Warning was called? Pester 5 doesn't easily assert Warnings without -WarningAction Stop
        # We assume it returns false for the right.

        $result = Get-GDSUserRightPolicyState -UserRight 'SeServiceLogonRight'
        $result.IsManagedByGPO | Should -Be $false
      }
    }
  }
}
