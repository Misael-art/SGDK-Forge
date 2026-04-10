# AAA Skill Curation Status — v2

Ultima atualizacao: 2026-04-09

## Escopo

Este arquivo mede apenas a maturidade doutrinaria das skills, drafts e trilhas artisticas.

Ele **nao** mede:

- status operacional de casos em `assets/reference/translation_curation/`
- status de promocao para ROM
- status de validacao em emulador

A verdade operacional dos casos vive em:

- `assets/reference/translation_curation/case_registry.json`
- `case_manifest.json` / `collection_manifest.json` / `corpus_manifest.json`

## Regua de status

- `RASCUNHO`
  - conteudo em elaboracao
- `DRAFT_APROVADO`
  - conteudo aprovado como doutrina de trabalho
- `INCORPORADO`
  - conhecimento absorvido pela skill ou protocolo principal
- `PENDENTE`
  - ainda nao iniciado

## Sprint 1 — Fundacao Visual

| ID | Trilha | Status | Local Canonico | Gate Seguinte |
|----|--------|--------|----------------|---------------|
| S1.1 | Animacao de Sprites | `INCORPORADO` | `tools/sgdk_wrapper/.agent/skills/art/sprite-animation/SKILL.md` | POC / ROM |
| S1.2 | Design de Personagem | `INCORPORADO` | `tools/sgdk_wrapper/.agent/skills/art/character-design/SKILL.md` | POC / ROM |
| S1.3 | Composicao Multi-Plano em ROM | `INCORPORADO` | `tools/sgdk_wrapper/.agent/skills/art/multi-plane-composition/SKILL.md` | prova runtime |

## Sprint 2 — Diferenciacao AAA

| ID | Trilha | Status | Dependencia |
|----|--------|--------|-------------|
| S2.1 | Efeitos Raster e Line Scroll | `PENDENTE` | Sprint 1 estabilizada |
| S2.2 | Shadow/Highlight Mode | `PENDENTE` | Sprint 1 estabilizada |
| S2.3 | Palette Cycling | `PENDENTE` | Sprint 1 estabilizada |
| S2.4 | Sistema de Particulas e FX | `PENDENTE` | Sprint 1 estabilizada |

## Sprint 3 — Polimento

| ID | Trilha | Status | Dependencia |
|----|--------|--------|-------------|
| S3.1 | Boss Design Visual | `PENDENTE` | Sprint 2 canonizada |
| S3.2 | HUD Design | `PENDENTE` | Sprint 2 canonizada |
| S3.3 | Title Screen e Menu Art | `PENDENTE` | Sprint 2 canonizada |

## Sprint 4 — Autonomia

| ID | Trilha | Status | Dependencia |
|----|--------|--------|-------------|
| S4.1 | Tilemap Design Avancado | `PENDENTE` | Sprint 3 canonizada |
| S4.2 | Pixel Art Original pelo Agent | `PENDENTE` | Sprint 3 canonizada |

## Historico

| Data | Trilha | Mudanca | Motivo |
|------|--------|---------|--------|
| 2026-04-08 | S1.1 | `RASCUNHO -> DRAFT_APROVADO` | draft aprovado como doutrina |
| 2026-04-08 | S1.2 | `RASCUNHO -> DRAFT_APROVADO` | draft aprovado como doutrina |
| 2026-04-09 | S1.1 | `DRAFT_APROVADO -> INCORPORADO` | skill operacional criada para animacao |
| 2026-04-09 | S1.2 | `DRAFT_APROVADO -> INCORPORADO` | skill operacional criada para design de personagem |
| 2026-04-09 | S1.3 | `DRAFT_APROVADO -> INCORPORADO` | skill operacional criada para multi-plano |
