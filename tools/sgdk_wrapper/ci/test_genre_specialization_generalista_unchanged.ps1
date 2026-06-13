<#
.SYNOPSIS
    Generalista regression-guard: a project WITHOUT a
    doc/genre_specialization_manifest.json must still pass
    validate_fighting_specialization.ps1 with status=ok and
    manifest_status=absent. Proves the new specialization tooling does
    not break general projects.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = $null
if ($args.Count -gt 0 -and $args[0]) {
    $wrapperRoot = $args[0]
}
if (-not $wrapperRoot) {
    $wrapperRoot = Split-Path $PSScriptRoot -Parent
}
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$validator = Join-Path $wrapperRoot 'validate_fighting_specialization.ps1'
$fixtureRoot = Join-Path $workspaceRoot 'out\ci\fighting_specialization_generalista_fixture'
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
Write-Host '=== Genre Specialization Generalista (Unchanged) Test ==='
Write-Host ''

Assert-True 'validator exists' (Test-Path -LiteralPath $validator) $validator

if (Test-Path -LiteralPath $fixtureRoot) {
    Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'out\logs') | Out-Null

# No doc/genre_specialization_manifest.json => generalista path.
# No doc/project_methodology_manifest.json => validator must default to safe ceiling.
& powershell -NoProfile -ExecutionPolicy Bypass -File $validator -ProjectRoot $fixtureRoot | Out-Null
$validatorExit = $LASTEXITCODE
Assert-True 'validator exits 0 on generalista (no manifest) project' ($validatorExit -eq 0) ("exit=$validatorExit")
Assert-True 'report file emitted' (Test-Path -LiteralPath $reportPath) $reportPath
if (Test-Path -LiteralPath $reportPath) {
    $report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-True 'report.status is ok' ([string]$report.status -eq 'ok') ([string]$report.status)
    Assert-True 'report.manifest_status is absent' ([string]$report.manifest_status -eq 'absent') ([string]$report.manifest_status)
    Assert-True 'report.design_contract_status is absent' ([string]$report.design_contract_status -eq 'absent') ([string]$report.design_contract_status)
    Assert-True 'report.moveset_audits is empty' ($report.moveset_audits.Count -eq 0) ("$($report.moveset_audits.Count) audits")
    $firedBlockers = @($report.blockers | Where-Object { $_.fired -eq $true })
    Assert-True 'no blockers fire in generalista path' ($firedBlockers.Count -eq 0) ("$($firedBlockers.Count) fired")
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
