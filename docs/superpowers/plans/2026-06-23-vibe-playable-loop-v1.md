# Vibe Playable Loop V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar o `vibe_playable_loop_v1` para rotear pedidos naturais a uma producao visual rastreavel, impedir autoria procedural final e separar validacao contratual rapida da prova real em BlastEm.

**Architecture:** Um roteador PowerShell deterministico consome um ruleset JSON, preserva targets e emite um contexto compacto. Os contratos canonicos existentes sao estendidos; novos reports existem apenas para decisoes ainda sem owner estrutural (rota, admissao e rastreabilidade agregada). O build e os validators propagam o menor teto de claim, enquanto a aceitacao visual real exige um projeto LAB dedicado, ROM, BlastEm e checkpoint humano.

**Tech Stack:** PowerShell 5.1/7, JSON Schema Draft-07, Python/jsonschema apenas para testes de schema, SGDK 2.11, ResComp, BlastEm e scripts canonicos do wrapper.

---

## Invariantes globais de execucao

- Preservar integralmente o worktree existente. Nunca usar `git reset`, `git checkout`, `git restore`, stash ou limpeza ampla.
- Antes de cada fase, definir `$PhaseFiles`, salvar `git status --porcelain=v1` em `out/ci/vibe_playable_worktree_baseline.txt`, salvar `git diff -- $PhaseFiles` em `out/ci/vibe_playable_phaseN_preexisting.diff` e registrar existencia/hash inicial dos caminhos em `out/ci/vibe_playable_phaseN_file_baseline.json`; depois da fase, comparar e aceitar somente os caminhos declarados neste plano.
- Aplicar patches pequenos com `apply_patch`; nunca sobrescrever arquivos inteiros que ja estejam modificados no worktree. Se um hunk da fase se misturar com alteracao preexistente no mesmo arquivo, parar a fase e migrar para worktree limpa dedicada em vez de commitar um delta ambiguo.
- Rodar RED antes de criar a implementacao correspondente e registrar a mensagem de falha esperada.
- Fazer um commit isolado por fase, adicionando explicitamente apenas o delta produzido pela fase. `git add -- $PhaseFiles` sozinho e proibido porque pode capturar alteracoes preexistentes nos mesmos arquivos.
- Imediatamente apos cada commit, registrar `$PhaseCommit = (git rev-parse HEAD)` no log de execucao. O rollback e `git revert $PhaseCommit`. Antes do commit, reverter somente o hunk criado pela fase ou remover somente arquivos novos cujos caminhos absolutos foram conferidos.
- `tools/sgdk_wrapper/ci/run_vibe_playable_fast_tests.ps1` nunca abre emulador.
- `tools/sgdk_wrapper/ci/run_vibe_playable_blastem_gate.ps1` e o unico runner desta entrega que fecha a fixture visual real.
- Nenhum teste escreve `doc/human_approval_record.md`; ele apenas valida um registro humano preexistente e com hash fixado.

### Politica obrigatoria de staging em worktree sujo

Cada fase deve escolher um dos dois caminhos antes do primeiro patch:

1. **Worktree limpa dedicada:** se a fase precisar tocar arquivo ja sujo no baseline e os hunks nao forem separaveis com seguranca, criar uma worktree limpa dedicada antes de implementar a fase. Essa escolha exige usar `superpowers:using-git-worktrees` no turno de implementacao e commitar a fase apenas nessa worktree limpa.
2. **Staging por delta no worktree atual:** quando os hunks forem separaveis, usar `git add -N -- $PhaseFiles` seguido de `git add -p -- $PhaseFiles` para arquivos texto existentes. Arquivos novos, inclusive PNG/WebP binarios, so podem ser staged inteiros quando ausentes no baseline e listados na secao **Criar** da fase. Em seguida, salvar `git diff --cached -- $PhaseFiles` em `out/ci/vibe_playable_phaseN_cached.diff` e revisar esse arquivo antes do commit. O commit so pode ocorrer se todos os hunks no diff staged forem produzidos pela fase, todos os arquivos staged estiverem em `$PhaseFiles`, e nenhum hunk preexistente do baseline aparecer no cached diff.

O executor deve tratar `git diff --cached` como evidencia obrigatoria da fase. Se a auditoria staged falhar, nao commitar; registrar o bloqueio e retornar ao caminho de worktree limpa dedicada.

Antes do Step 1 de cada fase, declarar o mesmo array `$PhaseNFiles` mostrado no passo de commit e executar o preflight da fase com o numero correto:

```powershell
$PhaseName = 'phaseN'
$BaselineFiles = @($PhaseFiles | ForEach-Object {
  $Exists = Test-Path -LiteralPath $_
  [pscustomobject]@{
    path = $_
    existed = $Exists
    sha256 = if ($Exists -and (Test-Path -LiteralPath $_ -PathType Leaf)) { (Get-FileHash -Algorithm SHA256 -LiteralPath $_).Hash } else { $null }
  }
})
git status --porcelain=v1 | Set-Content out/ci/vibe_playable_worktree_baseline.txt
git diff -- $PhaseFiles | Set-Content "out/ci/vibe_playable_${PhaseName}_preexisting.diff"
[pscustomobject]@{ files = $BaselineFiles } | ConvertTo-Json -Depth 5 | Set-Content "out/ci/vibe_playable_${PhaseName}_file_baseline.json"
```

## Inventario exato de arquivos

### Criar

**Fase 1**

- `tools/sgdk_wrapper/.agent/references/vibe_playable_intent_rules.json`
- `tools/sgdk_wrapper/schemas/vibe_playable_route_report.schema.json`
- `tools/sgdk_wrapper/lib/vibe_playable_router.psm1`
- `tools/sgdk_wrapper/route_vibe_playable_request.ps1`
- `tools/sgdk_wrapper/.agent/pipelines/vibe_playable_loop_v1.json`
- `tools/sgdk_wrapper/.agent/workflows/vibe-playable-loop.md`
- `tools/sgdk_wrapper/ci/test_vibe_playable_router.ps1`

**Fase 2**

- `tools/sgdk_wrapper/schemas/premium_source_manifest.schema.json`
- `tools/sgdk_wrapper/lib/premium_source_manifest.psm1`
- `tools/sgdk_wrapper/validate_premium_source_manifest.ps1`
- `tools/sgdk_wrapper/ci/test_premium_source_manifest_compatibility.ps1`
- `tools/sgdk_wrapper/ci/fixtures/vibe_playable/premium_source/v1_single.json`
- `tools/sgdk_wrapper/ci/fixtures/vibe_playable/premium_source/v1_root.json`
- `tools/sgdk_wrapper/ci/fixtures/vibe_playable/premium_source/v2_valid.json`
- `tools/sgdk_wrapper/ci/fixtures/vibe_playable/premium_source/v2_unknown.json`

**Fase 3**

- `tools/sgdk_wrapper/schemas/runtime_admission_report.schema.json`
- `tools/sgdk_wrapper/schemas/technical_change_scope_report.schema.json`
- `tools/sgdk_wrapper/lib/runtime_admission.psm1`
- `tools/sgdk_wrapper/evaluate_runtime_admission.ps1`
- `tools/sgdk_wrapper/ci/test_runtime_admission.ps1`

**Fase 4**

- `tools/sgdk_wrapper/schemas/visual_authoring_report.schema.json`
- `tools/sgdk_wrapper/audit_visual_authoring.ps1`
- `tools/sgdk_wrapper/ci/test_visual_authoring_policy.ps1`
- `tools/sgdk_wrapper/ci/fixtures/vibe_playable/procedural_adversarial/pillow_character.py`
- `tools/sgdk_wrapper/ci/fixtures/vibe_playable/procedural_adversarial/svg_stage.svg`
- `tools/sgdk_wrapper/ci/fixtures/vibe_playable/procedural_adversarial/canvas_hud.html`
- `tools/sgdk_wrapper/ci/fixtures/vibe_playable/procedural_adversarial/c_primitives_fx.c`
- `tools/sgdk_wrapper/ci/fixtures/vibe_playable/procedural_adversarial/quantize_only.py`

**Fase 5**

- `tools/sgdk_wrapper/schemas/build_meta.schema.json`
- `tools/sgdk_wrapper/schemas/visual_asset_traceability_report.schema.json`
- `tools/sgdk_wrapper/audit_visual_asset_traceability.ps1`
- `tools/sgdk_wrapper/ci/test_visual_asset_traceability.ps1`
- `tools/sgdk_wrapper/ci/fixtures/vibe_playable/approval/doc/human_approval_record.md`
- `tools/sgdk_wrapper/ci/fixtures/vibe_playable/approval/data/processed/reports/asset_approval_panel.png`
- `tools/sgdk_wrapper/ci/fixtures/vibe_playable/approval/data/processed/reports/asset_visual_delivery_gate_report.json`
- `tools/sgdk_wrapper/ci/fixtures/vibe_playable/approval/fixture_manifest.json`

**Fase 6**

- `tools/sgdk_wrapper/schemas/vibe_playable_cache_report.schema.json`
- `tools/sgdk_wrapper/lib/vibe_playable_cache.psm1`
- `tools/sgdk_wrapper/ci/test_vibe_playable_cache_and_context.ps1`

**Fase 7**

