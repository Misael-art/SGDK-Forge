<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `validation_report.json`
- Ultima sincronizacao: `2026-06-09T05:42:31.8233731-03:00`
- Changelog canonico: `doc/changelog/changelog.md`
- Assets versionados rastreados: 6
- Ultimo build versionado: build_v004
- ROM vigente: `764d5a95c5c6aa979905afaeba417c6225b0547299537bb27228c4c85a9b34da` (`131072` bytes)
- Validation summary: errors=0 warnings=11
- Blockers vigentes: project_methodology_manifest_invalid, gdd_substantial_insufficient, visual_gate_blocked, animation_gate_failed, emulator_evidence_stale, scene_tilemap_conversion_report_missing, tilemap_flag_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing, model_sheet_to_sprite_fidelity_failed
- Evidencia de emulador: session_not_captured
- Gate visual: visual_lab_aprovado=False
- Gate gameplay: gameplay_rom_aprovada=False
- Gate AAA: ready_for_aaa=False
- QA runtime: gameplay=nao_testado performance=nao_testado audio=nao_testado hardware_real=nao_testado
<!-- SGDK GENERATED STATUS END -->
## 2026-06-07 - Retomada v002 HYBRIDO MUAY THAI

- Placeholder v001 reclassificado como `technical_lab_asset`, `procedural_renderer`, `not_final_art`.
- Fonte IA registrada como concept/source candidate em `data/raw_ai/hibrido_fighter_v002/` e `data/source_art/hibrido_fighter_v002/`; nao e runtime asset direto.
- Novo builder: `data/builders/build_hibrido_fighter_assets_v002.py`.
- Novos strips runtime: `idle`, `walk_step`, `teep`, body em PAL2 e FX em PAL3.
- Viewer SGDK atualizado para alternar apenas as tres acoes v002.
- Build v002 gerou `out/rom.bin` sha256 `246b33725b479402cccf41cd28a1be79f6687c4524af0dbd74b4062021a978bc`.
- BlastEm executou a ROM e gerou screenshot/SRAM em `out/evidence/blastem/`; captura canonica ficou parcial por bug no script `capture_blastem_evidence.ps1`.
- Status honesto: `runtime_funcional=true`, `visual_aprovado=false`, `ready_for_aaa=false`, `lab_not_delivery=true`.

## 2026-06-07 - Reprovacao visual humana v002

- Decisao humana: trabalho visual v002 reprovado.
- Classificacao atual: `hibrido_fighter_runtime_v002=placeholder_rejected_visual_translation`.
- Falha anatomica: Pose 3 do source/model sheet apresenta leitura de tres bracos por duplicacao/sobreposicao de braco com faixa.
- Falha de acting: idle, knee e teep/kick mantem a mesma expressao fria; nao ha tensao de mandibula, dentes/kiai ou olhos estreitos no impacto.
- Falha de fidelidade runtime: em 48x64/BlastEm, olhos, braco de lava, calcao preto/dourado, bandagens e contraste quente nao ficam claramente identificaveis.
- Aprendizado absoluto local: `technical_pass` nao implica `visual_pass`; PNG indexado, PLTE<=16, grid 9-bit, build SGDK e BlastEm provam sintaxe, nao semantica visual.
- Novo gate local: antes de qualquer conversao final, source/model sheet deve passar por input gatekeeper de anatomia, articulacoes, extremidades, acting facial e eye tracking.
- Proibicao reforcada: downscale direto ou quantizacao global de concept high-res para 48x64 nao e sprite final; e preciso redraw/cleanup em clusters pixel art nativos.
- Evidencias/relatorios:
  - `out/logs/hibrido_v002_visual_rejection_report.json`
  - `out/logs/hibrido_v002_input_gatekeeper_report.json`
  - `out/logs/hibrido_v002_runtime_fidelity_report.json`
  - `doc/03_art/02_visual_feedback_bank.md`
- Curadoria canonica aplicada por instrucao humana explicita:
  - `tools/sgdk_wrapper/.agent/skills/art/visual-excellence-standards/SKILL.md`
  - `tools/sgdk_wrapper/.agent/skills/art/art-translation-to-vdp/SKILL.md`
  - `tools/sgdk_wrapper/.agent/skills/art/megadrive-pixel-strict-rules/SKILL.md`
  - `tools/sgdk_wrapper/.agent/references/learning_owner_catalog.json`

