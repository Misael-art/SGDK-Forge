<#
.SYNOPSIS
    Verifies all 4 brawler_belt_scroll schemas are well-formed JSON
    Schema Draft-07 and that a minimal manifest + design contract + enemy
    archetype fixture pass schema-lite validation through
    validate_brawler_belt_scroll_specialization.ps1.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$schemasDir = Join-Path $wrapperRoot 'schemas'
$validator = Join-Path $wrapperRoot 'validate_brawler_belt_scroll_specialization.ps1'
$fixtureRoot = Join-Path $workspaceRoot 'out\ci\brawler_specialization_contracts_fixture'

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
Write-Host '=== Brawler Specialization Contracts Test ==='
Write-Host ''

$schemas = @(
    'brawler_belt_scroll_design_contract.schema.json',
    'brawler_enemy_archetype_frame_data.schema.json',
    'brawler_specialization_report.schema.json',
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

Assert-True 'validate_brawler_belt_scroll_specialization.ps1 exists' (Test-Path -LiteralPath $validator) $validator

# Build minimal fixture
if (Test-Path -LiteralPath $fixtureRoot) { Remove-Item -LiteralPath $fixtureRoot -Recurse -Force }
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'doc\enemies\grunt') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'doc\enemies\boss') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'doc\changelog') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'out\logs') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'out\balance') | Out-Null

