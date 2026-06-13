<#
.SYNOPSIS
    Verifies all 5 fighting specialization schemas are well-formed JSON
    Schema Draft-07 and that a minimal manifest + design contract + moveset
    fixture pass schema-lite validation through validate_fighting_specialization.ps1.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$schemasDir = Join-Path $wrapperRoot 'schemas'
$validator = Join-Path $wrapperRoot 'validate_fighting_specialization.ps1'
$fixtureRoot = Join-Path $workspaceRoot 'out\ci\fighting_specialization_contracts_fixture'

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
Write-Host '=== Fighting Specialization Contracts Test ==='
Write-Host ''

# 1. All 5 schemas parse
$schemas = @(
    'genre_specialization_registry.schema.json',
    'genre_specialization_manifest.schema.json',
    'fighting_2d_design_contract.schema.json',
    'fighting_moveset_frame_data.schema.json',
    'fighting_specialization_report.schema.json'
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
Assert-True 'validate_fighting_specialization.ps1 exists' (Test-Path -LiteralPath $validator) $validator

# 3. Build minimal fixture: project opt-in, design contract, moveset
if (Test-Path -LiteralPath $fixtureRoot) {
    Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'doc\characters\ryu') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'doc\characters\ken') | Out-Null
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
    project = @{ name = "figh_contracts_fixture"; project_root_policy = "all_project_material_inside_project" }
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    active_specializations = @(
        @{
            specialization_id = "fighting_2d_traditional"
            activation_reason = "fixture for contract validation"
            design_contract_path = "doc/fighting_2d_design_contract.json"
            evidence = @{ gdd_section_ref = "doc/11-gdd.md#fighting" }
            doc_refs = @("doc/11-gdd.md", "doc/10-memory-bank.md", "doc/changelog/changelog.md")
            freeze_axes_acknowledgement = $true
        }
    )
    human_authorization = @{
        authorized_at = "2026-06-05T00:00:00Z"
        author_role = "framework_tester"
    }
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\genre_specialization_manifest.json') -Encoding UTF8

