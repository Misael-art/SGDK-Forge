# Inventário preliminar do tile kit — Vegetable Valley

Status: planejamento sem conversão. A cena-dourada é referência semântica; os números abaixo são envelope preliminar e não substituem `rescomp`.

| Kit | Surface | Peças repetíveis | Peças únicas/âncoras | Regra de reuso |
|---|---|---|---|---|
| céu | BG_B | duas bandas discretas, nuvem curta, nuvem larga | recorte assimétrico do horizonte | repetir em blocos largos; sem gradiente suave |
| montanhas | BG_B | pico esquerdo/direito, sela, sombra fria | uma quebra de horizonte | flip permitido em silhueta não direcional |
| hills/orchard | BG_B | arcos de hill, blob de copa, tronco | ritmo de cultivo próximo ao foco | 2–4 repetições e uma quebra assimétrica |
| terreno | BG_A | grass cap reto, cap de canto, soil fill, strata | transição do gap e ledge ends | prioridade para a borda de colisão |
| ledge/gap | BG_A | underside, corner, soil fill | topologia do gap | não deduplicar de modo a apagar a leitura física |
| foreground | priority/sprite graft | leaf cluster small/wide, grass tuft | janela de clareza do herói e gap | esparso; nunca cobrir pés/colisão |
| herói | sprite engine | janela ativa futura | pose-chave e silhueta | sem flip de rosto/FX; depende de model gate |
| inimigo | sprite engine | archetype active window | pose de ameaça | rampa compatível medida, não assumir PAL2 |
| pickups | sprite engine | pickup single | pickup de leitura | um por evento visível no slice |
| inhale FX | sprite engine | wind cluster A/B, leaf FX | eixo causal de sucção | separado do herói; reduzir antes de estourar scanline |

## Deduplicação e ritmo

Deduplicar céu, preenchimentos de solo, arcos de hills e clusters fora da janela focal. Preservar a quebra de horizonte, a transição do gap, três variações de grass cap e pequenas irregularidades do orchard. Flips só entram após prova de seam e não podem ser usados em rosto, inimigo direcional ou FX direcional.

## Envelope preliminar

- BG_B: 120–180 tiles únicos.
- BG_A: 140–220 tiles únicos.
- Foreground: 20–40 tiles únicos.
- Janela ativa de sprites: 50–80 tiles únicos.
- Total local candidato: 330–520 tiles únicos, ainda não medido por `rescomp`.
- Payload de tiles estimado: 10.560–16.640 bytes, sem mapas, paletas e empacotamento SGDK.
- Residency agregada do projeto, todos os assets simultâneos: 853/1740 tiles úteis (49%), referência de pior caso e não prova da cena nativa.

## Âncoras 320×224

Herói `(96,170)`, inimigo `(228,170)`, eixo de inalação `x=112..212,y=150`, ledge em torno de `y=135`, foreground `y=190..224`, HUD seguro `y=0..24`. O collision top é o topo da grama, não a sombra desenhada.

## Próximo teste obrigatório

Depois do gate do model sheet e da autorização nativa: autorar os kits por camada, medir tiles brutos/únicos com `rescomp`, gerar `scene_tilemap_conversion_report` e `per_tile_palette_conflict_report`, medir residency/DMA e só então testar a janela em BlastEm.
