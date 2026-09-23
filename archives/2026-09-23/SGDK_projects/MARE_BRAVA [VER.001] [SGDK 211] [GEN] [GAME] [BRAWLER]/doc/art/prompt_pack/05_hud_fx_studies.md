# Prompt 05 — HUD e FX source candidates

Salvar cada asset em:

- `data/source_art/concept/hud_frame_study/`
- `data/source_art/concept/hud_health_bar_chip_damage_study/`
- `data/source_art/concept/hud_digit_glyph_seed/`
- `data/source_art/concept/taina_hud_portrait_seed/`
- `data/source_art/concept/fx_small_hitspark_3f/`
- `data/source_art/concept/fx_medium_hitburst_3f/`
- `data/source_art/concept/fx_ringout_splash_3f/`
- `data/source_art/concept/fx_waterline_foam_loop_seed/`

Escopo: `concept_art` / `source_candidate`. HUD final é pixel-perfect em grid
8x8 no WINDOW; estes estudos definem forma, hierarquia e personalidade visual,
não pixels finais.

Leia junto:

- `doc/11-gdd.md#ui-pixel-surface-seed`
- `doc/art/authorial_line_style_contract.json`

## Traco autoral HUD/FX

HUD deve parecer parte de Porto Bravo: moldura grossa, cortes de madeira/corda
simplificados, espuma/teal como sinal de maré, sem glass UI, sem overlay
corporativo, sem retângulo debug. FX devem comunicar gameplay: impacto,
knockback, ring-out, peso na água.

## Prompt A — HUD frame study

```
Use case: ui-mockup
Asset type: HUD frame source candidate, not final pixel HUD
Primary request: 16-bit belt-scroll brawler HUD design study for the top of a
320x224 screen.

Layout: single horizontal top strip, small square character portrait frame at
left for future 16x16 portrait, chunky segmented health bar, visible chip
damage trailing segment, six-digit score counter right-aligned.

Authorial line contract: heavy dock-world frame with hard angular cuts,
simplified rope/wood notch accents, flat dark strip #111122, off-white
#F2F2E0, danger red #CC2244, teal #3A6B7A. Forms must feel carved and physical,
not generic modern UI.

Constraints: placeholder digits "000000" only, no extra text, no gradients,
no glass, no bevel, no glow, no subpixel-smooth UI, hard edges, grid-friendly
8x8 shapes.
```

## Prompt B — health bar chip damage study

```
Use case: ui-mockup
Asset type: health bar source candidate, not final pixel HUD
Primary request: focused 16-bit HUD health bar study for a 320x224 brawler,
showing 4 health states on one sheet.

Design: chunky 40x8 bar, delayed chip-damage trailing segment, two or three
flat colors, clear damage state, dark background #111122, off-white #F2F2E0,
red #CC2244, teal #3A6B7A.

Authorial line contract: hard dock-carved frame edges, small wave/foam notch
motif, bold readable damage buffer. No generic rectangle.

Constraints: no labels, no gradients, no glass, no bevel, no glow.
```

## Prompt C — digit glyph seed

```
Use case: ui-mockup
Asset type: numeric glyph source candidate
Primary request: six-digit score glyph seed for a 16-bit arcade HUD, showing
placeholder digits "000000" and numeric glyph fragments only.

Authorial line contract: blocky but slightly chipped numeric forms echoing the
MARE BRAVA logo cuts; readable in 8x8 grid; flat off-white on dark background.

Constraints: no alphabet text, no modern UI effect, no gradient, no bevel, no
glow.
```

## Prompt D — TAÍNA HUD portrait seed

```
Use case: stylized-concept
Asset type: tiny HUD portrait source candidate
Primary request: tiny portrait seed for TAÍNA designed to compress to 16x16
pixels: front-facing determined face.

Authorial face grammar: strong brow, tired focused eyes, wedge nose bridge,
compact jaw, short tied curly hair mass, brown skin, burnt-orange accent near
the shoulder. Readable as TAÍNA, not generic anime portrait.

Style/medium: hard cel shadows, 2-3 tones, high contrast, neutral background.

Constraints: no full body, no text, no glossy modern eyes, no painterly blur,
no generic fighter portrait.
```

## Prompt E — small hitspark 3f

```
Use case: stylized-concept
Asset type: FX source candidate
Primary request: small geometric hit spark concept sheet, 3 separated frames,
readable in a single gameplay frame.

Design: sharp 4-point impact shape bursting into hard shards, off-white
#F2F2E0 core with burnt orange #FF5533 edge and dark cut lines.

Authorial FX contract: angular wedge shards that imply dry hand-to-hand impact,
not magic sparkle or confetti.

Constraints: no blur, no glow, no gradient, no text, no background scene.
```

## Prompt F — medium hitburst 3f

```
Use case: stylized-concept
Asset type: FX source candidate
Primary request: medium hit burst concept sheet, 3 separated frames for a
heavy brawler impact.

Design: angular starburst, blocky shock shards, readable knockback direction,
2-3 colors, hard silhouettes.

Authorial FX contract: impact should feel like a dry percussive strike from
the "peso de maré" combat promise.

Constraints: no motion blur, no soft glow, no text.
```

## Prompt G — ring-out splash 3f

```
Use case: stylized-concept
Asset type: FX source candidate
Primary request: large water splash concept sheet for a dockside ring-out
knockout, 3 separated frames.

Frames: 1) heavy body hits water and foam rises, 2) apex wide splash crown,
3) falling foam and water sheets.

Authorial FX contract: teal water #3A6B7A and pale foam #F2F2E0 cut into bold
hard shapes; splash must feel like weight falling into dock water, not an
ornamental fountain.

Constraints: no gradients, no blur, no soft glow, no text.
```

## Prompt H — waterline foam loop seed

```
Use case: stylized-concept
Asset type: ecology/hazard loop source candidate
Primary request: waterline foam loop seed for a dock edge hazard, 4 separated
frames, thin horizontal strip shapes that can later become tile animation.

Authorial line contract: foam shapes are bold white cutouts over dark teal
water, with small angular breaks echoing the logo wave. Must communicate
ring-out edge before combat reaches it.

Constraints: low detail, loopable, no gradients, no blur, no text.
```

## Critérios de aceite

- [ ] HUD não parece debug, template corporativo ou glass UI.
- [ ] Health bar tem buffer de dano visualmente distinto.
- [ ] Retrato preserva rosto autoral da TAÍNA.
- [ ] Hitsparks comunicam impacto físico, não magia genérica.
- [ ] Splash tem subida/ápice/queda e parece peso caindo na água.
- [ ] Waterline comunica hazard/ring-out sem texto.
