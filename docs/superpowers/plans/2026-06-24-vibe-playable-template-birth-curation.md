# Vibe Playable Template Birth Curation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Use superpowers:test-driven-development before any production/template edit. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Curar `tools/sgdk_wrapper/modelo` para que projetos novos nascam com a rota Vibe Playable preparada, bloqueada e rastreavel, sem approvals, runtime evidence ou assets E2E falsos.

**Architecture:** A curadoria adiciona apenas instancias seed dos contratos canonicos do `vibe_playable_loop_v1`; nao cria schema paralelo. O teste `test_vibe_playable_template_birth.ps1` nasce primeiro e valida tanto o template quanto um projeto temporario criado por `new_project.bat/.sh`, incluindo bloqueios contra `out/`, approvals e evidencias. `new_project` passa a podar `out/` apos a copia e a orientar a rota sem declarar sucesso visual/runtime.

**Tech Stack:** PowerShell 5.1/7, Batch, Bash, JSON Schema Draft-07 via validadores canonicos existentes, `new_project.bat/.sh`, `doc/template_registry.json`, `tools/sgdk_wrapper/.agent/scripts/validate_template_registry.py`.

---

## Pre-requisitos e bloqueios

- Este plano implementa a especificacao aprovada em `docs/superpowers/specs/2026-06-24-vibe-playable-template-birth-curation-proposal.md` (`c1022c51`).
- Este plano depende dos contratos reais criados pelo plano `vibe_playable_loop_v1` aprovado em `a9e70939`.
- Nao criar `vibe_playable_birth_contract.schema.json`, `template_birth.schema.json` ou qualquer schema paralelo.
- Se um schema real ainda nao existir no momento da execucao, a fase correspondente fica bloqueada ate a fase do `vibe_playable_loop_v1` que cria esse schema.
- Seeds devem ser validos pelos schemas reais, ou entao o schema canonico real deve ser ajustado no plano principal; nunca contornar com schema local de template.

Schemas reais esperados:

- `tools/sgdk_wrapper/schemas/vibe_playable_route_report.schema.json`
- `tools/sgdk_wrapper/schemas/premium_source_manifest.schema.json`
- `tools/sgdk_wrapper/schemas/runtime_admission_report.schema.json`
- `tools/sgdk_wrapper/schemas/art_gameplay_direction_gate.schema.json`
- `tools/sgdk_wrapper/schemas/visual_delivery_gate_report.schema.json`

## Invariantes de execucao

- Nao iniciar implementacao sem observar RED em `test_vibe_playable_template_birth.ps1`.
- Preservar o worktree sujo existente; stage apenas o delta da fase.
- Usar `apply_patch` para edicoes de arquivo.
- Nao usar `git reset`, `git checkout`, `git restore`, stash ou limpeza ampla.
- Remover `tools/sgdk_wrapper/modelo/out/` somente depois de conferir o caminho absoluto e somente dentro do template canonico.
- Nenhum teste deve escrever approval humano ou evidencia runtime.
- Nenhum arquivo E2E da fixture `VIBE_PLAYABLE_LOOP_FIXTURE` pode entrar no template.
- Nenhuma fase pode declarar `ready_for_aaa`, `runtime_admitted`, `asset_approval_fresh` ou `runtime_evidence_fresh` como verdadeiro.

### Staging seguro por fase

Antes do primeiro patch de cada fase:

```powershell
$PhaseName = 'phaseN'
$PhaseFiles = @(...) # usar o array exato da fase
$BaselineFiles = @($PhaseFiles | ForEach-Object {
  $Exists = Test-Path -LiteralPath $_
  [pscustomobject]@{
    path = $_
    existed = $Exists
    sha256 = if ($Exists -and (Test-Path -LiteralPath $_ -PathType Leaf)) { (Get-FileHash -Algorithm SHA256 -LiteralPath $_).Hash } else { $null }
  }
})
git status --porcelain=v1 | Set-Content out/ci/vibe_template_birth_worktree_baseline.txt
git diff -- $PhaseFiles | Set-Content "out/ci/vibe_template_birth_${PhaseName}_preexisting.diff"
[pscustomobject]@{ files = $BaselineFiles } | ConvertTo-Json -Depth 5 | Set-Content "out/ci/vibe_template_birth_${PhaseName}_file_baseline.json"
```

Antes de cada commit:

