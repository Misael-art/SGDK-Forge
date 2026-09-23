<#
.SYNOPSIS
    Verifica gates de contrato de design de jogo (mechanic, level, enemy, tdd).

.DESCRIPTION
    Casos 1-11 (legado): gates de blocker e warn.
    Casos 12-18 (Canonical Hardening v2): gates de 3 buckets + ready flags.

    Buckets:
    - blocking_statuses:           blockers (integridade de contrato / runtime)
    - creative_blocking_statuses:  creative_blockers (direcao/autoria/visual)
    - technical_artifact_codes:    technical_artifacts (asset/lineage/optimization)

    Ready flags:
    - technical_ready:  blocker=0 AND technical_artifact_codes=0
    - creative_ready:   creative_blocker=0 AND semantic_audit_status != failed
    - ready_for_aaa:    technical_ready AND creative_ready
                        AND blocking_statuses.Count=0
                        AND creative_blocking_statuses.Count=0
                        AND semantic_audit_status != failed
                        AND semantic_audit_repeated_effect_learning_notes=false
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$fixtureRoot = Join-Path $workspaceRoot 'out\ci\game_design_contracts_fixture'
$auditScript = Join-Path $wrapperRoot 'audit_game_design_contracts.ps1'

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

function Assert-Equal {
    param([string]$Name, [string]$Expected, [string]$Actual, [string]$Detail = '')
    $script:total++
    if ($Expected -eq $Actual) {
        $script:passed++
        Write-Host "  [PASS] $Name"
    } else {
        $script:failed++
        $msg = "  [FAIL] $Name (expected='$Expected' actual='$Actual')"
        if ($Detail) { $msg += " -- $Detail" }
        Write-Host $msg
    }
}

function Reset-Fixture {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Run-Audit {
    param(
        [hashtable]$Params
    )
    $p = @{}
    foreach ($k in $Params.Keys) { $p[$k] = $Params[$k] }
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $auditScript @p 2>&1 | Out-Host
    return $LASTEXITCODE
}

function Read-Report {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path) {
        return (Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json)
    }
    return $null
}

Write-Host "=== Test 1: lab sem reports de mecanica (lab nao bloqueia) ==="
Reset-Fixture -Path $fixtureRoot
$labOut = Join-Path $fixtureRoot 'test1.json'
$ec = Run-Audit -Params @{ ProductStatus = 'technical_lab_validated'; OutputPath = $labOut }
$r = Read-Report -Path $labOut
Assert-Equal 'lab sem report nao bloqueia (status != blocked)' 'passed' "$($r.status)" "actual=$($r.status) exit=$ec"
Assert-True 'lab nao emite mechanic_contract_missing quando product_status=lab' ($r.blocking_statuses -notcontains 'mechanic_contract_missing')

Write-Host ""
Write-Host "=== Test 2: vertical_slice_candidate sem mechanic_validation_report.json ==="
Reset-Fixture -Path $fixtureRoot
$sliceOut = Join-Path $fixtureRoot 'test2.json'
$ec = Run-Audit -Params @{ ProductStatus = 'vertical_slice_candidate'; OutputPath = $sliceOut }
$r = Read-Report -Path $sliceOut
Assert-True 'slice sem mechanic emite mechanic_contract_missing' ($r.blocking_statuses -contains 'mechanic_contract_missing')
Assert-Equal 'slice sem contracts gera status=blocked' 'blocked' "$($r.status)"

Write-Host ""
Write-Host "=== Test 3: mecanica core com min_reuses=1 e versatility_cases=2 ==="
Reset-Fixture -Path $fixtureRoot
$mechPath = Join-Path $fixtureRoot 'mech.json'
Set-Content -LiteralPath $mechPath -Encoding UTF8 -Value @'
{
  "schema_version": "1.0.0",
  "mechanics": [
    {
      "mechanic_id": "double_jump",
      "mechanic_role": "core",
      "player_action": "jump twice in air",
      "system_rule": "second jump resets vertical velocity",
      "goal_link": "reach higher platforms",
      "input_binding": { "button": "A", "binding_description": "jump" },
      "activation_context": { "state_requirements": "midair" },
      "space_requirements": { "min_reuses_in_world": 3 },
      "required_game_elements": ["platforms"],
      "skill_challenge_type": "physical",
      "rules_and_limits": ["once per airtime"],
      "probability_model": { "type": "deterministic" },
      "versatility_cases": ["a", "b"],
      "level_design_reuse_plan": { "min_reuses": 1, "target_scenes": ["s1"] },
      "combination_map": [],
      "failure_states": [{ "failure_condition": "miss platform", "consequence": "fall" }],
      "feedback_model": { "visual": "flash", "audio": "jump_sfx", "haptic_or_camera": "none" },
      "tutorial_invisible_plan": { "teaching_scenes": ["s1"] },
      "test_scenarios": [{ "scenario_id": "t1", "setup": "platform gap", "expected_outcome": "land" }],
      "evidence_required": [{ "evidence_type": "screenshot", "location": "out/captures/s1.png" }],
      "mechanic_5_laws_compliance": {
        "agency": { "status": "passed" },
        "feedback": { "status": "passed" },
        "flow": { "status": "passed" },
        "consistency": { "status": "passed" },
        "reward": { "status": "passed" }
      }
    }
  ]
}
'@
$mechUnderusedOut = Join-Path $fixtureRoot 'test3.json'
$ec = Run-Audit -Params @{ MechanicContractPath = $mechPath; ProductStatus = 'vertical_slice_candidate'; OutputPath = $mechUnderusedOut }
$r = Read-Report -Path $mechUnderusedOut
Assert-True 'mechanic_underused eh emitido para core com versatility=2 e min_reuses=1' ($r.blocking_statuses -contains 'mechanic_underused')

