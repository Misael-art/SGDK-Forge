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
Write-Host '=== Validation Report Blocking Status Codes Test ==='
Write-Host ''

if (-not (Test-Path -LiteralPath $projectRoot -PathType Container)) {
    Write-Host "  [SKIP] Fixture ausente: $projectRoot"
    exit 0
}

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $validateScript -WorkDir $projectRoot | Out-Null
$exitCode = $LASTEXITCODE
$report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
$summary = $report.canonical_summary

Assert-True 'validate_resources exits cleanly on benchmark' ($exitCode -eq 0) "exit=$exitCode"
Assert-True 'blocking_statuses still contain visual_gate_blocked' (@($report.blocking_statuses) -contains 'visual_gate_blocked')
Assert-True 'canonical_summary mirrors visual_gate_blocked' (@($summary.blocking_status_codes) -contains 'visual_gate_blocked')
Assert-True 'wrapper_reports are published in canonical summary' ($null -ne $summary.wrapper_reports)

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