- `tools/sgdk_wrapper/ci/fixtures/vibe_playable/requests.json`
- `tools/sgdk_wrapper/ci/test_vibe_playable_contract_fixtures.ps1`
- `tools/sgdk_wrapper/ci/run_vibe_playable_fast_tests.ps1`

**Fase 8 — runner**

- `tools/sgdk_wrapper/schemas/vibe_playable_e2e_report.schema.json`
- `tools/sgdk_wrapper/ci/run_vibe_playable_blastem_gate.ps1`

**Fase 8 — projeto LAB dedicado**

Raiz: `SGDK_projects/_agent_laboratory/VIBE_PLAYABLE_LOOP_FIXTURE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]`

- `.mddev/project.json`
- `build.bat`
- `run.bat`
- `doc/project_context_manifest.json`
- `doc/project_methodology_manifest.json`
- `doc/project_hygiene_manifest.json`
- `doc/10-memory-bank.md`
- `doc/11-gdd.md`
- `doc/13-spec-cenas.md`
- `doc/technique_usage_manifest.json`
- `doc/human_approval_record.md`
- `doc/changelog/changelog.md`
- `doc/contracts/art_direction_decision_record.json`
- `doc/contracts/master_style_manifest.json`
- `doc/contracts/art_gameplay_direction_gate.json`
- `doc/contracts/hero_animation_strip_contract.json`
- `doc/contracts/boss_animation_strip_contract.json`
- `data/source_art/premium_source_manifest.json`
- `data/source_art/vibe_scene_v1/source_scene.png`
- `data/source_art/vibe_hero_v1/model_sheet.png`
- `data/source_art/vibe_hero_v1/hero_attack_strip.png`
- `data/source_art/vibe_boss_v1/model_sheet.png`
- `data/source_art/vibe_boss_v1/boss_attack_strip.png`
- `data/processed/bgs/vibe_stage_elite.png`
- `data/processed/sprites/vibe_hero_attack_elite.png`
- `data/processed/sprites/vibe_boss_attack_elite.png`
- `data/processed/reports/hero_motion_preview.webp`
- `data/processed/reports/boss_motion_preview.webp`
- `data/processed/reports/asset_approval_panel.png`
- `data/processed/reports/asset_visual_delivery_gate_report.json`
- `res/bgs/vibe_stage_elite.png`
- `res/sprites/vibe_hero_attack_elite.png`
- `res/sprites/vibe_boss_attack_elite.png`
- `res/resources.res`
- `src/main.c`
- `src/system/runtime_probe.c`
- `src/system/runtime_probe.h`

O bootstrap pode materializar `.agent/` local a partir do framework central. Essa arvore e gerada pelo helper canonico, nao recebe edicao manual e deve ser auditada pelo framework manifest.

**Fase 8 — artefatos gerados pelo runner, nao versionados, exigidos como evidencia**

- `out/logs/build_meta.json`
- `out/logs/emulator_session.json`
- `out/logs/evidence_closeout_report.json`
- `out/logs/visual_asset_traceability_report.json`
- `out/logs/visual_delivery_gate_report.json`
- `out/logs/runtime_comparison_panel.png`
- `out/logs/vibe_playable_e2e_report.json`

### Modificar

**Fase 1**

- `tools/sgdk_wrapper/.agent/framework_manifest.json`
- `tools/sgdk_wrapper/.agent/references/skill_lifecycle_registry.json`
- `tools/sgdk_wrapper/.agent/references/aaa_pipeline_curated_skill_map.json`
- `tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json`
- `tools/sgdk_wrapper/.agent/workflows/production-loop.md`
- `tools/sgdk_wrapper/.agent/workflows/aaa-scene-pipeline.md`
- `tools/sgdk_wrapper/ci/test_active_skill_routing.ps1`

**Fase 2**

- `tools/sgdk_wrapper/.agent/skills/art/art-creation-sourcing/SKILL.md`
- `tools/sgdk_wrapper/.agent/workflows/premium-art-pipeline.md`
- `tools/sgdk_wrapper/.agent/pipelines/vibe_playable_loop_v1.json`
- `tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json`
- `tools/sgdk_wrapper/ci/test_schema_contract_gates.py`

**Fase 3**

- `tools/sgdk_wrapper/build.bat`
- `tools/sgdk_wrapper/audit_promotion_claims.ps1`
- `tools/sgdk_wrapper/validate_resources.ps1`
- `tools/sgdk_wrapper/schemas/promotion_claim_manifest.schema.json`
- `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md`
- `tools/sgdk_wrapper/.agent/skills/code/sgdk-runtime-coder/SKILL.md`
- `tools/sgdk_wrapper/.agent/workflows/vibe-playable-loop.md`
- `tools/sgdk_wrapper/.agent/pipelines/vibe_playable_loop_v1.json`

**Fase 4**

- `tools/sgdk_wrapper/audit_placeholder_quarantine.ps1`
- `tools/sgdk_wrapper/validate_resources.ps1`
- `tools/sgdk_wrapper/schemas/art_gameplay_direction_gate.schema.json`
- `tools/sgdk_wrapper/schemas/visual_delivery_gate_report.schema.json`
- `tools/sgdk_wrapper/.agent/skills/art/art-asset-diagnostic/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/art/visual-excellence-standards/SKILL.md`
- `tools/sgdk_wrapper/.agent/workflows/vibe-playable-loop.md`

**Fase 5**

- `tools/sgdk_wrapper/update_project_changelog.ps1`
- `tools/sgdk_wrapper/capture_blastem_evidence.ps1`
- `tools/sgdk_wrapper/finalize_emulator_evidence.ps1`
- `tools/sgdk_wrapper/freshness_audit.ps1`
- `tools/sgdk_wrapper/scene_closeout_gate.ps1`
- `tools/sgdk_wrapper/validate_resources.ps1`
- `tools/sgdk_wrapper/schemas/visual_delivery_gate_report.schema.json`
- `tools/sgdk_wrapper/ci/test_evidence_closeout_seal.ps1`
- `tools/sgdk_wrapper/.agent/skills/art/visual-excellence-standards/references/source_to_rom_visual_gate.md`
- `tools/sgdk_wrapper/.agent/skills/operation/emulator-vdp-evidence-curator/SKILL.md`

**Fase 6**

- `tools/sgdk_wrapper/route_vibe_playable_request.ps1`
- `tools/sgdk_wrapper/lib/vibe_playable_router.psm1`
- `tools/sgdk_wrapper/assert_agent_environment.ps1`
- `tools/sgdk_wrapper/prepare_agent_environment.ps1`
- `tools/sgdk_wrapper/graphify_forge.ps1`
- `tools/sgdk_wrapper/ci/test_agent_startup_environment.ps1`
- `tools/sgdk_wrapper/ci/test_graphify_update_failure.ps1`
- `tools/sgdk_wrapper/.agent/workflows/agent-startup-environment.md`
- `doc/GRAPHIFY_OBSIDIAN_POLICY.md`

**Fase 7**

- `tools/sgdk_wrapper/ci/run_all_contract_gates.ps1`
- `tools/sgdk_wrapper/ci/test_schema_contract_gates.py`
- `tools/sgdk_wrapper/.agent/framework_manifest.json`

**Fase 8**

- `tools/sgdk_wrapper/.agent/framework_manifest.json`
- `doc/06_AI_MEMORY_BANK.md`

---

## Fase 1: roteador, targets e contexto compacto

### Task 1: contrato RED do roteador deterministico

**Files:**
- Create: `tools/sgdk_wrapper/ci/test_vibe_playable_router.ps1`
- Test target: `tools/sgdk_wrapper/route_vibe_playable_request.ps1`
- Test target: `tools/sgdk_wrapper/schemas/vibe_playable_route_report.schema.json`

- [ ] **Step 1: Escrever o teste que exige determinismo, PT/EN e multiplicidade**

O teste deve executar o comando duas vezes com a mesma entrada e comparar o JSON apos remover somente `generated_at`. Deve conter estas assercoes:

```powershell
Assert-True ($route.visual_route_required -eq $true) 'natural request must require visual route'
Assert-True (@($route.detected_targets | Where-Object role -eq 'player_hero').Count -eq 1) 'hero target missing'
Assert-True (@($route.detected_targets | Where-Object role -eq 'boss').Count -eq 1) 'boss target missing'
Assert-True ($hero.target_id -ne $boss.target_id) 'hero and boss collapsed'
Assert-True (@($route.required_owners)[0] -eq 'skills/art/art-direction-selector') 'visual owner must precede runtime'
Assert-True ($route.dispatch.mode -eq 'explicit_router_dispatch') 'selector dispatch must be explicit'
Assert-True ($route.compact_context_bytes -le 32768) 'compact context budget exceeded'
```

