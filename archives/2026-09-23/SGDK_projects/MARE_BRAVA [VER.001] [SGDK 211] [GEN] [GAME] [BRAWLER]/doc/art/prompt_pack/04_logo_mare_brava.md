# Prompt 04 — Logo MARE BRAVA source candidates

Salvar cada asset em:

- `data/source_art/concept/logo_lettering_studies/`
- `data/source_art/concept/logo_title_context_study/`
- `data/source_art/concept/logo_monochrome_thumbnail_test/`

Escopo: `concept_art` / `source_candidate`. O master vetorial/bitmap final é
trabalho autoral. Contratos:

- `doc/art/brand_identity_manifest.json`
- `doc/art/authorial_line_style_contract.json`

Texto exato permitido no logo: `MARE BRAVA` (sem acento na imagem gerada).

## Traco autoral do logo

O lettering deve parecer talhado por madeira molhada e impacto de onda: letras
grossas, angulares, com cortes de espuma; a barra do A final vira crista de
onda. Não usar fonte genérica, bevel cromado, logo cyberpunk, glass UI ou trade
dress de franquia conhecida.

## Prompt A — lettering studies

```
Use case: logo-brand
Asset type: logo lettering source candidate, not final runtime logo
Primary request: video game logo design studies for the exact title "MARE
BRAVA", arranged as 4 different heavy horizontal treatments on one sheet.

Authorial logo line contract: thick angular block letters that feel carved
from dock wood and struck by ocean foam; hard chipped cuts, wedge-shaped
negative spaces, bold silhouette. The crossbar of the final letter A becomes a
cresting ocean wave with readable foam. The wave mark must improve identity
without hurting the word read.

Color palette: two-color and three-color versions only: off-white #F2F2E0,
deep dark #111122, accent red #CC2244 or sea green #3A6B7A.

Style/medium: flat hard-edged arcade title lettering, no gradients, no bevel,
no chrome, no photorealism, no soft glow.

Constraints: exact text only "MARE BRAVA"; no extra words, no logos, no
watermark, no franchise trade dress, must read as a tiny thumbnail and in pure
single-color silhouette.
```

## Prompt B — title context study

```
Use case: stylized-concept
Asset type: title context source candidate, not final title screen
Primary request: the chosen heavy angular MARE BRAVA wave logo placed over a
flat cel-shaded sunset sea horizon, simulating a 16-bit title screen at
320x224 proportions.

Composition: logo occupies upper 40%, plain PRESS START spacing reserved below
but do not render extra text unless necessary; background is simple horizontal
bands of warm sunset sky #E8A05C and teal sea #3A6B7A.

Authorial line contract: logo keeps chipped dock-wood/angular wave cuts; sea
foam shapes echo the final A crossbar. Flat colors only.

Constraints: exact logo text "MARE BRAVA", no gradients, no bevel, no chrome,
no glow, no extra slogans, no known franchise trade dress.
```

## Prompt C — monochrome thumbnail test

```
Use case: logo-brand
Asset type: monochrome readability test source candidate
Primary request: monochrome thumbnail test sheet for the exact title "MARE
BRAVA": pure single-color fills only, black on white and white on black,
repeated at large, medium and tiny thumbnail sizes.

Authorial line contract: final letter A has a readable wave-crest crossbar;
letter cuts stay angular and heavy; no detail that disappears at 96px width.

Constraints: no extra text, no bevel, no chrome, no gradient, no glow, no
franchise trade dress.
```

## Critérios de aceite

- [ ] Silhueta: preenchido em 1 cor, ainda se lê `MARE BRAVA`.
- [ ] Miniatura: reduzido a ~96px de largura, ainda legível.
- [ ] Monocromático: não depende de gradiente/cor para funcionar.
- [ ] A onda na barra do A lê como onda, não mancha.
- [ ] O logo parece MARE_BRAVA, não fonte arcade genérica.
- [ ] Peso do título ≥ 85% do lockup.
