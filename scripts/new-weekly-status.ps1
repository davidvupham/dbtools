param(
    [Parameter(Mandatory=$false)][string]$ProjectPath = "docs/projects/sample-project",
    [Parameter(Mandatory=$false)][string]$TemplatePath = "docs/templates/status-report-weekly.md",
    [Parameter(Mandatory=$false)][string]$ReportDate = (Get-Date -Format 'yyyy-MM-dd')
)

$ErrorActionPreference = 'Stop'

# Compute period: previous Friday to this Thursday by default
$today = Get-Date
$start = ($today.AddDays(-($today.DayOfWeek.value__ + 2))).Date # approx previous Friday
$end = $today.Date

$destDir = Join-Path $ProjectPath "management"
if (!(Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir | Out-Null }

$destFile = Join-Path $destDir ("status-" + $ReportDate + ".md")

if (!(Test-Path $TemplatePath)) {
    Write-Error "Template not found: $TemplatePath"
}

$template = Get-Content -Raw -Path $TemplatePath

# Replace placeholders
$periodLine = "- **Period:** {0} to {1}" -f $start.ToString('yyyy-MM-dd'), $end.ToString('yyyy-MM-dd')
$content = $template -replace '(?m)^- \*\*Period:\*\* .*$', $periodLine

# Write file
Set-Content -Path $destFile -Value $content -Encoding UTF8

Write-Host "Created weekly status report: $destFile"