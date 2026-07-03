# Prompt 03 — Cais de Porto Bravo (dock_scene_kit modular do CAIS_01)

Salvar em: `data/source_art/concept/cais_world_modular/`

Escopo: `concept_art` para `scene_kit`. A saída deste prompt NÃO é panorama
final, NÃO é tilemap final e NÃO vai direto para `res/`.

## Correção curatorial

O pacote anterior pediu 3 painéis 16:9 de arena + 1 BG_B. Esses painéis ficam
apenas como `mood_reference_only` / `landmark_reference_only`. Eles ajudam a
lembrar paleta, atmosfera, cais ao entardecer, barco lacrado e beirada, mas
não resolvem o problema real: construir uma fase jogável com autoria, câmera,
streaming, repetição controlada, ritmo e gameplay.

Para o CAIS_01, o modelo de imagem deve gerar peças. O agente canônico monta a
fase.

Leia antes de usar:

- `doc/contracts/level_art_assembly_contract.json`
- `doc/contracts/level_blueprint.json`
- `doc/contracts/tilemap_streaming_contract.json`
- `doc/11-gdd.md`
- `doc/13-spec-cenas.md`

## Princípio obrigatório

Peça `asset boards` modulares, ortogonais ou com perspectiva lateral coerente,
com fundo simples e separação clara por objeto. Não peça uma cena pronta.

O resultado deve permitir que o agente monte:

- um mundo total `1344x224`;
- uma janela residente/câmera `320x224`;
- três arenas com calm/pressure/payoff;
- BG_B em parallax;
- BG_A streamado por colunas;
- foreground/oclusão com prioridade visual;
- ecology loops pequenos e baratos;
- landmarks únicos sem roubar leitura dos sprites.

## Prompt A — dock floor and edge tile kit

```
Modular 16-bit side-scrolling beat-em-up dock tileset concept sheet, 1990s
Brazilian coastal pier at late golden-hour sunset, designed as separate
reusable parts for a Mega Drive / Genesis level. Orthographic side-view game
asset board, no full background scene.

Create isolated modular wooden pier components: straight boardwalk floor
segments, cracked planks, missing-plank holes, pier edge pieces, dark water
edge strips, foam lapping against the edge, corner pieces, transition pieces,
short stair/step pieces, damaged boards, rope-tied posts. Keep the gameplay
walking lane flat and readable. Use warm sand-orange light #E8A05C, deep
purple-cool shadows #5C2E4A, teal water #3A6B7A, pale foam #F2F2E0 and warm
highlight #FFD98A. Flat cel shapes, hard shadow clusters, no gradients, no
airbrush, no characters, no text, no logos. Arrange pieces in a clean catalog
grid with generous spacing and plain neutral background.
```

Aceite:

- [ ] cada peça pode virar tile/metatile ou overlay separado;
- [ ] beirada de água lê como hazard/ring-out sem texto;
- [ ] chão jogável é plano e não compete com sprites;
- [ ] há variação sem virar ruído de tiles únicos.

## Prompt B — dock props and obstruction kit

```
Modular prop sheet for a 16-bit Brazilian coastal dock beat-em-up level,
separate reusable objects on a neutral background, not a finished scene.

Create isolated props: stacked wooden crates, fish crates, ice boxes with fish,
coiled ropes, hanging ropes, torn fishing nets, rolled nets, small market
stall frame, scale booth parts, rusty lamp posts, lanterns, barrels, sacks,
wooden pallets, mooring bollards, small warning markers without readable text,
broken planks, cargo hooks, anchor chain, scattered seafood market objects.
Use bold angular cel shading, limited color families, clean silhouettes,
hard-edged clusters, late sunset warm/cool palette. No characters, no readable
text, no real brands, no full background, no perspective painting.
```

Aceite:

- [ ] objetos grandes têm versões pequenas/médias para composição;
- [ ] pelo menos 8 objetos servem como landmark ou narrativa ambiental;
- [ ] nenhum objeto exige texto para comunicar função;
- [ ] caixas/cordas/redes podem ser rearranjadas pelo agente.

## Prompt C — large landmark plates

