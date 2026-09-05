# Changelog — TAINA resampling route lab

## 2026-09-01

- Laboratório isolado criado sob `_agent_laboratory`.
- Model sheet, fonte direcional 56×80, v04 rejeitada e contratos copiados com hashes.
- Decisão humana exata `rejected_requires_route_lab` para v04 registrada em
  `contracts/v04_route_lab_rejection.json`, SHA-256 do asset
  `0f0c758bd50fd41b028ad44f04a3c48e48faf1859f2b4e9769ca68621733800e`.
- Stage 1: 20 rotas ImageMagick/Pillow/OpenCV executadas; 5 rotas GIMP puladas após timeout sem export determinístico.
- Stage 2: quatro survivors selecionados para probes de paleta manual semântica.
- Stage 3: duas guias de retrabalho nativo produzidas por planos explícitos de grid; nenhuma é v05 ou candidata final.
- Repetição da matriz reproduziu os hashes das rotas.
- Nenhuma escrita em MARE_BRAVA/data, MARE_BRAVA/res, MARE_BRAVA/src ou em projeto externo.
- Recebida `approve_hybrid_cleanup_shootout` em 56x80; bases e hashes foram
  persistidos no contrato humano. Geradas três variantes com matte binário,
  paleta semântica e patches nativos explícitos; nenhuma foi promovida.
- Novo gate: seleção humana de uma candidata híbrida, com `res_promotion=false`.
- Selecionado o incumbent PRIMARY para rework localizado; gerado o rework
  `hybrid_cleanup_primary_im_lanczos3_rework_v01` com SHA-256
  `cb6ff5c695c5e7b76e80d84ebd497f8f55e162561c0f2caeb0f345604c31529e`.
- O rework remove a sombra de chão assada entre os pés e um pixel órfão do sash;
  permanece `technical_candidate` até nova decisão humana.
- Revisão humana corrigiu o método para `mechanical_palette_remap_with_minimal_native_patches`;
  `native_cleanup=incomplete`; `material_topology=not_run`; e
  `semantic_map=derived_diagnostic_not_independent`. O mapa por índice de
  paleta deixou de ser descrito como segmentação artística.
- A tentativa `hybrid_cleanup_primary_im_lanczos3_rework_v02` foi marcada como
  descartada por regressão visual de remapeamento amplo; não é fonte nem
  baseline. A v03 parte do controle v01 e registra 44 patches não nulos, além
  de mapa independente antes da recalculação restrita de rampas.
- A v03 vigente é
  `hybrid_cleanup_primary_im_lanczos3_rework_v03`, SHA-256
  `99160ec422010d2ac68fbb4b10cc03db72012316508882e1b9b8cf336ec51a33`.
  Pixel contract técnico passou: P/4bpp, 56x80, 14 cores visíveis, PLTE 16,
  índice 0 transparente, sem blocker. A linha 77 tem zero pixels na faixa
  central anteriormente assada. O gate visual humano continua pendente.
- Recebida a aprovação formal da v03 como checkpoint intermediário da rota
  híbrida, vinculada ao SHA-256
  `99160ec422010d2ac68fbb4b10cc03db72012316508882e1b9b8cf336ec51a33`.
  Ela congela a v03 como incumbent e não autoriza `visual_pass`, pose final,
  animação, `res/`, runtime, ROM ou AAA.
- Produzida a v04 estritamente localizada sobre a v03, sem novo resize, filtro
  ou remapeamento global. A candidata tem SHA-256
  `791074aa6919ac0bac78a60693c12daee8f03169b216996758a8a272bc6b214e` e 36
  patches não nulos. O mapa de materiais foi atribuído independentemente por
  coordenadas e contorno, mas permanece pendente de validação artística.
- Novo gate: `approved_for_final_native_pose`; o estado atual ainda é
  `technical_pass_visual_rework`/`pending_human_decision`.

## 2026-09-01 — v04 congelada; v05 localizada com contrato material independente

- Registrada a rejeição humana da v04 somente como pose final; v04 permanece o
  incumbent obrigatório de rework. Produzida v05 somente por edição direta de
  clusters na grade 56x80, sem resize, filtro, quantização ou remapeamento
  global. SHA-256 da v05:
  `6ef8528a91f8cc32e15af5ce8c3e404a37e57927adb0be74f1298b106e7600d3`.
- Criados contrato material, leakage report, mapas independentes,
  boundary overlay, palette role map, delta v04→v05, crops, composição,
  matte/halo, provenance e validação pixel-strict vinculados ao SHA da v05.
- Topologia permanece reprovada por leakage (v04 510; v05 505), apesar da
  cobertura geométrica exata e das cinco fronteiras críticas observáveis. O
  próximo gate positivo só vale após cleanup nativo completo, topologia aprovada
  e reconhecimento inequívoco em 1x.
- `res/`, animação, SGDK, ROM, `visual_pass` e AAA não foram tocados ou
  autorizados. Estado final da rodada: `pending_human_decision`.

## 2026-09-01 — medidor de topologia v02 reparado sem alterar v05

- Preservada a v05 como incumbent diagnóstico, sem alteração de pixels e sem
  produção de v06. SHA mantido:
  `6ef8528a91f8cc32e15af5ce8c3e404a37e57927adb0be74f1298b106e7600d3`.
- Corrigidos os relatórios para `patches_attempted=23`,
  `patches_effective=18`, `patches_noop=5`.
