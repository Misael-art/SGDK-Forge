<#
.SYNOPSIS
    Verifica o contrato minimo do gate de direcao arte + game design.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$schemaPath = Join-Path $wrapperRoot 'schemas\art_gameplay_direction_gate.schema.json'

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
Write-Host '=== Art Gameplay Direction Gate Test ==='
Write-Host ''

Assert-True 'schema existe' (Test-Path -LiteralPath $schemaPath -PathType Leaf)

if (Test-Path -LiteralPath $schemaPath -PathType Leaf) {
    $schema = Get-Content -LiteralPath $schemaPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $required = @($schema.required)
    $blockerEnum = @($schema.properties.blockers.items.enum)
    $assetKinds = @($schema.properties.asset_kind.enum)

    Assert-True 'schema exige art_director_review' ($required -contains 'art_director_review')
    Assert-True 'schema exige game_design_context' ($required -contains 'game_design_context')
    Assert-True 'schema exige identity_continuity_lock' ($required -contains 'identity_continuity_lock')
    Assert-True 'schema cobre model_sheet' ($assetKinds -contains 'model_sheet')
    Assert-True 'schema cobre final_sprite_sheet' ($assetKinds -contains 'final_sprite_sheet')
    Assert-True 'schema cobre background_plate' ($assetKinds -contains 'background_plate')
    Assert-True 'schema possui blocker de supervisao artistica' ($blockerEnum -contains 'art_director_supervision_missing')
    Assert-True 'schema possui blocker de contexto de game design' ($blockerEnum -contains 'game_design_context_missing')
    Assert-True 'schema possui blocker de drift de coesao' ($blockerEnum -contains 'cohesion_drift')

    $fixture = @{
        schema_version = '1.0.0'
        gate_id = 'fixture_hibrido_v009_direction_gate'
        project_id = 'hibrido_muay_thai'
        asset_id = 'hibrido_fighter_sprite_sheet_v009'
        asset_kind = 'final_sprite_sheet'
        evaluated_at = '2026-06-13T00:00:00Z'
        measurement_level = 'human_visual_review'
        art_director_review = @{
            status = 'blocked'
            reviewer = 'art-director'
            findings = @('perdeu cabelo, rosto, braco de lava, roupa e acting do model sheet')
        }
        game_design_context = @{
            status = 'blocked'
            gdd_ref = 'doc/11-gdd.md'
            scene_spec_ref = 'doc/13-spec-cenas.md'
            gameplay_role = 'lutador jogavel de Muay Thai com braco de lava'
            camera_perspective = 'side_view_close_combat'
            interaction_context = @('oponente frontal', 'golpes teep, joelho, jab e guarda')
        }
        identity_continuity_lock = @{
            must_preserve = @(
                @{
                    id = 'lava_arm'
                    kind = 'signature_feature'
                    expected = 'braco de lava rochoso com rachaduras laranja'
                    status = 'failed'
                }
            )
        }
        motion_personality_contract = @{
            status = 'blocked'
            secondary_motion = @('cabelo', 'faixas', 'shorts')
            expression_requirements = @('idle focado', 'kiai em golpe')
            state_fantasy_checks = @('Muay Thai reconhecivel')
        }
        decision = @{
            production_allowed = $false
            next_required_route = @('return_to_art_directed_lineart_blocking')
        }
        blockers = @(
            'art_director_supervision_missing',
            'game_design_context_missing',
            'cohesion_drift'
        )
    }

    $roundtrip = ($fixture | ConvertTo-Json -Depth 12) | ConvertFrom-Json
    Assert-True 'fixture bloqueia producao' (-not [bool]$roundtrip.decision.production_allowed)
    Assert-True 'fixture carrega blocker de coesao' (@($roundtrip.blockers) -contains 'cohesion_drift')
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
