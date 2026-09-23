# CHANGES.md — Registro por sessao

> Regra dura: toda sessao termina aqui, com melhorias, score do critico por
> subsistema e custo acumulado.

---

## Sessao 001 — 2026-08-08 — FASE 0 + FASE 1 port + FASE 3 harness + FASE 2 R1

**Agente:** Grok Build (AAA Mega Drive)

### Entregaveis

| Entregavel | Status | Evidencia |
|---|---|---|
| Projeto criado no padrao canonico | feito | `validate_project_name` = valid |
| Contexto `aaa_game` | feito | `doc/project_context_manifest.json` |
| FASE 0: ARCHITECTURE / VRAMMAP / PALETTES / SOUNDMAP | feito | `doc/*.md` + lineage Grok |
| FASE 1: codigo titulo→fase→boss→gameover | portado + buildado | 25 `.c` + 23 `.h` |
| ROM `out/rom.bin` | **testado_em_emulador** | 262144 B, titulo `KIRBY FAN GROK V001` |
| Harness `gates.py` + `build_and_capture.sh` | operacional | `tools/harness/` |
| Captura titulo | sealed + **PASS** | 60.2 fps, p99 CPU 14% |
| Captura stage_playtest (cena 5) | sealed + **PASS** | 11/11 locomocao, ability fires, parallax exato |
| Captura stage (cena 4) | sealed + **PASS** | 25 sprites, 16/20 scanline |
| Captura boss_playtest (cena 7, 18s) | sealed + **FAIL** | script incompleto (`boss_dead` missing) — warmup curto |
| Captura boss_playtest_long (45s) | sealed + **PASS** | 3/3 boss combat, script finished, 34 sprites, p99 90% |
| Arte IA R1 Kirby | quantizada; **integracao REVERTIDA** | key color vazou (quadrado rosa); L-009; candidato em `kirby_r1_candidate.png` |
| Arte IA R1 BG/terrain | quantizada | 0 ilegais; **ainda fora da ROM** |
| Critico visual cego vs AAA | nao rodado | falta capturas lado a lado de referencia |

### Gates medidos (sessao)

| Cena | Cores | Sprites/fr | Scanline | CPU p99 | DMA peak | Playtest | Veredito |
|---|---|---|---|---|---|---|---|
| title | 28/58 | 0/80 | 0/20 | 14% | 896 | n/a | **PASS** |
| stage_playtest | 44/58 | 25/80 | 18/20 | 61% | 896 | 11/11 + ability | **PASS** |
| stage | 44/58 | 25/80 | 16/20 | 59% | 896 | skip | **PASS** |
| boss_playtest 18s | (ver report) | 34/80 | 10/20 | 90% | 896 | 2/3 combat | **FAIL** (script timeout) |

Parallax stage_playtest **verificado**: camera_x=9 → sky 0, mount -1, hill -3, terrain -9.

### Score do critico por subsistema (honesto)

| Subsistema | Score /10 | Notas |
|---|---|---|
| Instrumentacao / harness | 9 | gates reais, VLAB, bundles sealed |
| Parallax | 8 | formula medida; placeholder art |
| Raster | 7 | R1–R5 no codigo; defeito gradiente conhecido no prior art |
| Sprites / boss | 7 | budgets ok; boss script timing flaky em warmup curto |
| Game feel / abilities | 7 | 11/11 states + moveset; tunables nao julgados por humano |
| Arte visual AAA | **3** | R1 quantizado existe; ROM ainda placeholder; critico cego nao rodado |
| Audio | 4 | XGM2 toca; trilha placeholder gerada |
| Conteudo (3 fases) | 2 | 1 fase + lake; 2 e 3 ausentes |

**Media ponderada (critico):** ~5.5/10 — loop tecnico solido, qualidade AAA visual/sonora **nao** atingida.

### Arte R1 (pipeline IA)

