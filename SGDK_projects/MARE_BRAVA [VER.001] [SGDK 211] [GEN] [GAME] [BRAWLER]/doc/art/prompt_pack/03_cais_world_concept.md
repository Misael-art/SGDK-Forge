# Prompt 03 — Cais de Porto Bravo (mundo do CAIS_01)

Salvar em: `data/source_art/concept/cais_world/`
Escopo: concept_art (referência de tileset/composição; a conversão real usa
tiles 8x8 com dedup — o concept guia, não vira tilemap direto).

O BG_A final tem 1344x224 (proporção 6:1). Nenhum modelo gera bem nessa
proporção — gere em 3 painéis 16:9 (um por arena) + 1 painel do fundo (BG_B).

## Prompt A — arena 1 (entrada do cais)

```
Side-scrolling beat-em-up stage concept, 1990s Brazilian coastal dock at
late golden-hour sunset: weathered wooden pier boardwalk as the walkable
ground plane (bottom third of frame, flat and readable for gameplay),
stacked wooden crates stamped with a union crest, coiled ropes, a rusty
lamp post, torn fishing nets hanging. Background layer: green-teal sea
#3A6B7A with white foam, distant harbor crane in warm backlight silhouette.
Warm sand-orange key light #E8A05C, deep purple-cool shadows #5C2E4A,
highlight #FFD98A. Flat cel rendering with hard shadow shapes (no gradients,
no airbrush), bold shape language, strong horizontal composition, colors
grouped in few flat families suitable for 16-color palettes, no characters,
no text, 16:9.
```

## Prompt B — arena 2 (meio do cais, barco atracado)

Mesmo prompt, trocando o trecho de cenário por:
```
... a moored fishing boat sealed with union tape at the middle ground,
fish crates and a scale booth, market stall skeleton ...
```

## Prompt C — arena 3 (beirada exposta — zona de ring-out)

```
... the pier edge fully exposed along the bottom of the walkable plane:
dark living water with animated white foam licking the wooden edge,
missing planks, a lit lantern post, the sunset sun low on the horizon.
The water edge must read INSTANTLY as a special danger zone: strongest
value contrast of the whole stage between warm boardwalk and dark sea ...
```
(este painel é o palco do Empurrão de Maré — o contraste beirada/água é
requisito de gameplay, não estética)

## Prompt D — BG_B (fundo em loop: mar e céu)

```
Seamless horizontally-tileable background strip for a 16-bit game: sunset
sky with warm bands #FFD98A to #E8A05C, thin backlit clouds, calm open sea
#3A6B7A with simple white wave crests in flat rows (parallax-friendly
horizontal bands), distant dark harbor silhouette line. Flat cel shapes,
no gradients (use stepped color bands), loopable left-right edges, no
characters, no text, wide 21:9.
```

## Critérios de aceite

- [ ] Chão jogável plano e legível no terço inferior (faixa de luta)
- [ ] Beirada d'água = maior contraste de valor do painel (arena 3)
- [ ] Famílias de cor contáveis (dá para imaginar em 16 cores por plano)
- [ ] Bandas horizontais no mar/céu (amigável a line-scroll)
- [ ] Landmark único por arena (guindaste / barco / farolete) para golden path
- [ ] Zero texto, zero personagens, zero marca real
