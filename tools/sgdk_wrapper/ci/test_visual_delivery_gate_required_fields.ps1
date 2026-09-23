<#
.SYNOPSIS
    Verifica que campos ausentes no visual_delivery_gate_report bloqueiam promocao visual.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$projectRoot = Join-Path $workspaceRoot 'out\ci\visual_delivery_gate_required_fields_fixture'
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
Write-Host '=== Visual Delivery Gate Required Fields Test ==='
Write-Host ''

if (Test-Path -LiteralPath $projectRoot) {
    Remove-Item -LiteralPath $projectRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'res\sprites') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'res\data') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'src') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'doc\changelog') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'out\logs') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'data\source_art') | Out-Null
Set-Content -LiteralPath (Join-Path $projectRoot 'doc\changelog\changelog.md') -Value '# CI fixture' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $projectRoot 'data\source_art\player_source.png') -Value 'placeholder source bytes' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $projectRoot 'res\sprites\player_missing_contract.png') -Value 'placeholder rom asset bytes' -Encoding UTF8
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
    ready_for_aaa = $true
    visual_route_status = 'delivery_candidate'
    blocking_status = 'none'
    critical_assets = @(
        @{
            asset_id = 'player_missing_contract'
            role = 'player_character'
            visual_status = 'elite_ready'
            perceptual_quality = 'aaa'
            premium_source_path = 'data/source_art/player_source.png'
            rom_asset_path = 'res/sprites/player_missing_contract.png'
            source_validity = $true
            authoriality_gate = 'passed'
            license = 'internal'
            authorial_source = 'original model sheet'
            derivative_of = 'none'
            benchmark_used_as = 'technical_reference'
            elite_ready = $true
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

Assert-True 'visual gate bloqueia campos obrigatorios ausentes' (-not [bool]$report.status_panel.visual_gate_ready)
Assert-True 'findings citam derivative_license_status ausente' ($findingText -match 'derivative_license_status_missing')
Assert-True 'findings citam clone_risk_score ausente' ($findingText -match 'clone_risk_score_missing')
Assert-True 'findings citam clone_risk_method ausente' ($findingText -match 'clone_risk_method_missing')
Assert-True 'findings citam source_to_rom_visual_match ausente para asset em res' ($findingText -match 'source_to_rom_visual_match_missing')
Assert-True 'findings citam measurement_level ausente no report' ($findingText -match 'measurement_level_missing')
Assert-True 'findings citam measurement_level ausente no asset' ($findingText -match 'player_missing_contract:measurement_level_missing')
Assert-True 'findings citam leaf_blocker_propagation ausente' ($findingText -match 'leaf_blocker_propagation_missing')
Assert-True 'findings citam workspace_scope_isolation ausente' ($findingText -match 'workspace_scope_isolation_missing')
Assert-True 'findings citam visual_vdp_dump obrigatorio ausente' ($findingText -match 'visual_vdp_dump_missing_required')
Assert-True 'findings citam baseline comparativo ausente' ($findingText -match 'baseline_comparison_report_missing')
Assert-True 'ready_for_aaa fica falso por blocker visual' (-not [bool]$report.status_panel.ready_for_aaa)

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
