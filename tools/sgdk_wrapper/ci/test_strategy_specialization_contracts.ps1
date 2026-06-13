<#
.SYNOPSIS
    Verifies all 4 strategy_tower_defense schemas are well-formed JSON
    Schema Draft-07 and that a minimal manifest + design contract + tower
    fixture pass schema-lite validation through validate_strategy_tower_defense_specialization.ps1.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$schemasDir = Join-Path $wrapperRoot 'schemas'
$validator = Join-Path $wrapperRoot 'validate_strategy_tower_defense_specialization.ps1'
$fixtureRoot = Join-Path $workspaceRoot 'out\ci\strategy_specialization_contracts_fixture'

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
Write-Host '=== Strategy Specialization Contracts Test ==='
Write-Host ''

$schemas = @(
    'strategy_tower_defense_design_contract.schema.json',
    'strategy_tower_frame_data.schema.json',
    'strategy_specialization_report.schema.json',
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

Assert-True 'validate_strategy_tower_defense_specialization.ps1 exists' (Test-Path -LiteralPath $validator) $validator

# Build minimal fixture
if (Test-Path -LiteralPath $fixtureRoot) { Remove-Item -LiteralPath $fixtureRoot -Recurse -Force }
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'doc\towers\arrow') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'doc\towers\cannon') | Out-Null
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
    project = @{ name = "strat_contracts_fixture"; project_root_policy = "all_project_material_inside_project" }
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    active_specializations = @(
        @{
            specialization_id = "strategy_tower_defense"
            activation_reason = "fixture for contract validation"
            design_contract_path = "doc/strategy_tower_defense_design_contract.json"
            evidence = @{ gdd_section_ref = "doc/11-gdd.md#strategy" }
            doc_refs = @("doc/11-gdd.md", "doc/10-memory-bank.md", "doc/changelog/changelog.md")
            freeze_axes_acknowledgement = $true
        }
    )
    human_authorization = @{
        authorized_at = "2026-06-05T00:00:00Z"
        author_role = "framework_tester"
    }
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\genre_specialization_manifest.json') -Encoding UTF8

