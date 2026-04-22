# AAA Skill Curation Status — v3

Ultima atualizacao: 2026-04-21

## Escopo

Este arquivo mede a maturidade das trilhas AAA em dois eixos obrigatorios:

- `doctrine_status`
- `runtime_proof_status`

Ele NAO substitui:

- manifests do corpus
- memory banks operacionais
- evidencia de emulador

## Regua de status

### `doctrine_status`

- `PENDENTE`
  - ainda nao iniciado
- `PROPOSTO`
  - backlog oficial futuro, sem Fase 1 ativa
- `RASCUNHO`
  - draft em elaboracao
- `DRAFT_APROVADO`
  - draft aprovado como doutrina de trabalho
- `INCORPORADO`
  - conhecimento absorvido por skill, protocolo ou documento canonico existente

### `runtime_proof_status`

- `NAO_INICIADA`
  - nenhuma prova em ROM vinculante registrada
- `POC_PENDENTE_ROM`
  - ha intencao ou POC parcial, mas sem gate BlastEm fechado
- `VALIDADA_EM_ROM`
  - rodou no emulador com evidencia, aguardando promocao final
- `APROVADA_PELO_HUMANO`
  - validada em ROM e aprovada explicitamente para uso de referencia

## Regras de leitura

- `INCORPORADO` NAO significa `APROVADA_PELO_HUMANO`
- Sprint 1 ja existe como doutrina incorporada; isso nao autoriza declarar runtime canonizado
- `99_sgdk_engines_scan_appendix.md` nao e roadmap mestre; evidencias de engine entram pela ordem `92_frontdoor -> 92_registry -> 99_appendix`
- `10_curation_roadmap_and_agent_directive.md` continua backlog de curadoria de traducao artistica, nao status board AAA

## Roadmap Objetivo de Proficiencia AAA do Agente

Este e o placar executivo do que o agente ja domina, do que esta parcialmente coberto e do que ainda falta para operar como construtor AAA de Mega Drive.

Fontes canonicas:

- status executivo: `doc/03_art/AAA_SKILL_CURATION_STATUS.md`
- mapa humano: `doc/05_technical/93_16bit_hardware_mastery_matrix.md`
- registry machine-readable: `doc/05_technical/93_16bit_hardware_mastery_registry.json`
- roadmap de execucao: `doc/05_technical/94_16bit_hardware_mastery_roadmap.md`

### Status sintetico

| Status | Itens |
|---|---|
| `ja_canonizado` | HUD/UI por `ui_decision_card`, tipografia hibrida com `glyph_manifest`, menu/title como front-end formal, transicoes por `scene_transition_card`, raster/luz/feedback FX, boss/setpieces, tilemap avancado, audio senior, multi-plano basico, budget VDP basico, DMA safety e tile flipping |
| `falta_doutrina` | Kinematics/experimentos especiais ainda fora da Fase 1; demais lacunas P0-P3 agora tem doutrina, mas nao prova runtime |
| `falta_runtime_proof` | HUD/UI, tipografia, menu/title, transicoes, raster/luz/feedback FX, boss/setpieces, tilemap avancado, audio senior, sprite animation, character design, multi-plano e tecnicas avancadas sem benchmark BlastEm |
| `gap_puro` | forward kinematics, interlaced 448 como uso produtivo, SAT mid-frame reuse, mutable tile decals e cellular microbuffer |

### Prioridade objetiva

| Prioridade | Registry ID | Trilha | Objetivo |
|---|---|---|---|
| `P0` | `feedback_fx_decision_system` | Raster + Lighting + Feedback FX | Canonizar H-Int, line/column scroll, palette split, Shadow/Highlight, palette cycling, hit sparks, particulas e feedback dramatizado com owner, reset e fallback |
| `P1` | `boss_setpiece_design` | Boss/Setpieces | Canonizar boss gigante, plane takeover, partes, weak points, telegraph, camera/impact FX e scanline budget |
| `P2` | `advanced_tilemap_design` | Tilemap Avancado | Canonizar streaming, metatiles, priority foreground, tile reuse, colisao visual, dano local e leitura de rota |
| `P3` | `xgm2_audio_architecture` | Audio Senior | Canonizar XGM2, PCM multiplexing, stingers, ambience, prioridade de SFX, pause/resume e audio handoff |
| `P4` | `aaa_agent_proficiency_roadmap` | Kinematics/Experimentos | Manter FK, SAT reuse, interlaced, mutable tile decals e cellular microbuffer como trilhas especiais ate benchmark proprio |

Regra:

- `ja_canonizado` significa doutrina ou contrato, nao runtime validado
- nenhuma trilha sobe para uso default AAA sem benchmark em BlastEm, budget aprovado e evidencia rastreavel

## Sprint 1 — Fundacao Visual

