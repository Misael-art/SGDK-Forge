---
prd_id: PRD-00
title: Autonomy Charter
status: seed
applies_to: [prototype, AAA, stable, release, delivery]
unlocks: [autonomous_decision_authority]
owner: agent
last_validated: null
---

# Autonomy Charter

## Decisoes Que O Agente Pode Tomar

- escolher nomes internos, filenames, ids de cena e organizacao local quando nao mudarem a fantasia do jogo
- preencher lacunas pequenas com a opcao mais conservadora do GDD e registrar em `doc/10-memory-bank.md`
- reduzir escopo visual, audio ou runtime para manter 60 fps e evidencia verificavel
- criar fallback de laboratorio somente com `lab_not_delivery=true`

## Decisoes Que Exigem Bloqueio Ou Escalada

- mudar genero, fantasia central, publico alvo ou promessa do jogador
- usar arte comercial, benchmark, rip ou derivado como fonte final sem licenca explicita
- declarar AAA/stable/release sem todos os gates de evidencia
- promover asset critico com `needs_review`, fonte invalida ou budget nao medido

## Politica De Preenchimento

Quando uma decisao criativa nao estiver especificada, o agente deve:

1. consultar o PRD correspondente no `doc/prd_index.json`
2. se o PRD estiver `filled` ou `locked`, obedecer
3. se estiver `seed`, preencher de forma conservadora e registrar a decisao
4. se estiver ausente e for bloqueante, parar com blocker rastreavel

