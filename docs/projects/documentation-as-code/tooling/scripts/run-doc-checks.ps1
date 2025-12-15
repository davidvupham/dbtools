<#
.SYNOPSIS
  Simple docs-as-code runner (Windows PowerShell).

.EXAMPLE
  pwsh -File tooling/scripts/run-doc-checks.ps1

.EXAMPLE
  pwsh -File tooling/scripts/run-doc-checks.ps1 -CSpell
#>

[CmdletBinding()]
param(
  [switch]$MarkdownLint,
  [switch]$CSpell,
  [switch]$Vale,
  [switch]$Lychee
)

$ErrorActionPreference = 'Stop'

$runAll = -not ($MarkdownLint -or $CSpell -or $Vale -or $Lychee)
if ($runAll) {
  $MarkdownLint = $true
  $CSpell = $true
  $Vale = $true
  $Lychee = $true
}

function Assert-Command {
  param(
    [Parameter(Mandatory)] [string]$Name,
    [Parameter(Mandatory)] [string]$Hint
  )
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "Missing required tool: $Name. $Hint"
  }
}

$docsGlob = 'docs/**/*.md'

if ($MarkdownLint) {
  Assert-Command -Name 'npx' -Hint 'Install Node.js and ensure npm/npx are on PATH.'
  Write-Host '== markdownlint ==' -ForegroundColor Cyan
  & npx markdownlint-cli2 $docsGlob
}

if ($CSpell) {
  Assert-Command -Name 'npx' -Hint 'Install Node.js and ensure npm/npx are on PATH.'
  Write-Host '== cspell ==' -ForegroundColor Cyan
  & npx cspell --config cspell.json $docsGlob
}

if ($Vale) {
  Assert-Command -Name 'vale' -Hint 'Install Vale and ensure vale.exe is on PATH.'
  Write-Host '== vale ==' -ForegroundColor Cyan
  & vale --config .vale.ini docs
}

if ($Lychee) {
  Assert-Command -Name 'lychee' -Hint 'Install Lychee and ensure lychee is on PATH.'
  Write-Host '== lychee ==' -ForegroundColor Cyan
  & lychee --config lychee.toml $docsGlob
}

Write-Host 'OK: docs checks passed' -ForegroundColor Green