| ID | Trilha | doctrine_status | runtime_proof_status | Local canonico | Proximo gate |
|----|--------|-----------------|----------------------|----------------|--------------|
| S1.1 | Animacao de Sprites | `INCORPORADO` | `POC_PENDENTE_ROM` | `tools/sgdk_wrapper/.agent/skills/art/sprite-animation/SKILL.md` | captura BlastEm `scene_sprite_anim` + aprovacao humana |
| S1.2 | Design de Personagem | `INCORPORADO` | `POC_PENDENTE_ROM` | `tools/sgdk_wrapper/.agent/skills/art/character-design/SKILL.md` | captura BlastEm `scene_character_design` + aprovacao humana |
| S1.3 | Composicao Multi-Plano em ROM | `INCORPORADO` | `POC_PENDENTE_ROM` | `tools/sgdk_wrapper/.agent/skills/art/multi-plane-composition/SKILL.md` | captura BlastEm `scene_multiplane` + aprovacao humana |

## Sprint 2 — Diferenciacao AAA

| ID | Trilha | doctrine_status | runtime_proof_status | Dependencia | Notas reconciliadas |
|----|--------|-----------------|----------------------|-------------|---------------------|
| S2.1 | Efeitos Raster e Line Scroll | `INCORPORADO` | `NAO_INICIADA` | Sprint 1 estabilizada | doutrina formal em `doc/03_art/15_aaa_runtime_spectacle_decision_system.md`; H-Int, line scroll, palette split e raster distortion entram via `feedback_fx_decision_card` |
| S2.2 | Shadow/Highlight Mode | `INCORPORADO` | `NAO_INICIADA` | Sprint 1 estabilizada | Shadow/Highlight, silhueta, backlight, spotlight, lanterna e weak point entram via `feedback_fx_decision_card` com `palette_slot_audit` |
| S2.3 | Palette Cycling | `INCORPORADO` | `NAO_INICIADA` | Sprint 1 estabilizada | palette cycling fica subordinado a gameplay_signal, owner de CRAM, reset e fallback |
| S2.4 | Sistema de Particulas e FX | `INCORPORADO` | `NAO_INICIADA` | Sprint 1 estabilizada | hit sparks, poeira, explosao, debris, energia e magia entram via `feedback_fx_decision_card`; SAT reuse permanece fora do default |

## Sprint 3 — Polimento

| ID | Trilha | doctrine_status | runtime_proof_status | Dependencia | Notas reconciliadas |
|----|--------|-----------------|----------------------|-------------|---------------------|
| S3.1 | Boss Design Visual | `INCORPORADO` | `NAO_INICIADA` | Sprint 2 canonizada | doutrina formal em `doc/03_art/15_aaa_runtime_spectacle_decision_system.md`; boss/setpiece entra via `boss_setpiece_card` |
| S3.2 | HUD Design | `INCORPORADO` | `NAO_INICIADA` | Sprint 2 canonizada | doutrina formal em `doc/03_art/13_hud_ui_fx_decision_system.md`; `window_plane_static_hud` e core, `front_end_profile` permanece seed de planejamento e se formaliza como `profile_kind=front_end_profile` no `ui_decision_card`, a tipografia segue politica hibrida com `glyph_manifest`, e `window_alias` continua fora do default |
| S3.3 | Title Screen e Menu Art | `INCORPORADO` | `NAO_INICIADA` | Sprint 2 canonizada | doutrina formal em `doc/03_art/12_menu_visual_language.md`; menu/title tratados como cena formal e integrados ao `ui_decision_card` via `profile_kind=front_end_profile` |
| S3.4 | Scene Transition Design | `INCORPORADO` | `NAO_INICIADA` | Sprint 2 canonizada | doutrina formal em `doc/03_art/14_contextual_scene_transition_system.md`; `scene_transition_card` canonizado sem skill nova |

## Sprint 4 — Autonomia

| ID | Trilha | doctrine_status | runtime_proof_status | Dependencia | Notas reconciliadas |
|----|--------|-----------------|----------------------|-------------|---------------------|
| S4.1 | Tilemap Design Avancado | `INCORPORADO` | `NAO_INICIADA` | Sprint 3 canonizada | doutrina formal em `doc/03_art/15_aaa_runtime_spectacle_decision_system.md`; streaming, metatiles e rota entram via `advanced_tilemap_design_card` |
| S4.2 | Pixel Art Original pelo Agent | `PENDENTE` | `NAO_INICIADA` | Sprint 3 canonizada | absorver dithering catalog |

## Sprint 5 — Kinematics e Audio

| ID | Trilha | doctrine_status | runtime_proof_status | Dependencia | Notas reconciliadas |
|----|--------|-----------------|----------------------|-------------|---------------------|
| S5.1 | Forward Kinematics e Esqueletos Articulados | `PROPOSTO` | `NAO_INICIADA` | Sprint 4 canonizada | backlog oficial futuro; skill final bloqueada ate Fase 1 |
| S5.2 | Arquitetura de Audio XGM2 e Multiplexing PCM | `INCORPORADO` | `NAO_INICIADA` | Sprint 4 canonizada | doutrina formal em `doc/03_art/15_aaa_runtime_spectacle_decision_system.md` e skill `xgm2-audio-director`; audio entra via `audio_architecture_card` |

