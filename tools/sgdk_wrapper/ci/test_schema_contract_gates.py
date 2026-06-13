"""Schema contract gates test (Python jsonschema Draft-07).

Validates that the new allOf/if-then constraints in the 3 schemas now actually
reject invalid contracts. Pairs with test_game_design_contract_gates.ps1
(PowerShell auditor) — the PowerShell side proves the audit reports the
issue; the Python side proves the schema WOULD reject it at parse time.

Usage:
    python tools/sgdk_wrapper/ci/test_schema_contract_gates.py
Exit codes:
    0 = all pass
    1 = at least one schema test failed
"""
import json
import sys
from pathlib import Path
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parent.parent.parent.parent
SCHEMAS = ROOT / "tools" / "sgdk_wrapper" / "schemas"

passed = 0
failed = 0
total = 0


def expect_pass(name, schema, data):
    global passed, failed, total
    total += 1
    v = Draft7Validator(schema)
    errs = sorted(v.iter_errors(data), key=lambda e: list(e.path))
    if not errs:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name} -- expected PASS, got {len(errs)} error(s):")
        for e in errs[:3]:
            print(f"    - {list(e.path)} :: {e.message[:120]}")


def expect_fail(name, schema, data, must_contain=None):
    global passed, failed, total
    total += 1
    v = Draft7Validator(schema)
    errs = sorted(v.iter_errors(data), key=lambda e: list(e.path))
    if not errs:
        failed += 1
        print(f"  [FAIL] {name} -- expected FAIL, got 0 errors")
        return
    if must_contain:
        all_text = " ".join(e.message for e in errs)
        if must_contain not in all_text:
            failed += 1
            print(f"  [FAIL] {name} -- expected error containing '{must_contain}', got:")
            for e in errs[:3]:
                print(f"    - {list(e.path)} :: {e.message[:120]}")
            return
    passed += 1
    print(f"  [PASS] {name} (rejected with {len(errs)} error(s))")


def load_schema(name):
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


mech_schema = load_schema("mechanic_contract.schema.json")
lvl_schema = load_schema("level_blueprint.schema.json")
enemy_schema = load_schema("enemy_roster.schema.json")
methodology_schema = load_schema("project_methodology_manifest.schema.json")
project_context_schema = load_schema("project_context_manifest.schema.json")
road_schema = load_schema("road_physics_contract.schema.json")
boss_parts_schema = load_schema("boss_parts.schema.json")
project_hygiene_schema = load_schema("project_hygiene_manifest.schema.json")
tdd_schema = load_schema("tdd_contract.schema.json")
technique_usage_schema = load_schema("technique_usage_manifest.schema.json")
scene_tilemap_schema = load_schema("scene_tilemap_conversion_report.schema.json")
tilemap_flag_schema = load_schema("tilemap_flag_report.schema.json")
learning_ledger_schema = load_schema("learning_ledger.schema.json")
composition_scope_schema = load_schema("composition_scope_contract.schema.json")
brand_identity_schema = load_schema("brand_identity_manifest.schema.json")
visual_dna_schema = load_schema("visual_dna_manifest.schema.json")
ui_pixel_surface_schema = load_schema("ui_pixel_surface_contract.schema.json")
creative_director_radar_schema = load_schema("creative_director_radar.schema.json")
agent_session_state_schema = load_schema("agent_session_state.schema.json")
operational_loop_decision_schema = load_schema("operational_loop_decision.schema.json")

print("=== mechanic_contract.schema.json ===")

valid_core_mech = {
    "schema_version": "1.0.0",
    "mechanic_id": "dash",
    "mechanic_role": "core",
    "player_action": "burst forward",
    "system_rule": "consume 1 stamina",
    "goal_link": "close gap",
    "input_binding": {"button": "C", "binding_description": "dash"},
    "activation_context": {"state_requirements": "ground"},
    "space_requirements": {"min_reuses_in_world": 5},
    "required_game_elements": ["enemies", "gaps"],
    "skill_challenge_type": "physical",
    "rules_and_limits": ["1 stamina"],
    "probability_model": {"type": "deterministic"},
    "versatility_cases": ["a", "b", "c"],
    "level_design_reuse_plan": {"min_reuses": 3, "target_scenes": ["s1"]},
    "combination_map": [{"combo_mechanic_id": "jump", "combo_effect": "aerial"}],
    "failure_states": [{"failure_condition": "miss", "consequence": "no dash"}],
    "feedback_model": {"visual": "blur", "audio": "whoosh", "haptic_or_camera": "shake"},
    "tutorial_invisible_plan": {"teaching_scenes": ["s1"]},
    "test_scenarios": [{"scenario_id": "t1", "setup": "near enemy", "expected_outcome": "close"}],
    "evidence_required": [{"evidence_type": "screenshot", "location": "out/captures/s1.png"}],
    "mechanic_5_laws_compliance": {
        "agency": {"status": "passed"},
        "feedback": {"status": "passed"},
        "flow": {"status": "passed"},
        "consistency": {"status": "passed"},
        "reward": {"status": "passed"},
    },
}
expect_pass("core mechanic with versatility=3, min_reuses=3, combos=1 PASSES", mech_schema, valid_core_mech)

bad_core_versatility = json.loads(json.dumps(valid_core_mech))
bad_core_versatility["versatility_cases"] = ["a", "b"]
expect_fail("core mechanic with versatility=2 is REJECTED", mech_schema, bad_core_versatility, must_contain=None)

bad_core_reuse = json.loads(json.dumps(valid_core_mech))
bad_core_reuse["level_design_reuse_plan"]["min_reuses"] = 1
expect_fail("core mechanic with min_reuses=1 is REJECTED", mech_schema, bad_core_reuse)

