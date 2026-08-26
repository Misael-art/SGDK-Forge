# Changelog - MUGEN SFF Showdown Study

## 2026-06-15 - Route A multi-plano vista no BlastEm

- Supersede a rodada `route_b_compare_flat_degraded` de 2026-06-14.
- Exportador SGDK atualizado para `route_a_multi_plane_streaming_context_palette_v2`:
  - `BG_B` carrega o plano distante com simplificacao controlada de VRAM;
  - `BG_A` carrega midground, agua/reflexos, rochas e floor anchor;
  - mapa custom agora grava, por frame, `BG_B` seguido de `BG_A`;
  - janela de streaming reduzida para 41x29 tiles;
  - culling de `BG_B` sob tiles totalmente opacos de `BG_A`.
- Bins regenerados e sincronizados com o viewer:
  - `showdown_tiles_4bpp.bin`: `2870` tiles unicos;
  - `showdown_maps_u16.bin`: `92160` bytes;
  - `showdown_palettes_u16.bin`: `128` bytes;
  - `nearest_color_remaps`: `235880`.
- Runtime SGDK alterado:
  - dois mapas de janela (`BG_B` e `BG_A`);
  - cache compartilhado de `1190` tiles;
  - layout VDP explicito: tile data ate `38592`, primeiro tilemap em `49152`;
  - upload de tiles em lotes pequenos para evitar travamento inicial;
  - `BG_B` far delta `43/100,285/1000`;
  - `BG_A` mid/floor delta `71/100,635/1000` e `1/1`;
  - `HSCROLL_LINE` em ambos os planos, com distorcao de agua em `BG_A`.
- Camera SGDK preservada como fixture de luta:
  - P1/P2 virtuais em world x `314`/`454`, floor y `471`;
  - camera X segue ponto medio;
  - camera Y usa zona morta e `verticalfollow=1/2` para super jump;
  - autopan livre continua desativado como evidencia.
- Build direto SGDK 2.11 debug passou; ROM `sgdk_viewer/showdown_viewer/out/rom.bin`, SHA256 `7e4f6a2e2149ff19b9788ffd3034adb556d595e1163b6af8c575ff09533ece2a`.
- BlastEm evidence passou com screenshot e SRAM:
  - `sgdk_viewer/showdown_viewer/out/evidence/blastem/screenshot.png`;
  - `sgdk_viewer/showdown_viewer/out/evidence/blastem/save.sram`;
  - `sgdk_viewer/showdown_viewer/out/logs/blastem_evidence.json`;
  - readiness source `post_close_sram_heartbeat`.
- `visual_vdp_dump.bin` continua ausente; portanto `validado_budget=false`.
- Auditoria binaria/VDP: `analysis/showdown_vdp_contract_audit_v001.json` com `status=pass`, `diff_pixels=0`, CRAM valida, tiles 4bpp validos, cache `1190`, max local tile index `1205`.
- Relatorios regenerados: camera, paleta, budget e board `work/diagnostics/showdown_recovery_comparison_v001.png`.
- Adicionado fluxo pedagogico ASCII `doc/showdown_recovery_ascii_decision_flow.md`, cobrindo V00..V05, intervencoes humanas H01..H03, sintaxe de decisao e passagem para a proxima versao.
- Testes Python: `22 passed`.
- Validacoes:
  - `validate_project_context`: ok, `context=exercise`, `blockers=0`;
  - `validate_project_methodology`: passed, `blockers=0`;
  - `validate_project_hygiene`: blocked, `blockers=3`;
  - `validate_resources -WorkDir` no estudo: failed, `errors=8`, `warnings=5`;
  - `validate_resources -WorkDir` no viewer: failed, `errors=1`, `warnings=10`;
  - `audit_project_learning -Mode Capture`: `lessons=13`, `candidates=9`, `canonical_promotion_performed=false`.
- Status honesto: `route_a_runtime_reworked_emulator_seen_budget_dump_pending`, nao AAA, nao asset autoral final, nao `validado_budget`.

## 2026-06-14 - Follow-up paleta viva, camera foco duplo e line scroll parcial

