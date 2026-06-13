<#
.SYNOPSIS
    Verifies lint enforcement for explicit comparison_artifacts on evidence bundles.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$lintScript = Join-Path $wrapperRoot 'lint_scene_contract.ps1'

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

function New-SyntheticProject {
    param(
        [Parameter(Mandatory)][string]$Root,
        [Parameter(Mandatory)][bool]$DeclareComparisonArtifacts
    )

    $docDir = Join-Path $Root 'doc'
    $outLogs = Join-Path $Root 'out\logs'
    New-Item -ItemType Directory -Force -Path $docDir | Out-Null
    New-Item -ItemType Directory -Force -Path $outLogs | Out-Null

    $scene = [ordered]@{
        scene_id            = 'scene_example'
        scene_role          = 'benchmark'
        boot_mode           = 'sram_bootstrap'
        capture_kind        = 'evidence_bundle'
        cleanup_required    = $true
        regression_required = $true
        capture_frame       = 120
        warmup_frames       = 60
    }

    if ($DeclareComparisonArtifacts) {
        $scene['comparison_artifacts'] = @('screenshot')
    }

    $contract = [ordered]@{
        schema_version  = '1.0.0'
        project_profile = 'lab'
        scenes          = @($scene)
    }

    $contract | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $docDir 'scene-contracts.json') -Encoding UTF8
}

function Invoke-LintReport {
    param([Parameter(Mandatory)][string]$ProjectRoot)

    & $lintScript -ProjectRoot $ProjectRoot -WarnOnly | Out-Null
    $reportPath = Join-Path $ProjectRoot 'out\logs\scene_contract_report.json'
    return (Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json)
}

$tmpMissing = Join-Path $env:TEMP "sgdk_lint_cmp_missing_$([guid]::NewGuid().ToString('N').Substring(0,8))"
$tmpPresent = Join-Path $env:TEMP "sgdk_lint_cmp_present_$([guid]::NewGuid().ToString('N').Substring(0,8))"

try {
    New-SyntheticProject -Root $tmpMissing -DeclareComparisonArtifacts:$false
    New-SyntheticProject -Root $tmpPresent -DeclareComparisonArtifacts:$true

    Write-Host ''
    Write-Host '=== Scene Contract Lint Comparison Artifacts Test ==='
    Write-Host ''

    $missingReport = Invoke-LintReport -ProjectRoot $tmpMissing
    $presentReport = Invoke-LintReport -ProjectRoot $tmpPresent

    $missingFindings = @($missingReport.findings)
    $presentFindings = @($presentReport.findings)

    $missingSC085 = @($missingFindings | Where-Object { $_.code -eq 'SC085' })
    $presentSC085 = @($presentFindings | Where-Object { $_.code -eq 'SC085' })

    Assert-True 'Missing comparison_artifacts emits SC085' ($missingSC085.Count -eq 1)
    Assert-True 'Missing comparison_artifacts yields warn status in lab mode' ($missingReport.status -eq 'warn') $missingReport.failure_reason
    Assert-True 'Declared comparison_artifacts emits no SC085' ($presentSC085.Count -eq 0)
    Assert-True 'Declared comparison_artifacts yields ok status' ($presentReport.status -eq 'ok') $presentReport.failure_reason
}
finally {
    Remove-Item -Recurse -Force $tmpMissing -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force $tmpPresent -ErrorAction SilentlyContinue
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