```powershell
git add -N -- $PhaseTextFiles
git add -p -- $PhaseTextFiles
git diff --cached -- $PhaseFiles | Tee-Object "out/ci/vibe_template_birth_${PhaseName}_cached.diff"
$UnexpectedCached = @(git diff --cached --name-only | Where-Object { $PhaseFiles -notcontains $_ })
if ($UnexpectedCached.Count -ne 0) { throw "unexpected staged files: $($UnexpectedCached -join ', ')" }
# Revisar o diff cached: todo hunk staged deve ter sido produzido nesta fase.
```

Arquivos novos binarios nao sao previstos neste plano. Se algum aparecer, parar e revisar o plano.

## Inventario exato de arquivos

### Criar

- `tools/sgdk_wrapper/modelo/doc/contracts/vibe_playable_route_report.json`
- `tools/sgdk_wrapper/modelo/doc/contracts/art_gameplay_direction_gate.json`
- `tools/sgdk_wrapper/modelo/doc/contracts/visual_delivery_gate_report.json`
- `tools/sgdk_wrapper/modelo/doc/contracts/runtime_admission_report.json`
- `tools/sgdk_wrapper/modelo/data/source_art/premium_source_manifest.json`
- `tools/sgdk_wrapper/modelo/doc/human_approval_record.md`
- `tools/sgdk_wrapper/ci/test_vibe_playable_template_birth.ps1`

### Modificar

- `tools/sgdk_wrapper/modelo/doc/11-gdd.md`
- `tools/sgdk_wrapper/modelo/doc/13-spec-cenas.md`
- `tools/sgdk_wrapper/modelo/doc/14-plano-de-provas-qa.md`
- `tools/sgdk_wrapper/modelo/doc/18-asset-register.json`
- `tools/sgdk_wrapper/new_project.bat`
- `tools/sgdk_wrapper/new_project.sh`
- `doc/template_registry.json`
- `tools/sgdk_wrapper/.agent/scripts/validate_template_registry.py`
- `tools/sgdk_wrapper/ci/run_all_contract_gates.ps1`

### Deletar

- `tools/sgdk_wrapper/modelo/out/`

---

## Fase 1: teste RED de nascimento do template

### Task 1: criar `test_vibe_playable_template_birth.ps1`

**Files:**
- Create: `tools/sgdk_wrapper/ci/test_vibe_playable_template_birth.ps1`

- [ ] **Step 1: Escrever o teste antes de tocar no template**

O teste deve validar o template e um projeto temporario. Ele deve conter helpers locais para asserts, leitura JSON e limpeza do projeto temporario dentro de `SGDK_projects/_agent_laboratory/`.

Assercoes obrigatorias:

```powershell
Assert-True (Test-Path "$TemplateRoot/doc/contracts/vibe_playable_route_report.json") 'missing route seed'
Assert-True (Test-Path "$TemplateRoot/doc/contracts/art_gameplay_direction_gate.json") 'missing art gameplay seed'
Assert-True (Test-Path "$TemplateRoot/doc/contracts/visual_delivery_gate_report.json") 'missing visual delivery seed'
Assert-True (Test-Path "$TemplateRoot/doc/contracts/runtime_admission_report.json") 'missing runtime admission seed'
Assert-True (-not (Test-Path "$TemplateRoot/out")) 'template contains out directory'
Assert-True (-not (Test-Path "$ProjectRoot/out")) 'new project preserved out directory'
Assert-True ($premium.production_source_ready -eq $false) 'template prevalidated premium source'
Assert-True (@($premium.assets).Count -eq 0) 'template contains premium assets'
Assert-True (-not ($approvalText -match 'decision:\s*approved')) 'template has pre-signed approval'
Assert-True (-not ($approvalText -match 'approved_by\s*:')) 'template has approved_by'
Assert-True (-not ($approvalText -match 'rom_sha256|screenshot|save\.sram|visual_vdp_dump')) 'approval record contains runtime evidence'
Assert-True (-not (Get-ChildItem -LiteralPath $TemplateRoot -Recurse -File | Where-Object { $_.FullName -match 'VIBE_PLAYABLE_LOOP_FIXTURE|runtime_comparison_panel|asset_approval_panel|visual_vdp_dump|save\.sram|rom\.bin' })) 'template contains E2E/evidence asset'
Assert-True ($routeSeed.template_prevalidated -eq $false) 'route seed claims prevalidation'
Assert-True ($runtimeSeed.admission_type -eq 'runtime_blocked_template_seed') 'runtime seed not blocking'
Assert-True ($visualSeed.ready_for_aaa -eq $false) 'visual seed claims ready_for_aaa'
Assert-True ($artSeed.decision.production_allowed -eq $false) 'art seed permits production'
Assert-True ($assetRegister.assets[0].promotion_allowed -eq $false) 'asset register seed promotes'
Assert-True ($newProjectOutput -match 'blocked_no_premium_source') 'new_project output does not explain blocker'
```

