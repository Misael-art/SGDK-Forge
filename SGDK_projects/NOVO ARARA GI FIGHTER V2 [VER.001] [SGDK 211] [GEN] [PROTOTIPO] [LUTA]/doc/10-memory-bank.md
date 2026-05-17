<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `validation_report.json`
- Ultima sincronizacao: `2026-05-17T00:12:47.4063224-03:00`
- Changelog canonico: `doc/changelog/changelog.md`
- Assets versionados rastreados: 31
- Ultimo build versionado: build_v006
- ROM vigente: `e32ed0d18c488f4195747626a7d2505e61d33b2b8f665c721626f5496349788f` (`262144` bytes)
- Validation summary: errors=0 warnings=3
- Blockers vigentes: visual_gate_blocked
- Evidencia de emulador: BlastEm fresco, `emulator_evidence_stale=false`
- Gate visual: visual_lab_aprovado=False
- Gate gameplay: gameplay_rom_aprovada=False
- Gate AAA: ready_for_aaa=False
- QA runtime: gameplay=stale performance=estavel audio=ok hardware_real=blastem_reference_emulator
<!-- SGDK GENERATED STATUS END -->
# 10 - Memory Bank & Context Tracker Ã¢â‚¬â€ NOVO ARARA GI FIGHTER V2 [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]

**Ultima atualizacao:** 2026-05-17 00:12 BRT
**Fase atual:** prototipo jogavel testado_em_emulador, AAA bloqueado por gate visual
**Proxima fase:** medir/capturar `visual_vdp_dump.bin` ou manter `visual_gate_blocked`

> **DIRETRIZ:** Este e o bloco de memoria primario do projeto.
> Leia integralmente antes de qualquer codigo ou decisao.
> Atualize ao encerrar sessoes relevantes.

---

## 1. ESTADO ATUAL DO PROJETO

### O que existe e funciona

- ROM SGDK em `out/rom.bin` com Caio Arara P1 e Davi Arara P2 jogaveis na cena `Lapa Open Mat - Noite`.
- Runtime de luta 1v1 com idle, caminhada, dash, crouch, jump, guard, jab, medium, grip, hip throw, hurt, knockdown e getup.
- HUD no plano WINDOW com nomes, barras e timer; controles basicos no pad 1; dummy P2 com IA simples.
- Stage autoral em BG_B/BG_A com skyline, Arcos sugeridos, arquibancada, tatame e paleta fria/quente.
- Evidencia BlastEm persistente e fresca: screenshot + `save.sram` MDRT, `emulator_session.json` com SHA256 da ROM vigente e runtime metrics sem over-budget.

### O que e placeholder

- Audio: sem recursos declarados em `.res`; eixo tratado como `not_required`/`ok` para este slice.
- Davi e uma variacao curada do rig/paleta do Caio para teste versus; suficiente para P2 tecnico, nao e personagem completo independente.
- `visual_vdp_dump.bin` nao e gerado porque a ROM exporta bloco MDRT, nao VLAB; a evidencia visual canonica deste slice e screenshot BlastEm + SRAM MDRT.

### O que falta para o slice ser completo

- O prototipo funcional atual esta jogavel, mas AAA/Elite continuam bloqueados por `visual_gate_blocked`: `visual_vdp_dump.bin` ausente, VRAM visual nao medida em dump e `visual_delivery_gate_report.json` marcado como `ready_for_aaa=false`.
- Qualquer nova arte critica deve passar novamente por `data/source_art`, manifests, res_graph, runtime capture, BlastEm e freshness.

### Snapshot dos gates QA

- visual_lab_aprovado: false
- gameplay_rom_aprovada: false
- ready_for_aaa: false
- freshness_audit: ok (`out/logs/freshness_audit_report.json`)
- scene_closeout_gate: blocked por `visual_gate_blocked` (`out/logs/scene_closeout_gate_report.json`)

### Blockers QA ativos

- `validation_report.json` tem blocker ativo: `visual_gate_blocked`.
- Avisos residuais: `INDEX0_VISIBLE_HIGH_RISK` em `lapa_bg_a`; gate visual critico bloqueado corretamente por `visual_delivery_gate_report.json`.

### Metricas de codigo

