<#
.SYNOPSIS
    Verifica que fallback de laboratorio nao pode ser promovido como entrega AAA,
    mesmo quando um visual_delivery_gate_report manual declara ready_for_aaa=true.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$projectRoot = Join-Path $workspaceRoot 'out\ci\visual_gate_lab_fallback_fixture'
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

function Test-JsonProperty {
    param([Parameter(Mandatory)]$Object, [Parameter(Mandatory)][string]$Name)
    return @($Object.PSObject.Properties | Where-Object { $_.Name -eq $Name }).Count -gt 0
}

function New-FixturePng {
    param([Parameter(Mandatory)][string]$Path)

    $script = @'
from pathlib import Path
import binascii
import struct
import sys
import zlib

path = Path(sys.argv[1])
width = 8
height = 8
palette = bytes([
    0, 0, 0,
    40, 160, 200,
    80, 200, 240,
    16, 80, 120,
])

def chunk(kind, data):
    body = kind + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", binascii.crc32(body) & 0xFFFFFFFF)

rows = []
for y in range(height):
    row = bytes([1 + ((x + y) & 1) for x in range(width)])
    rows.append(b"\x00" + row)

png = b"\x89PNG\r\n\x1a\n"
png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 3, 0, 0, 0))
png += chunk(b"PLTE", palette)
png += chunk(b"IDAT", zlib.compress(b"".join(rows)))
png += chunk(b"IEND", b"")
path.write_bytes(png)
'@
    $script | python - $Path
    if ($LASTEXITCODE -ne 0) {
        throw "failed to create indexed PNG fixture: $Path"
    }
}

Write-Host ''
Write-Host '=== Visual Gate Lab Fallback Blockers Test ==='
Write-Host ''

if (Test-Path -LiteralPath $projectRoot) {
    Remove-Item -LiteralPath $projectRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'res') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'res\bgs') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'src') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'doc\changelog') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'doc\baselines') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'out\logs') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'out\evidence\blastem') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'data\source_art') | Out-Null

Set-Content -LiteralPath (Join-Path $projectRoot 'doc\11-gdd.md') -Value 'Briefing minimo: jogo de teste com efeito visual.' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $projectRoot 'doc\changelog\changelog.md') -Value '# CI fixture' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $projectRoot 'doc\baselines\scene0.png') -Value 'baseline placeholder' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $projectRoot 'data\source_art\lab_bg_b_source.png') -Value 'source placeholder' -Encoding UTF8
New-FixturePng -Path (Join-Path $projectRoot 'res\lab_bg_b.png')
Set-Content -LiteralPath (Join-Path $projectRoot 'res\resources.res') -Value 'IMAGE bg_b_lab_plate "lab_bg_b.png" FAST' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $projectRoot 'src\main.c') -Encoding UTF8 -Value @'
#include <genesis.h>
static const char* const EFFECT_NAMES[2] = { "Mesh Alpha", "Safe Lane" };
void main(void)
{
    VDP_drawText("AAA READY", 1, 1);
    VDP_drawText("effect names visible", 1, 2);
    VDP_drawText("safe rhythm lane", 1, 3);
    VDP_drawText("efeito empurra", 1, 4);
    VDP_drawText("testado_em_emulador_via_fallba", 1, 5);
    VDP_drawText(EFFECT_NAMES[0], 1, 6);
    VDP_drawText(EFFECT_NAMES[1], 1, 7);
    VDP_drawText("debug panel", 1, 8);
    VDP_drawText("debug panel", 1, 9);
    while(1) { SYS_doVBlankProcess(); }
}
'@

[System.IO.File]::WriteAllBytes(
    (Join-Path $projectRoot 'out\evidence\blastem\visual_vdp_dump.bin'),
    [System.Text.Encoding]::ASCII.GetBytes('fake vdp dump')
)
$resGraph = @{
    vram = @{
        status = 'ok'
        method = 'fixture'
        measurement_level = 'estimated'
        overlaps = @()
    }
}
[System.IO.File]::WriteAllText((Join-Path $projectRoot 'out\logs\res_graph_report.json'), ($resGraph | ConvertTo-Json -Depth 8), [System.Text.Encoding]::UTF8)
$sceneRegression = @{
    results = @(
        @{
            scene_key = 'scene0'
            scene_id = 'scene0'
            status = 'passed'
            baseline_path = (Join-Path $projectRoot 'doc\baselines\scene0.png')
        }
    )
}
[System.IO.File]::WriteAllText((Join-Path $projectRoot 'out\logs\scene_regression_report.json'), ($sceneRegression | ConvertTo-Json -Depth 8), [System.Text.Encoding]::UTF8)

