# Workflow: Project Methodology Adoption

Use este fluxo ao abrir qualquer projeto SGDK, novo ou antigo, antes de arte,
runtime, build de entrega ou closeout.

## Objetivo

Garantir que metodologia, skills, claims e validacoes sejam declarados em
contrato estruturado, sem inferir capacidades por palavras soltas em codigo ou
Markdown.

## Passo 1. Materializar sem sobrescrever

Execute:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/adopt_project_methodology.ps1 -ProjectRoot "<projeto>" -Lifecycle <new|existing|reseed>
```

O script cria somente arquivos ausentes:

- `doc/project_methodology_manifest.json`
- `doc/technique_usage_manifest.json`
- `doc/project_hygiene_manifest.json`
- arquivos ausentes de `doc/agent_learning/`, incluindo `learning_ledger.json`
- `rascunho/README.md`

Arquivos existentes nunca sao sobrescritos.

## Passo 2. Classificar explicitamente

No `project_methodology_manifest.json`:

- classifique `project.lifecycle`
- mantenha `active_workflow=production-loop`
- declare as skills canonicas necessarias
- declare `preflight_host`, `validate_resources` e `scene_closeout_gate`
- declare `freshness_audit` para detectar documentacao/evidencia obsoleta
- declare `project_hygiene` para bloquear orfaos, rascunho fora do lugar e entrada externa sem copia local
- garanta que `project.name`, nome do diretorio e `.mddev/project.json` sejam coerentes e sem `__PROJECT_NAME__`
- classifique cada claim como `required` ou `not_applicable`
- nunca deixe `review_required` antes do closeout

Claims estruturados iniciais:

- `critical_motion`
- `road_physics`
- `modular_boss`

Palavras como `chase`, `sBossBody`, `impact_frame` ou a simples existencia de
runtime metrics nao criam claims automaticamente.

## Passo 3. Cumprir claims requeridos

- `critical_motion`
  - exige `visual-excellence-standards` e `sgdk-runtime-coder`
  - exige simultaneamente motion GIF, aprovacao humana, screenshot dedicado,
    SRAM fresca, VDP dump e os quatro eixos perceptivos acima de zero
- `road_physics`
  - exige `level-design-canonical`, `sgdk-runtime-coder` e
    `megadrive-vdp-budget-analyst`
  - exige `road_physics_contract.json` valido e simbolos presentes no runtime
- `modular_boss`
  - exige `forward-kinematics-rigging`, `sgdk-runtime-coder` e
    `megadrive-vdp-budget-analyst`
  - exige `boss_parts.json` valido, pelo menos duas partes runtime, FK chain e
    budget de scanline

## Passo 4. Validar

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/validate_project_methodology.ps1 -ProjectRoot "<projeto>"
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/validate_project_hygiene.ps1 -ProjectRoot "<projeto>"
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/audit_project_learning.ps1 -ProjectRoot "<projeto>" -Mode Audit
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/validate_resources.ps1 -WorkDir "<projeto>"
```

## Passa quando

- `project_methodology_report.json` tem `status=passed`
- nenhum claim permanece `review_required`
- skills e validacoes obrigatorias estao declaradas
- nome do projeto segue a identidade real do diretorio e o padrao canonico
- contratos requeridos possuem conteudo e implementacao runtime verificavel
- nenhuma evidencia usada pelo gate sai do projeto; material externo utilizado possui copia local registrada
- `doc/10-memory-bank.md` e `doc/changelog/changelog.md` refletem mudancas de implementacao/arquitetura
- apos mudar apenas relatorios ou blockers, `update_project_changelog.ps1 -StatusOnly` sincroniza o estado derivado sem criar snapshots ou entradas artificiais

## Handoff

- `workflows/production-loop.md` para executar a iteracao
- `workflows/build-validate.md` para validar
- `scene_closeout_gate.ps1` para fechamento
