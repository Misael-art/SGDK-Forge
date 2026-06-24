# Vibe Playable Template Birth Curation Proposal

**Status:** proposta registrada; implementacao nao autorizada neste documento.

**Escopo:** curadoria futura do template canonico `tools/sgdk_wrapper/modelo` para que projetos novos nascam preparados para seguir `vibe_playable_loop_v1`, mas ainda bloqueados para qualquer claim visual ou runtime ate existirem fonte premium, aprovacao humana e evidencia BlastEm reais.

**Regra central:** o template deve reduzir diagnostico e contexto, nao pre-validar nada.

---

## Resultado esperado

Ao criar um projeto novo via `tools/sgdk_wrapper/new_project.bat` ou `tools/sgdk_wrapper/new_project.sh`, o projeto deve nascer com:

- contratos seed em `doc/contracts/`;
- `data/source_art/premium_source_manifest.json` vazio e bloqueante;
- `doc/human_approval_record.md` presente, mas sem nenhuma aprovacao;
- GDD, spec de cenas, plano QA e asset register apontando para a rota Vibe Playable como caminho correto;
- nenhum `out/`, evidencia runtime, painel final, approval pre-assinado ou asset E2E;
- marcador opcional em `doc/template_registry.json` apenas se for necessario diferenciar maturidade do template.

O projeto novo ainda deve ser classificado como bloqueado para producao visual final ate:

1. fonte premium persistida com hash e autoria;
2. conversao VDP rastreada;
3. painel de aprovacao de asset imutavel;
4. aprovacao humana real vinculada a hashes;
5. ROM buildada;
6. captura BlastEm;
7. painel runtime separado;
8. `visual_delivery_gate_report.json` valido.

## Nao-objetivos

- Nao mover, limpar ou alterar agora `tools/sgdk_wrapper/modelo`.
- Nao criar approvals, evidencia, ROM, screenshots ou hashes runtime no template.
- Nao copiar assets da fixture E2E para o template.
- Nao promover `runtime_admitted`, `ready_for_aaa`, `visual_lab_aprovado` ou claim equivalente em projeto recem-criado.
- Nao duplicar schemas do plano `vibe_playable_loop_v1`; seeds sao instancias bloqueantes dos contratos canonicos.

## Inventario futuro de arquivos

### Criar ou atualizar dentro de `tools/sgdk_wrapper/modelo`

- `doc/contracts/vibe_playable_birth_contract.json`
- `doc/contracts/art_direction_decision_record.json`
- `doc/contracts/art_gameplay_direction_gate.json`
- `doc/contracts/visual_delivery_gate_report.json`
- `data/source_art/premium_source_manifest.json`
- `doc/human_approval_record.md`
- `doc/11-gdd.md`
- `doc/13-spec-cenas.md`
- `doc/14-plano-de-provas-qa.md`
- `doc/18-asset-register.json`

### Criar ou atualizar no wrapper

- `tools/sgdk_wrapper/new_project.bat`
- `tools/sgdk_wrapper/new_project.sh`
- `tools/sgdk_wrapper/ci/test_vibe_playable_template_birth.ps1`
- `doc/template_registry.json` somente se houver novo marcador de maturidade.

## Contratos seed em `doc/contracts/`

Os seeds devem existir para reduzir busca, token e diagnostico repetido. Eles nao sao evidencia.

### `vibe_playable_birth_contract.json`

Campos minimos:

```json
{
  "schema_version": "1.0.0",
  "contract_kind": "vibe_playable_birth_seed",
  "template_prevalidated": false,
  "visual_status": "blocked_no_premium_source",
  "runtime_status": "not_built",
  "required_next_gates": [
    "vibe_playable_route_report",
    "premium_source_manifest",
    "asset_visual_delivery_gate_report",
    "human_asset_approval",
    "runtime_admission_report",
    "blastem_runtime_evidence"
  ],
  "forbidden_claims_until_evidence": [
    "runtime_admitted",
    "visual_excellence_passed",
    "asset_approval_fresh",
    "runtime_evidence_fresh",
    "ready_for_aaa"
  ]
}
```

### `art_direction_decision_record.json`

