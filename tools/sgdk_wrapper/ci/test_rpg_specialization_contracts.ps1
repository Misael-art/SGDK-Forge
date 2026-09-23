<#
.SYNOPSIS
    Verifies all 4 RPG specialization schemas are well-formed JSON
    Schema Draft-07 and that a minimal manifest + design contract + party
    fixture pass schema-lite validation through validate_rpg_turn_based_jrpg_specialization.ps1.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$schemasDir = Join-Path $wrapperRoot 'schemas'
$validator = Join-Path $wrapperRoot 'validate_rpg_turn_based_jrpg_specialization.ps1'
$fixtureRoot = Join-Path $workspaceRoot 'out\ci\rpg_specialization_contracts_fixture'

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
Write-Host '=== RPG Specialization Contracts Test ==='
Write-Host ''

# 1. All 4 RPG schemas parse (genre_specialization_manifest is shared)
$schemas = @(
    'rpg_turn_based_jrpg_design_contract.schema.json',
    'rpg_party_frame_data.schema.json',
    'rpg_specialization_report.schema.json',
    'genre_specialization_manifest.schema.json'
)
foreach ($s in $schemas) {
    $path = Join-Path $schemasDir $s
    Assert-True "schema file exists: $s" (Test-Path -LiteralPath $path) $path
    if (Test-Path -LiteralPath $path) {
        try {
            $obj = Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json
            Assert-True "schema parses: $s" ($null -ne $obj) ('null after parse')
            Assert-True "schema has draft-07 marker: $s" ([string]$obj.'$schema' -match 'draft-07') ([string]$obj.'$schema')
        } catch {
            Assert-True "schema parses: $s" $false $_.Exception.Message
        }
    }
}

# 2. Validator exists
Assert-True 'validate_rpg_turn_based_jrpg_specialization.ps1 exists' (Test-Path -LiteralPath $validator) $validator

# 3. Build minimal fixture: project opt-in, design contract, party frame data
if (Test-Path -LiteralPath $fixtureRoot) {
    Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'doc\party\lyra') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'doc\party\kris') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'doc\changelog') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'out\logs') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'out\balance') | Out-Null

