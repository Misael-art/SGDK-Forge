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
