# 93 - 16-bit Hardware Mastery Matrix

Status: `canonical_domain_map`

---

## Objetivo

Consolidar em uma unica matriz o estado real de dominio das tecnicas hardware-level usadas para jogos Mega Drive de barra AAA.

Esta matriz NAO substitui:

- `doc/05_technical/92_sgdk_engine_pattern_frontdoor.md`
- `doc/05_technical/92_sgdk_engine_pattern_registry.json`
- `SGDK_projects/BENCHMARK_VISUAL_LAB/`

Papel desta camada:

- dizer o que ja esta incorporado
- separar candidato forte de gap puro
- nomear donos de skill
- declarar o artefato minimo para subir de nivel
- separar efeito visual, substrato de hardware e tecnica perigosa de excecao

## Escada unica de maestria

Toda tecnica sobe por estes estados:

`mapped -> incorporated -> reproducible -> blastem_proven -> senior_default`

Equivalencia operacional:

- `mapped`
  - existe no registry ou no scan, mas ainda sem dono claro
- `incorporated`
  - ja faz parte da doutrina de uma skill existente
- `reproducible`
  - tem `lib_case` ou benchmark local reproduzivel
- `blastem_proven`
  - tem prova observada em ROM no `BENCHMARK_VISUAL_LAB`
- `senior_default`
  - pode ser usada como comportamento especialista padrao do agente

<!-- HUMAN_PROFICIENCY_PANEL_START -->
## Painel vivo humano de proficiencia

Este painel e a superficie humana principal para acompanhar o aprendizado do agente. Ele e sincronizado com `doc/05_technical/93_16bit_hardware_mastery_registry.json`; o registry continua sendo a fonte machine-readable. O catalogo de aliases e cobertura consolidada vive em `doc/05_technical/96_advanced_hardware_technique_coverage.json`.

Uso por projeto: toda tecnica aplicada deve constar no `doc/technique_usage_manifest.json` local, no GDD/TDD e em `doc/13-spec-cenas.md`, com funcao, owner, budget, fallback, evidencias e docs sincronizados. Cobertura registrada nao significa dominio pratico.

Status publicos:

- `LABORATORIO`: estudo ou experimento; isolado de projetos de entrega.
- `TEORICA_STANDARD`: tecnica compreendida e curada, sem implementacao aprovada pelo fluxo do agente.
- `TEORICA_PRIORITARIA`: tecnica teorica marcada como prioridade metodologica para barra AAA.
- `MESTRE_STANDARD`: tecnica implementada em projeto aprovado, com ROM, BlastEm, budget, docs e aprovacao humana.
- `MESTRE_PRIORITARIA`: tecnica mestre e metodo preferencial aprovado para jogos Mega Drive de barra AAA.

Regra de leitura: `MESTRE_*` exige `promotion_evidence` completo. Nenhuma tecnica sobe por texto, promessa de otimizacao, build isolado ou cobertura de alias.

### Lotes externos de curadoria

| Lote | Tipo | Status | Uso canonico |
|---|---|---|---|
| `curation_2026_06_03_megadrive_video_text_batch` | `unverified_secondary_text` | `unverified_secondary_text` | nao promove MESTRE sem evidencia operacional |
| `celestial_chase_motion_visual_curation_2026_06_03` | `project_lesson` | `project_evidence_partial` | nao promove MESTRE sem evidencia operacional |
| `curation_2026_06_04_advanced_hardware_matrix` | `unverified_secondary_text_normalized_catalog` | `curated_but_not_operationally_proven` | nao promove MESTRE sem evidencia operacional |
| `curation_2026_06_06_retro_audio_architecture_text` | `unverified_secondary_text` | `unverified_secondary_text` | reforca identidade sonora FM/PSG/DAC; nao promove MESTRE sem evidencia operacional |

### Tecnicas registradas

