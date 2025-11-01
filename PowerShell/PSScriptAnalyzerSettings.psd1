# PSScriptAnalyzer Settings

@{
    IncludeRules = @(
        'PSAvoidUsingCmdletAliases',
        'PSAvoidUsingWMICmdlet',
        'PSAvoidUsingPositionalParameters',
        'PSAvoidUsingInvokeExpression',
        'PSAvoidUsingPlainTextForPassword',
        'PSAvoidUsingComputerNameHardcoded',
        'PSAvoidUsingConvertToSecureStringWithPlainText',
        'PSAvoidUsingUserNameAndPasswordParams',
        'PSAvoidUsingPlainTextForPassword',
        'PSUseApprovedVerbs',
        'PSUseCmdletCorrectly',
        'PSUsePSCredentialType',
        'PSUseShouldProcessForStateChangingFunctions'
    )
    ExcludeRules = @()
    Severity = @('Error', 'Warning')
}
