<#
.SYNOPSIS
    Verifica que sprite sheets derivadas nao podem virar fonte de geracao visual.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$projectRoot = Join-Path $workspaceRoot 'out\ci\visual_source_of_truth_fixture'
$schemaPath = Join-Path $wrapperRoot 'schemas\visual_source_of_truth.schema.json'
$validateScript = Join-Path $wrapperRoot 'validate_visual_source_of_truth.ps1'
$reportPath = Join-Path $projectRoot 'out\logs\visual_source_lineage_report.json'

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
Write-Host '=== Visual Source Of Truth Gate Test ==='
Write-Host ''

if (Test-Path -LiteralPath $projectRoot) {
    Remove-Item -LiteralPath $projectRoot -Recurse -Force
}

New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'doc\contracts') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'data\source_art\fighter_v010') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'data\processed\spritesheets') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'data\builders') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'res\sprites\hibrido') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'out\logs') | Out-Null

Set-Content -LiteralPath (Join-Path $projectRoot 'data\source_art\fighter_v010\source_concept.png') -Value 'model sheet placeholder' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $projectRoot 'data\processed\spritesheets\hibrido_fighter_complete_sprite_sheet_48x64_v009.png') -Value 'bad sheet placeholder' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $projectRoot 'res\sprites\hibrido\hibrido_idle_body_48x64_strip_v010.png') -Value 'partial runtime strip placeholder' -Encoding UTF8

$goodContract = @{
    schema_version = '1.0.0'
    asset_id = 'fixture_visual_source'
    evaluated_at = '2026-06-14T00:00:00Z'
    status = 'passed'
    approved_authorial_source = @{
        path = 'data/source_art/fighter_v010/source_concept.png'
        role = 'model_sheet'
        approval_status = 'approved_authorial_model_sheet'
    }
    allowed_generation_sources = @(
        @{
            path = 'data/source_art/fighter_v010/source_concept.png'
            role = 'model_sheet'
            source_status = 'approved_authorial_model_sheet'
        },
        @{
            path = 'doc/contracts/visual_dna_manifest_v010.json'
            role = 'visual_dna'
            source_status = 'identity_contract'
        }
    )
    forbidden_generation_sources = @(
        'data/processed/spritesheets/*',
        'res/sprites/*',
        'data/processed/reports/*contact*',
        'data/processed/reports/*.gif'
    )
    obsolete_assets = @(
        @{
            path = 'data/processed/spritesheets/hibrido_fighter_complete_sprite_sheet_48x64_v009.png'
            generation_source_status = 'obsolete_for_generation_source'
            allowed_usage = @('negative_evidence', 'comparison_only')
            reason = 'human_visual_rejected'
        }
    )
    partial_runtime_candidates = @()
    lineage_scan_policy = @{
        blocked_fields = @('source', 'baseline', 'reference_for_generation', 'img2img_base')
        scan_roots = @('doc/contracts', 'data/builders', 'data/raw_ai', 'out/logs')
    }
    decision = @{
        generation_source_locked = $true
        next_sprite_sheet_must_start_from_model_sheet = $true
        ready_for_aaa = $false
    }
}

$goodPath = Join-Path $projectRoot 'doc\contracts\visual_source_of_truth_v010.json'
[System.IO.File]::WriteAllText($goodPath, ($goodContract | ConvertTo-Json -Depth 12), [System.Text.Encoding]::UTF8)

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $validateScript -ProjectRoot $projectRoot -SchemaPath $schemaPath -OutputPath $reportPath | Out-Null
$goodExit = $LASTEXITCODE
$goodReport = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json

Assert-True 'contrato positivo passa' ($goodExit -eq 0) "exit=$goodExit"
Assert-True 'contrato positivo fica sem blockers' (@($goodReport.blocking_statuses).Count -eq 0)