## 2026-06-07 - Novo source candidate v003 para validacao humana

- Nova arte IA gerada como `source_candidate_pending_human_validation`.
- Caminho: `data/source_art/hibrido_fighter_v003/source_concept.png`.
- SHA256: `191c56940722bc8531eea30dec5f1ac46ed6821171f2d80d7b111af398cd3381`.
- Precheck do agente: sem anomalia grosseira de terceiro braco observada; acting facial melhorado em knee/teep; materiais mais claros no source.
- Status: aguardando validacao humana; nao e runtime art e nao deve sofrer downscale direto.
- Proximo passo se aprovado: lineart/blocking 48x64 nativo, com clusters manuais e PAL2/PAL3 por material.

## 2026-06-07 - Rework v003 e nova candidata v005

- Feedback humano: v003 avancou, mas nao passa como fonte canonica.
- Problemas v003:
  - primeira pose maior que as demais, gerando risco de escala instavel;
  - ausencia de pose de costas;
  - faixa vermelha no biceps do braco nao-lava inconsistente, ausente na primeira pose.
- v003 status: `source_candidate_needs_rework`.
- v004 gerada e preservada como tentativa intermediaria: `superseded_by_v005`.
- v005 gerada como candidata ativa:
  - caminho `data/source_art/hibrido_fighter_v005/source_concept.png`;
  - sha256 `39fe7f890245a735d02f507509cf58734cfe87478d9d9969773043c88175aec7`;
  - inclui front, back, walk/guard, knee, teep e FX;
  - precheck: escala melhor, pose de costas presente, faixa vermelha visivel nas poses, sem terceiro braco obvio.
- Status v005: `source_candidate_pending_human_validation`.
- Aprendizado local: model sheet canonico exige `scale_lock`, `back_pose/turnaround` e `costume_marker_continuity` antes de spritesheet.

## 2026-06-07 - Rework v005 e nova candidata v006 com palette map

- Feedback humano: v005 ainda nao passa por consistencia de adereco/material.
- Problema critico: mao de rocha/lava le com faixa/luva na ultima pose, diferente das poses anteriores.
- Problema de processo: faltava paleta/mapa de cores para orientar producao futura.
- Decisao de design travada:
  - braco/mao lava sempre rocha exposta com rachaduras laranja, sem faixa, sem luva, sem bandagem;
  - mao humana e pes usam faixas brancas sujas;
  - faixa vermelha fica no biceps do braco nao-lava;
  - shorts pretos com detalhes dourados.
- v005 status: `source_candidate_needs_rework`.
- v006 gerada como candidata ativa:
  - caminho `data/source_art/hibrido_fighter_v006/source_concept.png`;
  - sha256 `87246c88d5b2166a55358b18f2fd03d00a82a44d9e10a90cbf48d033dbbc2a69`;
  - status `source_candidate_pending_human_validation`.
- Mapa de cores criado:
  - `doc/contracts/hibrido_fighter_v006_palette_map.json`;
  - `data/processed/reports/hibrido_v006_palette_map.png`.
- Aprendizado local: personagem assimetrico exige `accessory/material lock` por membro e `palette/material map` antes de spritesheet.

## 2026-06-08 - Reprovacao v006 e preparacao v007 bloqueada por tooling

- Feedback humano: v006 reprovado.
- Falha critica: braco de rocha/lava sem mao/punho legivel; isso e falha anatomica de endpoint do membro especial.
- Falha visual/VDP: fonte ainda possui microdetalhe/spray que vira tile-noise e prejudica leitura/custo.
- Regras incorporadas:
  - membro especial exige extremidade legivel em todas as poses aplicaveis;
  - sombras devem usar 2-3 tons bem espacados por clusters;
  - evitar ruido de detalhe, spray e textura miuda;
  - personagem deve ser planejado em 1 paleta de 16 cores, com index 0 transparente;
  - alinhar recortes/poses/celulas pensando em multiplos de 8 px;
  - manter PNG runtime indexed e paleta controlada.
