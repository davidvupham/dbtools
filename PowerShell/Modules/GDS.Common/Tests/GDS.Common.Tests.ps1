$moduleRoot = Split-Path -Parent $PSScriptRoot
$modulesRoot = Split-Path -Parent $moduleRoot

if ($modulesRoot) {
    $pathSeparator = [System.IO.Path]::PathSeparator
    $currentPaths = if ($env:PSModulePath) { $env:PSModulePath -split [System.Text.RegularExpressions.Regex]::Escape($pathSeparator) } else { @() }

    if ($currentPaths -notcontains $modulesRoot) {
        if ([string]::IsNullOrWhiteSpace($env:PSModulePath)) {
            $env:PSModulePath = $modulesRoot
        }
        else {
            $env:PSModulePath = "$modulesRoot$pathSeparator$($env:PSModulePath)"
        }
    }
}

$manifestPath = Join-Path $moduleRoot 'GDS.Common.psd1'
Import-Module $manifestPath -Force

InModuleScope 'GDS.Common' {

    Describe 'Initialize-Logging' {
        BeforeEach {
            Push-Location $TestDrive

            $script:configStore = @{}
            $script:loggedMessages = @()
            $script:logProviders = @()

            $env:GDS_LOG_DIR = Join-Path $TestDrive 'logs'

            Mock -CommandName Get-Module -MockWith { [pscustomobject]@{ Name = 'PSFramework' } }

            Mock -CommandName Set-PSFConfig -MockWith {
                param(
                    [string]$FullName,
                    $Value,
                    $Initialize,
                    $Validation,
                    $Description
                )
                $script:configStore[$FullName] = $Value
            }

            Mock -CommandName Get-PSFConfigValue -MockWith {
                param(
                    [string]$FullName,
                    $Fallback
                )
                if ($script:configStore.ContainsKey($FullName)) {
                    return $script:configStore[$FullName]
                }
                return $Fallback
            }

            Mock -CommandName Set-PSFLoggingProvider -MockWith {
                param(
                    [string]$Name,
                    [string]$InstanceName,
                    [string]$FilePath,
                    [bool]$Enabled,
                    [int]$MinLevel,
                    [int]$MaxLevel
                )

                $script:logProviders += [pscustomobject]@{
                    Name         = $Name
                    InstanceName = $InstanceName
                    FilePath     = $FilePath
                    Enabled      = $Enabled
                }
            }

            Mock -CommandName Write-PSFMessage -MockWith {
                param(
                    [string]$Level,
                    [string]$Message,
                    [string[]]$Tag,
                    [string]$FunctionName,
                    [hashtable]$Target
                )

                if ($Message -like '*PSFramework logging initialized*') {
                    return
                }

                $script:loggedMessages += [pscustomobject]@{
                    Level        = $Level
                    Message      = $Message
                    Tag          = $Tag
                    FunctionName = $FunctionName
                    Target       = $Target
                }
            }

            Mock -CommandName Get-PSCallStack -MockWith {
                @(
                    [pscustomobject]@{ ScriptName = 'C:\Modules\GDS.TestModule\Public\Invoke-Test.ps1'; FunctionName = 'Invoke-Test' },
                    [pscustomobject]@{ ScriptName = 'TestHarness.ps1'; FunctionName = 'Invoke-Harness' }
                )
            }
        }

        AfterEach {
            Pop-Location

            if (-not [string]::IsNullOrWhiteSpace($env:GDS_LOG_DIR)) {
                Remove-Item -Path $env:GDS_LOG_DIR -Recurse -Force -ErrorAction SilentlyContinue
            }
            Remove-Variable -Name configStore -Scope Script -ErrorAction SilentlyContinue
            Remove-Variable -Name loggedMessages -Scope Script -ErrorAction SilentlyContinue
            Remove-Variable -Name logProviders -Scope Script -ErrorAction SilentlyContinue
            Remove-Item Env:GDS_LOG_DIR -ErrorAction SilentlyContinue
        }

        It 'uses the GDS_LOG_DIR environment variable when no custom path is provided' {
            $env:GDS_LOG_DIR | Should -Not -BeNullOrEmpty
            Initialize-Logging -ModuleName 'TestModule'

            $logProvider = $script:logProviders | Where-Object { $_.Name -eq 'logfile' -and $_.InstanceName -eq 'TestModule' }

            $logProvider | Should -Not -BeNullOrEmpty
            $expectedDirectory = [System.IO.Path]::GetFullPath($env:GDS_LOG_DIR)
            (Split-Path -Parent $logProvider.FilePath) | Should -Be $expectedDirectory
            Test-Path $env:GDS_LOG_DIR | Should -BeTrue
        }

        It 'throws when GDS_LOG_DIR is not set' {
            Remove-Item Env:GDS_LOG_DIR

            { Initialize-Logging -ModuleName 'TestModule' } | Should -Throw -ErrorId *
        }

        It 'honors a custom log path when provided' {
            $customPath = Join-Path $env:GDS_LOG_DIR 'custom.log'
            Initialize-Logging -ModuleName 'TestModule' -LogPath $customPath

            $logProvider = $script:logProviders | Where-Object { $_.Name -eq 'logfile' -and $_.InstanceName -eq 'TestModule' }
            $logProvider.FilePath | Should -Be ([System.IO.Path]::GetFullPath($customPath))
        }

        It 'resolves module name from the call stack when not provided' {
            Mock -CommandName Get-PSCallStack -MockWith {
                @(
                    [pscustomobject]@{ ScriptName = 'C:\Modules\GDS.My-Module\Public\Start-Workflow.ps1'; FunctionName = 'Start-Workflow' },
                    [pscustomobject]@{ ScriptName = 'TestHarness.ps1'; FunctionName = 'Invoke-Harness' }
                )
            }

            Initialize-Logging

            $logProvider = $script:logProviders | Where-Object { $_.Name -eq 'logfile' }
            $logProvider.InstanceName | Should -Be 'My-Module'

            $configName = 'GDS.Common.Logging.My-Module.MinimumLevel'
            $script:configStore.ContainsKey($configName) | Should -BeTrue
        }

        It 'expands relative log paths to absolute paths' {
            $relativePath = Join-Path 'relative' 'custom.log'
            Initialize-Logging -ModuleName 'RelativeModule' -LogPath $relativePath

            $logProvider = $script:logProviders | Where-Object { $_.Name -eq 'logfile' -and $_.InstanceName -eq 'RelativeModule' }

            $expectedPath = [System.IO.Path]::GetFullPath((Join-Path -Path (Get-Location).ProviderPath -ChildPath $relativePath))
            $logProvider.FilePath | Should -Be $expectedPath
            Test-Path (Split-Path -Path $expectedPath -Parent) | Should -BeTrue
        }
    }

    Describe 'Set-GDSLogging' {
        BeforeEach {
            Push-Location $TestDrive

            $script:configStore = @{}
            $script:logProviders = @()
            $script:messages = @()

            $env:GDS_LOG_DIR = Join-Path $TestDrive 'logs'

            Mock -CommandName Get-Module -MockWith { [pscustomobject]@{ Name = 'PSFramework' } }

            Mock -CommandName Set-PSFConfig -MockWith {
                param(
                    [string]$FullName,
                    $Value,
                    $Initialize,
                    $Validation,
                    $Description
                )
                $script:configStore[$FullName] = $Value
            }

            Mock -CommandName Get-PSFConfigValue -MockWith {
                param(
                    [string]$FullName,
                    $Fallback
                )
                if ($script:configStore.ContainsKey($FullName)) {
                    return $script:configStore[$FullName]
                }
                return $Fallback
            }

            Mock -CommandName Set-PSFLoggingProvider -MockWith {
                param(
                    [string]$Name,
                    [string]$InstanceName,
                    [string]$FilePath,
                    [bool]$Enabled,
                    [Parameter(ValueFromRemainingArguments = $true)]
                    [object[]]$RemainingArguments
                )

                $script:logProviders += [pscustomobject]@{
                    Name         = $Name
                    InstanceName = $InstanceName
                    FilePath     = $FilePath
                    Enabled      = $Enabled
                }
            }

            Mock -CommandName Write-PSFMessage -MockWith {
                param(
                    [string]$Level,
                    [string]$Message,
                    [string[]]$Tag
                )

                $script:messages += [pscustomobject]@{
                    Level   = $Level
                    Message = $Message
                    Tag     = $Tag
                }
            }
            Mock -CommandName Get-PSCallStack -MockWith { @() }
        }

        AfterEach {
            Pop-Location

            if (-not [string]::IsNullOrWhiteSpace($env:GDS_LOG_DIR)) {
                Remove-Item -Path $env:GDS_LOG_DIR -Recurse -Force -ErrorAction SilentlyContinue
            }
            Remove-Variable -Name configStore -Scope Script -ErrorAction SilentlyContinue
            Remove-Variable -Name logProviders -Scope Script -ErrorAction SilentlyContinue
            Remove-Variable -Name messages -Scope Script -ErrorAction SilentlyContinue
            Remove-Item Env:GDS_LOG_DIR -ErrorAction SilentlyContinue
        }

        It 'stores the minimum level configuration scoped to the module' {
            Set-GDSLogging -ModuleName 'TestModule' -MinimumLevel 'Warning' -EnableConsoleLog:$false -EnableFileLog:$false

            $configName = 'GDS.Common.Logging.TestModule.MinimumLevel'
            $script:configStore[$configName] | Should -Be 'Warning'
        }

        It 'uses GDS_LOG_DIR when file logging is enabled without a custom log path' {
            $env:GDS_LOG_DIR | Should -Not -BeNullOrEmpty
            Set-GDSLogging -ModuleName 'TestModule' -MinimumLevel 'Info'

            $logProvider = $script:logProviders | Where-Object { $_.Name -eq 'logfile' -and $_.InstanceName -eq 'TestModule' }

            $logProvider | Should -Not -BeNullOrEmpty
            $expectedDirectory = [System.IO.Path]::GetFullPath($env:GDS_LOG_DIR)
            (Split-Path -Parent $logProvider.FilePath) | Should -Be $expectedDirectory
        }

        It 'disables file logging when requested' {
            Set-GDSLogging -ModuleName 'TestModule' -EnableFileLog:$false

            $logProvider = $script:logProviders | Where-Object { $_.Name -eq 'logfile' -and $_.InstanceName -eq 'TestModule' }
            $logProvider.Enabled | Should -BeFalse
        }

        It 'honors console logging toggle' {
            Set-GDSLogging -ModuleName 'TestModule' -EnableConsoleLog:$false

            $consoleProvider = $script:logProviders | Where-Object { $_.Name -eq 'console' }
            $consoleProvider | Should -Not -BeNullOrEmpty
            $consoleProvider.Enabled | Should -BeFalse
        }

        It 'expands relative paths when configuring file logging' {
            $relativePath = Join-Path 'logs' 'module.log'
            Set-GDSLogging -ModuleName 'TestModule' -LogPath $relativePath

            $logProvider = $script:logProviders | Where-Object { $_.Name -eq 'logfile' -and $_.InstanceName -eq 'TestModule' }

            $expectedPath = [System.IO.Path]::GetFullPath((Join-Path -Path (Get-Location).ProviderPath -ChildPath $relativePath))
            $logProvider.FilePath | Should -Be $expectedPath
        }

        It 'allows disabling file logging without requiring GDS_LOG_DIR' {
            Remove-Item Env:GDS_LOG_DIR -ErrorAction SilentlyContinue

            { Set-GDSLogging -ModuleName 'TestModule' -EnableFileLog:$false } | Should -Not -Throw
        }
    }

    Describe 'Write-Log' {
        BeforeEach {
            $script:configStore = @{}
            $script:messages = @()

            $env:GDS_LOG_DIR = Join-Path $TestDrive 'logs'

            Mock -CommandName Get-Module -MockWith { [pscustomobject]@{ Name = 'PSFramework' } }

            Mock -CommandName Set-PSFConfig -MockWith {
                param(
                    [string]$FullName,
                    $Value,
                    $Initialize,
                    $Validation,
                    $Description
                )
                $script:configStore[$FullName] = $Value
            }

            Mock -CommandName Get-PSFConfigValue -MockWith {
                param(
                    [string]$FullName,
                    $Fallback
                )
                if ($script:configStore.ContainsKey($FullName)) {
                    return $script:configStore[$FullName]
                }
                return $Fallback
            }

            Mock -CommandName Set-PSFLoggingProvider -MockWith { }

            Mock -CommandName Write-PSFMessage -MockWith {
                param(
                    [string]$Level,
                    [string]$Message,
                    [string[]]$Tag,
                    [string]$FunctionName,
                    [hashtable]$Target
                )

                if ($Message -like '*PSFramework logging configured*') {
                    return
                }

                $script:messages += [pscustomobject]@{
                    Level        = $Level
                    Message      = $Message
                    Tag          = $Tag
                    FunctionName = $FunctionName
                    Target       = $Target
                }
            }

            Mock -CommandName Get-PSCallStack -MockWith {
                @(
                    [pscustomobject]@{ ScriptName = 'C:\Modules\GDS.TestModule\Public\Invoke-Test.ps1'; FunctionName = 'Invoke-Test' },
                    [pscustomobject]@{ ScriptName = 'TestHarness.ps1'; FunctionName = 'Invoke-Harness' }
                )
            }

            # Configure module logging threshold
            Set-GDSLogging -ModuleName 'TestModule' -MinimumLevel 'Warning' -EnableConsoleLog:$false -EnableFileLog:$false
        }

        AfterEach {
            Remove-Variable -Name configStore -Scope Script -ErrorAction SilentlyContinue
            Remove-Variable -Name messages -Scope Script -ErrorAction SilentlyContinue
            Remove-Item Env:GDS_LOG_DIR -ErrorAction SilentlyContinue
        }

        It 'skips messages below the configured minimum level' {
            Write-Log -ModuleName 'TestModule' -Message 'verbose message' -Level Verbose

            $script:messages | Should -BeNullOrEmpty
        }

        It 'emits messages at or above the configured minimum level' {
            Write-Log -ModuleName 'TestModule' -Message 'warning message' -Level Warning

            $script:messages.Count | Should -Be 1
            $script:messages[0].Level | Should -Be 'Warning'
        }

        It 'includes inferred module name in tags when not specified' {
            Mock -CommandName Get-PSCallStack -MockWith {
                @(
                    [pscustomobject]@{ ScriptName = 'C:\Modules\GDS.My-Module\Public\Invoke-Test.ps1'; FunctionName = 'Invoke-Test' },
                    [pscustomobject]@{ ScriptName = 'TestHarness.ps1'; FunctionName = 'Invoke-Harness' }
                )
            }

            Write-Log -Message 'warning message' -Level Warning

            $script:messages.Count | Should -Be 1
            $script:messages[0].Tag | Should -Contain 'My-Module'
        }
    }

}
