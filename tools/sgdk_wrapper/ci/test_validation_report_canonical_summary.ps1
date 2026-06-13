<#
.SYNOPSIS
    Verifies canonical summary publication inside validation_report.json.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$projectRoot = Join-Path $workspaceRoot 'SGDK_projects\BENCHMARK_VISUAL_LAB_V2'
$validateScript = Join-Path $wrapperRoot 'validate_resources.ps1'
$reportPath = Join-Path $projectRoot 'out\logs\validation_report.json'

$passed = 0
$failed = 0
$total = 0

function Assert-True {
    param([string]$Name, [bool]$Condition, [string]$Detail = '')
    $script:total++
    if ($Condition) {
        $script:passed++
        Write-Host "  [PASS] $Name"
    } else {
        $script:failed++
        $msg = "  [FAIL] $Name"
        if ($Detail) { $msg += " -- $Detail" }
        Write-Host $msg
    }
}

Write-Host ''
Write-Host '=== Validation Report Canonical Summary Test ==='
Write-Host ''

if (-not (Test-Path -LiteralPath $projectRoot -PathType Container)) {
    Write-Host "  [SKIP] Fixture ausente: $projectRoot"
    exit 0
}

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $validateScript -WorkDir $projectRoot | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "validate_resources.ps1 failed with exit code $LASTEXITCODE"
}

$report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
$summary = $report.canonical_summary

Assert-True 'canonical_summary exists' ($null -ne $summary)
Assert-True 'canonical_summary schema version is 1.0.0' ($summary.schema_version -eq '1.0.0')
Assert-True 'build qa axis is mirrored' ($summary.build.qa_axis -eq $report.qa_axes.build)
Assert-True 'runtime capture samples are mirrored' ([int]$summary.runtime_capture.samples_recorded -eq [int]$report.evidence.runtime_samples_recorded)
Assert-True 'scene regression ready is mirrored' ([bool]$summary.scene_regression.ready -eq [bool]$report.status_panel.scene_regression_ready)
Assert-True 'validado_budget gate is mirrored' ([bool]$summary.gates.validado_budget -eq [bool]$report.status_panel.validado_budget)
Assert-True 'ready_for_aaa gate is mirrored' ([bool]$summary.gates.ready_for_aaa -eq [bool]$report.status_panel.ready_for_aaa)
Assert-True 'source artifacts are published' (@($summary.source_artifacts).Count -gt 0)

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
