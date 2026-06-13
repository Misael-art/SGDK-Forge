<#
.SYNOPSIS
    Verifies the rpg-game-design specialization is registered as active in
    the v2 registry with the correct owner_skill, design_contract_schema and
    phase_aware_blockers.
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
Write-Host '=== RPG Specialization Registry Test ==='
Write-Host ''

Assert-True 'registry JSON exists' (Test-Path -LiteralPath $registryPath) $registryPath
if (-not (Test-Path -LiteralPath $registryPath)) { Write-Host ''; Write-Host "=== Results: $passed/$total passed, $failed failed ==="; exit 1 }

$registry = Get-Content -LiteralPath $registryPath -Raw -Encoding UTF8 | ConvertFrom-Json
$entry = $null
foreach ($k in $registry.known_specializations) {
    if ($k.specialization_id -eq 'rpg_turn_based_jrpg') { $entry = $k; break }
}
Assert-True 'rpg_turn_based_jrpg entry exists' ($null -ne $entry) ('not found in registry')
if ($null -eq $entry) { Write-Host ''; Write-Host "=== Results: $passed/$total passed, $failed failed ==="; exit 1 }

Assert-True 'rpg_turn_based_jrpg status is active' ([string]$entry.status -eq 'active') ([string]$entry.status)
Assert-True 'rpg_turn_based_jrpg promotion_tier is LABORATORIO' ([string]$entry.promotion_tier -eq 'LABORATORIO') ([string]$entry.promotion_tier)
Assert-True 'rpg_turn_based_jrpg category is rpg' ([string]$entry.category -eq 'rpg') ([string]$entry.category)
Assert-True 'rpg_turn_based_jrpg owner_skill is rpg-game-design' ([string]$entry.owner_skill -match 'rpg-game-design') ([string]$entry.owner_skill)
Assert-True 'rpg_turn_based_jrpg design_contract_schema is rpg_turn_based_jrpg_design_contract.schema.json' ([string]$entry.design_contract_schema -eq 'rpg_turn_based_jrpg_design_contract.schema.json') ([string]$entry.design_contract_schema)
Assert-True 'rpg_turn_based_jrpg has frozen_design_axes' ($entry.PSObject.Properties['frozen_design_axes'] -and @($entry.frozen_design_axes.PSObject.Properties).Count -ge 4) ("$(@($entry.frozen_design_axes.PSObject.Properties).Count) axes")
Assert-True 'rpg_turn_based_jrpg frozen_design_axes.party_size_max=4' ([int]$entry.frozen_design_axes.party_size_max -eq 4) ([string]$entry.frozen_design_axes.party_size_max)
Assert-True 'rpg_turn_based_jrpg frozen_design_axes.time_unit=ticks (turn)' ([string]$entry.frozen_design_axes.time_unit -eq 'ticks (turn)') ([string]$entry.frozen_design_axes.time_unit)
Assert-True 'rpg_turn_based_jrpg frozen_design_axes.permadeath=off' ([string]$entry.frozen_design_axes.permadeath -eq 'off') ([string]$entry.frozen_design_axes.permadeath)
Assert-True 'rpg_turn_based_jrpg has at least 2 phase_aware_blockers' (@($entry.phase_aware_blockers).Count -ge 2) ("$(@($entry.phase_aware_blockers).Count) blockers")

$blkrIds = @($entry.phase_aware_blockers)
$hasRpgParty = $false
$hasRpgEncounter = $false
$hasRpgSave = $false
foreach ($b in $blkrIds) {
    if ($b -eq 'rpg_party_size_unbounded') { $hasRpgParty = $true }
    if ($b -eq 'rpg_encounter_resolution_ambiguous') { $hasRpgEncounter = $true }
    if ($b -eq 'rpg_save_corruption_risk') { $hasRpgSave = $true }
}
Assert-True 'rpg_turn_based_jrpg has blocker rpg_party_size_unbounded' $hasRpgParty ('missing')
Assert-True 'rpg_turn_based_jrpg has blocker rpg_encounter_resolution_ambiguous' $hasRpgEncounter ('missing')
Assert-True 'rpg_turn_based_jrpg has blocker rpg_save_corruption_risk' $hasRpgSave ('missing')

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