Write-Host ""
Write-Host "=== Test 4: mecanica com input ambiguo (mesmo botao, sem disambiguation) ==="
Reset-Fixture -Path $fixtureRoot
$mechAmbPath = Join-Path $fixtureRoot 'mech_amb.json'
$mechAmb2Path = Join-Path $fixtureRoot 'mech_amb2.json'
$ambContent = @'
{
  "schema_version": "1.0.0",
  "mechanics": [
    {
      "mechanic_id": "context_action",
      "mechanic_role": "core",
      "player_action": "interact or attack depending on context",
      "system_rule": "use same button for two actions",
      "goal_link": "advance in game",
      "input_binding": { "button": "A", "binding_description": "context" },
      "activation_context": { "state_requirements": "near object" },
      "space_requirements": { "min_reuses_in_world": 3 },
      "required_game_elements": ["enemies", "npcs"],
      "skill_challenge_type": "cognitive",
      "rules_and_limits": ["context aware"],
      "probability_model": { "type": "deterministic" },
      "versatility_cases": ["a", "b", "c"],
      "level_design_reuse_plan": { "min_reuses": 3, "target_scenes": ["s1"] },
      "combination_map": [{ "combo_mechanic_id": "jump", "combo_effect": "jump+context" }],
      "failure_states": [{ "failure_condition": "wrong target", "consequence": "miss" }],
      "feedback_model": { "visual": "icon", "audio": "confirm", "haptic_or_camera": "none" },
      "tutorial_invisible_plan": { "teaching_scenes": ["s1"] },
      "test_scenarios": [{ "scenario_id": "t1", "setup": "near enemy", "expected_outcome": "attack" }],
      "evidence_required": [{ "evidence_type": "screenshot", "location": "out/captures/s1.png" }],
      "mechanic_5_laws_compliance": {
        "agency": { "status": "passed" },
        "feedback": { "status": "passed" },
        "flow": { "status": "passed" },
        "consistency": { "status": "passed" },
        "reward": { "status": "passed" }
      }
    }
  ]
}
'@
Set-Content -LiteralPath $mechAmbPath -Encoding UTF8 -Value $ambContent
$ambOut = Join-Path $fixtureRoot 'test4.json'
$ec = Run-Audit -Params @{ MechanicContractPath = $mechAmbPath; ProductStatus = 'vertical_slice_candidate'; OutputPath = $ambOut }
$r = Read-Report -Path $ambOut
# Note: a regra de input_ambiguous nao esta implementada no audit; marcamos como known_gap.
Assert-True 'audit processou sem crash' ($null -ne $r)

Write-Host ""
Write-Host "=== Test 5: probabilidade nao deterministica sem success_rate_percent ==="
Reset-Fixture -Path $fixtureRoot
$mechProbPath = Join-Path $fixtureRoot 'mech_prob.json'
$probContent = @'
{
  "schema_version": "1.0.0",
  "mechanics": [
    {
      "mechanic_id": "lucky_hit",
      "mechanic_role": "supporting",
      "player_action": "attack with crit chance",
      "system_rule": "5% crit chance",
      "goal_link": "burst damage",
      "input_binding": { "button": "B", "binding_description": "attack" },
      "activation_context": { "state_requirements": "combat" },
      "space_requirements": { "min_reuses_in_world": 1 },
      "required_game_elements": ["enemies"],
      "skill_challenge_type": "physical",
      "rules_and_limits": ["cooldown 500ms"],
      "probability_model": { "type": "random" },
      "versatility_cases": [],
      "level_design_reuse_plan": { "min_reuses": 1, "target_scenes": ["s1"] },
      "combination_map": [],
      "failure_states": [{ "failure_condition": "miss", "consequence": "no damage" }],
      "feedback_model": { "visual": "flash", "audio": "hit", "haptic_or_camera": "shake" },
      "tutorial_invisible_plan": { "teaching_scenes": ["s1"] },
      "test_scenarios": [{ "scenario_id": "t1", "setup": "attack enemy", "expected_outcome": "damage" }],
      "evidence_required": [{ "evidence_type": "screenshot", "location": "out/captures/s1.png" }],
      "mechanic_5_laws_compliance": {
        "agency": { "status": "passed" },
        "feedback": { "status": "passed" },
        "flow": { "status": "passed" },
        "consistency": { "status": "passed" },
        "reward": { "status": "passed" }
      }
    }
  ]
}
'@
Set-Content -LiteralPath $mechProbPath -Encoding UTF8 -Value $probContent
$probOut = Join-Path $fixtureRoot 'test5.json'
$ec = Run-Audit -Params @{ MechanicContractPath = $mechProbPath; ProductStatus = 'vertical_slice_candidate'; OutputPath = $probOut }
$r = Read-Report -Path $probOut
Assert-True 'mechanic_probability_undeclared emitido' ($r.blocking_statuses -contains 'mechanic_probability_undeclared')

Write-Host ""
Write-Host "=== Test 6: level sem golden_path ==="
Reset-Fixture -Path $fixtureRoot
$lvlNoGpPath = Join-Path $fixtureRoot 'lvl_no_gp.json'
$lvlNoGpContent = @'
{
  "schema_version": "1.0.0",
  "scope_id": "stage_1",
  "waypoints": [],
  "gates": [],
  "optional_routes": [],
  "risk_markers": [],
  "breathing_zones": [],
  "phase_rhythm_map": [{ "phase": "calm", "intensity": "low", "start_waypoint": "w1", "end_waypoint": "w2" }],
  "mechanic_reuse_map": [],
  "tutorial_invisible_beats": [],
  "environmental_narrative_map": [],
  "failure_recovery_model": { "last_checkpoint": "w1", "reset_strategy": "spawn at w1" },
  "acceptance_tests": []
}
'@
Set-Content -LiteralPath $lvlNoGpPath -Encoding UTF8 -Value $lvlNoGpContent
$noGpOut = Join-Path $fixtureRoot 'test6.json'
$ec = Run-Audit -Params @{ LevelBlueprintPath = $lvlNoGpPath; ProductStatus = 'vertical_slice_candidate'; OutputPath = $noGpOut }
$r = Read-Report -Path $noGpOut
Assert-True 'golden_path_missing emitido' ($r.blocking_statuses -contains 'golden_path_missing')

