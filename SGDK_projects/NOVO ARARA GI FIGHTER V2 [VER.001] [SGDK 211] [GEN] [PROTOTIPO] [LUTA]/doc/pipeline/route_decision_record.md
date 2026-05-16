# route_decision_record

context_type: projeto_novo
affected_surface: projeto + cena gameplay + HUD + personagem animado
user_goal: criar do zero um prototipo SGDK/Mega Drive jogavel de luta 1v1 autoral com Caio Arara, Davi Arara, Lapa Open Mat, HUD formal e animacoes reais.
dominant_route: art_diagnostic -> art_creation_sourcing -> source_translation -> budget -> runtime -> validation
first_skill: art/art-asset-diagnostic
supporting_skills:
- art/art-creation-sourcing
- art/sprite-animation
- art/character-design
- art/multi-plane-composition
- art/art-translation-to-vdp
- art/visual-excellence-standards
- hardware/megadrive-vdp-budget-analyst
- architecture/scene-state-architect
- code/sgdk-runtime-coder
- operation/sgdk-build-wrapper-operator

first_tool:
  command: python tools/sgdk_wrapper/art_diagnostic.py --project "<project>" --output doc/art_diagnostic_report.json
  reason: confirmar que o projeto novo esta em cenario 3_no_art antes de qualquer conversao.

existing_curation:
  builder: tools/image-tools/build_arara_gi_fighter_assets.py (reference only; must consume this project's own source_art if used)
  source_case_manifest: none
  reference_implementation: template runtime_probe and SGDK wrapper only; no HAMOOPIG source visual.

technical_family:
  resource_loading_model: animation_window_streaming
  plane_model: BG_B cold skyline/parallax, BG_A arena/tatame, WINDOW/HUD fixed text, SPRITES for fighters and hit spark.
  asset_strategy: source_art AI images persisted, translated to indexed SGDK sprite strips and BG images, per-state runtime sprite definitions.

evidence_required:
- context_pack_manifest
- visual_source_acquisition_plan
- master_style_manifest
- benchmark_profile
- authorial_model_sheet
- authorial_stage_concept
- animation_state_plan, pose_roster, frame_budget_table, pivot_and_scale_contract
- premium_source_manifest with hashes
- source_validity_report, authoriality_gate_report, clone_risk_report
- source_to_rom_asset_map, benchmark_match_report, visual_delivery_gate_report
- res/resources.res and build output
- validate_resources report
- BlastEm screenshot and emulator_session bound to out/rom.bin

forbidden_shortcuts_until_evidence:
- no HAMOOPIG assets, bgb1.png, pose, palette, or timing as source.
- no local_author_pixel_rasterization as final source for critical assets.
- no textual/proxy ROM as delivery.
- no asset promotion to res/ before persisted data/source_art and source validity.
- no delivery/AAA/pronto wording before BlastEm evidence.

handoff_next: art_diagnostic_report then art_creation_sourcing.