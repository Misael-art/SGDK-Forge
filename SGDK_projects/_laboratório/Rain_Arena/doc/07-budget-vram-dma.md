# 07 - Budget VRAM e DMA — Rain_Arena

## VRAM

- banco procedural base: 16 tiles de sistema
- tiles via rescomp: 757 tiles (`bg_sky` = 474, `bg_temple` = 283)
- reserva dinamica do sprite engine nesta cena: 80 tiles (`40` gotas x `maxNumTile = 2`)
- total operacional validado do slice: 853 tiles
- pressao de sprite em gameplay: 40 entradas SAT

## DMA por frame

Estimativa de pico nas cenas:

- chuva em queda: 800 words/frame (`160` words de SAT + `640` words de upload de tiles de sprite)
- hit flash com splash: 1488 words/frame (`160` words de SAT + `1280` words de upload de tiles de sprite + `48` words de paleta)

## Politica

- manter a cena abaixo de 1600 words/frame em runtime
- nao trocar tiles inteiros por frame sem necessidade
- preferir paleta e scroll para animacao de ambiente
- redraw de tilemap completo so em troca de estado ou mudanca estrutural

