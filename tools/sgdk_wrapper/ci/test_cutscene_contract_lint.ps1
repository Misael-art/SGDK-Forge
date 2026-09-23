<#
.SYNOPSIS
    Verifies production/AAA lint enforcement for cutscene contracts.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$lintScript = Join-Path $wrapperRoot 'lint_scene_contract.ps1'

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

function New-CutsceneProject {
    param(
        [Parameter(Mandatory)][string]$Root,
        [Parameter(Mandatory)][bool]$WithContract,
        [bool]$WithStoryboardContract = $true
    )

    $docDir = Join-Path $Root 'doc'
    $pipelineDir = Join-Path $docDir 'pipeline\cutscene'
    $outLogs = Join-Path $Root 'out\logs'
    New-Item -ItemType Directory -Force -Path $docDir | Out-Null
    New-Item -ItemType Directory -Force -Path $pipelineDir | Out-Null
    New-Item -ItemType Directory -Force -Path $outLogs | Out-Null

    if ($WithContract) {
        @(
            'intro_fsm.json',
            'intro_resource_plan.json',
            'intro_panel_layout.json',
            'intro_text_timing.json',
            'intro_palette_script.json',
            'intro_glyph_manifest.json',
            'intro_teardown_plan.json',
            'intro_evidence_plan.json'
        ) | ForEach-Object {
            '{}' | Set-Content -LiteralPath (Join-Path $pipelineDir $_) -Encoding UTF8
        }

        if ($WithStoryboardContract) {
            $storyboard = [ordered]@{
                schema_version = '1.0.0'
                contract_id = 'intro_cutscene_storyboard_v1'
                scene_id = 'intro_cutscene'
                scene_role = 'cutscene'
                status_ceiling = 'planning_only'
                ready_for_aaa = $false
                source_authority = [ordered]@{
                    roteiro_ref = 'doc/12-roteiro.md#intro'
                    spec_ref = 'doc/13-spec-cenas.md#intro_cutscene'
                    context_pack_manifest_ref = 'doc/context_pack_manifest.json'
                    reference_profile = @(
                        [ordered]@{ game = 'Phantasy Star IV'; inheritance = 'panel rhythm and portrait readability' },
                        [ordered]@{ game = 'Valis III'; inheritance = 'dramatic anime framing' },
                        [ordered]@{ game = 'Shinobi III'; inheritance = 'silhouette contrast discipline' }
                    )
                }
                cinematic_direction = [ordered]@{
                    intention = 'prove that the opening has directed time before runtime'
                    narrative_structure = 'hold, reveal, text beat'
                    cinematic_language_methods = @('pan_scroll', 'hold_frame')
                    selected_fake_cinema_tools = @('pan_scroll', 'hold_frame')
                    signature_moment = 'castle reveal before title'
                }
                state_machine = [ordered]@{
                    runtime_model = 'table_driven_fsm'
                    states = @(
                        [ordered]@{
                            state_id = 'intro_hold'
                            narrative_purpose = 'establish mood'
                            shot_type = 'panel_hold'
                            entry_load = [ordered]@{ assets = @('intro_panel'); palettes = @('PAL0') }
                            render_surfaces = [ordered]@{ BG_B = 'intro_backdrop'; BG_A = 'intro_panel'; WINDOW = 'none'; sprites = @() }
                            palette_domains = @([ordered]@{ slot = 'PAL0'; owner = 'cutscene_panel' })
                            text_block = [ordered]@{ mode = 'none' }
                            advance_trigger = 'WAIT_FRAMES'
                            duration_frames = 90
                            dynamic_fx = @()
                            motion_beats = @([ordered]@{ beat_type = 'hold'; start_frame = 0; duration_frames = 90; purpose = 'intentional stillness' })
                            animation_link = [ordered]@{ mode = 'none' }
                            audio_cue = [ordered]@{ cue_id = 'none'; trigger_frame = 0 }
                            exit_teardown = 'clear_panel'
                        }
                    )
                }
                cutscene_resource_plan = [ordered]@{
                    states = @(
                        [ordered]@{
                            state_id = 'intro_hold'
                            vram_resident_set = [ordered]@{ bg_b_tiles = 64; bg_a_tiles = 96; font_tiles = 0; sprite_tiles = 0 }
                            load_time_dma_cost = [ordered]@{ bytes = 5120; phase = 'scene_entry' }
                            per_frame_dma_cost = [ordered]@{ bytes = 0; cadence = 'none' }
                            palette_domains = @('PAL0')
                            glyph_cache = [ordered]@{ mode = 'none'; tiles = 0 }
                            sprite_pressure = [ordered]@{ max_sprites_total = 0; max_sprites_per_scanline = 0 }
                            state_teardown = 'clear_panel'
                            budget_decision = 'planned'
                        }
                    )
                }
                hardware_ownership = [ordered]@{
                    window_owner = 'none'
                    cram_owner = 'cutscene_palette_script'
                    scroll_owner = 'cutscene_fsm'
                    audio_owner = 'cutscene_audio_cues'
                    h_int = [ordered]@{ in_use = $false }
                }
                text_timing_map = [ordered]@{
                    glyph_manifest_ref = 'doc/pipeline/cutscene/intro_glyph_manifest.json'
                    font_surface_owner = 'WINDOW'
                    base_frames_per_glyph = 2
                    punctuation_pauses = [ordered]@{ comma = 8; period = 16; ellipsis = 28; line_break = 10 }
                    advance_controls = [ordered]@{ accelerate_button = 'A'; advance_button = 'START'; skip_policy = 'complete_current_block_first' }
                }
                visual_source_gate = [ordered]@{
                    production_source_ready = $false
                    premium_source_manifest_ref = 'doc/contracts/premium_source_manifest.json'
                    human_approval_record_ref = 'doc/contracts/human_approval_record.md'
                    visual_delivery_gate_report_ref = 'out/logs/visual_delivery_gate_report.json'
                    blocked_statuses = @('blocked_no_premium_source', 'visual_gate_blocked')
                }
                evidence_plan = [ordered]@{
                    blastem_required = $true
                    screenshot_required = $true
                    runtime_metrics_scene_id = 'intro_cutscene'
                    visual_vdp_dump_required = $true
                    save_sram_required = $true
                    baseline_comparison_required = $true
                    freshness_audit_required = $true
                }
                approval = [ordered]@{
                    human_approval_required = $true
                    approval_status = 'not_approved'
                    approval_record_ref = 'doc/contracts/human_approval_record.md'
                }
            }
            $storyboard | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath (Join-Path $pipelineDir 'intro_cinematic_storyboard_contract.json') -Encoding UTF8
        }
    }

    $scene = [ordered]@{
        scene_id            = 'intro_cutscene'
        scene_role          = 'cutscene'
        boot_mode           = 'sram_bootstrap'
        capture_kind        = 'evidence_bundle'
        comparison_artifacts = @('screenshot')
        cleanup_required    = $true
        regression_required = $true
        capture_frame       = 180
        warmup_frames       = 30
    }

    if ($WithContract) {
        $scene['cutscene_contract'] = [ordered]@{
            cutscene_mode                  = 'panel_sequence'
            fsm_script                     = 'doc/pipeline/cutscene/intro_fsm.json'
            resource_plan                  = 'doc/pipeline/cutscene/intro_resource_plan.json'
            panel_layout                   = 'doc/pipeline/cutscene/intro_panel_layout.json'
            text_timing_map                = 'doc/pipeline/cutscene/intro_text_timing.json'
            palette_script                 = 'doc/pipeline/cutscene/intro_palette_script.json'
            glyph_manifest                 = 'doc/pipeline/cutscene/intro_glyph_manifest.json'
            advance_model                  = 'MIXED'
            teardown_plan                  = 'doc/pipeline/cutscene/intro_teardown_plan.json'
            evidence_plan                  = 'doc/pipeline/cutscene/intro_evidence_plan.json'
            uses_fullscreen_bitmap         = $false
            dynamic_fx                     = @('palette_cycling')
        }
        if ($WithStoryboardContract) {
            $scene.cutscene_contract['cinematic_storyboard_contract'] = 'doc/pipeline/cutscene/intro_cinematic_storyboard_contract.json'
        }
    }

    $contract = [ordered]@{
        schema_version  = '1.0.0'
        project_profile = 'aaa_gate'
        scenes          = @($scene)
    }

    $contract | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $docDir 'scene-contracts.json') -Encoding UTF8
}