- ROM: 262144 bytes, SHA256 `e32ed0d18c488f4195747626a7d2505e61d33b2b8f665c721626f5496349788f`.
- Runtime capture: 32 amostras, `capture_status=partial`, `frames_seen=122`, `over_budget_frames=0`, `cpu_load_max=40`, `frame_cpu_ratio_p95=36`, `max_scanline_sprites=5`, `sprite_engine_peak=3`.
- Res graph: 31 declaracoes OK, VRAM residency `ok`, BG_B 565 tiles unicos, BG_A 214 tiles unicos, overlap 0.
- Sprite integrity Caio: 14 strips auditados, 0 findings bloqueantes.

### Estado de evidencia canonica

- ROM vigente: `out/rom.bin`, SHA256 `e32ed0d18c488f4195747626a7d2505e61d33b2b8f665c721626f5496349788f`.
- `validation_report.json`: ok tecnico, errors=0, warnings=3, blockers=[`visual_gate_blocked`].
- `runtime_metrics.json`: ok, scene_id=2, samples_recorded=32.
- `scene_regression_report.json`: ok, `first_playable_slice` capturado, `expected_app_scene_id=2`, `captured_app_scene_id=2`, baseline ainda ausente.
- `emulator_session.json`: ok, BlastEm, `fresh_sram_confirmed=true`.
- `freshness_audit_report.json`: ok, stale_count=0.
- `scene_closeout_gate_report.json`: blocked, 9/9 steps succeeded, blocker unico `visual_gate_blocked`.

---

## 2. O QUE ACABOU DE ACONTECER

**2026-05-16 Ã¢â‚¬â€ Fechamento funcional honesto**

- Corrigida a traducao dos BGs para caber no budget de VRAM sem perder a leitura principal do palco.
- Corrigido `capture_blastem_evidence.ps1` para emitir `emulator_session.json` persistente a partir da captura real.
- Corrigido `runtime_probe.c` para gravar pressao de scanline como proxy de scanline, nao total bruto de sprites VDP.
- Rebuild final, runtime capture e captura BlastEm refeitos depois das alteracoes.

---

## 3. DECISOES PENDENTES

- Definir se o proximo slice tera audio XGM/SFX ou regressao automatica multi-cena primeiro.
- Definir se Davi vira personagem autoral completo ou permanece P2 tecnico por enquanto.

---

## 4. DECISION LOG CONSERVADOR

Registre aqui escolhas que evitaram tentativa-e-erro ou mudanca de rota.

| Data | Contexto | Escolha | Alternativas recusadas | Evidencia | Proximo gate |
|------|----------|---------|------------------------|-----------|--------------|
| 2026-05-16 | Stage Lapa Open Mat | Reduzir detalhe de BG no builder para VRAM `ok` | Ignorar overlap, chamar ROM antiga de prova final | `out/logs/res_graph_report.json` | Revalidar ROM |
| 2026-05-16 | Emulador | Gravar `emulator_session.json` pela captura BlastEm persistente | Usar tempdir descartado ou ROM antiga | `out/logs/emulator_session.json` | Freshness/closeout |
| 2026-05-16 | Runtime metrics | Corrigir proxy de scanline no MDRT | Tratar total de sprites VDP como scanline real | `out/logs/runtime_metrics.json` | Budget gate |
| 2026-05-17 | Visual gate | Manter `ready_for_aaa=false` com `visual_gate_blocked` | Chamar screenshot sem VDP dump de prova AAA | `out/logs/visual_delivery_gate_report.json` | VDP/perceptual |
| 2026-05-17 | Scene regression | Usar `sram_bootstrap` para `first_playable_slice` scene_id 2 | Deixar `boot_mode=unsupported` passar como ok | `out/logs/scene_regression_report.json` | Baseline |

---

## 5. ROTEIRO DE FECHAMENTO

- build/rebuild canonico: ok
- contratos recompilados: ok
- grafo de recursos: ok
- validator: ok
- captura BlastEm: ok
- regressao de cena: ok, `first_playable_slice` capturado
- freshness audit: ok
- closeout gate: blocked por `visual_gate_blocked`

---

## 6. REFERENCIAS RAPIDAS

- GDD: `doc/11-gdd.md`
- Spec cenas: `doc/13-spec-cenas.md`
- Diretrizes agente: `doc/00-diretrizes-agente.md`
- Plano de provas QA: `doc/14-plano-de-provas-qa.md`













