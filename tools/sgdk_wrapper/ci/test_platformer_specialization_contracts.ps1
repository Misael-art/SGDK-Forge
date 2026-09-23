<#
.SYNOPSIS
    Verifies all 4 platformer_precision_2d schemas are well-formed JSON
    Schema Draft-07 and a minimal fixture passes validation.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$schemasDir = Join-Path $wrapperRoot 'schemas'
$validator = Join-Path $wrapperRoot 'validate_platformer_precision_2d_specialization.ps1'
$fixtureRoot = Join-Path $workspaceRoot 'out\ci\platformer_specialization_contracts_fixture'

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
Write-Host '=== Platformer Specialization Contracts Test ==='
Write-Host ''

$schemas = @(
    'platformer_precision_2d_design_contract.schema.json',
    'platformer_level_segment_frame_data.schema.json',
    'platformer_specialization_report.schema.json',
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

Assert-True 'validate_platformer_precision_2d_specialization.ps1 exists' (Test-Path -LiteralPath $validator) $validator

# Build minimal fixture
if (Test-Path -LiteralPath $fixtureRoot) { Remove-Item -LiteralPath $fixtureRoot -Recurse -Force }
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'doc\levels\level_1') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'doc\levels\level_2') | Out-Null
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
    project = @{ name = "plat_contracts_fixture"; project_root_policy = "all_project_material_inside_project" }
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    active_specializations = @(
        @{
            specialization_id = "platformer_precision_2d"
            activation_reason = "fixture for contract validation"
            design_contract_path = "doc/platformer_precision_2d_design_contract.json"
            evidence = @{ gdd_section_ref = "doc/11-gdd.md#platformer" }
            doc_refs = @("doc/11-gdd.md", "doc/10-memory-bank.md", "doc/changelog/changelog.md")
            freeze_axes_acknowledgement = $true
        }
    )
    human_authorization = @{
        authorized_at = "2026-06-05T00:00:00Z"
        author_role = "framework_tester"
    }
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\genre_specialization_manifest.json') -Encoding UTF8