Seed com `decision_status="pending_user_direction_or_router"`, `approved=false`, `source_hashes=[]` e `target_ids=[]`.

### `art_gameplay_direction_gate.json`

Seed com `gate_status="blocked_no_premium_source"`, `detected_targets=[]`, `owners_required=[]`, `critical_assets=[]` e `promotion_allowed=false`.

### `visual_delivery_gate_report.json`

Seed com `decision="blocked"`, `scope="template_seed"`, `owner="skills/art/visual-excellence-standards"`, `criteria_passed=false`, `panel=null`, `rom_sha256=null` e `blastem_session_sha256=null`.

Regra: validators devem rejeitar qualquer seed que tente declarar `passed` sem arquivos reais e hashes.

## `premium_source_manifest` vazio e bloqueante

Arquivo proposto: `tools/sgdk_wrapper/modelo/data/source_art/premium_source_manifest.json`

Conteudo conceitual:

```json
{
  "schema_version": "2.0.0",
  "manifest_kind": "premium_source_manifest",
  "template_seed": true,
  "production_source_ready": false,
  "blocking_status": "blocked_no_premium_source",
  "assets": []
}
```

Regras:

- `assets=[]` e intencional no template.
- `production_source_ready=false` e obrigatorio.
- `source_classification` nao pode fingir `human_authored`, `generated_bitmap` ou `licensed_source` sem arquivos reais.
- `procedural_debug` e `unknown` continuam bloqueantes para assets criticos.

## `human_approval_record.md` sem aprovacoes

Arquivo proposto: `tools/sgdk_wrapper/modelo/doc/human_approval_record.md`

Conteudo conceitual:

```markdown
# Human Approval Record

status: no_human_approval
template_seed: true

Nenhum asset visual deste projeto foi aprovado ainda.

Este arquivo deve ser preenchido somente por checkpoint humano real, apos fonte premium, asset convertido, painel imutavel e parecer visual canonico.
```

O arquivo nao pode conter:

- `decision: approved`;
- `approved_by`;
- assinatura;
- hash de painel aprovado;
- hash de ROM;
- qualquer claim `asset_approval_fresh=true`.

## Atualizacoes documentais do template

### `doc/11-gdd.md`

Adicionar secao curta "Vibe Playable Birth Route":

- pedidos naturais de jogo/fase/personagem/FX ativam rota visual;
- heroi, boss, cenario, HUD e FX viram targets separados;
- runtime definitivo fica bloqueado ate a rota visual;
- build tecnico de laboratorio pode existir, mas nao promove visual.

### `doc/13-spec-cenas.md`

Adicionar contrato transversal:

- cena nova nasce com `visual_route_required=unknown_until_router`;
- assets criticos nascem como `blocked_no_premium_source`;
- budget VDP so pode passar de estimado para validado depois de conversao e build reais;
- evidencia runtime depende de ROM SHA-256 e BlastEm.

### `doc/14-plano-de-provas-qa.md`

Adicionar gate:

- `vibe_playable_birth_seed`: passa apenas como seed estrutural;
- `visual_delivery`: bloqueado ate fonte premium, approval humano e BlastEm;
- `ready_for_aaa`: explicitamente falso em projeto recem-criado.

### `doc/18-asset-register.json`

Substituir exemplo ambiguo por registro seed bloqueante:

```json
{
  "asset_id": "vibe_playable_seed",
  "role": "template_seed",
  "criticality": "non_runtime_seed",
  "source_path": null,
  "runtime_path": null,
  "status": "blocked_no_premium_source",
  "promotion_allowed": false,
  "evidence": []
}
```

## Orientacao em `new_project.bat` e `new_project.sh`

Os scripts de novo projeto devem informar, sem alegar validacao:

```text
Vibe Playable seed installed.
Status: blocked_no_premium_source.
Next gates: premium source -> human asset approval -> VDP conversion -> build -> BlastEm evidence.
No visual or runtime approval was created by this bootstrap.
```

Tambem devem:

- copiar os seeds do template como arquivos normais;
- nao gerar `out/`;
- nao gerar `emulator_session.json`;
- nao chamar BlastEm;
- nao preencher `human_approval_record.md`;
- apontar o usuario para `doc/contracts/vibe_playable_birth_contract.json`.