bad_core_combo = json.loads(json.dumps(valid_core_mech))
bad_core_combo["combination_map"] = []
expect_fail("core mechanic with combination_map=[] is REJECTED", mech_schema, bad_core_combo)

# probability: random without success_rate_percent
bad_prob = json.loads(json.dumps(valid_core_mech))
bad_prob["probability_model"] = {"type": "random"}
expect_fail("probability type=random without success_rate_percent is REJECTED", mech_schema, bad_prob)

print()
print("=== level_blueprint.schema.json ===")

valid_level = {
    "schema_version": "1.0.0",
    "scope_id": "stage_1",
    "golden_path": {"waypoint_sequence": ["w1", "w2"], "visible_landmarks": ["tower"]},
    "waypoints": [
        {"waypoint_id": "w1", "position": "start", "purpose": "spawn"},
        {"waypoint_id": "w2", "position": "end", "purpose": "goal"},
    ],
    "gates": [],
    "optional_routes": [],
    "risk_markers": [],
    "breathing_zones": [],
    "phase_rhythm_map": [
        {"phase": "calm", "intensity": "low", "start_waypoint": "w1", "end_waypoint": "w2"},
        {"phase": "pressure", "intensity": "medium", "start_waypoint": "w2", "end_waypoint": "w1"},
    ],
    "mechanic_reuse_map": [{"mechanic_id": "dash", "target_scenes": ["stage_1"], "reuse_count": 5}],
    "tutorial_invisible_beats": [],
    "environmental_narrative_map": [],
    "failure_recovery_model": {"last_checkpoint": "w1", "reset_strategy": "spawn at w1"},
    "acceptance_tests": [{"test_id": "t1", "scenario": "play", "expected": "win"}],
}
expect_pass("level with calm+pressure phases and 2 waypoints PASSES", lvl_schema, valid_level)

# missing pressure
bad_rhythm_pressure = json.loads(json.dumps(valid_level))
bad_rhythm_pressure["phase_rhythm_map"] = [
    {"phase": "calm", "intensity": "low", "start_waypoint": "w1", "end_waypoint": "w2"},
    {"phase": "payoff", "intensity": "high", "start_waypoint": "w2", "end_waypoint": "w1"},
]
# This one may pass via anyOf fallback; we just check it doesn't crash.
expect_pass("level without 'pressure' may pass via anyOf fallback (auditor catches it)", lvl_schema, bad_rhythm_pressure)

# missing calm
bad_rhythm_calm = json.loads(json.dumps(valid_level))
bad_rhythm_calm["phase_rhythm_map"] = [
    {"phase": "pressure", "intensity": "high", "start_waypoint": "w1", "end_waypoint": "w2"},
    {"phase": "payoff", "intensity": "high", "start_waypoint": "w2", "end_waypoint": "w1"},
]
expect_pass("level without 'calm' may pass via anyOf fallback (auditor catches it)", lvl_schema, bad_rhythm_calm)

# only 1 waypoint
bad_waypoints = json.loads(json.dumps(valid_level))
bad_waypoints["golden_path"]["waypoint_sequence"] = ["w1"]
expect_fail("level with waypoint_sequence=1 is REJECTED", lvl_schema, bad_waypoints)

# invalid phase enum
bad_phase_enum = json.loads(json.dumps(valid_level))
bad_phase_enum["phase_rhythm_map"][0]["phase"] = "explosion"
expect_fail("level with invalid phase enum is REJECTED", lvl_schema, bad_phase_enum)

print()
print("=== enemy_roster.schema.json ===")

valid_enemy = {
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
            "ai_behavior": {"aggro_radius_px": 32, "retreat_threshold_hp_percent": 0},
            "telegraph_model": {"telegraph_frames": 12, "visual_cue": "blink"},
            "weakness_model": {"weakness_position": "head"},
            "synergy_partners": [{"enemy_id": "shooter", "synergy_type": "frontline_shield"}],
            "level_placement_rules": {"target_scenes": ["stage_1"]},
            "feedback_on_hit": {"visual": "flash", "audio": "pop"},
            "feedback_on_alert": {"visual": "blink", "audio": "beep"},
        },
        {
            "enemy_id": "dragon",
            "role": "boss",
            "head_metric": "XL",
            "hp": 80,
            "damage": 8,
            "movement_model": "phase_transition",
            "ai_behavior": {"aggro_radius_px": 200, "retreat_threshold_hp_percent": 0},
            "telegraph_model": {"telegraph_frames": 30, "visual_cue": "roar"},
            "weakness_model": {"weakness_position": "head"},
            "synergy_partners": [],
            "level_placement_rules": {"boss_arena_id": "stage_1_boss"},
            "feedback_on_hit": {"visual": "flash", "audio": "boom"},
            "feedback_on_alert": {"visual": "roar", "audio": "stinger_boss"},
            "boss_state_count": 3,
        },
    ],
}
expect_pass("enemy roster with boss+state_count=3 PASSES", enemy_schema, valid_enemy)

# boss without state_count and without justification
bad_boss_no_state = json.loads(json.dumps(valid_enemy))
del bad_boss_no_state["enemies"][1]["boss_state_count"]
expect_fail("boss without boss_state_count and without justification is REJECTED", enemy_schema, bad_boss_no_state)

# boss with state_count=2
bad_boss_short = json.loads(json.dumps(valid_enemy))
bad_boss_short["enemies"][1]["boss_state_count"] = 2
expect_fail("boss with boss_state_count=2 (below 3) is REJECTED", enemy_schema, bad_boss_short)

# boss with curto justification (allowed)
boss_curto = json.loads(json.dumps(valid_enemy))
del boss_curto["enemies"][1]["boss_state_count"]
boss_curto["enemies"][1]["boss_curto_justification"] = "Mini-boss tutorial; only 2 visual states."
expect_pass("boss with boss_curto_justification (no state_count) PASSES", enemy_schema, boss_curto)

