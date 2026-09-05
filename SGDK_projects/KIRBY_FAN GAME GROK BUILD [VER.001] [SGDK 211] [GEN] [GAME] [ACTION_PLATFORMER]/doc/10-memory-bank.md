<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: sessao 005 (2026-08-08) — critico cego + trilha VGM r2 + G1–G3
- Ultima sincronizacao: `2026-08-08`
- Evidencia visual: `stage_post_critic2` PASS; painel cego em `out/evidence/blind_critic/`
- Critico cego: **apontou o nosso (D)**; score ~5.8/10 apos G1–G3
- Trilha: `mus_stage_valley.vgm` ~16.8s loop, 4 FM + PSG; audio_gates PASS
- Blockers: `trilha_ainda_procedural_nao_furnace`, `fases_2_e_3_ausentes`, `g4_g6_fx_smear`, `critico_ainda_nao_hesita`
- Gate AAA: `ready_for_aaa=False`
<!-- SGDK GENERATED STATUS END -->

# 10 — Memory Bank — KIRBY_FAN GAME GROK BUILD

**Ultima atualizacao:** 2026-08-08
**Fase atual:** FASE 0 feita · FASE 1 testada em emulador · FASE 3 operacional · FASE 2 R1 iniciada
**Proxima:** camadas BG R1 → critico visual cego → trilha Furnace → fases 2/3

> **DIRETRIZ:** leia integralmente antes de qualquer codigo ou decisao.

---

## 1. O que este projeto e

Reimaginacao de **Kirby's Adventure (NES)** para Mega Drive. Fan game **nao
comercial**. Arte e trilha originais. ROM ≤ 4 MB, sem mapper.

Contrato tecnico mestre: [ARCHITECTURE.md](ARCHITECTURE.md)
Irmaos normativos: [VRAMMAP.md](VRAMMAP.md), [PALETTES.md](PALETTES.md),
[SOUNDMAP.md](SOUNDMAP.md).

Escopo VER.001: titulo → 3 fases Vegetable Valley → boss Whispy Woods →
game over/continue; 5 copy abilities (FIRE / BEAM / CUTTER / STONE / SWORD).

Tese: o NES *tentava* gradientes, profundidade e cor por regiao. Nos entregamos
isso com line-scroll, H-int, S/H e YM2612.

## 2. Verdades do host (verificadas no irmao CLOUDE / neste host)

| Fato | Detalhe |
|---|---|
| Unica rota de build | `bash tools/sgdk_wrapper/build_sgdk_wine_bridge.sh --project-root "<proj>"` |
| `build.sh` / `new_project.sh` | Quebrados em Linux (PATH com `*.exe` do GDK) |
| Captura | `capture_blastem_evidence_linux.sh` |
| Graphify | nao fica `fresh` neste host; consultivo, nao bloqueia producao |

## 3. Heranca tecnica do prior art CLOUDE

Portado nesta sessao (codigo + harness + contratos medidos):

- loop de cenas titulo/fase/boss/gameover
- Kirby + abilities + inimigos + Whispy Woods
- raster R1–R5, parallax 5 camadas, probe VLAB/KRB1
- `tools/harness/gates.py` e familia

**Nao e entrega AAA.** Arte ainda e placeholder; trilha e VGM gerado; visual
lab nao aprovado. GROK BUILD existe para empurrar qualidade via geracao de
assets + loop critico.

## 4. Estado por subsistema (vocabulario AGENTS.md)

| Subsistema | Status | Nota |
|---|---|---|
| Contratos FASE 0 | `documentado` | ARCHITECTURE/VRAM/PAL/SOUND presentes |
| Codigo FASE 1 | `implementado` | portado; aguarda build neste path |
| ROM | — | pendente build |
| Harness | `implementado` | tools/harness/ portado |
| Arte AAA | `placeholder` | placeholders `ph_*.png` |
| Audio | `parcial` | XGM2 + VGM placeholder |
| Critico FASE 2 | nao iniciado | — |

## 5. Decisoes que nao renegociamos sem medicao

1. XGM2 (ducking) — taxa PCM 13.3/6.65 kHz.
2. S/H global ligado; fundo priority=1; teto 58 cores de gameplay.
3. Planos 64×32; 1004 tiles de fundo.
4. Um unico H-int callback dirigido por tabela de faixas.
5. Pools estaticos; zero `malloc`/`float`.

## 6. Proximos passos ordenados

1. Build wine bridge → `out/rom.bin`
2. Captura BlastEm + `gates.py` PASS
3. FASE 2: prompts de imagem → quantizacao RGB333 → integrar
4. Loop critico visual
5. CHANGES.md por sessao

## Plano paralelo ativo (2026-08-08)

Aprendizado gráfico via Spriters Resource (lab only):
`doc/plans/PARALLEL_TSR_REFERENCE_LEARNING_PLAN.md`
Arquivo: `data/reference_archive/` (`ship_allowed=false`).
Ship continua arte original.

## Politica de assets (2026-08-08)

Fan/estudo non-commercial: `fan_study_allowed=true`.
Rips TSR convertidos **podem** ir a `res/` e ROM fan.
Comercial/marketplace: **nao**. Ver `data/reference_archive/LEGAL.md`.

## Sessao 012 — 2026-09-02 — Forward-test v02 native animation candidate

- Corrigido o falso blocker de native same-canvas no `forge-art`: canvas 32×32 preservado mesmo com bbox ocupado menor; binding de autoridade, escala e revisão humana agora são obrigatórios nos specs.
- Corrigida a heurística de matte do analisador de strips: cor dominante do corpo sem contato de borda não é matte; contato de borda de célula nativa pode ser declarado explicitamente.
- Staging produzido em `out/forward_test_v02/`: strips separadas `idle`, `run` e `inhale`, previews GIF, contact/1×/2×/3×/8×, composição 320×224, pivot/foot/continuity, pixel-strict P/4bpp, tile reuse, DMA e scanline.
- Fonte local: `data/source_art/ai_quantized/r1/kirby_sheet_32x8_q.png`, SHA `91317062374382e6c2a361e23538623732440b8daf61ddbf205fb8ce8690caec`; matte tratado por chroma conectado às bordas declarado.
- Claim máximo: `native_animation_candidate`; `res/`, runtime, ROM, BlastEm e AAA permanecem bloqueados até aprovação humana e integração.