O teste tambem deve static-scan `new_project.bat` e `new_project.sh` para exigir uma limpeza explicita de `TARGET_DIR/out` apos copia.

- [ ] **Step 2: Rodar RED**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_vibe_playable_template_birth.ps1
```

Expected RED atual: FAIL por pelo menos `missing route seed`, `missing premium_source_manifest` e `template contains out directory`. Se falhar por schema real ausente, registrar `blocked_missing_vibe_playable_schema` e executar primeiro as fases correspondentes do plano `vibe_playable_loop_v1`.

- [ ] **Step 3: Commit do teste RED**

```powershell
$PhaseName = 'phase1'
$PhaseFiles = @('tools/sgdk_wrapper/ci/test_vibe_playable_template_birth.ps1')
$PhaseTextFiles = $PhaseFiles
git add -N -- $PhaseTextFiles
git add -p -- $PhaseTextFiles
git diff --cached -- $PhaseFiles | Tee-Object out/ci/vibe_template_birth_phase1_cached.diff
$UnexpectedCached = @(git diff --cached --name-only | Where-Object { $PhaseFiles -notcontains $_ })
if ($UnexpectedCached.Count -ne 0) { throw "unexpected staged files: $($UnexpectedCached -join ', ')" }
git commit -m "test: add vibe playable template birth red gate"
$PhaseCommit = git rev-parse HEAD
```

**Conclusao:** RED existe e prova que o template atual ainda nao atende a especificacao.

**Rollback:** `git revert $PhaseCommit`.

---

## Fase 2: seeds canonicos bloqueantes e docs do template

### Task 2: adicionar seeds sem schema paralelo

**Files:**
- Create: contract seeds, `premium_source_manifest.json`, `human_approval_record.md`
- Modify: GDD, spec de cenas, QA plan, asset register
- Delete: `tools/sgdk_wrapper/modelo/out/`

- [ ] **Step 1: Confirmar schemas reais**

```powershell
$RequiredSchemas = @(
  'tools/sgdk_wrapper/schemas/vibe_playable_route_report.schema.json',
  'tools/sgdk_wrapper/schemas/premium_source_manifest.schema.json',
  'tools/sgdk_wrapper/schemas/runtime_admission_report.schema.json',
  'tools/sgdk_wrapper/schemas/art_gameplay_direction_gate.schema.json',
  'tools/sgdk_wrapper/schemas/visual_delivery_gate_report.schema.json'
)
$MissingSchemas = @($RequiredSchemas | Where-Object { -not (Test-Path $_) })
if ($MissingSchemas.Count -ne 0) { throw "blocked_missing_vibe_playable_schema: $($MissingSchemas -join ', ')" }
```

Expected: todos existem depois das fases aplicaveis do `vibe_playable_loop_v1`. Se nao existirem, parar; nao criar schema substituto.

- [ ] **Step 2: Criar seeds validos pelos contratos reais**

Criar estes arquivos:

```text
tools/sgdk_wrapper/modelo/doc/contracts/vibe_playable_route_report.json
tools/sgdk_wrapper/modelo/doc/contracts/art_gameplay_direction_gate.json
tools/sgdk_wrapper/modelo/doc/contracts/visual_delivery_gate_report.json
tools/sgdk_wrapper/modelo/doc/contracts/runtime_admission_report.json
tools/sgdk_wrapper/modelo/data/source_art/premium_source_manifest.json
tools/sgdk_wrapper/modelo/doc/human_approval_record.md
```

Regras de conteudo:

- `vibe_playable_route_report.json`: `template_seed=true`, `template_prevalidated=false`, `visual_route_required=false`, `runtime_open_allowed=false`, `detected_targets=[]`, `required_owners=[]`, `blocking_statuses=["blocked_no_user_request","blocked_no_premium_source"]`.
- `art_gameplay_direction_gate.json`: seguir `art_gameplay_direction_gate.schema.json`; usar `measurement_level="planned_contract"`, reviews `blocked`, `decision.production_allowed=false`, `decision.ready_for_aaa=false`, `next_required_route=["premium_source_manifest","art_direction_selector","human_asset_approval"]`.
- `visual_delivery_gate_report.json`: seguir `visual_delivery_gate_report.schema.json`; usar `schema="visual_delivery_gate_report.v1"`, `ready_for_aaa=false`, `creative_ready=false`, `measurement_level="declared"`, `visual_route_status="blocked_no_premium_source"`, `critical_assets` contendo apenas um seed `role="template_seed"` com `lab_not_delivery=true`, `visual_status="placeholder"` e `measurement_level="declared"`. Esse seed e bloqueante e nao e asset E2E.
- `runtime_admission_report.json`: seguir `runtime_admission_report.schema.json`; usar `admission_type="runtime_blocked_template_seed"`, `visual_status_promotion_allowed=false`, `claim_ceiling="template_seed_only"`, `blocking_statuses=["blocked_no_premium_source","blocked_no_human_approval","blocked_no_blastem_evidence"]`.
- `premium_source_manifest.json`: `production_source_ready=false`, `assets=[]`, `template_seed=true`, `blocking_status="blocked_no_premium_source"`.
- `human_approval_record.md`: conter `status: no_human_approval` e nao conter `approved_by`, `decision: approved`, hash de painel, ROM, screenshot, SRAM ou VDP dump.

- [ ] **Step 3: Atualizar docs do template**

`doc/11-gdd.md` deve ganhar a secao "Vibe Playable Birth Route" com:

```text
Projetos novos nascem com rota Vibe Playable preparada, mas bloqueada.
Pedido natural de jogo/fase/personagem/FX deve acionar roteador visual antes de runtime definitivo.
Nenhum asset, aprovacao humana ou evidencia BlastEm existe no template.
```

`doc/13-spec-cenas.md` deve registrar:

```text
visual_route_required=unknown_until_router
critical_asset_default_status=blocked_no_premium_source
runtime_evidence_default_status=missing
```

`doc/14-plano-de-provas-qa.md` deve registrar:

```text
vibe_playable_birth_seed=structural_only
visual_delivery=blocked_no_premium_source
ready_for_aaa=false_until_real_evidence
```

`doc/18-asset-register.json` deve trocar o exemplo ambiguo por asset seed bloqueante com `promotion_allowed=false`, `source_path=null`, `runtime_path=null`, `status="blocked_no_premium_source"` e `evidence=[]`.

- [ ] **Step 4: Remover `out/` do template com verificacao de caminho**

```powershell
$TemplateOut = (Resolve-Path 'tools/sgdk_wrapper/modelo/out' -ErrorAction SilentlyContinue)
if ($TemplateOut) {
  $ExpectedPrefix = (Resolve-Path 'tools/sgdk_wrapper/modelo').Path
  if (-not $TemplateOut.Path.StartsWith($ExpectedPrefix)) { throw "refusing to delete outside template: $($TemplateOut.Path)" }
  Remove-Item -LiteralPath $TemplateOut.Path -Recurse -Force
}
```

Expected: apenas `tools/sgdk_wrapper/modelo/out/` e removido; nenhum projeto existente e tocado.

- [ ] **Step 5: Rodar GREEN parcial**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_vibe_playable_template_birth.ps1
```

