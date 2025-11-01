# Run All Tests

# This script runs Pester tests for all modules

Import-Module Pester

$testResults = Invoke-Pester -Path ".\modules\*\tests" -PassThru -OutputFormat NUnitXml -OutputFile ".\test-results.xml"

if ($testResults.FailedCount -gt 0) {
    Write-Error "Tests failed: $($testResults.FailedCount) failed out of $($testResults.TotalCount)"
    exit 1
} else {
    Write-Host "All tests passed: $($testResults.PassedCount) passed"
}