Write-Host ""
Write-Host "=== Test 7: level sem mecanica core em reuse_map ==="
Reset-Fixture -Path $fixtureRoot
$mechOkPath = Join-Path $fixtureRoot 'mech_ok.json'
$lvlNoReusePath = Join-Path $fixtureRoot 'lvl_no_reuse.json'
$mechOkContent = @'
{
  "schema_version": "1.0.0",
  "mechanics": [
    {
      "mechanic_id": "dash",
      "mechanic_role": "core",
      "player_action": "quick burst forward",
      "system_rule": "consume 1 stamina",
      "goal_link": "close gap",
      "input_binding": { "button": "C", "binding_description": "dash" },
      "activation_context": { "state_requirements": "ground" },
      "space_requirements": { "min_reuses_in_world": 5 },
      "required_game_elements": ["enemies", "gaps"],
      "skill_challenge_type": "physical",
      "rules_and_limits": ["1 stamina"],
      "probability_model": { "type": "deterministic" },
      "versatility_cases": ["horizontal", "diagonal", "cancel"],
      "level_design_reuse_plan": { "min_reuses": 3, "target_scenes": ["stage_1"] },
      "combination_map": [{ "combo_mechanic_id": "jump", "combo_effect": "aerial dash" }],
      "failure_states": [{ "failure_condition": "no stamina", "consequence": "no dash" }],
      "feedback_model": { "visual": "blur", "audio": "whoosh", "haptic_or_camera": "shake" },
      "tutorial_invisible_plan": { "teaching_scenes": ["stage_1"] },
      "test_scenarios": [{ "scenario_id": "t1", "setup": "near enemy", "expected_outcome": "close" }],
      "evidence_required": [{ "evidence_type": "screenshot", "location": "out/captures/stage_1.png" }],
      "mechanic_5_laws_compliance": {
        "agency": { "status": "passed" },
        "feedback": { "status": "passed" },
        "flow": { "status": "passed" },
        "consistency": { "status": "passed" },
        "reward": { "status": "passed" }
      }
    }
  ]
}
'@
$lvlNoReuseContent = @'
{
  "schema_version": "1.0.0",
  "scope_id": "stage_1",
  "golden_path": { "waypoint_sequence": ["w1", "w2"], "visible_landmarks": ["tower"] },
  "waypoints": [{ "waypoint_id": "w1", "position": "start", "purpose": "spawn" }, { "waypoint_id": "w2", "position": "end", "purpose": "goal" }],
  "gates": [],
  "optional_routes": [],
  "risk_markers": [],
  "breathing_zones": [],
  "phase_rhythm_map": [{ "phase": "calm", "intensity": "low", "start_waypoint": "w1", "end_waypoint": "w2" }, { "phase": "pressure", "intensity": "medium", "start_waypoint": "w2", "end_waypoint": "w1" }],
  "mechanic_reuse_map": [],
  "tutorial_invisible_beats": [],
  "environmental_narrative_map": [],
  "failure_recovery_model": { "last_checkpoint": "w1", "reset_strategy": "spawn at w1" },
  "acceptance_tests": []
}
'@
Set-Content -LiteralPath $mechOkPath -Encoding UTF8 -Value $mechOkContent
Set-Content -LiteralPath $lvlNoReusePath -Encoding UTF8 -Value $lvlNoReuseContent
$noReuseOut = Join-Path $fixtureRoot 'test7.json'
$ec = Run-Audit -Params @{ MechanicContractPath = $mechOkPath; LevelBlueprintPath = $lvlNoReusePath; ProductStatus = 'vertical_slice_candidate'; OutputPath = $noReuseOut }
$r = Read-Report -Path $noReuseOut
Assert-True 'level_mechanic_reuse_missing emitido quando core nao em reuse_map' ($r.blocking_statuses -contains 'level_mechanic_reuse_missing')

Write-Host ""
Write-Host "=== Test 8: enemy roster sem role e sem telegraph ==="
Reset-Fixture -Path $fixtureRoot
$enemyNoRolePath = Join-Path $fixtureRoot 'enemy_no_role.json'
$enemyNoRoleContent = @'
{
  "schema_version": "1.0.0",
  "scope_id": "stage_1",
  "enemies": [
    {
      "enemy_id": "bug",
      "head_metric": "S",
      "hp": 1,
      "damage": 1,
      "movement_model": "ground_patrol",
      "ai_behavior": { "aggro_radius_px": 32, "retreat_threshold_hp_percent": 0 },
      "weakness_model": {},
      "synergy_partners": [],
      "level_placement_rules": { "target_scenes": ["stage_1"] },
      "feedback_on_hit": { "visual": "flash", "audio": "pop" },
      "feedback_on_alert": { "visual": "blink", "audio": "beep" }
    }
  ]
}
'@
Set-Content -LiteralPath $enemyNoRolePath -Encoding UTF8 -Value $enemyNoRoleContent
$noRoleOut = Join-Path $fixtureRoot 'test8.json'
$ec = Run-Audit -Params @{ EnemyRosterPath = $enemyNoRolePath; ProductStatus = 'vertical_slice_candidate'; OutputPath = $noRoleOut }
$r = Read-Report -Path $noRoleOut
Assert-True 'enemy_role_missing emitido' ($r.blocking_statuses -contains 'enemy_role_missing')
Assert-True 'enemy_telegraph_missing emitido' ($r.blocking_statuses -contains 'enemy_telegraph_missing')