| Registry id | Tecnica | Status humano | Tags humanas |
|---|---|---|---|
| `line_scrolling` | Per-scanline horizontal scroll | `TEORICA_PRIORITARIA` | `LINE_SCROLL`, `PARALLAX`, `PSEUDO_3D`, `RASTER_EFFECTS`, `VBLANK_BUDGET_AUDIT` |
| `column_scrolling` | Per-column vertical scroll | `LABORATORIO` | `COLUMN_SCROLL`, `PARALLAX`, `RASTER_EFFECTS`, `VSRAM_WAVE` |
| `hint_palette_blending` | H-Int palette split / raster blending / mid-frame palette swap | `TEORICA_STANDARD` | `H_INT`, `MID_FRAME_PALETTE_SWAPPING`, `PALETTE_MANAGEMENT_AVANCADO`, `RASTER_EFFECTS`, `CRAM_DOT_MASKING` |
| `h_int_control_plane` | Single-owner H-Int control plane and callback arbitration | `LABORATORIO` | `H_INT`, `H_INT_CONTROL`, `MID_FRAME_PALETTE_SWAPPING`, `PALETTE_MANAGEMENT_AVANCADO`, `RASTER_EFFECTS` |
| `shadow_highlight_mode` | VDP Shadow / Highlight contextual | `LABORATORIO` | `PALETTE_MANAGEMENT_AVANCADO`, `SHADOW_HIGHLIGHT`, `TEXT_PRESENTATION` |
| `masked_shadow_highlight_lighting` | Masked lighting illusion via Shadow / Highlight and controlled emissive masks | `LABORATORIO` | `BOSS_SETPIECE`, `PALETTE_MANAGEMENT_AVANCADO`, `SHADOW_HIGHLIGHT` |
| `palette_cycling` | Color cycling via CRAM rotation | `LABORATORIO` | `PALETTE_MANAGEMENT_AVANCADO`, `SHADOW_HIGHLIGHT`, `RASTER_EFFECTS` |
| `procedural_raster_glitch_suite` | Procedural raster glitch suite with directed HScroll noise, palette shock and HUD corruption | `LABORATORIO` | `HUD_UI`, `PALETTE_MANAGEMENT_AVANCADO`, `PARALLAX`, `RASTER_EFFECTS` |
| `dithering_crt_smearing` | Functional dithering with CRT-aware reading | `LABORATORIO` | `PALETTE_MANAGEMENT_AVANCADO`, `SHADOW_HIGHLIGHT` |
| `window_plane_static_hud` | Window plane as static HUD architecture | `TEORICA_PRIORITARIA` | `HUD_UI`, `WINDOW_PLANE` |
| `interlaced_448_display_mode` | Interlaced 448 display mode | `LABORATORIO` | `DMA_OPTIMIZADO`, `HUD_UI` |
| `forward_kinematics` | Articulated sprite chains via fixed-point forward kinematics | `LABORATORIO` | `CUSTOM_SPRITE_COMPOSITION`, `METASPRITE_OPTIMIZATION`, `SPRITE_ENGINEERING` |
| `sprite_temporal_multiplexing` | Temporal multiplexing of sprite populations | `LABORATORIO` | `CUSTOM_SPRITE_COMPOSITION`, `METASPRITE_OPTIMIZATION`, `MULTIPLEXING`, `SPRITE_ENGINEERING`, `SPRITE_SCANLINE_BUDGET`, `SPRITE_BAND_ALLOCATOR` |
| `sprite_midframe_sat_reuse` | Mid-frame SAT reuse via H-Int rewrite | `LABORATORIO` | `CUSTOM_SPRITE_COMPOSITION`, `H_INT`, `METASPRITE_OPTIMIZATION`, `MID_FRAME_PALETTE_SWAPPING`, `MULTIPLEXING`, `SPRITE_ENGINEERING`, `SAT_DOUBLE_BUFFERING` |
| `tile_flipping` | Tile and sprite flipping via hardware bits | `TEORICA_PRIORITARIA` | `CUSTOM_SPRITE_COMPOSITION`, `METASPRITE_OPTIMIZATION`, `SPRITE_ENGINEERING`, `VRAM_TILE_INDEX_MANAGEMENT` |
| `bg_b_bypassing` | Giant boss rendered as tilemap / plane takeover | `LABORATORIO` | `BOSS_SETPIECE`, `CUSTOM_SPRITE_COMPOSITION`, `METASPRITE_OPTIMIZATION`, `SPRITE_ENGINEERING`, `VRAM_TILE_INDEX_MANAGEMENT` |
| `priority_split_foreground` | Foreground priority split by tile segment | `TEORICA_STANDARD` | `CUSTOM_SPRITE_COMPOSITION`, `METASPRITE_OPTIMIZATION`, `SPRITE_ENGINEERING`, `VRAM_TILE_INDEX_MANAGEMENT` |
| `pseudo3d_road_stack` | Pseudo-3D road stack with zmap, curves and hills | `TEORICA_STANDARD` | `PSEUDO_3D`, `SOFTWARE_RENDERING`, `LINE_SCROLL`, `RASTER_EFFECTS`, `PALETTE_MANAGEMENT_AVANCADO` |
| `software_affine_pseudo3d` | Affine or software-transformed pseudo-3D | `LABORATORIO` | `PSEUDO_3D`, `SOFTWARE_RENDERING` |
| `mutable_tile_decal_mutation` | Persistent tile mutation for local decals and room-scoped surface damage | `LABORATORIO` | `SOFTWARE_RENDERING`, `VRAM_TILE_INDEX_MANAGEMENT` |
| `cellular_microbuffer_sim` | Local cellular microbuffer for sand, acid, lava or foam islands | `LABORATORIO` | `SOFTWARE_RENDERING` |
| `tile_cache_streaming_refcount` | Refcounted tile cache for maps larger than VRAM | `TEORICA_STANDARD` | `BOSS_SETPIECE`, `DMA_STREAMING`, `SOFTWARE_RENDERING`, `VRAM_TILE_INDEX_MANAGEMENT` |
| `xgm2_pcm_multiplexing` | XGM2 channel ownership and PCM multiplexing | `LABORATORIO` | `AUDIO_ENGINEERING`, `MULTIPLEXING`, `PCM_AUDIO`, `XGM2_AUDIO` |
| `dma_transfer_safety` | DMA safety, leakage control and worst-frame discipline | `TEORICA_PRIORITARIA` | `DMA_OPTIMIZADO`, `DMA_QUEUE`, `VBLANK_BUDGET_AUDIT` |
| `shadow_highlight_slot_rule` | Palette slot audit for Shadow / Highlight operator safety | `LABORATORIO` | `PALETTE_MANAGEMENT_AVANCADO`, `SHADOW_HIGHLIGHT`, `PALETTE_REMASTERING` |
| `contextual_scene_transition_system` | Contextual scene transition architecture | `TEORICA_PRIORITARIA` | `AUDIO_ENGINEERING`, `H_INT`, `PALETTE_MANAGEMENT_AVANCADO`, `PSEUDO_3D`, `SCENE_TRANSITION`, `TEXT_PRESENTATION`, `VRAM_TILE_INDEX_MANAGEMENT` |
| `aaa_agent_proficiency_roadmap` | AAA agent proficiency roadmap | `TEORICA_PRIORITARIA` | `DMA_OPTIMIZADO` |
| `feedback_fx_decision_system` | Raster, lighting and feedback FX decision system | `TEORICA_STANDARD` | `FEEDBACK_FX`, `RASTER_EFFECTS`, `PALETTE_MANAGEMENT_AVANCADO` |
| `boss_setpiece_design` | Boss and setpiece visual design system | `TEORICA_STANDARD` | `BOSS_SETPIECE` |
| `advanced_tilemap_design` | Advanced tilemap, streaming and route readability design | `TEORICA_STANDARD` | `DMA_STREAMING`, `VRAM_TILE_INDEX_MANAGEMENT` |
| `xgm2_audio_architecture` | XGM2 senior audio architecture | `TEORICA_STANDARD` | `AUDIO_ENGINEERING`, `XGM2_AUDIO`, `FM_SYNTHESIS`, `YM2612_AUDIO`, `PSG_AUDIO`, `DAC_AUDIO` |
| `ym2612_fm_timbre_design` | YM2612 FM patch and timbre design | `TEORICA_PRIORITARIA` | `AUDIO_ENGINEERING`, `FM_SYNTHESIS`, `YM2612_AUDIO`, `TIMBRE_DESIGN` |
| `custom_z80_audio_drivers` | Custom Z80 audio drivers | `TEORICA_STANDARD` | `AUDIO_ENGINEERING`, `Z80_AUDIO` |
| `pcm_streaming_ring_buffer` | PCM streaming / ring buffer | `TEORICA_STANDARD` | `AUDIO_ENGINEERING`, `DELAYED_UPDATE`, `DMA_STREAMING`, `PCM_AUDIO` |
| `dac_direct_manipulation` | YM2612 DAC direct manipulation | `TEORICA_STANDARD` | `AUDIO_ENGINEERING`, `DAC_AUDIO` |
| `psg_direct_control_audio` | PSG direct control | `TEORICA_PRIORITARIA` | `AUDIO_ENGINEERING`, `PSG_AUDIO` |
| `audio_dma_safety_bus_contention` | Audio DMA safety / bus contention | `TEORICA_PRIORITARIA` | `AUDIO_ENGINEERING`, `DMA_OPTIMIZADO` |
| `sample_format_engineering_audio` | Audio sample format engineering | `TEORICA_PRIORITARIA` | `AUDIO_ENGINEERING`, `PCM_AUDIO`, `SAMPLE_FORMAT`, `ROM_BUDGET` |
| `audio_event_contract` | Audio event contract | `TEORICA_PRIORITARIA` | `AUDIO_ENGINEERING` |
| `channel_ownership_templates_audio` | Channel ownership templates | `TEORICA_PRIORITARIA` | `AUDIO_ENGINEERING` |
| `expressive_text_presentation_system` | Expressive narrative text presentation | `TEORICA_PRIORITARIA` | `TEXT_PRESENTATION` |
| `sprite_frame_vram_slot_streaming` | Sprite frame VRAM slot streaming | `LABORATORIO` | `SPRITE_FRAME_STREAMING`, `DMA_STREAMING`, `VRAM_TILE_INDEX_MANAGEMENT`, `VBLANK_BUDGET_AUDIT` |
| `animation_lookahead_dma_queue` | Animation look-ahead DMA queue | `LABORATORIO` | `DMA_QUEUE`, `DELAYED_UPDATE`, `SPRITE_FRAME_STREAMING`, `DMA_OPTIMIZADO` |
| `large_metasprite_vblank_fit_audit` | Large metasprite VBlank fit audit | `TEORICA_PRIORITARIA` | `VBLANK_BUDGET_AUDIT`, `METASPRITE_OPTIMIZATION`, `DMA_OPTIMIZADO`, `SPRITE_ENGINEERING` |
| `rescomp_metasprite_decomposition_audit` | rescomp metasprite decomposition audit | `TEORICA_STANDARD` | `RESCOMP_METASPRITE_AUDIT`, `METASPRITE_OPTIMIZATION`, `SPRITE_SCANLINE_BUDGET`, `SPRITE_ENGINEERING` |
| `sat_double_buffering` | Sprite Attribute Table double buffering | `LABORATORIO` | `SAT_DOUBLE_BUFFERING`, `MULTIPLEXING`, `SPRITE_ENGINEERING`, `DMA_OPTIMIZADO` |
| `sprite_band_slot_allocator` | Sprite band slot allocator | `LABORATORIO` | `SPRITE_BAND_ALLOCATOR`, `SPRITE_SCANLINE_BUDGET`, `MULTIPLEXING`, `SPRITE_ENGINEERING` |
| `cram_dot_masking_strategy` | CRAM dot masking strategy | `LABORATORIO` | `CRAM_DOT_MASKING`, `MID_FRAME_PALETTE_SWAPPING`, `H_INT`, `RASTER_EFFECTS`, `PALETTE_MANAGEMENT_AVANCADO` |
| `palette_remastering_slot_audit` | Palette remastering slot audit | `TEORICA_STANDARD` | `PALETTE_REMASTERING`, `PALETTE_MANAGEMENT_AVANCADO`, `SHADOW_HIGHLIGHT` |
| `tile_dedup_hvflip_hashing` | Tile deduplication with H/V flip hashing | `TEORICA_PRIORITARIA` | `TILE_DEDUP_HVFLIP`, `VRAM_TILE_INDEX_MANAGEMENT`, `METASPRITE_OPTIMIZATION` |
| `ghost_afterimage_sprites` | Ghost afterimage sprites | `LABORATORIO` | `GHOST_AFTERIMAGE`, `SPRITE_SCANLINE_BUDGET`, `SPRITE_ENGINEERING`, `FEEDBACK_FX` |
| `arcade_tile_redraw_substitution` | Arcade tile redraw and substitution workflow | `LABORATORIO` | `ARCADE_TILE_REDRAW`, `TILE_SUBSTITUTION`, `PALETTE_REMASTERING`, `PALETTE_MANAGEMENT_AVANCADO` |
| `perceptual_motion_gate` | Perceptual motion gate (GIF + visual_vdp_dump + perceptual metrics) | `TEORICA_PRIORITARIA` | `PERCEPTUAL_MOTION`, `RUNTIME_EVIDENCE`, `GATING`, `VISUAL_DELIVERY`, `BLASTEM_EVIDENCE` |
| `source_baked_pixel_art_standard` | Source-baked pixel-art standard (arte nasce pixel, sem downscaling) | `TEORICA_PRIORITARIA` | `SOURCE_BAKED_PIXEL_ART`, `PIXEL_LOCK`, `ANIMATION_STRIP`, `MOTION_GIF`, `ART_PIPELINE_GATE` |
| `critical_visual_rework_blocker` | Critical visual rework blocker (visual_aesthetic_report=rework bloqueia entrega) | `TEORICA_PRIORITARIA` | `CRITICAL_VISUAL_GATE`, `REWORK_BLOCKER`, `HUMAN_OVERRIDE`, `VDP_DUMP_EVIDENCE`, `VISUAL_DELIVERY` |
| `road_physics_contract` | Road physics contract (claim de chase/pseudo-3D sem contrato de pista) | `LABORATORIO` | `ROAD_PHYSICS`, `PSEUDO_3D`, `GAMEPLAY_CONTRACT`, `HSCROLL_TABLE`, `CHASE_CLAIM` |
| `modular_boss_runtime_gate` | Modular boss runtime gate (claim de boss modular sem partes runtime) | `LABORATORIO` | `MODULAR_BOSS_RIG`, `FORWARD_KINEMATICS`, `BOSS_RUNTIME`, `SPRITE_PARTS`, `FK_CHAIN` |
| `gif_motion_approval_gate` | GIF motion approval gate (aprovacao de animacao exige motion_gif) | `TEORICA_PRIORITARIA` | `GIF_MOTION_APPROVAL`, `PIVOT_DECLARATION`, `CONTACT_POINTS`, `ASSET_APPROVAL`, `PERCEPTUAL_MOTION` |
| `perceptual_runtime_metrics` | Perceptual runtime metrics (perceptual_check nao pode zerar) | `LABORATORIO` | `PERCEPTUAL_RUNTIME_METRICS`, `FRAME_METRICS`, `SPRITE_COUNT`, `PERCEPTUAL_CHECK`, `RUNTIME_INSTRUMENTATION` |
| `visual_regression_temporal_baseline` | Visual regression temporal baseline (baseline temporal de regressao visual) | `TEORICA_STANDARD` | `VISUAL_REGRESSION`, `TEMPORAL_BASELINE`, `FRAME_DIFF`, `REGRESSION_DRIFT`, `MOTION_GIF_VERSIONS` |
| `camera_scroll_management` | Camera deadzone, look-ahead and multi-directional scroll management | `TEORICA_PRIORITARIA` | `CAMERA_MANAGEMENT`, `CAMERA_DEADZONE`, `CAMERA_LOOKAHEAD`, `INTEGER_RENDER_SNAP`, `PARALLAX`, `FIXED_POINT_MATH` |
| `fixed_point_trig_lookup` | Fixed-point trigonometric lookup tables | `TEORICA_PRIORITARIA` | `FIXED_POINT_MATH`, `TRIG_LOOKUP`, `CPU_OPTIMIZATION` |
| `slope_collision_heightmap` | Per-column slope collision heightmaps | `TEORICA_PRIORITARIA` | `SLOPE_COLLISION`, `PHYSICS`, `FIXED_POINT_MATH` |
| `prerendered_sprite_scaling` | Pre-rendered sprite scaling and pseudo-depth | `TEORICA_PRIORITARIA` | `PRERENDERED_SCALING`, `SPRITE_ENGINEERING`, `PSEUDO_3D` |
| `smear_frame_animation` | One-frame smear and stretch animation | `TEORICA_PRIORITARIA` | `SMEAR_FRAME`, `ANIMATION_TIMING`, `FEEDBACK_FX` |
| `knockback_push_feedback` | Knockback and push feedback contract | `TEORICA_PRIORITARIA` | `KNOCKBACK`, `GAMEPLAY_FEEDBACK`, `PHYSICS` |
| `palette_state_transitions` | Runtime palette states, fades, flashes and grading | `TEORICA_PRIORITARIA` | `PALETTE_MANAGEMENT_AVANCADO`, `PALETTE_TRANSITION`, `PALETTE_FLASH` |
| `glyph_cache_variable_width_text` | Glyph cache and variable-width text compositor | `TEORICA_PRIORITARIA` | `GLYPH_CACHE`, `VARIABLE_WIDTH_FONT`, `TEXT_PRESENTATION` |
| `save_sram_checksum_redundancy` | SRAM save checksum and redundant slots | `TEORICA_PRIORITARIA` | `SAVE_SRAM`, `CHECKSUM`, `DATA_REDUNDANCY` |
| `scene_indexed_promotion` | Indexed scene promotion and deterministic teardown | `TEORICA_PRIORITARIA` | `SCENE_PROMOTION`, `SCENE_TEARDOWN`, `VRAM_TILE_INDEX_MANAGEMENT` |
| `runtime_profiling_cycle_budget` | Runtime profiling and cycle-budget measurement | `TEORICA_PRIORITARIA` | `RUNTIME_PROFILING`, `CPU_CYCLE_BUDGET`, `FRAME_METRICS` |
| `active_sat_link_pruning` | Active SAT link pruning and off-screen culling | `TEORICA_PRIORITARIA` | `SAT_LINK_PRUNING`, `OFFSCREEN_CULLING`, `CAMERA_CULLING`, `SPRITE_SCANLINE_BUDGET` |
| `adaptive_dma_load_shedding` | Adaptive DMA load shedding by priority | `TEORICA_PRIORITARIA` | `ADAPTIVE_DMA_SHEDDING`, `DMA_QUEUE`, `DELAYED_UPDATE`, `VBLANK_BUDGET_AUDIT` |
| `hitstop_camera_shake_feedback` | Hitstop, frame freeze and camera shake feedback | `TEORICA_PRIORITARIA` | `HITSTOP`, `CAMERA_SHAKE`, `CAMERA_FEEDBACK`, `INTEGER_RENDER_SNAP`, `GAMEPLAY_FEEDBACK` |
| `m68k_instruction_optimization` | Measured M68000 instruction and hot-loop optimization | `TEORICA_PRIORITARIA` | `M68K_OPTIMIZATION`, `CPU_CYCLE_BUDGET`, `RUNTIME_PROFILING` |
| `hardware_sprite_clipping` | Intentional hardware sprite clipping masks | `TEORICA_STANDARD` | `HARDWARE_SPRITE_CLIPPING`, `SPRITE_SCANLINE_BUDGET`, `SPRITE_ENGINEERING` |
| `pre_shifted_sprite_rotation` | Pre-shifted and pre-rendered sprite rotation | `TEORICA_STANDARD` | `PRERENDERED_ROTATION`, `SPRITE_ENGINEERING`, `ROM_BUDGET` |
| `backlight_silhouette` | Backlight and silhouette palette treatment | `TEORICA_STANDARD` | `BACKLIGHT_SILHOUETTE`, `PALETTE_MANAGEMENT_AVANCADO`, `VISUAL_DELIVERY` |
| `tile_mask_mosaic_transition` | Tile-mask mosaic scene transition | `TEORICA_STANDARD` | `TILE_MASK_MOSAIC`, `SCENE_TRANSITION`, `VRAM_TILE_INDEX_MANAGEMENT` |
| `damage_number_popup` | Damage number popup sprite system | `TEORICA_STANDARD` | `DAMAGE_NUMBER_POPUP`, `HUD_UI`, `SPRITE_SCANLINE_BUDGET` |
| `cinematic_letterbox` | Cinematic letterbox using WINDOW or forced composition | `TEORICA_STANDARD` | `CINEMATIC_LETTERBOX`, `WINDOW_PLANE`, `CUTSCENE` |
| `voice_sample_lipsync` | Voice-sample portrait lip sync | `TEORICA_STANDARD` | `VOICE_LIPSYNC`, `PCM_AUDIO`, `CUTSCENE` |
| `beat_reactive_fx` | Beat-reactive visual and gameplay FX | `TEORICA_STANDARD` | `BEAT_REACTIVE_FX`, `AUDIO_ENGINEERING`, `PALETTE_MANAGEMENT_AVANCADO` |
| `automatic_audio_ducking` | Automatic audio ducking and recovery | `TEORICA_STANDARD` | `AUDIO_DUCKING`, `AUDIO_ENGINEERING`, `PCM_AUDIO` |
| `stinger_music_cue` | Stinger and music cue transitions | `TEORICA_STANDARD` | `MUSIC_STINGER`, `AUDIO_ENGINEERING`, `XGM2_AUDIO` |
| `psg_delta_pcm_playback` | PSG delta-modulation PCM playback | `TEORICA_STANDARD` | `PSG_DELTA_PCM`, `PSG_AUDIO`, `PCM_AUDIO` |
| `cooperative_multitasking` | SGDK cooperative multitasking and load slicing | `TEORICA_STANDARD` | `COOPERATIVE_MULTITASKING`, `DELAYED_UPDATE`, `CPU_CYCLE_BUDGET` |
| `megawifi_async_integration` | MegaWiFi non-blocking integration | `TEORICA_STANDARD` | `MEGAWIFI`, `ASYNC_IO`, `DELAYED_UPDATE` |
| `vram_to_vram_dma_copy` | VDP internal VRAM-to-VRAM DMA copy | `TEORICA_STANDARD` | `VRAM_TO_VRAM_DMA`, `DMA_OPTIMIZADO`, `VRAM_TILE_INDEX_MANAGEMENT` |
| `temporal_dithering_palette_blending` | Temporal dithering and palette blending | `TEORICA_STANDARD` | `TEMPORAL_DITHERING`, `PALETTE_MANAGEMENT_AVANCADO`, `CRT_AWARE` |
| `one_dimensional_tile_deformation` | One-dimensional tile deformation floor | `TEORICA_STANDARD` | `TILE_DEFORMATION_1D`, `LINE_SCROLL`, `PSEUDO_3D` |
| `real_time_reflection` | Real-time sprite reflection with raster distortion | `TEORICA_STANDARD` | `REAL_TIME_REFLECTION`, `SPRITE_SCANLINE_BUDGET`, `RASTER_EFFECTS` |
| `combined_scroll_fake_mode7` | Combined HScroll/VScroll roto-scrolling pseudo-3D | `LABORATORIO` | `FAKE_MODE7`, `PSEUDO_3D`, `LINE_SCROLL`, `COLUMN_SCROLL` |
| `vertical_line_scroll_hint` | Per-line VSRAM updates through H-Int | `LABORATORIO` | `VSRAM_PER_LINE`, `H_INT`, `RASTER_EFFECTS` |
| `cram_overdrive_midline` | Cycle-perfect mid-line CRAM overdrive | `LABORATORIO` | `CRAM_OVERDRIVE`, `MID_FRAME_PALETTE_SWAPPING`, `RASTER_EFFECTS` |
| `software_sprite_mirroring` | Software sprite mirroring for asymmetric art | `LABORATORIO` | `SOFTWARE_SPRITE_MIRRORING`, `DMA_STREAMING`, `SPRITE_ENGINEERING` |
| `dynamic_palette_slot_clustering` | Dynamic palette slot clustering | `LABORATORIO` | `DYNAMIC_PALETTE_CLUSTERING`, `PALETTE_MANAGEMENT_AVANCADO`, `CPU_CYCLE_BUDGET` |
| `z80_math_offloading` | Z80 math offloading while preserving audio ownership | `LABORATORIO` | `Z80_MATH_OFFLOAD`, `Z80_AUDIO`, `BUS_CONTENTION` |
| `raycasting_column_renderer` | Raycasting column renderer | `LABORATORIO` | `RAYCASTING`, `SOFTWARE_RENDERING`, `CPU_CYCLE_BUDGET` |
| `flat_shaded_polygon_renderer` | Flat-shaded software polygon renderer | `LABORATORIO` | `FLAT_SHADED_POLYGONS`, `SOFTWARE_RENDERING`, `CPU_CYCLE_BUDGET` |
| `segascope_stereoscopic_3d` | SegaScope stereoscopic 3D synchronization | `LABORATORIO` | `SEGASCOPE_3D`, `INTERLACE`, `HARDWARE_PERIPHERAL` |
| `ym2612_csm_mode` | YM2612 CSM special channel mode | `LABORATORIO` | `YM2612_CSM`, `AUDIO_ENGINEERING`, `FM_SYNTHESIS` |
| `vdp_fifo_active_display_scheduling` | VDP FIFO active-display scheduling | `LABORATORIO` | `VDP_FIFO_SCHEDULING`, `ACTIVE_DISPLAY_WRITE`, `CPU_CYCLE_BUDGET` |
| `hblank_dma_interleaving` | HBlank DMA interleaving | `LABORATORIO` | `HBLANK_DMA`, `H_INT`, `DMA_OPTIMIZADO` |
| `z80_ram_dma_shield` | Z80 RAM buffering and DMA shield | `LABORATORIO` | `Z80_RAM_BUFFERING`, `DMA_SHIELD`, `BUS_CONTENTION` |
| `cycle_balanced_ym2612_writes` | Cycle-balanced YM2612 write threading | `LABORATORIO` | `YM2612_CYCLE_BALANCE`, `M68K_OPTIMIZATION`, `AUDIO_ENGINEERING` |
| `zero_overhead_hblank_isr` | Zero-overhead HBlank interrupt service routine | `LABORATORIO` | `HBLANK_ISR`, `H_INT`, `INLINE_ASSEMBLY` |
| `direct_interrupt_vector_patching` | Direct interrupt vector patching | `LABORATORIO` | `DIRECT_VECTOR_PATCH`, `H_INT`, `INLINE_ASSEMBLY` |
| `global_register_pinning` | Global/register variable pinning | `LABORATORIO` | `REGISTER_PINNING`, `M68K_OPTIMIZATION`, `INLINE_ASSEMBLY` |
| `self_modifying_code` | Self-modifying code in isolated RAM | `LABORATORIO` | `SELF_MODIFYING_CODE`, `INLINE_ASSEMBLY`, `CPU_CYCLE_BUDGET` |
| `inline_assembly_critical_sections` | Inline assembly critical sections | `LABORATORIO` | `INLINE_ASSEMBLY`, `M68K_OPTIMIZATION`, `CPU_CYCLE_BUDGET` |
| `aggressive_gcc_optimization_profile` | Aggressive GCC optimization profile | `LABORATORIO` | `GCC_OPTIMIZATION`, `M68K_OPTIMIZATION`, `ROM_BUDGET` |
| `cram_direct_raster_fill` | CRAM direct color raster fill | `LABORATORIO` | `CRAM_RASTER_FILL`, `RASTER_EFFECTS`, `PALETTE_MANAGEMENT_AVANCADO` |
| `forced_blanking_dma_extension` | Forced blanking DMA extension | `LABORATORIO` | `FORCED_BLANKING`, `DMA_OPTIMIZADO`, `VBLANK_BUDGET_AUDIT` |
<!-- HUMAN_PROFICIENCY_PANEL_END -->

