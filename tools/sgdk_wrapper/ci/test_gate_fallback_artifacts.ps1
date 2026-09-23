<#
.SYNOPSIS
    Tests that gate scripts produce a fallback failure artifact when they crash.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$WrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))

$script:passed = 0
$script:failed = 0

function Assert-True {
    param([string]$Name, [bool]$Condition, [string]$Detail = '')
    if ($Condition) { $script:passed++; Write-Host "  [PASS] $Name" }
    else { $script:failed++; Write-Host "  [FAIL] $Name -- $Detail" }
}

function New-FallbackTestProject {
    param([string]$Label)
    $root = Join-Path ([System.IO.Path]::GetTempPath()) ('sgdk_fallback_test_{0}_{1}' -f $Label, ([guid]::NewGuid().ToString('N').Substring(0, 8)))
    New-Item -ItemType Directory -Force -Path (Join-Path $root 'doc'), (Join-Path $root 'out\logs') | Out-Null
    return $root
}

# Test 1: scene_closeout_gate with invalid ProjectRoot
Write-Host '--- scene_closeout_gate with bad ProjectRoot ---'
$badRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('sgdk_fallback_nonexistent_{0}' -f ([guid]::NewGuid().ToString('N')))
$reportPath = Join-Path $badRoot 'out\logs\scene_closeout_gate_report.json'
try {
    & (Join-Path $WrapperRoot 'scene_closeout_gate.ps1') -ProjectRoot $badRoot 2>&1 | Out-Null
} catch { }
$sceneBadExit = $LASTEXITCODE
Assert-True 'scene_closeout bad ProjectRoot exits 1' ($sceneBadExit -ne 0) "exit=$sceneBadExit"
if (Test-Path -LiteralPath $reportPath -PathType Leaf) {
    $report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-True 'scene_closeout fallback exists' ($null -ne $report)
    Assert-True 'scene_closeout fallback status=error' ($report.status -eq 'error') "got '$($report.status)'"
    Assert-True 'scene_closeout fallback has failure_reason' (-not [string]::IsNullOrWhiteSpace([string]$report.failure_reason))
    Assert-True 'scene_closeout fallback has closeout_status' ($report.closeout_status -eq 'error') "got '$($report.closeout_status)'"
} else {
    Assert-True 'scene_closeout fallback report file' $false "not found at $reportPath"
}

# Test 2: scene_closeout_gate with build.bat that crashes
Write-Host '--- scene_closeout_gate with crashing build ---'
$crashRoot = New-FallbackTestProject 'crash_build'
$crashReportPath = Join-Path $crashRoot 'out\logs\scene_closeout_gate_report.json'
[System.IO.File]::WriteAllText((Join-Path $crashRoot 'build.bat'), "@echo off`r`nexit /b 1`r`n", [System.Text.Encoding]::ASCII)
try {
    & (Join-Path $WrapperRoot 'scene_closeout_gate.ps1') -ProjectRoot $crashRoot -ErrorAction SilentlyContinue 2>&1 | Out-Null
} catch { }
if (Test-Path -LiteralPath $crashReportPath -PathType Leaf) {
    $report = Get-Content -LiteralPath $crashReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-True 'scene_closeout crash-build report exists' ($null -ne $report)
    Assert-True 'scene_closeout crash-build has closeout_status' (-not [string]::IsNullOrWhiteSpace([string]$report.closeout_status))
} else {
    Assert-True 'scene_closeout crash-build report file' $false "not found at $crashReportPath"
}
if (Test-Path -LiteralPath $crashRoot) { Remove-Item -LiteralPath $crashRoot -Recurse -Force }

# Test 3: validate_project_context with bad ProjectRoot
Write-Host '--- validate_project_context with bad ProjectRoot ---'
$badContextRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('sgdk_context_nonexistent_{0}' -f ([guid]::NewGuid().ToString('N')))
$ctxReportPath = Join-Path $badContextRoot 'out\logs\project_context_report.json'
try {
    & (Join-Path $WrapperRoot 'validate_project_context.ps1') -ProjectRoot $badContextRoot -Phase planning 2>&1 | Out-Null
} catch { }
$contextBadExit = $LASTEXITCODE
Assert-True 'context bad ProjectRoot exits 1' ($contextBadExit -ne 0) "exit=$contextBadExit"
if (Test-Path -LiteralPath $ctxReportPath -PathType Leaf) {
    $report = Get-Content -LiteralPath $ctxReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-True 'context fallback exists' ($null -ne $report)
    Assert-True 'context fallback status=error' ($report.status -eq 'error') "got '$($report.status)'"
    Assert-True 'context fallback has failure_reason' (-not [string]::IsNullOrWhiteSpace([string]$report.failure_reason))
    Assert-True 'context fallback has validation_status' ($report.validation_status -eq 'error') "got '$($report.validation_status)'"
} else {
    Assert-True 'context fallback report file' $false "not found at $ctxReportPath"
}

Write-Host ''
Write-Host "=== Results: $script:passed passed, $script:failed failed ==="
if ($script:failed -gt 0) { exit 1 }
exit 0