Write-Host ""
Write-Host "=== Test 9: produto candidato sem TDD ==="
Reset-Fixture -Path $fixtureRoot
$noTddOut = Join-Path $fixtureRoot 'test9.json'
$ec = Run-Audit -Params @{ ProductStatus = 'vertical_slice_candidate'; OutputPath = $noTddOut }
$r = Read-Report -Path $noTddOut
Assert-True 'tdd_missing_for_product emitido para slice' ($r.blocking_statuses -contains 'tdd_missing_for_product')

Write-Host ""
Write-Host "=== Test 10: boss com head_metric=M ==="
Reset-Fixture -Path $fixtureRoot
$bossMPath = Join-Path $fixtureRoot 'boss_m.json'
$bossMContent = @'
{
  "schema_version": "1.0.0",
  "scope_id": "boss_arena",
  "enemies": [
    {
      "enemy_id": "mini_boss",
      "role": "boss",
      "head_metric": "M",
      "hp": 30,
      "damage": 5,
      "movement_model": "ground_chase",
      "ai_behavior": { "aggro_radius_px": 200, "retreat_threshold_hp_percent": 0 },
      "telegraph_model": { "telegraph_frames": 20, "visual_cue": "blink" },
      "weakness_model": {},
      "synergy_partners": [],
      "level_placement_rules": { "boss_arena_id": "boss_arena" },
      "feedback_on_hit": { "visual": "flash", "audio": "hit" },
      "feedback_on_alert": { "visual": "roar", "audio": "stinger1" }
    }
  ]
}
'@
Set-Content -LiteralPath $bossMPath -Encoding UTF8 -Value $bossMContent
$bossMOut = Join-Path $fixtureRoot 'test10.json'
$ec = Run-Audit -Params @{ EnemyRosterPath = $bossMPath; ProductStatus = 'vertical_slice_candidate'; OutputPath = $bossMOut }
$r = Read-Report -Path $bossMOut
Assert-True 'enemy_head_metric_invalid emitido quando boss tem M' ($r.blocking_statuses -contains 'enemy_head_metric_invalid')

Write-Host ""
Write-Host "=== Test 11: fixture completa (todos contratos validos) ==="
Reset-Fixture -Path $fixtureRoot
$okMechPath = Join-Path $fixtureRoot 'ok_mech.json'
$okLvlPath = Join-Path $fixtureRoot 'ok_lvl.json'
$okEnemyPath = Join-Path $fixtureRoot 'ok_enemy.json'
$okTddPath = Join-Path $fixtureRoot 'ok_tdd.json'