## Modulo 1 - Manipulacao de Raster

| Tecnica | Estado atual | Dono principal | Situacao real |
|---|---|---|---|
| Line Scrolling | `candidate_with_evidence` | `sgdk-runtime-coder` | forte em engine scan, `lib_case` presente, falta benchmark canonico isolado |
| Column Scrolling | `partial` | `sgdk-runtime-coder` | conhecido conceitualmente, mas sem doutrina dedicada nem POC formal |
| H-Int Palette Blending / Mid-Frame Palette Swap | `candidate_with_evidence` | `sgdk-runtime-coder` | forte em `92_registry`, falta benchmark isolado e contrato explicito de ownership |
| Procedural Raster Glitch Suite | `partial` | `sgdk-runtime-coder` | suite composta muito viavel para rasgo, shock de paleta e corrupcao controlada de HUD; ainda sem benchmark proprio nem regra de legibilidade |

## Modulo 2 - Raster Control Plane

| Tecnica | Estado atual | Dono principal | Situacao real |
|---|---|---|---|
| H-Int Control Plane | `partial` | `sgdk-runtime-coder` | conhecimento existe, mas ainda nao esta formalizado como competencia-substrato unica |

## Modulo 3 - Luz, Cor e Ilusao Optica

| Tecnica | Estado atual | Dono principal | Situacao real |
|---|---|---|---|
| Shadow / Highlight Mode | `partial` | `megadrive-vdp-budget-analyst` | regras e alertas espalhados; falta trilha dedicada de auditoria + prova |
| Masked Shadow/Highlight Lighting | `partial` | `sgdk-runtime-coder` | spotlight ou lanterna viavel como ilusao contida; nao equivale a iluminacao dinamica moderna nem a alpha blending |
| Palette Cycling | `partial` | `sgdk-runtime-coder` | aparece como conceito vizinho, mas ainda sem competencia formal do workspace |
| Dithering + CRT Smearing | `partial` | `visual-excellence-standards` | dithering ja e doutrina; CRT-aware reading ainda nao esta canonizado como catalogo |

