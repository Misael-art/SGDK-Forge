<#
.SYNOPSIS
    Validates that gate scripts produce reports conforming to common_artifact.schema.json.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$WrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$SchemaPath = Join-Path $WrapperRoot 'schemas\common_artifact.schema.json'
$SchemaJson = Get-Content -LiteralPath $SchemaPath -Raw -Encoding UTF8 | ConvertFrom-Json
$RequiredFields = @($SchemaJson.required)

$ScriptsUnderTest = @(
    @{ name = 'scene_closeout_gate.ps1';     script = Join-Path $WrapperRoot 'scene_closeout_gate.ps1' }
    @{ name = 'validate_project_context.ps1'; script = Join-Path $WrapperRoot 'validate_project_context.ps1' }
)

$script:passed = 0
$script:failed = 0

function Assert-True {
    param([string]$Name, [bool]$Condition, [string]$Detail = '')
    if ($Condition) { $script:passed++; Write-Host "  [PASS] $Name" }
    else { $script:failed++; Write-Host "  [FAIL] $Name -- $Detail" }
}

$ProjectRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('sgdk_schema_gate_test_{0}' -f ([guid]::NewGuid().ToString('N')))
$DocDir = Join-Path $ProjectRoot 'doc'
$LogDir = Join-Path $ProjectRoot 'out\logs'
New-Item -ItemType Directory -Force -Path $DocDir, $LogDir | Out-Null
[System.IO.File]::WriteAllText((Join-Path $DocDir '13-spec-cenas.md'), '# spec', [System.Text.Encoding]::UTF8)
[System.IO.File]::WriteAllText((Join-Path $ProjectRoot 'build.bat'), "@echo off`r`nexit /b 0`r`n", [System.Text.Encoding]::ASCII)

foreach ($entry in $ScriptsUnderTest) {
    Write-Host "--- Testing $($entry.name) ---"

    if (-not (Test-Path -LiteralPath $entry.script -PathType Leaf)) {
        Assert-True "Script exists: $($entry.name)" $false "not found"
        continue
    }

    $report = $null
    try {
        if ($entry.name -eq 'scene_closeout_gate.ps1') {
            & $entry.script -ProjectRoot $ProjectRoot -PlanOnly
            $reportPath = Join-Path $LogDir 'scene_closeout_gate_report.json'
        } else {
            & $entry.script -ProjectRoot $ProjectRoot -Phase planning
            $reportPath = Join-Path $LogDir 'project_context_report.json'
        }
        if (Test-Path -LiteralPath $reportPath -PathType Leaf) {
            $report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
        }
    } catch {
        Assert-True "Script runs: $($entry.name)" $false $_.Exception.Message
        continue
    }

    Assert-True "Script exited: $($entry.name)" ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq 1) "exit=$LASTEXITCODE"
    Assert-True "Report exists: $($entry.name)" ($null -ne $report) "path=$reportPath"

    if ($null -ne $report) {
        foreach ($field in $RequiredFields) {
            $hasField = $report.PSObject.Properties.Name -contains $field
            Assert-True "Required field '$field' in $($entry.name)" $hasField
        }
        $statusOk = [string]$report.status -in @('ok', 'warn', 'error')
        Assert-True "status is ok|warn|error in $($entry.name)" $statusOk "got '$($report.status)'"
        if ($report.status -ne 'ok') {
            $hasReason = (-not [string]::IsNullOrWhiteSpace([string]$report.failure_reason))
            Assert-True "failure_reason present for status=$($report.status) in $($entry.name)" $hasReason
        }
    }
}

if (Test-Path -LiteralPath $ProjectRoot) { Remove-Item -LiteralPath $ProjectRoot -Recurse -Force }

Write-Host ''
Write-Host "=== Results: $script:passed passed, $script:failed failed ==="
if ($script:failed -gt 0) { exit 1 }
exit 0