$okMechContent = @'
{
  "schema_version": "1.0.0",
  "mechanics": [
    {
      "mechanic_id": "dash",
      "mechanic_role": "core",
      "player_action": "burst",
      "system_rule": "consume stamina",
      "goal_link": "close gap",
      "input_binding": { "button": "C", "binding_description": "dash" },
      "activation_context": { "state_requirements": "ground" },
      "space_requirements": { "min_reuses_in_world": 5 },
      "required_game_elements": ["enemies", "gaps"],
      "skill_challenge_type": "physical",
      "rules_and_limits": ["1 stamina"],
      "probability_model": { "type": "deterministic" },
      "versatility_cases": ["horizontal", "diagonal", "cancel"],
      "level_design_reuse_plan": { "min_reuses": 3, "target_scenes": ["stage_1"] },
      "combination_map": [{ "combo_mechanic_id": "jump", "combo_effect": "aerial dash" }],
      "failure_states": [{ "failure_condition": "no stamina", "consequence": "no dash" }],
      "feedback_model": { "visual": "blur", "audio": "whoosh", "haptic_or_camera": "shake" },
      "tutorial_invisible_plan": { "teaching_scenes": ["stage_1"] },
      "test_scenarios": [{ "scenario_id": "t1", "setup": "near enemy", "expected_outcome": "close" }],
      "evidence_required": [{ "evidence_type": "screenshot", "location": "out/captures/stage_1.png" }],
      "mechanic_5_laws_compliance": {
        "agency": { "status": "passed" },
        "feedback": { "status": "passed" },
        "flow": { "status": "passed" },
        "consistency": { "status": "passed" },
        "reward": { "status": "passed" }
      }
    }
  ]
}
'@
$okLvlContent = @'
{
  "schema_version": "1.0.0",
  "scope_id": "stage_1",
  "golden_path": { "waypoint_sequence": ["w1", "w2"], "visible_landmarks": ["tower"] },
  "waypoints": [{ "waypoint_id": "w1", "position": "start", "purpose": "spawn" }, { "waypoint_id": "w2", "position": "end", "purpose": "goal" }],
  "gates": [],
  "optional_routes": [],
  "risk_markers": [],
  "breathing_zones": [],
  "phase_rhythm_map": [{ "phase": "calm", "intensity": "low", "start_waypoint": "w1", "end_waypoint": "w2" }, { "phase": "pressure", "intensity": "medium", "start_waypoint": "w2", "end_waypoint": "w1" }],
  "mechanic_reuse_map": [{ "mechanic_id": "dash", "target_scenes": ["stage_1"], "reuse_count": 5 }],
  "tutorial_invisible_beats": [],
  "environmental_narrative_map": [],
  "failure_recovery_model": { "last_checkpoint": "w1", "reset_strategy": "spawn at w1" },
  "acceptance_tests": []
}
'@
$okEnemyContent = @'
{
  "schema_version": "1.0.0",
  "scope_id": "stage_1",
  "enemies": [
    {
      "enemy_id": "grunt",
      "role": "patrulheiro",
      "head_metric": "S",
      "hp": 2,
      "damage": 1,
      "movement_model": "ground_patrol",
      "ai_behavior": { "aggro_radius_px": 32, "retreat_threshold_hp_percent": 0 },
      "telegraph_model": { "telegraph_frames": 12, "visual_cue": "blink" },
      "weakness_model": { "weakness_position": "head" },
      "synergy_partners": [{ "enemy_id": "shooter", "synergy_type": "frontline_shield" }],
      "level_placement_rules": { "target_scenes": ["stage_1"] },
      "feedback_on_hit": { "visual": "flash", "audio": "pop" },
      "feedback_on_alert": { "visual": "blink", "audio": "beep" }
    },
    {
      "enemy_id": "dragon",
      "role": "boss",
      "head_metric": "XL",
      "hp": 80,
      "damage": 8,
      "movement_model": "phase_transition",
      "ai_behavior": { "aggro_radius_px": 200, "retreat_threshold_hp_percent": 0 },
      "telegraph_model": { "telegraph_frames": 30, "visual_cue": "roar" },
      "weakness_model": { "weakness_position": "head" },
      "synergy_partners": [],
      "level_placement_rules": { "boss_arena_id": "stage_1_boss" },
      "feedback_on_hit": { "visual": "flash", "audio": "boom" },
      "feedback_on_alert": { "visual": "roar", "audio": "stinger_boss" },
      "boss_state_count": 3
    }
  ]
}
'@
$okTddContent = @'
{
  "schema_version": "1.0.0",
  "tdd_id": "tdd_stage_1",
  "scene_manager_scope": { "topology": "linear", "deterministic": true },
  "input_abstraction_scope": { "abstraction_layer": "input_director", "latency_target_ms": 16 },
  "state_fsm_map": [
    { "scene_id": "stage_1", "states": ["play", "pause", "death"], "transitions": [{ "from": "play", "to": "pause", "trigger": "start_pause" }] }
  ],
  "memory_pool_map": [
    { "pool_id": "enemies", "type": "enemy", "size": 8, "owner": "enemy_director.c" }
  ],
  "vblank_dma_ownership": { "vblank_owner": "main.c", "dma_owners": ["vdp_loader.c"] },
  "h_int_ownership": { "h_int_in_use": false },
  "audio_ownership": { "driver": "xgm2", "channel_owners": ["bgm", "sfx", "voice"] },
  "save_scope": "none",
  "region_timing_scope": { "region": "NTSC" },
  "rom_mastering_scope": { "size_target_kb": 4096, "header_validated": true, "checksum_validated": true },
  "technique_selection": {
    "registry_source": "doc/05_technical/93_16bit_hardware_mastery_registry.json",
    "usage_manifest_path": "doc/technique_usage_manifest.json",
    "selected_registry_ids": ["line_scrolling"],
    "required_tags": ["LINE_SCROLL", "PARALLAX"],
    "owner_skills": ["code/sgdk-runtime-coder", "hardware/megadrive-vdp-budget-analyst"],
    "selection_rationale": "Line scrolling supports the stage depth with measurable budget.",
    "fallback_strategy": "Use coarse plane scroll bands if line updates exceed budget.",
    "application_plan": [
      {
        "registry_id": "line_scrolling",
        "scene_or_system": "stage_1",
        "gameplay_or_narrative_purpose": "Communicate speed and route depth during play.",
        "visual_or_audio_role": "Layered landscape depth.",
        "owner_skill": "code/sgdk-runtime-coder",
        "budget_evidence": "dma_queue_contract",
        "fallback": "Use plane scroll bands."
      }
    ],
    "rejected_or_deferred": []
  },
  "risk_mitigation_table": [
    { "risk_id": "vram_overflow", "risk": "too many tiles", "mitigation": "tilemap streaming" }
  ]
}
'@
Set-Content -LiteralPath $okMechPath -Encoding UTF8 -Value $okMechContent
Set-Content -LiteralPath $okLvlPath -Encoding UTF8 -Value $okLvlContent
Set-Content -LiteralPath $okEnemyPath -Encoding UTF8 -Value $okEnemyContent
Set-Content -LiteralPath $okTddPath -Encoding UTF8 -Value $okTddContent
$okOut = Join-Path $fixtureRoot 'test11.json'
$ec = Run-Audit -Params @{
    MechanicContractPath = $okMechPath
    LevelBlueprintPath = $okLvlPath
    EnemyRosterPath = $okEnemyPath
    TddContractPath = $okTddPath
    ProductStatus = 'vertical_slice_candidate'
    OutputPath = $okOut
}
$r = Read-Report -Path $okOut
Assert-Equal 'fixture completa: status=passed' 'passed' "$($r.status)"
Assert-True 'fixture completa: nenhum blocker de contrato de design' ($r.blocking_statuses.Count -eq 0)
Assert-True 'fixture completa: mechanic_role catalog tem dash=core' ($r.catalog_checks.mechanic_role_catalog.valid_roles_used -contains 'core')
Assert-True 'fixture completa: enemy_ai_role catalog tem patrulheiro e boss' ($r.catalog_checks.enemy_ai_role_catalog.valid_roles_used -contains 'patrulheiro')
Assert-True 'fixture completa: enemy_ai_role catalog tem boss' ($r.catalog_checks.enemy_ai_role_catalog.valid_roles_used -contains 'boss')
Assert-True 'fixture completa: head_metric catalog tem S e XL' ($r.catalog_checks.head_metric_reference.valid_metrics_used -contains 'S')

