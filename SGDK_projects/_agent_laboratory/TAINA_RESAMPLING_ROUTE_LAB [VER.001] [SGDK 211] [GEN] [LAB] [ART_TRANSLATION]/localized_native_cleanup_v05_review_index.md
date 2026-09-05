# TAÍNA 56x80 — v05 review index

## Gate atual

`pending_human_decision` — `technical_pass_visual_rework`.

v04 permanece congelada como incumbent de rework localizado, rejeitada somente
como pose final. v05 foi produzida exclusivamente por edição de clusters sobre
v04. A escala 56x80 continua travada; 64x96 é apenas `comparison_only`.

| item | asset / SHA-256 |
|---|---|
| model sheet aprovado, identidade | `inputs/model_sheet_v02.png` / `324951fb2c35da907229430ff128742a2cdb28632a098b1cb7b0c48c5c0cf87a` |
| incumbent v04 | `hybrid_cleanup_primary_im_lanczos3_rework_v04` / `791074aa6919ac0bac78a60693c12daee8f03169b216996758a8a272bc6b214e` |
| candidata v05 | `hybrid_cleanup_primary_im_lanczos3_rework_v05` / `6ef8528a91f8cc32e15af5ce8c3e404a37e57927adb0be74f1298b106e7600d3` |

## Evidência visual

- [v04 1x PNG](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v04/hybrid_cleanup_primary_im_lanczos3_rework_v04.png)
- [v05 1x PNG](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/hybrid_cleanup_primary_im_lanczos3_rework_v05.png)
- [board v04→v05](localized_native_cleanup_v05_comparison_board.png)
- [v05 2x](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/preview_nearest_2x.png), [3x](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/preview_nearest_3x.png), [8x nearest](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/preview_nearest_8x.png)
- [silhueta](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/silhouette_binary.png), [fundo claro](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/background_light.png), [fundo escuro](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/background_dark.png), [fundo chroma](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/background_chroma.png)
- [composição 320x224](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/composition_320x224.png)
- crops: [rosto](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/crop_head_face.png), [guarda](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/crop_shoulders_guard.png), [abdômen/sash](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/crop_waist_hip.png), [pés](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/crop_feet_ground.png)
- [delta v04→v05](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/delta_v04_to_v05.png)

## Topologia e contratos

- [material region contract v04](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v04/material_region_contract.json)
- [material region contract v05](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/material_region_contract.json)
- [v05 material map RGB](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/material_owner_map_diagnostic.png)
- [v05 material map RGB 8x](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/material_owner_map_diagnostic_8x.png)
- [v05 boundary overlay](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/material_boundary_expected_diagnostic_8x.png)
- [v05 two-layer annotation](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/material_owner_shade_annotation_v01.json)
- [v05 owner+shade overlay](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/material_owner_shade_overlay_8x.png)
- [v05 boundary contract overlay](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/material_boundary_contract_overlay_8x.png)
- [owner × index × shade matrix](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/owner_index_shade_confusion_matrix.json)
- [legacy vs corrected measurement](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/material_topology_old_vs_corrected.json)
- [adversarial semantic fixtures](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/material_topology_fixture_report.json)
- [v05 independent topology report](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/material_topology_independent_report.json)
- [v05 leakage report](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/material_leakage_report.json)
- [v05 palette role map](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/palette_role_map.png)
- [v05 cleanup action log](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/cleanup_actions.json)
- [v05 topology measurement repair report](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/material_topology_measurement_report.json)

O contrato v03 separa `material_owner_map` de `shade_role_map`, não usa
`owner_at` retangular, não usa fallback para skin e mantém `outline_shared` e
`deep_shadow_shared` apenas em coordenadas explícitas. A v05 tem cobertura
geométrica exata e zero pixels não anotados, mas `material_topology` continua
falhando: a medição confiável encontrou 829 violações de rampa, distribuídas em
44 componentes conectados. Isso não é autorização para 829 patches.

Resultados separados: `material_map_accuracy=passed`,
`material_boundary_topology=passed`, `palette_role_conformance=failed` e
`visual_material_readability=pending_human_review`. O RGB é somente diagnóstico;
não é arte nem fonte de pixels. As fixtures semânticas permanentes passaram 10/10.

Comparação histórica: a leitura anterior do mapa com fallback registrava
leakage 827 e não é oráculo. A leitura v03, com ownership e shade independentes,
registra leakage confiável 829; a diferença não foi convertida em patches.

Contabilidade da tentativa de rework: `patches_attempted=23`,
`patches_effective=18`, `patches_noop=5`. A contagem efetiva não é usada como
prova de qualidade.

## Validação e proveniência