## Modulo 4 - Arquitetura de Display

| Tecnica | Estado atual | Dono principal | Situacao real |
|---|---|---|---|
| Window Plane Static HUD | `candidate_with_evidence` | `sgdk-runtime-coder` | `window_plane_lifebar` ja aparece forte no scan, mas ainda nao esta na matriz de maestria |
| Interlaced 448 Display Mode | `gap_pure` | `sgdk-runtime-coder` | entra no core roadmap, mas com politica `special_scene_only` e sem prova dedicada ainda |

## Modulo 5 - Engenharia de Sprites

| Tecnica | Estado atual | Dono principal | Situacao real |
|---|---|---|---|
| Forward Kinematics | `gap_pure` | `forward-kinematics-rigging` | sem `lib_case`, sem benchmark dedicado |
| Sprite Temporal Multiplexing | `partial` | `megadrive-vdp-budget-analyst` | conhecido como tradeoff visual, mas sem regra binaria de uso e sem POC canonico |
| Sprite Mid-Frame SAT Reuse | `gap_pure` | `megadrive-vdp-budget-analyst` | tecnica perigosa e ainda sem competencia formal separada da alternancia temporal |
| Tile Flipping | `incorporated` | `megadrive-pixel-strict-rules` | doutrina solida em arte e VRAM; falta apenas vinculacao plena a trilha de maestria |
| BG_B Bypassing / Giant Boss Tilemap | `partial` | `sgdk-runtime-coder` | conhecido como tecnica valida, mas sem benchmark e sem checklist de proibicao/permissao |
| Priority Split Foreground | `candidate_with_evidence` | `sgdk-runtime-coder` | bem ancorado no scan, mas ainda nao virou modulo de dominio senior |