- Supersede a tentativa de recovery anterior de 2026-06-14 para o build observado mais recente.
- Paleta reforcada: `semantic_role_palette_v1` agora prioriza anchors cromaticos vivos por papel visual antes das cores mais frequentes da fonte.
- Metricas atuais de paleta:
  - source: `76` cores uteis, saturacao media `0.3805`;
  - export preview: `42` cores uteis, saturacao media `0.5185`, distancia RGB media `33.7969`;
  - BlastEm normalizado: saturacao media `0.4638`, distancia RGB media `72.4376`, `62.1275%` dos pixels acima de distancia 40.
- Testes adicionados/atualizados:
  - `tools/tests/test_showdown_semantic_palette.py`;
  - `tools/tests/test_showdown_fight_camera.py`;
  - suite Python: `22 passed`.
- Camera SGDK alterada para fixture de luta com foco duplo:
  - P1/P2 virtuais iniciam em world x `314`/`454`, floor y `471`;
  - camera X segue o ponto medio;
  - camera Y fica travada no chao ate a zona morta vertical e aplica `verticalfollow=1/2` no super jump;
  - entrada fria ao abrir a cena evita que o A do menu acione salto na evidencia inicial.
- Adicionada reparacao parcial de profundidade dentro do fallback:
  - `BG_A` usa `HSCROLL_LINE`;
  - linhas distantes usam delta `43/100`, midground `71/100`, floor `1/1`;
  - agua usa offset horizontal por linha entre y `88..176`.
- Regerados e sincronizados bins SGDK:
  - `showdown_tiles_4bpp.bin`: `2244` tiles unicos;
  - `showdown_maps_u16.bin`: `46080` bytes;
  - `showdown_palettes_u16.bin`: `128` bytes;
  - `nearest_color_remaps`: `390536`.
- Adicionada auditoria binaria `analysis/showdown_vdp_contract_audit_v001.json`: CRAM explicita, nibbles 0..15, descritor custom 12-bit, palette ids por celula e roundtrip do preview com `diff_pixels=0`.
- Build canonico via wrapper continua bloqueado antes da compilacao porque o Python de sistema do asset preparation nao possui `PIL`; build direto debug SGDK 2.11 foi usado apenas como evidencia de laboratorio.
- ROM observada no BlastEm: `sgdk_viewer/showdown_viewer/out/rom.bin`, SHA256 `80b91d451261a38b2db115eaa0f2558328bcd25f5dc03e0b89131bd093ffcd80`.
- Evidencia BlastEm atual:
  - screenshot `sgdk_viewer/showdown_viewer/out/evidence/blastem/screenshot.png`;
  - SRAM presente;
  - report `sgdk_viewer/showdown_viewer/out/logs/blastem_evidence.json`;
  - `visual_vdp_dump.bin` ausente.
- Gerados/atualizados: `analysis/showdown_camera_report_v001.json`, `analysis/showdown_recovery_palette_measurement_v001.json`, `analysis/showdown_budget_report_v001.json`, `work/diagnostics/showdown_recovery_comparison_v001.png`.
- Validacoes finais desta rodada:
  - `validate_project_context`: ok, `context=exercise`, `blockers=0`;
  - `validate_project_methodology`: passed, `blockers=0`;
  - `validate_project_hygiene`: blocked, `blockers=3`;
  - `freshness_audit`: warning, `stale=0`, `missing_required=2`;
  - `validate_resources -WorkDir`: failed, `errors=8`, `warnings=5`;
  - `audit_project_learning -Mode Capture`: `lessons=13`, `candidates=9`, `canonical_promotion_performed=false`.
- Resultado de rota: continua `route_b_compare_flat_degraded`, agora como `lab_flattened_reference_with_camera_palette_line_scroll_repair`; `route_a_multi_plane` ainda nao foi implementada. A auditoria de descritor passou, mas a perda cromatica perceptiva ainda bloqueia aprovacao artistica.
- Status final desta rodada: `blocked_rework_required`, `validado_budget=false`, `ready_for_aaa=false`.

