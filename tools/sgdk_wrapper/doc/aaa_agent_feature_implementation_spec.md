# Especificacao de Implementacao por Arquivo - Ecossistema AAA de Agentes

**Data:** 2026-04-21  
**Base:** `tools/sgdk_wrapper/doc/aaa_agent_feature_roadmap.md`  
**Objetivo:** orientar outro agente de IA na implementacao incremental das features propostas, com nomes exatos de arquivos, interfaces, artefatos e ordem de codificacao  
**Regra inviolavel:** nenhuma regressao no comportamento atual do wrapper

---

## 1. Escopo

Este documento detalha a implementacao tecnica das cinco frentes abaixo:

1. capturador canonico de evidencia BlastEm
2. linter de contrato de cena
3. runner deterministico de regressao por cena
4. auditor de budget por frame/cena
5. inspector visual de VRAM/paleta/sprites

Ordem tecnica obrigatoria para codificacao:

1. fundacao comum
2. capturador canonico de evidencia BlastEm
3. linter de contrato de cena
4. runner deterministico de regressao por cena
5. auditor de budget por frame/cena
6. inspector visual de VRAM/paleta/sprites
7. integracoes opt-in no wrapper principal

---

## 2. Regras de Implementacao

- nao alterar por default o comportamento de `build.bat`, `build_inner.bat`, `run.bat`, `validate_resources.ps1`, `run_runtime_capture.ps1`, `run_visual_capture.ps1` e `generate_scene_regression_report.ps1`
- toda feature nova entra primeiro como script isolado
- todo artefato novo precisa de schema versionado
- toda falha nova deve degradar para warning enquanto a feature estiver em modo experimental
- nenhuma escrita em `src/`, `res/`, `doc/` ou `out/rom.bin`
- toda integracao em wrapper principal precisa ser protegida por flag `SGDK_*`

---

## 3. Mapa de Arquivos Novos

### 3.1 Fundacao comum

Criar:

- `tools/sgdk_wrapper/schemas/common_artifact.schema.json`
- `tools/sgdk_wrapper/schemas/scene_id.schema.json`
- `tools/sgdk_wrapper/lib/sgdk_artifact_contracts.psm1`
- `tools/sgdk_wrapper/validate_artifact_schema.ps1`

### 3.2 Capturador canonico de evidencia BlastEm

Criar:

- `tools/sgdk_wrapper/capture_blastem_evidence.ps1`
- `tools/sgdk_wrapper/lib/blastem_evidence.psm1`
- `tools/sgdk_wrapper/schemas/blastem_evidence.schema.json`
- `tools/sgdk_wrapper/schemas/blastem_session_manifest.schema.json`

Integrar depois, por flag, em:

- `tools/sgdk_wrapper/run.bat`
- opcionalmente `tools/sgdk_wrapper/validate_resources.ps1`

### 3.3 Linter de contrato de cena

Criar:

- `tools/sgdk_wrapper/lint_scene_contract.ps1`
- `tools/sgdk_wrapper/schemas/scene_contract.schema.json`
- `tools/sgdk_wrapper/schemas/scene_contract_report.schema.json`

Consumir manifesto de projeto:

- `<project_root>/doc/scene-contracts.json`

### 3.4 Runner deterministico de regressao por cena

Criar:

- `tools/sgdk_wrapper/run_scene_regression.ps1`
- `tools/sgdk_wrapper/lib/scene_regression.psm1`
- `tools/sgdk_wrapper/lib/evidence_compare.psm1`
- `tools/sgdk_wrapper/schemas/scene_regression_manifest.schema.json`
- `tools/sgdk_wrapper/schemas/scene_regression_report.schema.json`
- `tools/sgdk_wrapper/schemas/scene_evidence_bundle.schema.json`

Consumir manifesto de projeto:

- `<project_root>/doc/scene-regression.json`

### 3.5 Auditor de budget por frame/cena

Criar:

- `tools/sgdk_wrapper/audit_scene_budget.ps1`
- `tools/sgdk_wrapper/merge_scene_budget_metrics.ps1`
- `tools/sgdk_wrapper/lib/scene_budget.psm1`
- `tools/sgdk_wrapper/schemas/scene_budget.schema.json`
- `tools/sgdk_wrapper/schemas/scene_budget_frame.schema.json`

### 3.6 Inspector visual de VRAM/paleta/sprites

Criar:

- `tools/sgdk_wrapper/inspect_vdp_scene_state.ps1`
- `tools/sgdk_wrapper/render_vdp_inspection_report.py`
- `tools/sgdk_wrapper/lib/vdp_inspection.psm1`
- `tools/sgdk_wrapper/schemas/vdp_inspection.schema.json`
- `tools/sgdk_wrapper/schemas/vdp_palette_snapshot.schema.json`
- `tools/sgdk_wrapper/schemas/vdp_sprite_snapshot.schema.json`

---

## 4. Arquitetura da Fundacao Comum

### 4.1 `common_artifact.schema.json`

Definir campos base obrigatorios para todo artefato novo:

```json
{
  "schema_version": "1.0.0",
  "generated_at": "ISO-8601",
  "tool_name": "string",
  "tool_version": "string",
  "project_root": "absolute-path",
  "workspace_root": "absolute-path",
  "status": "ok|warn|error",
  "failure_reason": "string|null"
}
```

### 4.2 `scene_id.schema.json`

Definir regra unica para `scene_id`:

- ASCII apenas
- regex sugerida: `^[a-z0-9_]+$`
- sem espacos
- sem prefixos ambiguos

### 4.3 `sgdk_artifact_contracts.psm1`

Exportar funcoes:

- `New-SgdkArtifactEnvelope`
- `Set-SgdkArtifactFailure`
- `Write-SgdkJsonArtifact`
- `Test-SgdkRequiredFile`
- `Get-SgdkRomIdentity`

Interface esperada:

```powershell
New-SgdkArtifactEnvelope -ToolName <string> -ToolVersion <string> -ProjectRoot <string> -WorkspaceRoot <string>
Write-SgdkJsonArtifact -Data <hashtable> -Path <string>
Get-SgdkRomIdentity -RomPath <string>
```

### 4.4 `validate_artifact_schema.ps1`

Responsabilidade:

- validar JSON gerado por scripts novos
- checar `schema_version`
- falhar apenas no proprio comando, nunca no build principal por default

Parametros:

```text
-SchemaPath <absolute path>
-ArtifactPath <absolute path>
-WarnOnly
```

---

## 5. Especificacao da Prioridade 1

## 5.1 `capture_blastem_evidence.ps1`

Responsabilidade:

- localizar ROM
- localizar BlastEm
- iniciar sessao isolada
- aguardar warmup
- disparar captura
- coletar screenshot, SRAM e dump VDP
- gerar manifesto final

Parametros obrigatorios:

```text
-ProjectRoot <absolute path>
```

Parametros opcionais:

```text
-RomPath <absolute path>
-EmulatorPath <absolute path>
-OutputRoot <absolute path>
-WarmupMs <int>
-BootTimeoutMs <int>
-CaptureMode <string>
-WarnOnly
```

Fluxo interno:

1. resolver `project_root`
2. resolver `rom.bin`
3. obter `rom_sha256`
4. criar pasta `out/evidence/blastem/`
5. iniciar sessao isolada
6. acionar captura via modulo
7. validar artefatos obrigatorios
8. escrever `blastem_evidence.json`

Saidas:

- `<project_root>/out/logs/blastem_evidence.json`
- `<project_root>/out/evidence/blastem/screenshot.png`
- `<project_root>/out/evidence/blastem/save.sram`
- `<project_root>/out/evidence/blastem/visual_vdp_dump.bin`
- `<project_root>/out/evidence/blastem/session_manifest.json`

### 5.2 `blastem_evidence.psm1`

Exportar funcoes:

- `Start-BlastemEvidenceSession`
- `Wait-BlastemReady`
- `Invoke-BlastemEvidenceCapture`
- `Stop-BlastemEvidenceSession`
- `Test-BlastemEvidenceBundle`

Interface esperada:

```powershell
Start-BlastemEvidenceSession -EmulatorPath <string> -RomPath <string> -OutputRoot <string>
Invoke-BlastemEvidenceCapture -SessionRoot <string> -CaptureMode <string>
Test-BlastemEvidenceBundle -SessionRoot <string> -RequireVdpDump
```

Dependencias:

- reutilizar `tools/sgdk_wrapper/lib/blastem_automation.psm1`
- nao duplicar automacao de teclado/janela sem necessidade

### 5.3 `blastem_evidence.schema.json`

Campos obrigatorios:

```json
{
  "schema_version": "1.0.0",
  "generated_at": "ISO-8601",
  "tool_name": "capture_blastem_evidence",
  "tool_version": "semver",
  "project_root": "absolute-path",
  "rom_path": "absolute-path",
  "rom_sha256": "sha256",
  "emulator_path": "absolute-path",
  "capture_mode": "canonical|minimal|debug",
  "session_started": true,
  "session_completed": true,
  "screenshot_present": true,
  "sram_present": true,
  "vdp_dump_present": true,
  "evidence_status": "ok|warn|error",
  "failure_reason": null
}
```

### 5.4 Ordem de codificacao da prioridade 1

1. `common_artifact.schema.json`
2. `sgdk_artifact_contracts.psm1`
3. `blastem_session_manifest.schema.json`
4. `blastem_evidence.schema.json`
5. `blastem_evidence.psm1`
6. `capture_blastem_evidence.ps1`
7. teste manual em um projeto laboratorio
8. integracao opt-in posterior

---

## 6. Especificacao da Prioridade 5

## 6.1 `lint_scene_contract.ps1`

Responsabilidade:

- ler `doc/scene-contracts.json`
- validar schema
- validar coerencia basica de assets, campos e obrigatoriedades
- emitir relatorio legivel por maquina

Parametros:

```text
-ProjectRoot <absolute path>
-ContractPath <absolute path>
-Mode <lab|production|aaa_gate>
-WarnOnly
```

Saida:

- `<project_root>/out/logs/scene_contract_report.json`

### 6.2 `scene_contract.schema.json`

Estrutura minima:

```json
{
  "schema_version": "1.0.0",
  "project_profile": "lab|production|aaa_gate",
  "scenes": [
    {
      "scene_id": "scene_example",
      "scene_role": "menu|title|gameplay|boss|cutscene|lab",
      "boot_mode": "debug_menu|sram_bootstrap|runtime_flag|unsupported",
      "capture_frame": 120,
      "warmup_frames": 60,
      "required_assets": [],
      "palette_policy": "string",
      "budget_profile": "string",
      "effects_active": [],
      "cleanup_required": true,
      "regression_required": true
    }
  ]
}
```

### 6.3 `scene_contract_report.schema.json`

Status por cena:

- `ok`
- `warn`
- `error`
- `unsupported`

Campos por finding:

- `scene_id`
- `severity`
- `code`
- `message`
- `related_path`

### 6.4 Ordem de codificacao da prioridade 5

1. `scene_id.schema.json`
2. `scene_contract.schema.json`
3. `scene_contract_report.schema.json`
4. `lint_scene_contract.ps1`
5. manifesto piloto em um projeto laboratorio

---

## 7. Especificacao da Prioridade 3

## 7.1 `run_scene_regression.ps1`

Responsabilidade:

- ler manifesto de regressao
- iterar cenas
- acionar bootstrap deterministico
- chamar captura canonica
- comparar com baseline
- gerar matriz final

Parametros:

```text
-ProjectRoot <absolute path>
-ManifestPath <absolute path>
-SceneId <string>
-UpdateBaseline
-WarnOnly
```

Saidas:

- `<project_root>/out/logs/scene_regression_report.json`
- `<project_root>/out/logs/scene_regression_matrix.json`
- `<project_root>/out/evidence/scenes/<scene_id>/...`

### 7.2 `scene_regression.psm1`

Exportar funcoes:

- `Get-SceneRegressionManifest`
- `Invoke-SceneBootstrap`
- `Invoke-SceneCapture`
- `Compare-SceneEvidence`
- `New-SceneRegressionResult`