## Modulo 6 - Renderizacao por Software

| Tecnica | Estado atual | Dono principal | Situacao real |
|---|---|---|---|
| Pseudo-3D Road Stack | `candidate_with_evidence` | `sgdk-runtime-coder` | `lib_case` presente, benchmark futuro obrigatorio para subir de nivel |
| Software Affine Pseudo-3D | `gap_pure` | `sgdk-runtime-coder` | tecnica distinta do road-stack; ainda nao formalizada no workspace |
| Mutable Tile Decal Mutation | `gap_pure` | `sgdk-runtime-coder` | persistencia local via pool mutavel e dirty uploads; nao e decal livre nem readback despreocupado de VRAM |
| Cellular Microbuffer Simulation | `gap_pure` | `sgdk-runtime-coder` | simulacao local de areia, acido ou lava em ilha pequena; nao e sandbox global estilo Noita |
| Tile Cache Streaming | `candidate_with_evidence` | `sgdk-runtime-coder` | muito forte no scan, ainda sem prova de laboratorio como tecnica oficial |

## Modulo 7 - Audio

| Tecnica | Estado atual | Dono principal | Situacao real |
|---|---|---|---|
| XGM2 / PCM Multiplexing | `incorporated` | `xgm2-audio-director` | doutrina e skill existem; falta benchmark oficial com BGM, SFX, ambience, stinger e pause/resume |
| YM2612 FM Timbre Design | `incorporated` | `xgm2-audio-director` | `sound_chip_identity_plan` formaliza papeis FM/PSG/DAC e traducao de referencias SNES/orquestrais; falta benchmark auditivo em BlastEm |
| Custom Z80 Audio Drivers | `incorporated` | `z80-pcm-custom-driver` | skill completa com doutrina de driver customizado, protocolo 68K→Z80, cycle budgets e skeleton asm; falta benchmark BlastEm |
| PCM Streaming / Ring Buffer | `incorporated` | `z80-pcm-custom-driver` | patterns de double/triple buffer, bank switching, scatter feed e underrun detection documentados; falta POC em BENCHMARK_VISUAL_LAB |
| DAC Direct Manipulation | `incorporated` | `z80-pcm-custom-driver` | registradores YM2612 DAC (0x2A/0x2B), timing e pipeline documentados; falta prova de voz hi-fi |
| PSG Direct Control | `incorporated` | `z80-pcm-custom-driver` | API PSG completa documentada com envelopes, noise shaping e efeitos procedurais; falta benchmark isolado |
| Bus Contention / Audio DMA Safety | `incorporated` | `z80-pcm-custom-driver`, `megadrive-vdp-budget-analyst` | bus protection, delay DMA e worst-case analysis documentados; falta prova de audio limpo sob DMA heavy |
| Sample Format Engineering | `incorporated` | `z80-pcm-custom-driver` | decision system completo (8-bit PCM, DPCM, u-law), pipeline de conversao e validacao automatizada via validate_audio.ps1 |
| Audio Event Contract | `incorporated` | `xgm2-audio-director` | evento dispatch, prioridade 16 niveis, pause/resume state machine e typewriter voice spec formalizados |
| Channel Ownership Templates | `incorporated` | `xgm2-audio-director` | 6 templates pre-built (standard, voice, boss, cutscene, sfx-only, hybrid) com fallback plans |

