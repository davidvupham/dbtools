#!/usr/bin/env pwsh
# Analyze-Logs.ps1 - Simple log analysis tool

param(
    [string]$LogPath = (Join-Path $PSScriptRoot "logs/app.json")
)

if (-not (Test-Path $LogPath)) {
    Write-Error "Log file not found: $LogPath"
    exit 1
}

$logs = Get-Content $LogPath | ForEach-Object { $_ | ConvertFrom-Json }

Write-Host "=== Log Analysis Report ===" -ForegroundColor Cyan
Write-Host "File: $LogPath"
Write-Host "Total Entries: $($logs.Count)"
Write-Host ""

# Count by Level
Write-Host "Entries by Level:" -ForegroundColor Yellow
$logs | Group-Object level | Sort-Object Count -Descending | Format-Table Count, Name -AutoSize

# Errors
$errors = $logs | Where-Object { $_.level -eq 'Error' -or $_.level -eq 'Critical' }
if ($errors) {
    Write-Host "Recent Errors:" -ForegroundColor Red
    $errors | Select-Object -Last 5 | ForEach-Object {
        Write-Host "[$($_.timestamp)] $($_.message)"
        if ($_.context.Error) {
            Write-Host "  Details: $($_.context.Error)" -ForegroundColor DarkGray
        }
    }
} else {
    Write-Host "No errors found." -ForegroundColor Green
}

Write-Host ""
Write-Host "Log analysis complete."
