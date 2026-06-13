<#
.SYNOPSIS
    Verifies all 4 racing_arcade schemas are well-formed JSON Schema Draft-07
    and a minimal fixture passes validation.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$schemasDir = Join-Path $wrapperRoot 'schemas'
$validator = Join-Path $wrapperRoot 'validate_racing_arcade_specialization.ps1'
$fixtureRoot = Join-Path $workspaceRoot 'out\ci\racing_specialization_contracts_fixture'

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
Write-Host '=== Racing Specialization Contracts Test ==='
Write-Host ''

$schemas = @(
    'racing_arcade_design_contract.schema.json',
    'racing_vehicle_frame_data.schema.json',
    'racing_specialization_report.schema.json',
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

Assert-True 'validate_racing_arcade_specialization.ps1 exists' (Test-Path -LiteralPath $validator) $validator

# Build minimal fixture
if (Test-Path -LiteralPath $fixtureRoot) { Remove-Item -LiteralPath $fixtureRoot -Recurse -Force }
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'doc\vehicles\karts_light') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'doc\vehicles\cars_medium') | Out-Null
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
    project = @{ name = "racing_contracts_fixture"; project_root_policy = "all_project_material_inside_project" }
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    active_specializations = @(
        @{
            specialization_id = "racing_arcade"
            activation_reason = "fixture for contract validation"
            design_contract_path = "doc/racing_arcade_design_contract.json"
            evidence = @{ gdd_section_ref = "doc/11-gdd.md#racing" }
            doc_refs = @("doc/11-gdd.md", "doc/10-memory-bank.md", "doc/changelog/changelog.md")
            freeze_axes_acknowledgement = $true
        }
    )
    human_authorization = @{
        authorized_at = "2026-06-05T00:00:00Z"
        author_role = "framework_tester"
    }
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\genre_specialization_manifest.json') -Encoding UTF8

