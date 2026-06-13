<#
.SYNOPSIS
    Verifica o contrato minimo do gate model sheet -> sprite sheet.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$schemaPath = Join-Path $wrapperRoot 'schemas\model_sheet_to_sprite_fidelity_report.schema.json'

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
Write-Host '=== Model Sheet To Sprite Fidelity Report Test ==='
Write-Host ''

$schema = Get-Content -LiteralPath $schemaPath -Raw -Encoding UTF8 | ConvertFrom-Json
$required = @($schema.required)
$blockerEnum = @($schema.properties.blockers.items.enum)

Assert-True 'schema existe' (Test-Path -LiteralPath $schemaPath -PathType Leaf)
Assert-True 'schema exige source_model_sheet' ($required -contains 'source_model_sheet')
Assert-True 'schema exige candidate_sprite_sheet' ($required -contains 'candidate_sprite_sheet')
Assert-True 'schema exige must_preserve_checks' ($required -contains 'must_preserve_checks')
Assert-True 'schema possui blocker de fidelidade' ($blockerEnum -contains 'model_sheet_to_sprite_fidelity_failed')
Assert-True 'schema possui blocker de redraw generico' ($blockerEnum -contains 'generic_blocky_redraw')

$fixture = @{
    schema_version = '1.0.0'
    asset_id = 'fixture_fighter_sheet'
    evaluated_at = '2026-06-13T00:00:00Z'
    measurement_level = 'human_visual_review'
    source_model_sheet = @{
        path = 'data/source_art/fighter/source.png'
        sha256 = '0000000000000000000000000000000000000000000000000000000000000000'
        approval_status = 'approved_as_direction'
    }
    candidate_sprite_sheet = @{
        path = 'data/processed/spritesheets/fighter.png'
        sha256 = '1111111111111111111111111111111111111111111111111111111111111111'
        cell_w = 48
        cell_h = 64
    }
    status = 'failed'
    must_preserve_checks = @(
        @{
            id = 'signature_feature'
            expected = 'feature assinatura legivel'
            observed = 'feature virou bloco generico'
            status = 'failed'
            evidence = @('fixture')
        }
    )
    frame_state_checks = @(
        @{
            id = 'idle_state'
            expected = 'idle preserva postura'
            observed = 'idle generico'
            status = 'failed'
            evidence = @('fixture')
        }
    )
    blockers = @('model_sheet_to_sprite_fidelity_failed', 'generic_blocky_redraw')
    decision = @{
        technical_pass = $true
        visual_pass = $false
        ready_for_res_promotion = $false
        ready_for_aaa = $false
        next_required_route = @('return_to_lineart_blocking_1px')
    }
}

$roundtrip = ($fixture | ConvertTo-Json -Depth 12) | ConvertFrom-Json
Assert-True 'fixture separa passe tecnico de falha visual' ([bool]$roundtrip.decision.technical_pass -and -not [bool]$roundtrip.decision.visual_pass)
Assert-True 'fixture bloqueia promocao para res' (-not [bool]$roundtrip.decision.ready_for_res_promotion)
Assert-True 'fixture carrega blocker canonico' (@($roundtrip.blockers) -contains 'model_sheet_to_sprite_fidelity_failed')

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
