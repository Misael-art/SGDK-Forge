# TAINA resampling route lab memory

- Identity is bound to the copied model sheet SHA; the 56x80 source is directional only.
- Stage 1 executed 20 deterministic ImageMagick/Pillow/OpenCV geometry routes and skipped 5 GIMP routes after batch timeout/no export.
- Stage 2 selected four probes for the same manual semantic palette; none is a native candidate.
- Stage 3 contains two native-grid guide candidates only; they are not v05, not final and not eligible for res/.
- Human rejection is recorded exactly as `rejected_requires_route_lab` for v04, SHA-256 `0f0c758bd50fd41b028ad44f04a3c48e48faf1859f2b4e9769ca68621733800e`, in `contracts/v04_route_lab_rejection.json`; normal TAÍNA production is paused until this lab gate.
- Human decision `approve_hybrid_cleanup_shootout` is recorded in
  `contracts/human_hybrid_cleanup_shootout_decision_v01.json`. The approved
  bases are Lanczos3, Mitchell-Netravali and Catmull-Rom at 56x80; three cleanup
  candidates exist, all still pending human selection.
- Human selected `hybrid_cleanup_primary_im_lanczos3_v01` for
  `localized_native_cleanup_only`. The rework removes the baked ground-shadow
  strip between the feet and one orphan sash-edge pixel; its human gate remains
  pending.
- A revisão humana corrigiu o rótulo do método: `mechanical_palette_remap_with_minimal_native_patches`;
  `native_cleanup=incomplete`; `material_topology=not_run`; e
  `semantic_map=derived_diagnostic_not_independent`. O mapa semântico derivado
  do índice de paleta não é tratado como segmentação artística.
- A v02 foi executada como tentativa de remapeamento amplo e descartada por
  regressão visual: achatou massas de material e não pode alimentar outra
  candidata. A v03 foi refeita somente sobre o controle v01, preservando a
  macrogeometria e aplicando 44 patches não nulos, incluindo cabelo, rosto,
  guarda, top/abdômen, sash, calças e pés.
- Candidata vigente: `hybrid_cleanup_primary_im_lanczos3_rework_v03`, SHA-256
  `99160ec422010d2ac68fbb4b10cc03db72012316508882e1b9b8cf336ec51a33`, 56x80.
  O pixel contract é técnico; `technical_pass_visual_rework` continua pendente
  de julgamento humano. A faixa central de chão na linha 77 mede zero pixels;
  isto não equivale a `visual_pass`.
- O mapa de materiais independente permanece apenas hipótese diagnóstica:
  `material_topology=not_run`, sem prova de separação artística. `res/`,
  animação, runtime, ROM, `visual_pass` e AAA continuam proibidos.
- A decisão humana aprovou a v03 somente como checkpoint intermediário:
  `approve_localized_native_cleanup`, SHA-256
  `99160ec422010d2ac68fbb4b10cc03db72012316508882e1b9b8cf336ec51a33`.
  A v03 está congelada como incumbent; não é `visual_pass` nem pose final.
- A v04 foi produzida estritamente sobre a v03, sem resize, filtro ou remapeamento
  global. Candidata atual: `hybrid_cleanup_primary_im_lanczos3_rework_v04`,
  SHA-256 `791074aa6919ac0bac78a60693c12daee8f03169b216996758a8a272bc6b214e`.
  Foram aplicados 36 patches não nulos. O mapa de materiais atribui cada pixel
  visível a um papel diagnóstico independente, mas aguarda revisão artística.
- O próximo gate positivo é separado e exato:
  `approved_for_final_native_pose`; animação e promoção continuam bloqueadas.

## 2026-09-01 — v04 preservada e v05 em gate de topologia

- A decisão humana rejeitou a v04 somente como pose final, preservando-a como
  incumbent para rework localizado. A v05 foi produzida exclusivamente sobre a
  v04, sem resize, filtro, nova quantização, remapeamento global ou regeneração.
- Candidata atual: `hybrid_cleanup_primary_im_lanczos3_rework_v05`, SHA-256
  `6ef8528a91f8cc32e15af5ce8c3e404a37e57927adb0be74f1298b106e7600d3`, escala
  56x80. As alterações são clusters localizados de cabelo, rosto, guarda,
  abdômen, sash e calças, mantendo a macrogeometria da v04.
- Contratos materiais independentes foram produzidos para v04 e v05. A
  cobertura é exata, mas há leakage de rampa: v04=510 e v05=505 ocorrências.
  As fronteiras críticas estão presentes na v05 (15, 14, 26, 33 e 17), sem
  transformar isso em aprovação estética. `material_topology=failed_requires_localized_material_cleanup`.