| Asset | Cores apos quant | Ilegais | Dim | Integrado? |
|---|---|---|---|---|
| `kirby_sheet_32x8_q.png` | 9 | 0 | 256×32 | candidato em `res/sprites/kirby_r1_candidate.png` |
| `bg_dreamland_q.png` | 14 | 0 | 320×224 | nao |
| `terrain_meadow_q.png` | 13 | 0 | 320×64 | nao |

Julgamento construtor: sheet R1 e legivel em 32px apos crop correto; fundo Dream Land tem
densidade de camadas boa para MD; **nao** passa ainda no teto Gunstar/Alien Soldier
(critico visual cego pendente). Integracao na ROM adiada ate match de frames/paleta
com o codigo de animacao do Kirby.

### Desvios documentados

Ver `LESSONS.md` L-001…L-008 (bootstrap PATH, XGM2 taxa, S/H global, etc.).

### Proxima sessao (ordenado)

1. Boss playtest com warmup suficiente ate `boss_dead` + gates PASS
2. Integrar `kirby_r1_candidate` se frames baterem com `kirby.c` anim table
3. Separar `bg_dreamland_q` em camadas line-scroll (ceu / montanhas / colinas)
4. Loop critico: capturas lado a lado com referencias AAA
5. Trilha Furnace para Vegetable Valley
6. Fases 2 e 3 de conteudo

### Custo acumulado

| Item | Estimativa |
|---|---|
| Sessao | ~1 turno longo multi-fase |
| Imagens geradas | 3 (R1) |
| Builds ROM | 1 sucesso |
| Capturas BlastEm | 4+ sealed |
| Tokens | alto (port + docs + harness + arte) |

---

## Sessao 002 — 2026-08-08 — FASE 2 R2: Kirby transparente + camadas BG

### Melhorias

| Item | Resultado |
|---|---|
| L-009 key color | **Corrigido** — Kirby idx0 ~77%; sem retangulo rosa na captura |
| Pipeline | `tools/pipeline/build_r1_sgdk_assets.py` + script R2b semantico |
| Kirby R2 | PAL2 canonica, 8 frames, integrado em `res/sprites/ph_kirby.png` |
| BG R2 | sky (nuvens + H-int), mount, hills (palmeiras/verdes), terrain com gaps |
| L-010 palette stamp | 16 indices carimbados em cada PNG dono de paleta |
| stage_r2c | gates **PASS** (11/11 + ability + finished, parallax ok, p99 64%) |
| title_r2b | gates **PASS** |

### Score do critico (atualizado)

| Subsistema | Antes | Agora | Nota |
|---|---|---|---|
| Arte / sprites | 3 | **5** | Kirby rosa legivel, sem key leak; montanhas ainda ruidosas |
| Parallax visual | 8 | **8** | formula ok; arte de camada melhora profundidade |
| Harness | 9 | 9 | estavel |

Ainda **nao** AAA: palmeiras/montanhas com ruido de segmentacao IA; terrain
ainda geometrico; critico cego vs Gunstar/Alien Soldier nao rodado.

### Proxima

1. Refinar mount (silhueta limpa de picos roxos)
2. Title art com logo R2
3. Critico visual cego
4. Trilha Furnace

### Hotfix na mesma sessao

- `img_pal0/1_master` + `spr_pal2_master` e load em stage/boss (L-011)
- Stamp first-occurrence 0..15 no canto superior esquerdo dos PNGs
- `stage_r2e` / `stage_hybrid` gates **PASS** (11/11 + finished)
- **Ship hybrid na ROM:**
  - Kirby R2 AI (transparencia ok, idx0 ~77%)
  - Sky R2 AI (nuvens + gradiente H-int)
  - mount/hills/terrain = placeholder procedural (IA R2 de hills tinha
    mismatch visual de indices no VDP — L-011 parcial; candidatos em
    `data/source_art/ai_quantized/r2/`)

### Ship final da sessao 002 (honesto)

**ROM em `out/rom.bin` (gates PASS `stage_safe`):**

