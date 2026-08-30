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

- `doc/project_context_manifest.json`
- docs de contexto ausentes: `00-project-brief.md`, `15-tdd.md`, `16-ldd.md`, `17-audio-design.md`, `18-asset-register.json`, `19-roadmap-risk-register.md`, `20-release-marketing-legal.md`, `21-review-consulting-context.md`
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
- declare `project_context` para bloquear abertura sem saber se e jogo AAA, demo tecnica, exercicio, review ou consultoria
- garanta que `project.name`, nome do diretorio e `.mddev/project.json` sejam coerentes e sem `__PROJECT_NAME__`
- classifique cada claim como `required` ou `not_applicable`
- nunca deixe `review_required` antes do closeout

No `project_context_manifest.json`:

- classifique `context_type` como `aaa_game`, `technical_demo`, `exercise`, `game_review` ou `consulting`
- alinhe `documentation_profile` e `delivery_claim_ceiling` ao contexto
- mantenha `context_decision_record` com motivo e origem da decisao
- nao trate documentos `phase_blocking` como bloqueio imediato quando o contexto/fase nao exige

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

## Passo 3a. Fechamento pre-runtime para `aaa_game`

Licao candidata extraida de `Celestial Chase Revive [VER.001] [SGDK 211] [GEN]
[GAME] [ACTION_RACING]`, evidencia `E1_project_artifact`. Use como gate
proporcional para jogos AAA/vertical slice; nao aplique como burocracia em
`exercise`, `technical_demo` pequeno, `consulting` ou `game_review`.

Antes de abrir runtime jogavel, o agente deve verificar se o pacote de specs
tem contratos executaveis para os pontos que costumam virar retrabalho:

- formato de dados de fase/pista
- colisao, hitbox e limites de gameplay
- HUD/Window Plane e ownership de UI
- animacao/sprite sheet e escala visual
- tuning numerico de progressao/dificuldade
- asset production spec e manifesto de mockups locais quando houver referencia
- build system contract apontando para o wrapper central
- boss/setpiece quando estiver no escopo
- pause, game over, continue e retorno ao title
- front-end identity minima: logo, fonte, menu e creditos quando o jogo tiver
  title/menu

Se estes contratos estiverem ausentes, o status maximo do planejamento e
`documentado_incompleto`. Se existirem mas nao houver ROM, asset, budget ou
BlastEm, o status maximo continua `documentado`.

Mockups locais podem orientar direcao de arte somente quando possuem hash,
origem local e `mockup_reference_only`; nunca sao arte final, prova visual ou
evidencia de emulador.

Para `aaa_game`, antes do primeiro runtime seed que promete fantasia jogavel,
emitir ou revisar uma passagem de coesao criativa: ameaca/presenca antagonista,
risco sistemico, identidade mecanica por setor, momento assinatura, audio como
feedback e gancho de replay. Esta passagem nao prova diversao; ela impede que
um pacote tecnicamente correto nasca generico.

## Passo 4. Validar

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/validate_project_context.ps1 -ProjectRoot "<projeto>"
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/validate_project_methodology.ps1 -ProjectRoot "<projeto>"
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/validate_project_hygiene.ps1 -ProjectRoot "<projeto>"
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/audit_project_learning.ps1 -ProjectRoot "<projeto>" -Mode Audit
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/validate_resources.ps1 -WorkDir "<projeto>"
```

## Passa quando

- `project_methodology_report.json` tem `status=passed`
- `project_context_report.json` tem `status=passed`
- o contexto nao esta `unclassified`
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