- [ ] **Step 2: Rodar RED**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_vibe_playable_router.ps1
```

Expected: FAIL porque `route_vibe_playable_request.ps1` e o schema ainda nao existem.

### Task 2: implementar ruleset, modulo, CLI, schema e superficies de rota

**Files:** todos os arquivos da Fase 1 listados no inventario.

- [ ] **Step 1: Criar o ruleset versionado**

`vibe_playable_intent_rules.json` deve conter arrays ordenados e IDs estaveis. Estrutura minima:

```json
{
  "schema_version": "1.0.0",
  "ruleset_version": "vibe_playable_intents_1.0.0",
  "languages": ["pt", "en"],
  "confidence_levels": {"explicit": 1.0, "verb_noun": 0.8, "broad": 0.6, "fallback": 0.4},
  "rules": [
    {"rule_id":"pt_create_stage","language":"pt","verbs":["crie","criar","faca","faça"],"targets":["fase","cenario","cenário"],"intent":"scene","target_type":"scene","role":"playable_stage"},
    {"rule_id":"pt_hero","language":"pt","targets":["heroi","herói","personagem"],"intent":"character","target_type":"character","role":"player_hero"},
    {"rule_id":"pt_boss","language":"pt","targets":["boss","chefe","chefao","chefão"],"intent":"character","target_type":"character","role":"boss"},
    {"rule_id":"en_create_stage","language":"en","verbs":["create","make","build"],"targets":["stage","level","scene"],"intent":"scene","target_type":"scene","role":"playable_stage"}
  ]
}
```

- [ ] **Step 2: Implementar funcoes publicas do modulo**

`vibe_playable_router.psm1` deve exportar exatamente:

```powershell
Normalize-VibeRequestText
Get-VibeDetectedLanguage
Get-VibeIntentMatches
Get-VibeDetectedTargets
Get-VibeRequiredOwners
New-VibePlayableRouteReport
New-VibePlayableCompactContext
```

IDs devem seguir `target_{role}_{ordinal}` e a ordenacao final deve ser `scene`, `player_hero`, `boss`, demais characters, animation, ui, fx.

- [ ] **Step 3: Criar CLI fina**

Interface exata:

```powershell
param(
    [Parameter(Mandatory)][string]$RequestText,
    [Parameter(Mandatory)][string]$ProjectRoot,
    [Parameter(Mandatory)][string]$OutputPath,
    [Parameter(Mandatory)][string]$CompactOutputPath,
    [ValidateSet('auto','pt','en')][string]$Language = 'auto',
    [string]$RulesPath = '',
    [switch]$SkipGraphify
)
```

- [ ] **Step 4: Criar schema Draft-07**

O schema deve exigir `detected_intents`, `detected_targets`, `required_owners`, `dispatch`, `runtime_admission`, `compact_context_bytes`, `ambiguity_status` e `fallback_decision`. `additionalProperties=false` em targets e intents.

- [ ] **Step 5: Registrar pipeline, workflow e dispatch explicito**

Adicionar `vibe_playable_loop_v1.json` ao framework manifest; adicionar `art/art-direction-selector` como lifecycle `active`, `legacy_path:null`, replacement vazio; adicionar rota `natural_visible_game_request` ao curated map sem alterar `allow_implicit_invocation:false`.

- [ ] **Step 6: Rodar GREEN e regressao de routing**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_vibe_playable_router.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_active_skill_routing.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_skill_lifecycle_registry.ps1
```

Expected: todos PASS; `art-direction-selector` continua implicitamente desabilitado e aparece na rota explicita.

- [ ] **Step 7: Verificar worktree e commit da fase**

```powershell
git diff --check -- tools/sgdk_wrapper
$Phase1Files = @(
  'tools/sgdk_wrapper/.agent/references/vibe_playable_intent_rules.json',
  'tools/sgdk_wrapper/schemas/vibe_playable_route_report.schema.json',
  'tools/sgdk_wrapper/lib/vibe_playable_router.psm1',
  'tools/sgdk_wrapper/route_vibe_playable_request.ps1',
  'tools/sgdk_wrapper/.agent/pipelines/vibe_playable_loop_v1.json',
  'tools/sgdk_wrapper/.agent/workflows/vibe-playable-loop.md',
  'tools/sgdk_wrapper/ci/test_vibe_playable_router.ps1',
  'tools/sgdk_wrapper/.agent/framework_manifest.json',
  'tools/sgdk_wrapper/.agent/references/skill_lifecycle_registry.json',
  'tools/sgdk_wrapper/.agent/references/aaa_pipeline_curated_skill_map.json',
  'tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json',
  'tools/sgdk_wrapper/.agent/workflows/production-loop.md',
  'tools/sgdk_wrapper/.agent/workflows/aaa-scene-pipeline.md',
  'tools/sgdk_wrapper/ci/test_active_skill_routing.ps1'
)
git add -N -- $Phase1Files
git add -p -- $Phase1Files
git diff --cached -- $Phase1Files | Tee-Object out/ci/vibe_playable_phase1_cached.diff
$UnexpectedCached = @(git diff --cached --name-only | Where-Object { $Phase1Files -notcontains $_ })
if ($UnexpectedCached.Count -ne 0) { throw "unexpected staged files: $($UnexpectedCached -join ', ')" }
# Revisar out/ci/vibe_playable_phase1_cached.diff: todo hunk staged deve ter sido produzido nesta fase; se houver hunk preexistente, nao commitar.
git commit -m "feat: add deterministic vibe playable routing"
$PhaseCommit = git rev-parse HEAD
```

**Conclusao da fase:** pedidos PT/EN geram intents/targets deterministas; heroi e boss permanecem distintos; runtime owner nunca antecede owners visuais.

**Rollback:** `git revert $PhaseCommit` remove somente roteador, schema e superficies registradas.

---

## Fase 2: extensao compativel do `premium_source_manifest`

### Task 3: normalizacao legacy e schema unico

**Files:** todos os arquivos da Fase 2 listados no inventario.

- [ ] **Step 1: Escrever fixtures e teste RED**

O teste deve exigir:

```powershell
Assert-True ($v1Single.normalized.assets.Count -eq 1) 'single legacy manifest not normalized'
Assert-True ($v1Root.normalized.assets.Count -ge 2) 'root legacy manifest assets not preserved'
Assert-True (@($v1Root.normalized.assets | Where-Object { $_.source_sha256 -match '^[A-Fa-f0-9]{64}$' }).Count -eq $v1Root.normalized.assets.Count) 'root legacy assets missing real hashes'
Assert-True ($v2.status -eq 'passed') 'extended canonical manifest rejected'
Assert-True ($unknown.blocking_statuses -contains 'unknown_authoring_method') 'unknown source promoted'
Assert-True (-not (Test-Path "$WrapperRoot/schemas/premium_visual_source_manifest.schema.json")) 'duplicate schema created'
```

- [ ] **Step 2: Rodar RED**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_premium_source_manifest_compatibility.ps1
```

Expected: FAIL por schema/validator ausentes.

- [ ] **Step 3: Criar schema unico com `oneOf` compatível**

O schema aceita `1.x` single-asset, `1.x` root `assets[]` com assets reais preservados e `2.0.0` estendido. Somente `2.0.0` pode obter `production_source_ready=true`. Campos novos obrigatorios por asset:

```json
["asset_id","asset_role","criticality","authoring_method","source_origin","source_classification","tool","source_files","transformations","variants"]
```

Classificacoes permitidas: `human_authored`, `generated_bitmap`, `licensed_source`, `procedural_debug`, `unknown`.

- [ ] **Step 4: Implementar normalizador sem escrita in-place**

`premium_source_manifest.psm1` exporta:

```powershell
ConvertTo-CanonicalPremiumSourceManifest
Test-PremiumSourceManifest
Get-PremiumSourceProductionBlockers
```

O CLI escreve somente `out/logs/premium_source_manifest_report.json`; `-NormalizedOutputPath` e opt-in e nunca sobrescreve o manifest original.

- [ ] **Step 5: Atualizar owners/workflows existentes**

Substituir listas informais de campos pelo schema canonico. Nao criar outro manifesto, sidecar de autoria ou nova skill.

- [ ] **Step 6: Rodar GREEN e schemas**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_premium_source_manifest_compatibility.ps1
uv run --with jsonschema python tools/sgdk_wrapper/ci/test_schema_contract_gates.py
```

Expected: legacy normalizado sem promocao falsa; v2 valido passa; `unknown` e `procedural_debug` bloqueiam producao.

- [ ] **Step 7: Commit**

```powershell
$Phase2Files = @(
  'tools/sgdk_wrapper/schemas/premium_source_manifest.schema.json',
  'tools/sgdk_wrapper/lib/premium_source_manifest.psm1',
  'tools/sgdk_wrapper/validate_premium_source_manifest.ps1',
  'tools/sgdk_wrapper/ci/test_premium_source_manifest_compatibility.ps1',
  'tools/sgdk_wrapper/ci/fixtures/vibe_playable/premium_source/v1_single.json',
  'tools/sgdk_wrapper/ci/fixtures/vibe_playable/premium_source/v1_root.json',
  'tools/sgdk_wrapper/ci/fixtures/vibe_playable/premium_source/v2_valid.json',
  'tools/sgdk_wrapper/ci/fixtures/vibe_playable/premium_source/v2_unknown.json',
  'tools/sgdk_wrapper/.agent/skills/art/art-creation-sourcing/SKILL.md',
  'tools/sgdk_wrapper/.agent/workflows/premium-art-pipeline.md',
  'tools/sgdk_wrapper/.agent/pipelines/vibe_playable_loop_v1.json',
  'tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json',
  'tools/sgdk_wrapper/ci/test_schema_contract_gates.py'
)
git add -N -- $Phase2Files
git add -p -- $Phase2Files
git diff --cached -- $Phase2Files | Tee-Object out/ci/vibe_playable_phase2_cached.diff
$UnexpectedCached = @(git diff --cached --name-only | Where-Object { $Phase2Files -notcontains $_ })
if ($UnexpectedCached.Count -ne 0) { throw "unexpected staged files: $($UnexpectedCached -join ', ')" }
# Revisar out/ci/vibe_playable_phase2_cached.diff: todo hunk staged deve ter sido produzido nesta fase; se houver hunk preexistente, nao commitar.
git commit -m "feat: extend canonical premium source manifest"
$PhaseCommit = git rev-parse HEAD
```

