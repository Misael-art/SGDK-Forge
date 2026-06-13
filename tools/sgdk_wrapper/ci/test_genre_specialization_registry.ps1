<#
.SYNOPSIS
    Verifies the genre specialization registry JSON is well-formed, has the
    expected v2 catalog (8 families, 38 specializations: 1 active from v1 + 19
    new actives, 6 future_knowledge, 10 future_architetural, 2 fighting
    sub-divisions), and the registry schema is in sync with the implementation
    (no MESTRE_* entries, no auto-promotion).
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$registryPath = Join-Path $workspaceRoot 'doc\07_game_design\genre_specialization_registry.json'
$schemaPath = Join-Path $wrapperRoot 'schemas\genre_specialization_registry.schema.json'
$matrixPath = Join-Path $workspaceRoot 'doc\07_game_design\genre_specialization_matrix.md'

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
Write-Host '=== Genre Specialization Registry Test (v2) ==='
Write-Host ''

Assert-True 'registry JSON exists' (Test-Path -LiteralPath $registryPath) $registryPath
Assert-True 'registry schema exists' (Test-Path -LiteralPath $schemaPath) $schemaPath
Assert-True 'human matrix exists' (Test-Path -LiteralPath $matrixPath) $matrixPath

if (-not (Test-Path -LiteralPath $registryPath)) { Write-Host ''; Write-Host "=== Results: $passed/$total passed, $failed failed ==="; exit 1 }

$registry = Get-Content -LiteralPath $registryPath -Raw -Encoding UTF8 | ConvertFrom-Json

Assert-True 'registry.registry_id is the canonical path' ([string]$registry.registry_id -eq 'doc/07_game_design/genre_specialization_registry.json') ([string]$registry.registry_id)
Assert-True 'registry.owner_skill is non-empty' (-not [string]::IsNullOrWhiteSpace([string]$registry.owner_skill)) ([string]$registry.owner_skill)
Assert-True 'registry.promotion_tier is LABORATORIO' ([string]$registry.promotion_tier -eq 'LABORATORIO') ([string]$registry.promotion_tier)
Assert-True 'forbidden_inferences lists at least 5 items' (@($registry.forbidden_inferences).Count -ge 5) ("$(@($registry.forbidden_inferences).Count) items")
$familyCount = @($registry.families.PSObject.Properties).Count
Assert-True 'families is non-empty object (8 families expected)' ($null -ne $registry.families -and $familyCount -ge 8) ("$familyCount families")
$legendCount = @($registry.mega_drive_feasibility_legend.PSObject.Properties).Count
Assert-True 'mega_drive_feasibility_legend has 3 keys' ($null -ne $registry.mega_drive_feasibility_legend -and $legendCount -eq 3) ("$legendCount legend keys")

$known = @($registry.known_specializations)
$knownCount = $known.Count
Assert-True 'known_specializations has 38 entries (v2 target)' ($knownCount -eq 38) ("$knownCount entries")
Assert-True 'known_specializations is non-empty' ($knownCount -ge 1) ("$knownCount items")

$fightingActive = @($known | Where-Object { $_.specialization_id -eq 'fighting_2d_traditional' -and $_.status -eq 'active' })
$fighting = if ($fightingActive.Count -gt 0) { $fightingActive[0] } else { $null }
Assert-True 'fighting_2d_traditional is active in v2' ($null -ne $fighting) ('not found')
Assert-True 'fighting_2d_traditional has time_unit=frames' ($null -ne $fighting -and [string]$fighting.frozen_design_axes.time_unit -eq 'frames') ($(if ($null -ne $fighting) { [string]$fighting.frozen_design_axes.time_unit } else { 'missing' }))
Assert-True 'fighting_2d_traditional has head_metric_policy=advisory' ($null -ne $fighting -and [string]$fighting.frozen_design_axes.head_metric_policy -eq 'advisory') ($(if ($null -ne $fighting) { [string]$fighting.frozen_design_axes.head_metric_policy } else { 'missing' }))
Assert-True 'fighting_2d_traditional has balance_evidence_required=true' ($null -ne $fighting -and [bool]$fighting.frozen_design_axes.balance_evidence_required -eq $true) ($(if ($null -ne $fighting) { [string]$fighting.frozen_design_axes.balance_evidence_required } else { 'missing' }))
Assert-True 'fighting_2d_traditional has rollback_netcode=not_applicable' ($null -ne $fighting -and [string]$fighting.frozen_design_axes.rollback_netcode -eq 'not_applicable') ($(if ($null -ne $fighting) { [string]$fighting.frozen_design_axes.rollback_netcode } else { 'missing' }))

