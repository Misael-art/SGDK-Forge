<#
.SYNOPSIS
    Verifica contratos de evidencia visual AAA: dump VDP, baseline comparativo,
    measurement_level, propagacao de leaf blockers e isolamento de escopo.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$projectRoot = Join-Path $workspaceRoot 'out\ci\visual_gate_evidence_contracts_fixture'
$validateScript = Join-Path $wrapperRoot 'validate_resources.ps1'
$reportPath = Join-Path $projectRoot 'out\logs\validation_report.json'
$visualGatePath = Join-Path $projectRoot 'out\logs\visual_delivery_gate_report.json'

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
Write-Host '=== Visual Gate Evidence Contracts Test ==='
Write-Host ''

if (Test-Path -LiteralPath $projectRoot) {
    Remove-Item -LiteralPath $projectRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'res\bgs') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'res\data') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'src') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'doc\changelog') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'out\logs') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'out\evidence\blastem') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'data\source_art') | Out-Null
Set-Content -LiteralPath (Join-Path $projectRoot 'doc\changelog\changelog.md') -Value '# CI fixture' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $projectRoot 'data\source_art\stage_source.png') -Value 'placeholder source bytes' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $projectRoot 'res\bgs\stage_bg.png') -Value 'placeholder rom asset bytes' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $projectRoot 'res\data\dummy.bin') -Value 'dummy resource bytes' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $projectRoot 'res\resources.res') -Value 'BIN dummy_blob "data/dummy.bin"' -Encoding UTF8
[System.IO.File]::WriteAllBytes(
    (Join-Path $projectRoot 'out\evidence\blastem\visual_vdp_dump.bin'),
    [System.Text.Encoding]::ASCII.GetBytes('fake vdp dump')
)

$resGraph = @{
    vram = @{
        status = 'ok'
        overlaps = @()
    }
}
[System.IO.File]::WriteAllText((Join-Path $projectRoot 'out\logs\res_graph_report.json'), ($resGraph | ConvertTo-Json -Depth 8), [System.Text.Encoding]::UTF8)

$sceneRegression = @{
    rom_sha256 = 'fixture-rom'
    scenes = @(
        @{
            scene_key = 'fight_scene'
            status = 'captured'
        }
    )
    results = @(
        @{
            scene_key = 'fight_scene'
            scene_id = 'fight_scene'
            status = 'missing'
            baseline_path = 'doc/baselines/fight_scene'
        }
    )
}
[System.IO.File]::WriteAllText((Join-Path $projectRoot 'out\logs\scene_regression_report.json'), ($sceneRegression | ConvertTo-Json -Depth 8), [System.Text.Encoding]::UTF8)

$visualGate = @{
    schema = 'visual_delivery_gate_report.v1'
    ready_for_aaa = $true
    visual_route_status = 'delivery_candidate'
    blocking_status = 'none'
    measurement_level = 'emulator_verified'
    leaf_blocker_propagation = $true
    workspace_scope_isolation = $true
    vram_residency_status = 'ok'
    vram_residency_report = 'out/logs/res_graph_report.json'
    runtime_visual_corruption_status = 'ok'
    visual_vdp_dump_required = $true
    visual_vdp_dump_status = 'captured'
    visual_vdp_dump_path = 'out/evidence/blastem/visual_vdp_dump.bin'
    scene_regression_report = 'out/logs/scene_regression_report.json'
    critical_assets = @(
        @{
            asset_id = 'stage_main'
            role = 'stage_background'
            visual_status = 'elite_ready'
            perceptual_quality = 'measured_aaa_candidate'
            measurement_level = 'measured'
            measured = $true
            source_validity = $true
            authoriality_gate = 'passed'
            license = 'internal'
            authorial_source = 'original stage concept'
            derivative_of = 'none'
            derivative_license_status = 'original'
            clone_risk_score = 0.05
            clone_risk_method = 'fixture_hash_and_visual_review'
            benchmark_used_as = 'technical_reference'
            premium_source_path = 'data/source_art/stage_source.png'
            rom_asset_path = 'res/bgs/stage_bg.png'
            source_to_rom_visual_match = 9.0
            elite_ready = $true
        }
    )
}
[System.IO.File]::WriteAllText($visualGatePath, ($visualGate | ConvertTo-Json -Depth 10), [System.Text.Encoding]::UTF8)

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $validateScript -WorkDir $projectRoot | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "validate_resources.ps1 failed with exit code $LASTEXITCODE"
}

$report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
$visualGateDetails = @($report.details | Where-Object {
    $_.type -eq 'BLOCKING_STATUS' -and
    $_.blocking_status -eq 'visual_gate_blocked' -and
    $_.file -eq $visualGatePath
})
$findingText = ($visualGateDetails | ConvertTo-Json -Depth 8)

Assert-True 'visual gate bloqueia baseline ausente mesmo com captura' ($findingText -match 'fight_scene:baseline_missing')
Assert-True 'visual gate exige caminho de baseline persistido' ($findingText -match 'fight_scene:baseline_path_missing')
Assert-True 'visual_vdp_dump presente nao gera missing_required' (-not ($findingText -match 'visual_vdp_dump_missing_required'))
Assert-True 'measurement_level valido nao gera blocker' (-not ($findingText -match 'measurement_level_missing|measurement_level_declared|measurement_level_estimated'))
Assert-True 'workspace_scope_isolation valido nao gera blocker' (-not ($findingText -match 'workspace_scope_isolation_missing|workspace_scope_isolation_false'))

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