```
Large modular landmark asset board for a side-scrolling 16-bit dock level,
not a panorama. Separate large setpiece plates with transparent-friendly
silhouettes and side-view readability.

Create: a moored fishing boat sealed by visual bands/ropes (no readable text),
a small scale booth, a distant crane silhouette, a dock entrance arch made of
wood and rope, a final pier lantern/farolete, a damaged market stall skeleton,
a large fishing net wall, a cargo stack silhouette. Each landmark must be
isolated, readable at 320x224, and designed to be placed by a level designer
inside three arenas. Flat cel rendering, hard shadows, few color families,
Brazilian coastal 1990s mood, no characters, no logos, no text.
```

Aceite:

- [ ] um landmark claro para arena 1, arena 2 e arena 3;
- [ ] boat/booth/crane/farolete podem ser separados de BG_A/BG_B;
- [ ] formas funcionam como guia de golden path sem setas;
- [ ] nenhum landmark congela a fase inteira como ilustração pronta.

## Prompt D — BG_B parallax layers

```
Seamless modular parallax background layer kit for a Mega Drive / Genesis
side-scrolling dock stage. Do not create a full gameplay foreground.

Generate separate horizontal strips/layers: sunset sky color bands,
thin backlit clouds, distant harbor silhouette, far cranes, open teal sea
with simple wave rows, far boats as separate silhouettes, mid-distance boats
that can drift slowly, tiny gull silhouettes in 2-3 simple poses. Left-right
loopable, flat cel shapes, stepped color bands, no gradients, no characters,
no text, no logos. Design for line-scroll/parallax: clean horizontal bands and
low detail density in the distance.
```

Aceite:

- [ ] camadas separáveis por scroll ratio: 0.125x, 0.25x, 0.5x;
- [ ] mar/céu competem menos que BG_A e sprites;
- [ ] navios e gaivotas podem virar ecology loops baratos;
- [ ] bordas esquerda/direita não denunciam seam.

## Prompt E — foreground and occlusion kit

```
Foreground occlusion asset board for a 16-bit dock beat-em-up, separate
front-layer objects only, no complete scene.

Create isolated foreground elements: large front pier pilings, closer rope
loops, thick mooring posts, hanging net strips, broken railing fragments,
water splash foreground shapes, dark underside beams, diagonal ropes. These
elements must frame the action without covering the gameplay lane. Use lower
detail than hero sprites, strong silhouettes, limited palette, hard-edge cel
shadows, no gradients, no text, no characters.
```

Aceite:

- [ ] foreground abraça a cena sem virar ruído;
- [ ] elementos podem receber priority split/sprite graft/fusão honesta;
- [ ] nenhum elemento cobre HUD, hitbox ou leitura de ring-out;
- [ ] pilastras de frente e de trás têm papéis visuais distintos.

## Prompt F — background ecology loops

```
Small animation concept sheet for living background ecology in a 16-bit
Brazilian dock beat-em-up. Create tiny loopable elements, each separated and
clearly labeled visually by position, but without readable text.

Include: boat bobbing cycle 3 frames, far boat drift silhouette 2 frames,
gull flap 3 frames, lantern flicker 3 frames, foam loop 4 frames, hanging
cloth flap 3 frames, fishing net sway 3 frames. Use minimal frames, strong
silhouettes, limited palette, hard pixel-friendly shapes, no blur, no alpha
blend, no characters.
```

Aceite:

- [ ] cada loop tem função narrativa/gameplay ou atmosfera controlada;
- [ ] espuma reforça ring-out, não apenas decoração;
- [ ] loops cabem como tile animation ou sprite graft após budget;
- [ ] nada depende de alpha blending, blur ou subpixel.

## Critérios globais de aceite

- [ ] O pacote gera `scene_kit`, não panorama pronto.
- [ ] O agente consegue montar o CAIS_01 sem pedir nova pintura completa.
- [ ] Cada peça tem papel: gameplay, landmark, narrativa, profundidade ou ecologia.
- [ ] BG_A/BG_B/foreground possuem densidade e contraste diferentes.
- [ ] A beirada de água é um sinal de mecânica, não só espuma bonita.
- [ ] Não há texto legível obrigatório; narrativa deve vir de forma, objeto e disposição.
- [ ] Nenhuma saída é `final_asset`; tudo entra como `source_candidate`.

## Saída esperada após receber as imagens

O próximo agente deve registrar cada asset no `premium_source_manifest` e então
produzir:

- `dock_scene_kit_inventory`;
- `object_role_map`;
- `world_layout_board` 1344x224;
- `object_placement_map`;
- `parallax_layer_contract`;
- `background_ecology_card`;
- `scene_tilemap_conversion_report` preliminar;
- contact sheet 320x224 para ratificação humana.
