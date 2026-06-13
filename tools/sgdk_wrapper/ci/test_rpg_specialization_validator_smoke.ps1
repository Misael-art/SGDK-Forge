<#
.SYNOPSIS
    Smoke test for validate_rpg_turn_based_jrpg_specialization.ps1 in
    generalista path (no manifest at the project root). Validator must
    exit 0, emit a report, and have manifest_status=absent, no blockers.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$validator = Join-Path $wrapperRoot 'validate_rpg_turn_based_jrpg_specialization.ps1'
$rogueRoot = Join-Path $workspaceRoot 'out\ci\rpg_validator_smoke_fixture'
$reportPath = Join-Path $rogueRoot 'out\logs\rpg_specialization_report.json'

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
Write-Host '=== RPG Specialization Validator Smoke Test ==='
Write-Host ''

Assert-True 'validator exists' (Test-Path -LiteralPath $validator) $validator

# Build empty project
if (Test-Path -LiteralPath $rogueRoot) { Remove-Item -LiteralPath $rogueRoot -Recurse -Force }
New-Item -ItemType Directory -Force -Path (Join-Path $rogueRoot 'out\logs') | Out-Null

# Run validator
& powershell -NoProfile -ExecutionPolicy Bypass -File $validator -ProjectRoot $rogueRoot | Out-Null
$exitCode = $LASTEXITCODE
Assert-True 'validator exits 0 on no-manifest project' ($exitCode -eq 0) ("exit=$exitCode")

Assert-True 'report file emitted' (Test-Path -LiteralPath $reportPath) $reportPath
if (Test-Path -LiteralPath $reportPath) {
    $report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-True 'report.status is ok' ([string]$report.status -eq 'ok') ([string]$report.status)
    Assert-True 'report.manifest_status is absent' ([string]$report.manifest_status -eq 'absent') ([string]$report.manifest_status)
    Assert-True 'report.design_contract_status is absent' ([string]$report.design_contract_status -eq 'absent') ([string]$report.design_contract_status)
    Assert-True 'report has 0 party_audits' ($report.party_audits.Count -eq 0) ("$($report.party_audits.Count) audits")
    Assert-True 'report has 0 blockers' ($report.blockers.Count -eq 0) ("$($report.blockers.Count) blockers")
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
