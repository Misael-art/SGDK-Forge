<#
.SYNOPSIS
    Verifica blockers de sprite_artifact_report, VRAM residency e corrupcao visual runtime.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$projectRoot = Join-Path $workspaceRoot 'out\ci\visual_gate_sprite_vram_fixture'
$validateScript = Join-Path $wrapperRoot 'validate_resources.ps1'
$reportPath = Join-Path $projectRoot 'out\logs\validation_report.json'
$visualGatePath = Join-Path $projectRoot 'out\logs\visual_delivery_gate_report.json'
$spriteReportPath = Join-Path $projectRoot 'out\logs\sprite_artifact_player.json'
$resGraphReportPath = Join-Path $projectRoot 'out\logs\res_graph_report.json'

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
Write-Host '=== Visual Gate Sprite/VRAM Blocker Test ==='
Write-Host ''

if (Test-Path -LiteralPath $projectRoot) {
    Remove-Item -LiteralPath $projectRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'res\sprites') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'res\data') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'data\source_art') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'doc\changelog') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'out\logs') | Out-Null
Set-Content -LiteralPath (Join-Path $projectRoot 'doc\changelog\changelog.md') -Value '# CI fixture' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $projectRoot 'data\source_art\player.png') -Value 'source' -Encoding ASCII
Set-Content -LiteralPath (Join-Path $projectRoot 'res\sprites\player.png') -Value 'runtime' -Encoding ASCII
Set-Content -LiteralPath (Join-Path $projectRoot 'res\data\dummy.bin') -Value 'dummy resource bytes' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $projectRoot 'res\resources.res') -Value 'BIN dummy_blob "data/dummy.bin"' -Encoding UTF8

$spriteReport = @{
    schema = 'sprite_strip_integrity_report.v1'
    status = 'rework'
    image_path = 'res/sprites/player.png'
    frame_width = 96
    frame_height = 112
    frame_count = 2
    findings = @(
        @{ code = 'FRAME_EDGE_CLIPPING'; severity = 'error'; message = 'edge clipping'; frame = 1 },
        @{ code = 'NON_INDEX0_BACKGROUND_MATTE'; severity = 'error'; message = 'matte'; frame = 1 },
        @{ code = 'SMALL_ISLAND_DEBRIS'; severity = 'warning'; message = 'debris'; frame = 1 },
        @{ code = 'STRAY_LARGE_COMPONENT'; severity = 'error'; message = 'large disconnected component'; frame = 2 },
        @{ code = 'BAKED_FX_IN_CHARACTER_SHEET'; severity = 'error'; message = 'baked fx'; frame = 2 }
    )
    frames = @(
        @{ frame = 1; non_background_pixels = 10 },
        @{ frame = 2; non_background_pixels = 12 }
    )
}
[System.IO.File]::WriteAllText($spriteReportPath, ($spriteReport | ConvertTo-Json -Depth 8), [System.Text.Encoding]::UTF8)

$resGraphReport = @{
    schema_version = '1.0.0'
    status = 'warn'
    vram = @{
        status = 'collision_risk'
        sprite_reserve_tiles = 420
        tile_ranges = @()
        overlaps = @(
            @{ resource_name = 'bg_a'; overlap_with = 'sprite_engine_reserve'; overlap_start_tile = 1020; overlap_end_tile = 1060 }
        )
    }
}
[System.IO.File]::WriteAllText($resGraphReportPath, ($resGraphReport | ConvertTo-Json -Depth 8), [System.Text.Encoding]::UTF8)

$visualGate = @{
    schema = 'visual_delivery_gate_report.v1'
    ready_for_aaa = $true
    visual_route_status = 'delivery_candidate'
    blocking_status = 'none'
    measurement_level = 'emulator_verified'
    leaf_blocker_propagation = $true
    workspace_scope_isolation = $true
    vram_residency_status = 'missing'
    vram_residency_report = 'out/logs/res_graph_report.json'
    runtime_visual_corruption_status = 'garbage_tiles'
    critical_assets = @(
        @{
            asset_id = 'player'
            role = 'player_character'
            asset_kind = 'animation_strip'
            visual_status = 'elite_ready'
            perceptual_quality = 'measured'
            measurement_level = 'measured'
            measured = $true
            premium_source_path = 'data/source_art/player.png'
            rom_asset_path = 'res/sprites/player.png'
            source_validity = $true
            authoriality_gate = 'passed'
            license = 'original'
            authorial_source = 'internal'
            derivative_of = ''
            derivative_license_status = 'not_applicable'
            clone_risk_score = 0.1
            clone_risk_method = 'fixture'
            benchmark_used_as = 'technical_reference'
            elite_ready = $true
            source_to_rom_visual_match = 9
            sprite_artifact_report = 'out/logs/sprite_artifact_player.json'
            animation_preview_evidence = 'out/logs/sprite_artifact_player.json'
            contact_sheet = 'out/logs/sprite_artifact_player.json'
            pivot_overlay = 'out/logs/sprite_artifact_player.json'
            foot_contact_report = 'out/logs/sprite_artifact_player.json'
            state_belongs_to_character_fantasy = $true
            frame_envelope_integrity = $false
            index0_transparency_clean = $false
            scale_consistency = $true
            baked_fx_separated = $false
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
$findingText = ($visualGateDetails | ConvertTo-Json -Depth 10)

Assert-True 'visual gate bloqueia fixture' (-not [bool]$report.status_panel.visual_gate_ready)
Assert-True 'findings citam sprite_artifact_report rework' ($findingText -match 'sprite_artifact_report_rework')
Assert-True 'findings citam clipping' ($findingText -match 'FRAME_EDGE_CLIPPING')
Assert-True 'findings citam matte nao transparente' ($findingText -match 'NON_INDEX0_BACKGROUND_MATTE')
Assert-True 'findings citam debris de ilhas soltas' ($findingText -match 'SMALL_ISLAND_DEBRIS')
Assert-True 'findings citam componente desconectado grande' ($findingText -match 'STRAY_LARGE_COMPONENT')
Assert-True 'findings citam baked FX' ($findingText -match 'BAKED_FX_IN_CHARACTER_SHEET')
Assert-True 'findings citam VRAM missing' ($findingText -match 'vram_residency_status_missing|vram_residency_report_missing')
Assert-True 'findings citam colisao VRAM reportada' ($findingText -match 'vram_residency_report_collision_risk|vram_residency_overlap_count_1')
Assert-True 'findings citam corrupcao visual runtime' ($findingText -match 'runtime_visual_corruption_garbage_tiles')

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