# Design contract: 3 towers (damage/slow/splash), 3 enemies, 5 waves, campaign mode
@{
    schema_version = "1.0.0"
    project = @{ name = "strat_contracts_fixture" }
    specialization_id = "strategy_tower_defense"
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    time_unit = "frames"
    grid = "fixed_path"
    lane_count = "1_to_3"
    tower_slots_max = 24
    wave_spawner = "scripted"
    resource_currency = "gold"
    victory = "survive_N_waves"
    grid_layout = @{
        width_tiles = 32
        height_tiles = 24
        path_tile_count = 50
        tower_slot_count = 16
        path_geometry = "curved"
        vram_budget_estimate_kb = 32
    }
    tower_catalog = @(
        @{
            id = "arrow_tower"
            display_name = "Arrow Tower"
            category = "damage"
            tier = "basic"
            base_cost = 50
            damage = 12
            range_tiles = 3
            fire_rate_frames = 30
            tower_frame_data_path = "doc/towers/arrow/tower_frame_data.json"
            upgrade_paths = @(@{ to_tier = "advanced"; cost = 75 })
        },
        @{
            id = "frost_tower"
            display_name = "Frost Tower"
            category = "slow"
            tier = "basic"
            base_cost = 60
            damage = 5
            range_tiles = 3
            fire_rate_frames = 36
            tower_frame_data_path = "doc/towers/arrow/tower_frame_data.json"
            upgrade_paths = @(@{ to_tier = "advanced"; cost = 90 })
        },
        @{
            id = "cannon_tower"
            display_name = "Cannon Tower"
            category = "splash"
            tier = "basic"
            base_cost = 100
            damage = 30
            range_tiles = 4
            fire_rate_frames = 90
            tower_frame_data_path = "doc/towers/cannon/tower_frame_data.json"
            upgrade_paths = @(@{ to_tier = "advanced"; cost = 150 })
        }
    )
    enemy_catalog = @(
        @{ id = "grunt"; display_name = "Grunt"; archetype = "grunt"; hp = 30; speed_tiles_per_second = 3; resistance_pct = 0; gold_reward = 8 },
        @{ id = "tank"; display_name = "Tank"; archetype = "tank"; hp = 200; speed_tiles_per_second = 1; resistance_pct = 60; gold_reward = 35 },
        @{ id = "flyer"; display_name = "Flyer"; archetype = "flyer"; hp = 60; speed_tiles_per_second = 4; resistance_pct = 0; gold_reward = 18 }
    )
    wave_composition = @{
        wave_count = 10
        goal_lives = 20
        boss_wave_interval = 5
        waves = @(
            @{ wave_id = 1; spawn_groups = @(@{ enemy_id = "grunt"; count = 8; delay_between_spawns_frames = 30 }) },
            @{ wave_id = 2; spawn_groups = @(@{ enemy_id = "grunt"; count = 12; delay_between_spawns_frames = 25 }) },
            @{ wave_id = 3; spawn_groups = @(@{ enemy_id = "tank"; count = 3; delay_between_spawns_frames = 60 }) },
            @{ wave_id = 4; spawn_groups = @(@{ enemy_id = "flyer"; count = 5; delay_between_spawns_frames = 40 }) },
            @{ wave_id = 5; spawn_groups = @(@{ enemy_id = "tank"; count = 5; delay_between_spawns_frames = 50 }); is_boss_wave = $true }
        )
    }
    modes = @(
        @{ id = "campaign"; kind = "campaign"; starting_resources = 200; save_model = "save_station" }
    )
    economy = @{
        starting_currency = 200
        kill_reward_multiplier = 1.0
        wave_clear_bonus = 50
        combo_bonus = $true
        perfect_wave_bonus = $true
        speed_bonus = $false
    }
    balance = @{
        method = "tower_dps_first"
        evidence_paths = @("out/balance/wave_clear_log.md")
    }
    doc_refs = @("doc/11-gdd.md", "doc/10-memory-bank.md", "doc/changelog/changelog.md")
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\strategy_tower_defense_design_contract.json') -Encoding UTF8

# arrow tower frame data (basic only, but valid)
@{
    schema_version = "1.0.0"
    project = @{ name = "strat_contracts_fixture" }
    tower_id = "arrow_tower"
    tower_category = "damage"
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    time_unit = "frames"
    tiers = @(
        @{
            tier_id = "basic"
            tier_name = "Arrow Tower"
            cost = 50
            damage = 12
            range_tiles = 3
            fire_rate_frames = 30
            projectile_speed_tiles_per_second = 8
            animation_idle_frames = 60
            animation_fire_frames = 6
            voxel_size = "16x16"
            head_metric = "M"
        }
    )
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\towers\arrow\tower_frame_data.json') -Encoding UTF8

# cannon tower frame data (basic + advanced + elite)
@{
    schema_version = "1.0.0"
    project = @{ name = "strat_contracts_fixture" }
    tower_id = "cannon_tower"
    tower_category = "splash"
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    time_unit = "frames"
    tiers = @(
        @{
            tier_id = "basic"
            tier_name = "Cannon"
            cost = 100
            damage = 30
            range_tiles = 4
            fire_rate_frames = 90
            projectile_speed_tiles_per_second = 6
            splash_radius_tiles = 1
            animation_idle_frames = 60
            animation_fire_frames = 12
            voxel_size = "16x16"
            head_metric = "L"
        },
        @{
            tier_id = "advanced"
            tier_name = "Heavy Cannon"
            cost = 200
            damage = 60
            range_tiles = 5
            fire_rate_frames = 80
            projectile_speed_tiles_per_second = 6
            splash_radius_tiles = 2
            animation_idle_frames = 60
            animation_fire_frames = 14
            voxel_size = "16x16"
            head_metric = "L"
        },
        @{
            tier_id = "elite"
            tier_name = "Siege Cannon"
            cost = 400
            damage = 150
            range_tiles = 6
            fire_rate_frames = 70
            projectile_speed_tiles_per_second = 7
            splash_radius_tiles = 3
            ultimate_unlocked_at_wave = 8
            animation_idle_frames = 60
            animation_fire_frames = 16
            voxel_size = "16x32"
            head_metric = "XL"
        }
    )
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\towers\cannon\tower_frame_data.json') -Encoding UTF8

Set-Content -LiteralPath (Join-Path $fixtureRoot 'out\balance\wave_clear_log.md') -Value '# Wave clear log' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\changelog\changelog.md') -Value '# CI fixture' -Encoding UTF8

& powershell -NoProfile -ExecutionPolicy Bypass -File $validator -ProjectRoot $fixtureRoot | Out-Null
$validatorExit = $LASTEXITCODE
Assert-True 'validator passes on fixture (vertical_slice phase)' ($validatorExit -eq 0) ("exit=$validatorExit")

$reportPath = Join-Path $fixtureRoot 'out\logs\strategy_specialization_report.json'
Assert-True 'report file emitted' (Test-Path -LiteralPath $reportPath) $reportPath
if (Test-Path -LiteralPath $reportPath) {
    $report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-True 'report.status is ok' ([string]$report.status -eq 'ok') ([string]$report.status)
    Assert-True 'report.manifest_status is present' ([string]$report.manifest_status -eq 'present') ([string]$report.manifest_status)
    Assert-True 'report.design_contract_status is present' ([string]$report.design_contract_status -eq 'present') ([string]$report.design_contract_status)
    Assert-True 'report.tower_audits has 3 entries' ($report.tower_audits.Count -eq 3) ("$($report.tower_audits.Count) audits")
    Assert-True 'report has 3 blockers' ($report.blockers.Count -eq 3) ("$($report.blockers.Count) blockers")
    $firedBlockers = @($report.blockers | Where-Object { $_.fired -eq $true })
    Assert-True 'vertical_slice does not fire any blocker' ($firedBlockers.Count -eq 0) ("$($firedBlockers.Count) fired")
}

# Negative case: tower_slot_count=30 > cap 24, ready_for_aaa
$brokenRoot = Join-Path $workspaceRoot 'out\ci\strategy_specialization_contracts_broken_fixture'
if (Test-Path -LiteralPath $brokenRoot) { Remove-Item -LiteralPath $brokenRoot -Recurse -Force }
New-Item -ItemType Directory -Force -Path (Join-Path $brokenRoot 'doc') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $brokenRoot 'out\logs') | Out-Null
Copy-Item -LiteralPath (Join-Path $fixtureRoot 'doc\genre_specialization_manifest.json') -Destination (Join-Path $brokenRoot 'doc\genre_specialization_manifest.json') -Force
$brokenContract = Get-Content -LiteralPath (Join-Path $fixtureRoot 'doc\strategy_tower_defense_design_contract.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$brokenContract.grid_layout.tower_slot_count = 30
$brokenContract.grid_layout.vram_budget_estimate_kb = 80
@{
    schema_version = "1.0.0"
    project_root_policy = "all_project_material_inside_project"
    claim_ceiling = "ready_for_aaa"
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $brokenRoot 'doc\project_methodology_manifest.json') -Encoding UTF8
$brokenContract | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $brokenRoot 'doc\strategy_tower_defense_design_contract.json') -Encoding UTF8
& powershell -NoProfile -ExecutionPolicy Bypass -File $validator -ProjectRoot $brokenRoot | Out-Null
$brokenExit = $LASTEXITCODE
$brokenReportPath = Join-Path $brokenRoot 'out\logs\strategy_specialization_report.json'
Assert-True 'validator fails on broken grid (ready_for_aaa phase)' ($brokenExit -ne 0) ("exit=$brokenExit")
if (Test-Path -LiteralPath $brokenReportPath) {
    $brokenReport = Get-Content -LiteralPath $brokenReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $firedBlk = @($brokenReport.blockers | Where-Object { $_.fired -eq $true })
    $gridFired = @($firedBlk | Where-Object { $_.blocker_id -eq 'strategy_grid_vram_overflow' })
    Assert-True 'strategy_grid_vram_overflow fires' ($gridFired.Count -eq 1) ('not fired')
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