## Teste contratual

Criar `tools/sgdk_wrapper/ci/test_vibe_playable_template_birth.ps1`.

O teste deve:

1. criar projeto temporario a partir de `tools/sgdk_wrapper/modelo`;
2. validar que existem os seeds em `doc/contracts/`;
3. validar `premium_source_manifest` com `assets.Count=0` e `production_source_ready=false`;
4. validar `human_approval_record.md` sem `approved_by`, `decision: approved`, assinatura ou hash de ROM;
5. validar GDD, spec de cenas, plano QA e asset register com os blockers Vibe Playable;
6. validar que `new_project.bat/.sh` orientam a rota, mas nao prometem sucesso;
7. falhar se o template ou o projeto recem-criado contem:
   - `out/`;
   - `out/logs/emulator_session.json`;
   - `out/logs/evidence_closeout_report.json`;
   - `out/logs/visual_delivery_gate_report.json` com `passed`;
   - `out/logs/runtime_comparison_panel.png`;
   - `data/processed/reports/asset_approval_panel.png`;
   - assets da fixture E2E `VIBE_PLAYABLE_LOOP_FIXTURE`;
   - ROM, screenshot, SRAM ou dump VDP;
8. validar que nenhum campo seed declara `runtime_admitted`, `asset_approval_fresh=true`, `runtime_evidence_fresh=true` ou `ready_for_aaa=true`.

Asserts essenciais:

```powershell
Assert-True (Test-Path "$ProjectRoot/doc/contracts/vibe_playable_birth_contract.json") 'birth contract missing'
Assert-True ($premium.production_source_ready -eq $false) 'template prevalidated premium source'
Assert-True (@($premium.assets).Count -eq 0) 'template contains premium assets'
Assert-True (-not ($approvalText -match 'decision:\s*approved')) 'template has pre-signed approval'
Assert-True (-not (Test-Path "$ProjectRoot/out")) 'new project contains runtime evidence directory'
Assert-True ($birth.template_prevalidated -eq $false) 'birth seed claims prevalidation'
Assert-True ($birth.visual_status -eq 'blocked_no_premium_source') 'visual seed not blocking'
Assert-True (-not ($assetRegisterText -match 'promotion_allowed\"\s*:\s*true')) 'seed asset promotes'
```

## Template registry

Se a curadoria introduzir novo marcador de maturidade, atualizar `doc/template_registry.json` com campos conservadores:

```json
{
  "id": "sgdk_modelo",
  "vibe_playable_birth_seed": true,
  "template_prevalidated": false,
  "contains_runtime_evidence": false,
  "contains_human_approval": false,
  "contains_e2e_fixture_assets": false,
  "default_visual_status": "blocked_no_premium_source"
}
```

Se nao houver novo marcador, manter apenas `owner_review_notes` explicando que o template e preparado, nao validado.

## Criterios de aceite da curadoria futura

- `test_vibe_playable_template_birth.ps1` passa em projeto temporario.
- `doc/template_registry.json`, se alterado, continua declarando `contains_out=false`.
- `tools/sgdk_wrapper/modelo` nao contem `out/`.
- O template nao contem evidence runtime.
- O template nao contem approval pre-assinado.
- O template nao contem assets da fixture E2E.
- O template reduz a descoberta: os contracts seed apontam owners e blockers sem carregar relatórios longos.
- Projeto novo nasce pronto para seguir o fluxo correto, mas bloqueado para fonte premium, aprovacao humana e BlastEm reais.

## Autorrevisao

- Duplicidade: nenhum schema novo e proposto; apenas instancias seed dos contratos canonicos.
- Compatibilidade: `new_project.bat/.sh` seguem como entrada; o template continua sendo `tools/sgdk_wrapper/modelo`.
- Falsificacao de aprovacao: `human_approval_record.md` nasce explicitamente sem aprovacao e o teste procura strings proibidas.
- Falsificacao de evidencia: `out/`, ROM, screenshot, SRAM, VDP dump e reports runtime sao proibidos no template.
- Custo de contexto: seeds pequenos apontam owners e blockers; nao carregam paineis, imagens E2E ou reports runtime.