Expected: ainda pode falhar por `new_project` nao podar `out/`/nao orientar blocker, mas nao deve falhar por seeds, manifest, approval ou template `out/`.

- [ ] **Step 6: Commit da fase**

```powershell
$PhaseName = 'phase2'
$PhaseFiles = @(
  'tools/sgdk_wrapper/modelo/doc/contracts/vibe_playable_route_report.json',
  'tools/sgdk_wrapper/modelo/doc/contracts/art_gameplay_direction_gate.json',
  'tools/sgdk_wrapper/modelo/doc/contracts/visual_delivery_gate_report.json',
  'tools/sgdk_wrapper/modelo/doc/contracts/runtime_admission_report.json',
  'tools/sgdk_wrapper/modelo/data/source_art/premium_source_manifest.json',
  'tools/sgdk_wrapper/modelo/doc/human_approval_record.md',
  'tools/sgdk_wrapper/modelo/doc/11-gdd.md',
  'tools/sgdk_wrapper/modelo/doc/13-spec-cenas.md',
  'tools/sgdk_wrapper/modelo/doc/14-plano-de-provas-qa.md',
  'tools/sgdk_wrapper/modelo/doc/18-asset-register.json',
  'tools/sgdk_wrapper/modelo/out'
)
$PhaseTextFiles = @($PhaseFiles | Where-Object { $_ -ne 'tools/sgdk_wrapper/modelo/out' })
git add -N -- $PhaseTextFiles
git add -p -- $PhaseTextFiles
git add -u -- 'tools/sgdk_wrapper/modelo/out'
git diff --cached -- $PhaseFiles | Tee-Object out/ci/vibe_template_birth_phase2_cached.diff
$UnexpectedCached = @(git diff --cached --name-only | Where-Object { $PhaseFiles -notcontains $_ -and $_ -notlike 'tools/sgdk_wrapper/modelo/out/*' })
if ($UnexpectedCached.Count -ne 0) { throw "unexpected staged files: $($UnexpectedCached -join ', ')" }
git commit -m "feat: seed vibe playable template blockers"
$PhaseCommit = git rev-parse HEAD
```

