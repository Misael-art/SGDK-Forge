<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: doc/changelog + validation_report.json + emulator_session.json + runtime_metrics.json
- Ultima sincronizacao: 2026-05-14T05:34:46-03:00
- Changelog canonico: doc/changelog/changelog.md
- Assets versionados rastreados: 30
- Ultimo build versionado: build_v001
- ROM vigente: 5f8a5d66969554c08861975d5080863d652b89512956afdd5647931d66eff00f (262144 bytes)
- Validation summary: errors=0 warnings=2
- Blockers vigentes: visual_gate_blocked, local_rasterization_used_as_final, source_to_rom_mismatch
- Evidencia de emulador: blastem_gate_ok, fresh_sram_confirmed=True
- Gate visual: visual_lab_aprovado=False
- Gate gameplay: gameplay_basico=funcional, gameplay_rom_aprovada=False no gate AAA
- Gate AAA: ready_for_aaa=False
- QA runtime: capture_status=partial, scene_id=3, frames_seen=151, samples=32, over_budget_frames=0, audio=nao_testado, hardware_real=nao_testado
<!-- SGDK GENERATED STATUS END -->
# 10 - Memory Bank & Context Tracker - AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]

**Ultima atualizacao:** 2026-05-14T05:34:46-03:00
**Fase atual:** prototype_playable com visual_gate_blocked
**Proxima fase:** substituir strips procedurais por strips premium por acao e repetir gates ate AAA ou novo bloqueio real.

## 1. ESTADO ATUAL DO PROJETO

### O que existe e funciona

- Projeto SGDK 2.11 bootstrapado e buildado em out/rom.bin.
- Cena direta de luta APP_SCENE_FIGHT = 3, sem menu textual de debug.
- Dois lutadores visiveis: Marina "Raio de Roda" Santana e Bento "Martelo" Duarte.
- Controle P1: movimento, dash por duplo toque ou X, crouch, hop, guarda, golpe leve, medio e rasteira/especial curto.
- P2 com IA simples de aproximar, recuar, guardar e atacar.
- Sistema de HP, timer, hit stun, pushback, knockdown/getup, spark separado e camera shake leve.
- BlastEm rodou a ROM vigente com screenshot persistente e SRAM fresca confirmada.

### O que e placeholder ou bloqueia AAA

- Sprites finais dos lutadores sao runtime strips locais/procedurais derivados do builder, nao strips premium gerados por acao.
- Gate visual bloqueado por local_rasterization_used_as_final e source_to_rom_mismatch.
- Audio tem hooks PSG de impacto, mas a validacao de audio segue nao_testado.
- visual_vdp_dump.bin nao foi produzido nesta modalidade MDRT; a evidencia real usada foi screenshot BlastEm + SRAM fresca.
- Runtime capture e real, mas parcial: 151 frames vistos e 32 samples, nao um soak longo completo.

### Snapshot dos gates QA

- build: ok, out/rom.bin existe.
- res_graph: ok, VRAM ok, overlaps=0.
- sprite_integrity: passed (26/26 strips).
- validation_report: errors=0, warnings=2, blockers=visual_gate_blocked, local_rasterization_used_as_final, source_to_rom_mismatch.
- emulator_session: boot=ok, fresh_sram_confirmed=True, gameplay_basico=funcional.
- visual_delivery_gate: visual_gate_blocked, ready_for_aaa=False.
- scene_closeout_gate: blocked; subpassos scene_contract_compiler/res_graph_audit/validate_resources/freshness_audit ok.

### Evidencia canonica

- ROM vigente: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\rom.bin.
- ROM sha256: 5f8a5d66969554c08861975d5080863d652b89512956afdd5647931d66eff00f.
- Screenshot BlastEm: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\captures\benchmark_visual.png.
- Screenshot sha256: c0cb2d1d196fd3a6dd23b638676e08bb692fb540058424a25122b19fb56e3c58.
- SRAM persistente: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\captures\save.sram.
- SRAM sha256: 4d18466bc9fad69c28e61861f58826484bd632165042acbd1925bb11711ce6b8.
- validation_report: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\validation_report.json.
- runtime_metrics: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\runtime_metrics.json.
- emulator_session: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\emulator_session.json.
- res_graph_report: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\res_graph_report.json.
- vram_residency_report: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\vram_residency_report.json.
- visual_delivery_gate_report: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\visual_delivery_gate_report.json.
- scene_closeout_gate_report: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\scene_closeout_gate_report.json.

## 2. DECISION LOG CONSERVADOR

| Data | Contexto | Escolha | Alternativas recusadas | Evidencia | Proximo gate |
|------|----------|---------|------------------------|-----------|--------------|
| 2026-05-14T05:34:46-03:00 | Fechamento | Manter status visual bloqueado em vez de promover AAA | Chamar sprite procedural de final premium | F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\visual_delivery_gate_report.json | gerar strips premium por acao |
| 2026-05-14T05:34:46-03:00 | VRAM | Usar SPR_initEx(420) e residencia apertada sem overlap | Aumentar tiles residentes sem budget | F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\vram_residency_report.json | reduzir tiles antes de adicionar arte |
| 2026-05-14T05:34:46-03:00 | Evidencia | Citar somente ROM/screenshot/SRAM persistentes | Prova fake ou tempdir descartado | F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\emulator_session.json | repetir BlastEm apos novas mudancas |
| 2026-05-14T05:34:46-03:00 | Closeout | Rodar closeout sem rebuild/captura para nao stalar a prova | Rebuild apos captura sem recapturar | F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\scene_closeout_gate_report.json | recapturar se ROM mudar |

## 3. ROTEIRO DE FECHAMENTO

- build/rebuild canonico: ok.
- contratos recompilados: ok.
- grafo de recursos: ok.
- validator: ok com blocker visual.
- captura BlastEm: ok, screenshot + SRAM persistentes.
- regressao de cena: nao requerida neste closeout.
- freshness audit: ok dentro do closeout.
- closeout gate: blocked por gate visual, nao por ausencia de ROM/emulador.
