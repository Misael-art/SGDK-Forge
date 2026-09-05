# Human Approval Record

status: direction_ratified_selected_assets_runtime_candidates
template_seed: false
checkpoint_date: 2026-07-05
checkpoint_scope: direcao_artistica_e_contrato_de_traco
checkpoint_source: prompt_humano_de_continuacao_autonoma

O owner humano declarou a direcao artistica e o contrato de traco autoral
curados e congelados como direcao de producao.

Esta ratificacao autoriza produzir model sheets pixel, lineart, key poses,
strips e o kit modular sob os contratos existentes. Ela nao aprova
individualmente os PNGs atuais, nao autoriza promocao para `res/` e nao prova
qualidade em runtime.

Assets continuam sujeitos a pixel-strict, fidelidade model-sheet-to-sprite,
budget VDP, evidencia BlastEm e closeout visual.

## 2026-07-28 — baseline visual selecionada pelo diretor de arte

O diretor de arte humano confirmou como baseline de direção a imagem 04 da
linha do tempo: `data/processed/contact_sheets/authorial_style_validation_contact_sheet_v01.png`.
Para a TAÍNA, a fonte individual correspondente é
`data/source_art/concept/authorial_style_validation_2026_07_04/taina_identity_turnaround_authorial_v01.png`.

As imagens 05 e 06 da linha do tempo são retrocessos. Os candidatos de lineart
v05, v06 e v07 ficam proibidos como fonte, baseline, referência de geração ou
img2img; seu único uso permitido é comparação/evidência negativa.

Esta aprovação fixa direção e linhagem de geração. Ela não aprova sprite final,
promoção para `res/`, budget, build, ROM ou evidência de emulador.

## 2026-07-29 — resultado visual v02 aprovado para continuidade

O diretor de arte humano declarou: `Visual Resultado visual v02 ficou bom
prossiga`.

A aprovação cobre a pose-mestre e a direção visual da strip
`taina_idle_guard_v02`: silhueta alta, cabelo dominante, face angular, guarda
elevada, top laranja, faixa teal e calça índigo. Ela autoriza usar essa v02
como incumbente e origem dos próximos estados da TAÍNA.

A v01, o proxy v02 com morphing e os linearts v05-v07 continuam proibidos como
fonte. A aprovação visual não substitui dump VDP, budget do gameplay completo,
teste sustentado de performance, áudio ou scene closeout.

## 2026-07-29 — direção da pose ativa do primeiro jab aprovada

Após a apresentação da pose direcional
`taina_light_jab_active_directional_study_v01.png`, o diretor de arte humano
respondeu `Prossiga`. A resposta aprova a direção do contato ativo:
extensão horizontal do braço dianteiro, base de muay thai, identidade da
TAÍNA v02 e envelope de ação 64×64.

Esta aprovação autoriza o redesenho no grid nativo. Ela não aprova
automaticamente a nova pose pixel, os quatro quadros restantes, a strip,
promoção para `data/processed`/`res`, build ou runtime.

## 2026-07-29 — pose nativa do primeiro jab aprovada para produção

Após receber a candidata pixel nativa 64×64, o diretor de arte humano
respondeu `Prossiga`. A instrução aprova a escala do punho, a interpretação da
guarda traseira e a pose de contato como topologia do frame ativo.

Essa aprovação autorizou derivar os outros quatro quadros por edição
controlada, executar os gates técnicos e promover a strip somente após eles
passarem. Ela não constitui, por si só, aprovação de budget da cena completa,
combate funcional, performance sustentada ou closeout AAA.

## 2026-08-29 — fonte autoral de reseed da TAÍNA aprovada para tradução pixel

O owner humano aprovou explicitamente a fonte
`data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png`
(SHA-256 `324951fb2c35da907229430ff128742a2cdb28632a098b1cb7b0c48c5c0cf87a`)
como a fonte autoral vigente da TAÍNA.

Esta decisão autoriza o pipeline `model_sheet_pixel_nativo -> tradução VDP ->
strips -> validação`, preservando rosto, cabelo cacheado preso, guarda, top
laranja, bandagens teal, calça índigo e faixa assimétrica. A prancha permanece
source high-res: não é PNG para `res/`, não é sprite sheet, não é model sheet
pixel validado e não aprova arte final, budget, ROM ou AAA.

## 2026-09-01 — reseed rejeitado; blocking nativo A/B pendente

O owner humano rejeitou os challengers `taina_56x80_material_palette_reseed_basic_v01`
(SHA-256 `24bee2d802e9bda6cbbabd43637220b5c2c99b1d66ebdeba21fd24205fedd33a`)
e `taina_56x80_material_palette_reseed_elite_v01` (SHA-256
`753815ea994859cc52c35e701a505258cbb141896b44717fb7f8239aeb415f9b`) com a
decisão exata `reject_material_palette_reseed_as_visual_challengers` e motivo
`semantic_flattening_destroyed_internal_drawing_and_identity`.

Eles foram reclassificados como `method=diagnostic_semantic_color_blocking`,
`acceptance_status=visual_lab_control`, `promotable=false` e
`allowed_as_pixel_source=false`. A rejeição não autoriza pose final, animação,
`res/`, ROM ou AAA.

A etapa seguinte é um gate de lineart blocking 56x80, ainda sem materiais
finais: candidata A `taina_56x80_native_lineart_blocking_a_v03`, SHA-256
`cd911846f1eab6f05e59be714fdf0520a021ea88b9fdc008f2279112133c10ff`; candidata
B `taina_56x80_native_lineart_blocking_b_v03`, SHA-256
`2783c59c6c26e645825295d570c70d2a1ea01be1580fa02c306e35017e045264`.
O estado é `pending_human_decision`; esta entrada não é aprovação de nenhuma
das duas.
