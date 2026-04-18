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
| XGM2 / PCM Multiplexing | `gap_pure` | `xgm2-audio-director` | workspace nao tem skill de audio dedicada nem prova oficial |

## Tecnicas transversais

| Tecnica | Estado atual | Dono principal | Situacao real |
|---|---|---|---|
| DMA Transfer Safety | `incorporated` | `megadrive-vdp-budget-analyst` | forte, mas espalhado; falta checklist unico e benchmark de worst-frame |
| Shadow/Highlight Slot Rule | `partial` | `visual-excellence-standards` | auditoria existe como ideia forte, mas ainda nao esta organizada como competencia autonoma |

## Leitura por maturidade

### Ja incorporado

- `tile_flipping`
- `dma_transfer_safety`
- timing/pivot/frame economy basico de sprite
- multi-plano basico
- budget VDP basico

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
- `xgm2_pcm_multiplexing`

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