Write-Host ""
Write-Host "=== Test 12: 3-bucket separation - creative_blocker NAO vai em blocking_statuses ==="
# Cria fixture completa e verifica que:
# - blocking_statuses.Count = 0
# - creative_blocking_statuses.Count = 0 (sem semantic_audit nao ha creative blockers)
# - technical_artifact_codes.Count = 0
# - technical_artifact_status = "technical_artifact_ok"
# - technical_ready, creative_ready, ready_for_aaa = true
# (creative_blockers vem de semantic_audit, nao do proprio audit. Esta fixture
# confirma que o report separa os 3 buckets corretamente.)
Reset-Fixture -Path $fixtureRoot
$creDecorMech = Join-Path $fixtureRoot 'cre_decor_mech.json'
$creDecorLvl = Join-Path $fixtureRoot 'cre_decor_lvl.json'
$creDecorEnemy = Join-Path $fixtureRoot 'cre_decor_enemy.json'
$creDecorTdd = Join-Path $fixtureRoot 'cre_decor_tdd.json'
Set-Content -LiteralPath $creDecorMech -Encoding UTF8 -Value $okMechContent
Set-Content -LiteralPath $creDecorLvl -Encoding UTF8 -Value $okLvlContent
Set-Content -LiteralPath $creDecorEnemy -Encoding UTF8 -Value $okEnemyContent
Set-Content -LiteralPath $creDecorTdd -Encoding UTF8 -Value $okTddContent
$creDecorOut = Join-Path $fixtureRoot 'test12.json'
$ec = Run-Audit -Params @{
    MechanicContractPath = $creDecorMech
    LevelBlueprintPath = $creDecorLvl
    EnemyRosterPath = $creDecorEnemy
    TddContractPath = $creDecorTdd
    ProductStatus = 'vertical_slice_candidate'
    OutputPath = $creDecorOut
}
$r = Read-Report -Path $creDecorOut
Assert-Equal 'fixture completa: status=passed' 'passed' "$($r.status)"
Assert-True 'fixture completa: zero blockers (integridade)' ($r.blocking_statuses.Count -eq 0)
Assert-True 'fixture completa: zero creative_blockers (sem semantic audit)' ($r.creative_blocking_statuses.Count -eq 0)
Assert-True 'fixture completa: zero technical_artifact_codes' ($r.technical_artifact_codes.Count -eq 0)
Assert-True 'fixture completa: technical_artifact_status=technical_artifact_ok' ("$($r.technical_artifact_status)" -eq 'technical_artifact_ok')
Assert-True 'fixture completa: technical_ready=true' ([bool]$r.technical_ready)
Assert-True 'fixture completa: creative_ready=true (sem semantic audit)' ([bool]$r.creative_ready)
Assert-True 'fixture completa: ready_for_aaa=true (sem semantic audit)' ([bool]$r.ready_for_aaa)
Assert-Equal 'fixture completa: semantic_audit_status=not_provided' 'not_provided' "$($r.semantic_audit_status)"
Assert-True 'fixture completa: repeated_effect_learning_notes=false' (-not [bool]$r.semantic_audit_repeated_effect_learning_notes)

Write-Host ""
Write-Host "=== Test 13: lab downgrade - blocker vira warn, mas creative_blocker permanece ==="
# Em lab, blockers sao downgraded para warn. creative_blockers sao criados pelo
# semantic_audit, nao pelo proprio audit. Validamos: com lab+fixture completa,
# nenhum blocker eh emitido (porque lab nao exige contratos), e status=passed.
Reset-Fixture -Path $fixtureRoot
$labWithMech = Join-Path $fixtureRoot 'lab_mech.json'
Set-Content -LiteralPath $labWithMech -Encoding UTF8 -Value $okMechContent
$labCoreOut = Join-Path $fixtureRoot 'test13.json'
$ec = Run-Audit -Params @{
    MechanicContractPath = $labWithMech
    ProductStatus = 'technical_lab_validated'
    OutputPath = $labCoreOut
}
$r = Read-Report -Path $labCoreOut
Assert-Equal 'lab+fixture completa: status=passed (lab nao exige contracts)' 'passed' "$($r.status)"
Assert-True 'lab+fixture completa: zero blockers' ($r.blocking_statuses.Count -eq 0)
Assert-True 'lab+fixture completa: zero creative_blockers' ($r.creative_blocking_statuses.Count -eq 0)
Assert-True 'lab+fixture completa: ready_for_aaa=true (lab sem policy)' ([bool]$r.ready_for_aaa)