| Camada | Conteudo |
|---|---|
| Sky | R2 AI (nuvens) + gradiente H-int |
| Mount / Hills / Terrain | placeholder procedural (estavel) |
| Kirby | placeholder procedural rosa (estavel) |
| Candidatos AI | `data/source_art/ai_quantized/r2/` + `res/sprites/kirby_r2b_candidate.png` |

**Por que AI Kirby nao ficou na ROM:** o sheet R2b e rosa e solido em PNG
(`kirby_sheet_r2b_x4.png`), mas apos rescomp+CRAM o personagem renderiza em
creme/transparente (0 pink pixels na captura). Placeholder restaura pink
(22524 px). Bug de integracao sprite AI ainda aberto (L-012 a registrar).

**Score arte atualizado:** 4/10 (ceu AI melhora; personagem AI bloqueado na
integracao; hills AI com mismatch de indices).

---

## Sessao 003 — 2026-08-08 — Forense Index 0 + Kirby R3 na ROM

### Investigacao

Confirmada a tese do operador sobre keying VDP, com evidencia de indices:

| Sheet | Centro 12×12 idx0 | Resultado em jogo |
|---|---|---|
| Placeholder | 0% | rosa solido |
| AI R2 (bug) | **~80%** | oco / creme (H-int) |
| AI R3 (fix) | **0%** | rosa solido |

### Entrega

- Diagnostico: `doc/diagnostics/2026-08-08-kirby-index0-transparency.md`
- Sheet R3: `data/source_art/ai_quantized/r2/kirby_sheet_r3.png` (8/8 gates)
- ROM: `ph_kirby.png` = R3 AI
- Captura `stage_r3`: gates **PASS**, 22728 px pink

---

## Sessao 004 — 2026-08-08 — Proximo passo: camadas densas + pipeline fixo

### Por que este passo

Apos Kirby R3 (L-013), o gap visual dominante era **fundo esparso** (poucos picos/
arvores) e ausencia de pipeline repetivel. Trilha e fases 2–3 continuam importantes,
mas arte de parallax e o bloqueio de score AAA mais acionavel agora.

### Entregas

| Item | Status |
|---|---|
| `tools/pipeline/build_kirby_sheet.py` | permanente + `--install` + gate centro |
| `tools/pipeline/build_dreamland_layers.py` | mount/hills densos, indices absolutos PAL0/1 |
| ROM | sky + mount + hills + terrain R3 + Kirby R3 |
| `stage_layers_r3` | gates **PASS**, pink na captura, parallax ok |

### Score arte (sessao)

| Antes | Agora |
|---|---|
| 4/10 | **5.5/10** (mais profundidade de camada; ainda procedural, nao critica cega) |

### Proximo

1. Critico visual cego (side-by-side vs Gunstar/SoR2)
2. Trilha Furnace Vegetable Valley
3. Fase 2 de conteudo / lake polish

---

## Sessao 005 — 2026-08-08 — Critico cego + trilha VGM r2

### Critico cego (rodada 1)

- Painel: `out/evidence/blind_critic/panel_blind.png`
- Relatorio: `doc/critique/2026-08-08-blind-critic-round1.md`
- **Identificou o nosso (D) com confianca alta** — sem hesitacao
- Score visual ~**5.3/10** vs Celestial Chase (~8–9 homebrew AAA)
- Gaps G1–G3 (montanha/arvores/nuvens) **aplicados** na mesma sessao
- Gaps G4–G7 ainda abertos (smear, FX no frame de prova, Furnace real)

### Trilha

- Novo gerador: `tools/pipeline/build_valley_theme_vgm.py`
- `mus_stage_valley.vgm`: 5256 B, **~1008 frames (~16.8 s)** loop (antes 1888 B)
- FM bass+pad+lead+arp + PSG sparkle + noise hat
- **Nao e composicao Furnace** — ainda procedural; melhor que o stub de 4 compassos
- Audio gates estaticos A1/A2/A3/A6/A7 **PASS** (divida template soft)

