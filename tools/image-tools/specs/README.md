# Specs de lote (batch_resize_index)

Cada arquivo JSON aqui define um lote para a ferramenta generica `batch_resize_index.py`.

Este diretorio tambem pode guardar manifestos de curadoria para a skill `art-translation-to-vdp`.
Ele agora tambem guarda manifestos supervisionados de parsing semantico de `source`.

## Formato

- **production:** lista de itens com:
  - `name`: identificador (para mensagens de erro)
  - `png_rel`: caminho relativo do PNG no batch root (ex.: `production/arquivo.png`)
  - `w`, `h`: dimensao final do PNG
  - `bmp_rel`: caminho relativo do BMP indexado (ex.: `indexed/arquivo.bmp`)
  - `bmp_w`, `bmp_h`: dimensao do BMP (pode diferir do PNG, ex.: paleta 16x1)
  - `transparency`: `true` se o asset deve ter pelo menos uma cor transparente (validador exige)
- **boards:** lista de itens com:
  - `rel`: caminho relativo do PNG (ex.: `boards/cena.png`)
  - `w`, `h`: dimensao final

## Uso

```bash
python tools/image-tools/batch_resize_index.py --spec tools/image-tools/specs/pequeno_principe_v2.json --batch-root tmp/imagegen/inbox/pequeno_principe_v2
```

Novos projetos podem adicionar um novo JSON e chamar `batch_resize_index.py` com `--spec` apontando para ele.

## Manifesto de curadoria da skill `art-translation-to-vdp`

Use `art_translation_case.template.json` como modelo para casos `basic` vs `elite`.

Campos principais:

- `case_id`
- `source_image`
- `translation_target`
- `reference_profile`
- `minimum_delta`
- `intent_notes`
- `soul_contract`
- `variants.basic.analysis_units`
- `variants.elite.analysis_units`

Cada `analysis_unit` pode declarar:

- `asset`
- `role`
- `critical_visual`
- `weight`
- `paired_bg`
- `paired_bg_layers`

Uso:

```bash
python tools/image-tools/analyze_translation_case.py --manifest tools/image-tools/specs/art_translation_case.template.json --output out/translation_case.json
```

## Manifesto supervisionado de parsing semantico

Use `source_semantic_case.template.json` como modelo para casos de alfabetizacao semantica de `source`.

Campos principais:

- `case_id`
- `source_image`
- `scene_truth_kind`
- `layout_complexity`
- `source_inventory`
- `drop_policy`
- `composition_schema`
- `semantic_parse_report`
- `training_labels`

`semantic_parse_report` pode declarar:

- `semantic_regions`
- `auxiliary_regions`
- `drop_regions`
- `animation_ranges`
- `final_scene_hypothesis`

Uso:

```bash
python tools/image-tools/analyze_source_semantics.py --manifest tools/image-tools/specs/source_semantic_case.template.json --output out/source_semantics.json
```
