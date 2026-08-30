# Prompt to Pipeline Gate Checklist

Status: `pipeline_update_candidate`

Use esta checklist quando um prompt pedir jogo, cena, personagem, stage,
efeito visual ou tecnica "AAA" para Mega Drive.

## 1. Classificar dominio

- claim AAA/release/tecnica avancada: `aaa-pipeline-guardian`
- personagem/sprite sheet: `character-design`, `sprite-animation`, `art-translation-to-vdp`
- stage/cena: `scene-direction-curator`, `multi-plane-composition`
- tilemap/cenario largo: `tiled-hybrid-parallax-curator`, `vram-streaming-dma-queue`
- efeito VDP: `shadow-highlight-scroll-fx`
- colisao/mecanica fisica: `collision-system-architect`
- catalogo de entidades: `entity-polymorphism-architect`
- transicao de jogo: `game-state-transition-architect`

## 2. Exigir contrato antes do asset/runtime

- claim AAA: `aaa_pipeline_gate_report`
- arte critica: visual DNA, art/gameplay direction gate e fonte canonica
- camera: camera behavior/motion contract
- tilemap: scene tilemap conversion report
- streaming: DMA queue contract
- FX scroll/raster: scroll FX contract
- entidade: entity vtable plan
- colisao: collision topology report
- transicao: state transition contract

## 3. Bloquear falso positivo

O agente nao pode declarar `ready_for_aaa` quando:

- falta revisao visual humana exigida;
- falta screenshot/emulador para claim visual;
- falta VDP dump para claim dependente de mid-frame/CRAM/scroll real;
- build verde e usado como prova de arte;
- asset parcial e usado como fonte de nova geracao;
- tecnica avancada nao tem owner, fallback ou budget.

## 4. Handoff minimo

Cada skill nova precisa entregar artefato validavel:

- `collision-system-architect` -> `collision_topology_report`
- `vram-streaming-dma-queue` -> `dma_queue_contract`
- `shadow-highlight-scroll-fx` -> `scroll_fx_contract`
- `entity-polymorphism-architect` -> `entity_vtable_plan`
- `game-state-transition-architect` -> `state_transition_contract`
- `aaa-pipeline-guardian` -> `aaa_pipeline_gate_report`

## 5. Status honesto

- `conceptual_reference`: material externo ainda sem fixture
- `case_study_candidate`: licao util com owner e limites
- `pipeline_update_candidate`: altera fluxo, mas ainda pede validacao
- `lab_candidate`: implementado em estudo, sem prova de entrega
- `candidate_applied_not_verified`: patch aplicado, runner/teste pendente
- `canonical_ready`: so apos evidencia atual, validadores e revisao humana