**Conclusao da fase:** existe um unico schema/manifest; legacy continua legivel; campos ausentes nunca sao inventados.

**Rollback:** `git revert $PhaseCommit` restaura consumidores antigos e remove somente schema/normalizador novos.

---

## Fase 3: tres admissoes de runtime e tetos de claims

### Task 4: admission report, escopo tecnico e propagacao de teto

**Files:** todos os arquivos da Fase 3 listados no inventario.

- [ ] **Step 1: Escrever teste RED com matriz de admissao**

Casos obrigatorios:

```powershell
Assert-Admission visual_ready runtime_admitted visual_delivery_candidate
Assert-Admission logic_only technical_runtime_admitted technical_only
Assert-Admission explicit_lab runtime_lab_admitted technical_lab_validated
Assert-Blocked technical_with_res_change technical_scope_visual_change_detected
Assert-Blocked visual_without_route vibe_visual_route_missing
Assert-NoVisualPromotion technical_runtime_admitted
Assert-NoVisualPromotion runtime_lab_admitted
```

- [ ] **Step 2: Rodar RED**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_runtime_admission.ps1
```

Expected: FAIL por evaluator e schemas ausentes.

- [ ] **Step 3: Criar os dois schemas**

`runtime_admission_report` exige `admission_type`, `route_report_sha256`, `input_fingerprint`, `claim_ceiling`, `visual_status_promotion_allowed`, `blocking_statuses` e `evidence_refs`.

`technical_change_scope_report` exige listas `changed_files`, `changed_contracts`, `visual_sensitive_hits` e flags para `assets`, `composition`, `presentation`, `camera`, `palette`, `ui`, `animation`, `fx`.

- [ ] **Step 4: Implementar evaluator**

`runtime_admission.psm1` exporta:

```powershell
Get-RuntimeAdmissionType
Test-TechnicalChangeScope
Get-RuntimeClaimCeiling
New-RuntimeAdmissionReport
```

Tetos exatos:

```text
runtime_admitted           -> visual_delivery_candidate (ainda nao aprovado)
technical_runtime_admitted -> technical_runtime_validated
runtime_lab_admitted       -> technical_lab_validated + lab_not_delivery
blocked                    -> no_runtime_admission
```

- [ ] **Step 5: Integrar build, promotion audit e validator**

`build.bat` chama `evaluate_runtime_admission.ps1` somente quando existe `vibe_playable_route_report.json` ou quando o projeto declara `vibe_playable_loop_v1`. Projetos legacy sem essa declaracao continuam buildando, mas nao ganham claims visuais novos.

`audit_promotion_claims.ps1` e `validate_resources.ps1` devem adicionar blockers `vibe_visual_route_missing`, `runtime_admission_missing`, `technical_runtime_visual_promotion_attempt` e `lab_runtime_visual_promotion_attempt`.

- [ ] **Step 6: Rodar GREEN e regressao rapida**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_runtime_admission.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_validation_report_visual_gate_blocker.ps1
```

Expected: matriz passa e validacao visual antiga continua bloqueando falsos positivos.

- [ ] **Step 7: Commit**

```powershell
$Phase3Files = @(
  'tools/sgdk_wrapper/schemas/runtime_admission_report.schema.json',
  'tools/sgdk_wrapper/schemas/technical_change_scope_report.schema.json',
  'tools/sgdk_wrapper/lib/runtime_admission.psm1',
  'tools/sgdk_wrapper/evaluate_runtime_admission.ps1',
  'tools/sgdk_wrapper/ci/test_runtime_admission.ps1',
  'tools/sgdk_wrapper/build.bat',
  'tools/sgdk_wrapper/audit_promotion_claims.ps1',
  'tools/sgdk_wrapper/validate_resources.ps1',
  'tools/sgdk_wrapper/schemas/promotion_claim_manifest.schema.json',
  'tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md',
  'tools/sgdk_wrapper/.agent/skills/code/sgdk-runtime-coder/SKILL.md',
  'tools/sgdk_wrapper/.agent/workflows/vibe-playable-loop.md',
  'tools/sgdk_wrapper/.agent/pipelines/vibe_playable_loop_v1.json'
)
git add -N -- $Phase3Files
git add -p -- $Phase3Files
git diff --cached -- $Phase3Files | Tee-Object out/ci/vibe_playable_phase3_cached.diff
$UnexpectedCached = @(git diff --cached --name-only | Where-Object { $Phase3Files -notcontains $_ })
if ($UnexpectedCached.Count -ne 0) { throw "unexpected staged files: $($UnexpectedCached -join ', ')" }
# Revisar out/ci/vibe_playable_phase3_cached.diff: todo hunk staged deve ter sido produzido nesta fase; se houver hunk preexistente, nao commitar.
git commit -m "feat: enforce runtime admission claim ceilings"
$PhaseCommit = git rev-parse HEAD
```

**Conclusao da fase:** tres admissoes mutuamente exclusivas; tecnica/lab nunca promovem visual; build legacy preservado.

**Rollback:** `git revert $PhaseCommit` remove o pre-build gate e a propagacao de claims sem tocar em assets/projetos.

---

## Fase 4: autoria procedural e validators

### Task 5: detectar autoria proibida e preservar processadores permitidos

**Files:** todos os arquivos da Fase 4 listados no inventario.

- [ ] **Step 1: Criar adversarios e teste RED**

Os quatro adversarios devem conter sinais reais sem serem executados:

```text
Pillow: ImageDraw.rectangle/polygon/ellipse/text
SVG: elementos rect, polygon e linearGradient
Canvas: fillRect, lineTo, arc, fillText, createLinearGradient
C: VDP_drawText, VDP_fillTileMapRect, loop que escreve tiles esteticos
```

`quantize_only.py` usa apenas `Image.open`, `convert('P')`, paleta e save, com input/output declarados.

Assercoes:

```powershell
Assert-LabOnly pillow_character.py
Assert-LabOnly svg_stage.svg
Assert-LabOnly canvas_hud.html
Assert-LabOnly c_primitives_fx.c
Assert-AllowedProcessor quantize_only.py operation_class=quantize
Assert-BlockedCriticalSource source_classification=unknown
```

- [ ] **Step 2: Rodar RED**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_visual_authoring_policy.ps1
```

Expected: FAIL porque o auditor ainda nao classifica authoring APIs.

- [ ] **Step 3: Implementar auditor por manifest + sinais estaticos**

O auditor aceita `-ProjectRoot`, `-PremiumSourceManifestPath`, `-OutputPath`. Ele nunca decide apenas pela extensao. Ordem:

1. validar classificacao e authoring method;
2. validar lineage input/output das transformacoes;
3. escanear sinais de autoria procedural;
4. cruzar com papel/criticidade;
5. emitir `passed`, `lab_not_delivery` ou `blocked`.

Operation classes permitidas:

```json
["convert","quantize","crop","tile_assembly","atlas_assembly","mask_generation","metrics","diagnostic","review_preview"]
```

- [ ] **Step 4: Integrar quarantine, visual gate e direcao**

`audit_placeholder_quarantine.ps1` absorve o report; `visual_delivery_gate_report` referencia `visual_authoring_report`; `art_gameplay_direction_gate` exige `premium_source_manifest_ref` para asset critico.

- [ ] **Step 5: Rodar GREEN**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_visual_authoring_policy.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_visual_gate_lab_fallback_blockers.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_visual_delivery_gate_report_blocks.ps1
```

Expected: quatro adversarios em `lab_not_delivery`; processador permitido passa; gates antigos continuam verdes.

- [ ] **Step 6: Commit**

```powershell
$Phase4Files = @(
  'tools/sgdk_wrapper/schemas/visual_authoring_report.schema.json',
  'tools/sgdk_wrapper/audit_visual_authoring.ps1',
  'tools/sgdk_wrapper/ci/test_visual_authoring_policy.ps1',
  'tools/sgdk_wrapper/ci/fixtures/vibe_playable/procedural_adversarial/pillow_character.py',
  'tools/sgdk_wrapper/ci/fixtures/vibe_playable/procedural_adversarial/svg_stage.svg',
  'tools/sgdk_wrapper/ci/fixtures/vibe_playable/procedural_adversarial/canvas_hud.html',
  'tools/sgdk_wrapper/ci/fixtures/vibe_playable/procedural_adversarial/c_primitives_fx.c',
  'tools/sgdk_wrapper/ci/fixtures/vibe_playable/procedural_adversarial/quantize_only.py',
  'tools/sgdk_wrapper/audit_placeholder_quarantine.ps1',
  'tools/sgdk_wrapper/validate_resources.ps1',
  'tools/sgdk_wrapper/schemas/art_gameplay_direction_gate.schema.json',
  'tools/sgdk_wrapper/schemas/visual_delivery_gate_report.schema.json',
  'tools/sgdk_wrapper/.agent/skills/art/art-asset-diagnostic/SKILL.md',
  'tools/sgdk_wrapper/.agent/skills/art/visual-excellence-standards/SKILL.md',
  'tools/sgdk_wrapper/.agent/workflows/vibe-playable-loop.md'
)
git add -N -- $Phase4Files
git add -p -- $Phase4Files
git diff --cached -- $Phase4Files | Tee-Object out/ci/vibe_playable_phase4_cached.diff
$UnexpectedCached = @(git diff --cached --name-only | Where-Object { $Phase4Files -notcontains $_ })
if ($UnexpectedCached.Count -ne 0) { throw "unexpected staged files: $($UnexpectedCached -join ', ')" }
# Revisar out/ci/vibe_playable_phase4_cached.diff: todo hunk staged deve ter sido produzido nesta fase; se houver hunk preexistente, nao commitar.
git commit -m "feat: quarantine procedural visual authoring"
$PhaseCommit = git rev-parse HEAD
```

