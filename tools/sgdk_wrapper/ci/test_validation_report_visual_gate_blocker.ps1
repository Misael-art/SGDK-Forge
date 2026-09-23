<#
.SYNOPSIS
    Verifica que o validator publica blocker explicito quando o gate visual nao foi medido.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$projectRoot = Join-Path $workspaceRoot 'out\ci\visual_gate_no_analysis_fixture'
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
Write-Host '=== Validation Report Visual Gate Blocker Test ==='
Write-Host ''

if (Test-Path -LiteralPath $projectRoot) {
    Remove-Item -LiteralPath $projectRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'res') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'src') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'doc\changelog') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'out\logs') | Out-Null
Set-Content -LiteralPath (Join-Path $projectRoot 'doc\changelog\changelog.md') -Value '# CI fixture' -Encoding UTF8

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $validateScript -WorkDir $projectRoot | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "validate_resources.ps1 failed with exit code $LASTEXITCODE"
}

$report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
$visualBlockers = @($report.blocking_statuses | Where-Object { $_ -eq 'visual_gate_blocked' })
$noAnalysisDetails = @($report.details | Where-Object {
    $_.type -eq 'BLOCKING_STATUS' -and
    $_.blocking_status -eq 'visual_gate_blocked' -and
    $_.reason -eq 'no_visual_analysis'
})

Assert-True 'visual gate permanece fechado' (-not [bool]$report.status_panel.visual_gate_ready)
Assert-True 'visual_lab_aprovado permanece falso' (-not [bool]$report.status_panel.visual_lab_aprovado)
Assert-True 'blocking_statuses inclui visual_gate_blocked' ($visualBlockers.Count -gt 0)
Assert-True 'detail explicita ausencia de medicao visual' ($noAnalysisDetails.Count -gt 0)
Assert-True 'closing_blockers espelha visual_gate_blocked' (@($report.status_panel.closing_blockers | Where-Object { $_ -eq 'visual_gate_blocked' }).Count -gt 0)

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
