# Epic Branding Rebrand Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar tres setpieces de branding memoraveis, tecnicamente seguros e observados no BlastEm.

**Architecture:** Um builder deterministico gera todos os assets SGDK-safe. `scene_branding.c` carrega um resident set por slot e executa uma FSM de antecipacao, impacto e resolucao usando BG_A, BG_B, sprites, paleta, HScroll e audio.

**Tech Stack:** Python 3.13 + Pillow, SGDK 2.11 C, ResComp, XGM2/PSG, PowerShell wrapper, BlastEm.

---

### Task 1: Congelar contratos

**Files:**
- Modify: `doc/branding_sequence_contract.json`
- Modify: `doc/13-spec-cenas.md`
- Modify: `doc/08-bible-artistica.md`

- [ ] Registrar timeline `150 + 150 + 180`, ownership de planos/paletas e referencias.
- [ ] Registrar que PSG 3 e ruido e que os fundos sao distintos por slot.

### Task 2: Testar contrato do builder

**Files:**
- Create: `tools/image-tools/tests/test_branding_v3_assets.py`
- Create: `tools/image-tools/build_branding_v3_assets.py`

- [ ] Escrever teste que exige a lista completa de outputs e dimensoes.
- [ ] Executar o teste e confirmar falha porque o builder ainda nao existe.
- [ ] Implementar builder deterministico com preview e lineage.
- [ ] Executar teste e confirmar que todos os outputs sao 4-bit, PLTE <= 16 e 8px aligned.

### Task 3: Promover recursos

**Files:**
- Modify: `res/resources.res`
- Generate: `res/branding/*.png`

- [ ] Executar builder v3.
- [ ] Atualizar `.res` com tres fundos e sprites v3.
- [ ] Rodar `art_diagnostic.py`, `res_graph_audit.ps1` e `validate_resources.ps1`.

### Task 4: Refatorar runtime

**Files:**
- Modify: `src/scenes/scene_branding.c`

- [ ] Alterar limites para frames 150/300/480.
- [ ] Carregar fundo distinto por slot.
- [ ] Implementar entrada fisica dos logos, monograma 32x32 e shield 64x32.
- [ ] Implementar slide de `PRESENTS`, shake/debris, fade final e PSG correto.
- [ ] Preservar teardown, `DMA_QUEUE`, APIs publicas e skip input.

### Task 5: Fechar gates

**Files:**
- Update: `doc/07-budget-vram-dma.md`
- Update: `doc/10-memory-bank.md`
- Update: `doc/changelog/changelog.md`

- [ ] Buildar pelo wrapper.
- [ ] Confirmar ROM vigente e validacao sem erro tecnico.
- [ ] Capturar engine, author, project e transicao no BlastEm.
- [ ] Revisar arte em escala nativa e corrigir qualquer falha perceptiva.
- [ ] Rodar freshness e scene closeout.