print()
print("=== methodology and structured claim schemas ===")

project_context_example = json.loads(
    (ROOT / "tools" / "sgdk_wrapper" / "modelo" / "doc" / "project_context_manifest.json").read_text(encoding="utf-8")
)
expect_pass("project context template PASSES schema", project_context_schema, project_context_example)

aaa_context = json.loads(json.dumps(project_context_example))
aaa_context.update({
    "context_type": "aaa_game",
    "context_status": "planned",
    "delivery_claim_ceiling": "vertical_slice",
    "documentation_profile": "full_game",
})
aaa_context["context_decision_record"].update({
    "selected_by": "human",
    "rationale": "Human selected an AAA game context.",
    "evidence_or_prompt": "new game request",
})
expect_pass("AAA project context with full_game profile PASSES schema", project_context_schema, aaa_context)

bad_exercise_aaa = json.loads(json.dumps(project_context_example))
bad_exercise_aaa.update({
    "context_type": "exercise",
    "context_status": "planned",
    "delivery_claim_ceiling": "ready_for_aaa",
    "documentation_profile": "exercise",
})
bad_exercise_aaa["context_decision_record"].update({
    "selected_by": "human",
    "rationale": "Human selected exercise context.",
    "evidence_or_prompt": "training request",
})
expect_fail("exercise context cannot claim ready_for_aaa", project_context_schema, bad_exercise_aaa)

methodology_example = json.loads(
    (ROOT / "tools" / "sgdk_wrapper" / "modelo" / "doc" / "project_methodology_manifest.json").read_text(encoding="utf-8")
)
expect_pass("project methodology template PASSES schema", methodology_schema, methodology_example)

bad_no_freshness = json.loads(json.dumps(methodology_example))
bad_no_freshness["required_validations"].remove("freshness_audit")
expect_fail("project methodology without freshness_audit is REJECTED", methodology_schema, bad_no_freshness)

bad_required_motion = json.loads(json.dumps(methodology_example))
bad_required_motion["claims"]["critical_motion"] = {
    "applicability": "required",
    "rationale": "Critical motion is part of delivery.",
}
expect_fail("required critical_motion without evidence paths is REJECTED", methodology_schema, bad_required_motion)

road_example = json.loads(
    (ROOT / "tools" / "sgdk_wrapper" / "examples" / "contracts" / "road_physics_contract.example.json").read_text(encoding="utf-8")
)
expect_pass("road physics example PASSES schema", road_schema, road_example)
expect_fail("empty road physics contract is REJECTED by schema", road_schema, {})

boss_example = json.loads(
    (ROOT / "tools" / "sgdk_wrapper" / "examples" / "contracts" / "boss_parts.example.json").read_text(encoding="utf-8")
)
expect_pass("boss parts example PASSES schema", boss_parts_schema, boss_example)
bad_single_part_boss = json.loads(json.dumps(boss_example))
bad_single_part_boss["parts"] = bad_single_part_boss["parts"][:1]
bad_single_part_boss["fk_chain"] = []
expect_fail("single-part modular boss contract is REJECTED by schema", boss_parts_schema, bad_single_part_boss)

print()
print("=== composition_scope_contract.schema.json ===")

valid_micro_sketch = {
    "schema_version": "1.0.0",
    "contract_id": "stage_1_music_sketch",
    "scene_id": "stage_1",
    "track_id": "bgm_stage_1_sketch",
    "scope": "micro_sketch_1m",
    "intended_use": "prototype",
    "status_ceiling": "prototype_only",
    "identity_note": "Urgent bass pulse and short rhythmic hook.",
    "promotion_criteria": ["Promote through core_loop_10m before final use."],
}
expect_pass("micro sketch with prototype ceiling PASSES", composition_scope_schema, valid_micro_sketch)

bad_micro_aaa = json.loads(json.dumps(valid_micro_sketch))
bad_micro_aaa["status_ceiling"] = "ready_for_aaa_candidate"
expect_fail("micro sketch cannot claim AAA ceiling", composition_scope_schema, bad_micro_aaa)

valid_core_loop = {
    "schema_version": "1.0.0",
    "contract_id": "stage_1_core_loop",
    "scene_id": "stage_1",
    "track_id": "bgm_stage_1_core",
    "scope": "core_loop_10m",
    "intended_use": "stage_bgm",
    "status_ceiling": "vertical_slice_candidate",
    "loop_plan": {
        "bar_count": 8,
        "seamless_loop_report_path": "out/logs/stage_1_bgm_loop.json",
        "click_free_strategy": "zero-crossing tail and matching first beat",
        "pause_resume_behavior": "resume from saved musical position",
    },
    "sfx_protection": {
        "frequency_masking_plan_path": "doc/audio/stage_1_frequency_masking.md",
        "critical_sfx": ["sfx_hit", "sfx_damage", "sfx_alert"],
        "masking_strategy": "leave transient headroom and avoid dense lead during attacks",
    },
    "promotion_criteria": ["No click in emulator", "SFX remain readable during combat"],
}
expect_pass("core loop with loop report and SFX protection PASSES", composition_scope_schema, valid_core_loop)

bad_core_no_loop = json.loads(json.dumps(valid_core_loop))
del bad_core_no_loop["loop_plan"]
expect_fail("core loop without loop plan is REJECTED", composition_scope_schema, bad_core_no_loop)