# Design contract: 4 vehicles, 4 tracks, 2 modes, 3 items, AI profile
@{
    schema_version = "1.0.0"
    project = @{ name = "racing_contracts_fixture" }
    specialization_id = "racing_arcade"
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    time_unit = "frames"
    camera = "behind_or_chase"
    track_count_max = 16
    lap_count_max = 5
    ai_opponents = "5_to_7"
    boost_on_drift = "on"
    collision_model = "arcade_forgiving"
    vehicle_catalog = @(
        @{ id = "kart_light"; display_name = "Light Kart"; weight_class = "light"; vehicle_frame_data_path = "doc/vehicles/karts_light/vehicle_frame_data.json"; starting_position = 1; lore_id = "kart_light_lore"; head_metric = "S" },
        @{ id = "car_medium"; display_name = "Sport Car"; weight_class = "medium"; vehicle_frame_data_path = "doc/vehicles/cars_medium/vehicle_frame_data.json"; starting_position = 2; lore_id = "car_medium_lore"; head_metric = "M" },
        @{ id = "truck_heavy"; display_name = "Heavy Truck"; weight_class = "heavy"; vehicle_frame_data_path = "doc/vehicles/cars_medium/vehicle_frame_data.json"; starting_position = 3; lore_id = "truck_heavy_lore"; head_metric = "L" },
        @{ id = "formula_x"; display_name = "Formula X"; weight_class = "formula"; vehicle_frame_data_path = "doc/vehicles/karts_light/vehicle_frame_data.json"; starting_position = 4; lore_id = "formula_x_lore"; head_metric = "M" }
    )
    track_catalog = @(
        @{ track_id = "monaco"; display_name = "Monaco GP"; length_pixels = 32000; lane_count = 2; shortcut_count = 1; weather_policy = "clear"; recommended_lap_count = 3; par_lap_time_frames = 7200; track_music_loop_seconds = 60 },
        @{ track_id = "rainforest"; display_name = "Rainforest"; length_pixels = 28000; lane_count = 3; shortcut_count = 0; weather_policy = "rain"; recommended_lap_count = 4; par_lap_time_frames = 9000; track_music_loop_seconds = 75 },
        @{ track_id = "desert"; display_name = "Desert Run"; length_pixels = 40000; lane_count = 2; shortcut_count = 2; weather_policy = "clear"; recommended_lap_count = 3; par_lap_time_frames = 8000; track_music_loop_seconds = 80 },
        @{ track_id = "night_city"; display_name = "Night City"; length_pixels = 30000; lane_count = 2; shortcut_count = 1; weather_policy = "night"; recommended_lap_count = 5; par_lap_time_frames = 10000; track_music_loop_seconds = 90 }
    )
    race_modes = @(
        @{ id = "grand_prix"; kind = "grand_prix"; laps = 3; ai_count = 6; item_box_enabled = $true; rubber_banding_enabled = $true },
        @{ id = "time_trial"; kind = "time_trial"; laps = 3; ai_count = 0; item_box_enabled = $false; rubber_banding_enabled = $false }
    )
    item_catalog = @(
        @{ id = "rocket"; display_name = "Rocket"; category = "rocket"; duration_frames = 60; stack_max = 1; value = 1 },
        @{ id = "shield"; display_name = "Shield"; category = "shield"; duration_frames = 600; stack_max = 2; value = 1 },
        @{ id = "boost"; display_name = "Boost"; category = "boost"; duration_frames = 60; stack_max = 3; value = 1 }
    )
    ai_profile = @{
        difficulty_levels = @("easy", "normal", "hard")
        drafting_enabled = $true
        rubber_banding_enabled = $true
        rubber_band_strength_pct = 20
        ai_top_speed_variance_pct = 10
    }
    hud_config = @{
        show_position = $true
        show_lap_counter = $true
        show_lap_time = $true
        show_minimap = $true
        show_speed_kmh = $true
        show_boost_meter = $true
        show_item_slot = $true
    }
    balance = @{
        method = "top_speed_first"
        evidence_paths = @("out/balance/lap_time_log.md")
        difficulty_curve_path = "out/balance/difficulty_curve.json"
    }
    doc_refs = @("doc/11-gdd.md", "doc/10-memory-bank.md", "doc/changelog/changelog.md")
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\racing_arcade_design_contract.json') -Encoding UTF8

# Light vehicle frame data
@{
    schema_version = "1.0.0"
    project = @{ name = "racing_contracts_fixture" }
    vehicle_id = "kart_light"
    weight_class = "light"
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    time_unit = "frames"
    stats = @{
        top_speed_kmh = 180
        acceleration_frames_to_top = 120
        handling_rad_per_sec = "1.8"
        drift_factor = 60
        boost_consumption_pct_per_sec = 30
        weight_kg = 600
        tire_grip_pct = 70
        downforce_pct = 30
    }
    animation = @{
        animation_idle_frames = 6
        animation_drift_frames = 12
        animation_boost_frames = 8
        animation_crash_frames = 24
        voxel_size = "24x24"
        head_metric = "S"
    }
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\vehicles\karts_light\vehicle_frame_data.json') -Encoding UTF8

# Medium vehicle frame data
@{
    schema_version = "1.0.0"
    project = @{ name = "racing_contracts_fixture" }
    vehicle_id = "car_medium"
    weight_class = "medium"
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    time_unit = "frames"
    stats = @{
        top_speed_kmh = 220
        acceleration_frames_to_top = 180
        handling_rad_per_sec = "1.2"
        drift_factor = 40
        boost_consumption_pct_per_sec = 25
        weight_kg = 1200
        tire_grip_pct = 80
        downforce_pct = 50
    }
    animation = @{
        animation_idle_frames = 6
        animation_drift_frames = 12
        animation_boost_frames = 8
        animation_crash_frames = 24
        voxel_size = "32x32"
        head_metric = "M"
    }
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\vehicles\cars_medium\vehicle_frame_data.json') -Encoding UTF8

Set-Content -LiteralPath (Join-Path $fixtureRoot 'out\balance\lap_time_log.md') -Value '# Lap time log' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $fixtureRoot 'out\balance\difficulty_curve.json') -Value '{}' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\changelog\changelog.md') -Value '# CI fixture' -Encoding UTF8

& powershell -NoProfile -ExecutionPolicy Bypass -File $validator -ProjectRoot $fixtureRoot | Out-Null
$validatorExit = $LASTEXITCODE
Assert-True 'validator passes on fixture (vertical_slice phase)' ($validatorExit -eq 0) ("exit=$validatorExit")

$reportPath = Join-Path $fixtureRoot 'out\logs\racing_specialization_report.json'
Assert-True 'report file emitted' (Test-Path -LiteralPath $reportPath) $reportPath
if (Test-Path -LiteralPath $reportPath) {
    $report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-True 'report.status is ok' ([string]$report.status -eq 'ok') ([string]$report.status)
    Assert-True 'report.manifest_status is present' ([string]$report.manifest_status -eq 'present') ([string]$report.manifest_status)
    Assert-True 'report.design_contract_status is present' ([string]$report.design_contract_status -eq 'present') ([string]$report.design_contract_status)
    Assert-True 'report.vehicle_audits has 4 entries' ($report.vehicle_audits.Count -eq 4) ("$($report.vehicle_audits.Count) audits")
    Assert-True 'report has 3 blockers' ($report.blockers.Count -eq 3) ("$($report.blockers.Count) blockers")
    $firedBlockers = @($report.blockers | Where-Object { $_.fired -eq $true })
    Assert-True 'vertical_slice does not fire any blocker' ($firedBlockers.Count -eq 0) ("$($firedBlockers.Count) fired")
}

# Negative case: collision_model=realistic_full + 30 tracks -> ready_for_aaa
$brokenRoot = Join-Path $workspaceRoot 'out\ci\racing_specialization_contracts_broken_fixture'
if (Test-Path -LiteralPath $brokenRoot) { Remove-Item -LiteralPath $brokenRoot -Recurse -Force }
New-Item -ItemType Directory -Force -Path (Join-Path $brokenRoot 'doc\vehicles\karts_light') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $brokenRoot 'doc\vehicles\cars_medium') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $brokenRoot 'doc\changelog') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $brokenRoot 'out\logs') | Out-Null
Copy-Item -LiteralPath (Join-Path $fixtureRoot 'doc\genre_specialization_manifest.json') -Destination (Join-Path $brokenRoot 'doc\genre_specialization_manifest.json') -Force
Copy-Item -LiteralPath (Join-Path $fixtureRoot 'doc\vehicles\karts_light\vehicle_frame_data.json') -Destination (Join-Path $brokenRoot 'doc\vehicles\karts_light\vehicle_frame_data.json') -Force
Copy-Item -LiteralPath (Join-Path $fixtureRoot 'doc\vehicles\cars_medium\vehicle_frame_data.json') -Destination (Join-Path $brokenRoot 'doc\vehicles\cars_medium\vehicle_frame_data.json') -Force
$brokenContract = Get-Content -LiteralPath (Join-Path $fixtureRoot 'doc\racing_arcade_design_contract.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$brokenContract.collision_model = "realistic_full"
@{
    schema_version = "1.0.0"
    project_root_policy = "all_project_material_inside_project"
    claim_ceiling = "ready_for_aaa"
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $brokenRoot 'doc\project_methodology_manifest.json') -Encoding UTF8
$brokenContract | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $brokenRoot 'doc\racing_arcade_design_contract.json') -Encoding UTF8
& powershell -NoProfile -ExecutionPolicy Bypass -File $validator -ProjectRoot $brokenRoot | Out-Null
$brokenExit = $LASTEXITCODE
$brokenReportPath = Join-Path $brokenRoot 'out\logs\racing_specialization_report.json'
Assert-True 'validator fails on broken collision_model (ready_for_aaa phase)' ($brokenExit -ne 0) ("exit=$brokenExit")
if (Test-Path -LiteralPath $brokenReportPath) {
    $brokenReport = Get-Content -LiteralPath $brokenReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $firedBlk = @($brokenReport.blockers | Where-Object { $_.fired -eq $true })
    $colFired = @($firedBlk | Where-Object { $_.blocker_id -eq 'racing_collision_model_audit' })
    Assert-True 'racing_collision_model_audit fires' ($colFired.Count -eq 1) ('not fired')
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
