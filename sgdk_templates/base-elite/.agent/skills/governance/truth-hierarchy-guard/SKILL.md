---
name: truth-hierarchy-guard
description: Carrega e aplica a hierarquia de verdade, gates e disciplina documental de projetos SGDK.
---

# Truth Hierarchy Guard

Use esta skill antes de qualquer analise, plano ou implementacao relevante em projetos SGDK.

## Objetivo

Garantir que a IA parta do estado real do projeto, e nao de suposicoes.

## Contrato Operacional

### Entrada minima

- raiz do projeto
- docs existentes em `doc/` e manifesto `.mddev/project.json` (quando existir)
- qualquer evidência operacional ja gerada (`out/logs/validation_report.json` quando existir)

### Saida minima

- qual fonte venceu (com hierarquia explicitada)
- quais docs estao faltando, vencidos ou em conflito
- classificacao do pedido: `escopo real`, `futuro_arquitetural` ou `deriva`
- riscos de drift que bloqueiam declaracao de "pronto"

### Passa quando

- a fonte de maior autoridade esta declarada sem ambiguidade
- contradicoes relevantes foram sinalizadas com proposta objetiva de resolucao

### Handoff para proxima etapa

- se for trabalho multi-arquivo: entregar contexto para `workflows/plan.md`
- se for auditoria: entregar conflitos para `governance/doc-sync-audit`

## Checklist

- ler `doc/10-memory-bank.md` quando existir
- ler `doc/11-gdd.md` quando existir
- ler `doc/13-spec-cenas.md` quando existir
- ler `doc/00-diretrizes-agente.md` quando existir
- identificar lacunas entre documentacao e codigo
- classificar o pedido em `escopo real`, `futuro arquitetural` ou `deriva`

## Saida minima

- qual fonte venceu
- quais docs estao faltando ou vencidos
- se existe risco de drift

## Proibido

- responder como se a implementacao ja existisse quando ela so estiver documentada
- tratar placeholder como final
