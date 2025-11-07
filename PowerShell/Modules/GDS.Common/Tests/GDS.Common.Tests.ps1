BeforeAll {
    $moduleRoot = Split-Path -Parent $PSScriptRoot
    $manifestPath = Join-Path $moduleRoot 'GDS.Common.psd1'
    Import-Module $manifestPath -Force
}

Describe 'Initialize-Logging' {
    BeforeEach {
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
                [int]$LogRotationMaxSizeMB,
                [int]$LogRetentionDays
            )

            $script:logProviders += [pscustomobject]@{
                Name = $Name
                InstanceName = $InstanceName
                FilePath = $FilePath
                Enabled = $Enabled
                LogRotationMaxSizeMB = $LogRotationMaxSizeMB
                LogRetentionDays = $LogRetentionDays
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

            $script:loggedMessages += [pscustomobject]@{
                Level = $Level
                Message = $Message
                Tag = $Tag
                FunctionName = $FunctionName
                Target = $Target
            }
        }

        Mock -CommandName Get-PSCallStack -MockWith {
            @(
                [pscustomobject]@{ ScriptName = 'GDS.Test\TestModule.ps1'; FunctionName = 'Invoke-Test' },
                [pscustomobject]@{ ScriptName = 'TestHarness.ps1'; FunctionName = 'Invoke-Harness' }
            )
        }
    }

    AfterEach {
        Remove-Item -Path $env:GDS_LOG_DIR -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Variable -Name configStore -Scope Script -ErrorAction SilentlyContinue
        Remove-Variable -Name loggedMessages -Scope Script -ErrorAction SilentlyContinue
        Remove-Variable -Name logProviders -Scope Script -ErrorAction SilentlyContinue
        Remove-Item Env:GDS_LOG_DIR -ErrorAction SilentlyContinue
    }

    It 'uses the GDS_LOG_DIR environment variable when no custom path is provided' {
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
}

Describe 'Set-GDSLogging' {
    BeforeEach {
        $script:configStore = @{}
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
                [int]$LogRotationMaxSizeMB,
                [int]$LogRetentionDays
            )

            $script:logProviders += [pscustomobject]@{
                Name = $Name
                InstanceName = $InstanceName
                FilePath = $FilePath
                Enabled = $Enabled
                LogRotationMaxSizeMB = $LogRotationMaxSizeMB
                LogRetentionDays = $LogRetentionDays
            }
        }

        Mock -CommandName Write-PSFMessage -MockWith { }
        Mock -CommandName Get-PSCallStack -MockWith { @() }
    }

    AfterEach {
        Remove-Item -Path $env:GDS_LOG_DIR -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Variable -Name configStore -Scope Script -ErrorAction SilentlyContinue
        Remove-Variable -Name logProviders -Scope Script -ErrorAction SilentlyContinue
        Remove-Item Env:GDS_LOG_DIR -ErrorAction SilentlyContinue
    }

    It 'stores the minimum level configuration scoped to the module' {
        Set-GDSLogging -ModuleName 'TestModule' -MinimumLevel 'Warning' -EnableConsoleLog:$false -EnableFileLog:$false

        $configName = 'GDS.Common.Logging.TestModule.MinimumLevel'
        $script:configStore[$configName] | Should -Be 'Warning'
    }

    It 'uses GDS_LOG_DIR when file logging is enabled without a custom log path' {
        Set-GDSLogging -ModuleName 'TestModule' -MinimumLevel 'Info'

        $logProvider = $script:logProviders | Where-Object { $_.Name -eq 'logfile' -and $_.InstanceName -eq 'TestModule' }

        $logProvider | Should -Not -BeNullOrEmpty
        $expectedDirectory = [System.IO.Path]::GetFullPath($env:GDS_LOG_DIR)
        (Split-Path -Parent $logProvider.FilePath) | Should -Be $expectedDirectory
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

            $script:messages += [pscustomobject]@{
                Level = $Level
                Message = $Message
                Tag = $Tag
                FunctionName = $FunctionName
                Target = $Target
            }
        }

        Mock -CommandName Get-PSCallStack -MockWith {
            @(
                [pscustomobject]@{ ScriptName = 'GDS.Test\TestModule.ps1'; FunctionName = 'Invoke-Test' },
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
}