- A v05 passa o contrato técnico P/4bpp (56x80, 15 cores visíveis, PLTE 16,
  índice 0 transparente, alpha binário, sem blocker), mas permanece
  `technical_pass_visual_rework`, `native_cleanup=incomplete` e
  `pending_human_decision`. Não houve promoção para `res/`, animação, runtime,
  ROM, `visual_pass` ou AAA.
- O budget continua `planning_budget`: TAÍNA 56x80 + 4 CRIA 48x64 = 22 links,
  pico 10 sprites e 248 pixels/scanline; 2 CRIA + 2 ESTIVADOR = 22 links,
  pico 10 e 264 pixels; estresse 3+3 = 30 links, pico 14 e 368 pixels, acima
  de H40.

## 2026-09-01 — reparo do medidor de topologia da v05

- A v05 foi congelada como incumbent visual de diagnóstico; nenhum pixel foi
  alterado e nenhuma v06 foi produzida. SHA permanece
  `6ef8528a91f8cc32e15af5ce8c3e404a37e57927adb0be74f1298b106e7600d3`.
- Corrigida a contabilidade: `patches_attempted=23`,
  `patches_effective=18`, `patches_noop=5`. A contagem não é critério de
  qualidade.
- Removida a topologia retangular como fonte canônica. O novo mapa externo é
  pixel-accurate, revisável e usa rótulos RGB distintos; a atribuição não
  consulta índices de paleta. `outline_shared` existe somente em coordenadas
  explícitas; wraps e sash compartilham `teal_fabric`; pés pertencem a `skin`.
- Fixtures adversariais permanentes passaram 8/8. Rederivação: v04 registra
  `ownership_annotation_error=4` e `material_palette_leakage=832`; v05 registra
  `ownership_annotation_error=0` e `material_palette_leakage=827`.
  `ambiguous_requires_human_review` permanece verdadeiro e não há base honesta
  para decidir patches de v06.

## 2026-09-01 — contrato v03: ownership e shade role independentes

- A anotação v02 foi desautorizada como oráculo por permitir fallback e por
  confundir material com shade. A v03 persiste
  `material_owner_shade_annotation_v01.json` antes de medir, com pixels
  visíveis sempre explícitos ou `unassigned`, sem `default=skin`.
- O `material_owner_map` usa transparent, hair, skin, orange_top, teal_fabric e
  indigo_trousers. O `shade_role_map` usa outline_shared, deep_shadow_shared,
  shadow, base e highlight. Roles compartilhados são válidos apenas em
  coordenadas explicitamente autorizadas; wraps/sash continuam teal_fabric e
  pés continuam skin.
- A v05 foi medida por pares esperados de fronteira e por matriz
  material × índice × shade_role. Resultados: `material_map_accuracy=passed`,
  `material_boundary_topology=passed`, `palette_role_conformance=failed` e
  `visual_material_readability=pending_human_review`.
- Leakage confiável v05 = 829 pixels em 44 componentes conectados. O valor
  legado 827 (v04=832) permanece somente como comparação do mapa com fallback.
  Fixtures semânticas v03: 10/10. Isso não autoriza patches equivalentes ao
  contador e não modifica a v05.
- Os conflitos atravessam interiores de vários materiais; a rota causal
  `material_palette_reseed_v01` foi aberta em staging. BASIC e ELITE foram
  produzidos por `material_owner + shade_role`, sem nearest-color ou
  remapeamento global, e aguardam escolha humana. BASIC SHA-256
  `24bee2d802e9bda6cbbabd43637220b5c2c99b1d66ebdeba21fd24205fedd33a`; ELITE
  SHA-256 `753815ea994859cc52c35e701a505258cbb141896b44717fb7f8239aeb415f9b`.
  Permanecem
  `native_cleanup=incomplete`,
  `visual_pass=false`, `res_promotion=false`, `animation_authorization=false`,
  `rom_authorization=false` e `ready_for_aaa=false`.

## 2026-09-01 — contrato v03: ownership e shade role independentes

- A anotação v02 foi desautorizada como oráculo por permitir fallback e por
  confundir material com shade. A v03 persiste
  `material_owner_shade_annotation_v01.json` antes de medir, com pixels
  visíveis sempre explícitos ou `unassigned`, sem `default=skin`.
