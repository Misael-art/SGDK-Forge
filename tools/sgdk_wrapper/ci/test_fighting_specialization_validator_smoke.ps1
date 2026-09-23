<#
.SYNOPSIS
    Smoke call to validate_fighting_specialization.ps1 against a no-manifest
    fixture. Proves the validator's generalista path is intact at CI time.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ciDir = $PSScriptRoot
$wrapperRoot = Split-Path $ciDir -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$validator = Join-Path $wrapperRoot 'validate_fighting_specialization.ps1'
$fixtureRoot = Join-Path $workspaceRoot 'out\ci\fighting_specialization_validator_smoke'
$reportPath = Join-Path $fixtureRoot 'out\logs\fighting_specialization_report.json'

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
Write-Host '=== Genre Specialization Validator Smoke ==='
Write-Host ''

Assert-True 'validator exists' (Test-Path -LiteralPath $validator) $validator
if (Test-Path -LiteralPath $fixtureRoot) {
    Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'out\logs') | Out-Null

& powershell -NoProfile -ExecutionPolicy Bypass -File $validator -ProjectRoot $fixtureRoot | Out-Null
$validatorExit = $LASTEXITCODE
Assert-True 'validator exits 0 on no-manifest project' ($validatorExit -eq 0) ("exit=$validatorExit")
Assert-True 'report file emitted' (Test-Path -LiteralPath $reportPath) $reportPath
if (Test-Path -LiteralPath $reportPath) {
    $report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-True 'report.status is ok' ([string]$report.status -eq 'ok') ([string]$report.status)
    Assert-True 'report.manifest_status is absent' ([string]$report.manifest_status -eq 'absent') ([string]$report.manifest_status)
    $firedBlockers = @($report.blockers | Where-Object { $_.fired -eq $true })
    Assert-True 'no blockers fire' ($firedBlockers.Count -eq 0) ("$($firedBlockers.Count) fired")
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
