<#
.SYNOPSIS
    Verifies the strategy_tower_defense specialization is registered as
    active in the v2 registry with correct owner_skill,
    design_contract_schema and phase_aware_blockers.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$registryPath = Join-Path $workspaceRoot 'doc\07_game_design\genre_specialization_registry.json'

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
Write-Host '=== Strategy Specialization Registry Test ==='
Write-Host ''

Assert-True 'registry JSON exists' (Test-Path -LiteralPath $registryPath) $registryPath
if (-not (Test-Path -LiteralPath $registryPath)) { Write-Host ''; Write-Host "=== Results: $passed/$total passed, $failed failed ==="; exit 1 }

$registry = Get-Content -LiteralPath $registryPath -Raw -Encoding UTF8 | ConvertFrom-Json
$entry = $null
foreach ($k in $registry.known_specializations) {
    if ($k.specialization_id -eq 'strategy_tower_defense') { $entry = $k; break }
}
Assert-True 'strategy_tower_defense entry exists' ($null -ne $entry) ('not found in registry')
if ($null -eq $entry) { Write-Host ''; Write-Host "=== Results: $passed/$total passed, $failed failed ==="; exit 1 }

Assert-True 'strategy_tower_defense status is active' ([string]$entry.status -eq 'active') ([string]$entry.status)
Assert-True 'strategy_tower_defense promotion_tier is LABORATORIO' ([string]$entry.promotion_tier -eq 'LABORATORIO') ([string]$entry.promotion_tier)
Assert-True 'strategy_tower_defense category is strategy' ([string]$entry.category -eq 'strategy') ([string]$entry.category)
Assert-True 'strategy_tower_defense owner_skill is strategy-game-design' ([string]$entry.owner_skill -match 'strategy-game-design') ([string]$entry.owner_skill)
Assert-True 'strategy_tower_defense design_contract_schema is strategy_tower_defense_design_contract.schema.json' ([string]$entry.design_contract_schema -eq 'strategy_tower_defense_design_contract.schema.json') ([string]$entry.design_contract_schema)
Assert-True 'strategy_tower_defense has frozen_design_axes' ($entry.PSObject.Properties['frozen_design_axes'] -and @($entry.frozen_design_axes.PSObject.Properties).Count -ge 4) ("$(@($entry.frozen_design_axes.PSObject.Properties).Count) axes")
Assert-True 'strategy_tower_defense frozen_design_axes.tower_slots_max=24' ([int]$entry.frozen_design_axes.tower_slots_max -eq 24) ([string]$entry.frozen_design_axes.tower_slots_max)
Assert-True 'strategy_tower_defense frozen_design_axes.time_unit=frames' ([string]$entry.frozen_design_axes.time_unit -eq 'frames') ([string]$entry.frozen_design_axes.time_unit)
Assert-True 'strategy_tower_defense frozen_design_axes.grid=fixed_path' ([string]$entry.frozen_design_axes.grid -eq 'fixed_path') ([string]$entry.frozen_design_axes.grid)
Assert-True 'strategy_tower_defense has at least 2 phase_aware_blockers' (@($entry.phase_aware_blockers).Count -ge 2) ("$(@($entry.phase_aware_blockers).Count) blockers")

$blkrIds = @($entry.phase_aware_blockers)
$hasGrid = $false
$hasAp = $false
$hasFog = $false
foreach ($b in $blkrIds) {
    if ($b -eq 'strategy_grid_vram_overflow') { $hasGrid = $true }
    if ($b -eq 'strategy_unit_ap_unbounded') { $hasAp = $true }
    if ($b -eq 'strategy_fog_of_war_race') { $hasFog = $true }
}
Assert-True 'strategy_tower_defense has blocker strategy_grid_vram_overflow' $hasGrid ('missing')
Assert-True 'strategy_tower_defense has blocker strategy_unit_ap_unbounded' $hasAp ('missing')
Assert-True 'strategy_tower_defense has blocker strategy_fog_of_war_race' $hasFog ('missing')

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