## Trilhas Futuras Fora da Malha S1.1-S5.2

Estas trilhas entram no roadmap de maestria do agente, mas NAO alteram a numeracao canonica de Sprint 1-5.

| ID | Trilha | doctrine_status | runtime_proof_status | Politica | Notas |
|----|--------|-----------------|----------------------|----------|-------|
| T1 | Interlaced 448 Display Mode | `PROPOSTO` | `NAO_INICIADA` | `special_scene_only` | tecnica core de dominio, mas proibida como default de cena; exige benchmark proprio e comparacao contra 224p |
| T2 | Sprite Mid-Frame SAT Reuse | `PROPOSTO` | `NAO_INICIADA` | `hazardous_experimental` | tecnica perigosa, separada de multiplex temporal e dependente de `h_int_control_plane` |
| T3 | Mutable Tile Decal Mutation | `PROPOSTO` | `NAO_INICIADA` | `special_scene_only` | dano persistente local por pool mutavel; proibido vender como decal livre ou mutacao global de qualquer parede |
| T4 | Cellular Microbuffer Simulation | `PROPOSTO` | `NAO_INICIADA` | `special_scene_only` | microframebuffer local para areia, acido ou lava; bloqueado ate dirty upload e tile mutation amadurecerem |

## Historico

| Data | Trilha | Mudanca | Motivo |
|------|--------|---------|--------|
| 2026-04-08 | S1.1 | `RASCUNHO -> DRAFT_APROVADO` | draft aprovado como doutrina |
| 2026-04-08 | S1.2 | `RASCUNHO -> DRAFT_APROVADO` | draft aprovado como doutrina |
| 2026-04-09 | S1.1 | `DRAFT_APROVADO -> INCORPORADO` | skill operacional criada para animacao |
| 2026-04-09 | S1.2 | `DRAFT_APROVADO -> INCORPORADO` | skill operacional criada para design de personagem |
| 2026-04-09 | S1.3 | `DRAFT_APROVADO -> INCORPORADO` | skill operacional criada para multi-plano |
| 2026-04-10 | Global | `status unico -> dois eixos` | reconciliacao do diagnostico externo sem rebaixar Sprint 1 |
| 2026-04-10 | S5.1 | `inexistente -> PROPOSTO` | backlog oficial futuro aceito na reconciliacao |
| 2026-04-10 | S5.2 | `inexistente -> PROPOSTO` | backlog oficial futuro aceito na reconciliacao |
| 2026-04-10 | S2.1 / S2.4 / S3.2 | `notas reconciliadas ampliadas` | H-Int vira substrato formal, Window Plane HUD entra em S3.2 e multiplexing temporal se separa de SAT reuse |
| 2026-04-10 | T1 | `inexistente -> PROPOSTO` | `interlaced_448_display_mode` entra no roadmap de maestria com politica `special_scene_only` |
| 2026-04-10 | T2 | `inexistente -> PROPOSTO` | `sprite_midframe_sat_reuse` entra como trilha futura perigosa, fora do escopo padrao das sprints atuais |
| 2026-04-10 | S2.1 / S2.2 | `notas reconciliadas ampliadas` | `procedural_raster_glitch_suite` e `masked_shadow_highlight_lighting` entram como suites honestas de hardware, nao como equivalentes literais a pipelines modernos |
| 2026-04-10 | T3 | `inexistente -> PROPOSTO` | `mutable_tile_decal_mutation` entra como trilha futura especial de dano local persistente |
| 2026-04-10 | T4 | `inexistente -> PROPOSTO` | `cellular_microbuffer_sim` entra como trilha futura tardia de microframebuffer local |
| 2026-04-20 | S3.2 | `PENDENTE -> INCORPORADO` | `ui_decision_card` canonizado, `front_end_profile` mantido como seed e formalizado via `profile_kind=front_end_profile`, com handoff de ownership/budget/fallback amarrado ao framework |
| 2026-04-20 | S3.2 | `notas reconciliadas ampliadas` | politica hibrida de tipografia, `glyph_manifest` e fallback tipografico passam a fazer parte da doutrina de HUD/UI |
| 2026-04-21 | S3.3 | `PENDENTE -> INCORPORADO` | menu/title screen reconhecidos como doutrina ja registrada em `doc/03_art/12_menu_visual_language.md` e absorvida pelo contrato `ui_decision_card` |
| 2026-04-21 | S3.4 | `PENDENTE -> INCORPORADO` | `scene_transition_card` canonizado como doutrina integrada para transicoes contextualizadas sem criar skill nova |
| 2026-04-21 | Roadmap AAA | `inexistente -> CANONIZADO` | placar objetivo de proficiencia do agente registrado como ponte entre status executivo, matriz humana, registry machine-readable e roadmap de execucao |
| 2026-04-21 | S2/S3/S4/S5 | `PENDENTE/PROPOSTO -> INCORPORADO` | `AAA Runtime Spectacle Decision System` canoniza raster, luz, FX, particulas, boss/setpieces, tilemap avancado e audio senior como contratos objetivos |