# v2: counts
$active = @($known | Where-Object { $_.status -eq 'active' })
$deferred = @($known | Where-Object { $_.status -eq 'deferred' })
Assert-True '20 active specializations in v2' ($active.Count -eq 20) ("$($active.Count) active")
Assert-True '18 deferred specializations in v2' ($deferred.Count -eq 18) ("$($deferred.Count) deferred")

# v2: 8 families
$expectedFamilies = @('fighting', 'rpg', 'strategy', 'horror', 'brawler', 'fps', 'platformer_puzzle', 'racing_sports_adventure')
foreach ($fam in $expectedFamilies) {
    $count = @($known | Where-Object { $_.category -eq $fam }).Count
    Assert-True "family '$fam' has at least 3 entries" ($count -ge 3) ("$count entries")
}

# v2: future_architetural specs are deferred and have mega_drive_feasible=false
$architetural = @($known | Where-Object { $_.frozen_design_axes.PSObject.Properties.Name -contains 'mega_drive_feasible' -and $_.frozen_design_axes.mega_drive_feasible -eq $false })
$archCount = @($architetural).Count
Assert-True 'at least 10 future_architetural entries (mega_drive_feasible=false)' ($archCount -ge 10) ("$archCount architetural")
foreach ($arch in $architetural) {
    Assert-True "architetural '$($arch.specialization_id)' is deferred" ([string]$arch.status -eq 'deferred') ([string]$arch.status)
}

# v2: future_knowledge specs are deferred but mega_drive_feasible is not false (or missing)
$futureKnowledge = @($known | Where-Object {
    $hasFalse = $_.frozen_design_axes.PSObject.Properties.Name -contains 'mega_drive_feasible' -and $_.frozen_design_axes.mega_drive_feasible -eq $false
    $_.status -eq 'deferred' -and -not $hasFalse
})
$fkCount = @($futureKnowledge).Count
Assert-True 'at least 6 future_knowledge entries' ($fkCount -ge 6) ("$fkCount future_knowledge")

# v2: every spec has a valid owner_skill pointing to a family skill
$expectedFamilySkills = @{
    'fighting' = 'tools/sgdk_wrapper/.agent/skills/planning/fighting-game-design'
    'rpg' = 'tools/sgdk_wrapper/.agent/skills/planning/rpg-game-design'
    'strategy' = 'tools/sgdk_wrapper/.agent/skills/planning/strategy-game-design'
    'horror' = 'tools/sgdk_wrapper/.agent/skills/planning/horror-game-design'
    'brawler' = 'tools/sgdk_wrapper/.agent/skills/planning/brawler-game-design'
    'fps' = 'tools/sgdk_wrapper/.agent/skills/planning/fps-game-design'
    'platformer_puzzle' = 'tools/sgdk_wrapper/.agent/skills/planning/platformer-puzzle-game-design'
    'racing_sports_adventure' = 'tools/sgdk_wrapper/.agent/skills/planning/racing-sports-adventure-game-design'
}
foreach ($fam in $expectedFamilies) {
    $famSpecs = @($known | Where-Object { $_.category -eq $fam })
    foreach ($spec in $famSpecs) {
        $expected = $expectedFamilySkills[$fam]
        Assert-True "$($spec.specialization_id) owner_skill is $expected" ([string]$spec.owner_skill -eq $expected) ([string]$spec.owner_skill)
    }
}

# v2: design_contract_schema is non-empty
foreach ($spec in $known) {
    Assert-True "$($spec.specialization_id) has non-empty design_contract_schema" (-not [string]::IsNullOrWhiteSpace([string]$spec.design_contract_schema)) ([string]$spec.design_contract_schema)
}

# v2: phase_aware_blockers only on active specs
foreach ($spec in $active) {
    $blockers = $spec.phase_aware_blockers
    Assert-True "active '$($spec.specialization_id)' has at least 2 phase_aware_blockers" ($blockers.Count -ge 2) ("$($blockers.Count) blockers")
}

# Auto-promotion guard: no specialization is at MESTRE_*
$master = @($known | Where-Object { [string]$_.promotion_tier -like 'MESTRE_*' })
Assert-True 'no specialization at MESTRE_* tier (no auto-promotion)' ($master.Count -eq 0) ("$($master.Count) MESTRE entries")

# v2: every active spec has frozen_design_axes.time_unit defined
foreach ($spec in $active) {
    $tu = [string]$spec.frozen_design_axes.time_unit
    Assert-True "active '$($spec.specialization_id)' has time_unit defined" (-not [string]::IsNullOrWhiteSpace($tu)) ("'$tu'")
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