**Conclusao da fase:** PNG existente nao prova autoria; authoring procedural/unknown bloqueia criticidade; conversao rastreada continua permitida.

**Rollback:** `git revert $PhaseCommit` remove apenas auditor e novos campos; placeholder quarantine anterior permanece funcional.

---

## Fase 5: rastreabilidade asset -> ROM -> BlastEm

### Task 6: build meta, approval asset-scoped e evidence seal

**Files:** todos os arquivos da Fase 5 listados no inventario.

- [ ] **Step 1: Escrever fixture humana imutavel e teste RED**

`fixture_manifest.json` fixa SHA-256 de `doc/human_approval_record.md`, do painel imutavel `data/processed/reports/asset_approval_panel.png` e do parecer `data/processed/reports/asset_visual_delivery_gate_report.json`. O Markdown contem bloco machine-readable com:

```yaml
approval_scope: asset
asset_id: fixture_hero
source_sha256: 64-hex
converted_sha256: 64-hex
visual_excellence_report_path: data/processed/reports/asset_visual_delivery_gate_report.json
visual_excellence_report_sha256: 64-hex
asset_approval_panel_path: data/processed/reports/asset_approval_panel.png
asset_approval_panel_sha256: 64-hex
approved_by: human_fixture_reviewer
decision: approved
```

O teste copia a fixture sem editar e valida:

```powershell
Assert-True $trace.asset_approval_fresh 'preapproved asset record rejected'
Assert-True $trace.runtime_evidence_fresh 'matching ROM evidence rejected'
Assert-True ($trace.links.rescomp_link.kind -eq 'manifest_link') 'raw asset hash inferred from ROM'
Assert-True ($trace.asset_approval_panel_sha256 -eq $trace.human_record.asset_approval_panel_sha256) 'approval panel hash drifted'
Assert-True ($trace.visual_excellence_report_sha256 -eq $trace.human_record.visual_excellence_report_sha256) 'visual excellence report hash drifted'
Assert-True (-not $rebuilt.runtime_evidence_fresh) 'new ROM did not stale runtime evidence'
Assert-True $rebuilt.asset_approval_fresh 'new ROM incorrectly invalidated unchanged asset approval'
```

- [ ] **Step 2: Rodar RED**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_visual_asset_traceability.ps1
```

Expected: FAIL por schema/auditor/build fields ausentes.

- [ ] **Step 3: Criar schemas e auditor agregado**

`build_meta.schema.json` formaliza `rom_sha256`, `res_entries`, `route_report_sha256`, `runtime_admission_sha256` e `source_commit_when_available`.

`visual_asset_traceability_report.schema.json` exige elos separados:

```text
premium_source -> converted_asset -> res_declaration -> rescomp/build_meta -> rom -> emulator_session -> evidence artifacts
```

Nenhum campo declara que o PNG hash foi extraido da ROM.

`visual_delivery_gate_report.schema.json` passa a ser o schema canonico tambem para o parecer de `visual-excellence-standards`. Campos minimos obrigatorios:

```text
schema_version
scope = asset_approval | runtime_evidence
owner = skills/art/visual-excellence-standards
target_ids[]
source_hashes[]
converted_hashes[]
panel.path
panel.sha256
criteria.identity | materials | silhouette | depth | movement
structural_metrics
decision = passed | failed | blocked
decision_rationale
generated_at
content_sha256
```

O SHA-256 do arquivo completo do report fica fora do proprio report, em `human_approval_record.md`, `fixture_manifest.json` ou `vibe_playable_e2e_report.json`. O campo `content_sha256` e calculado sobre o JSON canonico sem o proprio campo de hash.

No escopo `runtime_evidence`, o mesmo schema tambem exige `rom_sha256`, `blastem_session_sha256`, `runtime_screenshot_sha256`, `runtime_comparison_panel_sha256` e `asset_visual_delivery_gate_report_sha256`.

- [ ] **Step 4: Estender produtores canonicos existentes**

- `update_project_changelog.ps1`: gravar hashes dos assets convertidos, declaracao `.res`, report ResComp e route/admission.
- `capture_blastem_evidence.ps1`: gravar build meta path/hash, scene id e target ids.
- `finalize_emulator_evidence.ps1`: selar ROM + artefatos + build meta, sem alterar approval record.
- `freshness_audit.ps1`: separar `asset_approval_fresh` de `runtime_evidence_fresh`.
- `scene_closeout_gate.ps1`: chamar `audit_visual_asset_traceability.ps1` antes da promocao.
- `visual_delivery_gate_report.json`: aceitar `visual_excellence=passed` somente quando o relatorio canonico validar contra schema, o runner recomputar `content_sha256` e o SHA-256 do arquivo completo referenciado externamente, e o report apontar para paineis/assets existentes.

- [ ] **Step 5: Rodar GREEN e evidence regressions**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_visual_asset_traceability.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_evidence_closeout_seal.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_freshness_audit.ps1
```

Expected: cadeia completa passa; rebuild invalida somente runtime evidence; adulterar approval record quebra hash.

- [ ] **Step 6: Commit**

```powershell
$Phase5Files = @(
  'tools/sgdk_wrapper/schemas/build_meta.schema.json',
  'tools/sgdk_wrapper/schemas/visual_asset_traceability_report.schema.json',
  'tools/sgdk_wrapper/audit_visual_asset_traceability.ps1',
  'tools/sgdk_wrapper/ci/test_visual_asset_traceability.ps1',
  'tools/sgdk_wrapper/ci/fixtures/vibe_playable/approval/doc/human_approval_record.md',
  'tools/sgdk_wrapper/ci/fixtures/vibe_playable/approval/data/processed/reports/asset_approval_panel.png',
  'tools/sgdk_wrapper/ci/fixtures/vibe_playable/approval/data/processed/reports/asset_visual_delivery_gate_report.json',
  'tools/sgdk_wrapper/ci/fixtures/vibe_playable/approval/fixture_manifest.json',
  'tools/sgdk_wrapper/update_project_changelog.ps1',
  'tools/sgdk_wrapper/capture_blastem_evidence.ps1',
  'tools/sgdk_wrapper/finalize_emulator_evidence.ps1',
  'tools/sgdk_wrapper/freshness_audit.ps1',
  'tools/sgdk_wrapper/scene_closeout_gate.ps1',
  'tools/sgdk_wrapper/validate_resources.ps1',
  'tools/sgdk_wrapper/schemas/visual_delivery_gate_report.schema.json',
  'tools/sgdk_wrapper/ci/test_evidence_closeout_seal.ps1',
  'tools/sgdk_wrapper/.agent/skills/art/visual-excellence-standards/references/source_to_rom_visual_gate.md',
  'tools/sgdk_wrapper/.agent/skills/operation/emulator-vdp-evidence-curator/SKILL.md'
)
$Phase5NewBinaryFiles = @(
  'tools/sgdk_wrapper/ci/fixtures/vibe_playable/approval/data/processed/reports/asset_approval_panel.png'
)
$Phase5Baseline = Get-Content out/ci/vibe_playable_phase5_file_baseline.json -Raw | ConvertFrom-Json
$BinaryAlreadyExisted = @($Phase5NewBinaryFiles | Where-Object {
  $Candidate = $_
  @($Phase5Baseline.files | Where-Object { $_.path -eq $Candidate -and $_.existed }).Count -ne 0
})
if ($BinaryAlreadyExisted.Count -ne 0) { throw "binary paths were not new at baseline: $($BinaryAlreadyExisted -join ', ')" }
git add -- $Phase5NewBinaryFiles
$Phase5TextPatchFiles = @($Phase5Files | Where-Object { $Phase5NewBinaryFiles -notcontains $_ })
git add -N -- $Phase5TextPatchFiles
git add -p -- $Phase5TextPatchFiles
git diff --cached -- $Phase5Files | Tee-Object out/ci/vibe_playable_phase5_cached.diff
$UnexpectedCached = @(git diff --cached --name-only | Where-Object { $Phase5Files -notcontains $_ })
if ($UnexpectedCached.Count -ne 0) { throw "unexpected staged files: $($UnexpectedCached -join ', ')" }
# Revisar out/ci/vibe_playable_phase5_cached.diff: todo hunk staged deve ter sido produzido nesta fase; se houver hunk preexistente, nao commitar.
git commit -m "feat: seal visual assets through BlastEm evidence"
$PhaseCommit = git rev-parse HEAD
```

**Conclusao da fase:** cada elo tem hash proprio; ResComp e build manifest fazem a ponte; approval e runtime freshness sao independentes.

**Rollback:** `git revert $PhaseCommit` restaura build meta/evidence anteriores; snapshots historicos nao sao reescritos.