### 7.3 `evidence_compare.psm1`

Exportar comparadores:

- `Compare-ExactHash`
- `Compare-ImageTolerance`
- `Compare-BinaryExact`
- `Compare-PaletteSnapshot`

### 7.4 `scene_regression_manifest.schema.json`

Estrutura minima:

```json
{
  "schema_version": "1.0.0",
  "scenes": [
    {
      "scene_id": "scene_example",
      "boot_mode": "debug_menu",
      "capture_kind": "screenshot|evidence_bundle",
      "capture_frame": 120,
      "warmup_frames": 60,
      "baseline_root": "doc/baselines/scene_example",
      "comparison_mode": "exact|tolerant",
      "required_artifacts": ["screenshot", "vdp_dump"]
    }
  ]
}
```

### 7.5 `scene_regression_report.schema.json`

Status finais:

- `passed`
- `failed`
- `missing`
- `stale`
- `unsupported`
- `error`

### 7.6 Ordem de codificacao da prioridade 3

1. `scene_regression_manifest.schema.json`
2. `scene_evidence_bundle.schema.json`
3. `scene_regression_report.schema.json`
4. `evidence_compare.psm1`
5. `scene_regression.psm1`
6. `run_scene_regression.ps1`
7. piloto com uma unica cena

Dependencia de entrada:

- `capture_blastem_evidence.ps1` ja funcional
- `scene-contracts.json` ja definido ao menos no minimo

---

## 8. Especificacao da Prioridade 2

## 8.1 `audit_scene_budget.ps1`

Responsabilidade:

- consolidar metrica de budget por cena
- classificar origem da metrica
- emitir relatorio por cena e por frame

Parametros:

```text
-ProjectRoot <absolute path>
-RuntimeMetricsPath <absolute path>
-SceneId <string>
-WarnOnly
```

Saidas:

- `<project_root>/out/logs/scene_budget_report.json`
- `<project_root>/out/logs/scene_budget_summary.md`

### 8.2 `merge_scene_budget_metrics.ps1`

Responsabilidade:

- combinar `runtime_metrics.json`
- combinar artefatos de regressao por cena
- consolidar serie temporal

Parametros:

```text
-ProjectRoot <absolute path>
-SourcePaths <string[]>
-OutputPath <absolute path>
```

### 8.3 `scene_budget.psm1`

Exportar funcoes:

- `Import-SceneBudgetMetrics`
- `Measure-SceneBudget`
- `Get-SceneBudgetThresholds`
- `Write-SceneBudgetSummary`

### 8.4 `scene_budget.schema.json`

Estrutura minima:

```json
{
  "schema_version": "1.0.0",
  "project_root": "absolute-path",
  "scenes": [
    {
      "scene_id": "scene_example",
      "measurement_origin": "measured|estimated|inferred",
      "frames_analyzed": 300,
      "dma_bytes_peak": 0,
      "dma_ops_peak": 0,
      "sprite_count_peak": 0,
      "sprites_per_scanline_peak": 0,
      "pal_changes_peak": 0,
      "vram_usage_estimate_peak": 0,
      "budget_status": "ok|warn|error"
    }
  ]
}
```

### 8.5 Ordem de codificacao da prioridade 2

1. `scene_budget_frame.schema.json`
2. `scene_budget.schema.json`
3. `scene_budget.psm1`
4. `merge_scene_budget_metrics.ps1`
5. `audit_scene_budget.ps1`
6. integrar apenas em modo observacao

Dependencia recomendada:

- `run_scene_regression.ps1` funcionando
- `runtime_metrics.json` conhecido

---

## 9. Especificacao da Prioridade 4

## 9.1 `inspect_vdp_scene_state.ps1`

Responsabilidade:

- ler dump VDP e artefatos auxiliares
- gerar snapshot estruturado do estado visual
- serializar JSON de inspeção

Parametros:

```text
-ProjectRoot <absolute path>
-SceneId <string>
-VdpDumpPath <absolute path>
-OutputPath <absolute path>
-WarnOnly
```