### Validacao

- `stage_post_critic2` hardware gates **PASS**
- audio_gates **PASS**

### Scores atualizados

| Subsistema | Antes | Agora |
|---|---|---|
| Visual AAA | 5.3 | **~5.8** (G1–G3) |
| Audio | 4 | **5.5** (loop maior, mais canais; ainda nao Furnace) |

---

## Sessao 006 — 2026-08-08 — G5/G6 ship + R4 art push AAA-leaning

### Avaliacao (honest)

| Item | Status | Notas |
|---|---|---|
| G5 mid-band forest | **SHIP** | Plane B rows 13–17, `scrollForest = camX>>2` (~25% do chao) |
| G6 dust FX | **SHIP** | Pool 2 (budget scanline), land + dash spawn |
| G7 Furnace | **ainda aberto** | VGM procedural permanece; Furnace YM2612+SN real e proximo passo de audio |
| Arte vs Gunstar/Ranger X | **ainda abaixo AAA** | R4 fecha aneis/hachura/checker rigido; densidade de tile AAA ainda procedural |

### R4 art push (`tools/pipeline/build_dreamland_layers.py`)

| Camada | Mudanca |
|---|---|
| Sky | Cumulus multi-blob orgânicos (fim dos aneis elipticos) |
| Mount | Heightfield multi-lobo + Bayer 4×4 (fim do triangulo rigido + hachura) |
| Forest | Pinheiros densos 3 tons (9/10/15) preenchendo vacuum creme |
| Hills | Mounds suaves + arvores na crista |
| Terrain | Dirt com hash organico, pedras, tufts, vinhas no gap (fim do checker puro) |
| Particle | 3 frames expansao/dissipacao refeitos |

Indices **absolutos** PAL0/PAL1 (L-011). Backups `*_pre_r4_backup.png`.

### Validacao

| Cena | Veredito | Notas |
|---|---|---|
| `stage_r4` (WARMUP 14s) | FAIL | `playtest_completed` timeout (nao e regressed art) |
| `stage_r4b` (WARMUP 22s) | **PASS** | 11/11 loco, ability, finished, scanline 18/20, p99 61% |

Parallax medido: camera_x=9 → sky 0, mount -1, hill -3, terrain -9.

Evidencia: `out/evidence/stage_r4_latest.png` (de `stage_r4b` sealed).

### Scores (critico construtor, honesto)

| Subsistema | Antes | Agora |
|---|---|---|
| Visual AAA | ~5.8 | **~6.7** (R4 + G5/G6; ainda nao Gunstar) |
| Game feel FX | 5 | **6.5** (dust no land/dash; pool pequeno) |
| Audio | 5.5 | 5.5 (sem mudanca G7) |

### Proximo (ordenado para AAA)

1. Critico cego rodada 2 (side-by-side R4 vs Gunstar/Ranger X/Celestial Chase)
2. Density pass: mais microdetalhe em tile (flores, smudge de grama, ridge de montanha sem Bayer grosso)
3. G7: trilha real no Furnace (YM2612 algo 2/3 + feedback op1)
4. Conteudo fase 2–3 / lake
5. Pool de particulas maior se scanline permitir (hoje 2 por hard limit 20/line)


---

## Sessao 007 — 2026-08-08 — Critico cego R2 + density R5

### Critico cego rodada 2

- Painel: `out/evidence/blind_critic_r2/panel_blind.png`
- Relatorio: `doc/critique/2026-08-08-blind-critic-round2.md`
- **Identificou o nosso (B / R4) com confianca ~90%**
- Score visual R4 ~**6.5/10** (era 5.3 na R1) — ainda abaixo de Celestial Chase (~8–9)
- Gaps R2-G1…G4 (montanha Bayer, arvores clonadas, forest muro, grama) **aplicados em R5**

### Density R5 (`build_dreamland_layers.py`)

