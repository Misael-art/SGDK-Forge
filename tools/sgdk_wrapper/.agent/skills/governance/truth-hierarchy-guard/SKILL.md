---
name: truth-hierarchy-guard
description: Carrega e aplica a hierarquia de verdade, gates e disciplina documental de projetos SGDK.
---

# Truth Hierarchy Guard

Use esta skill antes de qualquer analise, plano ou implementacao relevante em projetos SGDK.

## Objetivo

Garantir que a IA parta do estado real do projeto, e nao de suposicoes.

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
