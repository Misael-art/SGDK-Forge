# Canonical Skill Curation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Manter apenas skills SGDK com owner distinto, técnica defensável e
contrato operacional, arquivando aliases e técnicas frágeis em legado
reversível.

**Architecture:** A árvore `skills/` conterá somente owners ativos. Skills
desativadas serão movidas integralmente para `legacy/skills/` e registradas por
hash em `skill_lifecycle_registry.json`. Validadores passarão a consultar esse
registro, em vez de preservar contagens históricas de um lote de curadoria.

**Tech Stack:** PowerShell 7, Python 3, JSON Schema Draft-07, Markdown/YAML,
headers SGDK 2.11.

---

## File Structure

### Criar

- `tools/sgdk_wrapper/schemas/skill_lifecycle_registry.schema.json`
  - contrato machine-readable de lifecycle e reversão.
- `tools/sgdk_wrapper/ci/test_skill_lifecycle_registry.ps1`
  - teste de hashes, paths, referências e árvore legado.
- `tools/sgdk_wrapper/ci/test_active_skill_routing.ps1`
  - garante owner único e ausência de aliases arquivados nas rotas ativas.
- `tools/sgdk_wrapper/.agent/references/skill_lifecycle_registry.json`
  - decisão humana e rastreabilidade de todas as skills ativas/legadas.
- `tools/sgdk_wrapper/.agent/legacy/skills/`
  - quarentena fora da descoberta ativa.
- `tools/sgdk_wrapper/audit_skill_lifecycle.ps1`
  - auditor read-only e verificador de restauração.

### Modificar

- `tools/sgdk_wrapper/.agent/scripts/validate_skill_framework.py`
- `tools/sgdk_wrapper/validate_aaa_video_curation.py`
- `tools/sgdk_wrapper/.agent/framework_manifest.json`
- `tools/sgdk_wrapper/.agent/references/aaa_pipeline_curated_skill_map.json`
- `tools/sgdk_wrapper/.agent/skills/governance/aaa-pipeline-guardian/SKILL.md`
- oito skills técnicas mantidas, listadas na Task 4
- cinco orchestrators de planejamento, listados na Task 5
- `doc/07_game_design/genre_specialization_registry.json`
- `tools/sgdk_wrapper/ci/test_genre_specialization_registry.ps1`
- testes de orchestrator afetados
- `doc/06_AI_MEMORY_BANK.md`
- `doc/agent_learning/changelog_2026-06-18.md`

### Mover para legado

| Skill | Lifecycle | Substituta ativa |
|---|---|---|
| `architecture/level-manifest-architect` | `merged` | `design/level-design-canonical` |
| `art/color-conversion-curator` | `merged` | `art/art-translation-to-vdp` |
| `art/dither-composite-transparency` | `merged` | `art/visual-excellence-standards` |
| `art/palette-cram-curator` | `merged` | `art-conversion-pipeline` + `megadrive-vdp-budget-analyst` |
| `art/sprite-asset-budget-curator` | `merged` | `sprite-animation` + `megadrive-vdp-budget-analyst` |
| `art/tilemap-attribute-director` | `merged` | `art-conversion-pipeline` + `tiled-hybrid-parallax-curator` |
| `audio/sfx-prep-fm-psg-pcm` | `merged` | `xgm2-audio-director` |
| `audio/z80-audio-boundary-architect` | `merged` | `xgm2-audio-director` + `z80-pcm-custom-driver` |
| `code/articulated-sprite-architect` | `merged` | `forward-kinematics-rigging` |
| `code/software-tile-rasterizer` | `experimental` | nenhuma; exige benchmark dedicado |
| `hardware/hscroll-linescroll-road-fx` | `merged` | `shadow-highlight-scroll-fx` |
| `hardware/raster-palette-hint-director` | `merged` | `shadow-highlight-scroll-fx` |
| `hardware/sprite-scanline-budgeter` | `merged` | `megadrive-vdp-budget-analyst` |

---

### Task 1: Baseline RED e contrato de lifecycle

**Files:**
- Create: `tools/sgdk_wrapper/ci/test_skill_lifecycle_registry.ps1`
- Create: `tools/sgdk_wrapper/ci/test_active_skill_routing.ps1`
- Test: `tools/sgdk_wrapper/.agent/scripts/validate_skill_framework.py`

- [ ] **Step 1: Registrar o baseline atual**

Executar:

```powershell
uv run python tools/sgdk_wrapper/.agent/scripts/validate_skill_framework.py
```