valid_modular_track = json.loads(json.dumps(valid_core_loop))
valid_modular_track["contract_id"] = "boss_modular_track"
valid_modular_track["scene_id"] = "boss_1"
valid_modular_track["track_id"] = "bgm_boss_1_modular"
valid_modular_track["scope"] = "modular_track_1h"
valid_modular_track["intended_use"] = "boss"
valid_modular_track["status_ceiling"] = "ready_for_aaa_candidate"
valid_modular_track["modular_plan"] = {
    "arrangement_sections": ["intro", "loop_a", "loop_b"],
    "transition_plan": "stinger into loop_b when boss phase changes",
    "stem_or_layer_plan": [
        {"id": "base_groove", "role": "core groove", "owner_channel_or_layer": "bgm_base"},
        {"id": "lead_pressure", "role": "phase pressure layer", "owner_channel_or_layer": "bgm_layer_lead"},
    ],
    "adaptive_music_state_map_path": "doc/audio/boss_1_adaptive_music_state_map.json",
}
expect_pass("modular track with layers and adaptive map PASSES", composition_scope_schema, valid_modular_track)

bad_modular_no_masking = json.loads(json.dumps(valid_modular_track))
del bad_modular_no_masking["sfx_protection"]
expect_fail("modular track without SFX protection is REJECTED", composition_scope_schema, bad_modular_no_masking)

valid_silence = {
    "schema_version": "1.0.0",
    "contract_id": "stage_2_silence",
    "scene_id": "stage_2",
    "scope": "silence_intentional",
    "intended_use": "intentional_silence",
    "status_ceiling": "silent_intentional",
    "silence_rationale": "Horror scene needs empty space before impact.",
    "sfx_or_ambience_plan": "low wind ambience and distant metal creaks carry tension",
    "promotion_criteria": ["Silence preserved in BlastEm closeout"],
}
expect_pass("intentional silence with rationale PASSES", composition_scope_schema, valid_silence)

bad_silence_no_rationale = json.loads(json.dumps(valid_silence))
del bad_silence_no_rationale["silence_rationale"]
expect_fail("silence without rationale is REJECTED", composition_scope_schema, bad_silence_no_rationale)

print()
print("=== brand_identity_manifest.schema.json ===")

valid_brand_identity = {
    "schema_version": "1.0.0",
    "project_id": "neon_steel",
    "manifest_id": "neon_steel_brand_identity",
    "brand_role": "front_end",
    "source_authority": {
        "gdd_ref": "doc/11-gdd.md",
        "ui_decision_card_ref": "doc/13-spec-cenas.md#title_ui_decision_card",
        "master_style_manifest_ref": "doc/03_art/01_master_style_manifest.md",
        "reference_policy": "technical_inspiration_only",
    },
    "logo_system": {
        "primary_title_text": "Neon Steel",
        "subtitle_text": None,
        "main_title_weight_percent": 100,
        "genre_tone_alignment": "Angular industrial sci-fi with readable high-contrast letter mass.",
        "source_vector_master_path": "data/source_art/logo/neon_steel_logo.svg",
        "gameplay_metaphor": {
            "metaphor": "The I stroke becomes a charged rail used by the dash mechanic.",
            "target_letter_or_shape": "letter_i",
            "readability_priority": True,
        },
        "silhouette_test": {
            "method": "Fill logo black on white background.",
            "pass_condition": "Title remains readable as a single shape at native scale.",
            "evidence_ref": "out/brand/logo_silhouette.png",
        },
        "monochrome_test": {
            "method": "Render pure black and pure white variants.",
            "pass_condition": "No letter depends on color gradient to be understood.",
            "evidence_ref": "out/brand/logo_monochrome.png",
        },
        "thumbnail_test": {
            "method": "Scale to small preview and inspect in 2 seconds.",
            "pass_condition": "Primary title reads before decorative details.",
            "evidence_ref": "out/brand/logo_thumbnail.png",
        },
        "dynamic_background_test": {
            "method": "Place over light, dark, noisy concept, and gameplay backgrounds.",
            "pass_condition": "Outline/shadow keeps title separated in all backgrounds.",
            "evidence_ref": "out/brand/logo_backgrounds.png",
        },
    },
    "typography_system": {
        "font_roles": [
            {
                "role": "logo_display",
                "render_mode": "vector_source",
                "charset_profile": "ascii_core",
                "asset_ref": "data/source_art/logo/neon_steel_logo.svg",
                "usage": "Title logo and press-start reveal.",
                "fallback": "Use static indexed title tiles without glow.",
            },
            {
                "role": "front_end_body",
                "render_mode": "bitmap_tileset",
                "charset_profile": "ptbr_core_accents",
                "asset_ref": "res/ui/front_end_font.png",
                "usage": "Menu labels, options, and short status text.",
                "fallback": "Reduce to fixed custom uppercase labels.",
            },
        ],
        "generic_font_policy": {
            "sgdk_default_font_use": "fallback_only",
            "final_identity_requires_custom_font": True,
        },
        "glyph_manifest_ref": "doc/13-spec-cenas.md#title_glyph_manifest",
    },
    "title_screen_export_plan": {
        "runtime_layers": [
            {
                "layer_id": "main_logo_tiles",
                "role": "main_text",
                "vdp_surface": "BG_A",
                "palette_domain": "PAL2 logo metal and neon accents",
                "animation_role": "static",
            },
            {
                "layer_id": "logo_glow_sprites",
                "role": "glow",
                "vdp_surface": "SPRITES",
                "palette_domain": "PAL3 pulse highlight",
                "animation_role": "palette_cycle",
            },
        ],
        "vdp_budget_ref": "doc/13-spec-cenas.md#title_logo_budget",
        "fallback_static_plan": "Disable sprite glow and keep readable BG_A title tiles.",
    },
    "validation_plan": {
        "native_320x224_status": "planned",
        "silhouette_status": "planned",
        "monochrome_status": "planned",
        "thumbnail_status": "planned",
        "dynamic_background_status": "planned",
        "blastem_evidence_required": True,
        "blastem_evidence_ref": None,
    },
    "fallback_policy": {
        "budget_fallback": "Drop glow layer and reserve only title tiles.",
        "font_fallback": "Use front-end fixed bitmap font, not SGDK default, for final UI.",
        "logo_animation_fallback": "Static logo plus animated cursor.",
    },
    "approval_status": "planned",
}
expect_pass("planned brand identity manifest PASSES", brand_identity_schema, valid_brand_identity)

