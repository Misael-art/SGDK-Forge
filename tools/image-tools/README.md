# Image Tools

Ferramentas de tratamento de imagem do workspace MegaDrive_DEV: correcoes manuais de PNG, **pipeline generico** de redimensionamento e indexacao de lotes (Mega Drive / SGDK) e automacao canonica do lote do projeto Pequeno Principe.

## Conteudo

| Ferramenta | Uso |
|------------|-----|
| `batch_resize_index.py` | **Generico:** redimensiona PNGs e gera BMP indexado conforme spec JSON. Use para qualquer projeto com lote em production/ + indexed/ + boards/. |
| `analyze_aesthetic.py` | **Juiz estetico:** mede conformidade visual AAA orientada a hardware (paleta, tiles 8x8, silhueta, contraste entre planos, reuse). |
| `analyze_translation_case.py` | **Curadoria da skill:** compara `basic` vs `elite` para um caso da skill `art-translation-to-vdp` e gera laudo agregado de acuracia. |
| `infer_source_structure.py` | **IR estrutural minima:** observa o `source`, gera `observed_ir.json` e `derived_structure_ir.json` com confianca por dimensao e conflitos estruturais. |
| `export_source_structure.py` | **Exportador estrutural:** consome `derived_structure_ir.json`, roda gate engine-aware + recomposicao visual e exporta `final` ou `provisional`. |
| `analyze_source_semantics.py` | **Alfabetizacao de source:** valida parsing semantico supervisionado de pranchas-fonte, gera `semantic_parse_report` e painéis humanos para treino da skill. |
| `reference_profiles.json` | Perfis de benchmark visual (Streets of Rage 3, Monster World IV, Earthworm Jim, Shinobi III, Sonic 3K). |
| `aesthetic_thresholds.json` | Thresholds por papel do asset (`sprite`, `bg_a`, `bg_b`, `hud`) para o juiz estetico. |
| `specs/pequeno_principe_v2.json` | Spec do lote Pequeno Principe (production + boards). Modelo para novos specs. |
| `specs/art_translation_case.template.json` | Template de manifesto para curadoria da skill `art-translation-to-vdp`. |
| `specs/source_semantic_case.template.json` | Template para casos supervisionados de parsing semantico de `source`. |
| `resize_and_index_pequeno_principe_batch.py` | Wrapper que chama `batch_resize_index.py` com o spec do PP e batch root default. |
| `validate_pequeno_principe_asset_batch.ps1` | Valida dimensoes, cores e contrapartes indexadas do lote PP. |
| `promote_pequeno_principe_asset_batch.ps1` | Promove lote validado para `res/` do projeto PP (com backup). |
| `fix_png_transparency_final.py` | Corrige transparencia/paleta em PNG para uso SGDK. |

## Pipeline generico (qualquer projeto)

1. **Definir um spec JSON** em `specs/` (ou outro caminho), no formato:
   - `production`: lista de `{ "name", "png_rel", "w", "h", "bmp_rel", "bmp_w", "bmp_h", "transparency" }`.
   - `boards`: lista de `{ "rel", "w", "h" }` (opcional).
2. **Colocar os PNGs** no diretorio do lote em `production/` (e `boards/` se houver).
3. **Rodar:**  
   `python tools/image-tools/batch_resize_index.py --spec specs/meu_projeto.json --batch-root tmp/imagegen/inbox/meu_projeto`
4. **Validar** com o script de validacao do seu projeto (ex.: PowerShell que verifica dimensoes e indexed/).

Exemplo de spec minimo: ver `specs/pequeno_principe_v2.json`.

## Juiz estetico

Para medir conformidade visual AAA com foco em hardware:

`python tools/image-tools/analyze_aesthetic.py --asset <png> --role sprite --reference-profile generic-megadrive-elite --output out.json`

Campos principais avaliados:
- `palette_efficiency`
- `tile_efficiency`
- `detail_density_8x8`
- `dithering_density`
- `silhouette_readability`
- `layer_separation`
- `reuse_opportunity`
- `visual_excellence_score`

## Curadoria da skill `art-translation-to-vdp`

Para comparar uma traducao `basic` com uma `elite` de um mesmo caso:

`python tools/image-tools/analyze_translation_case.py --manifest tools/image-tools/specs/art_translation_case.template.json --output out.json`

O manifesto do caso declara:
- imagem-fonte
- alvo de traducao
- contrato da alma visual
- unidades de analise por variante
- `paired_bg` ou `paired_bg_layers`
- delta minimo esperado entre `basic` e `elite`

O laudo final agrega:
- score por variante
- delta `elite_minus_basic`
- status comparativo
- `hardware_budget_review` com sinais de `compare_flat`, `SPR_initEx` e risco de conversao de imagem inteira
- evidence block quando existir `out/captures/` no projeto

## Alfabetizacao semantica de `source`

Para treinar a skill a entender pranchas-fonte antes da traducao:

`python tools/image-tools/analyze_source_semantics.py --manifest tools/image-tools/specs/source_semantic_case.template.json --output out/source_semantics.json`

Para inferencia operacional a partir de um `source` real:

1. `python tools/image-tools/infer_source_structure.py --source <png> --output-dir <dir> --layout-hint auto`
2. `python tools/image-tools/export_source_structure.py --ir <dir>/derived_structure_ir.json --output-dir <dir>`

Esse fluxo produz:

- `observed_ir.json`
- `derived_structure_ir.json`
- `structural_metadata.json`
- `validation_report.json`
- `semantic_parse_report.json`
- `human_semantic_panel.png`
- `drop_regions_panel.png`
- `inferred_composition_panel.png`
- `recomposed_scene.png` quando houver referencia supervisionada da cena

Regras novas do pipeline:

- `observed_ir` guarda apenas fatos observaveis; `derived_structure_ir` guarda hipoteses estruturais minimas
- cada regiao derivada precisa de `confidence_bbox`, `confidence_classification`, `confidence_composition` e `confidence_engine_affordance`
- o gate final combina coerencia estrutural, conflitos globais, `engine_affordance` e verificador visual de recomposicao
- a exportacao pode sair em `extracts/final` ou `extracts/provisional`
- `provisional` nunca alimenta automaticamente `basic`/`elite`
- o laudo agora precisa expor `delivery_findings` antes da entrega, incluindo:
  - risco de `frame spill` entre bandas de animacao
  - candidatos a `internal key-hole alpha` em sprites
  - `drop regions` grandes preservadas para inspecao
  - nota explicita quando `scene layers` forem PNGs RGBA em `shared_canvas` de review

Artefatos adicionais de review:

- `extracts/<mode>/drops/` para regioes descartadas grandes ou pedagogicamente relevantes
- `extracts/<mode>/layer_previews/` com `tight preview` de layers de cena exportadas em canvas comum

Ele tambem suporta:

- `auxiliary_regions` para paleta, nomes e dados tecnicos
- classes estruturais como `scene_plane_sky`, `scene_plane_architecture`, `scene_plane_ground`
- `object_animation_sequence`, `overlay_cluster` e `corrupted_region`

Corpus canonico inicial:

- `assets/reference/translation_curation/composição_de_cenas/`
- `tools/image-tools/specs/source_semantic_cases/`

## Projeto Pequeno Principe: fluxo canonico

1. Lote chega em `tmp/imagegen/inbox/pequeno_principe_v2/` (production/, indexed/, boards/).
2. Redimensionar e indexar:  
   `python tools/image-tools/resize_and_index_pequeno_principe_batch.py`  
   (ou passando o batch root como argumento).
3. Validar:  
   `powershell -ExecutionPolicy Bypass -File tools/image-tools/validate_pequeno_principe_asset_batch.ps1`
4. Promover para `res/`:  
   `powershell -ExecutionPolicy Bypass -File tools/image-tools/promote_pequeno_principe_asset_batch.ps1`

A arte conceito do jogo e a referencia canonica; ver `doc/REFERENCIA_ARTE_CONCEITO.md` na raiz do repo e `08-bible-artistica.md` no projeto.

## Dependencia

- **Pillow:** `pip install Pillow` (para `batch_resize_index.py` e `fix_png_transparency_final.py`).

## Observacao

O fluxo automatico de build (transparencia em recursos) continua em `tools/sgdk_wrapper/fix_transparency.ps1`. Este diretorio concentra tratamento de **lotes** e correcoes manuais fora do build.