## 2026-06-14 - Recovery parcial camera/paleta, parallax ainda bloqueado

- Criados/atualizados contratos de recovery:
  - `doc/contracts/camera_motion_contract_v001.json`;
  - `doc/contracts/parallax_layer_contract_v001.json`;
  - `doc/contracts/palette_vitality_report_v001.json`;
  - `doc/contracts/showdown_route_decision_record_v001.json`.
- Substituida a exportacao `banded_palette_v1_world` por `semantic_role_palette_v1`, separando papeis visuais de ceu/predios, vegetacao, agua/reflexos e rochas/chao.
- Adicionado teste `tools/tests/test_showdown_semantic_palette.py`; suite Python do estudo passou com `11 passed`.
- Regerados bins SGDK:
  - `showdown_tiles_4bpp.bin`: `2242` tiles unicos;
  - `showdown_maps_u16.bin`: `46080` bytes;
  - `showdown_palettes_u16.bin`: `128` bytes;
  - `nearest_color_remaps`: `149137`.
- Atualizado o viewer SGDK para desativar autopan como evidencia de camera e alinhar constantes de cache/tile com o novo export.
- Build canonico via wrapper falhou antes da compilacao porque o Python de sistema usado pelo asset preparation nao possui `PIL`; build direto debug SGDK 2.11 foi usado apenas como evidencia de laboratorio.
- ROM observada: `sgdk_viewer/showdown_viewer/out/rom.bin`, SHA256 `535cac333cea8d3410a36fa054b9cc7188d43246f7cfef447b387cb993060564`, `262144` bytes.
- Capturada evidencia BlastEm atual:
  - screenshot `sgdk_viewer/showdown_viewer/out/evidence/blastem/screenshot.png`;
  - SRAM `sgdk_viewer/showdown_viewer/out/evidence/blastem/save.sram`;
  - report `sgdk_viewer/showdown_viewer/out/logs/blastem_evidence.json`;
  - session log `sgdk_viewer/showdown_viewer/out/evidence/blastem/evidence_session_20260614_062303_2883de4b.log`.
- Evidencia incompleta: `visual_vdp_dump.bin` ausente; `session_manifest.json` agregado permaneceu stale de 2026-06-08, embora o log JSONL atual e `blastem_evidence.json` registrem a nova captura.
- Gerados relatórios:
  - comparacao lado a lado `work/diagnostics/showdown_recovery_comparison_v001.png`;
  - camera `analysis/showdown_camera_report_v001.json`;
  - paleta `analysis/showdown_recovery_palette_measurement_v001.json`;
  - budget `analysis/showdown_budget_report_v001.json`.
- Resultado visual: paleta mais viva, mas BlastEm ainda mostra artefato de borda direita; source/blastem normalizado tem distancia RGB media `68.2465` e `49.8549%` dos pixels acima de distancia 40.
- Resultado de rota: `route_a_multi_plane` permanece nao implementada; ROM atual e `route_b_compare_flat_degraded` com reparos de camera/paleta, portanto `lab_flattened_reference`.
- Status final desta tentativa: `blocked_rework_required`, `validado_budget=false`, `ready_for_aaa=false`.

## 2026-06-13 - Curadoria camera/paleta reprovada

- Classificado o root do estudo como `exercise` em `doc/project_context_manifest.json`.
- Atualizado `doc/00-project-brief.md` para refletir o escopo real: treino controlado de conversao MUGEN SFF/DEF, nao entrega AAA.
- Atualizado `doc/project_methodology_manifest.json` para declarar `project_context` entre as validacoes obrigatorias.
- Criado `doc/showdown_camera_palette_curation_2026-06-13.md` com a avaliacao formal.
- Decisao visual: `rework_required`.
- Principais blockers:
  - `flattened_mugen_parallax`: deltas BG0/BG1/BG2/BG3 foram achatados em um unico `BG_A`;
  - `fighting_stage_camera_contract_missing`: camera de laboratorio/autopan nao preserva zoffset, verticalfollow e foco de palco de luta;
  - `palette_vibrancy_lost`: `banded_palette_v1_world` gerou `187569` nearest-color remaps e reduziu o viewport de 76 para 26 cores uteis;
  - `visual_gate_too_narrow`: gate atual mede matte/magenta, mas nao mede composicao, vitalidade cromatica ou fidelidade perceptiva;
  - `nested_lab_art_not_detected`: `art_diagnostic.py` no root retorna `3_no_art` para um estudo com arte em `work/`, `analysis/`, `evidence/` e viewer aninhado.
