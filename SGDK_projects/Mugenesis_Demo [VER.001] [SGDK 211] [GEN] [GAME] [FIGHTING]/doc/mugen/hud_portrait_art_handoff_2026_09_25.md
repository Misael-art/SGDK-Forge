# Tarefa delimitada para artista com geracao de imagem: retrato HUD 32x32

Leia `doc/mugen/hud_stage_review_2026_09_25.md` e as skills canonicas
`art-translation-to-vdp`, `character-design`, `megadrive-pixel-strict-rules`,
`visual-excellence-standards`. Fonte autoral permitida para uso local:
`rascunho/inputs/hud_review_2026_09_25/portrait_source.png` (Ken 9000,0 do
pacote original). Referencias visuais do usuario, com hashes, na mesma pasta.

Tarefa: redesenhar **somente** o retrato e a moldura, em 32x32 pixels nativos,
preservando sobrancelhas, olhos, sorriso e massa do cabelo da fonte. Canto
externo com indice 0 transparente, sem matte. Moldura discreta de 1 px com
cantos interrompidos, separacao clara do rosto e contraste 1x no fundo claro
e escuro. Dithering controlado so onde suaviza material amplo; evitar ruido de
1 px na face. O candidato tecnico corrigido esta em
`rascunho/processado/hud_review_2026_09_25/portrait_palette_fixed.png`;
ele repara a transparencia, nao e uma aprovacao artistica.

Paleta fixa do corpo em todas as 12 variantes; nao ocupar a roupa (slots
7,9,10,12,13,14) nem o slot 6 de FX:

| indice | palavra VDP | RGB de autoria no PNG | uso sugerido |
|---:|---:|---|---|
| 0 | transparente | marcador | exterior |
| 1 | `0x68C` | 204,136,102 | pele |
| 2 | `0x0AE` | 238,170,0 | ouro medio |
| 3 | `0x6CE` | 238,204,102 | luz do cabelo |
| 4 | `0x8CE` | 238,204,136 | pele clara |
| 5 | `0xAEE` | 238,238,170 | brilho pequeno |
| 8 | `0x006` | 102,0,0 | recorte do gi |
| 11 | `0x468` | 136,102,68 | sombra quente |
| 15 | `0x000` | 0,0,0 | contorno/olhos |

Os valores RGB sao da grade de autoria `0x22` de
`tools/sgdk_wrapper/forge_art/vdp_color.py`, nao curva CRT. O indice 0 usa
marcador magenta `238,0,238` e transparencia tRNS; nao e visivel.
Cada tile 8x8 deve consumir so indice 0 e os slots acima. Nao remapear a
paleta inteira do lutador para melhorar apenas a miniatura: isso alteraria
corpo, projeteis e flash. P2 usa a mesma arte espelhada; verificar ambos.

Use geracao de imagem apenas como ideia. A candidata anterior
`portrait_frame_concept.png` saiu 1254x1254 com mais de 100 mil cores RGBA;
nao e sprite. A versao final precisa de trabalho em canvas 32x32 indexado;
nao reduzir automaticamente a ideia e chamar de arte nativa.

Entregue arquivo fonte separado em staging, PNG indexado com indice 0
transparente, SHA-256, contato 1x/zoom nearest, vistas sobre fundo claro e
escuro, relatorio de slots/tiles e comparacao com 9000,0 e captura do BlastEm.
So depois de revisao visual por hash atualizar `res/mugen/ken/portrait.png` e
seu registro de proveniencia. Se nenhuma versao supera a fonte corrigida sem
perder expressao, entregue `needs_review` com o motivo; nao troque pixels so
para dar por concluido.
