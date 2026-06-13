<#
.SYNOPSIS
    Verifies the brawler_belt_scroll specialization is registered as
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
Write-Host '=== Brawler Specialization Registry Test ==='
Write-Host ''

Assert-True 'registry JSON exists' (Test-Path -LiteralPath $registryPath) $registryPath
if (-not (Test-Path -LiteralPath $registryPath)) { Write-Host ''; Write-Host "=== Results: $passed/$total passed, $failed failed ==="; exit 1 }

$registry = Get-Content -LiteralPath $registryPath -Raw -Encoding UTF8 | ConvertFrom-Json
$entry = $null
foreach ($k in $registry.known_specializations) {
    if ($k.specialization_id -eq 'brawler_belt_scroll') { $entry = $k; break }
}
Assert-True 'brawler_belt_scroll entry exists' ($null -ne $entry) ('not found in registry')
if ($null -eq $entry) { Write-Host ''; Write-Host "=== Results: $passed/$total passed, $failed failed ==="; exit 1 }

Assert-True 'brawler_belt_scroll status is active' ([string]$entry.status -eq 'active') ([string]$entry.status)
Assert-True 'brawler_belt_scroll promotion_tier is LABORATORIO' ([string]$entry.promotion_tier -eq 'LABORATORIO') ([string]$entry.promotion_tier)
Assert-True 'brawler_belt_scroll category is brawler' ([string]$entry.category -eq 'brawler') ([string]$entry.category)
Assert-True 'brawler_belt_scroll owner_skill is brawler-game-design' ([string]$entry.owner_skill -match 'brawler-game-design') ([string]$entry.owner_skill)
Assert-True 'brawler_belt_scroll design_contract_schema is brawler_belt_scroll_design_contract.schema.json' ([string]$entry.design_contract_schema -eq 'brawler_belt_scroll_design_contract.schema.json') ([string]$entry.design_contract_schema)
Assert-True 'brawler_belt_scroll has frozen_design_axes' ($entry.PSObject.Properties['frozen_design_axes'] -and @($entry.frozen_design_axes.PSObject.Properties).Count -ge 4) ("$(@($entry.frozen_design_axes.PSObject.Properties).Count) axes")
Assert-True 'brawler_belt_scroll frozen_design_axes.enemy_count_on_screen_max=8' ([int]$entry.frozen_design_axes.enemy_count_on_screen_max -eq 8) ([string]$entry.frozen_design_axes.enemy_count_on_screen_max)
Assert-True 'brawler_belt_scroll frozen_design_axes.time_unit=frames' ([string]$entry.frozen_design_axes.time_unit -eq 'frames') ([string]$entry.frozen_design_axes.time_unit)
Assert-True 'brawler_belt_scroll frozen_design_axes.camera=horizontal_lanes' ([string]$entry.frozen_design_axes.camera -eq 'horizontal_lanes') ([string]$entry.frozen_design_axes.camera)
Assert-True 'brawler_belt_scroll has at least 2 phase_aware_blockers' (@($entry.phase_aware_blockers).Count -ge 2) ("$(@($entry.phase_aware_blockers).Count) blockers")

$blkrIds = @($entry.phase_aware_blockers)
$hasIframe = $false
$hasPickup = $false
$hasWave = $false
foreach ($b in $blkrIds) {
    if ($b -eq 'brawler_iframe_window_unsafe') { $hasIframe = $true }
    if ($b -eq 'brawler_pickup_drop_unbounded') { $hasPickup = $true }
    if ($b -eq 'brawler_wave_spawner_deterministic') { $hasWave = $true }
}
Assert-True 'brawler_belt_scroll has blocker brawler_iframe_window_unsafe' $hasIframe ('missing')
Assert-True 'brawler_belt_scroll has blocker brawler_pickup_drop_unbounded' $hasPickup ('missing')
Assert-True 'brawler_belt_scroll has blocker brawler_wave_spawner_deterministic' $hasWave ('missing')

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