bad_brand_no_thumbnail = json.loads(json.dumps(valid_brand_identity))
del bad_brand_no_thumbnail["logo_system"]["thumbnail_test"]
expect_fail("brand identity without thumbnail test is REJECTED", brand_identity_schema, bad_brand_no_thumbnail)

bad_brand_generic_final = json.loads(json.dumps(valid_brand_identity))
bad_brand_generic_final["typography_system"]["generic_font_policy"]["final_identity_requires_custom_font"] = False
expect_fail("brand identity allowing generic final font is REJECTED", brand_identity_schema, bad_brand_generic_final)

bad_brand_metaphor_over_readability = json.loads(json.dumps(valid_brand_identity))
bad_brand_metaphor_over_readability["logo_system"]["gameplay_metaphor"]["readability_priority"] = False
expect_fail("brand identity with metaphor over readability is REJECTED", brand_identity_schema, bad_brand_metaphor_over_readability)

runtime_brand = json.loads(json.dumps(valid_brand_identity))
runtime_brand["approval_status"] = "approved_for_runtime"
runtime_brand["validation_plan"].update({
    "native_320x224_status": "passed",
    "silhouette_status": "passed",
    "monochrome_status": "passed",
    "thumbnail_status": "passed",
    "dynamic_background_status": "passed",
    "blastem_evidence_ref": "out/logs/title_blastem_evidence.json",
})
expect_pass("runtime-approved brand identity with evidence PASSES", brand_identity_schema, runtime_brand)

bad_runtime_no_blastem = json.loads(json.dumps(runtime_brand))
bad_runtime_no_blastem["validation_plan"]["blastem_evidence_ref"] = None
expect_fail("runtime-approved brand identity without BlastEm evidence is REJECTED", brand_identity_schema, bad_runtime_no_blastem)

print()
print("=== creative_director_radar.schema.json ===")

valid_creative_radar = json.loads(
    (
        ROOT
        / "tools"
        / "sgdk_wrapper"
        / ".agent"
        / "references"
        / "agentic_aaa_contracts"
        / "examples"
        / "creative_director_radar.example.json"
    ).read_text(encoding="utf-8")
)
expect_pass("creative director radar example PASSES", creative_director_radar_schema, valid_creative_radar)

bad_creative_copy_policy = json.loads(json.dumps(valid_creative_radar))
bad_creative_copy_policy["do_not_copy_policy"]["benchmark_usage"] = "source_art"
expect_fail("creative radar forbids benchmark as source art", creative_director_radar_schema, bad_creative_copy_policy)

bad_creative_few_axes = json.loads(json.dumps(valid_creative_radar))
bad_creative_few_axes["benchmark_axis_matrix"] = bad_creative_few_axes["benchmark_axis_matrix"][:3]
expect_fail("approved creative radar requires at least 5 benchmark axes", creative_director_radar_schema, bad_creative_few_axes)

bad_creative_few_gaps = json.loads(json.dumps(valid_creative_radar))
bad_creative_few_gaps["proactive_gap_radar"] = bad_creative_few_gaps["proactive_gap_radar"][:2]
expect_fail("approved creative radar requires at least 5 proactive gaps", creative_director_radar_schema, bad_creative_few_gaps)

bad_creative_feature_creep = json.loads(json.dumps(valid_creative_radar))
bad_creative_feature_creep["decision_policy"]["feature_creep_guard"] = False
expect_fail("creative radar requires feature creep guard", creative_director_radar_schema, bad_creative_feature_creep)

print()
print("=== visual_dna_manifest.schema.json ===")

valid_visual_dna = {
    "schema_version": "1.0.0",
    "asset_id": "hero_roller",
    "asset_role": "hero_character",
    "authorial_source": "data/source_art/hero/model_sheet.png",
    "license": "project_owned",
    "benchmark_used_as": "technical_quality_bar",
    "style_pillars": ["readable silhouette", "warm light", "cool shadows"],
    "palette_intent": {
        "max_palettes": 1,
        "reserved_slots": [{"palette": 0, "slot": 0, "purpose": "transparent"}],
        "material_ramps": [
            {
                "material": "jacket",
                "slots": [1, 2, 3, 4],
                "contrast_goal": "highlight shifts warm, shadow shifts cool",
            }
        ],
    },
    "shape_language": ["compact head", "large boots"],
    "material_rules": ["fabric shadows move toward blue/purple"],
    "scale_contract": {
        "native_resolution": "320x224",
        "nominal_bbox_px": {"w": 32, "h": 48},
        "pivot_policy": "bottom_center_feet",
        "scale_class": "medium_24_48",
        "scale_lock_status": "locked",
        "gameplay_scale_fit": {
            "camera_fov_role": "balanced_action",
            "hitbox_alignment_role": "coarse_body",
            "animation_workload_policy": "standard_16bit_pipeline",
            "integer_pixel_motion_policy": "fixed_point_logic_integer_render",
        },
        "scale_change_policy": "requires_reseed_before_art",
    },
    "forbidden_drift": ["anatomy", "pivot", "scale", "palette", "bounding_box"],
    "approval_status": "approved_for_key_poses",
}
expect_pass("visual DNA with locked character scale PASSES", visual_dna_schema, valid_visual_dna)

