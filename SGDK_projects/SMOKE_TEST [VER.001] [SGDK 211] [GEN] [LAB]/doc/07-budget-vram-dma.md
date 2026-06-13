# 07 - Budget VRAM e DMA — SMOKE_TEST [VER.001] [SGDK 211] [GEN] [LAB]

## Semantica obrigatoria

Separar sempre:

- `rom_asset_cost`: asset em ROM e compressao (`FAST`, `BEST`, `NONE`)
- `vram_resident_set`: tiles/fontes/sprites/mapas simultaneamente residentes na cena
- `load_time_dma_cost`: uploads de boot, loading ou troca de cena
- `per_frame_dma_cost`: uploads por VBlank durante gameplay
- `active_animation_window`: frames/ciclos realmente residentes agora
- `scene_local_scope`: assets permitidos na cena atual
- `scanline_sprite_pressure`: sprites totais e pior scanline

## VRAM residente por cena

- `APP_SCENE_BRANDING`: BG ativo parte de tile `16` e usa no pior fundo 25 tiles unicos; logo ativo parte de `176` e usa no pior slot 141 tiles; `PRESENTS` parte de `536` e usa 39 tiles; fonte bitmap ativa parte de `656` e usa no pior caso 59 tiles.
- Apenas um fundo, um logo e uma fonte bitmap ficam ativos por slot.
- Reserva padrao do sprite engine: `420` tiles em `1020..1439`; fonte SGDK em `1440..1535`.
- `res_graph_report.json`: `21/21` declaracoes, `0` overlap, `vram_residency_status=ok`.
- O grafo sequencial estima os dez recursos IMAGE em `16..664`; o runtime scene-local usa destinos fixos ainda mais conservadores.

## ROM e compressao

- Logos e FX sprites: `BEST`.
- Fontes bitmap: `NONE`, para o renderer selecionar glyphs via tilemap sem alocacao dinamica.
- Audio XGM2: `30.691` bytes estimados, `0,73%` do budget de ROM de 4096 KB.
- Observacao: compressao reduz ROM/load, nao o custo final em VRAM quando descompactado.

## DMA de preload/loading

- Entrada de cada slot: fundo, logo, fonte aplicavel e paletas carregados durante a troca estrutural da tela.
- O preload e scene-local; a origem canonica dos 16 assets v3 e o builder deterministico `tools/image-tools/build_branding_v3_assets.py`.

## DMA por frame no pior caso

- Engine, frames locais `2..29`: tabela HScroll de `224` words (`448` bytes) enfileirada com `DMA_QUEUE`.
- Projeto, frames locais `26..37`: tabela HScroll de `224` words (`448` bytes) enfileirada com `DMA_QUEUE`.
- Paleta usa escritas CRAM pontuais; nao ha streaming de tiles por frame.

## Animacao, streaming e sprites

- `active_animation_window`: spark 4 frames, monograma 12, cursor 3, escudo 4, glow 1 e debris 4.
- `scene_local_scope`: engine usa ate 12 sparks + glow; autor usa monograma + cursor + glow; projeto usa escudo + ate 8 debris.
- `streaming/fallback`: `scene_local_preload`; reduzir particulas antes de aumentar reserva de sprites.
- `scanline_sprite_pressure`: picos de design 13/3/9 sprites por slot, todos abaixo de 20 por scanline se sobrepostos; a medicao SAT continua estimada porque o probe MDRT atual registra `0`.
- Performance BlastEm final da cena: 151 frames observados, CPU medio/p95/max `6%`, jitter max `0`, `0` frames acima do threshold.

## Parecer

- eixo tecnico da cena 0: `cabe`
- eixo perceptivo: `perceptivel com recuo`
- recuo/gate restante: captura final dedicada da Engine, baseline comparativo e VDP dump antes de qualquer promocao AAA

## Politica

- nao contar o mundo inteiro como residente se houver scene-local loading ou streaming declarado
- nao contar asset `BEST` como menor em VRAM; medir tiles descompactados
- nao trocar tiles inteiros por frame sem necessidade
- preferir paleta e scroll para animacao de ambiente
- redraw de tilemap completo so em troca de estado ou mudanca estrutural
