# AAA Skill Curation Status — v3

Ultima atualizacao: 2026-04-10

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
| S1.1 | Animacao de Sprites | `INCORPORADO` | `NAO_INICIADA` | `tools/sgdk_wrapper/.agent/skills/art/sprite-animation/SKILL.md` | prova em `BENCHMARK_VISUAL_LAB` |
| S1.2 | Design de Personagem | `INCORPORADO` | `NAO_INICIADA` | `tools/sgdk_wrapper/.agent/skills/art/character-design/SKILL.md` | prova em `BENCHMARK_VISUAL_LAB` |
| S1.3 | Composicao Multi-Plano em ROM | `INCORPORADO` | `NAO_INICIADA` | `tools/sgdk_wrapper/.agent/skills/art/multi-plane-composition/SKILL.md` | revisao in place de `doc/05_technical/91_multi_plane_composition.md` + BlastEm |

## Sprint 2 — Diferenciacao AAA

| ID | Trilha | doctrine_status | runtime_proof_status | Dependencia | Notas reconciliadas |
|----|--------|-----------------|----------------------|-------------|---------------------|
| S2.1 | Efeitos Raster e Line Scroll | `PENDENTE` | `NAO_INICIADA` | Sprint 1 estabilizada | absorver line scroll, column scroll, H-Int palette, fake mode 7 e DMA safety |
| S2.2 | Shadow/Highlight Mode | `PENDENTE` | `NAO_INICIADA` | Sprint 1 estabilizada | reforcar regra obrigatoria do slot 15 |
| S2.3 | Palette Cycling | `PENDENTE` | `NAO_INICIADA` | Sprint 1 estabilizada | manter foco em custo zero de VRAM |
| S2.4 | Sistema de Particulas e FX | `PENDENTE` | `NAO_INICIADA` | Sprint 1 estabilizada | absorver sub-deliverable de sprite multiplexing |

## Sprint 3 — Polimento

| ID | Trilha | doctrine_status | runtime_proof_status | Dependencia | Notas reconciliadas |
|----|--------|-----------------|----------------------|-------------|---------------------|
| S3.1 | Boss Design Visual | `PENDENTE` | `NAO_INICIADA` | Sprint 2 canonizada | absorver BG plane bypassing e cross-link com `S5.1` |
| S3.2 | HUD Design | `PENDENTE` | `NAO_INICIADA` | Sprint 2 canonizada | sem alteracao estrutural nesta passada |
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
