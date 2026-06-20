# Case Study - Pequenos desenvolvedores e arquitetura sob restricao

Status: `case_study_candidate`
Owners principais: `entity-polymorphism-architect`, `vram-streaming-dma-queue`, `game-state-transition-architect`
Owners complementares: `z80-pcm-custom-driver`, `megadrive-vdp-budget-analyst`, `sgdk-runtime-coder`

## Licao util

O valor tecnico dos estudos sobre estúdios pequenos nao e "copiar hacks". A
licao reutilizavel e decompor sistemas complexos em donos claros: CPU principal
para logica e transformacoes, Z80 para audio quando justificado, VDP para
planos/sprites/CRAM, e pipelines que medem o pior quadro antes de prometer
espetaculo.

## O que o agente deve absorver

- Catalogos de inimigos e objetos precisam de archetypes e function pointers,
  nao switch-case espalhado por todo subsistema.
- Chefe grande deve ser orcado como partes, janelas ativas e scanlines reais.
- Streaming de tiles e tile animation precisam de fila DMA e slots de VRAM.
- Transicoes de estado precisam de mutex, flush e reset de callbacks.
- Drivers Z80 customizados so entram com owner, formato, prioridade e benchmark.

## Gate recomendado

1. `entity_vtable_plan` para catalogo de entidades.
2. `dma_queue_contract` para streaming/animacao de tiles.
3. `state_transition_contract` para troca de cena.
4. `audio_architecture_card` para qualquer isolamento Z80/PCM.
5. `constraint_budget_report` ou budget equivalente no pior quadro.

## Limites

- Engenharia reversa historica nao autoriza comportamento inseguro por default.
- SAT reuse, mid-frame tricks e quirks entram apenas como `signature_only`.
- Assembly inline so entra quando o C/SGDK medido nao cumpre budget e o trecho
  critico tem fixture.

## Falha que previne

Evita engine crescente com switch-case gigante, transicoes reentrantes,
streaming sem slot de VRAM e promessas de performance sem pior quadro medido.
