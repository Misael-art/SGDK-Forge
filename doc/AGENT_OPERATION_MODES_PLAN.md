# Agent Operation Modes Plan

Status: `canonical_implementation_plan`

## Objetivo

Organizar a entrada do agente em cinco modos de operacao, separando producao,
aprendizado, laboratorio e curadoria sem substituir os pipelines ja
canonizados.

O sistema deve funcionar em chat, CLI, IDE ou qualquer modelo de linguagem
porque se baseia em documentos, schemas e workflows locais, nao em recurso
proprietario de uma interface especifica.

## Analise Dos Planos Recebidos

Os dois planos convergem em quatro pontos corretos:

- falta uma camada de bootstrap acima de `project-opening.md`;
- os cinco modos precisam mapear para workflows existentes;
- alternancia de perspectiva precisa pedir consentimento humano;
- aprendizado e curadoria nao podem aplicar patch canonico automaticamente.

Pontos aproveitados:

- menu inicial com mascote ASCII;
- estado de sessao validavel;
- workflow central de bootstrap;
- gate de alternancia entre perspectivas;
- modos especificos para treino, laboratorio e curadoria.

Pontos ajustados por conservadorismo:

- nao criar uma segunda arvore de agentes ou skills;
- nao duplicar `project-opening`, `production-loop` ou `project-learning-loop`;
- nao criar arquivo solto novo na raiz alem dos que ja sao canonicos;
- nao copiar mascote, marca ou interface de outra ferramenta;
- nao transformar laboratorio em bypass de entrega;
- nao deixar o menu bloquear uma solicitacao direta e clara do usuario.

## Decisao Arquitetural

Criar uma camada fina chamada `Agent Session Bootstrap`.

Ela:

1. apresenta o menu quando a sessao nao tem tarefa explicita ou quando o
   usuario pede menu/modo;
2. registra o modo em `doc/agent_session_state.json`;
3. roteia para workflows existentes;
4. oferece troca de perspectiva com consentimento;
5. preserva a regra de ferro: entrega real exige ROM vista no BlastEm.

Ela nao:

- executa build;
- valida projeto;
- altera canone automaticamente;
- substitui os gates existentes;
- transforma proposta em escopo sem aprovacao.

## Menu Canonico

Mascote original do workspace: `FORGE-16`.

```text
+--------------------------------------------------+
|                 SGDK FORGE                       |
|        .----.      FORGE-16      .----.          |
|       / o  o \   16-BIT READY   / o  o \         |
|       \  --  /------------------\  --  /         |
|        '----'                    '----'          |
+--------------------------------------------------+

[1] CRIAR NOVO PROJETO DE JOGO DE MEGA DRIVE
[2] ANALISAR PROJETO EXISTENTE
[3] TREINAR AGENTE
[4] LABORATORIO
[5] CURADORIA
```

O mascote aparece no menu e nas transicoes de modo. Durante execucao tecnica,
o agente volta ao tom operacional normal.

## Modos

| Modo | Uso | Workflow principal | Saida minima |
|---|---|---|---|
| `create_new_project` | fundar projeto ou reseed autorizado | `project-opening.md` -> `game-design-planning` -> `5-stage-production.md` | fundacao documental, rota, manifesto, GDD/spec seeds |
| `analyze_existing_project` | auditar, continuar ou corrigir projeto existente | `project-opening.md` + `project-methodology-adoption.md` + `route-decision-gate.md` | estado real, blockers, rota de continuidade |
| `train_agent` | aprender a partir de pratica controlada | `agent-training-mode.md` + `project-learning-loop.md` | ledger local, proposta `not_applied`, zero patch automatico |
| `laboratory` | testar tecnica/hipotese sem contaminar produto | `laboratory-mode.md` | lab report, `lab_not_delivery=true`, evidencia delimitada |
| `curation` | reconciliar propostas, docs, drift e canone | `curation-mode.md` | decisao humana, patch controlado, regressao |

## Perspectivas

Perspectivas nao sao novos agentes. Sao lentes operacionais que roteiam para
skills reais:

| Perspectiva | Foco | Skills/workflows comuns |
|---|---|---|
| `director` | escopo, promessa, GDD, radar criativo | `game-design-planning`, `creative_director_radar` |
| `architect` | TDD, FSM, ownership, estrutura | `tdd-authoring`, `scene-state-architect` |
| `artist` | arte, UI, animacao, traducao VDP | `visual-excellence-standards`, `sprite-animation` |
| `hardware` | VRAM, DMA, sprites, budget | `megadrive-vdp-budget-analyst` |
| `coder` | C/SGDK, build, runtime | `sgdk-runtime-coder`, `sgdk-build-wrapper-operator` |
| `audio` | XGM2, SFX, PCM, states | `xgm2-audio-director`, `z80-pcm-custom-driver` |
| `qa` | validacao, BlastEm, freshness | `build-validate`, `rom-mastering` |
| `learner` | auditoria/captura local | `project-learning-loop` |
| `curator` | patch canonico revisado | `truth-hierarchy-guard`, `doc-sync-audit` |
| `lab_operator` | experimento isolado | `laboratory-mode` |

