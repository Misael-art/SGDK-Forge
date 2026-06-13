<#
.SYNOPSIS
    Regression suite for structured project methodology governance.

.DESCRIPTION
    Protects against:
    - broad text-regex false positives
    - perceptual evidence bypasses
    - empty road/boss contracts
    - missing methodology adoption in old projects
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$validator = Join-Path $wrapperRoot 'validate_project_methodology.ps1'
$adopter = Join-Path $wrapperRoot 'adopt_project_methodology.ps1'
$fixtureRoot = Join-Path $workspaceRoot 'out\ci\project_methodology_governance_fixture'
$reportPath = Join-Path $fixtureRoot 'out\logs\project_methodology_report.json'

$script:passed = 0
$script:failed = 0
$script:total = 0

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

function Write-JsonFile {
    param([string]$Path, $Value)
    $parent = Split-Path $Path -Parent
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    [System.IO.File]::WriteAllText(
        $Path,
        ($Value | ConvertTo-Json -Depth 20),
        [System.Text.Encoding]::UTF8
    )
}

function Reset-Fixture {
    if (Test-Path -LiteralPath $fixtureRoot) {
        Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'doc\contracts') | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'out\logs') | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'out\evidence\blastem') | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'out\evidence\motion') | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'src\scenes') | Out-Null
}

function New-Claim {
    param(
        [string]$Applicability = 'not_applicable',
        [string]$Rationale = 'Not used by this fixture.'
    )
    return [ordered]@{
        applicability = $Applicability
        rationale = $Rationale
    }
}

function New-MethodologyManifest {
    param(
        [string]$Lifecycle = 'existing',
        [string]$ProjectName = '',
        $CriticalMotion = $null,
        $RoadPhysics = $null,
        $ModularBoss = $null,
        [string[]]$RequiredSkills = @(
            'governance/truth-hierarchy-guard',
            'governance/doc-sync-audit',
            'operation/sgdk-build-wrapper-operator'
        ),
        [string[]]$RequiredValidations = @(
            'preflight_host',
            'validate_resources',
            'scene_closeout_gate',
            'freshness_audit',
            'project_hygiene',
            'project_context'
        )
    )

    if ($null -eq $CriticalMotion) { $CriticalMotion = New-Claim }
    if ($null -eq $RoadPhysics) { $RoadPhysics = New-Claim }
    if ($null -eq $ModularBoss) { $ModularBoss = New-Claim }
    if ([string]::IsNullOrWhiteSpace($ProjectName)) { $ProjectName = Split-Path $fixtureRoot -Leaf }

    return [ordered]@{
        schema_version = '1.0.0'
        methodology_version = '2026.06.04'
        project = [ordered]@{
            name = $ProjectName
            lifecycle = $Lifecycle
            project_root_policy = 'all_project_material_inside_project'
        }
        active_workflow = 'production-loop'
        required_skills = $RequiredSkills
        required_validations = $RequiredValidations
        claims = [ordered]@{
            critical_motion = $CriticalMotion
            road_physics = $RoadPhysics
            modular_boss = $ModularBoss
        }
    }
}

