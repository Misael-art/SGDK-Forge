<#
.SYNOPSIS
    Verifies production/AAA lint enforcement for cutscene contracts.
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

function New-CutsceneProject {
    param(
        [Parameter(Mandatory)][string]$Root,
        [Parameter(Mandatory)][bool]$WithContract
    )

    $docDir = Join-Path $Root 'doc'
    $pipelineDir = Join-Path $docDir 'pipeline\cutscene'
    $outLogs = Join-Path $Root 'out\logs'
    New-Item -ItemType Directory -Force -Path $docDir | Out-Null
    New-Item -ItemType Directory -Force -Path $pipelineDir | Out-Null
    New-Item -ItemType Directory -Force -Path $outLogs | Out-Null

    if ($WithContract) {
        @(
            'intro_fsm.json',
            'intro_resource_plan.json',
            'intro_panel_layout.json',
            'intro_text_timing.json',
            'intro_palette_script.json',
            'intro_glyph_manifest.json',
            'intro_teardown_plan.json',
            'intro_evidence_plan.json'
        ) | ForEach-Object {
            '{}' | Set-Content -LiteralPath (Join-Path $pipelineDir $_) -Encoding UTF8
        }
    }

    $scene = [ordered]@{
        scene_id            = 'intro_cutscene'
        scene_role          = 'cutscene'
        boot_mode           = 'sram_bootstrap'
        capture_kind        = 'evidence_bundle'
        comparison_artifacts = @('screenshot')
        cleanup_required    = $true
        regression_required = $true
        capture_frame       = 180
        warmup_frames       = 30
    }

    if ($WithContract) {
        $scene['cutscene_contract'] = [ordered]@{
            cutscene_mode                  = 'panel_sequence'
            fsm_script                     = 'doc/pipeline/cutscene/intro_fsm.json'
            resource_plan                  = 'doc/pipeline/cutscene/intro_resource_plan.json'
            panel_layout                   = 'doc/pipeline/cutscene/intro_panel_layout.json'
            text_timing_map                = 'doc/pipeline/cutscene/intro_text_timing.json'
            palette_script                 = 'doc/pipeline/cutscene/intro_palette_script.json'
            glyph_manifest                 = 'doc/pipeline/cutscene/intro_glyph_manifest.json'
            advance_model                  = 'MIXED'
            teardown_plan                  = 'doc/pipeline/cutscene/intro_teardown_plan.json'
            evidence_plan                  = 'doc/pipeline/cutscene/intro_evidence_plan.json'
            uses_fullscreen_bitmap         = $false
            dynamic_fx                     = @('palette_cycling')
        }
    }

    $contract = [ordered]@{
        schema_version  = '1.0.0'
        project_profile = 'aaa_gate'
        scenes          = @($scene)
    }

    $contract | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $docDir 'scene-contracts.json') -Encoding UTF8
}

function Invoke-Lint {
    param(
        [Parameter(Mandatory)][string]$ProjectRoot,
        [Parameter(Mandatory)][bool]$ExpectSuccess
    )

    powershell -NoProfile -ExecutionPolicy Bypass -File $lintScript -ProjectRoot $ProjectRoot -Mode aaa_gate | Out-Null
    $exitCode = $LASTEXITCODE
    $reportPath = Join-Path $ProjectRoot 'out\logs\scene_contract_report.json'
    $report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json

    if ($ExpectSuccess) {
        Assert-True 'Cutscene contract passes aaa_gate lint' ($exitCode -eq 0 -and $report.status -eq 'ok') $report.failure_reason
    } else {
        Assert-True 'Missing cutscene_contract fails aaa_gate lint' ($exitCode -ne 0)
    }

    return $report
}

$tmpMissing = Join-Path $env:TEMP "sgdk_cutscene_missing_$([guid]::NewGuid().ToString('N').Substring(0,8))"
$tmpValid = Join-Path $env:TEMP "sgdk_cutscene_valid_$([guid]::NewGuid().ToString('N').Substring(0,8))"

try {
    New-CutsceneProject -Root $tmpMissing -WithContract:$false
    New-CutsceneProject -Root $tmpValid -WithContract:$true

    Write-Host ''
    Write-Host '=== Cutscene Contract Lint Test ==='
    Write-Host ''

    $missingReport = Invoke-Lint -ProjectRoot $tmpMissing -ExpectSuccess:$false
    $validReport = Invoke-Lint -ProjectRoot $tmpValid -ExpectSuccess:$true

    $missingSC100 = @($missingReport.findings | Where-Object { $_.code -eq 'SC100' })
    $validSC100 = @($validReport.findings | Where-Object { $_.code -eq 'SC100' })

    Assert-True 'Missing contract emits SC100' ($missingSC100.Count -eq 1)
    Assert-True 'Valid contract emits no SC100' ($validSC100.Count -eq 0)
}
finally {
    Remove-Item -Recurse -Force $tmpMissing -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force $tmpValid -ErrorAction SilentlyContinue
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