**Conclusao:** template contem seeds bloqueantes e nao contem `out/`.

**Rollback:** `git revert $PhaseCommit`.

---

## Fase 3: `new_project.bat/.sh` nao preservam `out/`

### Task 3: orientar bootstrap e podar evidencia

**Files:**
- Modify: `tools/sgdk_wrapper/new_project.bat`
- Modify: `tools/sgdk_wrapper/new_project.sh`

- [ ] **Step 1: Garantir que o RED ainda falha pelo script**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_vibe_playable_template_birth.ps1
```

Expected antes da edicao: FAIL por `new_project output does not explain blocker` e/ou static-scan sem poda explicita de `out/`.

- [ ] **Step 2: Atualizar `new_project.bat`**

Depois da remocao de `.agent` no projeto novo, adicionar limpeza segura:

```batch
REM Vibe Playable template seeds are structural only. Runtime evidence must never be born from the template.
if exist "%TARGET_DIR%\out" (
    rmdir /S /Q "%TARGET_DIR%\out"
)
```

Nos "Next steps", adicionar:

```text
Vibe Playable seed installed: blocked_no_premium_source.
No approval, ROM, screenshot, SRAM, VDP dump or runtime panel was created by this bootstrap.
Next visual gates: premium source -> human asset approval -> VDP conversion -> build -> BlastEm evidence.
```

- [ ] **Step 3: Atualizar `new_project.sh`**

Depois da remocao de `.agent` no projeto novo, adicionar limpeza segura:

```bash
# Vibe Playable template seeds are structural only. Runtime evidence must never be born from the template.
if [ -d "$TARGET_DIR/out" ]; then
    rm -rf "$TARGET_DIR/out"
fi
```

Nos "Next steps", adicionar a mesma orientacao conservadora.

- [ ] **Step 4: Rodar GREEN do teste de nascimento**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_vibe_playable_template_birth.ps1
```

Expected: PASS para template e projeto temporario; nenhum `out/` no projeto criado; mensagem inclui `blocked_no_premium_source`.

- [ ] **Step 5: Commit da fase**

```powershell
$PhaseName = 'phase3'
$PhaseFiles = @(
  'tools/sgdk_wrapper/new_project.bat',
  'tools/sgdk_wrapper/new_project.sh',
  'tools/sgdk_wrapper/ci/test_vibe_playable_template_birth.ps1'
)
$PhaseTextFiles = $PhaseFiles
git add -N -- $PhaseTextFiles
git add -p -- $PhaseTextFiles
git diff --cached -- $PhaseFiles | Tee-Object out/ci/vibe_template_birth_phase3_cached.diff
$UnexpectedCached = @(git diff --cached --name-only | Where-Object { $PhaseFiles -notcontains $_ })
if ($UnexpectedCached.Count -ne 0) { throw "unexpected staged files: $($UnexpectedCached -join ', ')" }
git commit -m "fix: prevent template runtime evidence birth"
$PhaseCommit = git rev-parse HEAD
```

**Conclusao:** projetos novos nascem com seeds e sem evidencia runtime.

**Rollback:** `git revert $PhaseCommit`.

---

## Fase 4: registry de template e validador

### Task 4: marcador de maturidade conservador

**Files:**
- Modify: `doc/template_registry.json`
- Modify: `tools/sgdk_wrapper/.agent/scripts/validate_template_registry.py`