- v006 status: `source_candidate_rejected`.
- v007:
  - fonte visual nao gerada por falha do servico de imagem nativo e bloqueio local `license_blocked`;
  - generation brief: `doc/contracts/hibrido_fighter_v007_generation_brief.md`;
  - palette map single-character: `doc/contracts/hibrido_fighter_v007_palette_map.json`;
  - swatches: `data/processed/reports/hibrido_v007_single_palette_map.png`;
  - attempt report: `out/logs/hibrido_v007_generation_attempt_report.json`.

## 2026-06-08 - Retentativa de geracao v007

- Pedido humano: tentar gerar o model sheet novamente.
- Resultado atualizado: nova imagem v007 gerada no canal nativo do chat apos nova retentativa.
- Source: `data/source_art/hibrido_fighter_v007/source_concept.png`.
- SHA256: `eba6f1c195ff443c9cc426bdc0e2d63c626b1e1ac90015a3f8627c1e87d41735`.
- Status: `source_candidate_pending_human_validation`.
- Precheck do agente:
  - mao/punho do braco lava melhor que v006 nas poses principais;
  - sem terceiro braco obvio;
  - pose de costas presente;
  - cluster shading melhor, mas ainda exige revisao humana por possivel ruido/textura fina;
  - teep ainda requer validacao humana do endpoint da mao lava.
- Gerador nativo: houve falhas de servidor antes da tentativa bem-sucedida.
- Rota local:
  - `imagegen_tool status`: ComfyUI ausente/offline, modelos ausentes, GPU nao detectada/0 VRAM, RAM livre baixa;
  - `imagegen_circuit preflight`: `license_blocked`, host gate falhou, scope concept_art passou.
- Evidencia: `out/logs/hibrido_v007_generation_attempt_report.json`, `out/logs/hibrido_v007_model_sheet_precheck_report.json` e `out/logs/generation_channel_decision.json`.

## 2026-06-09 - v008 com pose 5 corrigida e paleta embutida

- Pedido humano: refazer model sheet com a mao de pedra/lava da quinta pose mais clara, aberta e acima da perna; incluir lista de cores/paleta no proprio model sheet.
- v007 status: `superseded_by_v008`.
- v008 source ativo:
  - `data/source_art/hibrido_fighter_v008/source_concept.png`;
  - sha256 `04e898f74564c7b1e8a00b7b1f2130ea8d4381b51d8ef0b5266545e04464e4ec`.
- Source bruto preservado:
  - `data/source_art/hibrido_fighter_v008/source_concept_raw.png`;
  - sha256 `87b4bb4a3ed8369c9587cf7a8a1718fd7dbb79c01f797b4eda6bfb2030f6ed11`.
- Precheck:
  - quinta pose agora mostra mao de lava aberta, visivel e acima/na frente da perna;
  - paleta 16 cores embutida no model sheet;
  - sem anomalia grosseira de membro observada;
  - ainda requer validacao humana antes de lineart 48x64.
- Status v008: `source_candidate_pending_human_validation`.
- Proibicao preservada: nao converter direto; proximo passo, se aprovado, e lineart/blocking nativo 48x64.

## 2026-06-09 - v009 sprite sheet runtime candidate

- Feedback humano: v008 aceito como direcao para traducao nativa; nao como runtime art direto.
- Novo builder dedicado:
  - `data/builders/build_hibrido_fighter_sprite_sheet_v009.py`.
- Nova folha nativa 48x64 gerada sem downscale direto do concept:
  - `data/processed/spritesheets/hibrido_fighter_complete_sprite_sheet_48x64_v009.png`;
  - `data/processed/reports/hibrido_fighter_complete_contact_sheet_with_palette_v009.png`;
  - `data/processed/reports/hibrido_fighter_complete_contact_sheet_with_palette_v009_preview_x4.png`;
  - `data/processed/lineart/hibrido_fighter_lineart_blocking_48x64_v009.png`.
- Strips runtime v009 em `res/sprites/hibrido/`:
  - `idle`, `walk_step`, `guard_block`, `jab`, `knee`, `teep`;
  - todos 288x64, PNG modo P, PLTE=16, index 0 transparente, cores no grid 9-bit, sem contato de borda.