## Tecnicas transversais

| Tecnica | Estado atual | Dono principal | Situacao real |
|---|---|---|---|
| DMA Transfer Safety | `incorporated` | `megadrive-vdp-budget-analyst` | forte, mas espalhado; falta checklist unico e benchmark de worst-frame |
| Shadow/Highlight Slot Rule | `partial` | `visual-excellence-standards` | auditoria existe como ideia forte, mas ainda nao esta organizada como competencia autonoma |
| Contextual Scene Transition System | `incorporated` | `game-design-planning`, `scene-state-architect`, `sgdk-runtime-coder` | doutrina e `scene_transition_card` canonizados; runtime proof continua `NAO_INICIADA` ate benchmark BlastEm |

## Roadmap de Proficiencia AAA do Agente

| Trilha | Estado atual | Dono principal | Situacao real |
|---|---|---|---|
| AAA Agent Proficiency Roadmap | `incorporated` | `scene-state-architect`, `megadrive-vdp-budget-analyst` | placar canonico existe; serve para ordenar doutrina, prova runtime e gaps sem criar arvore paralela |
| Expressive Narrative Text Presentation | `incorporated` | `visual-excellence-standards`, `scene-state-architect`, `sgdk-runtime-coder`, `xgm2-audio-director` | doutrina formal existe via `text_presentation_profile`; falta `expressive_text_lab` em BlastEm |
| Feedback FX Decision System | `incorporated` | `visual-excellence-standards`, `sgdk-runtime-coder`, `megadrive-vdp-budget-analyst` | doutrina formal existe via `feedback_fx_decision_card`; falta runtime proof em BlastEm |
| Boss / Setpiece Design | `incorporated` | `visual-excellence-standards`, `multi-plane-composition`, `sgdk-runtime-coder` | doutrina formal existe via `boss_setpiece_card`; falta benchmark de boss/setpiece |
| Advanced Tilemap Design | `incorporated` | `multi-plane-composition`, `sgdk-runtime-coder`, `megadrive-vdp-budget-analyst` | doutrina formal existe via `advanced_tilemap_design_card`; falta benchmark de streaming/metatile/rota |
| XGM2 Audio Architecture | `incorporated` | `xgm2-audio-director`, `sgdk-runtime-coder` | doutrina formal existe via `audio_architecture_card`; falta prova de audio senior em BlastEm |
| Z80/PCM Custom Audio AAA | `incorporated` | `z80-pcm-custom-driver`, `xgm2-audio-director` | skill completa com driver architecture, streaming patterns, hardware memory map, sample format decision system, audio event contract, channel templates e validate_audio.ps1; falta benchmark runtime em BlastEm |