@{
    schema_version = "1.0.0"
    project_root_policy = "all_project_material_inside_project"
    claim_ceiling = "vertical_slice"
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\project_methodology_manifest.json') -Encoding UTF8

@{
    schema_version = "1.0.0"
    project = @{ name = "brawl_contracts_fixture"; project_root_policy = "all_project_material_inside_project" }
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    active_specializations = @(
        @{
            specialization_id = "brawler_belt_scroll"
            activation_reason = "fixture for contract validation"
            design_contract_path = "doc/brawler_belt_scroll_design_contract.json"
            evidence = @{ gdd_section_ref = "doc/11-gdd.md#brawler" }
            doc_refs = @("doc/11-gdd.md", "doc/10-memory-bank.md", "doc/changelog/changelog.md")
            freeze_axes_acknowledgement = $true
        }
    )
    human_authorization = @{
        authorized_at = "2026-06-05T00:00:00Z"
        author_role = "framework_tester"
    }
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\genre_specialization_manifest.json') -Encoding UTF8

# Design contract: 2 players, 4 enemy archetypes (grunt/heavy/runner/boss), 3 pickups, 3 stages
@{
    schema_version = "1.0.0"
    project = @{ name = "brawl_contracts_fixture" }
    specialization_id = "brawler_belt_scroll"
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    time_unit = "frames"
    camera = "horizontal_lanes"
    player_count = "1_to_2"
    enemy_count_on_screen_max = 8
    pickup_drop = "health_and_score"
    stage_progression = "linear_with_bosses"
    iframe_on_hit = "on"
    player_roster = @(
        @{
            id = "axel"
            display_name = "Axel Stone"
            role = "player_1"
            archetype = "brawler"
            starting_hp = 120
            iframe_frames = 16
            special_move_id = "special_uppercut"
            lore_id = "axel_lore"
            head_metric = "M"
        },
        @{
            id = "blaze"
            display_name = "Blaze Fielding"
            role = "player_2"
            archetype = "speedster"
            starting_hp = 100
            iframe_frames = 12
            special_move_id = "special_somersault"
            lore_id = "blaze_lore"
            head_metric = "M"
        }
    )
    enemy_archetypes = @(
        @{ id = "grunt"; display_name = "Thug"; archetype = "grunt"; enemy_archetype_frame_data_path = "doc/enemies/grunt/enemy_archetype_frame_data.json"; spawn_pattern = "off_screen_left" },
        @{ id = "heavy"; display_name = "Big Joe"; archetype = "heavy"; enemy_archetype_frame_data_path = "doc/enemies/grunt/enemy_archetype_frame_data.json"; spawn_pattern = "off_screen_right" },
        @{ id = "runner"; display_name = "Sprinter"; archetype = "runner"; enemy_archetype_frame_data_path = "doc/enemies/grunt/enemy_archetype_frame_data.json"; spawn_pattern = "off_screen_left" },
        @{ id = "boss_kungfu"; display_name = "Mr. X"; archetype = "boss"; enemy_archetype_frame_data_path = "doc/enemies/boss/enemy_archetype_frame_data.json"; spawn_pattern = "door" }
    )
    pickup_catalog = @(
        @{ id = "health_small"; display_name = "Small Potion"; category = "health"; drop_chance_pct = 30; max_on_screen = 4; value = 20 },
        @{ id = "score_bag"; display_name = "Money Bag"; category = "score"; drop_chance_pct = 50; max_on_screen = 8; value = 100 },
        @{ id = "life_orb"; display_name = "1UP"; category = "extra_life"; drop_chance_pct = 3; max_on_screen = 1 }
    )
    stages = @(
        @{ id = "stage_1_subway"; display_name = "Subway Streets"; lane_count = 2; wave_count = 4; boss_archetype_id = "boss_kungfu"; boss_phases = 2; hazard_policy = "soft_hazards"; bg_music_loop_seconds = 32 },
        @{ id = "stage_2_pier"; display_name = "Harbor Pier"; lane_count = 3; wave_count = 5; boss_archetype_id = "boss_kungfu"; boss_phases = 3; hazard_policy = "soft_hazards"; bg_music_loop_seconds = 40 },
        @{ id = "stage_3_factory"; display_name = "Syndicate Factory"; lane_count = 2; wave_count = 6; boss_archetype_id = "boss_kungfu"; boss_phases = 3; hazard_policy = "lethal_hazards"; bg_music_loop_seconds = 48 }
    )
    modes = @(
        @{ id = "arcade"; kind = "arcade"; starting_lives = 3; continue_policy = "limited_3" }
    )
    combat = @{
        move_set = @("punch", "kick", "grab", "throw", "jump", "special")
        iframe_window_frames = 16
        grab_throw_enabled = $true
        super_bar_max = 100
        knockback_px = 16
        hit_stun_frames = 12
    }
    balance = @{
        method = "wave_playtest"
        evidence_paths = @("out/balance/wave_clear_log.md")
    }
    doc_refs = @("doc/11-gdd.md", "doc/10-memory-bank.md", "doc/changelog/changelog.md")
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\brawler_belt_scroll_design_contract.json') -Encoding UTF8

# grunt archetype frame data (used by grunt, heavy, runner)
@{
    schema_version = "1.0.0"
    project = @{ name = "brawl_contracts_fixture" }
    archetype_id = "grunt"
    archetype_role = "grunt"
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    time_unit = "frames"
    base_stats = @{ hp = 10; damage = 4; move_speed_px_per_second = 60; score_reward = 100; hit_stun_frames = 10; iframe_frames = 0 }
    drop_table = @{
        drop_pool = @(
            @{ pickup_id = "health_small"; drop_chance_pct = 15 },
            @{ pickup_id = "score_bag"; drop_chance_pct = 50 }
        )
    }
    animation = @{
        animation_idle_frames = 30
        animation_attack_frames = 12
        animation_hit_frames = 8
        animation_death_frames = 24
        voxel_size = "16x24"
        head_metric = "M"
    }
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\enemies\grunt\enemy_archetype_frame_data.json') -Encoding UTF8

# boss archetype frame data (must have >=2 boss_phases)
@{
    schema_version = "1.0.0"
    project = @{ name = "brawl_contracts_fixture" }
    archetype_id = "boss_kungfu"
    archetype_role = "boss"
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    time_unit = "frames"
    base_stats = @{ hp = 300; damage = 18; move_speed_px_per_second = 40; score_reward = 5000; hit_stun_frames = 16; iframe_frames = 0 }
    drop_table = @{
        drop_pool = @()
        guaranteed_drop = "life_orb"
    }
    animation = @{
        animation_idle_frames = 30
        animation_attack_frames = 20
        animation_hit_frames = 12
        animation_death_frames = 60
        voxel_size = "32x32"
        head_metric = "L"
    }
    boss_phases = @(
        @{ phase_id = 1; hp_threshold_pct = 100; behavior = "attack_pattern_1"; attack_pattern_frames = 240 },
        @{ phase_id = 2; hp_threshold_pct = 50; behavior = "rage_mode"; attack_pattern_frames = 360 },
        @{ phase_id = 3; hp_threshold_pct = 25; behavior = "summon_adds"; attack_pattern_frames = 480 }
    )
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\enemies\boss\enemy_archetype_frame_data.json') -Encoding UTF8

Set-Content -LiteralPath (Join-Path $fixtureRoot 'out\balance\wave_clear_log.md') -Value '# Wave clear log' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\changelog\changelog.md') -Value '# CI fixture' -Encoding UTF8

& powershell -NoProfile -ExecutionPolicy Bypass -File $validator -ProjectRoot $fixtureRoot | Out-Null
$validatorExit = $LASTEXITCODE
Assert-True 'validator passes on fixture (vertical_slice phase)' ($validatorExit -eq 0) ("exit=$validatorExit")

$reportPath = Join-Path $fixtureRoot 'out\logs\brawler_specialization_report.json'
Assert-True 'report file emitted' (Test-Path -LiteralPath $reportPath) $reportPath
if (Test-Path -LiteralPath $reportPath) {
    $report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-True 'report.status is ok' ([string]$report.status -eq 'ok') ([string]$report.status)
    Assert-True 'report.manifest_status is present' ([string]$report.manifest_status -eq 'present') ([string]$report.manifest_status)
    Assert-True 'report.design_contract_status is present' ([string]$report.design_contract_status -eq 'present') ([string]$report.design_contract_status)
    Assert-True 'report.enemy_archetype_audits has 4 entries' ($report.enemy_archetype_audits.Count -eq 4) ("$($report.enemy_archetype_audits.Count) audits")
    Assert-True 'report has 3 blockers' ($report.blockers.Count -eq 3) ("$($report.blockers.Count) blockers")
    $firedBlockers = @($report.blockers | Where-Object { $_.fired -eq $true })
    Assert-True 'vertical_slice does not fire any blocker' ($firedBlockers.Count -eq 0) ("$($firedBlockers.Count) fired")
}

# Negative case: player iframe_frames=4 (<8) and pickup chance=60 max=10 -> ready_for_aaa
$brokenRoot = Join-Path $workspaceRoot 'out\ci\brawler_specialization_contracts_broken_fixture'
if (Test-Path -LiteralPath $brokenRoot) { Remove-Item -LiteralPath $brokenRoot -Recurse -Force }
New-Item -ItemType Directory -Force -Path (Join-Path $brokenRoot 'doc') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $brokenRoot 'out\logs') | Out-Null
Copy-Item -LiteralPath (Join-Path $fixtureRoot 'doc\genre_specialization_manifest.json') -Destination (Join-Path $brokenRoot 'doc\genre_specialization_manifest.json') -Force
New-Item -ItemType Directory -Force -Path (Join-Path $brokenRoot 'doc\enemies\grunt') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $brokenRoot 'doc\enemies\boss') | Out-Null
Copy-Item -LiteralPath (Join-Path $fixtureRoot 'doc\enemies\grunt\enemy_archetype_frame_data.json') -Destination (Join-Path $brokenRoot 'doc\enemies\grunt\enemy_archetype_frame_data.json') -Force
Copy-Item -LiteralPath (Join-Path $fixtureRoot 'doc\enemies\boss\enemy_archetype_frame_data.json') -Destination (Join-Path $brokenRoot 'doc\enemies\boss\enemy_archetype_frame_data.json') -Force
$brokenContract = Get-Content -LiteralPath (Join-Path $fixtureRoot 'doc\brawler_belt_scroll_design_contract.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$brokenContract.player_roster[0].iframe_frames = 4
# Update pickup to trigger pickup_drop_unbounded
$brokenContract.pickup_catalog[1].drop_chance_pct = 60
$brokenContract.pickup_catalog[1].max_on_screen = 10
@{
    schema_version = "1.0.0"
    project_root_policy = "all_project_material_inside_project"
    claim_ceiling = "ready_for_aaa"
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $brokenRoot 'doc\project_methodology_manifest.json') -Encoding UTF8
$brokenContract | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $brokenRoot 'doc\brawler_belt_scroll_design_contract.json') -Encoding UTF8
& powershell -NoProfile -ExecutionPolicy Bypass -File $validator -ProjectRoot $brokenRoot | Out-Null
$brokenExit = $LASTEXITCODE
$brokenReportPath = Join-Path $brokenRoot 'out\logs\brawler_specialization_report.json'
Assert-True 'validator fails on broken iframe + pickup (ready_for_aaa phase)' ($brokenExit -ne 0) ("exit=$brokenExit")
if (Test-Path -LiteralPath $brokenReportPath) {
    $brokenReport = Get-Content -LiteralPath $brokenReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $firedBlk = @($brokenReport.blockers | Where-Object { $_.fired -eq $true })
    $iframeFired = @($firedBlk | Where-Object { $_.blocker_id -eq 'brawler_iframe_window_unsafe' })
    Assert-True 'brawler_iframe_window_unsafe fires' ($iframeFired.Count -eq 1) ('not fired')
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