$badContract = $goodContract | ConvertTo-Json -Depth 12 | ConvertFrom-Json
$badContract.allowed_generation_sources = @(
    @{
        path = 'data/processed/spritesheets/hibrido_fighter_complete_sprite_sheet_48x64_v009.png'
        role = 'sprite_sheet'
        source_status = 'obsolete_for_generation_source'
    }
)
[System.IO.File]::WriteAllText($goodPath, ($badContract | ConvertTo-Json -Depth 12), [System.Text.Encoding]::UTF8)

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $validateScript -ProjectRoot $projectRoot -SchemaPath $schemaPath -OutputPath $reportPath | Out-Null
$badExit = $LASTEXITCODE
$badReport = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json

Assert-True 'sprite sheet em allowed_generation_sources falha' ($badExit -ne 0)
Assert-True 'blocker cita obsolete_for_generation_source' (@($badReport.blocking_statuses) -contains 'obsolete_generation_source_used')
Assert-True 'blocker cita forbidden_generation_source_used' (@($badReport.blocking_statuses) -contains 'forbidden_generation_source_used')

$badContract.allowed_generation_sources = @(
    @{
        path = 'data/source_art/fighter_v010/source_concept.png'
        role = 'model_sheet'
        source_status = 'approved_authorial_model_sheet'
    }
)
[System.IO.File]::WriteAllText($goodPath, ($badContract | ConvertTo-Json -Depth 12), [System.Text.Encoding]::UTF8)
Set-Content -LiteralPath (Join-Path $projectRoot 'data\builders\bad_prompt.py') -Value 'reference_for_generation = "data/processed/spritesheets/hibrido_fighter_complete_sprite_sheet_48x64_v009.png"' -Encoding UTF8

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $validateScript -ProjectRoot $projectRoot -SchemaPath $schemaPath -OutputPath $reportPath | Out-Null
$scanExit = $LASTEXITCODE
$scanReport = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json

Assert-True 'builder usando sheet como referencia de geracao falha' ($scanExit -ne 0)
Assert-True 'blocker cita visual_lineage_forbidden_reference' (@($scanReport.blocking_statuses) -contains 'visual_lineage_forbidden_reference')

Set-Content -LiteralPath (Join-Path $projectRoot 'data\builders\bad_prompt.py') -Value 'img2img_base = "res/sprites/hibrido/hibrido_idle_body_48x64_strip_v010.png"' -Encoding UTF8

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $validateScript -ProjectRoot $projectRoot -SchemaPath $schemaPath -OutputPath $reportPath | Out-Null
$resExit = $LASTEXITCODE
$resReport = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json

Assert-True 'res/sprites como img2img_base falha' ($resExit -ne 0)
Assert-True 'res/sprites em img2img_base cita visual_lineage_forbidden_reference' (@($resReport.blocking_statuses) -contains 'visual_lineage_forbidden_reference')

Set-Content -LiteralPath (Join-Path $projectRoot 'data\builders\bad_prompt.py') -Value '# harmless builder placeholder' -Encoding UTF8
$partialGate = @{
    schema = 'visual_delivery_gate_report.v1'
    ready_for_aaa = $true
    creative_blocking_statuses = @(
        'human_visual_review_missing_for_aaa',
        'visual_vdp_dump_missing'
    )
    visual_vdp_dump_status = 'missing'
    visual_route_status = 'visual_gate_blocked'
    critical_assets = @(
        @{
            asset_id = 'fixture_fighter'
            model_sheet_to_sprite_fidelity_report = @{
                path = 'doc/contracts/model_sheet_to_sprite_fidelity_report_v010.json'
                status = 'passed'
            }
        }
    )
}
[System.IO.File]::WriteAllText((Join-Path $projectRoot 'out\logs\visual_delivery_gate_report.json'), ($partialGate | ConvertTo-Json -Depth 8), [System.Text.Encoding]::UTF8)

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $validateScript -ProjectRoot $projectRoot -SchemaPath $schemaPath -OutputPath $reportPath | Out-Null
$partialExit = $LASTEXITCODE
$partialReport = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json

Assert-True 'passed parcial com human review ausente nao promove AAA' ($partialExit -ne 0)
Assert-True 'blocker cita visual_partial_pass_promoted_to_aaa' (@($partialReport.blocking_statuses) -contains 'visual_partial_pass_promoted_to_aaa')

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
