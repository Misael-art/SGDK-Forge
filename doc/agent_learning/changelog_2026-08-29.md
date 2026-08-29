# Changelog de aprendizado - 2026-08-29

Status: `doctrine_canonized_runtime_unproven`

## Barra viva da cena

- O operador fixou o piso visual do Forge no oficio da cena viva, nao
  na barra 1994 sozinha e nao nos handles como celebridade.
- Evidencia publica decodificada (nao copiada):
  - RheoGamer: densidade arcade legal, paleta com papel, stage reautorado
    (~980 tiles BG+FG), metasprite, streaming comprimido, 60 fps, SGDK,
    Everdrive como verdade, tese VRAM+CRAM+decisao artistica.
  - PigsyRetro: source→MD sem quantize cego, S/H como cor extra e
    transparencia falsa, enhanced 8-bit, matching 9-bit manual, paleta
    compartilhada, parallax como upgrade, prova em movimento.
- Artefatos: `doc/03_art/18_live_scene_bar.md`,
  `doc/03_art/live_scene_bar.json`,
  `tools/sgdk_wrapper/schemas/live_scene_bar_report.schema.json`,
  brief, SGDK_GLOBAL §39, plano `19_plan_pixel_art_live_scene_capability.md`.

## Correcao de rota de geracao

- Exemplos de prompt que pediam "pixel art sprite sheet Mega Drive"
  em `art-creation-sourcing` foram substituidos por concept/volume.
  Esses prompts produziam fake pixel art e contradiziam a sprint 03.

## Honestidade de status

- `runtime_proof_status` da barra: `NAO_INICIADA`.
- Gargalo permanece o do censo grafico 2026-08-06: veto maduro,
  redesenho nativo imaturo.
- Proximo agente executa Fase 1 (fonte persistida), nao reescreve a
  doutrina.

## Expansao da barra — time da cena (2026-08-29b)

Operador acrescentou ponteiros. Oficio extraido, nao IP:

- Pyron: restage de palco ao teto de VRAM; lembrar artwork, nao dump.
- ReySilveira28/Chev: segundo passe; 512 wide para scroll, gate 320x224
  4:3; sem cola de tile; beleza > demo de Mode 7.
- Diggo: arrange YM2612 com identidade Neo Geo; trilha co-autora.
- MXRetroDev (1900597106068296043): carta de paletas compartilhadas do
  FFMD; alt vs palco; mais atores cortam objetos.
- Shannon (2077723799316013354): buffer 3D 256x160, planos como
  framebuffer, sprites como fundo multiplexado, XGM1 porque DMA mata
  XGM2, ~20 fps com musica, LUT, dirty DMA.
- Daniel Moura (1824963016586056183): HAMOOPIG; luta e contrato; "sim
  isso e Mega Drive"; repros ameacam o oficio.

Fixtures novas no plano 19: F-Y1, F-C1, F-M1, F-D1, F-H1, F-S1.
Runtime proof continua `NAO_INICIADA`.

## Parametros de concepcao (2026-08-29c)

Fonte unica de tetos: `doc/03_art/live_scene_bar_parameters.json`.
Nao duplicar ensaio. Oficio novo so o que faltava: G1/G2 (SGDK base
nao teto; driver medido), D4 (arrange sob DMA), Z1 (0 lag), S6
(multiplex extremo e opt-in). Handles extras mapeados, nao viram
escola. Correcoes: CRAM=4 paletas; XGM2 nao e automaticamente mais
leve sob DMA alto; 1000 sprites e 97% CPU nao sao default de produto.

Cadeia de modos: brief + project-opening + laboratory-mode +
scene-direction-first passo 4 + agent-session-bootstrap.

## F-R2 fase 2 — lineart nativo 48x64 (2026-08-29d)

LIVE_BAR_FR2 reconstruiu heroi e thug no grid 48x64 com
`lineart_blocking_1px` (1 px, tinta temporaria, papel de construcao).
Nao e downscale da pintura. Fontes Imagine + desenhos de construcao
em `data/source_art/`. Downscale v001 marcado
`obsolete_for_generation_source`. ROM 131072 B sha256
`4c07c842ab5509c79a05743836e663ffcb9bb1f5d3f359e25ee8069749f5642d`.
BlastEm screenshot mostra os dois lutadores em lineart no cais;
semantic gate `passed`; bundle canonico ainda rejeitado (VLAB/dump).
Cais continua quantize. Cor/rampas nao comecaram. `visual_pass=false`.
`lab_not_delivery=true`.

## F-R2 fase 2b — color blocking com rampas (2026-08-29e)

Color blocking no lineart 48x64 travado. Silhueta nao mexeu. Tinta de
construcao (corda, abertura do colete, alcas) preservada. Rampas 9-bit
com hue shift: pele, colete teal, tanque vermelho, bermuda. Outline =
dark_shadow, fora de swap. Painel lineart/basic/elite. ROM
`f694b841e8f1450b481d45b5be5a35ac1a25eb3dc96fe5d24e00a592e10c73f9`
vista no BlastEm: heroi teal vs thug vermelho no cais. Cais ainda
quantize. `visual_pass=false`. `lab_not_delivery=true`.

## F-R2 fase 2c — cais nativo 8x8 (2026-08-29f)

Cais reautorado com vocabulario de tiles 8x8 (99 unicos vs 931 da
pintura quantizada). `compare_flat` num IMAGE 320x224. Indice 0 do
plano nao pintado (VDP transparente; backdrop = nevoa PAL2). Recursos
7 KB vs 33 KB. ROM
`2411a37d0472f59aaccf1228ec3811b5ef0128ee97ceb350b27ccff70663b3ed`
vista no BlastEm. Nao e palco dual-plane nem `visual_pass`. Sem motion.

## F-R2 idle + agua (2026-08-29g)

Video Imagine de guarda no lugar → harvest; pixels do idle sao deltas
no sprite 48x64 travado (4 frames, pes plantados, time=12). Ciclo PAL2
slots 4-6 na agua. ROM
`e3720f3210180dbf70e55fb65f5fe31703e64d60b5fcce630487f3b8691dca99`
com GIF de burst no BlastEm. Continua `lab_not_delivery`. Nao e
`ready_for_aaa`. O patamar AAA pede cena de `aaa_game` + humano, nao
esta fixture sozinha.