- Validacoes da curadoria:
  - `validate_project_context`: passed, `context=exercise`, `blockers=0`;
  - `validate_project_methodology`: passed, `blockers=0`;
  - `validate_project_hygiene`: blocked, `blockers=3`;
  - `freshness_audit`: warning, `stale=2`, `missing_required=2`;
  - `validate_resources`: failed, `errors=8`, `warnings=6`, `checked=0`;
  - `audit_project_learning` via Python embutido: `lessons=13`, `candidates=9`, `canonical_promotion_performed=false`.
- Status permanece `controlled_training_area`, `lab_not_delivery=true`, `ready_for_aaa=false`, `validado_budget=false`.

## 2026-07-19 - Discovery de arte laboratorial corrigido

- Atualizado `doc/art_diagnostic_report.json` com o cenario
  `4_lab_nested_art_review`, substituindo o falso `3_no_art`.
- Inventariados separadamente 9 fontes, 3 evidencias, 5 recursos ativos e 73
  imagens de trabalho; o viewer `sgdk_viewer/showdown_viewer` foi identificado
  com hygiene manifest local.
- O discovery nao segue symlinks nem diretorios externos e o teste de
  regressao do pipeline passou 46/46.
- Esta mudanca corrige apenas classificacao e roteamento de arte. O estudo
  permanece `controlled_training_area`, `lab_not_delivery=true`,
  `ready_for_aaa=false` e `validado_budget=false`.

## 2026-06-08 - Full-world camera streaming fixture

- Corrected the stage contract from 320x224 output to the full MUGEN camera world:
  - `boundleft=-224`, `boundright=224`, `boundhigh=-240`, `boundlow=0`;
  - reconstructed world `768x480` px, `96x60` tiles;
  - viewer viewport remains `320x224` px with camera scroll bounds `x=0..448`, `y=0..256`.
- Updated DEF parsing to carry camera bounds and `verticalfollow`, and expanded the visual gate to validate declared world dimensions.
- Rebuilt the pipeline so `work/reconstructed_layers/frame_0000.png` through `frame_0003.png` are full-world 768x480 frames; no downscale/crop is used for the source conversion.
- Generated viewport previews under `work/reconstructed_viewports/` for default/start and world corners.
- Re-exported SGDK bins as custom streaming resources:
  - `showdown_tiles_4bpp.bin`: 2253 global ROM tiles;
  - `showdown_maps_u16.bin`: 96x60 maps for 4 frames using custom map words;
  - `showdown_palettes_u16.bin`: four banded sub-palettes.
- Updated tile reports:
  - raw tiles `23040`;
  - unique global tiles `2253`;
  - dedup saving ratio `0.902214`;
  - H/V/HV flip matches `5/12/4`;
  - lossy tile merge disabled.
- Reworked the SGDK viewer from full-resident 40x28 loading to a streamed 42x30 camera window. The camera supports D-pad movement and delayed autopan across the full 768x480 world.
- Added a RAM staging buffer and batch tile upload to reduce visible tile-stream tearing during evidence capture.
- Disabled automatic frame animation in the viewer (`FRAME_ANIMATION_ENABLED=0`) after evidence showed large per-frame tile-cache reloads could tear the image. The four reconstructed frames remain in the export/report surface for later curation.
- Built final ROM `sgdk_viewer/showdown_viewer/out/rom.bin` with SHA256 `4b0ce91f5e370a8d6fd4e842a511c7f6c2e52a8f49ee4f2419696c972305fe2e`.
- Captured final BlastEm evidence:
  - screenshot `evidence/blastem_showdown_screenshot.png`;
  - SRAM `evidence/blastem_showdown_save.sram`;
  - session manifest `evidence/blastem_session_manifest.json`;
  - matte check `evidence/blastem_screenshot_visual_check.json` with `bad_ratio=0.0`.
