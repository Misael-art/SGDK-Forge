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
- o asset pertence ao `active_epoch` do `visual_workset_manifest`; estado
  `frozen_case_study` bloqueia qualquer claim novo de producao visual
- `ready_for_aaa` exige todos os gates aplicaveis
- `ready_for_aaa` exige `live_scene_bar_report.status=passed` no slice visual (`doc/03_art/18_live_scene_bar.md`); ausencia vira `live_scene_bar_report_missing`
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
| pixel art AAA / barra viva / Rheo / Pigsy | `visual-excellence-standards` + `art-translation-to-vdp`; laudo `live_scene_bar_report` |
| sprite/sheet/objeto/FX autoral de concept ou high-res | `native-sprite-production`; record validado + pixel, visual, escala, budget e humano separados |
| strip, ciclo ou sprite sheet animada | `sprite-animation`; `animation_candidate_gate_report` hash-bound + revisao visual cega + budget/runtime proporcionais |

## Regras

- Build verde nao prova gameplay, visual, audio, budget ou AAA.
- Runtime ou ROM que ainda alcanca `visual_lab_control`, `negative_evidence`,
  `procedural_code_probe` ou epoca superseded e evidencia de laboratorio, nao entrega.
- E1 orienta investigacao; nao promove regra automaticamente.
- Alias legado nunca recebe claim novo.
- Blocker repetido exige mudanca que o ataque diretamente.
- Falha de uma unica ferramenta encerra a rota, nao o projeto; use
  `workflows/causal-persistence-loop.md` enquanto houver alternativa segura.
- Gate humano bloqueia apenas os ramos que dependem materialmente da decisao.
- Pedido explicito de forward-test continuo pode adiar o gate humano por meio de
  `deferred_nonpromotional_review`: rework e prototipos reversiveis continuam em
  staging, mas aprovacao humana, promocao e claims permanecem bloqueados.
- Persistencia nunca amplia escopo, autorizacao ou teto de claim.
- Técnica experimental exige fixture isolada, budget, fallback e BlastEm.
- Sprite, sheet ou strip critico so pode ser promovido com
  `lineart_blocking_1px`, `native_sprite_production_record` e variantes
  `basic`+`elite` na trilha (`native-sprite-production` +
  `art-translation-to-vdp`); ausencia vira `translation_route_skipped` e
  bloqueia `elite_ready`, `delivery` e `ready_for_aaa`. Leia
  `references/conception_agent_brief.md` antes de conceber.
- Sprite nativo critico exige `validate_native_sprite_production.py` com
  veredito `passed`; veredito `failed` vira `native_sprite_semantic_gate_failed`
  e bloqueia `elite_ready`/`delivery`. O guardian apenas CONSUME o veredito
  (proveniencia, evidencias distintas, pixel ree-derivado, scale report) — a
  logica semantica vive no validator, nunca duplicada aqui.
- Animacao critica exige `validate_animation_candidate.py` com veredito `ok` e
  `maximum_proven_claim` compativel. O guardian nao aceita `visual_pass` isolado:
  fidelity, art_direction e blind_visual_review precisam estar `passed`; conflito
  de timing, frame lineage ou metasprite bloqueia `delivery`/`ready_for_aaa`.
- Animacao premium/AAA exige `animation_principles_report` completo e hash-bound
  para cada acao, com os 12 principios e `production_method`. O guardian consome
  o veredito do agregado: apelo, staging, exaggeration e solid drawing nao podem
  ser aprovados apenas por automacao; `needs_review` bloqueia `delivery` e
  `ready_for_aaa`.
- `motion_semantic_candidate` exige report da versao canonica vigente e rejeita
  pose unica escalada/deslocada, lineart procedural declarada nativa e contato
  de apoio meramente declarado.

## Anti-padroes

- preservar contagem histórica de skills
- screenshot estática para provar movimento ou efeito mid-frame
- chamar placeholder de entrega
- expandir infraestrutura enquanto blocker dominante permanece
- gerar direto o PNG do SGDK — produzir asset final quantizado por conversao
  direta de concept sem `art-translation-to-vdp` (basic/elite) e
  `lineart_blocking_1px`
- promover `mechanical_scale_probe` ou mudar a escala travada porque a versao
  maior parece melhor ampliada