- Substituída a anotação retangular por mapa externo em spans de linha, contrato
  material, mapa RGB de rótulos, overlay de fronteiras e relatório de leakage.
  A validação adversarial permanente passou 8/8.
- Medição nova: v04 = annotation error 4 / palette leakage 832; v05 =
  annotation error 0 / palette leakage 827. As fronteiras esperadas da v05
  passaram, mas a topologia geral permanece ambígua e reprovada.

## 2026-09-01 — contrato de topologia v03 em duas camadas

- A v05 foi mantida byte a byte; SHA-256 confirmado:
  `6ef8528a91f8cc32e15af5ce8c3e404a37e57927adb0be74f1298b106e7600d3`. Não foi
  produzida v06 e nenhum arquivo em `res/` foi alterado.
- Persistida a anotação externa
  `material_owner_shade_annotation_v01.json`, com `material_owner_map` e
  `shade_role_map` independentes. Não há `default=skin`; pixels visíveis não
  anotados são `unassigned`. A anotação foi revisada contra v05 1x, nearest 8x
  e model sheet; o RGB gerado é apenas diagnóstico.
- O medidor v03 passou a conferir pares de proprietários esperados em múltiplos
  segmentos, permissões coordenadas para papéis compartilhados e a matriz
  material × índice × shade_role. Os resultados separados da v05 são:
  `material_map_accuracy=passed`, `material_boundary_topology=passed`,
  `palette_role_conformance=failed` e `visual_material_readability=pending_human_review`.
- A medição confiável encontrou 829 violações de rampa em 44 componentes
  conectados; o valor histórico 827 veio do mapa legado com fallback e foi
  preservado apenas para comparação. Leakage não equivale a contagem de patches.
- Fixtures adversariais semânticas passaram 10/10, cobrindo fallback residual,
  hair/skin, par de fronteira errado, outline/deep shadow fora de contrato,
  fronteira vacuamente verdadeira, pé isolado, expansão global de índice,
  mapa derivado da paleta e no-op accounting.
- Decisão causal: os conflitos estão espalhados pelos interiores de vários
  materiais; a rota de staging `material_palette_reseed_v01` foi executada por
  `material_owner + shade_role`. BASIC SHA-256
  `24bee2d802e9bda6cbbabd43637220b5c2c99b1d66ebdeba21fd24205fedd33a`; ELITE
  SHA-256 `753815ea994859cc52c35e701a505258cbb141896b44717fb7f8239aeb415f9b`.
  `native_cleanup=incomplete`,
  `material_topology=failed_requires_localized_material_cleanup`,
  `visual_pass=false`, `res_promotion=false`, `animation_authorization=false`,
  `rom_authorization=false` e `ready_for_aaa=false` permanecem.

## 2026-09-01 — rejeição humana do reseed de paleta

- Recebida a decisão exata `reject_material_palette_reseed_as_visual_challengers`.
  BASIC SHA-256 `24bee2d802e9bda6cbbabd43637220b5c2c99b1d66ebdeba21fd24205fedd33a`;
  ELITE SHA-256 `753815ea994859cc52c35e701a505258cbb141896b44717fb7f8239aeb415f9b`.
- Motivo humano: `semantic_flattening_destroyed_internal_drawing_and_identity`.
  A decisão registra 4 pixels diferentes entre BASIC e ELITE e ratio declarado
  `0.00271`; essa contagem não é usada como proxy de qualidade.
- Os challengers foram preservados somente como evidência rejeitada. A v05
  continua o controle congelado, sem alteração de pixels. Não houve promoção
  para `res/`, animação, ROM, `visual_pass` ou AAA.
- Classificação final dos challengers: `method=diagnostic_semantic_color_blocking`,
  `acceptance_status=visual_lab_control`, `promotable=false` e
  `allowed_as_pixel_source=false`.

## 2026-09-01 — blocking nativo estrutural 56x80, stage v03

- A rejeição humana do reseed foi registrada sem apagar os controles BASIC/ELITE
  e sem permitir que eles sejam fontes de pixel. A nova rota volta ao lineart
  blocking guiado exclusivamente pelo model sheet v02; Lanczos3 e Mitchell
  permanecem apenas como underlays de direção/proporção.
- v01 foi tentada e descartada porque o torso e os braços liam como massa
  genérica. v02 foi tentada e descartada porque a separação melhorou, mas a
  guarda ainda permanecia lateral. Essas falhas são preservadas como evidência
  negativa, sem promoção.
- Stage v03 produziu duas alternativas independentes em 56x80. A usa SHA-256
  `cd911846f1eab6f05e59be714fdf0520a021ea88b9fdc008f2279112133c10ff`; B usa
  SHA-256 `2783c59c6c26e645825295d570c70d2a1ea01be1580fa02c306e35017e045264`.
  A/B diferem em 93 pixels de 1678 visíveis, ratio 0.055423..., e em seis
  regiões nomeadas. A diferença é evidência de alternativas, não score.
- A etapa é `agent_authored_native_lineart_blocking` /
  `visual_lab_control`; ainda não há materiais, sombras ou highlights finais.
  O contrato técnico de cada PNG é P/4bpp, 56x80, índice 0 transparente e
  grade 8x8. Fixtures adversariais do gate: 5/5.
- O próximo gate é humano e restrito à escolha A/B. Permanecem
  `visual_pass=false`, `promotable=false`, `res_promotion=false`,
  `animation_authorization=false`, `rom_authorization=false` e
  `ready_for_aaa=false`.
