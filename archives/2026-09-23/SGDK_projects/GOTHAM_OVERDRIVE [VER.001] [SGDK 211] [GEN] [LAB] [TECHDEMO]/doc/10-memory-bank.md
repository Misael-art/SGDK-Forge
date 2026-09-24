<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: MVP Técnico / Laboratório de Hardware Avançado
- Ultima sincronizacao: 2026-09-09
- Ultimo build versionado: out/rom.bin (SGDK 2.11 GCC m68000)
- ROM vigente: out/rom.bin
- Evidencia de emulador: captura Linux presente; cena observada `scene_id=4`, performance sustentada não certificada
- Gate visual: ativos e proveniência registrados; aprovação visual não foi revalidada nesta regressão
- Gate gameplay: captura parcial; telemetria observou pressão VDP acima do contrato
- Gate AAA: `technical_demo_ready=false` até reconciliar cena e budget
<!-- SGDK GENERATED STATUS END -->

## Atualizacao vigente — 2026-09-09: instrumento migrado e blocker de runtime observado

- `.agent/scripts/vdp_scanline_simulator.py` local foi migrado isoladamente de
  1.1.0 para a versão canônica 1.2.0; SHA local/canônico:
  `5b0afd5b20d3993468a62c562f2cea2e14b767c5acfa7de12e2d7f880915b3ab`;
- self-check passou com decomposição geométrica, os dois limites de scanline,
  headroom e H32;
- regressão `branding_sequence` executou pela rota Linux/Flatpak correta e
  selou screenshot, SRAM e `visual_vdp_dump.bin` no bundle
  `out/evidence/scenes_host/branding_sequence`;
- a regressão não passou: o contrato esperava `expected_app_scene_id=0`, mas a
  ROM observou `captured_app_scene_id=4` (TECHDEMO);
- no mesmo bundle, a telemetria observou `over_budget_frames=661`,
  `max_scanline_sprites=21`, `max_cpu_load=213` e `max_active_sprites=91`;
- ROM observada: `20e7c2c9647fddabb890e63fd72036faaa7b9d26f5a828aaaf110031bb095e75`;
  isso não certifica 60 FPS sustentados, áudio, arte final ou AAA.

# 10 - Memory Bank & Context Tracker - GOTHAM_OVERDRIVE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]

**Ultima atualizacao:** 2026-08-29
**Fase atual:** assets_graficos_aaa_injetados_e_validados
**Proxima fase:** expansao_de_fases_e_polimento_geral

## 1. Estado operacional

- documentado: sim (`00-project-brief`, `08-bible-artistica`, `10-memory-bank`, `13-spec-cenas`, `14-plano-de-provas-qa`, `18-asset-register`, `spec_assets_dark_deco.md`)
- implementado: sim (motor pseudo-3D multi-eixo e chefe modular biônico; budget runtime pendente)
- buildado: sim (SGDK 2.11 GCC m68000 via wine bridge)
- testado_em_emulador: parcial (captura Linux e cena observada; regressão de branding falhou)
- validado_budget: não (telemetria observou 661 frames acima do budget e pico de 21 sprites/scanline)
- gate_estetico: ativos/proveniência registrados; aprovação final não revalidada nesta rodada

## 2. Conformidade com a Diretriz de Bloqueio Estético

- Todos os gráficos de personagens, inimigos, chefe e cenários consomem exclusivamente arquivos PNG indexados a 4 bits em `res/bgs/` e `res/sprites/`.
- Proveniência de assets 100% declarada e validada em `doc/asset_provenance_manifest.json` através do auditor `audit_procedural_asset_provenance.py`.
- Fontes autorais de alta resolução preservadas e com hash verificado em `data/source_art/`.