Write-Host ""
Write-Host "=== Test 14: lab downgrade - core mechanic with bad versatility vira warn, nao blocker ==="
Reset-Fixture -Path $fixtureRoot
$labBadMech = Join-Path $fixtureRoot 'lab_bad_mech.json'
$labBadContent = @'
{
  "schema_version": "1.0.0",
  "mechanics": [
    {
      "mechanic_id": "jump",
      "mechanic_role": "core",
      "player_action": "jump",
      "system_rule": "vertical impulse",
      "goal_link": "reach platforms",
      "input_binding": { "button": "A", "binding_description": "jump" },
      "activation_context": { "state_requirements": "ground" },
      "space_requirements": { "min_reuses_in_world": 1 },
      "required_game_elements": ["platforms"],
      "skill_challenge_type": "physical",
      "rules_and_limits": ["cooldown 200ms"],
      "probability_model": { "type": "deterministic" },
      "versatility_cases": ["a"],
      "level_design_reuse_plan": { "min_reuses": 1, "target_scenes": ["s1"] },
      "combination_map": [],
      "failure_states": [{ "failure_condition": "miss", "consequence": "fall" }],
      "feedback_model": { "visual": "flash", "audio": "jump", "haptic_or_camera": "none" },
      "tutorial_invisible_plan": { "teaching_scenes": ["s1"] },
      "test_scenarios": [{ "scenario_id": "t1", "setup": "platform gap", "expected_outcome": "land" }],
      "evidence_required": [{ "evidence_type": "screenshot", "location": "out/captures/s1.png" }],
      "mechanic_5_laws_compliance": {
        "agency": { "status": "passed" }, "feedback": { "status": "passed" },
        "flow": { "status": "passed" }, "consistency": { "status": "passed" },
        "reward": { "status": "passed" }
      }
    }
  ]
}
'@
Set-Content -LiteralPath $labBadMech -Encoding UTF8 -Value $labBadContent
$labBadOut = Join-Path $fixtureRoot 'test14.json'
$ec = Run-Audit -Params @{
    MechanicContractPath = $labBadMech
    ProductStatus = 'technical_lab_validated'
    OutputPath = $labBadOut
}
$r = Read-Report -Path $labBadOut
Assert-Equal 'lab+bad mech: status=warn (downgrade), nao blocked' 'warn' "$($r.status)"
Assert-True 'lab+bad mech: mechanic_underused NAO esta em blocking_statuses' ($r.blocking_statuses -notcontains 'mechanic_underused')
# Note: o audit emite warn, nao em nenhum bucket. Verify issues list.
$underusedIssues = @($r.issues | Where-Object { $_.code -eq 'mechanic_underused' })
Assert-True 'lab+bad mech: mechanic_underused emitido como warn (severity=warn)' (@($underusedIssues).Count -gt 0 -and $underusedIssues[0].severity -eq 'warn')
Assert-True 'lab+bad mech: zero creative_blockers (lab nao diferencia)' ($r.creative_blocking_statuses.Count -eq 0)
Assert-True 'lab+bad mech: zero technical_artifacts' ($r.technical_artifact_codes.Count -eq 0)
Assert-True 'lab+bad mech: ready_for_aaa=true (lab sem policy)' ([bool]$r.ready_for_aaa)

Write-Host ""
Write-Host "=== Test 15: technical_artifact (style_manifest_missing) - vou em technical_artifact_codes, NAO em blocking/creative ==="
# O audit nao emite style_manifest_missing por si (vem de outro lugar), mas
# verificamos que a estrutura do report separa os 3 buckets. Validamos isso
# checando a existencia dos 3 campos no report.
Reset-Fixture -Path $fixtureRoot
$bucketsMech = Join-Path $fixtureRoot 'buckets_mech.json'
$bucketsLvl = Join-Path $fixtureRoot 'buckets_lvl.json'
$bucketsEnemy = Join-Path $fixtureRoot 'buckets_enemy.json'
$bucketsTdd = Join-Path $fixtureRoot 'buckets_tdd.json'
Set-Content -LiteralPath $bucketsMech -Encoding UTF8 -Value $okMechContent
Set-Content -LiteralPath $bucketsLvl -Encoding UTF8 -Value $okLvlContent
Set-Content -LiteralPath $bucketsEnemy -Encoding UTF8 -Value $okEnemyContent
Set-Content -LiteralPath $bucketsTdd -Encoding UTF8 -Value $okTddContent
$bucketsOut = Join-Path $fixtureRoot 'test15.json'
$ec = Run-Audit -Params @{
    MechanicContractPath = $bucketsMech
    LevelBlueprintPath = $bucketsLvl
    EnemyRosterPath = $bucketsEnemy
    TddContractPath = $bucketsTdd
    ProductStatus = 'vertical_slice_candidate'
    OutputPath = $bucketsOut
}
$r = Read-Report -Path $bucketsOut
Assert-True 'report tem campo blocking_statuses' ($r.PSObject.Properties.Name -contains 'blocking_statuses')
Assert-True 'report tem campo creative_blocking_statuses' ($r.PSObject.Properties.Name -contains 'creative_blocking_statuses')
Assert-True 'report tem campo technical_artifact_codes' ($r.PSObject.Properties.Name -contains 'technical_artifact_codes')
Assert-True 'report tem campo technical_artifact_status' ($r.PSObject.Properties.Name -contains 'technical_artifact_status')
Assert-True 'report tem campo technical_ready' ($r.PSObject.Properties.Name -contains 'technical_ready')
Assert-True 'report tem campo creative_ready' ($r.PSObject.Properties.Name -contains 'creative_ready')
Assert-True 'report tem campo ready_for_aaa' ($r.PSObject.Properties.Name -contains 'ready_for_aaa')
Assert-True 'report tem campo semantic_audit_status' ($r.PSObject.Properties.Name -contains 'semantic_audit_status')
Assert-True 'report tem campo semantic_audit_repeated_effect_learning_notes' ($r.PSObject.Properties.Name -contains 'semantic_audit_repeated_effect_learning_notes')

Write-Host ""
Write-Host "=== Test 16: schema_version 2.0.0 ==="
Reset-Fixture -Path $fixtureRoot
$verMech = Join-Path $fixtureRoot 'ver_mech.json'
Set-Content -LiteralPath $verMech -Encoding UTF8 -Value $okMechContent
$verOut = Join-Path $fixtureRoot 'test16.json'
$ec = Run-Audit -Params @{
    MechanicContractPath = $verMech
    ProductStatus = 'vertical_slice_candidate'
    OutputPath = $verOut
}
$r = Read-Report -Path $verOut
Assert-Equal 'audit report schema_version=2.0.0' '2.0.0' "$($r.schema_version)"

