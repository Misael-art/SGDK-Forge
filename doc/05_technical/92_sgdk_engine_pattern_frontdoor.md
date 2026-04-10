# 92 - SGDK Engine Pattern Front Door

Status: `front_door / canonical classification layer`

---

## Objetivo

Resolver a lacuna do "pass 1" ausente sem reconstruir historia artificial.

Este documento e o ponto de entrada canonico para a pesquisa de `SGDK_Engines`:

- o appendix em [99_sgdk_engines_scan_appendix.md](F:/Projects/MegaDrive_DEV/doc/05_technical/99_sgdk_engines_scan_appendix.md) continua preservado
- o registry machine-readable em [92_sgdk_engine_pattern_registry.json](F:/Projects/MegaDrive_DEV/doc/05_technical/92_sgdk_engine_pattern_registry.json) vira a fonte automatizavel
- este arquivo define classificacao, peso e leitura correta dos resultados

## Regras de leitura

- `verified_example`
  - exemplo forte e real, mas ainda tratado como referencia observada
- `interpreted_pattern`
  - ha sinal real no engine, mas o resumo do appendix ja faz compressao conceitual
- `candidate_for_canon`
  - padrao validado, promissor e elegivel para virar skill/lib_case depois de reproducao
- `blocked_pending_repro`
  - util, mas perigoso ou especifico demais para promover sem prova isolada

Regra importante:

- o appendix usa varios `idiom summaries`
- esses resumos sao validos como leitura tecnica, mas nao devem ser confundidos com citacao literal do codigo

## Mapa de classificacao

| Family ID | Status | Dominio | Skill alvo | Nota |
|---|---|---|---|---|
| `lizardrive_hint_fx_family` | `candidate_for_canon` | FX / raster | `sgdk-runtime-coder` | inclui `wobble`, `scaling`, `spotlight` e `linescroll` como familia-base de H-Int |
| `sonic_camera_streaming_family` | `candidate_for_canon` | camera / mapa | `sgdk-runtime-coder` | inclui camera com deadzone, parallax por bit-shift e streaming manual de tilemap |
| `sonic_hud_physics_family` | `candidate_for_canon` | HUD / feel | `sprite-animation`, `sgdk-runtime-coder` | inclui HUD por frame manual e desaceleracao multi-taxa |
| `platformer_feel_family` | `candidate_for_canon` | gameplay feel | `sgdk-runtime-coder` | inclui `coyote`, `jump buffer`, `half-jump cancel` e tolerancia de one-way |
| `platformer_camera_math_family` | `verified_example` | camera / collision math | `sgdk-runtime-coder` | inclui deadzone AABB e helpers por shift para tiles 16x16 |
| `tsk_multitasking_api` | `verified_example` | scheduler | `sgdk-runtime-coder` | referencia oficial de `TSK_userSet`, `TSK_superPend`, `TSK_superPost` |
| `benchmark_runtime_diagnostics` | `verified_example` | diagnostico | `sgdk-runtime-coder` | forma recomendada de strip diagnostico e leitura de memoria/DMA |
| `mega_metroid_slope_collision` | `candidate_for_canon` | collision | `sgdk-runtime-coder` | slope por gradiente de coluna com clamp e aderencia ao piso |
| `nexzr_runtime_patterns` | `candidate_for_canon` | entity / starfield / font | `sgdk-runtime-coder` | inclui entity manager minimalista, sprite chains de star warp e font por tile-index math |
| `megadriving_pseudo3d_stack` | `candidate_for_canon` | pseudo-3D | `sgdk-runtime-coder`, `megadrive-vdp-budget-analyst` | inclui ZMAP, curves, hills e color banding |
| `tile_cache_streaming_refcount` | `candidate_for_canon` | streaming / VRAM | `sgdk-runtime-coder`, `megadrive-vdp-budget-analyst` | forte candidato para mapas maiores que a VRAM |
| `window_plane_lifebar` | `candidate_for_canon` | HUD | `sgdk-runtime-coder` | barra em `WINDOW` com tiles graduais e remainder logic |
| `tidytext_variable_width` | `candidate_for_canon` | texto | `sgdk-runtime-coder` | principal candidato do scan para canonizacao imediata |
| `tile_text_stream_renderer` | `candidate_for_canon` | texto | `sgdk-runtime-coder` | streaming renderer com ring buffer e escape codes |
| `packed_multilingual_script_pool` | `interpreted_pattern` | script / localizacao | `sgdk-runtime-coder` | padrao promissor, mas ainda dependente do renderer escolhido |
| `axis_slide_collision` | `verified_example` | collision | `sgdk-runtime-coder` | boa referencia de RPG top-down com slide por eixo |
| `bitmap_palette_masking_family` | `interpreted_pattern` | bitmap / trick rendering | `sgdk-runtime-coder`, `megadrive-vdp-budget-analyst` | inclui BMP nibble fill, 2-color framebuffer e mask transitions |
| `raycasting_renderer_family` | `blocked_pending_repro` | 3D / raster / DMA | `sgdk-runtime-coder`, `megadrive-vdp-budget-analyst` | inclui column tiles, split de paleta, DMA flush em ASM e otimizações frágeis |
| `trig_lookup_and_atan2` | `candidate_for_canon` | math / projectile | `sgdk-runtime-coder` | forte referencia para projeteis, homing e dash angular |

## Fila inicial de promocao

Esta e a fila operacional inicial, alinhada ao appendix e ajustada pela auditoria:

1. `tidytext_variable_width`
2. `megadriving_pseudo3d_stack`
3. `tile_cache_streaming_refcount`
4. `lizardrive_hint_fx_family`
5. `platformer_feel_family`
6. `sonic_hud_physics_family`
7. `nexzr_runtime_patterns`
8. `window_plane_lifebar`
9. `mega_metroid_slope_collision`
10. `trig_lookup_and_atan2`

## Regras de promocao

Um padrao so sobe de `candidate_for_canon` para canon quando tiver:

- referencia exata em engine
- descricao limpa, sem inflacao interpretativa
- `lib_case` reproduzivel
- skill alvo declarada
- gate humano explicito

Padrao `blocked_pending_repro` nao sobe por inercia.

## Spot audit fechado nesta passada

A auditoria manual confirmou diretamente, no codigo fonte real, pelo menos estes grupos:

- `lizardrive_hint_fx_family`
- `sonic_camera_streaming_family`
- `platformer_feel_family`
- `tsk_multitasking_api`
- `mega_metroid_slope_collision`
- `nexzr_runtime_patterns`
- `megadriving_pseudo3d_stack`
- `tile_cache_streaming_refcount`
- `tidytext_variable_width`
- `tile_text_stream_renderer`
- `raycasting_renderer_family`
- `trig_lookup_and_atan2`

Isso torna a pesquisa `validada`, mas ainda nao `canonizada`.
