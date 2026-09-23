# AGENT HANDOFF — KIRBY_FAN GAME GROK BUILD

**Atualizado:** 2026-08-08 (pós stage_tsr2)
**Projeto root:**

```
/mnt/sdcard/Projects/Sgdk Forge/SGDK_projects/KIRBY_FAN GAME GROK BUILD [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]
```

Qualquer agente que retome o trabalho: **leia este arquivo primeiro**, depois
`README.md`, `data/reference_archive/LEGAL.md`, e o plano paralelo.

---

## 1. O que é o projeto

| | |
|---|---|
| Tipo | **Estudo + fan game non-commercial** (Mega Drive / SGDK 2.11) |
| Base | Reimaginação de *Kirby's Adventure* (NES) |
| Stack | C + SGDK, wine bridge build, BlastEm harness |
| IP | Kirby = Nintendo/HAL; projeto **não** é comercial/marketplace |

### Política de assets (decisão do operador, 2026-08-08)

| Flag | Valor |
|---|---|
| `fan_study_allowed` | **true** |
| `commercial_marketplace_allowed` | **false** |

- Rips do **Spriters Resource** convertidos para MD **podem** ir a `res/` e à ROM fan.
- **Proibido:** marketplace, venda, ads, IAP, monetização com rips.
- Docs: `README.md`, `data/reference_archive/LEGAL.md`, `doc/00-project-brief.md`.

---

## 2. Estado técnico atual

### Gates / ROM

| Item | Estado |
|---|---|
| `out/rom.bin` | Builda (wine bridge) |
| Último PASS visual | `stage_r6b` — 11/11 loco, scanline 18/20, p99 ~65% |
| Evidência | `out/evidence/stage_r6_latest.png` |
| Critico visual | ~**7.1**/10 (R6); personagem 7.2; ainda abaixo Celestial Chase |

### Arte na ROM agora

| Asset | Origem atual | Path |
|---|---|---|
| Kirby | **TSR SNES Super Star convertido** (7/8 gate PASS soft) | `res/sprites/ph_kirby.png` 256×32; backup `ph_kirby_pre_tsr_backup.png` |
| BG layers | R5 density | `res/gfx/ph_{sky,mount,forest,hills,terrain}.png` |
| Forest G5 | Plane B mid-band, scroll `camX>>2` | `ph_forest.png` + `raster.c` |
| Dust G6 | Pool 2, land/dash, life 18 | `ph_particle.png` + `particle.c` |
| Enemy | **TSR NES enemies convertido** | `ph_enemy.png` 32×16; backup `ph_enemy_pre_tsr_backup.png` |

### Anim Kirby (`kirby.c`)

```
frame 0 = idle
1–4   = run
5     = jump
6–7   = float (6+animFrame) / inhale shares 7
```

`resources.res`: `SPRITE spr_ph_kirby ... 4 4` (= 32×32 cell).

### Parallax (medido gates)

`camera_x=9` → sky 0, mount −1, hill −3, terrain −9
Forest band: lines 104–143, `scrollForest = camX>>2`.

---

## 3. Arquivo de referência TSR (Tier S — 10/10 baixados)

Path: `data/reference_archive/`

| ID | Arquivo | Role |
|---|---|---|
| 49192 | `raw/nes_kirby_adventure/49192_kirby.png` | Kirby NES |
| 49202 | `.../49202_enemies.png` | Enemies |
| 49193 | `.../49193_whispy.png` | Whispy |
| 2637–2640 | Vegetable Valley 1–4 | Stage tiles |
| 2635 | World 01 map | Overview |
| 52859 | `raw/snes_kirby_super_star/52859_kirby.png` | Kirby AAA 16-bit |
| 32130 | `raw/gba_nightmare_dreamland/32130_kirby.png` | Kirby GBA |

- Manifest + sha256: `MANIFEST.json`
- Snapshot: `versions/v001_raw/`
- Metrics: `compare/metrics_v001.json`
- Panel: `compare/ours_r6_vs_ref_kirby_panel.png`
- Premises draft: `premises/PREMISES_DRAFT.md`
- Plano: `doc/plans/PARALLEL_TSR_REFERENCE_LEARNING_PLAN.md` (v1.1)

### Tools pipeline

```bash
python3 tools/pipeline/tsr_fetch_curated.py
python3 tools/pipeline/tsr_analyze_and_compare.py
python3 tools/pipeline/tsr_install_to_res.py          # instalar convertidos → res/
python3 tools/pipeline/build_kirby_procedural.py --install
python3 tools/pipeline/build_dreamland_layers.py --install
```

### Build + gates

```bash
export WARMUP_SECONDS=22   # playtest precisa ≥~16s; 22–26 seguro
bash tools/harness/build_and_capture.sh stage_NAME 5
# scene ids: 4 STAGE, 5 STAGE_PLAYTEST, 6 BOSS, 7 BOSS_PLAYTEST, 9 TITLE
```

