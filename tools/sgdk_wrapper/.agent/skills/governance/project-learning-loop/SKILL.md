---
name: project-learning-loop
description: Use ao abrir, auditar ou fechar trabalho em projeto SGDK para consultar aprendizado local, capturar lições comprováveis, deduplicar candidatos contra owners canônicos existentes e gerar propostas de patch sem alterar automaticamente o framework.
---

# Project Learning Loop

Use esta skill para fechar o ciclo entre experiência, lição local, evidência e proposta canônica revisável.

## Principio

`doc/agent_learning/learning_ledger.json` e a fonte estruturada do aprendizado local. O agente pode atualizá-la automaticamente em `Capture`, mas nunca aplica sozinho propostas em `.agent`, skills, workflows, `lib_case`, registry, schemas ou regras globais.

Leia `references/closed_learning_loop_contract.md` antes de classificar evidência, lifecycle ou promoção.

## Entrada minima

- raiz do projeto SGDK ou contexto de campanha;
- `doc/agent_learning/` e `learning_ledger.json` quando existirem;
- evidencia real da tarefa encerrada: build, validacao, screenshot BlastEm, log, hash ou report.

## Saida minima

- status de contexto: `learning_context_present`, `learning_context_absent` ou `learning_context_incomplete`;
- índice compacto de candidatos na abertura;
- `doc/agent_learning/learning_ledger.json` atualizado no fechamento quando houver contexto local;
- `out/logs/project_learning_report.json` gerado em `Capture`;
- propostas deduplicadas contra owners existentes antes de sugerir nova skill;
- confirmação `canonical_promotion_performed=false`.

## Passa quando

- ausencia de memoria local em projeto legado vira warning, nao blocker;
- `Audit` nao escreve nenhum arquivo;
- `Capture` escreve apenas dentro do projeto;
- conteúdo local e classificado com evidência, lifecycle, routing e proposta;
- owner existente recebe proposta de patch antes de surgir sugestão de skill nova;
- toda proposta permanece `not_applied` e com aprovação humana `pending`;
- falhas observadas nao sao reescritas como sucesso.

## Operacao

### Abertura read-only

```powershell
tools/sgdk_wrapper/audit_project_learning.ps1 -ProjectRoot <projeto> -Mode Audit -OutputFormat Json
```

Leia primeiro `candidate_index`. Abra lições completas do ledger somente quando forem relevantes à tarefa atual.

### Fechamento com captura local

Depois de atualizar os registros Markdown com observações reais:

```powershell
tools/sgdk_wrapper/audit_project_learning.ps1 -ProjectRoot <projeto> -Mode Capture -OutputFormat Json
```

Confirme que os arquivos escritos estão limitados a:

- `doc/agent_learning/learning_ledger.json`;
- `out/logs/project_learning_report.json`.

### Promoção canônica

Uma proposta local só pode chegar à fila canônica após:

1. evidência suficiente e fresca;
2. deduplicação contra owner existente;
3. teste de generalização proporcional ao risco;
4. aprovação humana explícita;
5. edição canônica controlada e regressão completa.

## Proibicoes

- Nao aplique automaticamente proposta canônica.
- Nao crie skill nova quando regra, validator, schema, workflow, doc ou skill existente já possuir o problema.
- O rotulo `promotion_candidate` nao autoriza `create_skill`; primeiro compare
  titulo, problema e heuristica com `references/learning_owner_catalog.json`.
- Candidato conhecido sem match no catalogo e falha de roteamento a revisar,
  nao prova de gap puro.
- Nao use evidência externa, stale ou apenas narrativa para elevar lifecycle.
- Nao promova falha isolada ou solução ainda não comprovada.
- Nao trate ausencia de `doc/agent_learning/` em projeto legado como falha de entrega.

## Handoff

- Entregar `candidate_index`, gaps de evidência e propostas `not_applied` para revisão humana.
- Se nada reutilizável foi aprendido, manter a lição local ou encerrar como `no_qualified_lessons`.
- Sempre declarar `canonical_promotion_performed=false`, salvo após ato humano registrado e aplicação controlada fora do modo automático.
