# Showdown Recovery - Fluxo ASCII de Decisao por Versao

Este documento explica, de forma pedagogica, como cada versao do estudo
Showdown foi decidida, o que foi produzido, qual sintaxe operacional guiou a
proxima etapa e onde houve intervencao humana.

Escopo fixo:

```text
PROJETO = estudo controlado / fixture tecnico
NAO_EH = entrega AAA
NAO_DECLARAR = ready_for_aaa | asset autoral final | validado_budget sem VDP dump
REGRA = se nao foi visto no BlastEm, nao existe
```

## Sintaxe de Decisao Global

```text
[entrada tecnica]
    |
    v
parse SFF/DEF -> reconstruir mundo -> medir arte -> exportar bins SGDK
    |
    v
copiar bins para viewer -> build SGDK -> BlastEm evidence
    |
    v
se screenshot + SRAM existem:
    status_emulador = testado_em_blastem_minimal
senao:
    status_emulador = blocked_rework_required

se visual_vdp_dump.bin existe e budget bate:
    budget = validado_budget
senao:
    budget = documented_not_validated_budget

se rota achata BG0/BG1/BG2/BG3 em um plano:
    route_status = lab_flattened_reference
senao se BG_B + BG_A preservam deltas e camera:
    route_status = route_a_multi_plane

se qualquer gate canonico falhar:
    nao declarar AAA/final
```

## Fluxo Geral das Versoes

```text
V00 raiz consolidada
   |
   v
V01 anti-magenta / reconstrucao logica
   |
   v
V02 mundo 768x480 + streaming de camera
   |
   v
[HUMANO: curadoria reprova camera/paleta/parallax]
   |
   v
V03 contratos + primeira recuperacao de paleta/camera
   |
   v
[HUMANO: "cores ainda nao estao vividas" + camera de luta/super jump]
   |
   v
V04 foco duplo + paleta viva + line scroll parcial
   |
   v
[HUMANO: diagnostico de color scrambling / index anchoring / tile budget]
   |
   v
V05 route_a_multi_plane + BlastEm ok + budget dump pendente
```

---

## V00 - 2026-06-07 - Consolidacao da Raiz

Objetivo:

```text
fazer o estudo existir como projeto rastreavel
```

Fluxo:

```text
tools/mugen2sgdk auditado
    |
    +-- se CLI reproduzivel existir -> usar ferramenta empacotada
    |
    +-- se CLI reproduzivel nao existir -> manter parser/exporter local
                                      |
                                      v
                              gerar relatorios medidos
                                      |
                                      v
                              viewer boota direto no Showdown
                                      |
                                      v
                              build + BlastEm inicial
```

Sintaxe de decisao:

```text
IF packaged_tool.has_reproducible_cli == false:
    pipeline_owner = "local_training_pipeline"
    canonical_promotion = false

IF BlastEm.screenshot_present:
    status = "stage_visible_but_not_approved"
```

Produzido:

```text
doc/10-memory-bank.md
doc/viewer_aggregate_manifest.json
analysis/* conversion reports
sgdk_viewer/showdown_viewer/out/rom.bin
evidence/blastem_showdown_screenshot.png
evidence/blastem_showdown_save.sram
```

Resultado:

```text
aparece no BlastEm, mas ainda com matte/magenta e budget nao validado
```

Intervencao humana registrada:

```text
nenhuma intervencao de curadoria especifica nesta versao;
foi uma consolidacao tecnica inicial.
```

Proxima sintaxe:

```text
IF visual has magenta/matte:
    fix_reconstruction_before_palette()
```

---

## V01 - 2026-06-07 - Anti-Magenta e Reconstrucao Logica

Objetivo:

```text
parar de tratar imagem bruta como verdade unica
e executar as regras reais do MUGEN/SFF/DEF
```

Fluxo:

```text
showdown.def + SFF/PCX
    |
    v
parse start/delta/tile/zoffset/camera
    |
    v
usar eixo do sprite SFF + ordem dos BGs do DEF
    |
    v
mask=1 -> indice 0 vira alpha
magenta claro -> alpha inferido quando for matte
    |
    v
visual_gate: matte/magenta <= 5%
    |
    v
export SGDK banded_palette_v1
    |
    v
BlastEm
```

Sintaxe de decisao:

```text
FOR each BG in DEF order:
    place(sprite, start, axis, delta)

IF bg.mask == 1:
    pcx.palette_index_0 = transparent

IF matte_ratio > 0.05:
    fail_pipeline()

IF palette_slot_0_holes:
    use_banded_palette_v1()
```

Produzido:

```text
tools/mugen_sff/visual_gate.py
work/reconstructed_layers/frame_0000..0003.png
analysis/palette_violations.json
sgdk_viewer runtime com 895 tiles unicos
BlastEm ROM sem matte catastrofico
```

Resultado:

```text
magenta corrigido; paleta ainda banded/degradada;
validado_budget=false
```

Intervencao humana registrada:

```text
nenhuma intervencao humana nova entre V00 e V01;
a decisao veio da evidencia visual/tecnica.
```

Proxima sintaxe:

```text
IF world was cropped/downscaled to 320x224:
    reconstruct_full_camera_world()
```

---

## V02 - 2026-06-08 - Mundo 768x480 e Camera Streaming

Objetivo:

```text
preservar a extensao real da camera MUGEN
```

Fluxo:

```text
DEF bounds:
  boundleft=-224
  boundright=224
  boundhigh=-240
  boundlow=0
    |
    v
world = 768x480 px = 96x60 tiles
viewport = 320x224
scroll_x = 0..448
scroll_y = 0..256
    |
    v
export custom map words
    |
    v
viewer streams 42x30 tile window
    |
    v
BlastEm evidence
```

Sintaxe de decisao:

```text
world_w = viewport_w + abs(boundleft) + abs(boundright)
world_h = viewport_h + abs(boundhigh) + abs(boundlow) + logical_padding

IF world_w > viewport_w OR world_h > viewport_h:
    use_window_streaming = true

IF frame_animation_reload_tears:
    FRAME_ANIMATION_ENABLED = 0
```

Produzido:

```text
work/reconstructed_viewports/*
work/sgdk_bins/showdown_tiles_4bpp.bin
work/sgdk_bins/showdown_maps_u16.bin
work/sgdk_bins/showdown_palettes_u16.bin
sgdk_viewer streaming runtime
BlastEm screenshot + SRAM
```

Resultado:

```text
camera world preservado;
mas parallax MUGEN ainda achatado;
paleta banded ainda opaca;
budget ainda sem VDP dump.
```

Intervencao humana registrada:

```text
nenhuma intervencao humana nova entre V01 e V02;
decisao guiada pelo contrato DEF de bounds/camera.
```

Proxima sintaxe:

```text
IF curation says "aparece no BlastEm" is not enough:
    add visual/camera/palette contracts
```

---

## Intervencao Humana H01 - 2026-06-13 - Curadoria Reprova

Entrada humana:

```text
"Showdown aparece no BlastEm, mas foi reprovado por curadoria:
 parallax MUGEN achatado em um unico BG_A,
 camera de luta sem contrato,
 paleta opaca apesar da diretriz de cores vibrantes."
```

Decisao causada:

```text
status = rework_required
must_create_contracts = true
must_compare_routes = true
must_not_call_flat_success = true
```

Sintaxe de passagem:

```text
IF human_curation.rejects_visual:
    create camera_motion_contract
    create parallax_layer_contract
    create palette_vitality_report
    create route_decision_record
```

---

## V03 - 2026-06-14 - Contratos + Recuperacao Parcial

Objetivo:

```text
documentar o contrato antes de mexer no codigo
e tentar recuperar cor/camera sem declarar sucesso falso
```

Fluxo:

```text
contracts:
  camera_motion_contract
  parallax_layer_contract
  palette_vitality_report
  route_decision_record
    |
    v
semantic_role_palette_v1
    |
    v
autopan desativado como evidencia
    |
    v
BlastEm
    |
    v
route_b_compare_flat_degraded
```

Sintaxe de decisao:

```text
IF route_a_not_implemented:
    selected_route = "route_b_compare_flat_degraded"
    allowed_label = "lab_flattened_reference"
    closeout = "blocked_rework_required"

IF palette == banded_palette_v1_world:
    replace_with_semantic_roles()
```

Produzido:

```text
doc/contracts/*.json
tools/tests/test_showdown_semantic_palette.py
analysis/showdown_camera_report_v001.json
analysis/showdown_recovery_palette_measurement_v001.json
analysis/showdown_budget_report_v001.json
work/diagnostics/showdown_recovery_comparison_v001.png
```