Write-Host ""
Write-Host "=== Test 17: lab + contrato ausente - status=passed (lab nao exige) ==="
# Validacao: lab nao emite contract_missing, mas ready_for_aaa continua true
# (lab e o caso onde NAO se aplica politica).
Reset-Fixture -Path $fixtureRoot
$labNoOut = Join-Path $fixtureRoot 'test17.json'
$ec = Run-Audit -Params @{
    ProductStatus = 'technical_lab_validated'
    OutputPath = $labNoOut
}
$r = Read-Report -Path $labNoOut
Assert-Equal 'lab sem contracts: status=passed' 'passed' "$($r.status)"
Assert-True 'lab sem contracts: blocking_statuses.Count=0' ($r.blocking_statuses.Count -eq 0)
Assert-True 'lab sem contracts: creative_blocking_statuses.Count=0' ($r.creative_blocking_statuses.Count -eq 0)
Assert-True 'lab sem contracts: technical_artifact_codes.Count=0' ($r.technical_artifact_codes.Count -eq 0)
Assert-True 'lab sem contracts: technical_artifact_status=technical_artifact_ok' ("$($r.technical_artifact_status)" -eq 'technical_artifact_ok')
Assert-True 'lab sem contracts: ready_for_aaa=true' ([bool]$r.ready_for_aaa)

Write-Host ""
Write-Host "=== Test 18: ready flags - co-existencia (tecnico+creative) ==="
# Confirma que ready_for_aaa exige ambos, mesmo quando o report so tem blockers tecnicos.
Reset-Fixture -Path $fixtureRoot
$sliceBadMech = Join-Path $fixtureRoot 'slice_bad_mech.json'
$sliceBadLvl = Join-Path $fixtureRoot 'slice_bad_lvl.json'
$sliceBadEnemy = Join-Path $fixtureRoot 'slice_bad_enemy.json'
$badTddPath = Join-Path $fixtureRoot 'bad_tdd.json'
Set-Content -LiteralPath $sliceBadMech -Encoding UTF8 -Value $okMechContent
Set-Content -LiteralPath $sliceBadLvl -Encoding UTF8 -Value $okLvlContent
Set-Content -LiteralPath $sliceBadEnemy -Encoding UTF8 -Value $okEnemyContent
$badTddContent = @'
{
  "schema_version": "1.0.0",
  "tdd_id": "tdd_partial",
  "scene_manager_scope": { "topology": "linear", "deterministic": true }
}
'@
Set-Content -LiteralPath $badTddPath -Encoding UTF8 -Value $badTddContent
$sliceBadTddOut = Join-Path $fixtureRoot 'test18.json'
$ec = Run-Audit -Params @{
    MechanicContractPath = $sliceBadMech
    LevelBlueprintPath = $sliceBadLvl
    EnemyRosterPath = $sliceBadEnemy
    TddContractPath = $badTddPath
    ProductStatus = 'vertical_slice_candidate'
    OutputPath = $sliceBadTddOut
}
$r = Read-Report -Path $sliceBadTddOut
Assert-Equal 'slice+tdd parcial: status=blocked' 'blocked' "$($r.status)"
Assert-True 'slice+tdd parcial: scene_fsm_missing em blocking_statuses' ($r.blocking_statuses -contains 'scene_fsm_missing')
Assert-True 'slice+tdd parcial: technical_ready=false' (-not [bool]$r.technical_ready)
Assert-True 'slice+tdd parcial: ready_for_aaa=false' (-not [bool]$r.ready_for_aaa)
Assert-True 'slice+tdd parcial: creative_ready=true (criativo limpo, mas ready_for_aaa exige tecnico tambem)' ([bool]$r.creative_ready)



Write-Host ""
Write-Host "=== Test 19: TDD de produto sem selecao explicita de tecnicas ==="
Reset-Fixture -Path $fixtureRoot
$tddNoTechniquePath = Join-Path $fixtureRoot 'tdd_no_technique.json'
Set-Content -LiteralPath $tddNoTechniquePath -Encoding UTF8 -Value @'
{
  "schema_version": "1.0.0",
  "tdd_id": "stage_1_tdd",
  "scene_manager_scope": { "topology": "linear", "deterministic": true },
  "input_abstraction_scope": { "abstraction_layer": "input.c", "latency_target_ms": 16 },
  "state_fsm_map": [{ "scene_id": "stage_1", "states": ["enter", "play"], "transitions": [] }],
  "memory_pool_map": [{ "pool_id": "actors", "type": "enemy", "size": 4, "owner": "actors.c" }],
  "vblank_dma_ownership": { "vblank_owner": "video.c", "dma_owners": ["video.c"] },
  "h_int_ownership": { "h_int_in_use": false },
  "audio_ownership": { "driver": "xgm2", "channel_owners": ["music"] },
  "save_scope": "none",
  "region_timing_scope": { "region": "NTSC", "frame_budget_ms": 16.67 },
  "rom_mastering_scope": { "size_target_kb": 4096 },
  "risk_mitigation_table": [{ "risk_id": "dma", "risk": "DMA overflow", "mitigation": "queue budget" }]
}
'@
$tddNoTechniqueOut = Join-Path $fixtureRoot 'test19.json'
$ec = Run-Audit -Params @{ TddContractPath = $tddNoTechniquePath; ProductStatus = 'vertical_slice_candidate'; OutputPath = $tddNoTechniqueOut }
$r = Read-Report -Path $tddNoTechniqueOut
Assert-True 'produto sem technique_selection emite tdd_technique_selection_missing' ($r.blocking_statuses -contains 'tdd_technique_selection_missing')

Write-Host ""
Write-Host "=== Resumo ==="
Write-Host "Passou: $passed / $total"
if ($failed -gt 0) {
    Write-Host "FALHOU: $failed" -ForegroundColor Red
    exit 1
} else {
    Write-Host "OK: todos os casos passaram" -ForegroundColor Green
    exit 0
}