Esperado: FAIL com 94 achados.

- [ ] **Step 2: Escrever teste de lifecycle**

O teste deve exigir:

```powershell
$RegistryPath = "tools/sgdk_wrapper/.agent/references/skill_lifecycle_registry.json"
$SchemaPath = "tools/sgdk_wrapper/schemas/skill_lifecycle_registry.schema.json"

Assert-True (Test-Path $RegistryPath) "registry missing"
Assert-True (Test-Path $SchemaPath) "schema missing"
```

Para cada registro não ativo:

```powershell
Assert-True (-not (Test-Path $entry.source_path)) "legacy skill still active"
Assert-True (Test-Path $entry.legacy_path) "legacy payload missing"
Assert-True ($entry.content_sha256 -match '^[0-9a-f]{64}$') "hash missing"
```

- [ ] **Step 3: Escrever teste de roteamento**

Aliases proibidos nas superfícies operacionais:

```powershell
$Archived = @(
  "level-manifest-architect",
  "color-conversion-curator",
  "dither-composite-transparency",
  "palette-cram-curator",
  "sprite-asset-budget-curator",
  "tilemap-attribute-director",
  "sfx-prep-fm-psg-pcm",
  "z80-audio-boundary-architect",
  "articulated-sprite-architect",
  "software-tile-rasterizer",
  "hscroll-linescroll-road-fx",
  "raster-palette-hint-director",
  "sprite-scanline-budgeter"
)
```

Pesquisar apenas:

- `framework_manifest.json`;
- pipelines;
- workflows;
- rules;
- `aaa_pipeline_curated_skill_map.json`;
- `learning_owner_catalog.json`.

Documentos históricos, `legacy/` e `lib_case/` não contam como rota ativa.

- [ ] **Step 4: Executar e confirmar RED**

Esperado:

- registry/schema ausentes;
- aliases ainda ativos;
- lifecycle não auditável.

---

### Task 2: Schema, registry e auditor read-only

**Files:**
- Create: `tools/sgdk_wrapper/schemas/skill_lifecycle_registry.schema.json`
- Create: `tools/sgdk_wrapper/.agent/references/skill_lifecycle_registry.json`
- Create: `tools/sgdk_wrapper/audit_skill_lifecycle.ps1`
- Modify: `tools/sgdk_wrapper/.agent/scripts/validate_skill_framework.py`

- [ ] **Step 1: Implementar schema**

Campos obrigatórios por entrada:

```json
{
  "skill_id": "hardware/sprite-scanline-budgeter",
  "lifecycle": "merged",
  "decision_reason": "Budget já pertence ao megadrive-vdp-budget-analyst.",
  "replacement_skills": ["hardware/megadrive-vdp-budget-analyst"],
  "evidence_grade": "E1_framework_audit",
  "source_path": "tools/sgdk_wrapper/.agent/skills/hardware/sprite-scanline-budgeter",
  "legacy_path": "tools/sgdk_wrapper/.agent/legacy/skills/hardware/sprite-scanline-budgeter",
  "content_sha256": "<64 hex>",
  "references_redirected": [],
  "restore_conditions": ["Novo owner distinto comprovado por fixture e validator."],
  "decision_date": "2026-06-18",
  "human_approved": true
}
```

Enums:

```json
["active", "merged", "superseded", "deprecated", "experimental"]
```

- [ ] **Step 2: Implementar auditor**

`audit_skill_lifecycle.ps1` deve:

- validar JSON contra schema;
- recalcular hash determinístico da pasta;
- confirmar que `active` existe somente em `skills/`;
- confirmar que não ativo existe somente em `legacy/skills/`;
- rejeitar replacement inexistente;
- rejeitar skill ativa sem registro;
- nunca mover ou editar arquivos em modo audit.

- [ ] **Step 3: Atualizar validator do framework**

Adicionar:

```python
LIFECYCLE_REGISTRY = AGENT_ROOT / "references" / "skill_lifecycle_registry.json"
LEGACY_ROOT = AGENT_ROOT / "legacy" / "skills"
```

Validar somente `SKILLS_ROOT.rglob("SKILL.md")` como skills ativas. Verificar
se cada uma possui entrada `active`; verificar hashes e ausência de referências
operacionais para entries não ativas.

- [ ] **Step 4: Executar testes**

Esperado: ainda FAIL porque as skills não foram movidas.

---

### Task 3: Arquivar aliases e redirecionar owners