function Invoke-MethodologyValidator {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $validator `
        -ProjectRoot $fixtureRoot `
        -WorkspaceRoot $workspaceRoot `
        -OutputPath $reportPath | Out-Null
    $exitCode = $LASTEXITCODE
    $report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    return [pscustomobject]@{
        exit_code = $exitCode
        report = $report
        statuses = @($report.blocking_statuses)
    }
}

function Has-Status {
    param($Run, [string]$Status)
    return @($Run.statuses) -contains $Status
}

Write-Host ''
Write-Host '=== Project Methodology Governance Test ==='
Write-Host ''

try {
    Reset-Fixture
    $run = Invoke-MethodologyValidator
    Assert-True 'old project without methodology manifest is blocked' (Has-Status $run 'project_methodology_manifest_missing')

    Write-JsonFile (Join-Path $fixtureRoot '.mddev\project.json') @{
        name = '__PROJECT_NAME__'
        display_name = '__PROJECT_NAME__'
        kind = 'lab'
    }
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $adopter -ProjectRoot $fixtureRoot -Lifecycle existing | Out-Null
    $adoptedPath = Join-Path $fixtureRoot 'doc\project_methodology_manifest.json'
    $adopted = Get-Content -LiteralPath $adoptedPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-True 'adopter materializes missing methodology inside project' (Test-Path -LiteralPath $adoptedPath -PathType Leaf)
    Assert-True 'adopter replaces template project-name placeholder with folder name' ([string]$adopted.project.name -eq (Split-Path $fixtureRoot -Leaf))
    Assert-True 'adopter keeps old project claims review_required' ([string]$adopted.claims.critical_motion.applicability -eq 'review_required')
    $beforeHash = (Get-FileHash -LiteralPath $adoptedPath -Algorithm SHA256).Hash
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $adopter -ProjectRoot $fixtureRoot -Lifecycle new | Out-Null
    $afterHash = (Get-FileHash -LiteralPath $adoptedPath -Algorithm SHA256).Hash
    Assert-True 'adopter never overwrites existing methodology' ($beforeHash -eq $afterHash)

    Reset-Fixture
    Write-JsonFile (Join-Path $fixtureRoot 'doc\project_methodology_manifest.json') (New-MethodologyManifest -Lifecycle 'unclassified')
    $run = Invoke-MethodologyValidator
    Assert-True 'unclassified methodology is invalid' (Has-Status $run 'project_methodology_manifest_invalid')

    Reset-Fixture
    Write-JsonFile (Join-Path $fixtureRoot 'doc\project_methodology_manifest.json') (New-MethodologyManifest -ProjectName '__PROJECT_NAME__')
    $run = Invoke-MethodologyValidator
    Assert-True 'template project-name placeholder is blocked' (Has-Status $run 'project_naming_invalid')

    Reset-Fixture
    Write-JsonFile (Join-Path $fixtureRoot 'doc\project_methodology_manifest.json') (
        New-MethodologyManifest -Lifecycle 'new'
    )
    $run = Invoke-MethodologyValidator
    Assert-True 'new project without canonical directory naming is blocked' (Has-Status $run 'project_naming_invalid')

    Reset-Fixture
    Write-JsonFile (Join-Path $fixtureRoot 'doc\project_methodology_manifest.json') (
        New-MethodologyManifest -RequiredValidations @('preflight_host', 'validate_resources', 'scene_closeout_gate', 'project_hygiene', 'project_context')
    )
    $run = Invoke-MethodologyValidator
    Assert-True 'freshness audit is mandatory for documentation synchronization' (Has-Status $run 'project_methodology_manifest_invalid')

    Reset-Fixture
    Set-Content -LiteralPath (Join-Path $fixtureRoot 'src\scenes\scene_false_positive.c') -Value 'void chase(void) { void *sBossBody = 0; }' -Encoding UTF8
    Write-JsonFile (Join-Path $fixtureRoot 'doc\project_methodology_manifest.json') (New-MethodologyManifest)
    $run = Invoke-MethodologyValidator
    Assert-True 'generic chase and sBossBody text do not create claims' ($run.statuses.Count -eq 0) ($run.statuses -join ',')

    Reset-Fixture
    $critical = New-Claim -Applicability 'required' -Rationale 'Critical boss animation is part of delivery.'
    $critical['critical_asset_ids'] = @('boss_main')
    $critical['motion_gif_path'] = 'out/evidence/motion/boss_main.gif'
    $critical['human_approval_record_path'] = 'doc/human_approval_record.md'
    $skills = @(
        'governance/truth-hierarchy-guard',
        'governance/doc-sync-audit',
        'operation/sgdk-build-wrapper-operator',
        'art/visual-excellence-standards',
        'code/sgdk-runtime-coder'
    )
    Write-JsonFile (Join-Path $fixtureRoot 'doc\project_methodology_manifest.json') (New-MethodologyManifest -CriticalMotion $critical -RequiredSkills $skills)
    Write-JsonFile (Join-Path $fixtureRoot 'out\logs\runtime_metrics.json') @{
        perceptual_check = @{ fluidez = 1; leitura = 1; naturalidade = 1; impacto = 1 }
    }
    $vdpPath = Join-Path $fixtureRoot 'out\evidence\blastem\visual_vdp_dump.bin'
    [System.IO.File]::WriteAllBytes($vdpPath, [byte[]](1, 2, 3))
    Write-JsonFile (Join-Path $fixtureRoot 'out\logs\blastem_evidence.json') @{
        screenshot_present = $false
        screenshot_path = $null
        sram_present = $false
        sram_path = $null
        fresh_sram_confirmed = $false
        vdp_dump_present = $true
        vdp_dump_path = $vdpPath
    }
    $run = Invoke-MethodologyValidator
    Assert-True 'VDP dump alone cannot bypass perceptual gate' (Has-Status $run 'perceptual_motion_unvalidated')

    $screenshotPath = Join-Path $fixtureRoot 'out\evidence\blastem\screenshot.png'
    $sramPath = Join-Path $fixtureRoot 'out\evidence\blastem\save.sram'
    $motionPath = Join-Path $fixtureRoot 'out\evidence\motion\boss_main.gif'
    $approvalPath = Join-Path $fixtureRoot 'doc\human_approval_record.md'
    Set-Content -LiteralPath $screenshotPath -Value 'screenshot' -Encoding UTF8
    Set-Content -LiteralPath $sramPath -Value 'sram' -Encoding UTF8
    Set-Content -LiteralPath $motionPath -Value 'gif' -Encoding UTF8
    Set-Content -LiteralPath $approvalPath -Value '# Approved boss_main motion' -Encoding UTF8
    Write-JsonFile (Join-Path $fixtureRoot 'out\logs\blastem_evidence.json') @{
        screenshot_present = $true
        screenshot_path = $screenshotPath
        sram_present = $true
        sram_path = $sramPath
        fresh_sram_confirmed = $true
        vdp_dump_present = $true
        vdp_dump_path = $vdpPath
    }
    $run = Invoke-MethodologyValidator
    Assert-True 'complete perceptual evidence passes' (-not (Has-Status $run 'perceptual_motion_unvalidated')) ($run.statuses -join ',')

    Reset-Fixture
    $road = New-Claim -Applicability 'required' -Rationale 'Pseudo-3D road is a gameplay system.'
    $road['contract_path'] = 'doc/contracts/road_physics_contract.json'
    $roadSkills = @(
        'governance/truth-hierarchy-guard',
        'governance/doc-sync-audit',
        'operation/sgdk-build-wrapper-operator',
        'design/level-design-canonical',
        'code/sgdk-runtime-coder',
        'hardware/megadrive-vdp-budget-analyst'
    )
    Write-JsonFile (Join-Path $fixtureRoot 'doc\project_methodology_manifest.json') (New-MethodologyManifest -RoadPhysics $road -RequiredSkills $roadSkills)
    Write-JsonFile (Join-Path $fixtureRoot 'doc\contracts\road_physics_contract.json') @{}
    $run = Invoke-MethodologyValidator
    Assert-True 'empty road contract is rejected' (Has-Status $run 'road_physics_contract_invalid')

    Set-Content -LiteralPath (Join-Path $fixtureRoot 'src\scenes\scene_road.c') -Value 'void road_lane_update(void){} void road_curve_update(void){} void road_impact_handler(void){}' -Encoding UTF8
    Write-JsonFile (Join-Path $fixtureRoot 'doc\contracts\road_physics_contract.json') @{
        schema_version = '1.0.0'
        contract_id = 'road_main'
        scene_id = 'road_scene'
        lane_model = @{ lane_count = 3; lane_width_px = 64; player_lateral_model = 'discrete_lanes' }
        parallax_equation = 'offset = camera_x / depth'
        curvature = @{ model = 'hscroll_table'; maximum_offset_px = 24 }
        impact_frame = @{ source = 'boss_collision'; frame_index = 3 }
        screen_shake = @{ maximum_offset_px = 4; duration_frames = 8 }
        hscroll_budget = @{ rows_updated = 224; bytes_per_frame = 448; update_phase = 'vblank' }
        runtime_source_paths = @('src/scenes/scene_road.c')
        runtime_symbols = @{ lane_update = 'road_lane_update'; curvature_update = 'road_curve_update'; impact_handler = 'road_impact_handler' }
    }
    $run = Invoke-MethodologyValidator
    Assert-True 'implemented road contract passes' (-not (Has-Status $run 'road_physics_contract_invalid')) ($run.statuses -join ',')

    Reset-Fixture
    $boss = New-Claim -Applicability 'required' -Rationale 'Boss is explicitly modular.'
    $boss['contract_path'] = 'doc/contracts/boss_parts.json'
    $bossSkills = @(
        'governance/truth-hierarchy-guard',
        'governance/doc-sync-audit',
        'operation/sgdk-build-wrapper-operator',
        'code/forward-kinematics-rigging',
        'code/sgdk-runtime-coder',
        'hardware/megadrive-vdp-budget-analyst'
    )
    Write-JsonFile (Join-Path $fixtureRoot 'doc\project_methodology_manifest.json') (New-MethodologyManifest -ModularBoss $boss -RequiredSkills $bossSkills)
    Write-JsonFile (Join-Path $fixtureRoot 'doc\contracts\boss_parts.json') @{
        schema_version = '1.0.0'
        boss_id = 'boss_main'
        scene_id = 'boss_scene'
        parts = @(@{ part_id = 'body'; runtime_symbol = 'sBossBody'; parent_id = $null; pivot_x = 0; pivot_y = 0; scanline_sprite_cost = 1 })
        fk_chain = @()
        fk_update_symbol = 'boss_fk_update'
        runtime_source_paths = @('src/scenes/scene_boss.c')
        scanline_budget = @{ maximum_sprites_per_line = 16; measured_peak = 1 }
    }
    $run = Invoke-MethodologyValidator
    Assert-True 'single-part modular boss contract is rejected' (Has-Status $run 'modular_boss_runtime_invalid')

    Set-Content -LiteralPath (Join-Path $fixtureRoot 'src\scenes\scene_boss.c') -Value 'void *sBossBody; void *sBossWing; void boss_fk_update(void){}' -Encoding UTF8
    Write-JsonFile (Join-Path $fixtureRoot 'doc\contracts\boss_parts.json') @{
        schema_version = '1.0.0'
        boss_id = 'boss_main'
        scene_id = 'boss_scene'
        parts = @(
            @{ part_id = 'body'; runtime_symbol = 'sBossBody'; parent_id = $null; pivot_x = 0; pivot_y = 0; scanline_sprite_cost = 1 },
            @{ part_id = 'wing'; runtime_symbol = 'sBossWing'; parent_id = 'body'; pivot_x = 16; pivot_y = 4; scanline_sprite_cost = 1 }
        )
        fk_chain = @(@{ parent_part_id = 'body'; child_part_id = 'wing'; transform_rule = 'rotate_about_parent_pivot' })
        fk_update_symbol = 'boss_fk_update'
        runtime_source_paths = @('src/scenes/scene_boss.c')
        scanline_budget = @{ maximum_sprites_per_line = 16; measured_peak = 2 }
    }
    $run = Invoke-MethodologyValidator
    Assert-True 'implemented modular boss contract passes' (-not (Has-Status $run 'modular_boss_runtime_invalid')) ($run.statuses -join ',')
}
finally {
    if (Test-Path -LiteralPath $fixtureRoot) {
        Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
    }
}

Write-Host ''
Write-Host "=== Results: $($script:passed)/$($script:total) passed, $($script:failed) failed ==="
if ($script:failed -gt 0) { exit 1 }
exit 0