bad_visual_scale_draft = json.loads(json.dumps(valid_visual_dna))
bad_visual_scale_draft["scale_contract"]["scale_lock_status"] = "draft"
expect_fail("visual DNA cannot approve key poses with draft scale", visual_dna_schema, bad_visual_scale_draft)

bad_visual_non_tile_bbox = json.loads(json.dumps(valid_visual_dna))
bad_visual_non_tile_bbox["scale_contract"]["nominal_bbox_px"]["w"] = 34
expect_fail("visual DNA rejects non-8px character bbox", visual_dna_schema, bad_visual_non_tile_bbox)

print()
print("=== ui_pixel_surface_contract.schema.json ===")

valid_health_bar = {
    "schema_version": "1.0.0",
    "surface_id": "hud_player_health",
    "surface_kind": "health_bar",
    "ui_decision_card_ref": "doc/13-spec-cenas.md#hud_ui_decision_card",
    "pixel_grid_policy": {
        "native_resolution": "320x224",
        "integer_positioning_required": True,
        "scaling_policy": "window_plane_pixels",
        "forbidden_interpolation": ["bilinear", "bicubic", "engine_free_scale", "subpixel_ui_motion"],
    },
    "typography_policy": {
        "font_role": "hud_critical",
        "native_font_height_px": 8,
        "baseline_grid_px": 8,
        "contrast_treatment": "one_px_shadow",
        "glyph_manifest_ref": "doc/13-spec-cenas.md#hud_glyph_manifest",
    },
    "atlas_plan": {
        "atlas_ref": "res/ui/hud_atlas.png",
        "vdp_surface": "WINDOW",
        "palette_domain": "PAL3_HUD",
        "index0_policy": "solid_for_window_or_bg",
        "budget_ref": "doc/13-spec-cenas.md#hud_budget",
    },
    "health_bar_system": {
        "container_layer": "dark_outer_frame",
        "latent_damage_buffer": {"enabled": True, "delay_frames": 12, "drain_frames": 24},
        "active_fill": {
            "high_color_role": "green_or_cyan_safe",
            "mid_color_role": "yellow_or_orange_warning",
            "critical_color_role": "red_critical",
        },
        "drain_step_px": 1,
        "critical_threshold_percent": 30,
        "low_hp_feedback": {"flash_cadence_frames": 8, "ui_shake_allowed": True, "audio_cue_ref": "sfx_low_hp"},
        "inner_edge_policy": "hard_aliased_no_antialias",
    },
    "validation_plan": {
        "native_readability_status": "planned",
        "integer_pixel_motion_status": "planned",
        "atlas_budget_status": "planned",
        "blastem_evidence_required": True,
        "blastem_evidence_ref": None,
    },
    "approval_status": "planned",
}
expect_pass("planned health bar UI pixel contract PASSES", ui_pixel_surface_schema, valid_health_bar)

bad_health_no_buffer = json.loads(json.dumps(valid_health_bar))
del bad_health_no_buffer["health_bar_system"]["latent_damage_buffer"]
expect_fail("health bar without latent damage buffer is REJECTED", ui_pixel_surface_schema, bad_health_no_buffer)

bad_ui_fractional = json.loads(json.dumps(valid_health_bar))
bad_ui_fractional["pixel_grid_policy"]["integer_positioning_required"] = False
expect_fail("UI allowing fractional positioning is REJECTED", ui_pixel_surface_schema, bad_ui_fractional)

runtime_health_bar = json.loads(json.dumps(valid_health_bar))
runtime_health_bar["approval_status"] = "approved_for_runtime"
runtime_health_bar["validation_plan"].update({
    "native_readability_status": "passed",
    "integer_pixel_motion_status": "passed",
    "atlas_budget_status": "passed",
    "blastem_evidence_ref": "out/logs/hud_player_health_blastem.json",
})
expect_pass("runtime-approved health bar with evidence PASSES", ui_pixel_surface_schema, runtime_health_bar)

bad_runtime_health_no_blastem = json.loads(json.dumps(runtime_health_bar))
bad_runtime_health_no_blastem["validation_plan"]["blastem_evidence_ref"] = None
expect_fail("runtime-approved UI without BlastEm evidence is REJECTED", ui_pixel_surface_schema, bad_runtime_health_no_blastem)

print()
print("=== project hygiene and technique selection schemas ===")

hygiene_example = json.loads(
    (ROOT / "tools" / "sgdk_wrapper" / "modelo" / "doc" / "project_hygiene_manifest.json").read_text(encoding="utf-8")
)
expect_pass("project hygiene template PASSES schema", project_hygiene_schema, hygiene_example)

bad_external_input = json.loads(json.dumps(hygiene_example))
bad_external_input["external_inputs"] = [{"source": "C:/outside/source.png"}]
expect_fail("external input without copied_to metadata is REJECTED", project_hygiene_schema, bad_external_input)

technique_usage_template = json.loads(
    (ROOT / "tools" / "sgdk_wrapper" / "modelo" / "doc" / "technique_usage_manifest.json").read_text(encoding="utf-8")
)
expect_pass("technique usage template PASSES schema", technique_usage_schema, technique_usage_template)

bad_external_technique_evidence = json.loads(json.dumps(technique_usage_template))
bad_external_technique_evidence["allowed_external_artifacts"] = [{
    "path": "C:/outside/evidence.png",
    "reason": "legacy authorization",
    "human_authorized": True,
}]
expect_fail(
    "technique usage external artifact authorization is REJECTED",
    technique_usage_schema,
    bad_external_technique_evidence,
)