---

## Fase 6: cache, warm start e orçamento de contexto

### Task 7: fingerprints, cache seletivo e Graphify degradavel

**Files:** todos os arquivos da Fase 6 listados no inventario.

- [ ] **Step 1: Escrever teste RED instrumentado**

O teste usa callbacks contadores, nao tempo de parede como verdade principal:

```powershell
Assert-Equal 1 $cold.graphify_attempts
Assert-Equal 1 $cold.diagnostic_runs
Assert-Equal 0 $warm.graphify_rebuilds
Assert-Equal 0 $warm.diagnostic_runs
Assert-True ($warm.compact_context_bytes -le 32768)
Assert-SetEqual $expectedOwners $warm.owners_loaded
Assert-SetEqual $expectedFiles $warm.files_loaded
Assert-True $warm.reused.direction
Assert-True $warm.reused.sources
Assert-True $warm.reused.asset_approval
```

Tambem simular Graphify timeout e exigir `consultive_index_unavailable` com exit code de rota 0.

- [ ] **Step 2: Rodar RED**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_vibe_playable_cache_and_context.ps1
```

Expected: FAIL por modulo/cache policy ausentes.

- [ ] **Step 3: Implementar cache por fingerprints**

`vibe_playable_cache.psm1` exporta:

```powershell
Get-VibeInputFingerprint
Get-VibeCacheDecision
Read-VibeCacheRecord
Write-VibeCacheRecord
Split-VibeCompactContextByTarget
```

Cache record exige hashes de request/ruleset/project context, asset inventory, direction inputs, premium sources, approval chain e ROM/build evidence.

- [ ] **Step 4: Tornar Graphify consultivo no caminho quente**

No roteador: no maximo uma chamada `status` com timeout curto configuravel; se `fresh`, usar cache; se missing/stale/timeout, registrar degradacao e ler arquivos canonicos. Nunca chamar `build` no pedido.

Nos scripts de ambiente ja modificados no worktree: aplicar hunk minimo que diferencia `interactive_request` de `explicit_maintenance`. Rebuild completo continua disponivel somente por comando explicito.

- [ ] **Step 5: Rodar GREEN e testes de ambiente**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_vibe_playable_cache_and_context.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_agent_startup_environment.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_graphify_update_failure.ps1
```

Expected: warm start sem rebuild/diagnostico; timeout Graphify nao bloqueia rota; manutencao explicita ainda pode rebuildar.

- [ ] **Step 6: Auditar sobreposicao com worktree preexistente**

```powershell
git diff -- tools/sgdk_wrapper/assert_agent_environment.ps1 tools/sgdk_wrapper/prepare_agent_environment.ps1 tools/sgdk_wrapper/graphify_forge.ps1
```

Confirmar visualmente que os hunks de ai-memory/Graphify preexistentes permanecem intactos.

- [ ] **Step 7: Commit**

```powershell
$Phase6Files = @(
  'tools/sgdk_wrapper/schemas/vibe_playable_cache_report.schema.json',
  'tools/sgdk_wrapper/lib/vibe_playable_cache.psm1',
  'tools/sgdk_wrapper/ci/test_vibe_playable_cache_and_context.ps1',
  'tools/sgdk_wrapper/route_vibe_playable_request.ps1',
  'tools/sgdk_wrapper/lib/vibe_playable_router.psm1',
  'tools/sgdk_wrapper/assert_agent_environment.ps1',
  'tools/sgdk_wrapper/prepare_agent_environment.ps1',
  'tools/sgdk_wrapper/graphify_forge.ps1',
  'tools/sgdk_wrapper/ci/test_agent_startup_environment.ps1',
  'tools/sgdk_wrapper/ci/test_graphify_update_failure.ps1',
  'tools/sgdk_wrapper/.agent/workflows/agent-startup-environment.md',
  'doc/GRAPHIFY_OBSIDIAN_POLICY.md'
)
git add -N -- $Phase6Files
git add -p -- $Phase6Files
git diff --cached -- $Phase6Files | Tee-Object out/ci/vibe_playable_phase6_cached.diff
$UnexpectedCached = @(git diff --cached --name-only | Where-Object { $Phase6Files -notcontains $_ })
if ($UnexpectedCached.Count -ne 0) { throw "unexpected staged files: $($UnexpectedCached -join ', ')" }
# Revisar out/ci/vibe_playable_phase6_cached.diff: todo hunk staged deve ter sido produzido nesta fase; se houver hunk preexistente, nao commitar.
git commit -m "perf: cache vibe context and bound Graphify attempts"
$PhaseCommit = git rev-parse HEAD
```

**Conclusao da fase:** cold/warm mensuraveis; zero rebuild fresh; diagnostico nao repete; contexto <=32 KiB ou split sem perda.

**Rollback:** `git revert $PhaseCommit`; confirmar depois que as mudancas preexistentes nos tres scripts Graphify continuam presentes.

---

## Fase 7: fixtures contratuais e gate rapido

### Task 8: pacote PT/EN, matriz contratual e runner rapido

**Files:** todos os arquivos da Fase 7 listados no inventario, mais fixtures criadas nas Fases 2, 4 e 5.

- [ ] **Step 1: Criar `requests.json` e teste RED de cobertura**

O fixture pack deve ter IDs e expected blockers para, no minimo:

```text
pt_create_game
pt_stage_hero_boss
pt_add_character
pt_animate_attack
pt_improve_scenery
en_create_game
en_stage_hero_boss
en_add_character
en_animate_attack
en_improve_hud
ambiguous_visual_fallback
explicit_debug_lab
```

O teste falha se qualquer um dos 21 cenarios da spec nao estiver mapeado a pelo menos uma fixture automatica ou ao gate manual da Fase 8.

- [ ] **Step 2: Rodar RED**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_vibe_playable_contract_fixtures.ps1
```

Expected: FAIL ate o fixture pack e o mapa de cobertura existirem.

- [ ] **Step 3: Criar runner rapido fail-fast**

`run_vibe_playable_fast_tests.ps1` executa exatamente, nesta ordem:

```text
test_vibe_playable_router.ps1
test_premium_source_manifest_compatibility.ps1
test_runtime_admission.ps1
test_visual_authoring_policy.ps1
test_visual_asset_traceability.ps1
test_vibe_playable_cache_and_context.ps1
test_vibe_playable_contract_fixtures.ps1
test_active_skill_routing.ps1
test_skill_lifecycle_registry.ps1
test_schema_contract_gates.py
```

Ele gera `out/ci/vibe_playable_fast_report.json` e nao importa nem chama modulos BlastEm.

- [ ] **Step 4: Registrar apenas o fast gate no contrato geral**

`run_all_contract_gates.ps1` chama o runner rapido. Nao registrar `run_vibe_playable_blastem_gate.ps1` nesse arquivo.

- [ ] **Step 5: Rodar GREEN e regressao geral**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/run_vibe_playable_fast_tests.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/run_all_contract_gates.ps1 -Mode smoke
```

Expected: `vibe_playable_fast_report.json.status=passed`; nenhum processo BlastEm criado.

- [ ] **Step 6: Commit**

```powershell
$Phase7Files = @(
  'tools/sgdk_wrapper/ci/fixtures/vibe_playable/requests.json',
  'tools/sgdk_wrapper/ci/test_vibe_playable_contract_fixtures.ps1',
  'tools/sgdk_wrapper/ci/run_vibe_playable_fast_tests.ps1',
  'tools/sgdk_wrapper/ci/run_all_contract_gates.ps1',
  'tools/sgdk_wrapper/ci/test_schema_contract_gates.py',
  'tools/sgdk_wrapper/.agent/framework_manifest.json'
)
git add -N -- $Phase7Files
git add -p -- $Phase7Files
git diff --cached -- $Phase7Files | Tee-Object out/ci/vibe_playable_phase7_cached.diff
$UnexpectedCached = @(git diff --cached --name-only | Where-Object { $Phase7Files -notcontains $_ })
if ($UnexpectedCached.Count -ne 0) { throw "unexpected staged files: $($UnexpectedCached -join ', ')" }
# Revisar out/ci/vibe_playable_phase7_cached.diff: todo hunk staged deve ter sido produzido nesta fase; se houver hunk preexistente, nao commitar.
git commit -m "test: add vibe playable contract fixtures"
$PhaseCommit = git rev-parse HEAD
```

**Conclusao da fase:** todas as regras contratuais e adversariais rodam rapidamente e separadas do emulador.

**Rollback:** `git revert $PhaseCommit` remove apenas agregador/fixtures; testes unitarios das fases anteriores continuam executaveis.

---

## Fase 8: fixture visual real e checkpoint humano

### Task 9: bootstrap LAB, fonte bitmap real e checkpoint de asset

**Files:** arquivos do projeto LAB listados no inventario, exceto `out/` gerado.

Em todos os comandos desta fase:

```powershell
$FixtureRoot = Join-Path (Get-Location) 'SGDK_projects\_agent_laboratory\VIBE_PLAYABLE_LOOP_FIXTURE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]'
```

- [ ] **Step 1: Criar teste/runner RED antes do projeto**

`run_vibe_playable_blastem_gate.ps1` deve sair com codigo 2 e:

```text
manual_checkpoint_required: human_asset_approval_missing
```

quando o projeto, a fonte ou o approval record ainda nao existirem. O runner nunca cria o approval record.