- [ ] **Step 1: Escrever RED no teste de nascimento para registry**

Adicionar ao `test_vibe_playable_template_birth.ps1`:

```powershell
Assert-True ($template.vibe_playable_birth_seed -eq $true) 'registry missing vibe birth marker'
Assert-True ($template.template_prevalidated -eq $false) 'registry says template prevalidated'
Assert-True ($template.contains_runtime_evidence -eq $false) 'registry permits runtime evidence'
Assert-True ($template.contains_human_approval -eq $false) 'registry permits human approval'
Assert-True ($template.contains_e2e_fixture_assets -eq $false) 'registry permits e2e fixture assets'
Assert-True ($template.default_visual_status -eq 'blocked_no_premium_source') 'registry visual default not blocking'
```

Rodar:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_vibe_playable_template_birth.ps1
```

Expected: FAIL por marcador ausente.

- [ ] **Step 2: Atualizar `doc/template_registry.json`**

No template `sgdk_modelo`, adicionar:

```json
"vibe_playable_birth_seed": true,
"template_prevalidated": false,
"contains_runtime_evidence": false,
"contains_human_approval": false,
"contains_e2e_fixture_assets": false,
"default_visual_status": "blocked_no_premium_source"
```

Manter `contains_out=false`.

- [ ] **Step 3: Atualizar `validate_template_registry.py`**

Se qualquer template declarar `vibe_playable_birth_seed=true`, o validador deve exigir:

```python
for field in [
    "template_prevalidated",
    "contains_runtime_evidence",
    "contains_human_approval",
    "contains_e2e_fixture_assets",
    "default_visual_status",
]:
    if field not in template:
        errors.append(f"{template['id']}: missing vibe playable marker field {field}")

if template.get("template_prevalidated") is not False:
    errors.append(f"{template['id']}: vibe playable template must not be prevalidated")
if template.get("contains_runtime_evidence") is not False:
    errors.append(f"{template['id']}: vibe playable template must not contain runtime evidence")
if template.get("contains_human_approval") is not False:
    errors.append(f"{template['id']}: vibe playable template must not contain human approval")
if template.get("contains_e2e_fixture_assets") is not False:
    errors.append(f"{template['id']}: vibe playable template must not contain E2E fixture assets")
if template.get("default_visual_status") != "blocked_no_premium_source":
    errors.append(f"{template['id']}: default visual status must be blocked_no_premium_source")
```

Tambem transformar `contains_out=true` em erro para template ativo, nao apenas warning, quando `vibe_playable_birth_seed=true`.

- [ ] **Step 4: Rodar GREEN**

```powershell
python tools/sgdk_wrapper/.agent/scripts/validate_template_registry.py
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_vibe_playable_template_birth.ps1
```

Expected: registry ok; template birth test PASS.

- [ ] **Step 5: Commit da fase**

```powershell
$PhaseName = 'phase4'
$PhaseFiles = @(
  'doc/template_registry.json',
  'tools/sgdk_wrapper/.agent/scripts/validate_template_registry.py',
  'tools/sgdk_wrapper/ci/test_vibe_playable_template_birth.ps1'
)
$PhaseTextFiles = $PhaseFiles
git add -N -- $PhaseTextFiles
git add -p -- $PhaseTextFiles
git diff --cached -- $PhaseFiles | Tee-Object out/ci/vibe_template_birth_phase4_cached.diff
$UnexpectedCached = @(git diff --cached --name-only | Where-Object { $PhaseFiles -notcontains $_ })
if ($UnexpectedCached.Count -ne 0) { throw "unexpected staged files: $($UnexpectedCached -join ', ')" }
git commit -m "feat: validate vibe playable template registry marker"
$PhaseCommit = git rev-parse HEAD
```

**Conclusao:** registry e validador sabem que o template e preparado, bloqueado e nao prevalidado.

**Rollback:** `git revert $PhaseCommit`.

---

## Fase 5: gate rapido e evidencia final do plano

### Task 5: integrar teste sem abrir emulador

**Files:**
- Modify: `tools/sgdk_wrapper/ci/run_all_contract_gates.ps1`

- [ ] **Step 1: RED de integracao**

Adicionar expectativa no `test_vibe_playable_template_birth.ps1` ou rodar manualmente que `run_all_contract_gates.ps1 -Mode smoke` ainda nao chama o teste novo.

Expected RED: relatorio/gate smoke nao referencia `test_vibe_playable_template_birth.ps1`.

- [ ] **Step 2: Incluir teste no gate rapido**

Adicionar chamada a:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_vibe_playable_template_birth.ps1
```