Saida:

- `<project_root>/out/logs/vdp_inspection.json`

### 9.2 `render_vdp_inspection_report.py`

Responsabilidade:

- ler `vdp_inspection.json`
- gerar relatorio HTML e imagens auxiliares

CLI sugerida:

```text
python render_vdp_inspection_report.py --input <json> --output <html>
```

### 9.3 `vdp_inspection.psm1`

Exportar funcoes:

- `Import-VdpDump`
- `Measure-VdpPaletteUsage`
- `Measure-VdpTileUsage`
- `Measure-VdpSpriteState`
- `New-VdpInspectionArtifact`

### 9.4 `vdp_inspection.schema.json`

Estrutura minima:

```json
{
  "schema_version": "1.0.0",
  "scene_id": "scene_example",
  "palette_snapshots": [],
  "tile_usage": {},
  "sprite_snapshot": {},
  "plane_usage": {},
  "inspection_status": "ok|warn|error"
}
```

### 9.5 Ordem de codificacao da prioridade 4

1. `vdp_palette_snapshot.schema.json`
2. `vdp_sprite_snapshot.schema.json`
3. `vdp_inspection.schema.json`
4. `vdp_inspection.psm1`
5. `inspect_vdp_scene_state.ps1`
6. `render_vdp_inspection_report.py`

Dependencia obrigatoria:

- dump VDP confiavel vindo da prioridade 1

---

## 10. Integracoes Opt-In no Wrapper Principal

Estas integracoes so podem ocorrer depois que os scripts isolados estiverem estaveis.

### 10.1 `run.bat`

Integracao futura permitida:

- se `SGDK_CAPTURE_CANONICAL_EVIDENCE=1`, chamar `capture_blastem_evidence.ps1` apos ou junto da sessao de runtime

Proibido nesta fase:

- substituir a logica atual de run
- mudar o fluxo default sem flag

### 10.2 `validate_resources.ps1`

Integracao futura permitida:

- consumir `blastem_evidence.json`
- consumir `scene_contract_report.json`
- consumir `scene_regression_report.json`
- consumir `scene_budget_report.json`

Proibido nesta fase:

- tornar qualquer uma dessas dependencias obrigatoria por default

### 10.3 `build_inner.bat`

Integracao futura permitida:

- warnings resumidos de artefatos novos

Proibido nesta fase:

- chamar ferramentas novas sem flags explicitas

---

## 11. Ordem Global de Codificacao

Sequencia obrigatoria:

1. `schemas/common_artifact.schema.json`
2. `schemas/scene_id.schema.json`
3. `lib/sgdk_artifact_contracts.psm1`
4. `validate_artifact_schema.ps1`
5. prioridade 1 completa
6. prioridade 5 completa
7. prioridade 3 completa
8. prioridade 2 completa
9. prioridade 4 completa
10. integracoes opt-in

---

## 12. Criterios de Conclusao por Etapa

### 12.1 Etapa de script isolado

- script executa sozinho
- gera artefato em `out/logs` ou `out/evidence`
- schema valida
- nao interfere em fluxo atual

### 12.2 Etapa de piloto

- roda ao menos em um projeto laboratorio
- comportamento e repetivel
- falhas conhecidas estao documentadas

### 12.3 Etapa de integracao opt-in

- feature protegida por flag
- default mantido intacto
- warnings claros

---

## 13. Decisoes que o Agente Nao Pode Inventar

Se qualquer item abaixo surgir, parar e registrar decisao pendente:

- formato definitivo do dump VDP se nao estiver documentado
- forma oficial de bootstrap deterministico de cena no runtime
- thresholds canonicos de budget por tipo de cena
- politica de baseline tolerante versus exata
- schema obrigatorio final para todos os projetos

---

## 14. Veredito de Implementacao

Este plano e viavel, mas so se for seguido com disciplina:

- primeiro scripts isolados
- depois schemas
- depois piloto
- so depois integracao por flag

Qualquer tentativa de pular direto para gate ou mexer cedo no wrapper principal aumenta muito o risco de regressao operacional.
