# Epic Branding Rebrand Design

## Goal

Transformar `APP_SCENE_BRANDING` em tres setpieces memoraveis onde a tecnica do
Mega Drive produz fisicamente a marca, preservando a arquitetura e os gates ja
validados.

## Direcao Aprovada

### Slot 1 - Mega Forge Engine

- ideia: o metal esquenta, recebe impacto, esfria e toma forma;
- antecipacao: camara de forja escura, bigorna e faisca em queda;
- impacto: wordmark emerge quente, heat-wave em HScroll line e spark shower;
- resolucao: paleta esfria para aco-ciano e o logo recebe shimmer;
- duracao: 150 frames NTSC.

### Slot 2 - Misael Oliveira

- ideia: o selo pessoal do autor se revela em um vazio digital;
- antecipacao: grid fosforo escuro e scanline;
- impacto: monograma `MO` dourado, facetado e rotativo em 12 frames;
- resolucao: nome revelado progressivamente, sino cristalino e glow;
- duracao: 150 frames NTSC.

### Slot 3 - Mega Master Games

- ideia: um carimbo industrial autentica o projeto;
- antecipacao: `PRESENTS` sobe e prepara a prensa;
- impacto: escudo/metasprite cai, aciona shake, debris e transient de ruido;
- resolucao: `MEGA MASTER GAMES` e `SMOKE TEST LAB` aparecem como selo aprovado;
- duracao: 180 frames NTSC.

## Arquitetura Visual

- `BG_B`: atmosfera distinta por slot, desenhada por tiles modulares.
- `BG_A`: logos e texto estrutural.
- sprites: atores de impacto, nunca decoracao sem funcao.
- `PAL0`: BG_B; `PAL1`: logo/BG_A; `PAL2`: FX/sprites; `PAL3`: fonte ativa.
- loading model: `scene_local_preload`.
- nenhum uso de `WINDOW`, H-Int, float, heap ou DMA fora do VBlank.

## Assets

O builder dedicado `tools/image-tools/build_branding_v3_assets.py` gera:

- tres fundos modulares: forge chamber, phosphor void e industrial press;
- logos compactos com silhueta propria;
- wordmark `PRESENTS`;
- tres fontes identitarias revisadas;
- spark, monograma `MO` 32x32, cursor, shield 64x32 em quatro frames e glow;
- preview e lineage JSON.

Todos os PNGs finais devem ser indexados 4-bit, grid 8x8, maximo 16 entradas
PLTE e index 0 magenta/transparente quando aplicavel.

## Runtime

`scene_branding.c` continua como cena modular, mas cada slot possui
`enter/update/exit`. A timeline total muda para `480` frames:

- engine: `0..149`;
- author: `150..299`;
- project: `300..479`;
- teardown para boot: `480`.

O canal PSG 3 e ruido; no impacto industrial ele fornece o transient, enquanto
os canais 0-2 formam o bass stack.

## Budget Preliminar

- decisao tecnica: `cabe`;
- monograma: 12 frames x 16 tiles = 192 tiles;
- shield: 4 frames x 16 tiles = 64 tiles;
- reserva vigente de sprites: 420 tiles;
- no maximo um fundo, um logo, uma fonte e o conjunto de sprites do slot ficam
  residentes simultaneamente;
- HScroll line usa a tabela estatica existente via `DMA_QUEUE`.

## Success Criteria

- logos legiveis e distintos em 320x224;
- fundo generico anterior ausente;
- cada slot demonstra antecipacao, impacto e resolucao;
- build gera `out/rom.bin`;
- resource validation e budget sem erro tecnico;
- tres screenshots dedicadas no BlastEm;
- 60 fps estaveis e zero frame acima do budget;
- documentacao e freshness sincronizados.

