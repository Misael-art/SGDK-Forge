<#
.SYNOPSIS
    Verifies the platformer_precision_2d specialization is registered as
    active in the v2 registry.
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
Write-Host '=== Platformer Specialization Registry Test ==='
Write-Host ''

Assert-True 'registry JSON exists' (Test-Path -LiteralPath $registryPath) $registryPath
if (-not (Test-Path -LiteralPath $registryPath)) { Write-Host ''; Write-Host "=== Results: $passed/$total passed, $failed failed ==="; exit 1 }

$registry = Get-Content -LiteralPath $registryPath -Raw -Encoding UTF8 | ConvertFrom-Json
$entry = $null
foreach ($k in $registry.known_specializations) {
    if ($k.specialization_id -eq 'platformer_precision_2d') { $entry = $k; break }
}
Assert-True 'platformer_precision_2d entry exists' ($null -ne $entry) ('not found in registry')
if ($null -eq $entry) { Write-Host ''; Write-Host "=== Results: $passed/$total passed, $failed failed ==="; exit 1 }

Assert-True 'platformer_precision_2d status is active' ([string]$entry.status -eq 'active') ([string]$entry.status)
Assert-True 'platformer_precision_2d promotion_tier is LABORATORIO' ([string]$entry.promotion_tier -eq 'LABORATORIO') ([string]$entry.promotion_tier)
Assert-True 'platformer_precision_2d category is platformer_puzzle' ([string]$entry.category -eq 'platformer_puzzle') ([string]$entry.category)
Assert-True 'platformer_precision_2d owner_skill is platformer-puzzle-game-design' ([string]$entry.owner_skill -match 'platformer-puzzle-game-design') ([string]$entry.owner_skill)
Assert-True 'platformer_precision_2d design_contract_schema is platformer_precision_2d_design_contract.schema.json' ([string]$entry.design_contract_schema -eq 'platformer_precision_2d_design_contract.schema.json') ([string]$entry.design_contract_schema)
Assert-True 'platformer_precision_2d has frozen_design_axes' ($entry.PSObject.Properties['frozen_design_axes'] -and @($entry.frozen_design_axes.PSObject.Properties).Count -ge 4) ("$(@($entry.frozen_design_axes.PSObject.Properties).Count) axes")
Assert-True 'platformer_precision_2d frozen_design_axes.time_unit=frames' ([string]$entry.frozen_design_axes.time_unit -eq 'frames') ([string]$entry.frozen_design_axes.time_unit)
Assert-True 'platformer_precision_2d frozen_design_axes.coyote_time=on' ([string]$entry.frozen_design_axes.coyote_time -eq 'on') ([string]$entry.frozen_design_axes.coyote_time)
Assert-True 'platformer_precision_2d frozen_design_axes.death_loop=on' ([string]$entry.frozen_design_axes.death_loop -eq 'on') ([string]$entry.frozen_design_axes.death_loop)
Assert-True 'platformer_precision_2d has at least 2 phase_aware_blockers' (@($entry.phase_aware_blockers).Count -ge 2) ("$(@($entry.phase_aware_blockers).Count) blockers")

$blkrIds = @($entry.phase_aware_blockers)
$hasCoyote = $false
$hasMetroid = $false
$hasPuzzle = $false
foreach ($b in $blkrIds) {
    if ($b -eq 'platformer_coyote_time_overflow') { $hasCoyote = $true }
    if ($b -eq 'metroidvania_ability_unlock_path') { $hasMetroid = $true }
    if ($b -eq 'puzzle_undo_count_unbounded') { $hasPuzzle = $true }
}
Assert-True 'platformer_precision_2d has blocker platformer_coyote_time_overflow' $hasCoyote ('missing')
Assert-True 'platformer_precision_2d has blocker metroidvania_ability_unlock_path' $hasMetroid ('missing')
Assert-True 'platformer_precision_2d has blocker puzzle_undo_count_unbounded' $hasPuzzle ('missing')

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