- [pixel/topology validation](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/localized_native_cleanup_validation_report.json)
- [matte/halo](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/matte_halo_report.json)
- [ground contact](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/ground_contact_report.json)
- [provenance](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/provenance_report.json)
- [localized cleanup report](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05/localized_native_cleanup_report.json)
- [human gate request](human_gate_request_localized_cleanup.md)

## Teto honesto

`native_cleanup=incomplete`, `visual_pass=false`, `res_promotion=false`,
`animation_authorization=false`, `rom_authorization=false`, `AAA=false`.
Nenhum arquivo em `res/` foi tocado. Como os conflitos estão espalhados pelos
interiores de vários materiais, a decisão causal é abrir a etapa
`material_palette_reseed_v01` em staging, preservando a v05 como controle; a
etapa produziu BASIC e ELITE abaixo, posteriormente rejeitados pela curadoria
humana. O único próximo gate positivo possível
é `approved_for_final_native_pose`, mas ainda não deve ser emitido enquanto o
cleanup não for completo, a topologia não passar e os pontos de reconhecimento
não forem inequívocos em 1x.

## Rota aberta: `material_palette_reseed_v01`

Os challengers foram produzidos por `material_owner + shade_role`, sem
nearest-color ou remapeamento global, preservando silhueta, pose, pivot,
contato e macrogeometria da v05:

- [BASIC 56x80](material_palette_reseed_v01/basic/taina_56x80_material_palette_reseed_basic_v01.png) — `24bee2d802e9bda6cbbabd43637220b5c2c99b1d66ebdeba21fd24205fedd33a`
- [ELITE 56x80](material_palette_reseed_v01/elite/taina_56x80_material_palette_reseed_elite_v01.png) — `753815ea994859cc52c35e701a505258cbb141896b44717fb7f8239aeb415f9b`
- [manifest](material_palette_reseed_v01/material_palette_reseed_manifest_v01.json) — `ad3152809a3311b0dfb6e60d77aca2197a44c6929cb1972f7f30cea332b4340d`

BASIC e ELITE são classificados como
`method=diagnostic_semantic_color_blocking`,
`acceptance_status=visual_lab_control`, `promotable=false` e
`allowed_as_pixel_source=false`. A validação estrutural passou nos dois, mas a
decisão humana os rejeitou como challengers visuais: o reseed achatou o desenho
interno e destruiu identidade.
Foram observados 4 pixels diferentes entre BASIC e ELITE (`0.00271`), sem que
essa contagem fosse usada como critério de qualidade.

[Decisão humana de rejeição](contracts/material_palette_reseed_rejection_v01.json)

## Blocking nativo 56x80 — gate A/B

O reseed BASIC/ELITE acima permanece somente controle técnico: a decisão
humana registrou `semantic_flattening_destroyed_internal_drawing_and_identity`
e proibiu seu uso como fonte de pixels. A nova etapa retoma lineart blocking
autoral em grade nativa, guiado pelo model sheet v02. Lanczos3 e Mitchell são
underlays de direção, não fontes de pixel.

As tentativas v01 e v02 foram preservadas como negativas. v01 deixou torso e
guarda como massa genérica; v02 melhorou o negativo, mas ainda deixou a guarda
lateral. A v03 é a etapa corrente:

- [board A/B](native_lineart_blocking_v03/native_lineart_shootout_board.png)
- [manifest](native_lineart_blocking_v03/native_lineart_blocking_manifest_v01.json)
- [validation report](native_lineart_blocking_v03/native_lineart_validation_report_v01.json)
- [delta A→B](native_lineart_blocking_v03/delta_overlay_a_vs_b.png)
- [human gate request](native_lineart_blocking_v03/human_gate_request_native_lineart_v01.md)
- [A PNG 1x](native_lineart_blocking_v03/A/taina_56x80_native_lineart_blocking_a_v03.png) — `cd911846f1eab6f05e59be714fdf0520a021ea88b9fdc008f2279112133c10ff`
- [B PNG 1x](native_lineart_blocking_v03/B/taina_56x80_native_lineart_blocking_b_v03.png) — `2783c59c6c26e645825295d570c70d2a1ea01be1580fa02c306e35017e045264`

A/B diferem em 93 pixels de 1678 visíveis, em face, cabelo, guarda, hem,
sash e pés. A proporção objetiva é evidência de alternativas, não score
estético. Cada candidata possui previews 2x/3x/8x nearest, silhueta,
fundos claro/escuro/chroma, composição 320x224, crops, overlay com o model
sheet e mapa de contorno interno.

## Estado do gate

`pending_human_decision`; `visual_pass=false`; `promotable=false`;
`res_promotion=false`; `animation_authorization=false`; `rom_authorization=false`;
`ready_for_aaa=false`. A decisão humana necessária é escolher A ou B como
direção de lineart para a próxima etapa de materiais, sem ainda autorizar pose
final, animação ou `res/`.