# Design contract: 1 player, 2 abilities, 3 hazards, 3 collectibles, 6 levels
@{
    schema_version = "1.0.0"
    project = @{ name = "plat_contracts_fixture" }
    specialization_id = "platformer_precision_2d"
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    time_unit = "frames"
    camera = "side_scroll_with_lookahead"
    run_speed_horizontal = "2x_player"
    jump_count = "1_to_2"
    coyote_time = "on"
    death_loop = "on"
    level_length = "short_tight"
    player_profile = @{
        run_speed_px_per_frame = 3
        walk_speed_px_per_frame = 2
        jump_velocity_px_per_frame = 12
        gravity_px_per_frame_squared = 2
        max_jump_height_tiles = 5
        coyote_time_frames = 5
        jump_buffer_frames = 5
        wall_jump_enabled = $true
        dash_enabled = $true
        dash_duration_frames = 8
        starting_lives = 3
        instant_restart = $true
        voxel_size = "16x16"
    }
    ability_set = @(
        @{ id = "wall_jump"; display_name = "Wall Jump"; category = "movement"; frames_active = 8; frames_cooldown = 30 },
        @{ id = "dash"; display_name = "Dash"; category = "movement"; frames_active = 10; frames_cooldown = 60 }
    )
    hazard_catalog = @(
        @{ id = "spike"; display_name = "Spike"; category = "spike"; damage = 99; respawn_pattern = "instant_on_death" },
        @{ id = "saw"; display_name = "Saw"; category = "saw"; damage = 99; respawn_pattern = "loop_forever" },
        @{ id = "fire"; display_name = "Fire"; category = "fire"; damage = 50; respawn_pattern = "loop_forever" }
    )
    collectible_catalog = @(
        @{ id = "coin"; display_name = "Coin"; category = "coin"; value = 100; respawn_pattern = "on_death" },
        @{ id = "gem"; display_name = "Gem"; category = "gem"; value = 1000; respawn_pattern = "once_per_run" },
        @{ id = "extra_life"; display_name = "1UP"; category = "extra_life"; value = 1; respawn_pattern = "once_per_run" }
    )
    level_catalog = @(
        @{ level_id = "level_1"; display_name = "Green Hill"; length_tiles = 200; hazards_count = 5; collectibles_count = 8; level_segment_frame_data_path = "doc/levels/level_1/level_segment_frame_data.json"; par_time_seconds = 45 },
        @{ level_id = "level_2"; display_name = "Bridge Zone"; length_tiles = 180; hazards_count = 7; collectibles_count = 6; level_segment_frame_data_path = "doc/levels/level_2/level_segment_frame_data.json"; par_time_seconds = 50 },
        @{ level_id = "level_3"; display_name = "Sky High"; length_tiles = 220; hazards_count = 4; collectibles_count = 5; level_segment_frame_data_path = "doc/levels/level_1/level_segment_frame_data.json"; par_time_seconds = 55 },
        @{ level_id = "level_4"; display_name = "Lava Cave"; length_tiles = 240; hazards_count = 9; collectibles_count = 7; level_segment_frame_data_path = "doc/levels/level_1/level_segment_frame_data.json"; par_time_seconds = 60 },
        @{ level_id = "level_5"; display_name = "Robotnik Boss"; length_tiles = 160; hazards_count = 3; collectibles_count = 4; level_segment_frame_data_path = "doc/levels/level_1/level_segment_frame_data.json"; par_time_seconds = 40 }
    )
    modes = @(
        @{ id = "story"; kind = "story"; lives_policy = "limited_3"; score_policy = "time_and_collectibles" },
        @{ id = "speedrun"; kind = "speedrun"; lives_policy = "no_lives"; score_policy = "time_only" }
    )
    balance = @{
        method = "playtest_first"
        evidence_paths = @("out/balance/clear_time_log.md")
        difficulty_curve_path = "out/balance/difficulty_curve.json"
    }
    doc_refs = @("doc/11-gdd.md", "doc/10-memory-bank.md", "doc/changelog/changelog.md")
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\platformer_precision_2d_design_contract.json') -Encoding UTF8

# level_1 frame data
@{
    schema_version = "1.0.0"
    project = @{ name = "plat_contracts_fixture" }
    level_id = "level_1"
    level_role = "tutorial"
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    time_unit = "frames"
    layout = @{
        width_tiles = 200
        height_tiles = 16
        tile_size_px = 16
        gravity_zone_count = 1
        ceiling_y_px = 32
        floor_y_px = 224
    }
    parallax_layers = @(
        @{ layer_id = "bg_far"; parallax_factor = 0.2; tile_count = 32; animation_idle_frames = 60 },
        @{ layer_id = "bg_mid"; parallax_factor = 0.5; tile_count = 48; animation_idle_frames = 30 },
        @{ layer_id = "bg_near"; parallax_factor = 0.8; tile_count = 64; animation_idle_frames = 15 }
    )
    hazard_zones = @(
        @{ hazard_id = "spike"; x_start_tile = 50; x_end_tile = 54; y_tile = 14; frames_active = 60; frames_idle = 0 }
    )
    collectible_zones = @(
        @{ collectible_id = "coin"; x_tile = 30; y_tile = 10; respawn_pattern = "on_death" }
    )
    jump_arcs = @(
        @{ arc_id = "normal_jump"; max_height_tiles = 5; horizontal_distance_tiles = 4; frames_to_apex = 12 }
    )
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\levels\level_1\level_segment_frame_data.json') -Encoding UTF8

# level_2 frame data (boss role with 2+ jump_arcs)
@{
    schema_version = "1.0.0"
    project = @{ name = "plat_contracts_fixture" }
    level_id = "level_2"
    level_role = "boss"
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    time_unit = "frames"
    layout = @{
        width_tiles = 180
        height_tiles = 18
        tile_size_px = 16
        gravity_zone_count = 1
        ceiling_y_px = 32
        floor_y_px = 224
    }
    parallax_layers = @(
        @{ layer_id = "bg_far"; parallax_factor = 0.2; tile_count = 32; animation_idle_frames = 60 },
        @{ layer_id = "bg_mid"; parallax_factor = 0.5; tile_count = 48; animation_idle_frames = 30 }
    )
    hazard_zones = @(
        @{ hazard_id = "saw"; x_start_tile = 60; x_end_tile = 64; y_tile = 15; frames_active = 8; frames_idle = 16 }
    )
    jump_arcs = @(
        @{ arc_id = "telegraph_jump"; max_height_tiles = 3; horizontal_distance_tiles = 3; frames_to_apex = 8 },
        @{ arc_id = "escape_jump"; max_height_tiles = 6; horizontal_distance_tiles = 5; frames_to_apex = 14 }
    )
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\levels\level_2\level_segment_frame_data.json') -Encoding UTF8

Set-Content -LiteralPath (Join-Path $fixtureRoot 'out\balance\clear_time_log.md') -Value '# Clear time log' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $fixtureRoot 'out\balance\difficulty_curve.json') -Value '{}' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\changelog\changelog.md') -Value '# CI fixture' -Encoding UTF8

& powershell -NoProfile -ExecutionPolicy Bypass -File $validator -ProjectRoot $fixtureRoot | Out-Null
$validatorExit = $LASTEXITCODE
Assert-True 'validator passes on fixture (vertical_slice phase)' ($validatorExit -eq 0) ("exit=$validatorExit")

$reportPath = Join-Path $fixtureRoot 'out\logs\platformer_specialization_report.json'
Assert-True 'report file emitted' (Test-Path -LiteralPath $reportPath) $reportPath
if (Test-Path -LiteralPath $reportPath) {
    $report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-True 'report.status is ok' ([string]$report.status -eq 'ok') ([string]$report.status)
    Assert-True 'report.manifest_status is present' ([string]$report.manifest_status -eq 'present') ([string]$report.manifest_status)
    Assert-True 'report.design_contract_status is present' ([string]$report.design_contract_status -eq 'present') ([string]$report.design_contract_status)
    Assert-True 'report.level_audits has 5 entries' ($report.level_audits.Count -eq 5) ("$($report.level_audits.Count) audits")
    Assert-True 'report has 3 blockers' ($report.blockers.Count -eq 3) ("$($report.blockers.Count) blockers")
    $firedBlockers = @($report.blockers | Where-Object { $_.fired -eq $true })
    Assert-True 'vertical_slice does not fire any blocker' ($firedBlockers.Count -eq 0) ("$($firedBlockers.Count) fired")
}

# Negative case: coyote_time_frames=12 > 6 -> ready_for_aaa
$brokenRoot = Join-Path $workspaceRoot 'out\ci\platformer_specialization_contracts_broken_fixture'
if (Test-Path -LiteralPath $brokenRoot) { Remove-Item -LiteralPath $brokenRoot -Recurse -Force }
New-Item -ItemType Directory -Force -Path (Join-Path $brokenRoot 'doc\levels\level_1') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $brokenRoot 'doc\levels\level_2') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $brokenRoot 'doc\changelog') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $brokenRoot 'out\logs') | Out-Null
Copy-Item -LiteralPath (Join-Path $fixtureRoot 'doc\genre_specialization_manifest.json') -Destination (Join-Path $brokenRoot 'doc\genre_specialization_manifest.json') -Force
Copy-Item -LiteralPath (Join-Path $fixtureRoot 'doc\levels\level_1\level_segment_frame_data.json') -Destination (Join-Path $brokenRoot 'doc\levels\level_1\level_segment_frame_data.json') -Force
Copy-Item -LiteralPath (Join-Path $fixtureRoot 'doc\levels\level_2\level_segment_frame_data.json') -Destination (Join-Path $brokenRoot 'doc\levels\level_2\level_segment_frame_data.json') -Force
$brokenContract = Get-Content -LiteralPath (Join-Path $fixtureRoot 'doc\platformer_precision_2d_design_contract.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$brokenContract.player_profile.coyote_time_frames = 12
$brokenContract.player_profile.jump_buffer_frames = 10
# Add 3 more levels to satisfy minItems=5
$brokenContract.level_catalog += @{ level_id = "level_3"; display_name = "Sky High"; length_tiles = 220; hazards_count = 4; collectibles_count = 5; level_segment_frame_data_path = "doc/levels/level_1/level_segment_frame_data.json"; par_time_seconds = 55 }
$brokenContract.level_catalog += @{ level_id = "level_4"; display_name = "Lava Cave"; length_tiles = 240; hazards_count = 9; collectibles_count = 7; level_segment_frame_data_path = "doc/levels/level_1/level_segment_frame_data.json"; par_time_seconds = 60 }
$brokenContract.level_catalog += @{ level_id = "level_5"; display_name = "Robotnik Boss"; length_tiles = 160; hazards_count = 3; collectibles_count = 4; level_segment_frame_data_path = "doc/levels/level_1/level_segment_frame_data.json"; par_time_seconds = 40 }
@{
    schema_version = "1.0.0"
    project_root_policy = "all_project_material_inside_project"
    claim_ceiling = "ready_for_aaa"
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $brokenRoot 'doc\project_methodology_manifest.json') -Encoding UTF8
$brokenContract | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $brokenRoot 'doc\platformer_precision_2d_design_contract.json') -Encoding UTF8
& powershell -NoProfile -ExecutionPolicy Bypass -File $validator -ProjectRoot $brokenRoot | Out-Null
$brokenExit = $LASTEXITCODE
$brokenReportPath = Join-Path $brokenRoot 'out\logs\platformer_specialization_report.json'
Assert-True 'validator fails on broken coyote_time (ready_for_aaa phase)' ($brokenExit -ne 0) ("exit=$brokenExit")
if (Test-Path -LiteralPath $brokenReportPath) {
    $brokenReport = Get-Content -LiteralPath $brokenReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $firedBlk = @($brokenReport.blockers | Where-Object { $_.fired -eq $true })
    $coyoteFired = @($firedBlk | Where-Object { $_.blocker_id -eq 'platformer_coyote_time_overflow' })
    Assert-True 'platformer_coyote_time_overflow fires' ($coyoteFired.Count -eq 1) ('not fired')
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
