# TAINA — revisão direta da PRIMARY v03

## Linhagem

- Model sheet de identidade: `../../MARE_BRAVA [VER.001] [SGDK 211] [GEN] [GAME] [BRAWLER]/data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png`, SHA-256 `324951fb2c35da907229430ff128742a2cdb28632a098b1cb7b0c48c5c0cf87a`.
- Direção/proporção aprovada: fonte visual 56x80, SHA-256 `32c5a8089c52251c0276eb0c28406b44e7797455a767b4a498c1da74be094d4f`; não é fonte de pixels finais.
- PRIMARY selecionada para rework: `hybrid_cleanup_primary_im_lanczos3_v01`, SHA-256 `3e60cd9efb233d0ce715c543e9cacdaacbe044b253c088dd06ada52f131b4cf1`.
- Rework atual: `hybrid_cleanup_primary_im_lanczos3_rework_v03`, SHA-256 `99160ec422010d2ac68fbb4b10cc03db72012316508882e1b9b8cf336ec51a33`.

## Comparação observável

- [Board parent v01 vs rework v03](localized_native_cleanup_v03_comparison_board.png)
- [PNG v03 em 1x](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v03/hybrid_cleanup_primary_im_lanczos3_rework_v03.png)
- [Preview nearest 8x](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v03/preview_nearest_8x.png)
- [Crops de rosto, guarda, sash e pés](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v03/)

Ganhos verificáveis na v03: faixa de chão central removida; patches explícitos em
cachos, olho/contorno facial, wraps/punhos, hem/axilas/abdômen, nó do sash,
clusters das calças e contato dos pés. Perdas/limites: a macrogeometria herdada
continua presente; a limpeza ainda não recebeu aprovação visual humana; o mapa
independente é hipótese diagnóstica e `material_topology` continua `not_run`.

## Estado do método

`method=mechanical_palette_remap_with_minimal_native_patches`

`native_cleanup=incomplete`

`material_topology=not_run`

`semantic_map=derived_diagnostic_not_independent`

A v02 está descartada por regressão de remapeamento amplo e não pode ser usada
como fonte ou baseline.
