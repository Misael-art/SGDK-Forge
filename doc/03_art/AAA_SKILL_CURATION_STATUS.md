# AAA Skill Curation Status — v3

Ultima atualizacao: 2026-04-12

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

## Sprint 1 — Fundacao Visual

| ID | Trilha | doctrine_status | runtime_proof_status | Local canonico | Proximo gate |
|----|--------|-----------------|----------------------|----------------|--------------|
| S1.1 | Animacao de Sprites | `INCORPORADO` | `POC_PENDENTE_ROM` | `tools/sgdk_wrapper/.agent/skills/art/sprite-animation/SKILL.md` | captura BlastEm `scene_sprite_anim` + aprovacao humana |
| S1.2 | Design de Personagem | `INCORPORADO` | `POC_PENDENTE_ROM` | `tools/sgdk_wrapper/.agent/skills/art/character-design/SKILL.md` | captura BlastEm `scene_character_design` + aprovacao humana |
| S1.3 | Composicao Multi-Plano em ROM | `INCORPORADO` | `POC_PENDENTE_ROM` | `tools/sgdk_wrapper/.agent/skills/art/multi-plane-composition/SKILL.md` | captura BlastEm `scene_multiplane` + aprovacao humana |

## Sprint 2 — Diferenciacao AAA

| ID | Trilha | doctrine_status | runtime_proof_status | Dependencia | Notas reconciliadas |
|----|--------|-----------------|----------------------|-------------|---------------------|
| S2.1 | Efeitos Raster e Line Scroll | `PENDENTE` | `NAO_INICIADA` | Sprint 1 estabilizada | absorver `h_int_control_plane`, mid-frame palette swap, line scroll, column scroll, pseudo3d road-stack, `procedural_raster_glitch_suite` e DMA safety |
| S2.2 | Shadow/Highlight Mode | `PENDENTE` | `NAO_INICIADA` | Sprint 1 estabilizada | reforcar regra obrigatoria do slot 15 e absorver `masked_shadow_highlight_lighting` como nome honesto da trilha |
| S2.3 | Palette Cycling | `PENDENTE` | `NAO_INICIADA` | Sprint 1 estabilizada | manter foco em custo zero de VRAM |
| S2.4 | Sistema de Particulas e FX | `PENDENTE` | `NAO_INICIADA` | Sprint 1 estabilizada | absorver apenas `sprite_temporal_multiplexing`; SAT reuse fica fora desta sprint |

## Sprint 3 — Polimento

| ID | Trilha | doctrine_status | runtime_proof_status | Dependencia | Notas reconciliadas |
|----|--------|-----------------|----------------------|-------------|---------------------|
| S3.1 | Boss Design Visual | `PENDENTE` | `NAO_INICIADA` | Sprint 2 canonizada | absorver BG plane bypassing e cross-link com `S5.1` |
| S3.2 | HUD Design | `PENDENTE` | `NAO_INICIADA` | Sprint 2 canonizada | absorver `window_plane_static_hud` como competencia core; `window_alias` continua fora do default |
| S3.3 | Title Screen e Menu Art | `PENDENTE` | `NAO_INICIADA` | Sprint 2 canonizada | sem alteracao estrutural nesta passada |

## Sprint 4 — Autonomia

| ID | Trilha | doctrine_status | runtime_proof_status | Dependencia | Notas reconciliadas |
|----|--------|-----------------|----------------------|-------------|---------------------|
| S4.1 | Tilemap Design Avancado | `PENDENTE` | `NAO_INICIADA` | Sprint 3 canonizada | absorver tile flipping inteligente |
| S4.2 | Pixel Art Original pelo Agent | `PENDENTE` | `NAO_INICIADA` | Sprint 3 canonizada | absorver dithering catalog |

## Sprint 5 — Kinematics e Audio

| ID | Trilha | doctrine_status | runtime_proof_status | Dependencia | Notas reconciliadas |
|----|--------|-----------------|----------------------|-------------|---------------------|
| S5.1 | Forward Kinematics e Esqueletos Articulados | `PROPOSTO` | `NAO_INICIADA` | Sprint 4 canonizada | backlog oficial futuro; skill final bloqueada ate Fase 1 |
| S5.2 | Arquitetura de Audio XGM2 e Multiplexing PCM | `PROPOSTO` | `NAO_INICIADA` | Sprint 4 canonizada | backlog oficial futuro; prioridade mantida em `P1` |

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