O mesmo RED deve incluir uma fixture adversarial de E2E com `visual_excellence=passed` textual, mas sem `out/logs/visual_delivery_gate_report.json` valido. Resultado esperado: exit 2 com `visual_excellence_report_missing_or_invalid`.

`vibe_playable_e2e_report.schema.json` exige objeto:

```json
{
  "visual_excellence": {
    "status": "passed",
    "report_path": "out/logs/visual_delivery_gate_report.json",
    "report_sha256": "64-hex",
    "schema_path": "tools/sgdk_wrapper/schemas/visual_delivery_gate_report.schema.json",
    "content_sha256": "64-hex",
    "criteria_passed": true,
    "runtime_panel_sha256": "64-hex"
  }
}
```

- [ ] **Step 2: Rodar RED**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/run_vibe_playable_blastem_gate.ps1 -ProjectRoot "SGDK_projects/_agent_laboratory/VIBE_PLAYABLE_LOOP_FIXTURE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]"
```

Expected: exit 2, checkpoint humano ausente, nenhum build/captura iniciado.

- [ ] **Step 3: Bootstrap e validar contexto LAB**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/adopt_project_methodology.ps1 -ProjectRoot $FixtureRoot
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/validate_project_context.ps1 -ProjectRoot $FixtureRoot
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/validate_project_hygiene.ps1 -ProjectRoot $FixtureRoot
```

Expected: contexto `technical_demo`/LAB valido e `lab_not_delivery=true` durante construcao da fixture.

- [ ] **Step 4: Produzir fonte premium bitmap sem primitivas procedurais**

Usar image generation ou fonte licenciada para persistir exatamente cinco bitmaps-fonte listados no inventario. Para geracao, registrar canal, ferramenta, modelo, prompt/receipt e seeds no `premium_source_manifest`. Proibido usar Pillow/SVG/Canvas/C para desenhar esses arquivos.

Prompt-base de direcao para a familia:

```text
Original 16-bit dark-fantasy Mega Drive production source, side-view playable stage,
distinct masked hero confronting a massive stone-and-brass boss, clear silhouettes,
layered depth, readable materials, hard pixel clusters, no gradients, no antialiasing,
no logos, no existing IP, consistent model-sheet proportions and action key poses.
```

- [ ] **Step 5: Traduzir/processar para VDP e gerar motion previews**

Somente ferramentas de conversao/quantizacao/corte/atlas podem produzir `data/processed` e `res`. Gerar WebP a partir dos strips finais sem desenhar frames novos. Validar indexacao, PLTE, grid 8x8, pivots, motion phases e budget.

- [ ] **Step 6: Montar painel de aprovacao**

`data/processed/reports/asset_approval_panel.png` mostra fonte, basic, elite e previews de movimento, em escala nativa e ampliada. O painel registra hashes de fonte/convertido/motion preview e ainda nao inclui BlastEm.

Gerar tambem `data/processed/reports/asset_visual_delivery_gate_report.json`, validado por `tools/sgdk_wrapper/schemas/visual_delivery_gate_report.schema.json` com `scope=asset_approval`. Esse parecer e produzido pelo owner `skills/art/visual-excellence-standards`, inclui criterios de identidade, materiais, silhueta, profundidade e movimento, e recebe hash SHA-256 fixado antes do checkpoint.

- [ ] **Step 7: PARAR para checkpoint humano real**

Apresentar ao usuario os cinco bitmaps-fonte, tres assets convertidos, dois motion previews, `asset_approval_panel.png`, hashes e `asset_visual_delivery_gate_report.json`. O usuario escreve/aprova a entrada asset-scoped em `doc/human_approval_record.md`, vinculada aos hashes do painel imutavel e do parecer canonico.

O agente nao pode preencher `approved_by`, `decision=approved` ou assinatura em nome do usuario. Sem aprovacao, status da Task 9 permanece `manual_checkpoint_required` e a Task 10 nao inicia.

**Conclusao da Task 9:** fonte real, conversao, motion preview, painel de aprovacao imutavel e parecer visual canonico existem; approval record humano referencia hashes exatos.

**Rollback antes do checkpoint:** remover somente o novo projeto LAB apos confirmar o caminho absoluto; nenhum arquivo do framework ou projeto existente e tocado.

### Task 10: ROM, BlastEm, traceability e aceite final

**Files:** runner/schema da Fase 8; `src/`, `res/` e docs do projeto LAB; `out/` gerado pelo wrapper.

- [ ] **Step 1: Validar approval record imutavel**

O runner calcula o hash do record e confirma source/converted hashes, `asset_approval_panel_sha256` e `visual_excellence_report_sha256`. Se divergir, sair 2 com `human_asset_approval_stale` antes do build. A Task 10 nunca escreve nem sobrescreve `data/processed/reports/asset_approval_panel.png`.

- [ ] **Step 2: Build central**

```powershell
cmd /c tools\sgdk_wrapper\build.bat $FixtureRoot
```

Expected: exit 0 e `(Join-Path $FixtureRoot 'out\rom.bin')` existente.

- [ ] **Step 3: Validacao estruturada e traceability pre-capture**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/validate_resources.ps1 -WorkDir $FixtureRoot
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/audit_visual_asset_traceability.ps1 -ProjectRoot $FixtureRoot -OutputPath (Join-Path $FixtureRoot 'out\logs\visual_asset_traceability_report.json')
```

Expected antes da captura: cadeia source->converted->.res->build->ROM passa; runtime evidence fica `pending_capture`, nao `passed`.

- [ ] **Step 4: Captura canonica BlastEm**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/capture_blastem_evidence.ps1 -ProjectRoot $FixtureRoot -CaptureMode canonical
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/finalize_emulator_evidence.ps1 -ProjectRoot $FixtureRoot
```

Expected: `emulator_session.json`, screenshot dedicado, `save.sram`, `visual_vdp_dump.bin` e `evidence_closeout_report.json` selados para o ROM SHA-256 atual.

- [ ] **Step 5: Painel final e comparacao**

Criar `out/logs/runtime_comparison_panel.png` como painel separado (`source + basic + elite + BlastEm`) usando apenas montagem de review permitida. Nao sobrescrever `data/processed/reports/asset_approval_panel.png`; o hash aprovado na Task 9 permanece imutavel.

Rodar `visual-excellence-standards` para gerar `out/logs/visual_delivery_gate_report.json` com `scope=runtime_evidence`. O runner valida esse JSON contra `tools/sgdk_wrapper/schemas/visual_delivery_gate_report.schema.json`, recomputa o hash do arquivo canonico, confirma `rom_sha256`, `blastem_session_sha256`, `runtime_screenshot_sha256`, `runtime_comparison_panel_sha256` e o hash do parecer asset-scope aprovado. O E2E rejeita qualquer `visual_excellence=passed` sem esse report valido.