- O `material_owner_map` usa transparent, hair, skin, orange_top, teal_fabric e
  indigo_trousers. O `shade_role_map` usa outline_shared, deep_shadow_shared,
  shadow, base e highlight. Roles compartilhados são válidos apenas em
  coordenadas explicitamente autorizadas; wraps/sash continuam teal_fabric e
  pés continuam skin.
- A v05 foi medida por pares esperados de fronteira e por matriz
  material × índice × shade_role. Resultados: `material_map_accuracy=passed`,
  `material_boundary_topology=passed`, `palette_role_conformance=failed` e
  `visual_material_readability=pending_human_review`.
- Leakage confiável v05 = 829 pixels em 44 componentes conectados. O valor
  legado 827 (v04=832) permanece somente como comparação do mapa com fallback.
  Fixtures semânticas v03: 10/10. Isso não autoriza patches equivalentes ao
  contador e não modifica a v05.
- Os conflitos atravessam interiores de vários materiais; a rota causal
  `material_palette_reseed_v01` foi executada em staging. BASIC e ELITE foram
  produzidos por `material_owner + shade_role`, mas a decisão humana os rejeitou
  por `semantic_flattening_destroyed_internal_drawing_and_identity`.
  Permanecem `native_cleanup=incomplete`,
  `visual_pass=false`, `res_promotion=false`, `animation_authorization=false`,
  `rom_authorization=false` e `ready_for_aaa=false`.

## 2026-09-01 — rejeição humana dos challengers de reseed

- Registrada a decisão exata `reject_material_palette_reseed_as_visual_challengers`,
  vinculada aos SHA da BASIC
  `24bee2d802e9bda6cbbabd43637220b5c2c99b1d66ebdeba21fd24205fedd33a` e da ELITE
  `753815ea994859cc52c35e701a505258cbb141896b44717fb7f8239aeb415f9b`.
- `basic_elite_changed_pixels=4` e `basic_elite_changed_ratio=0.00271` foram
  preservados como observação humana, não como score. Os challengers ficam
  somente como evidência rejeitada; a v05 continua controle congelado em 56x80.
- Classificação dos challengers: `method=diagnostic_semantic_color_blocking`,
  `acceptance_status=visual_lab_control`, `promotable=false` e
  `allowed_as_pixel_source=false`.

## 2026-09-01 — blocking nativo 56x80 para novo gate humano

- Registrada a decisão humana que rejeitou BASIC e ELITE do reseed como
  challengers visuais, preservando-os somente como controles técnicos. A razão
  é `semantic_flattening_destroyed_internal_drawing_and_identity`; nenhum pixel
  deles pode alimentar a nova arte.
- Produzidas três tentativas de blocking estrutural em staging. v01 e v02
  foram descartadas por leitura observável genérica: torso em bloco e guarda
  lateral/ambígua. A v03 é a tentativa vigente do stage, com máscara autorada
  em grade nativa, negativo entre braços e caixa torácica, dois punhos elevados
  e variações A/B derivadas de hipóteses de lineart, não de pixels das fontes.
- Candidata A: `taina_56x80_native_lineart_blocking_a_v03`, SHA-256
  `cd911846f1eab6f05e59be714fdf0520a021ea88b9fdc008f2279112133c10ff`.
  Candidata B: `taina_56x80_native_lineart_blocking_b_v03`, SHA-256
  `2783c59c6c26e645825295d570c70d2a1ea01be1580fa02c306e35017e045264`.
  Ambas permanecem `visual_lab_control`, `allowed_as_pixel_source=false` e
  `pending_human_decision`.
- A comparação A/B tem 93 pixels diferentes sobre 1678 visíveis, ratio
  observacional 0.055423..., e diferenças em face, cabelo, guarda, hem, sash e
  pés. Isso apenas prova alternativas estruturais; não é score estético nem
  visual pass.
- Evidências geradas para cada candidata: PNG P/4bpp 56x80, 1x/2x/3x/8x
  nearest, silhueta, fundos claro/escuro/chroma, composição 320x224, crops,
  overlay com model sheet e mapa de contorno interno. Fixtures adversariais do
  gate passaram 5/5; o relatório mantém a decisão visual humana pendente.
- As tentativas v01 e v02 ficam preservadas como evidência negativa da rota; a
  v05 continua congelada como controle, SHA-256
  `6ef8528a91f8cc32e15af5ce8c3e404a37e57927adb0be74f1298b106e7600d3`.
  Não houve alteração em v05, material maps, `res/`, animação, SGDK ou ROM.