Wine bridge (único build Linux estável):

```bash
bash "/mnt/sdcard/Projects/Sgdk Forge/tools/sgdk_wrapper/build_sgdk_wine_bridge.sh" \
  --project-root "<PROJECT_ROOT>"
```

---

## 4. Contratos que não quebrar (lessons)

| ID | Regra |
|---|---|
| L-001 | Build só via wine bridge (PATH `cp.exe` quebra wrapper nativo) |
| L-011 | Índices de paleta **absolutos** 0..15; stamp full palette no PNG |
| L-012/013 | Index 0 = key; key = magenta alto R/B baixo G — **não** comer rosa do corpo |
| PAL0/1 | Masters: `res/gfx/pal0_master.png`, `pal1_master.png` — CRAM runtime |
| Scanline | ≤20 sprites/line; dust pool=2, FG tufts=2 |
| S/H | Global ON; tiles priority=1 |
| Gates | Nunca enfraquecer teste; `ruff` N/A aqui (C project) |

PAL2 Kirby (doc/PALETTES.md):
0 key, 1–5 pink ramp, 6 outline, 7–8 feet, 9 eye, 10 white.

---

## 5. Próximos passos (ordem)

### P4 — FEITO (parcial, 2026-08-08)

1. ~~`tsr_install_to_res.py`~~ SNES Kirby → res (7/8 PASS soft install); NES enemies → res
2. ~~`stage_tsr2` gates **PASS**~~ — evidência `out/evidence/stage_tsr2_latest.png`
3. **Próximo:** re-pick frame1 (center hollow) para 8/8 PASS; crop tiles VV; critic R4


### Depois

| # | Item |
|---|---|
| P5 | Premises finais + gerador original batendo métricas SNES |
| P6 | Tiles VV convertidos para parallax (sem estourar VRAM) |
| P7 | Whispy sheet real no boss |
| P8 | Furnace trilha (G7) |
| P9 | Conteúdo fase 2–3 |
| P10 | Critico cego R4 (original/ref vs Celestial) |

---

## 6. Arquivos quentes (tocados nas sessões recentes)

```
README.md
doc/00-project-brief.md
doc/plans/PARALLEL_TSR_REFERENCE_LEARNING_PLAN.md
doc/AGENT_HANDOFF.md                    ← este arquivo
doc/critique/2026-08-08-blind-critic-round{1,2,3}.md
data/reference_archive/**/*
tools/pipeline/tsr_fetch_curated.py
tools/pipeline/tsr_analyze_and_compare.py
tools/pipeline/tsr_install_to_res.py
tools/pipeline/build_kirby_procedural.py
tools/pipeline/build_dreamland_layers.py
src/entities/particle.c + inc/entities/particle.h
src/system/playtest.c                   # hop final para dust no frame
src/scenes/scene_stage.c                # G5 forest + G6 dust
src/systems/raster.c                    # BAND_FOREST, scrollForest
res/sprites/ph_kirby.png
res/gfx/ph_*.png
CHANGES.md
```

---

## 7. Critérios de sucesso para o próximo agente

| Gate | Critério |
|---|---|
| Política | Não reintroduzir barreira “só original” no fan study |
| Install | Sheet Kirby idx0 safe (center hollow <5%, opaque >35%) |
| ROM | `gates.py` VERDICT PASS em stage_playtest (cena 5) |
| Visual | Screenshot em `out/evidence/stage_tsr*_latest.png` |
| Log | Sessão em `CHANGES.md` |
| Handoff | Atualizar **este** `AGENT_HANDOFF.md` se o estado mudar |

---

## 8. Comandos de sanidade (1 min)

```bash
cd "<PROJECT_ROOT>"
test -f data/reference_archive/MANIFEST.json && echo MANIFEST_OK
python3 -c "import json; m=json.load(open('data/reference_archive/MANIFEST.json')); print('fan', m.get('fan_study_allowed'), 'assets', len(m.get('assets',[])))"
ls res/sprites/ph_kirby.png res/gfx/ph_forest.png
# rebuild smoke
export WARMUP_SECONDS=22
bash tools/harness/build_and_capture.sh stage_handoff_smoke 5
```

---

## 9. Histórico de scores (honesto)

| Marco | Visual |
|---|---|
| R1 placeholder | 5.3 |
| R2 G5 forest + critic | 6.5 |
| R5 density | ~7.0 |
| R6 Kirby procedural volume | ~7.1 |
| TSR install (meta) | ≥7.5 se sheet SNES/NES bem convertido |

---

*Fim do handoff. Atualize a data no topo quando retomar.*


## 10. Nota técnica install TSR

- Sheet NES bg ≈ (84,110,140); SNES bg ≈ (128,128,255). `detect_bg()` no instalador.
- Blob BFS em `tsr_install_to_res.py`; frame1 às vezes FAIL center idx0 — re-sample blobs.
- Soft install se ≥6/8 frames PASS.