**Files:**
- Move: as 13 skills da tabela para `.agent/legacy/skills/`
- Modify: `tools/sgdk_wrapper/.agent/framework_manifest.json`
- Modify: `tools/sgdk_wrapper/.agent/references/aaa_pipeline_curated_skill_map.json`
- Modify: `tools/sgdk_wrapper/validate_aaa_video_curation.py`
- Modify: `tools/sgdk_wrapper/.agent/skills/governance/aaa-pipeline-guardian/SKILL.md`

- [ ] **Step 1: Calcular hashes antes do move**

Hash de pasta deve ordenar caminhos relativos e combinar:

```text
relative_path + NUL + file_sha256 + LF
```

O SHA-256 final entra no registry.

- [ ] **Step 2: Mover integralmente para legado**

Não reescrever payload legado. Preservar `SKILL.md`, `agents/` e referências.

- [ ] **Step 3: Redirecionar rotas**

Rotas ativas:

```json
{
  "advanced_scroll_or_raster_fx": ["shadow-highlight-scroll-fx"],
  "sprite_scanline_or_vram_budget": ["megadrive-vdp-budget-analyst"],
  "high_color_or_ai_art_translation": ["art-translation-to-vdp"],
  "tilemap_conversion_or_attributes": ["art-conversion-pipeline"],
  "audio_architecture": ["xgm2-audio-director"],
  "custom_z80_pcm": ["z80-pcm-custom-driver"],
  "articulated_runtime_rig": ["forward-kinematics-rigging"],
  "level_design_and_manifest": ["level-design-canonical"]
}
```

`software-tile-rasterizer` não ganha substituta automática. A rota deve
retornar `experimental_requires_benchmark`.

- [ ] **Step 4: Remover contagens históricas do validator operacional**

`validate_aaa_video_curation.py` não deve mais exigir “20 skills novas”.
Preservar os documentos como snapshots históricos, mas validar owners atuais
pelo lifecycle registry.

- [ ] **Step 5: Executar testes de lifecycle e roteamento**

Esperado: PASS para paths e aliases.

---

### Task 4: Curar e compactar os oito owners técnicos mantidos

**Files:**
- Modify: `architecture/game-state-transition-architect/SKILL.md`
- Modify: `code/camera-system-sgdk/SKILL.md`
- Modify: `code/collision-system-architect/SKILL.md`
- Modify: `code/entity-polymorphism-architect/SKILL.md`
- Modify: `code/input-system-sgdk/SKILL.md`
- Modify: `governance/aaa-pipeline-guardian/SKILL.md`
- Modify: `hardware/shadow-highlight-scroll-fx/SKILL.md`
- Modify: `hardware/vram-streaming-dma-queue/SKILL.md`
- Modify: respectivos `agents/openai.yaml`

- [ ] **Step 1: Padronizar contrato**

Cada skill deve conter:

```markdown
## Contrato Operacional
### Entrada minima
### Saida minima
### Passa quando
### Handoff para proxima etapa
```

- [ ] **Step 2: Remover narrativa de projeto**

Mover lições Celestial Chase e lotes de vídeo para `lib_case`; manter na skill
somente a regra generalizada.

- [ ] **Step 3: Verificar APIs citadas**

Confirmar em headers:

- `JOY_*` em `inc/joy.h`;
- `PAL_fadeInAll` em `inc/pal.h`;
- scroll modes/functions em `inc/vdp.h` e `inc/vdp_bg.h`;
- `VDP_loadTileData` em `inc/vdp_tile.h`;
- `DMA_queueDma` em `inc/dma.h`.

Qualquer API ausente deve ser removida ou marcada como proibida.

- [ ] **Step 4: Compactar**

Alvos:

- cada skill técnica ≤ 500 palavras;
- guardian ≤ 650 palavras;
- descrição de frontmatter apenas com gatilhos;
- nenhum exemplo repetido de regras globais.

- [ ] **Step 5: Corrigir metadata**

Owners técnicos usam:

```yaml
policy:
  allow_implicit_invocation: true
```

`short_description` deve ter 25–64 caracteres.

---

### Task 5: Corrigir orchestrators e registry de gêneros

**Files:**
- Modify: cinco `planning/*-game-design/SKILL.md`
- Modify: `doc/07_game_design/genre_specialization_registry.json`
- Modify: `tools/sgdk_wrapper/ci/test_genre_specialization_registry.ps1`
- Modify: cinco testes de orchestrator

- [ ] **Step 1: Manter ativas somente especializações comprovadas**

Ativas:

```text
fighting_2d_traditional
brawler_belt_scroll
platformer_precision_2d
racing_arcade
rpg_turn_based_jrpg
strategy_tower_defense
```

Uma especialização só pode ser `active` quando existem simultaneamente:

- schema específico;
- validator específico;
- owner skill;
- teste do validator;
- opt-in explícito.

- [ ] **Step 2: Rebaixar entradas sem implementação**

Exemplos obrigatórios:

- `rpg_action_topdown` -> `deferred`;
- `strategy_tactical_turn_based` -> `deferred`;
- `brawler_run_and_gun_*` -> `deferred`;
- `metroidvania_*` e puzzles sem schema -> `deferred`;
- `sports_action_direct` e `adventure_action_2d` -> `deferred`.

- [ ] **Step 3: Remover limites inventados**

Excluir regras sem derivação de budget, como:

- “5+ party quebra VRAM”;
- “32 magias é teto”;
- “4 fases causa pattern overflow”;
- “50–100 níveis exige save >32KB”;
- contagem fixa de tracks/stages/waves como limite de hardware.

Substituir por:

```markdown
- dimensionar por dados realmente residentes, save encoding, pior quadro,
  sprites por scanline, VRAM e DMA;
- valores de projeto pertencem ao GDD/contrato e ao budget, não à skill.
```

- [ ] **Step 4: Compactar orchestrators**

Cada orchestrator deve:

- ficar abaixo de 550 palavras;
- manter `allow_implicit_invocation=false`;
- delegar, não duplicar especialistas;
- incluir `Passa quando` e `Handoff`.

- [ ] **Step 5: Atualizar testes**

Remover asserts de constantes arbitrárias e adicionar:

```powershell
Assert-True 'only implemented specialization is active' (...)
Assert-True 'skill contains Passa quando' (...)
Assert-True 'skill contains Handoff' (...)
Assert-True 'no unsupported hard ceilings' (...)
```

---

### Task 6: Validar restauração e economia de contexto

**Files:**
- Modify: `tools/sgdk_wrapper/ci/test_skill_lifecycle_registry.ps1`
- Modify: `tools/sgdk_wrapper/.agent/scripts/validate_skill_framework.py`

- [ ] **Step 1: Testar restauração em fixture temporária**

Copiar uma entry `merged` para diretório temporário, conferir hash e simular
retorno para `skills/`. Não alterar árvore real.

- [ ] **Step 2: Testar budget de contexto**

Para as 13 skills curadas:

```python
assert word_count <= entry["context_budget_words"]
```

- [ ] **Step 3: Testar descoberta**

Confirmar:

- `.agents/skills` resolve apenas `skills/`;
- nenhuma pasta em `legacy/skills/` aparece como skill ativa;
- archived aliases não aparecem no route map.

---

### Task 7: Rodada de validação completa

**Files:**
- Test only

- [ ] **Step 1: Framework**

```powershell
uv run python tools/sgdk_wrapper/.agent/scripts/validate_skill_framework.py
```

Esperado: `Skill framework validation passed.`

- [ ] **Step 2: Lifecycle**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_skill_lifecycle_registry.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_active_skill_routing.ps1
```

Esperado: PASS.

- [ ] **Step 3: Gêneros**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_genre_specialization_registry.ps1
```

Executar também os cinco testes de orchestrator. Esperado: PASS.

- [ ] **Step 4: Curadoria AAA**

```powershell
uv run --with jsonschema python tools/sgdk_wrapper/validate_aaa_video_curation.py
```

Esperado: PASS sem exigir skills arquivadas ou contagem histórica.

- [ ] **Step 5: Integridade**

```powershell
git diff --check
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/assert_agent_environment.ps1
```

---

### Task 8: Memória e handoff factual

**Files:**
- Modify: `doc/06_AI_MEMORY_BANK.md`
- Create: `doc/agent_learning/changelog_2026-06-18.md`

- [ ] **Step 1: Registrar decisões**

Incluir:

- skills mantidas;
- skills fundidas/experimentais;
- substitutas;
- especializações rebaixadas;
- redução de palavras da árvore ativa;
- comandos e resultados de validação.

- [ ] **Step 2: Declarar limites**

Registrar explicitamente:

- nenhuma ROM foi gerada;
- nenhuma técnica ganhou prova de runtime;
- lifecycle ativo significa owner operacional, não domínio comprovado em
  hardware;
- técnicas experimentais continuam exigindo fixture, budget e BlastEm.

- [ ] **Step 3: Verificação final**

Reexecutar os comandos da Task 7 após a atualização documental.