- Viewer SGDK atualizado para v009 body-only em PAL2; PAL3/FX separado fica fora desta rodada porque a fonte aprovada trabalha uma paleta unica de personagem.
- Fundo do viewer alterado para teal escuro `#224444` via `PAL_setColor`/`VDP_setBackgroundColor` para nao esconder cabelo/outline preto na evidencia.
- Build vigente:
  - `out/rom.bin`;
  - sha256 `764d5a95c5c6aa979905afaeba417c6225b0547299537bb27228c4c85a9b34da`;
  - tamanho `131072` bytes.
- Evidencia BlastEm:
  - `out/evidence/blastem/screenshot.png`;
  - `out/evidence/blastem/save.sram`;
  - `out/logs/blastem_evidence_reconciliation_v009.json`;
  - captura oficial continua parcial por bug conhecido no `capture_blastem_evidence.ps1` minimal mode (`$screenshotArtifactPath` indefinido).
- Reports v009:
  - `out/logs/hibrido_v009_animation_report.json`;
  - `out/logs/hibrido_v009_pixel_compliance_report.json`;
  - `out/logs/sprite_strip_integrity_report_v009.json`;
  - `out/logs/hibrido_v009_visual_translation_report.json`;
  - `out/logs/hibrido_v009_sprite_artifact_report.json`.
- Contratos v009:
  - `doc/contracts/visual_dna_manifest_v009.json`;
  - `doc/contracts/animation_direction_contract_v009.json`;
  - `doc/contracts/human_validation_record_v009.md`.
- Status honesto: `technical_runtime_candidate=true`, `blastem_partial_evidence=true`, `visual_aprovado=false`, `human_visual_validation=rejected`, `ready_for_aaa=false`.
- Pos-validacao 2026-06-09T05:52-03:00: `validate_resources.ps1 -WorkDir <project>` retornou errors=0, warnings=11, checked=6; o `technique_usage_manifest.json` foi corrigido para usar registry_id canonico e tags reconhecidas.

## 2026-06-13 - Reprovacao curatorial v009 por fidelidade model sheet -> sprite sheet

- Pedido humano: revisar o estudo porque o model sheet v008 tinha direcao forte, mas o sprite sheet v009 virou arte blocada e desconectada do design original.
- Decisao curatorial: `hibrido_fighter_complete_sprite_sheet_48x64_v009.png` fica reprovado visualmente.
- Evidencia:
  - source/model sheet: `data/source_art/hibrido_fighter_v008/source_concept.png`;
  - sprite sheet reprovado: `data/processed/spritesheets/hibrido_fighter_complete_sprite_sheet_48x64_v009.png`;
  - report novo: `out/logs/hibrido_v009_model_sheet_to_sprite_fidelity_report.json`.
- Falha principal: conformidade tecnica de celula, PNG modo P, PLTE e grid 9-bit nao preservou anatomia, rosto/olhos, braco de lava, calcao preto/dourado, bandagens, marcadores vermelhos nem acting de Muay Thai.
- Novo aprendizado local: folha de personagem 48x64 derivada de model sheet aprovado exige `model_sheet_to_sprite_fidelity_report` antes de promocao para `res/`, baseline visual ou claim de qualidade.
- Status v009 apos revisao: `technical_pass=true`, `visual_pass=false`, `ready_for_res_promotion=false`, `ready_for_aaa=false`.
- Proxima rota: nao remendar PNG final; voltar para `lineart_blocking_1px` por estado/acao, reconstruir clusters nativos preservando o DNA v008 e gerar comparativo model sheet/sprite/contact sheet antes de runtime.
- Validacao pos-curadoria:
  - `validate_project_context`: status ok, contexto `exercise`, blockers=0;
  - `validate_project_methodology`: passed, blockers=0;
  - `validate_project_hygiene`: passed, blockers=0;
  - `validate_resources`: errors=0, warnings=11, checked=6; avisos preservam bloqueio visual, evidencia de emulador insuficiente e closeout ausente;
  - `freshness_audit`: status warning; nao ha entrega AAA, apenas registro honesto de estudo rejeitado.