Troca de perspectiva exige:

- motivo;
- entrega anterior completa ou risco de continuar errado;
- proxima perspectiva sugerida;
- artefatos esperados;
- confirmacao do usuario.

## Estado De Sessao

Arquivo:

- `doc/agent_session_state.json`

Schema:

- `tools/sgdk_wrapper/schemas/agent_session_state.schema.json`

O estado registra:

- modo atual;
- perspectiva atual;
- projeto ativo opcional;
- historico de transicoes;
- transicao pendente;
- insights pendentes;
- politica de consentimento.

O estado nao substitui `doc/10-memory-bank.md`, changelog, reports ou
evidencia de projeto.

## Organizacao Dos Ambientes

| Area | Local | Regra |
|---|---|---|
| Producao | `SGDK_projects/<project>/` ou `SGDK_Engines/<project>/` | segue todos os gates |
| Treino | `SGDK_projects/_agent_training/` | sempre `LAB/TRAINING`, sem claim AAA |
| Laboratorio | `SGDK_projects/_agent_laboratory/` | sempre `LAB/TECHDEMO`, isolado |
| Aprendizado local | `<project>/doc/agent_learning/` | `Audit` read-only, `Capture` local |
| Curadoria canonica | `tools/sgdk_wrapper/.agent/`, `tools/sgdk_wrapper/`, `doc/` | somente com aprovacao humana e regressao |

## Gatilhos De Menu

Mostrar o menu quando:

- o usuario pedir `menu`, `modo`, `iniciar`, `abrir sessao` ou equivalente;
- a solicitacao inicial for ambigua;
- o agente precisar confirmar se a intencao e produzir, analisar, treinar,
  experimentar ou curar.

Nao mostrar o menu quando:

- o usuario pedir uma tarefa clara e direta;
- ja houver modo ativo coerente com a tarefa;
- mostrar o menu atrasaria uma correcao urgente claramente definida.

## Riscos E Mitigacoes

| Risco | Mitigacao |
|---|---|
| Menu virar burocracia | menu e gatilho, nao gate universal |
| Treino contaminar canone | `project-learning-loop` mantem propostas `not_applied` |
| Laboratorio virar entrega | `lab_not_delivery=true`, sem `ready_for_aaa` |
| Perspectiva virar persona ficticia | cada perspectiva referencia skills reais |
| Estado stale enganar agente | estado e auxiliar; hierarquia de verdade continua superior |
| Mascote virar tom infantil na execucao | mascote so no menu/transicao |

## Implementacao

Arquivos novos:

- `tools/sgdk_wrapper/schemas/agent_session_state.schema.json`
- `doc/agent_session_state.json`
- `tools/sgdk_wrapper/.agent/workflows/agent-session-bootstrap.md`
- `tools/sgdk_wrapper/.agent/workflows/perspective-switch-gate.md`
- `tools/sgdk_wrapper/.agent/workflows/agent-training-mode.md`
- `tools/sgdk_wrapper/.agent/workflows/laboratory-mode.md`
- `tools/sgdk_wrapper/.agent/workflows/curation-mode.md`
- `tools/sgdk_wrapper/show_agent_menu.ps1`
- `SGDK_projects/_agent_training/README.md`
- `SGDK_projects/_agent_laboratory/README.md`
- `.cursor/rules/session-bootstrap.mdc`

Arquivos ajustados:

- `AGENTS.md`
- `CLAUDE.md`
- `.agents/README.md`
- `tools/sgdk_wrapper/.agent/ARCHITECTURE.md`
- `tools/sgdk_wrapper/.agent/framework_manifest.json`
- `tools/sgdk_wrapper/ci/test_schema_contract_gates.py`
- `doc/06_AI_MEMORY_BANK.md`

## Aceitacao

Aceito quando:

- menu renderiza via script;
- schema valida estado canonico;
- testes rejeitam modo invalido e consentimento desligado;
- framework validation passa;
- full contract gate passa;
- memoria canonica registra a mudanca;
- nenhum workflow existente de producao/aprendizado/curadoria e substituido.
