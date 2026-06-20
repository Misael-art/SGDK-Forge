---
name: aaa-pipeline-guardian
description: Use quando prompt, plano ou entrega alegar AAA, tecnica avancada de Mega Drive, port complexo, jogo completo, stable, release ou ready_for_aaa.
---

# AAA Pipeline Guardian

Seleciona gates proporcionais e limita status ao menor claim realmente provado.
Nao substitui especialistas.

## Contrato Operacional

### Entrada minima

- claims tecnicos, visuais e de entrega
- contexto e metodologia do projeto
- artefatos, reports e evidencia existentes
- owners ativos no lifecycle registry

### Saida minima

- `aaa_pipeline_gate_report`
- matriz claim -> owner -> artefato
- blockers e proximas acoes
- decisao de status por escopo

### Passa quando

- cada claim importante possui owner ativo
- ausencia de contrato vira blocker
- evidencia esta fresca e vinculada ao mesmo hash
- `ready_for_aaa` exige todos os gates aplicaveis
- a decisao pode ser reproduzida pelos mesmos arquivos

### Handoff para proxima etapa

- encaminhar cada claim ao owner ativo
- entregar blockers a planejamento, runtime, budget e closeout

## Roteamento minimo

| Claim | Owner |
|---|---|
| colisao, one-way, slope, boxes | `collision-system-architect` |
| streaming ou dirty tiles | `vram-streaming-dma-queue` |
| Shadow/Highlight, H-Int, scroll FX | `shadow-highlight-scroll-fx` |
| entidades por archetype | `entity-polymorphism-architect` |
| transicao de estado | `game-state-transition-architect` |
| camera | `camera-system-sgdk` |
| input | `input-system-sgdk` |
| VDP/CRAM/DMA/scanline | `megadrive-vdp-budget-analyst` |
| evidencia BlastEm | `emulator-vdp-evidence-curator` |

## Regras

- Build verde nao prova gameplay, visual, audio, budget ou AAA.
- E1 orienta investigacao; nao promove regra automaticamente.
- Alias legado nunca recebe claim novo.
- Blocker repetido exige mudanca que o ataque diretamente.
- Técnica experimental exige fixture isolada, budget, fallback e BlastEm.

## Anti-padroes

- preservar contagem histórica de skills
- screenshot estática para provar movimento ou efeito mid-frame
- chamar placeholder de entrega
- expandir infraestrutura enquanto blocker dominante permanece
