# TAINA — revisão v04 da PRIMARY

## Estado

- v03 congelada como checkpoint intermediário: `hybrid_cleanup_primary_im_lanczos3_rework_v03`, SHA-256 `99160ec422010d2ac68fbb4b10cc03db72012316508882e1b9b8cf336ec51a33`.
- v04 atual: `hybrid_cleanup_primary_im_lanczos3_rework_v04`, SHA-256 `791074aa6919ac0bac78a60693c12daee8f03169b216996758a8a272bc6b214e`.
- Escala travada: `56x80`; `64x96` é `comparison_only`.

## Evidência visual

- [PNG v04 1x](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v04/hybrid_cleanup_primary_im_lanczos3_rework_v04.png)
- [Preview nearest 8x](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v04/preview_nearest_8x.png)
- [Board v03/v04/silhueta](localized_native_cleanup_v04_comparison_board.png)
- [Crops e composição 320x224](localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v04/)

## Alterações causais v04

- rosto: cluster conectado de testa/cabelo, sobrancelha, olho, nariz implícito,
  bochecha e mandíbula;
- cabelo: três entalhes de silhueta e quatro grupos de cachos;
- guarda: separadores hard-edge entre punho, wrap e antebraço dos dois lados;
- abdômen: consolidação de highlights em planos de pele;
- sash: reforço do nó e do caimento;
- calças: continuidade das sombras internas dos joelhos;
- pés: contato mantido sem faixa de chão assada.

Todos os patches têm região, sintoma, coordenada, índice antes/depois e motivo.
Não houve resize, filtro ou remapeamento global.

## Limite

`status=technical_pass_visual_rework`

`native_cleanup=incomplete`

`material_topology=independent_candidate_pending_human_review`

`semantic_map=derived_diagnostic_not_independent`

O próximo gate positivo é `approved_for_final_native_pose`; não há autorização
para `res/`, animação, integração, ROM, `visual_pass` ou AAA.