em `tools/sgdk_wrapper/ci/run_all_contract_gates.ps1`, sem abrir BlastEm.

- [ ] **Step 3: Validar tudo**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_vibe_playable_template_birth.ps1
python tools/sgdk_wrapper/.agent/scripts/validate_template_registry.py
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/run_all_contract_gates.ps1 -Mode smoke
```

Expected:

```text
template_birth=passed
premium_source_ready=false
assets_count=0
human_approval=missing_or_unapproved
template_contains_out=false
new_project_contains_out=false
runtime_evidence_absent=true
registry=passed
blastem_not_invoked=true
```

- [ ] **Step 4: Commit da fase**

```powershell
$PhaseName = 'phase5'
$PhaseFiles = @(
  'tools/sgdk_wrapper/ci/run_all_contract_gates.ps1',
  'tools/sgdk_wrapper/ci/test_vibe_playable_template_birth.ps1'
)
$PhaseTextFiles = $PhaseFiles
git add -N -- $PhaseTextFiles
git add -p -- $PhaseTextFiles
git diff --cached -- $PhaseFiles | Tee-Object out/ci/vibe_template_birth_phase5_cached.diff
$UnexpectedCached = @(git diff --cached --name-only | Where-Object { $PhaseFiles -notcontains $_ })
if ($UnexpectedCached.Count -ne 0) { throw "unexpected staged files: $($UnexpectedCached -join ', ')" }
git commit -m "test: gate vibe playable template birth"
$PhaseCommit = git rev-parse HEAD
```

**Conclusao:** a curadoria do template fica coberta por teste rapido, sem emulador.

**Rollback:** `git revert $PhaseCommit`.

---

## Validacao final obrigatoria

Executar nesta ordem:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_vibe_playable_template_birth.ps1
python tools/sgdk_wrapper/.agent/scripts/validate_template_registry.py
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/run_all_contract_gates.ps1 -Mode smoke
git diff --check -- tools/sgdk_wrapper/modelo tools/sgdk_wrapper/ci tools/sgdk_wrapper/new_project.bat tools/sgdk_wrapper/new_project.sh doc/template_registry.json
```

Evidencias esperadas:

- `tools/sgdk_wrapper/modelo/doc/contracts/` contem seeds reais e bloqueantes.
- `tools/sgdk_wrapper/modelo/data/source_art/premium_source_manifest.json` tem `production_source_ready=false` e `assets=[]`.
- `tools/sgdk_wrapper/modelo/doc/human_approval_record.md` nao contem approval.
- `tools/sgdk_wrapper/modelo/out/` nao existe.
- Projeto temporario criado por `new_project` tambem nao contem `out/`.
- Nenhum ROM, screenshot, SRAM, VDP dump, painel runtime ou asset da fixture E2E aparece no template.
- Registry validator passa se novo marcador existir.
- Nenhum teste abre BlastEm.

## Criterio de encerramento

O trabalho so pode ser declarado concluido quando:

1. cada fase teve RED observado antes de GREEN;
2. cada commit teve diff staged auditado;
3. nenhum schema paralelo foi criado;
4. template e projeto temporario continuam bloqueados para visual/runtime;
5. `new_project.bat/.sh` impedem `out/` herdado;
6. registry e validador concordam sobre o marcador conservador;
7. as alteracoes preexistentes fora do inventario permanecem intactas.

## Autorrevisao

- Requisito 1: seeds em `tools/sgdk_wrapper/modelo/doc/contracts/` cobertos pela Fase 2.
- Requisito 2: proibicoes de approval/ROM/screenshot/SRAM/VDP/painel runtime/E2E cobertas pelo teste RED e GREEN.
- Requisito 3: `premium_source_manifest` vazio e bloqueante coberto pela Fase 2.
- Requisito 4: `human_approval_record.md` sem aprovacao coberto pela Fase 2.
- Requisito 5: `new_project.bat/.sh` podam `out/` coberto pela Fase 3.
- Requisito 6: teste temporario recem-criado coberto pela Fase 1 e validado ate a Fase 5.
- Requisito 7: registry e validator atualizados juntos na Fase 4.
- Requisito 8: nenhum schema paralelo; execucao bloqueia se os schemas reais do `vibe_playable_loop_v1` ainda nao existirem.
