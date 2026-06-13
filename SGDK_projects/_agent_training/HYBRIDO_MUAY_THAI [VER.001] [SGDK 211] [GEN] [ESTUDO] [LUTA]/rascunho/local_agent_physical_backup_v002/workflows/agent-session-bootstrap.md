# Agent Session Bootstrap

Status: `canonical_workflow`

## Objetivo

Oferecer uma entrada organizada para o agente sem substituir os workflows de
producao, aprendizado, laboratorio ou curadoria.

Este workflow deve funcionar em chat, CLI, IDE ou qualquer modelo porque sua
autoridade esta nos arquivos locais, schemas e runbooks canonicos.

## Quando Usar

Use este workflow quando:

- o usuario pedir `menu`, `modo`, `iniciar`, `abrir sessao` ou equivalente;
- a intencao inicial estiver ambigua;
- for necessario decidir se o trabalho e producao, analise, treino,
  laboratorio ou curadoria.

Nao use como bloqueio quando:

- o usuario ja pediu uma tarefa clara;
- ha um projeto ativo e o pedido continua a rota atual;
- a interrupcao atrasaria correcao ou validacao claramente solicitada.

## Saudacao De Entrada

Todo agente ainda deve obedecer `AGENTS.md` e dizer:

```text
[Contexto MD Carregado]
```

Depois, se o menu for apropriado, renderize `FORGE-16`:

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

O mascote e usado apenas no menu ou transicao. Durante execucao tecnica, volte
ao tom operacional normal.

## Modos

| Opcao | `current_mode` | Perspectiva inicial | Workflow inicial |
|---|---|---|---|
| 1 | `create_new_project` | `director` | `project-opening.md` |
| 2 | `analyze_existing_project` | `qa` | `project-opening.md` + `project-methodology-adoption.md` |
| 3 | `train_agent` | `learner` | `agent-training-mode.md` |
| 4 | `laboratory` | `lab_operator` | `laboratory-mode.md` |
| 5 | `curation` | `curator` | `curation-mode.md` |

## Estado

Estado canonico da sessao:

- `doc/agent_session_state.json`

Schema:

- `tools/sgdk_wrapper/schemas/agent_session_state.schema.json`

O estado registra modo, perspectiva, projeto ativo opcional, historico,
transicao pendente e politica de consentimento.

Regra:

- estado de sessao e auxiliar;
- `doc/10-memory-bank.md`, GDD, spec, manifestos, reports e evidencia de
  emulador continuam acima dele na hierarquia de verdade;
- estado stale deve ser corrigido ou ignorado quando contradizer artefatos
  reais do projeto.

## Contrato De Roteamento

1. Carregue `AGENTS.md`, `SGDK_GLOBAL.md` e `ARCHITECTURE.md`.
2. Se o pedido for direto, execute o pedido e nao force menu.
3. Se o pedido pedir menu ou estiver ambiguo, mostre o menu.
4. Ao escolher um modo, registre transicao com confirmacao humana.
5. Roteie para o workflow principal do modo.
6. Se mudar de perspectiva durante o trabalho, use
   `perspective-switch-gate.md`.
7. Ao fechar trabalho relevante, execute as validacoes exigidas pelo modo.

## Ferramenta De Apoio

Renderizacao e atualizacao leve:

```powershell
tools/sgdk_wrapper/show_agent_menu.ps1
tools/sgdk_wrapper/show_agent_menu.ps1 -Action Set -Mode analyze_existing_project -Perspective qa -ActiveProject "SGDK_projects/foo" -Reason "Usuario escolheu analisar projeto" -UserConfirmed
```

A ferramenta nao executa build, nao muda canone e nao aprova entrega. Ela so
ajuda a manter o estado da sessao legivel.

## Regras De Consentimento

Exigem confirmacao humana explicita:

- troca de modo;
- troca de perspectiva;
- entrada em laboratorio;
- aplicacao de patch canonico;
- promocao de aprendizado local para curadoria canonica.

Nao exigem menu:

- correcao pontual claramente solicitada;
- leitura de arquivo;
- validacao direta;
- pergunta objetiva sobre estado do workspace.

## Entregaveis Minimos Por Modo

| Modo | Entregavel minimo |
|---|---|
| `create_new_project` | brief, GDD/TDD seed, metodologia, rota e primeiro slice |
| `analyze_existing_project` | estado real, blockers, rota de continuidade e validacoes |
| `train_agent` | ledger local e propostas `not_applied` |
| `laboratory` | lab report com `lab_not_delivery=true` |
| `curation` | decisao, patch revisado, regressao e memoria canonica |

## Anti-Drift

- Nao crie novas arvores paralelas de skills.
- Nao duplique `project-opening.md`, `production-loop.md` ou
  `project-learning-loop.md`.
- Nao coloque treino ou laboratorio na raiz do workspace.
- Nao use resultado de laboratorio como prova de entrega.
- Nao transforme proposta de aprendizado em regra canonica sem aprovacao
  humana e teste.

