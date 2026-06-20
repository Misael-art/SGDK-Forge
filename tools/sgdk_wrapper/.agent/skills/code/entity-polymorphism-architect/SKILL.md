---
name: entity-polymorphism-architect
description: Use quando inimigos, bosses, objetos ou pickups SGDK precisarem de comportamento variavel sem switch central gigante, com archetypes e function pointers.
---

# Entity Polymorphism Architect

Organiza variacao de comportamento em dados e callbacks C simples.

## Contrato Operacional

### Entrada minima

- catalogo de archetypes
- estados e eventos comuns
- limite simultaneo de entidades
- requisitos de spawn, update e teardown

### Saida minima

- `entity_vtable_plan`
- layout de pool estatico
- ordem deterministica de update
- lifecycle e fixtures por archetype

### Passa quando

- callbacks possuem assinatura comum
- pool tem capacidade e politica de falha
- spawn/despawn nao deixa handles pendentes
- update order e reproduzivel
- archetypes nao dependem de switch central para cada comportamento

### Handoff para proxima etapa

- entregar tabelas e pool a `sgdk-runtime-coder`
- entregar pior quadro de entidades a `megadrive-vdp-budget-analyst`
- entregar comportamento de inimigos a `enemy-design-canonical`

## Regras

- Usar arrays fixos e indices/handles; sem `malloc`/`free`.
- Dados compartilhados ficam no archetype; estado mutavel fica na instancia.
- Callback ausente usa comportamento neutro explicito.
- Boss modular nao e inferido por nome: exige contrato proprio.

## Anti-padroes

- switch por tipo em todo subsistema
- ponteiro para instancia reciclada
- spawn silenciosamente acima do pool
- update dependente da ordem acidental de memoria