# design contract: 1 primary (ryu), 1 secondary (ken), training mode, balance evidence path
@{
    schema_version = "1.0.0"
    project = @{ name = "figh_contracts_fixture" }
    specialization_id = "fighting_2d_traditional"
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    time_unit = "frames"
    head_metric_policy = "advisory"
    archetype_policy = "design_tool_not_law"
    balance_evidence_required = $true
    rollback_netcode = "not_applicable"
    roster = @{
        size = 2
        characters = @(
            @{
                id = "ryu"
                display_name = "Ryu"
                role = "primary"
                archetype = "shoto"
                moveset_frame_data_path = "doc/characters/ryu/moveset_frame_data.json"
                lore_id = "ryu_lore"
                head_metric = "M"
            },
            @{
                id = "ken"
                display_name = "Ken"
                role = "secondary"
                archetype = "rushdown"
                moveset_frame_data_path = "doc/characters/ken/moveset_frame_data.json"
                lore_id = "ken_lore"
                head_metric = "M"
            }
        )
    }
    lore = @{
        characters = @(
            @{ id = "ryu_lore"; summary = "wandering fighter"; ip_status = "original" },
            @{ id = "ken_lore"; summary = "rival and friend"; ip_status = "original" }
        )
    }
    modes = @(
        @{ id = "versus"; kind = "versus"; human_or_cpu_opponent = "human_vs_human"; round_config = @{ round_time_limit_frames = 5940; rounds_to_win = 2; max_rounds = 3 } },
        @{ id = "training"; kind = "training"; human_or_cpu_opponent = "human_vs_cpu"; round_config = @{ round_time_limit_frames = 5940; rounds_to_win = 1; max_rounds = 1 }; training_features = @("input_display", "frame_advantage_display") }
    )
    stages = @(
        @{ id = "dojo"; display_name = "Dojo"; camera_bounds_px = @{ left = 0; right = 320; top = 0; bottom = 224 }; floor_y_px = 180; hazard_policy = "no_hazards" }
    )
    balance = @{
        method = "frame_data_first"
        evidence_paths = @("out/balance/playtest_log.md")
    }
    doc_refs = @("doc/11-gdd.md", "doc/10-memory-bank.md", "doc/changelog/changelog.md")
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\fighting_2d_design_contract.json') -Encoding UTF8

# ryu moveset (primary, full frame data)
@{
    schema_version = "1.0.0"
    project = @{ name = "figh_contracts_fixture" }
    character_id = "ryu"
    character_role = "primary"
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    time_unit = "frames"
    moves = @(
        @{
            move_id = "hadouken"
            display_name = "Hadouken"
            input_motion = "236P"
            category = "special"
            startup_frames = 11
            active_frames = 8
            recovery_frames = 38
            on_hit_advantage_frames = 3
            on_block_advantage_frames = -4
        },
        @{
            move_id = "shoryuken"
            display_name = "Shoryuken"
            input_motion = "623P"
            category = "special"
            startup_frames = 4
            active_frames = 14
            recovery_frames = 32
            on_hit_advantage_frames = 2
            on_block_advantage_frames = -8
        },
        @{
            move_id = "walk"
            display_name = "Walk"
            input_motion = "5 -> 4/6"
            category = "movement"
        }
    )
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\characters\ryu\moveset_frame_data.json') -Encoding UTF8

# ken moveset (secondary, partial frame data)
@{
    schema_version = "1.0.0"
    project = @{ name = "figh_contracts_fixture" }
    character_id = "ken"
    character_role = "secondary"
    registry_source = "doc/07_game_design/genre_specialization_registry.json"
    time_unit = "frames"
    moves = @(
        @{
            move_id = "walk"
            display_name = "Walk"
            input_motion = "5 -> 4/6"
            category = "movement"
        }
    )
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\characters\ken\moveset_frame_data.json') -Encoding UTF8

# balance evidence file
Set-Content -LiteralPath (Join-Path $fixtureRoot 'out\balance\playtest_log.md') -Value '# Playtest log' -Encoding UTF8

# changelog
Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\changelog\changelog.md') -Value '# CI fixture' -Encoding UTF8

# 4. Run validator against fixture
& powershell -NoProfile -ExecutionPolicy Bypass -File $validator -ProjectRoot $fixtureRoot | Out-Null
$validatorExit = $LASTEXITCODE
Assert-True 'validator passes on fixture (vertical_slice phase)' ($validatorExit -eq 0) ("exit=$validatorExit")

# 5. Read report and verify status
$reportPath = Join-Path $fixtureRoot 'out\logs\fighting_specialization_report.json'
Assert-True 'report file emitted' (Test-Path -LiteralPath $reportPath) $reportPath
if (Test-Path -LiteralPath $reportPath) {
    $report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-True 'report.status is ok' ([string]$report.status -eq 'ok') ([string]$report.status)
    Assert-True 'report.manifest_status is present' ([string]$report.manifest_status -eq 'present') ([string]$report.manifest_status)
    Assert-True 'report.design_contract_status is present' ([string]$report.design_contract_status -eq 'present') ([string]$report.design_contract_status)
    Assert-True 'report.moveset_audits has 2 entries' ($report.moveset_audits.Count -eq 2) ("$($report.moveset_audits.Count) audits")
    Assert-True 'report has 3 blockers' ($report.blockers.Count -eq 3) ("$($report.blockers.Count) blockers")
    $firedBlockers = @($report.blockers | Where-Object { $_.fired -eq $true })
    Assert-True 'vertical_slice does not fire any blocker' ($firedBlockers.Count -eq 0) ("$($firedBlockers.Count) fired")
}

# 6. Negative case: missing balance evidence file -> validator warns/fails the design contract status
$brokenRoot = Join-Path $workspaceRoot 'out\ci\fighting_specialization_contracts_broken_fixture'
if (Test-Path -LiteralPath $brokenRoot) {
    Remove-Item -LiteralPath $brokenRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $brokenRoot 'doc') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $brokenRoot 'out\logs') | Out-Null
Copy-Item -LiteralPath (Join-Path $fixtureRoot 'doc\genre_specialization_manifest.json') -Destination (Join-Path $brokenRoot 'doc\genre_specialization_manifest.json') -Force
# Design contract with evidence_paths pointing to missing file
$brokenContract = Get-Content -LiteralPath (Join-Path $fixtureRoot 'doc\fighting_2d_design_contract.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$brokenContract.balance.evidence_paths = @("out/balance/does_not_exist.md")
# Bump methodology ceiling to ready_for_aaa so the balance_evidence_missing blocker can fire
@{
    schema_version = "1.0.0"
    project_root_policy = "all_project_material_inside_project"
    claim_ceiling = "ready_for_aaa"
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $brokenRoot 'doc\project_methodology_manifest.json') -Encoding UTF8
$brokenContract | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $brokenRoot 'doc\fighting_2d_design_contract.json') -Encoding UTF8
& powershell -NoProfile -ExecutionPolicy Bypass -File $validator -ProjectRoot $brokenRoot | Out-Null
$brokenExit = $LASTEXITCODE
$brokenReportPath = Join-Path $brokenRoot 'out\logs\fighting_specialization_report.json'
Assert-True 'validator fails on broken balance evidence (ready_for_aaa phase)' ($brokenExit -ne 0) ("exit=$brokenExit")
if (Test-Path -LiteralPath $brokenReportPath) {
    $brokenReport = Get-Content -LiteralPath $brokenReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $firedBlk = @($brokenReport.blockers | Where-Object { $_.fired -eq $true })
    $balanceFired = @($firedBlk | Where-Object { $_.blocker_id -eq 'fighting_balance_evidence_missing' })
    Assert-True 'fighting_balance_evidence_missing fires' ($balanceFired.Count -eq 1) ('not fired')
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
