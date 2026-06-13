# 07 - Budget VRAM e DMA - Celestial Chase First Playable

Status: `validado_budget_tecnico_v011`; aprovacao perceptual humana e dump VDP visual permanecem pendentes.

## Particao VRAM

- `TILE_MAX_NUM`: 1536 tiles antes das tabelas em `0xC000`
- sistema: 16 tiles
- fonte: 96 tiles
- sprite engine: `SPR_initEx(680)`
- user tiles disponiveis para BG_A + BG_B + letterbox: `744`
- BG_B v011 medido pelo snapshot ResComp ligado ao hash da ROM: `488` tiles unicos
- BG_A v011 de 512px medido pelo snapshot ResComp ligado ao hash da ROM: `186` tiles unicos
- letterbox v009: `1` tile
- total de background: `675`
- headroom de user tiles: `69`
- custo incremental real dos gutters laterais v011: `1` tile unico

O controle `basic` usa `1355` tiles e nao cabe. A v011 cabe somente com
traducao tile-aware, deduplicacao dos gutters, reserva de sprites em 680 tiles
e residencia scene-local confirmada pelo `res_graph`.

## Resident Set

- BG_B: atmosfera/horizonte, PAL0, 488 tiles
- BG_A: road/foreground 512px com gutters seguros, PAL3, 186 tiles
- letterbox: PAL3, 1 tile
- hero: PAL1, pior frame 80 tiles
- dois afterimages do hero: PAL1, 80 tiles compartilhados
- pursuer torso + head + duas garras: PAL2, 264 tiles; garra distante compartilha 64 tiles
- tres slots de obstaculo, um por tipo: PAL2, 112 tiles
- energy pickup: PAL2, 16 tiles
- Pulse: PAL2, 48 tiles
- dust: PAL2, 32 tiles
- duas nuvens diagonais: PAL0, 32 tiles compartilhados
- total estimado alocado pelo sprite engine: `648/680` tiles

Duplicatas frame-locked compartilham slots de VRAM via `SPR_addSpriteEx`; o pool
de obstaculos representa o pior conjunto simultaneo real. Pools sao criados no
`enter` e ficam ocultos quando inativos para evitar alocacao surpresa.

## DMA

- preload de background: 27.776 bytes no `enter`
- preload dos frames iniciais do pool: ate 12.544 bytes no `enter`
- BG_A line scroll: 448 bytes por VBlank quando habilitado
- BG_B line scroll: 448 bytes por VBlank quando `HSCROLL_LINE` esta ativo
- BG_A/BG_B column scroll: 80 bytes por VBlank
- tabelas de estrada usam cadencia de 30 Hz; atores/logica e shake de impacto permanecem em 60 Hz
- SAT do sprite engine: 640 bytes por VBlank
- hero frame: ate 2.560 bytes
- pursuer frame: ate 3.840 bytes
- dust frame: ate 1.024 bytes

Hero e modulos do pursuer nao podem trocar frame no mesmo VBlank. A cena alterna
a prioridade e o rig alterna torso/cabeca contra garras. O trace DMA detalhado
continua pendente, portanto nenhuma folga adicional pode ser consumida sem nova
medicao.

## Sprites e Scanline

Entradas deterministicas:

- `out/logs/sprite_scanline_traffic_v011_input.json`
- `out/logs/sprite_scanline_impact_v011_input.json`
- `out/logs/sprite_scanline_pulse_v011_input.json`
- `out/logs/sprite_scanline_pressure_report.json`

Regras runtime:

- no maximo dois hazards simultaneos em um pool de tres slots
- pickup oculto durante Pulse
- Pulse limpa hazards antes de mostrar o FX
- pursuer ocupa a faixa alta, evitando sobreposicao com Pulse
- sprites inativos ficam ocultos
- enumerador ligado a ROM cobre fases FK, bandas de pressao, frames do heroi e todos os frames de impacto/Pulse
- pior caso offline v011: `12/20` sprites por scanline, com `8` de headroom
- pico real observado pelo probe no BlastEm: `9/20` sprites por scanline

## Paletas

- PAL0: BG_B
- PAL1: hero e texto HUD
- PAL2: pursuer, hazards, pickup, dust e Pulse
- PAL3: BG_A road

Nao ha alpha blending. Index 0 do BG_A e transparencia estrutural. Mudancas de
paleta sao pequenas, documentadas e feitas no fluxo seguro do frame.

## H-Int e Scroll

- H-Int: nao usado
- owner de line/column scroll: `chase_road`
- tabelas: 224 offsets assinados por plano + 20 colunas por plano, 976 bytes no total
- hot loop de curva: diferencas finitas por soma, sem multiplicacao por scanline
- fallback: `HSCROLL_PLANE` com road estatico
- teardown: restaurar scroll de BG_A/BG_B para zero ao sair da cena

## Veredito

- eixo tecnico de residencia/scanline/runtime: `validado_budget`
- eixo DMA: `cabe_com_recuo`, trace detalhado ainda pendente
- eixo perceptivo: `aprovacao_humana_pendente`
- status maximo honesto: `testado_em_emulador` e `validado_budget_tecnico_v011`, ainda nao `ready_for_aaa`

Evidencia da ROM final SHA256
`950e35dfe1510769c3f9b9b53c45f3a91b3db1c44c273fecc8928e6a18d60a52`:

- BlastEm MDRT curto/partial: `frames_seen=151`, `over_budget_frames=0`,
  `cpu_load_max=72`, `cpu_load_p95=70`, `max_scanline_sprites=9` e
  `sprite_engine_peak=19`.
- Enumeracao offline ligada a geometria `FrameVDPSprite` da ROM: trafego `12`,
  impacto `12`, Pulse `11`; pior caso `12/20`.
- `res_graph`: `31/31` declaracoes, zero issues, zero overlaps e residencia
  medida `675/744`, com `69` tiles de headroom.
- Regressao deterministica: `3/3` cenas aprovadas.

O `visual_vdp_dump.bin` segue obrigatorio para a modalidade visual canonica
completa, mas nao invalida as medicoes tecnicas de residencia, scanline e
runtime acima.