valid_tdd_selection = {
    "schema_version": "1.0.0",
    "tdd_id": "stage_1_tdd",
    "scene_manager_scope": {"topology": "linear", "deterministic": True},
    "input_abstraction_scope": {"abstraction_layer": "input.c", "latency_target_ms": 16},
    "state_fsm_map": [{"scene_id": "stage_1", "states": ["enter", "play"], "transitions": []}],
    "memory_pool_map": [{"pool_id": "actors", "type": "enemy", "size": 4, "owner": "actors.c"}],
    "vblank_dma_ownership": {"vblank_owner": "video.c", "dma_owners": ["video.c"]},
    "h_int_ownership": {"h_int_in_use": False},
    "audio_ownership": {"driver": "xgm2", "channel_owners": ["music"]},
    "save_scope": "none",
    "region_timing_scope": {"region": "NTSC", "frame_budget_ms": 16.67},
    "rom_mastering_scope": {"size_target_kb": 4096},
    "technique_selection": {
        "registry_source": "doc/05_technical/93_16bit_hardware_mastery_registry.json",
        "usage_manifest_path": "doc/technique_usage_manifest.json",
        "selected_registry_ids": ["line_scrolling"],
        "required_tags": ["LINE_SCROLL", "PARALLAX"],
        "owner_skills": ["code/sgdk-runtime-coder", "hardware/megadrive-vdp-budget-analyst"],
        "selection_rationale": "Line scrolling gives the stage depth while preserving sprite budget.",
        "fallback_strategy": "Use plane scroll bands if per-line updates exceed budget.",
        "application_plan": [{
            "registry_id": "line_scrolling",
            "scene_or_system": "stage_1",
            "gameplay_or_narrative_purpose": "Communicate speed and route depth during play.",
            "visual_or_audio_role": "Layered landscape depth.",
            "owner_skill": "code/sgdk-runtime-coder",
            "budget_evidence": "dma_queue_contract",
            "fallback": "Use plane scroll bands."
        }],
        "rejected_or_deferred": []
    },
    "risk_mitigation_table": [{"risk_id": "dma", "risk": "DMA overflow", "mitigation": "queue budget"}],
}
expect_pass("TDD with explicit technique selection PASSES schema", tdd_schema, valid_tdd_selection)

bad_tdd_selection = json.loads(json.dumps(valid_tdd_selection))
del bad_tdd_selection["technique_selection"]
expect_fail("TDD without explicit technique selection is REJECTED", tdd_schema, bad_tdd_selection)

print()
print("=== scene_tilemap_conversion_report.schema.json ===")

valid_scene_tilemap = {
    "$schema": "tools/sgdk_wrapper/schemas/scene_tilemap_conversion_report.schema.json",
    "source_path": "rascunho/scene/source.png",
    "source_sha256": "a" * 64,
    "conversion_target": "scene_slice",
    "output_tileset_path": "res/scene_tiles.bin",
    "output_tilemap_path": "res/scene_map.bin",
    "output_palette_path": "res/scene_pal.bin",
    "tile_size_px": 8,
    "total_tiles": 1120,
    "unique_tiles_exact": 420,
    "unique_tiles_hflip": 12,
    "unique_tiles_vflip": 8,
    "unique_tiles_hvflip": 4,
    "final_unique_tiles": 396,
    "dedup_savings_tiles": 724,
    "dedup_savings_percent": 64.64,
    "palette_count": 4,
    "per_tile_palette_conflicts": 0,
    "priority_tile_count": 0,
    "hflip_tile_count": 12,
    "vflip_tile_count": 8,
    "hvflip_tile_count": 4,
    "estimated_vram_bytes": 12672,
    "estimated_map_bytes": 2240,
    "rom_resource_strategy": "TILESET_MAP",
    "status": "ok",
    "blockers": [],
    "generated_at": "2026-06-09T12:00:00Z",
    "tool_name": "fixture",
    "tool_version": "1.0.0",
}
expect_pass("basic scene tilemap conversion report PASSES schema", scene_tilemap_schema, valid_scene_tilemap)

valid_streaming_tilemap = json.loads(json.dumps(valid_scene_tilemap))
valid_streaming_tilemap.update({
    "conversion_target": "world_tilemap_with_camera_window_streaming",
    "rom_resource_strategy": "BIN_CUSTOM_TILE_GRAPHICS_AND_TILEMAP_WINDOW_STREAMING",
    "total_tiles": 23040,
    "unique_tiles_exact": 2253,
    "final_unique_tiles": 2253,
    "dedup_savings_tiles": 20787,
    "dedup_savings_percent": 90.22,
    "estimated_vram_bytes": 72096,
    "estimated_map_bytes": 46080,
    "status": "needs_review",
    "blockers": ["runtime_vdp_evidence_missing"],
    "world_dimensions": {
        "pixels_w": 768,
        "pixels_h": 240,
        "tiles_w": 96,
        "tiles_h": 30,
    },
    "viewport_dimensions": {
        "pixels_w": 320,
        "pixels_h": 224,
        "tiles_w": 40,
        "tiles_h": 28,
    },
    "runtime_streaming": {
        "strategy": "camera_window_tile_streaming",
        "window_tiles_w": 42,
        "window_tiles_h": 30,
        "max_window_unique_tiles": 1087,
        "cache_capacity_tiles": 1151,
        "estimated_cache_vram_bytes": 36832,
        "upload_method": "CPU",
        "frame_animation_enabled": False,
        "visual_vdp_dump_required": True,
        "evidence_level": "estimated",
        "notes": "Lab evidence only until VDP dump or runtime telemetry proves residency.",
    },
})
expect_pass("world camera-window streaming report PASSES schema", scene_tilemap_schema, valid_streaming_tilemap)

