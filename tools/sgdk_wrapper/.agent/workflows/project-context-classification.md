# Workflow: Project Context Classification

Use este fluxo antes de fundar, adotar ou revisar qualquer projeto quando o tipo de trabalho ainda nao estiver explicito.

## Objetivo

Classificar se a sessao e:

- `aaa_game`: jogo real com ambicao de entrega AAA para Mega Drive
- `technical_demo`: demonstracao tecnica validavel, sem promessa de jogo completo
- `exercise`: estudo controlado, treino ou fixture
- `game_review`: auditoria ou parecer sobre projeto/material existente
- `consulting`: orientacao sem obrigacao de alterar/buildar

O contexto define quais documentos bloqueiam. Ele nao reduz os gates de entrega quando o agente promete ROM, cena ou status AAA.

## Passo 1. Ler ou materializar contexto

1. Rode `tools/sgdk_wrapper/adopt_project_methodology.ps1` quando houver projeto.
2. Abra `doc/project_context_manifest.json`.
3. Se `context_type=unclassified`, classifique pelo pedido do usuario e evidencias locais.
4. Se houver troca de contexto depois do inicio, peça confirmacao humana e registre no `context_decision_record`.

## Passo 2. Selecionar perfil documental

| Contexto | Perfil | Bloqueante por padrao |
|---|---|---|
| `aaa_game` | `full_game` | brief, GDD, TDD, spec de cenas, QA, asset register, roadmap/risk, hygiene, technique manifest, memory, changelog |
| `technical_demo` | `demo` | brief, spec de cenas, QA, technique manifest, asset register, memory, changelog |
| `exercise` | `exercise` | brief, memory, changelog, learning ledger quando aplicavel |
| `game_review` | `review` | contexto de review, memory e evidencias citadas |
| `consulting` | `consulting` | pergunta, limites, assumptions, fontes consultadas |

Documentos de release, marketing, legal, LDD completo e audio design sao `phase_blocking`: bloqueiam apenas quando a fase ou a promessa exigir.

## Passo 3. Rodar validador

Use:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/validate_project_context.ps1 -ProjectRoot "<project>"
```

O report fica em `out/logs/project_context_report.json`.

## Passo 4. Regras de decisao

- Pedido direto de "fazer jogo completo", "AAA", "vertical slice" ou "entrega final" classifica como `aaa_game`.
- Pedido de "demo tecnica", "benchmark visual", "provar tecnica" classifica como `technical_demo`.
- Pedido de "estudo", "treino", "fixture", "laboratorio" classifica como `exercise`, exceto quando houver promessa de ROM demo.
- Pedido de "avalie", "revise", "valide retorno", "parecer" classifica como `game_review`.
- Pedido de "me oriente", "faça um prompt", "como implementar" classifica como `consulting`.

Se o usuario pedir implementacao depois de uma consultoria/review, reclassifique antes de editar.

## Passa quando

- `doc/project_context_manifest.json` existe e nao esta `unclassified`.
- O perfil documental combina com o contexto.
- Os documentos bloqueantes para o contexto existem.
- O teto de promessa nao excede o que o contexto pode provar.

## Falha quando

- O agente inicia runtime/arte/build sem contexto classificado.
- Um exercicio tenta declarar `ready_for_aaa`.
- Um review exige ROM sem pedido de implementacao.
- Um jogo AAA nao tem GDD/TDD/spec/QA/asset register/roadmap.
