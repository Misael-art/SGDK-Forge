<#
.SYNOPSIS
    Verifies the racing_arcade specialization is registered as active in the v2 registry.
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
Write-Host '=== Racing Specialization Registry Test ==='
Write-Host ''

Assert-True 'registry JSON exists' (Test-Path -LiteralPath $registryPath) $registryPath
if (-not (Test-Path -LiteralPath $registryPath)) { Write-Host ''; Write-Host "=== Results: $passed/$total passed, $failed failed ==="; exit 1 }

$registry = Get-Content -LiteralPath $registryPath -Raw -Encoding UTF8 | ConvertFrom-Json
$entry = $null
foreach ($k in $registry.known_specializations) {
    if ($k.specialization_id -eq 'racing_arcade') { $entry = $k; break }
}
Assert-True 'racing_arcade entry exists' ($null -ne $entry) ('not found in registry')
if ($null -eq $entry) { Write-Host ''; Write-Host "=== Results: $passed/$total passed, $failed failed ==="; exit 1 }

Assert-True 'racing_arcade status is active' ([string]$entry.status -eq 'active') ([string]$entry.status)
Assert-True 'racing_arcade promotion_tier is LABORATORIO' ([string]$entry.promotion_tier -eq 'LABORATORIO') ([string]$entry.promotion_tier)
Assert-True 'racing_arcade category is racing_sports_adventure' ([string]$entry.category -eq 'racing_sports_adventure') ([string]$entry.category)
Assert-True 'racing_arcade owner_skill is racing-sports-adventure-game-design' ([string]$entry.owner_skill -match 'racing-sports-adventure-game-design') ([string]$entry.owner_skill)
Assert-True 'racing_arcade design_contract_schema is racing_arcade_design_contract.schema.json' ([string]$entry.design_contract_schema -eq 'racing_arcade_design_contract.schema.json') ([string]$entry.design_contract_schema)
Assert-True 'racing_arcade has frozen_design_axes' ($entry.PSObject.Properties['frozen_design_axes'] -and @($entry.frozen_design_axes.PSObject.Properties).Count -ge 4) ("$(@($entry.frozen_design_axes.PSObject.Properties).Count) axes")
Assert-True 'racing_arcade frozen_design_axes.track_count_max=16' ([int]$entry.frozen_design_axes.track_count_max -eq 16) ([string]$entry.frozen_design_axes.track_count_max)
Assert-True 'racing_arcade frozen_design_axes.lap_count_max=5' ([int]$entry.frozen_design_axes.lap_count_max -eq 5) ([string]$entry.frozen_design_axes.lap_count_max)
Assert-True 'racing_arcade frozen_design_axes.time_unit=frames' ([string]$entry.frozen_design_axes.time_unit -eq 'frames') ([string]$entry.frozen_design_axes.time_unit)
Assert-True 'racing_arcade has at least 2 phase_aware_blockers' (@($entry.phase_aware_blockers).Count -ge 2) ("$(@($entry.phase_aware_blockers).Count) blockers")

$blkrIds = @($entry.phase_aware_blockers)
$hasCollision = $false
$hasInventory = $false
$hasSave = $false
foreach ($b in $blkrIds) {
    if ($b -eq 'racing_collision_model_audit') { $hasCollision = $true }
    if ($b -eq 'adventure_inventory_overflow') { $hasInventory = $true }
    if ($b -eq 'adventure_save_overflow') { $hasSave = $true }
}
Assert-True 'racing_arcade has blocker racing_collision_model_audit' $hasCollision ('missing')
Assert-True 'racing_arcade has blocker adventure_inventory_overflow' $hasInventory ('missing')
Assert-True 'racing_arcade has blocker adventure_save_overflow' $hasSave ('missing')

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