$semanticAudit = @{
    status = 'failed'
    summary = @{
        status = 'failed'
        blockers = 1
    }
    findings = @(
        @{
            severity = 'blocker'
            code = 'repeated_effect_learning_notes'
            message = 'fixture semantic blocker'
        }
    )
}
[System.IO.File]::WriteAllText((Join-Path $projectRoot 'out\logs\semantic_audit_report.json'), ($semanticAudit | ConvertTo-Json -Depth 8), [System.Text.Encoding]::UTF8)

$visualGate = @{
    schema = 'visual_delivery_gate_report.v1'
    ready_for_aaa = $true
    visual_route_status = 'delivery_candidate'
    blocking_status = 'none'
    visual_direction_status = 'failed'
    visual_direction_findings = @(
        'repetitive_pattern',
        'text_panel_debug',
        'generic_character',
        'static_rain',
        'debug_mosaic',
        'poor_procedural_asset'
    )
    decision_log = @(
        'decisao global rasa'
    )
    measurement_level = 'vdp_dump_verified'
    leaf_blocker_propagation = $true
    workspace_scope_isolation = $true
    anti_lab_fallback = @{
        lab_bg_b_absent = $true
        vdp_drawtext_not_dominant = $true
        effect_names_not_visible = $true
        debug_panel_absent = $true
        axis_specific_playable_scene = $true
    }
    vram_residency_status = 'ok'
    vram_residency_report = 'out/logs/res_graph_report.json'
    runtime_visual_corruption_status = 'ok'
    visual_vdp_dump_required = $true
    visual_vdp_dump_status = 'captured'
    visual_vdp_dump_path = 'out/evidence/blastem/visual_vdp_dump.bin'
    baseline_comparison_status = 'passed'
    critical_assets = @(
        @{
            asset_id = 'bg_b_lab_plate'
            role = 'stage_background'
            visual_status = 'elite_ready'
            perceptual_quality = 'measured_aaa_candidate'
            measurement_level = 'vdp_dump_verified'
            measured = $true
            source_validity = $true
            authoriality_gate = 'passed'
            license = 'internal'
            authorial_source = 'fixture'
            derivative_of = 'none'
            derivative_license_status = 'original'
            clone_risk_score = 0.05
            clone_risk_method = 'fixture'
            benchmark_used_as = 'technical_reference'
            premium_source_path = 'data/source_art/lab_bg_b_source.png'
            rom_asset_path = 'res/lab_bg_b.png'
            source_to_rom_visual_match = 9.0
            elite_ready = $true
            benchmark_profile_required_match = 8.0
            benchmark_match = 9.0
            generation_channel = 'procedural_renderer'
        }
        @{
            asset_id = 'hero_character'
            role = 'player_character'
            asset_kind = 'character_animation_strip'
            requires_animation_gate = $true
            visual_status = 'elite_ready'
            perceptual_quality = 'measured_aaa_candidate'
            measurement_level = 'vdp_dump_verified'
            measured = $true
            source_validity = $true
            authoriality_gate = 'passed'
            license = 'internal'
            authorial_source = 'fixture'
            derivative_of = 'none'
            derivative_license_status = 'original'
            clone_risk_score = 0.05
            clone_risk_method = 'fixture'
            benchmark_used_as = 'technical_reference'
            premium_source_path = 'data/source_art/lab_bg_b_source.png'
            rom_asset_path = 'res/lab_bg_b.png'
            source_to_rom_visual_match = 9.0
            elite_ready = $true
            benchmark_profile_required_match = 8.0
            benchmark_match = 9.0
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

Assert-True 'visual gate bloqueia falso AAA de laboratorio' (-not [bool]$report.status_panel.visual_gate_ready)
Assert-True 'findings citam lab_bg_b promovido' ($findingText -match 'project_static_audit:lab_bg_b_resource_promoted')
Assert-True 'findings citam VDP_drawText dominante sem sprites' ($findingText -match 'project_static_audit:vdp_drawtext_dominant_without_sprites')
Assert-True 'findings citam catalogo EFFECT_NAMES em runtime' ($findingText -match 'project_static_audit:effect_names_catalog_in_runtime')
Assert-True 'findings citam safe lane/debug text' ($findingText -match 'project_static_audit:safe_lane_debug_text_in_runtime')
Assert-True 'findings citam status debug promovido' ($findingText -match 'project_static_audit:debug_status_text_promoted')
Assert-True 'findings citam renderer procedural promovido' ($findingText -match 'bg_b_lab_plate:local_rasterization_used_as_final')
Assert-True 'static audit conta chamadas VDP_drawText' ($findingText -match '"vdp_draw_text_calls":\s*9')
$hasTechnicalReady = Test-JsonProperty -Object $report.status_panel -Name 'technical_ready'
$hasCreativeReady = Test-JsonProperty -Object $report.status_panel -Name 'creative_ready'
$hasTechnicalArtifactStatus = Test-JsonProperty -Object $report.status_panel -Name 'technical_artifact_status'
$hasAggregateStatus = Test-JsonProperty -Object $report.status_panel -Name 'aggregate_status'
$hasAggregateDeprecated = Test-JsonProperty -Object $report.status_panel -Name 'aggregate_status_deprecated'
$hasSemanticStatus = Test-JsonProperty -Object $report.status_panel -Name 'semantic_audit_status'
$hasMaxDeliveryStatus = Test-JsonProperty -Object $report.status_panel -Name 'max_delivery_status'
$hasCreativeBlockingStatuses = Test-JsonProperty -Object $report.status_panel -Name 'creative_blocking_statuses'

Assert-True 'status_panel expoe technical_ready' $hasTechnicalReady
Assert-True 'status_panel expoe creative_ready falso' ($hasCreativeReady -and -not [bool]$report.status_panel.creative_ready)
Assert-True 'technical_artifact_status substitui aggregate_status' ($hasTechnicalArtifactStatus -and [string]$report.status_panel.technical_artifact_status -ne '')
Assert-True 'aggregate_status permanece alias deprecated' (
    $hasAggregateStatus -and
    $hasAggregateDeprecated -and
    [string]$report.status_panel.aggregate_status -eq [string]$report.status_panel.technical_artifact_status -and
    [bool]$report.status_panel.aggregate_status_deprecated
)
Assert-True 'semantic audit failed vira blocker canonico' (@($report.blocking_statuses) -contains 'semantic_audit_failed')
Assert-True 'semantic_audit_status fica failed' ($hasSemanticStatus -and [string]$report.status_panel.semantic_audit_status -eq 'failed')
Assert-True 'fallback procedural limita max_delivery_status' ($hasMaxDeliveryStatus -and [string]$report.status_panel.max_delivery_status -eq 'technical_lab_validated')
Assert-True 'fallback procedural bloqueia creative_ready' (@($report.blocking_statuses) -contains 'procedural_fallback_as_final')
Assert-True 'GDD raso bloqueia creative_ready' (@($report.blocking_statuses) -contains 'gdd_substantial_insufficient')
Assert-True 'direcao visual falha bloqueia' (@($report.blocking_statuses) -contains 'visual_direction_failed')
Assert-True 'decision log raso bloqueia' (@($report.blocking_statuses) -contains 'decision_log_too_shallow')
Assert-True 'evidencia por eixo ausente bloqueia' (@($report.blocking_statuses) -contains 'axis_evidence_missing')
Assert-True 'consequencia jogavel ausente bloqueia' (@($report.blocking_statuses) -contains 'gameplay_consequence_missing')
Assert-True 'animation gate premium bloqueia' (@($report.blocking_statuses) -contains 'animation_gate_failed')
Assert-True 'creative_blocking_statuses lista blockers criativos' (
    $hasCreativeBlockingStatuses -and
    @($report.status_panel.creative_blocking_statuses) -contains 'semantic_audit_failed' -and
    @($report.status_panel.creative_blocking_statuses) -contains 'visual_direction_failed' -and
    @($report.status_panel.creative_blocking_statuses) -contains 'gdd_substantial_insufficient'
)
Assert-True 'ready_for_aaa fica falso' (-not [bool]$report.status_panel.ready_for_aaa)

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