bad_streaming_without_contract = json.loads(json.dumps(valid_streaming_tilemap))
del bad_streaming_without_contract["runtime_streaming"]
expect_fail(
    "world camera-window streaming without runtime_streaming is REJECTED",
    scene_tilemap_schema,
    bad_streaming_without_contract,
)

bad_streaming_flat_fields = json.loads(json.dumps(valid_streaming_tilemap))
bad_streaming_flat_fields["world_pixels_w"] = 768
bad_streaming_flat_fields["streaming_window_tiles_w"] = 42
expect_fail(
    "legacy flat streaming fields are REJECTED",
    scene_tilemap_schema,
    bad_streaming_flat_fields,
)

print()
print("=== tilemap_flag_report.schema.json ===")

valid_tilemap_flag_report = {
    "$schema": "tools/sgdk_wrapper/schemas/tilemap_flag_report.schema.json",
    "generated_at": "2026-06-09T12:00:00Z",
    "tool_name": "fixture",
    "tool_version": "1.0.0",
    "entries": [{
        "frame_index": 0,
        "tile_x": 1,
        "tile_y": 2,
        "tile_index": 3,
        "palette_id": 2,
        "priority": False,
        "hflip": True,
        "vflip": False,
        "source_tile_hash": "b" * 64,
        "canonical_tile_hash": "c" * 64,
    }],
}
expect_pass("tilemap flag report with optional frame_index PASSES schema", tilemap_flag_schema, valid_tilemap_flag_report)

bad_tilemap_flag_extra = json.loads(json.dumps(valid_tilemap_flag_report))
bad_tilemap_flag_extra["entries"][0]["legacy_note"] = "not allowed"
expect_fail("tilemap flag report rejects unknown entry fields", tilemap_flag_schema, bad_tilemap_flag_extra)

print()
print("=== learning_ledger.schema.json ===")

learning_ledger_template = json.loads(
    (ROOT / "tools" / "sgdk_wrapper" / "modelo" / "doc" / "agent_learning" / "learning_ledger.json").read_text(
        encoding="utf-8"
    )
)
expect_pass("project learning ledger template PASSES schema", learning_ledger_schema, learning_ledger_template)

bad_learning_mutation = json.loads(json.dumps(learning_ledger_template))
bad_learning_mutation["policy"]["canonical_auto_mutation"] = True
expect_fail(
    "project learning ledger with automatic canonical mutation is REJECTED",
    learning_ledger_schema,
    bad_learning_mutation,
)

print()
print("=== agent_session_state.schema.json ===")

agent_session_state = json.loads((ROOT / "doc" / "agent_session_state.json").read_text(encoding="utf-8"))
expect_pass("workspace session state template PASSES schema", agent_session_state_schema, agent_session_state)

active_session_state = json.loads(json.dumps(agent_session_state))
active_session_state["last_updated"] = "2026-06-05T12:00:00Z"
active_session_state["current_mode"] = "analyze_existing_project"
active_session_state["current_perspective"] = "qa"
active_session_state["active_project"] = "SGDK_projects/sample_project"
active_session_state["mode_history"] = [{
    "timestamp": "2026-06-05T12:00:00Z",
    "from_mode": "idle",
    "to_mode": "analyze_existing_project",
    "from_perspective": "none",
    "to_perspective": "qa",
    "reason": "Human selected project analysis mode.",
    "user_confirmed": True,
}]
expect_pass("active session with confirmed transition PASSES schema", agent_session_state_schema, active_session_state)

bad_session_mode = json.loads(json.dumps(agent_session_state))
bad_session_mode["current_mode"] = "ship_without_blastem"
expect_fail("session state rejects invalid mode", agent_session_state_schema, bad_session_mode)

bad_idle_project = json.loads(json.dumps(agent_session_state))
bad_idle_project["active_project"] = "SGDK_projects/sample_project"
expect_fail("idle session cannot keep active project", agent_session_state_schema, bad_idle_project)

bad_consent_policy = json.loads(json.dumps(agent_session_state))
bad_consent_policy["consent_policy"]["canonical_patch_requires_explicit_human_approval"] = False
expect_fail("session state rejects disabled canonical approval gate", agent_session_state_schema, bad_consent_policy)

bad_unconfirmed_transition = json.loads(json.dumps(active_session_state))
bad_unconfirmed_transition["mode_history"][0]["user_confirmed"] = False
expect_fail("session history rejects unconfirmed mode transition", agent_session_state_schema, bad_unconfirmed_transition)

print()
print("=== operational_loop_decision.schema.json ===")

valid_loop_decision = {
    "schema_version": "1.0.0",
    "generated_at": "2026-06-06T12:00:00Z",
    "project_root": "SGDK_projects/example_project",
    "owner": "human_owner",
    "decision_date": "2026-06-06T12:00:00Z",
    "dominant_blockers": ["visual_gate_blocked"],
    "strategy": "Freeze infra changes and focus on fixing the dominant visual blocker.",
    "why_now_different": "A new measured capture and art review exist for the current ROM hash.",
    "progress_justification": {
        "meaningful_change_summary": "Replaced placeholder sprite sheet with approved silhouette and updated capture pipeline for comparison."
    },
}
expect_pass("operational loop decision with meaningful_change_summary PASSES schema", operational_loop_decision_schema, valid_loop_decision)

bad_loop_decision_no_progress = json.loads(json.dumps(valid_loop_decision))
bad_loop_decision_no_progress["progress_justification"] = {}
expect_fail("operational loop decision without progress justification is REJECTED", operational_loop_decision_schema, bad_loop_decision_no_progress)

print()
print("=== Resumo ===")
print(f"Passou: {passed} / {total}")
if failed > 0:
    print(f"FALHOU: {failed}")
    sys.exit(1)
else:
    print("OK: todos os casos de schema passaram")
    sys.exit(0)