function Invoke-Lint {
    param(
        [Parameter(Mandatory)][string]$ProjectRoot,
        [Parameter(Mandatory)][bool]$ExpectSuccess
    )

    powershell -NoProfile -ExecutionPolicy Bypass -File $lintScript -ProjectRoot $ProjectRoot -Mode aaa_gate | Out-Null
    $exitCode = $LASTEXITCODE
    $reportPath = Join-Path $ProjectRoot 'out\logs\scene_contract_report.json'
    $report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json

    if ($ExpectSuccess) {
        Assert-True 'Cutscene contract passes aaa_gate lint' ($exitCode -eq 0 -and $report.status -eq 'ok') $report.failure_reason
    } else {
        Assert-True 'Missing cutscene_contract fails aaa_gate lint' ($exitCode -ne 0)
    }

    return $report
}

$tmpMissing = Join-Path $env:TEMP "sgdk_cutscene_missing_$([guid]::NewGuid().ToString('N').Substring(0,8))"
$tmpNoStoryboard = Join-Path $env:TEMP "sgdk_cutscene_no_storyboard_$([guid]::NewGuid().ToString('N').Substring(0,8))"
$tmpValid = Join-Path $env:TEMP "sgdk_cutscene_valid_$([guid]::NewGuid().ToString('N').Substring(0,8))"

try {
    New-CutsceneProject -Root $tmpMissing -WithContract:$false
    New-CutsceneProject -Root $tmpNoStoryboard -WithContract:$true -WithStoryboardContract:$false
    New-CutsceneProject -Root $tmpValid -WithContract:$true -WithStoryboardContract:$true

    Write-Host ''
    Write-Host '=== Cutscene Contract Lint Test ==='
    Write-Host ''

    $missingReport = Invoke-Lint -ProjectRoot $tmpMissing -ExpectSuccess:$false
    $noStoryboardReport = Invoke-Lint -ProjectRoot $tmpNoStoryboard -ExpectSuccess:$false
    $validReport = Invoke-Lint -ProjectRoot $tmpValid -ExpectSuccess:$true

    $missingSC100 = @($missingReport.findings | Where-Object { $_.code -eq 'SC100' })
    $missingSC107 = @($noStoryboardReport.findings | Where-Object { $_.code -eq 'SC107' })
    $validSC100 = @($validReport.findings | Where-Object { $_.code -eq 'SC100' })
    $validSC107 = @($validReport.findings | Where-Object { $_.code -eq 'SC107' })

    Assert-True 'Missing contract emits SC100' ($missingSC100.Count -eq 1)
    Assert-True 'Missing cinematic storyboard emits SC107' ($missingSC107.Count -eq 1)
    Assert-True 'Valid contract emits no SC100' ($validSC100.Count -eq 0)
    Assert-True 'Valid contract emits no SC107' ($validSC107.Count -eq 0)
}
finally {
    Remove-Item -Recurse -Force $tmpMissing -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force $tmpNoStoryboard -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force $tmpValid -ErrorAction SilentlyContinue
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