- [ ] **Step 6: Rodar gate E2E GREEN**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/run_vibe_playable_blastem_gate.ps1 -ProjectRoot $FixtureRoot
```

Expected:

```text
build=passed
validation=passed
asset_approval_fresh=true
runtime_evidence_fresh=true
traceability=passed
blastem_gate=true
visual_excellence=passed
manual_checkpoint=approved
```

O runner grava `(Join-Path $FixtureRoot 'out\logs\vibe_playable_e2e_report.json')`; ele valida a aprovacao humana, nunca a cria. O campo `visual_excellence=passed` so aparece no resumo se `visual_excellence.report_path`, `visual_excellence.report_sha256`, `visual_excellence.schema_path`, `visual_excellence.criteria_passed=true` e `visual_excellence.runtime_panel_sha256` tiverem sido verificados.

- [ ] **Step 7: Provar invalidacao seletiva**

Em uma copia temporaria da fixture, alterar somente a ROM e confirmar:

```text
runtime_evidence_fresh=false
asset_approval_fresh=true
```

Nao modificar o projeto canonico para este teste.

- [ ] **Step 8: Atualizar memoria/changelog e commit**

Registrar claims exatos: fixture LAB testada, nao jogo release. Incluir ROM SHA-256 e paths de evidencia.

```powershell
$FixtureRelative = 'SGDK_projects/_agent_laboratory/VIBE_PLAYABLE_LOOP_FIXTURE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]'
$Phase8Files = @(
  'tools/sgdk_wrapper/schemas/vibe_playable_e2e_report.schema.json',
  'tools/sgdk_wrapper/ci/run_vibe_playable_blastem_gate.ps1',
  'tools/sgdk_wrapper/.agent/framework_manifest.json',
  'doc/06_AI_MEMORY_BANK.md',
  "$FixtureRelative/.mddev/project.json",
  "$FixtureRelative/build.bat",
  "$FixtureRelative/run.bat",
  "$FixtureRelative/doc/project_context_manifest.json",
  "$FixtureRelative/doc/project_methodology_manifest.json",
  "$FixtureRelative/doc/project_hygiene_manifest.json",
  "$FixtureRelative/doc/10-memory-bank.md",
  "$FixtureRelative/doc/11-gdd.md",
  "$FixtureRelative/doc/13-spec-cenas.md",
  "$FixtureRelative/doc/technique_usage_manifest.json",
  "$FixtureRelative/doc/human_approval_record.md",
  "$FixtureRelative/doc/changelog/changelog.md",
  "$FixtureRelative/doc/contracts/art_direction_decision_record.json",
  "$FixtureRelative/doc/contracts/master_style_manifest.json",
  "$FixtureRelative/doc/contracts/art_gameplay_direction_gate.json",
  "$FixtureRelative/doc/contracts/hero_animation_strip_contract.json",
  "$FixtureRelative/doc/contracts/boss_animation_strip_contract.json",
  "$FixtureRelative/data/source_art/premium_source_manifest.json",
  "$FixtureRelative/data/source_art/vibe_scene_v1/source_scene.png",
  "$FixtureRelative/data/source_art/vibe_hero_v1/model_sheet.png",
  "$FixtureRelative/data/source_art/vibe_hero_v1/hero_attack_strip.png",
  "$FixtureRelative/data/source_art/vibe_boss_v1/model_sheet.png",
  "$FixtureRelative/data/source_art/vibe_boss_v1/boss_attack_strip.png",
  "$FixtureRelative/data/processed/bgs/vibe_stage_elite.png",
  "$FixtureRelative/data/processed/sprites/vibe_hero_attack_elite.png",
  "$FixtureRelative/data/processed/sprites/vibe_boss_attack_elite.png",
  "$FixtureRelative/data/processed/reports/hero_motion_preview.webp",
  "$FixtureRelative/data/processed/reports/boss_motion_preview.webp",
  "$FixtureRelative/data/processed/reports/asset_approval_panel.png",
  "$FixtureRelative/data/processed/reports/asset_visual_delivery_gate_report.json",
  "$FixtureRelative/res/bgs/vibe_stage_elite.png",
  "$FixtureRelative/res/sprites/vibe_hero_attack_elite.png",
  "$FixtureRelative/res/sprites/vibe_boss_attack_elite.png",
  "$FixtureRelative/res/resources.res",
  "$FixtureRelative/src/main.c",
  "$FixtureRelative/src/system/runtime_probe.c",
  "$FixtureRelative/src/system/runtime_probe.h"
)
$Phase8NewBinaryFiles = @(
  "$FixtureRelative/data/source_art/vibe_scene_v1/source_scene.png",
  "$FixtureRelative/data/source_art/vibe_hero_v1/model_sheet.png",
  "$FixtureRelative/data/source_art/vibe_hero_v1/hero_attack_strip.png",
  "$FixtureRelative/data/source_art/vibe_boss_v1/model_sheet.png",
  "$FixtureRelative/data/source_art/vibe_boss_v1/boss_attack_strip.png",
  "$FixtureRelative/data/processed/bgs/vibe_stage_elite.png",
  "$FixtureRelative/data/processed/sprites/vibe_hero_attack_elite.png",
  "$FixtureRelative/data/processed/sprites/vibe_boss_attack_elite.png",
  "$FixtureRelative/data/processed/reports/hero_motion_preview.webp",
  "$FixtureRelative/data/processed/reports/boss_motion_preview.webp",
  "$FixtureRelative/data/processed/reports/asset_approval_panel.png",
  "$FixtureRelative/res/bgs/vibe_stage_elite.png",
  "$FixtureRelative/res/sprites/vibe_hero_attack_elite.png",
  "$FixtureRelative/res/sprites/vibe_boss_attack_elite.png"
)
$Phase8Baseline = Get-Content out/ci/vibe_playable_phase8_file_baseline.json -Raw | ConvertFrom-Json
$BinaryAlreadyExisted = @($Phase8NewBinaryFiles | Where-Object {
  $Candidate = $_
  @($Phase8Baseline.files | Where-Object { $_.path -eq $Candidate -and $_.existed }).Count -ne 0
})
if ($BinaryAlreadyExisted.Count -ne 0) { throw "binary paths were not new at baseline: $($BinaryAlreadyExisted -join ', ')" }
git add -- $Phase8NewBinaryFiles
$Phase8TextPatchFiles = @($Phase8Files | Where-Object { $Phase8NewBinaryFiles -notcontains $_ })
git add -N -- $Phase8TextPatchFiles
git add -p -- $Phase8TextPatchFiles
git diff --cached -- $Phase8Files | Tee-Object out/ci/vibe_playable_phase8_cached.diff
$UnexpectedCached = @(git diff --cached --name-only | Where-Object { $Phase8Files -notcontains $_ })
if ($UnexpectedCached.Count -ne 0) { throw "unexpected staged files: $($UnexpectedCached -join ', ')" }
# Revisar out/ci/vibe_playable_phase8_cached.diff: todo hunk staged deve ter sido produzido nesta fase; novos PNG/WebP so podem estar inteiros se ausentes no baseline.
git commit -m "test: prove vibe playable loop in BlastEm"
$PhaseCommit = git rev-parse HEAD
```

**Conclusao da fase:** fixture real possui fonte nao procedural, conversao VDP, motion preview, ROM, BlastEm, traceability, parecer estetico e approval humano fresco.

**Rollback:** `git revert $PhaseCommit` remove runner/schema/projeto fixture versionado. Evidencia gerada nao deve ser reutilizada depois do revert; freshness deve marca-la stale/ausente.

---

## Validacao final da implementacao

Executar nesta ordem, com saidas frescas:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/run_vibe_playable_fast_tests.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/run_all_contract_gates.ps1 -Mode smoke
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/run_vibe_playable_blastem_gate.ps1 -ProjectRoot "SGDK_projects/_agent_laboratory/VIBE_PLAYABLE_LOOP_FIXTURE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]"
```

Evidencias obrigatorias:

- `out/ci/vibe_playable_fast_report.json` com zero falhas;
- fixture `out/rom.bin` e SHA-256;
- fixture `out/logs/validation_report.json` sem blocker da rota visual;
- fixture `out/logs/visual_authoring_report.json` sem autoria procedural critica;
- fixture `out/logs/visual_asset_traceability_report.json` com todos os elos;
- fixture `data/processed/reports/asset_approval_panel.png` com hash referenciado no `human_approval_record.md`;
- fixture `data/processed/reports/asset_visual_delivery_gate_report.json` validado por schema e hash aprovado;
- fixture `out/logs/runtime_comparison_panel.png` separado do painel de aprovacao;
- fixture `out/logs/visual_delivery_gate_report.json` validado por schema, hash e criterios minimos;
- fixture `out/logs/emulator_session.json`;
- fixture `out/logs/evidence_closeout_report.json` selado;
- fixture screenshot, `save.sram` e `visual_vdp_dump.bin`;
- fixture `out/logs/vibe_playable_e2e_report.json` com checkpoint humano aprovado;
- `git diff --check` limpo;
- comparacao do worktree confirma que alteracoes preexistentes fora do inventario permanecem intactas.

## Criterio de encerramento

O trabalho so pode ser declarado completo quando:

1. cada fase possui RED observado, GREEN observado, commit e rollback documentado;
2. o fast gate passa sem abrir BlastEm;
3. o E2E passa com a ROM e evidencia atuais;
4. `crie uma fase com um heroi enfrentando um boss` produz tres targets distintos e owners visuais antes do runtime;
5. tecnica/lab nao promovem visual;
6. procedural/unknown nao promovem asset critico;
7. approval humano preexistente e validado, nunca sintetizado;
8. nenhum arquivo preexistente fora do escopo foi revertido, sobrescrito ou incorporado ao commit;
9. cada commit de fase inclui auditoria `git diff --cached` comprovando que apenas o delta da fase foi staged.

## Autorrevisao do plano

| Requisito da spec | Cobertura |
|---|---|
| Roteamento deterministico, intents, targets e dispatch explicito | Tasks 1-2 |
| `premium_source_manifest` unico e migracao legacy | Task 3 |
| Tres admissoes e tetos de claim | Task 4 |
| Procedural final bloqueado e processadores permitidos | Task 5 |
| Fonte -> convertido -> `.res` -> build -> ROM -> BlastEm | Task 6 |
| Cache, Graphify degradavel, warm start e 32 KiB | Task 7 |
| PT/EN, adversariais e fast gate | Task 8 |
| Fonte real, motion preview, ROM, BlastEm e checkpoint humano | Tasks 9-10 |

Resultado da autorrevisao:

- nenhum `premium_visual_source_manifest`, approval record paralelo ou evidence record paralelo foi planejado;
- nomes `runtime_admitted`, `technical_runtime_admitted` e `runtime_lab_admitted` permanecem identicos em schema, evaluator, testes e docs;
- todos os arquivos modificados existem hoje; todos os arquivos novos possuem um unico owner no plano;
- nao ha marcador de implementacao incompleta no documento;
- o gate rapido nao chama BlastEm;
- o gate E2E para antes do build quando a aprovacao humana esta ausente ou stale;
- as alteracoes Graphify preexistentes recebem revisao de hunk antes do commit, e qualquer hunk inseparavel migra para worktree limpa dedicada;
- staging/commit em worktree sujo nao depende de `git add -- $PhaseFiles`; cada fase exige baseline, staging por delta e `git diff --cached` auditado;
- o painel de aprovacao de asset (`asset_approval_panel.png`) e imutavel e separado do painel final runtime (`runtime_comparison_panel.png`);
- `visual-excellence-standards` produz artefato verificavel em `visual_delivery_gate_report.json`, com schema, campos minimos e hashes; o runner nao aceita `visual_excellence=passed` textual;
- a fixture `v1_root` valida assets reais preservados, nao `assets.Count=0`;
- a fixture real fica isolada em novo projeto LAB e nao reutiliza projetos atualmente sujos.