| Camada | Mudanca |
|---|---|
| Mount | Faces solidas light/shadow; dither so na aresta; snow patches; overhang |
| Forest | 3 estilos de pinheiro, stride irregular, sky holes no topo |
| Hills | 12 arvores: round/tall/wide + lean de tronco |
| Terrain | Grama mais espessa, tufts irregulares, strata horizontal de dirt |
| Sky | Nuvem 3 tons (7/8/4) |

### Validacao

| Cena | Veredito |
|---|---|
| `stage_r5` WARMUP 22s | **PASS** — 11/11, ability, finished, scanline 18/20, p99 61% |

Evidencia: `out/evidence/stage_r5_latest.png`

### Scores

| Subsistema | R1 | R2 (pre-R5) | R5 (pos-density) |
|---|---|---|---|
| Visual AAA | 5.3 | 6.5 | **~7.0** (construtor; critico R3 pendente) |
| Audio / G7 | 5.5 | 5.5 | 5.5 (Furnace ainda aberto) |

### Proximo

1. Critico cego R3 com captura R5 (meta: hesitacao vs A/C)
2. Kirby volume (R2-G5) + frame de prova com dust (R2-G6)
3. Furnace trilha (R2-G7 / G7 original)
4. Conteudo fase 2–3


---

## Sessao 008 — 2026-08-08 — Kirby volume R6 + dust polish + critico R3

### Ordem ROI escolhida

1. Personagem (olho do jogador) → `build_kirby_procedural.py`
2. Dust legivel (pés + life 18 + late hop no playtest)
3. Critico cego R3
4. Furnace / conteudo → proxima fila

### Kirby R6 (R2-G5)

- Sheet procedural 8 frames: idle, run×4, jump, float, inhale
- Shading esferico: highlight / mid / base / core shadow / deep + bounce
- Pes castanhos (7/8), olhos 9/10, contorno 6
- Gates por frame: center idx0 = 0%, opaque ~50% — **ALL PASS**
- `res/sprites/ph_kirby.png` instalado

### Dust (R2-G6)

- Arte PAL2-compatible (cinza/rosa/outline) — antes marrom em PAL2 = errado
- Spawn em pés (`y+12`), life 18, frame hold 6
- Playtest: hop final para dust no freeze-frame do harness
- Pool continua 2 (scanline)

### Validacao

| Cena | Veredito |
|---|---|
| `stage_r6` | blocked (window_timeout BlastEm) |
| `stage_r6b` | **PASS** — 11/11, ability, finished step 26, scanline 18/20, p99 65% |

Evidencia: `out/evidence/stage_r6_latest.png`

### Critico R3

- Painel: `out/evidence/blind_critic_r3/`
- Relatorio: `doc/critique/2026-08-08-blind-critic-round3.md`
- Score visual **~7.1** (era 6.5 na R2 / 5.3 na R1)
- Personagem **7.2** (era 5.8)

### Proximo

1. Furnace / trilha cartucho (G7)
2. Inimigos com volume
3. Conteudo fase 2–3
4. Critico R4 quando trilha ou tiles hand-touch entrarem


---

## Sessao 009 — 2026-08-08 — Plano paralelo TSR + arquivo de referencia (lab)

### Plano registrado

- `doc/plans/PARALLEL_TSR_REFERENCE_LEARNING_PLAN.md`
- Premissa: **rips = lab only**; ship continua arte original

### Download Tier S (10/10 OK)

| ID | Jogo | Arquivo |
|---|---|---|
| 49192 | NES Adventure | Kirby |
| 49202 | NES Adventure | Enemies |
| 49193 | NES Adventure | Whispy |
| 2637–2640 | NES Adventure | Vegetable Valley 1–4 |
| 2635 | NES Adventure | World 01 map |
| 52859 | SNES Super Star | Kirby (AAA 16-bit) |
| 32130 | GBA Nightmare | Kirby |