## Leitura por maturidade

### Ja incorporado

- `tile_flipping`
- `dma_transfer_safety`
- timing/pivot/frame economy basico de sprite
- multi-plano basico
- budget VDP basico
- `ui_decision_card`, politica tipografica hibrida e menu/title como front-end formal em doutrina
- `expressive_text_presentation_system` como doutrina de texto dramatico, baloes, paineis, retratos, hype text, typewriter voice e flavor text
- `contextual_scene_transition_system` como doutrina e contrato, ainda sem runtime proof
- `aaa_agent_proficiency_roadmap` como placar canonico de prioridades do agente
- `feedback_fx_decision_system`, `boss_setpiece_design`, `advanced_tilemap_design` e `xgm2_audio_architecture` como doutrina, ainda sem runtime proof

### Candidato com evidencia forte

- `line_scrolling`
- `hint_palette_blending`
- `window_plane_static_hud`
- `pseudo3d_road_stack`
- `priority_split_foreground`
- `tile_cache_streaming_refcount`

### Parcial

- `column_scrolling`
- `h_int_control_plane`
- `shadow_highlight_mode`
- `masked_shadow_highlight_lighting`
- `palette_cycling`
- `dithering_crt_smearing`
- `sprite_temporal_multiplexing`
- `bg_b_bypassing`
- `shadow_highlight_slot_rule`
- `procedural_raster_glitch_suite`