# project methodology manifest with claim_ceiling=vertical_slice
@{
    schema_version = "1.0.0"
    project_root_policy = "all_project_material_inside_project"
    claim_ceiling = "vertical_slice"
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\project_methodology_manifest.json') -Encoding UTF8

# manifest with opt-in
@{
    schema_version = "1.0.0"
    project = @{ name = "rpg_contracts_fixture"; project_root_policy = "all_project_material_inside_project" }
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    active_specializations = @(
        @{
            specialization_id = "rpg_turn_based_jrpg"
            activation_reason = "fixture for contract validation"
            design_contract_path = "doc/rpg_turn_based_jrpg_design_contract.json"
            evidence = @{ gdd_section_ref = "doc/11-gdd.md#rpg" }
            doc_refs = @("doc/11-gdd.md", "doc/10-memory-bank.md", "doc/changelog/changelog.md")
            freeze_axes_acknowledgement = $true
        }
    )
    human_authorization = @{
        authorized_at = "2026-06-05T00:00:00Z"
        author_role = "framework_tester"
    }
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\genre_specialization_manifest.json') -Encoding UTF8

# design contract: 2 members, main_story mode, save_station, balance evidence
@{
    schema_version = "1.0.0"
    project = @{ name = "rpg_contracts_fixture" }
    specialization_id = "rpg_turn_based_jrpg"
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    time_unit = "ticks (turn)"
    party_size_max = 4
    equipment_grid = "slot_based"
    encounter_trigger = "fixed+random"
    permadeath = "off"
    narrative_branching = "linear_with_optional_scenes"
    party = @{
        size = 2
        members = @(
            @{
                id = "lyra"
                display_name = "Lyra"
                role = "leader"
                class_id = "knight"
                party_frame_data_path = "doc/party/lyra/party_frame_data.json"
                lore_id = "lyra_lore"
                head_metric = "M"
            },
            @{
                id = "kris"
                display_name = "Kris"
                role = "healer"
                class_id = "white_mage"
                party_frame_data_path = "doc/party/kris/party_frame_data.json"
                lore_id = "kris_lore"
                head_metric = "M"
            }
        )
    }
    lore = @{
        characters = @(
            @{ id = "lyra_lore"; summary = "wandering knight"; ip_status = "original" },
            @{ id = "kris_lore"; summary = "mystic healer"; ip_status = "original" }
        )
        world = @{ summary = "kingdom of Astoria" }
    }
    modes = @(
        @{ id = "main_story"; kind = "main_story"; human_or_cpu_opponent = "single_player"; save_model = "save_station" },
        @{ id = "arena"; kind = "arena"; human_or_cpu_opponent = "single_player"; save_model = "save_station" }
    )
    combat = @{
        turn_order = @{ formula = "agility_only"; tiebreaker = "level" }
        action_menu = @{ actions = @("attack", "magic", "item", "defend") }
        magic_system = @{ mp_resource = "mp_per_member"; categories = @("white_magic", "black_magic", "heal") }
        status_effects = @("poison", "sleep", "paralysis")
    }
    equipment = @{
        slot_based = $true
        slots = @("weapon", "armor", "helmet", "shield", "accessory_1")
        item_categories = @("consumable", "weapon", "armor", "key_item")
    }
    progression = @{
        xp_curve = "quadratic"
        level_cap = 50
        skill_tree_policy = "job_based"
    }
    balance = @{
        method = "encounter_playtest"
        evidence_paths = @("out/balance/playtest_log.md")
    }
    doc_refs = @("doc/11-gdd.md", "doc/10-memory-bank.md", "doc/changelog/changelog.md")
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\rpg_turn_based_jrpg_design_contract.json') -Encoding UTF8

# lyra party frame data (leader, 3+ abilities)
@{
    schema_version = "1.0.0"
    project = @{ name = "rpg_contracts_fixture" }
    member_id = "lyra"
    member_role = "leader"
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    time_unit = "ticks (turn)"
    base_stats = @{ hp = 200; mp = 30; attack = 25; defense = 22; agility = 18; magic = 10 }
    growth_curve = @{ hp_per_level = 30; mp_per_level = 2; attack_per_level = 3; defense_per_level = 3; agility_per_level = 2; magic_per_level = 1 }
    learned_abilities = @(
        @{ ability_id = "slash"; display_name = "Slash"; category = "attack"; learned_at_level = 1; mp_cost = 0; target_type = "single_enemy"; power = 30 },
        @{ ability_id = "cleave"; display_name = "Cleave"; category = "skill"; learned_at_level = 5; mp_cost = 4; target_type = "all_enemies"; power = 50 },
        @{ ability_id = "valor_strike"; display_name = "Valor Strike"; category = "ultimate"; learned_at_level = 20; mp_cost = 25; target_type = "single_enemy"; power = 200 }
    )
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\party\lyra\party_frame_data.json') -Encoding UTF8

# kris party frame data (healer, 1+ ability)
@{
    schema_version = "1.0.0"
    project = @{ name = "rpg_contracts_fixture" }
    member_id = "kris"
    member_role = "healer"
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    time_unit = "ticks (turn)"
    base_stats = @{ hp = 120; mp = 80; attack = 8; defense = 14; agility = 20; magic = 28 }
    growth_curve = @{ hp_per_level = 18; mp_per_level = 6; attack_per_level = 1; defense_per_level = 2; agility_per_level = 2; magic_per_level = 4 }
    learned_abilities = @(
        @{ ability_id = "cure"; display_name = "Cure"; category = "heal"; learned_at_level = 1; mp_cost = 4; target_type = "single_ally"; power = 40 }
    )
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\party\kris\party_frame_data.json') -Encoding UTF8

# balance evidence file
Set-Content -LiteralPath (Join-Path $fixtureRoot 'out\balance\playtest_log.md') -Value '# Playtest log' -Encoding UTF8

# changelog
Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\changelog\changelog.md') -Value '# CI fixture' -Encoding UTF8

# 4. Run validator against fixture
& powershell -NoProfile -ExecutionPolicy Bypass -File $validator -ProjectRoot $fixtureRoot | Out-Null
$validatorExit = $LASTEXITCODE
Assert-True 'validator passes on fixture (vertical_slice phase)' ($validatorExit -eq 0) ("exit=$validatorExit")

# 5. Read report and verify status
$reportPath = Join-Path $fixtureRoot 'out\logs\rpg_specialization_report.json'
Assert-True 'report file emitted' (Test-Path -LiteralPath $reportPath) $reportPath
if (Test-Path -LiteralPath $reportPath) {
    $report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-True 'report.status is ok' ([string]$report.status -eq 'ok') ([string]$report.status)
    Assert-True 'report.manifest_status is present' ([string]$report.manifest_status -eq 'present') ([string]$report.manifest_status)
    Assert-True 'report.design_contract_status is present' ([string]$report.design_contract_status -eq 'present') ([string]$report.design_contract_status)
    Assert-True 'report.party_audits has 2 entries' ($report.party_audits.Count -eq 2) ("$($report.party_audits.Count) audits")
    Assert-True 'report has 3 blockers' ($report.blockers.Count -eq 3) ("$($report.blockers.Count) blockers")
    $firedBlockers = @($report.blockers | Where-Object { $_.fired -eq $true })
    Assert-True 'vertical_slice does not fire any blocker' ($firedBlockers.Count -eq 0) ("$($firedBlockers.Count) fired")
}

# 6. Negative case: missing balance evidence file -> ready_for_aaa -> balance_evidence... not relevant for rpg;
#    use party_size_unbounded instead: party.size=10 > cap 4
$brokenRoot = Join-Path $workspaceRoot 'out\ci\rpg_specialization_contracts_broken_fixture'
if (Test-Path -LiteralPath $brokenRoot) {
    Remove-Item -LiteralPath $brokenRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $brokenRoot 'doc') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $brokenRoot 'out\logs') | Out-Null
Copy-Item -LiteralPath (Join-Path $fixtureRoot 'doc\genre_specialization_manifest.json') -Destination (Join-Path $brokenRoot 'doc\genre_specialization_manifest.json') -Force
$brokenContract = Get-Content -LiteralPath (Join-Path $fixtureRoot 'doc\rpg_turn_based_jrpg_design_contract.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$brokenContract.party.size = 10
@{
    schema_version = "1.0.0"
    project_root_policy = "all_project_material_inside_project"
    claim_ceiling = "ready_for_aaa"
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $brokenRoot 'doc\project_methodology_manifest.json') -Encoding UTF8
$brokenContract | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $brokenRoot 'doc\rpg_turn_based_jrpg_design_contract.json') -Encoding UTF8
& powershell -NoProfile -ExecutionPolicy Bypass -File $validator -ProjectRoot $brokenRoot | Out-Null
$brokenExit = $LASTEXITCODE
$brokenReportPath = Join-Path $brokenRoot 'out\logs\rpg_specialization_report.json'
Assert-True 'validator fails on broken party size (ready_for_aaa phase)' ($brokenExit -ne 0) ("exit=$brokenExit")
if (Test-Path -LiteralPath $brokenReportPath) {
    $brokenReport = Get-Content -LiteralPath $brokenReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $firedBlk = @($brokenReport.blockers | Where-Object { $_.fired -eq $true })
    $partyFired = @($firedBlk | Where-Object { $_.blocker_id -eq 'rpg_party_size_unbounded' })
    Assert-True 'rpg_party_size_unbounded fires' ($partyFired.Count -eq 1) ('not fired')
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