Resultado:

```text
paleta melhor, camera menos errada, mas ainda flat;
route_a nao implementada;
blocked_rework_required.
```

Intervencao humana registrada:

```text
H01 foi a causa direta desta versao.
```

Proxima sintaxe:

```text
IF user says colors still not vivid AND camera has fight contract:
    strengthen palette anchors
    implement dual_focus_camera
```

---

## Intervencao Humana H02 - 2026-06-14 - Cores e Camera de Luta

Entrada humana:

```text
"as cores ainda nao estao vividas o suficiente
 e prossiga se atentando a gestao de camera"

"O objetivo do sistema de camera e triplo:
 manter os dois lutadores visiveis,
 transmitir profundidade 2D,
 suportar Super Jumps."
```

Decisao causada:

```text
camera_model = dual_focus_midpoint
vertical_model = dead_zone + verticalfollow
depth_model = parallax_bands + water_line_scroll
palette_model = vivid_role_anchors
```

Sintaxe de passagem:

```text
camera_x = midpoint(p1.x, p2.x) - viewport_w / 2
camera_y = floor_locked

IF airborne_delta > deadzone:
    camera_y -= (airborne_delta - deadzone) * verticalfollow

IF screen_y in water_band:
    hscroll += line_depth_offset(screen_y)
```

---

## V04 - 2026-06-14 - Foco Duplo + Paleta Viva + Line Scroll Parcial

Objetivo:

```text
trocar camera de explorador por fixture de luta
e deixar a paleta mais viva sem fingir multi-plano real
```

Fluxo:

```text
semantic palette anchors
    |
    v
virtual fighters:
  p1 = x314,y471
  p2 = x454,y471
    |
    v
camera follows midpoint
    |
    v
super jump -> vertical deadzone -> verticalfollow 1/2
    |
    v
single BG_A with row multicamera bands
    |
    v
BlastEm evidence
```

Sintaxe de decisao:

```text
IF input == LEFT/RIGHT:
    move_p1_or_p2()

IF input == A:
    p1_super_jump()

IF input == B:
    p2_super_jump()

IF route still single_plane:
    route_status = "route_b_compare_flat_degraded"
    closeout = "blocked_rework_required"
```

Produzido:

```text
tools/tests/test_showdown_fight_camera.py
camera dual-focus no scene_demo.c
line scroll parcial em BG_A
analysis/showdown_vdp_contract_audit_v001.json
ROM SHA256 80b91d...
```

Resultado:

```text
camera de luta fixture implementada;
line scroll parcial implementado;
paleta mais viva, mas ainda flat;
route_a ainda pendente.
```

Intervencao humana registrada:

```text
H02 foi a causa direta desta versao.
```

Proxima sintaxe:

```text
IF human points color scrambling / index anchoring / tile cost:
    audit palette indices
    compare route_a vs route_b
    implement real BG_B/BG_A split if budget can fit
```

---

## Intervencao Humana H03 - 2026-06-15 - Diagnostico de Cor/Indices/Tiles

Entrada humana:

```text
"Na janela BlastEm o cenario sofreu degradacao severa de cor..."
"forcar quantizacao hard-coded"
"injetar cabecalho de ancoragem"
"varredura de redundancia e flags"
"declaracao dinamica no SGDK"
```

Interpretacao tecnica aplicada:

```text
o problema visivel ja aparecia no export preview,
logo a cor precisava ser corrigida no pipeline/exportador,
nao tratada como azar do emulador.
```

Decisao causada:

```text
route_a must be attempted for real
fallback can exist only as lab_flattened_reference
palette must be contextual, not banded blind
tile budget must be measured before claiming success
```

Sintaxe de passagem:

```text
IF export_preview is degraded:
    fix exporter first

IF route_a_preview_good AND route_a_budget_too_high:
    reduce far_plane_detail
    cull BG_B behind opaque BG_A

IF cache_fits_before_0xC000:
    implement runtime_BG_B_BG_A()
```

---

## V05 - 2026-06-15 - Route A Multi-Plano Vista no BlastEm

Objetivo:

```text
preservar profundidade real no Mega Drive
sem chamar fallback flat de sucesso artistico
```

Fluxo:

```text
debug layers:
  BG0 -> BG_B
  BG1/BG2/BG3 -> BG_A overlay
    |
    v
manual contextual MD palettes:
  sky/buildings
  vegetation
  water/reflections
  rocks/floor
    |
    v
route_a preview
    |
    +-- if max window unique too high -> simplify BG_B
    |
    +-- if still too high -> cull BG_B under opaque BG_A
    |
    v
cache = 1190 tiles
tile VRAM end = 38592
first tilemap = 49152
    |
    v
runtime SGDK:
  BG_B map window
  BG_A map window
  shared cache
  explicit VRAM layout
  batched tile upload
    |
    v
build SGDK
    |
    v
BlastEm screenshot + SRAM
```

Sintaxe de decisao:

```text
maps_bin layout:
    frame_0: BG_B[96*60] + BG_A[96*60]
    frame_1: BG_B[96*60] + BG_A[96*60]
    ...

custom_map_word:
    bits  0..11 = global_tile_id
    bit      12 = hflip
    bit      13 = vflip
    bits 14..15 = palette_id

runtime:
    stream BG_A first
    mark tile opaque if all nibbles != 0
    stream BG_B second

IF BG_A_cell_is_opaque:
    BG_B_cell = blank_tile
ELSE:
    BG_B_cell = far_plane_tile

IF cache_capacity * 32 + TILE_USER_INDEX*32 < 0xC000:
    vram_layout_status = pass
ELSE:
    route_a_budget = blocked
```

Camera sintaxe:

```text
p1_start = (314, 471)
p2_start = (454, 471)
floor_anchor_screen_y = 215
camera_default = (224, 256)

focus_x = (p1.x + p2.x) / 2
target_x = clamp(focus_x - 160, 0, 448)

highest_y = min(p1.y, p2.y)
airborne_delta = floor_y - highest_y

IF airborne_delta <= 100:
    target_y = 256
ELSE:
    target_y = 256 - ((airborne_delta - 100) / 2)
```

Parallax sintaxe:

```text
BG_B:
    x_delta = 43/100
    y_delta = 285/1000

BG_A upper/mid:
    x_delta = 71/100
    y_delta = 635/1000

BG_A floor:
    x_delta = 1/1
    y_delta = 1/1

water band:
    y = 88..176
    hscroll += depth_gradient(line_y)
```

Produzido:

```text
tools/sgdk_export/export_showdown_bins.py
sgdk_viewer/showdown_viewer/src/scenes/scene_demo.c
work/sgdk_bins/showdown_*.bin
analysis/showdown_vdp_contract_audit_v001.json
analysis/showdown_camera_report_v001.json
analysis/showdown_recovery_palette_measurement_v001.json
analysis/showdown_budget_report_v001.json
work/diagnostics/showdown_recovery_comparison_v001.png
doc/contracts/*.json
```

Resultado:

```text
route_a_multi_plane = implementada
BlastEm screenshot = presente
SRAM = presente
visual_vdp_dump.bin = ausente
validado_budget = false
ready_for_aaa = false
```

Intervencao humana registrada:

```text
H03 foi a causa direta desta versao.
O pedido humano "prossiga" autorizou continuar a execucao
sem trocar o escopo do estudo.
```

Proxima sintaxe:

```text
IF next_version_requested:
    add VLAB/visual_vdp_dump runtime block
    capture moving-camera parallax evidence
    validate foreground priority against fighter sprites
    keep status below AAA until all gates pass
```

---

## Linha de Decisao Compacta

```text
V00 visible_in_blastem
  -> NOT enough

V01 anti_magenta
  -> fixes matte, not palette/depth

V02 full_world_streaming
  -> fixes camera extent, not MUGEN parallax

H01 human curation rejects flat/palette/camera
  -> contracts required

V03 semantic palette + contracts
  -> still flat

H02 human demands vivid colors + fight camera
  -> dual focus + super jump + water line scroll

V04 camera fixture + line scroll fallback
  -> still route_b

H03 human diagnoses color/tile/index route
  -> real route_a attempt

V05 BG_B + BG_A + culling + BlastEm evidence
  -> visually reworked, budget dump pending
```

## Regra de Continuidade

```text
Ao encontrar intervencao humana:
    registrar texto/intent
    registrar decisao que ela causou
    fechar a versao atual com status honesto
    abrir a sintaxe da proxima versao

Nunca pular direto para "pronto".
```
