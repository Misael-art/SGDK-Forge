<#
.SYNOPSIS
    Verifica que visual_delivery_gate_report.json bloqueia entrega AAA quando a fonte premium ou o match visual falham.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$projectRoot = Join-Path $workspaceRoot 'out\ci\visual_delivery_gate_fixture'
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
Write-Host '=== Visual Delivery Gate Report Blocker Test ==='
Write-Host ''

if (Test-Path -LiteralPath $projectRoot) {
    Remove-Item -LiteralPath $projectRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'res\data') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'src') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'doc\changelog') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'out\logs') | Out-Null
Set-Content -LiteralPath (Join-Path $projectRoot 'doc\changelog\changelog.md') -Value '# CI fixture' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $projectRoot 'res\data\dummy.bin') -Value 'dummy resource bytes' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $projectRoot 'res\resources.res') -Value 'BIN dummy_blob "data/dummy.bin"' -Encoding UTF8
$resGraph = @{
    vram = @{
        status = 'ok'
        method = 'fixture'
        measurement_level = 'estimated'
        overlaps = @()
    }
}
[System.IO.File]::WriteAllText((Join-Path $projectRoot 'out\logs\res_graph_report.json'), ($resGraph | ConvertTo-Json -Depth 8), [System.Text.Encoding]::UTF8)

$visualGate = @{
    schema = 'visual_delivery_gate_report.v1'
    ready_for_aaa = $false
    blocking_status = 'visual_gate_blocked'
    critical_assets = @(
        @{
            asset_id = 'player_bjj_fighter'
            role = 'player_character'
            visual_status = 'needs_review'
            perceptual_quality = 'nao_medido'
            premium_source_path = 'data/source_art/missing_player.png'
            rom_asset_path = 'res/sprites/player_bjj_fighter.png'
            source_validity = $false
            authoriality_gate = 'failed'
            license = ''
            authorial_source = ''
            derivative_of = 'HAMOOPIG benchmark'
            clone_risk_score = 0.72
            benchmark_similarity_index = 0.51
            benchmark_used_as = 'source_art'
            elite_ready = $false
            palette_status = 'PALETTE_WASTE'
            material_profile = 'white_gi'
            manual_palette_pass_required = $true
            manual_palette_pass = $false
            has_attack_states = $true
            bjj_state = $true
            state_belongs_to_character_fantasy = $false
            source_to_rom_visual_match = 2
            HAMOOPIG_benchmark_match = 3
            generation_channel = 'local_author_pixel_rasterization'
        }
    )
}
[System.IO.File]::WriteAllText($visualGatePath, ($visualGate | ConvertTo-Json -Depth 8), [System.Text.Encoding]::UTF8)

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

Assert-True 'visual gate permanece fechado' (-not [bool]$report.status_panel.visual_gate_ready)
Assert-True 'blocking_statuses inclui visual_gate_blocked' (@($report.blocking_statuses | Where-Object { $_ -eq 'visual_gate_blocked' }).Count -gt 0)
Assert-True 'visual_delivery_gate_report foi usado como evidencia' (@($report.status_panel.source_artifacts | Where-Object { $_ -eq $visualGatePath }).Count -gt 0)
Assert-True 'findings citam raster local final' ($findingText -match 'local_rasterization_used_as_final')
Assert-True 'findings citam premium_source_missing' ($findingText -match 'premium_source_missing')
Assert-True 'findings citam source_validity_failed' ($findingText -match 'source_validity_failed')
Assert-True 'findings citam clone_risk_score' ($findingText -match 'clone_risk_score')
Assert-True 'findings citam benchmark_similarity_index' ($findingText -match 'benchmark_similarity_index')
Assert-True 'findings citam elite_ready_missing' ($findingText -match 'elite_ready_missing')
Assert-True 'findings citam PALETTE_WASTE' ($findingText -match 'PALETTE_WASTE')
Assert-True 'findings citam contrato de gi branco' ($findingText -match 'white_material_palette_contract_missing')
Assert-True 'findings citam active_recovery_map ausente' ($findingText -match 'active_recovery_map_missing')
Assert-True 'ready_for_aaa permanece falso' (-not [bool]$report.status_panel.ready_for_aaa)

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