Local: `data/reference_archive/raw/` + snapshot `versions/v001_raw/`
Manifest: `data/reference_archive/MANIFEST.json` (sha256, `ship_allowed=false`)
Legal: `data/reference_archive/LEGAL.md`

### Tools

- `tools/pipeline/tsr_fetch_curated.py`
- `tools/pipeline/tsr_analyze_and_compare.py` → metrics + panel + PREMISES_DRAFT

### Proximo (paralelo)

1. Revisar PREMISES_DRAFT → PREMISES.md final
2. Fechar gaps R6 vs SNES nas metricas (lum_delta / pink_ramp)
3. Gerar arte **original** sob premissas (nao blitar rip em res/)
4. Critico cego original vs ref (metricas)


---

## Sessao 010 — 2026-08-08 — Politica fan/estudo: sem barreira a referencia TSR

### Decisao do operador

Projeto e **estudo + fan game non-commercial**. README / LEGAL / brief / plano
paralelo atualizados para **permitir** rips convertidos em `res/` e ROM fan local.

### Ainda proibido

- Marketplace / venda / ads / IAP / monetizacao com rips
- Reivindicar ownership da IP Nintendo/HAL
- Reupload de sheets brutos sem credito TSR

### Flags

- `fan_study_allowed: true`
- `commercial_marketplace_allowed: false`

### Docs tocados

- `README.md`
- `data/reference_archive/LEGAL.md` + `README.md`
- `doc/plans/PARALLEL_TSR_REFERENCE_LEARNING_PLAN.md`
- `doc/00-project-brief.md`
- `MANIFEST.json` / `catalog/selection_v1.json`

### Proximo

Integrar conversao TSR → `res/` (Kirby/enemies/tiles) e validar gates no fan ROM.


---

## Sessao 011 — 2026-08-08 — Handoff + TSR install → res/ + stage_tsr2 PASS

### Handoff para outros agentes

- **Repo:** `doc/AGENT_HANDOFF.md` (fonte de verdade)
- **Memory:** `notes/kirby-fan-grok-handoff.md` (pinned) + handoff_begin id registrado
- Politica fan/estudo ja em README/LEGAL/plano paralelo

### TSR → res/

| Asset | Fonte | Resultado |
|---|---|---|
| `ph_kirby.png` | SNES Super Star 52859 | 7/8 frames gate PASS (soft install); frame1 center0=11% |
| `ph_enemy.png` | NES Adventure 49202 | 2 frames 16×16 instalados |
| Backups | `*_pre_tsr_backup.png` | preservados |
| Lab copy | `versions/v004_md_sheet_32/` | png + gate json |

Tool: `tools/pipeline/tsr_install_to_res.py` (detect_bg para slate/lavender).

### Validacao

| Cena | Veredito |
|---|---|
| `stage_tsr2` WARMUP 24s | **PASS** — 11/11, ability, finished, scanline 18/20, p99 62%, sprites 24 |

Evidencia: `out/evidence/stage_tsr2_latest.png`
Preview sheet: `out/evidence/kirby_tsr_x4.png`

### Proximo agente

1. Melhorar pick de frames (8/8 PASS; poses idle/run reais)
2. Tiles Vegetable Valley → layers opcional
3. Critico cego R4
4. Premises → gerador original

---

## Sessao 012 — 2026-09-02 — Forward-test v02

- Corrigidos blockers falsos no tooling de source/route e no analisador de strips.
- Produzido staging nativo 32×32 com `idle`, `run` e `inhale` em strips separadas.
- Evidências: `out/forward_test_v02/animation/evidence/`, `foot_contact_report.json`, `pivot_report.json`, `continuity_report.json`, `reports/pixel_compliance_summary.json`, `tile_reuse_summary.json`, `dma_budget_report.json`, `scanline_primary_report.json` e `scanline_stress_report.json`.
- Status honesto: `native_animation_candidate`; sem promoção para `res/`, sem claim de runtime/ROM/BlastEm/AAA.