### Gap puro

- `interlaced_448_display_mode`
- `sprite_midframe_sat_reuse`
- `software_affine_pseudo3d`
- `mutable_tile_decal_mutation`
- `cellular_microbuffer_sim`
- `forward_kinematics`

## Licao Celestial Chase 2026-06-03

Lote `celestial_chase_motion_visual_curation_2026_06_03` derivado do projeto `Celestial Chase visual benchmark [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]` (LAB/TECHDEMO, runtime v005, ROM `9608a0f706b1242d89ba14ae30f899e0717808a1ea4e948352b4618384837bed`, build_v004, `technical_ready=true` mas `creative_ready=false` e `ready_for_aaa=false`).

Sintese da licao em tres frases:

1. **Movimento precisa de prova perceptiva, nao so de build verde.** Quando `claims.critical_motion=required`, asset critico sobe de status so com os 6 sinais juntos: `motion_gif`, `human_approval_record`, screenshot dedicado, SRAM fresca, `visual_vdp_dump.bin` e os quatro eixos de `perceptual_check` acima de zero.
2. **Claim de gameplay exige contrato.** Declarar `scene_id=chase_runtime_v005` + `CHASE_BOSS_IMPACT_FRAME=3` sem `road_physics_contract` (lane model, parallax, impact frame, screen shake) nem `boss_parts.json` + `FK chain` eh placeholder, nao entrega.
3. **Arte que nasce pixel nao passa por downscaling.** Source art autoral ja pixel-art segue `source_baked_pixel_art_standard` (pixel_lock + animation_strip + motion_gif); tentar encaixar no pipeline de `art-conversion-pipeline` ou `art-translation-to-vdp` eh anti-padrao.

Mapa rapido das 8 tecnicas adicionadas e seu papel no gate chain:

| Gate chain | Tecnica | Funcao |
|---|---|---|
| Aprovacao de asset | `gif_motion_approval_gate` | exige `motion_gif` + pivos + contact points para aprovar sprite de animacao |
| Aprovacao de asset | `source_baked_pixel_art_standard` | separa arte-nascida-pixel de arte-traduzida-de-high-res |
| Aprovacao de asset | `critical_visual_rework_blocker` | bloqueia promocao enquanto `visual_aesthetic_report` marcar `rework`, mesmo com aprovacao humana por GIF |
| Claim gameplay | `road_physics_contract` | claim de chase/pseudo-3D sem contrato de pista = placeholder |
| Claim gameplay | `modular_boss_runtime_gate` | claim de boss modular sem partes runtime + FK chain = placeholder |
| Evidencia runtime | `perceptual_runtime_metrics` | `perceptual_check` nao pode zerar; `frame_metrics.sprite_count` > 0 nos frames observados |
| Evidencia runtime | `perceptual_motion_gate` | gate final estruturado: 6 sinais juntos; nenhum sinal isolado libera promocao |
| Regressao | `visual_regression_temporal_baseline` | baseline temporal por frame para detectar drift entre versoes (ainda `documented`) |

Status humano aplicado a este lote:

- `TEORICA_PRIORITARIA` (4): `perceptual_motion_gate`, `source_baked_pixel_art_standard`, `critical_visual_rework_blocker`, `gif_motion_approval_gate`.
- `LABORATORIO` (3): `road_physics_contract`, `modular_boss_runtime_gate`, `perceptual_runtime_metrics` — gates de governanca ainda sem lib_case.
- `TEORICA_STANDARD` (1): `visual_regression_temporal_baseline` — apenas doutrina, sem benchmark.

Nenhuma tecnica deste lote foi promovida para `MESTRE_*`. Subida para `MESTRE_*` exige: projeto aprovado fora de LAB/TECHDEMO, ROM com sha256 registrado, evidencia BlastEm rastreavel, budget aprovado, doc/10-memory-bank.md e doc/changelog atualizados, aprovacao humana registrada, `visual_vdp_dump.bin` confirmando o asset em runtime.

### Correcao de enforcement 2026-06-04

- Claims de `critical_motion`, `road_physics` e `modular_boss` vivem em `doc/project_methodology_manifest.json`.
- O agente nao infere claims por palavras soltas como `chase`, `sBossBody` ou `impact_frame`.
- `review_required` bloqueia closeout; `required` aciona skills, contratos e validacoes; `not_applicable` exige justificativa.
- Nome placeholder/divergente gera `project_naming_invalid`; `freshness_audit` e obrigatorio para impedir closeout com docs ou evidencias obsoletas.
- Contrato vazio nao fecha gate: road physics precisa de modelo, budget e simbolos runtime; boss modular precisa de pelo menos duas partes, FK chain, simbolos runtime e budget de scanline.

## Regra de promocao

Tecnica so sobe para `senior_default` quando tiver:

1. dono de skill definido
2. regra explicita em skill ou doc canonico
3. `lib_case` ou modulo reproduzivel
4. scene dedicada em `BENCHMARK_VISUAL_LAB`
5. `validation_report` com `blastem_gate = true`
6. budget aprovado
7. aprovacao humana registrada

## Regra de seguranca

Nenhum projeto jogavel principal absorve tecnica nova antes de ela atingir pelo menos `blastem_proven` no laboratorio.