- Gate state:
  - Python tests: 8 passed;
  - `res_graph_audit.ps1`: `warn`, code-loaded tile budget unmeasured;
  - viewer `freshness_audit.ps1`: `warning`, `stale=2`, `missing_required=2`;
  - root `freshness_audit.ps1`: `warning`, `stale=1`, `missing_required=2`;
  - `validate_resources.ps1`: failed with 1 error and 11 warnings, expected for lab because VDP tile streaming lacks dump/telemetry and canonical closeout schemas are not delivery-clean.
- Status remains `controlled_training_area`, `lab_not_delivery=true`, `ready_for_aaa=false`, `validado_budget=false`.

## 2026-06-07 - Root fixture consolidation

- Audited `tools/mugen2sgdk` before continuing local automation.
- Kept the study parser/exporter local because no reproducible CLI output was found for the existing packaged tool.
- Regenerated reconstruction/export reports with relative paths.
- Added measured reports for tilemap conversion, tilemap flags, palette violations and per-tile palette conflicts.
- Added root memory bank, technique manifest, learning ledger and viewer aggregate manifest.
- Updated SGDK viewer flow to boot directly into the Showdown viewer instead of the generic branding/template path.
- Built `sgdk_viewer/showdown_viewer/out/rom.bin` via direct SGDK 2.11 debug make after wrapper validation blocked the normal build path.
- Captured initial BlastEm evidence for ROM SHA256 `3fe934583099d632b2407a46dadc43571dbf246eb8634a5348dbcf6fe656a3e1`; this was later superseded by the anti-magenta rebuild below.
- Copied root evidence to `evidence/blastem_showdown_screenshot.png`, `evidence/blastem_showdown_save.sram` and `evidence/blastem_evidence.json`.
- Recorded the initial visual/budget limits before the reconstruction fix: Showdown was visible in BlastEm, but magenta matte/background remained, VDP dump was absent and `validado_budget=false`.
- Regenerated `tilemap_flag_report.json` in the canonical schema with 4480 measured entries.
- Final gate state for the initial consolidation pass was superseded by the later validation below.
- Status remains `controlled_training_area`, `lab_not_delivery=true`, `ready_for_aaa=false`.

## 2026-06-07 - Logical reconstruction anti-magenta fix

- Fixed the MUGEN reconstruction pipeline before SGDK export:
  - parses `start`, `delta`, `tile`, `zoffset` and camera start from `showdown.def`;
  - composes `[BG x]` sections in DEF order;
  - uses SFF sprite axes for x/y placement, capped to the 240 px MUGEN logical canvas on Y;
  - converts PCX palette index 0 to alpha for `mask=1`;
  - infers alpha for unmistakable magenta index 0 mattes in animation frames and records `mask_source=inferred_chroma_key_index0`.
- Added `mugen_sff/visual_gate.py` and wired it into reconstruction/export. `frame_0000.png` now fails the pipeline if matte/magenta/transparent pixels exceed 5%.
- Regenerated reconstructed frames; current `frame_0000.png` has `bad_ratio=0.0`.
- Reworked SGDK export to `banded_palette_v1` to prevent slot-0 holes after palette fitting. Palette status is `pass_with_degradation`, with 15623 nearest-color remaps.
- Updated viewer runtime to load 895 unique tiles and stopped overwriting `PAL3` with a debug text palette.
- Rebuilt and recaptured BlastEm evidence for ROM SHA256 `69cffe7b834699d0313c8896d849f69272d91d5400f52bfbf5132a1322a51556`.
- Final gate state after technique-manifest cleanup: `freshness_audit.ps1` warning (`stale=2`, `missing_required=2`) and `validate_resources.ps1` failed with 1 error / 8 warnings. The remaining hard error is `code_loaded_tiles_unmeasured`.
- Remaining status: stage appears without catastrophic magenta; palette banding/degradation remains a curation target; `validado_budget=false`, `ready_for_aaa=false`.
