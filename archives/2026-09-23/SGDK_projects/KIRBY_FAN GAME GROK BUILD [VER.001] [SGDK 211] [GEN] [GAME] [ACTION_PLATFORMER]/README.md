# KIRBY_FAN GAME GROK BUILD

**Projeto de estudo e fan game non-commercial** — reimaginação de
*Kirby's Adventure* (NES) para **SEGA Mega Drive / Genesis** (SGDK 2.11).

Kirby e personagens relacionados são propriedade da **Nintendo / HAL Laboratory**.
Este repositório **não é um produto comercial**, não será vendido, não terá ads/IAP
e não será publicado em marketplace (Steam, App Store, etc.) sob este status.

## Política de assets (fan / estudo)

| Fonte | Permitido neste projeto? |
|---|---|
| Arte **original** (procedural, Imagine, hand) | sim |
| Referência / sheets do [Spriters Resource](https://www.spriters-resource.com/) convertidos para MD | **sim** (estudo + fan build local) |
| Rips em build **comercial** / marketplace / monetizado | **não** (ToU TSR + copyright) |

- Arquivo de referência: `data/reference_archive/` (proveniência + hashes).
- Legal detalhado: `data/reference_archive/LEGAL.md`.
- Plano de aprendizado gráfico: `doc/plans/PARALLEL_TSR_REFERENCE_LEARNING_PLAN.md`.
- Crédito de origem: The Spriters Resource + jogo/fonte de cada sheet (manifesto).

Objetivo da trilha de referência: **aprender construção gráfica AAA**, calibrar
pipeline RGB333/4bpp, e (quando útil) integrar conversões no `res/` para o fan
ROM de estudo — sem barreira interna de “só arte original” neste contexto.

| Campo | Valor |
|---|---|
| Stack | SGDK 2.11, C + asm68k quando necessário, make via wine bridge |
| Gênero | ACTION_PLATFORMER |
| ROM | `out/rom.bin` (≤ 4 MB, sem mapper) — fan/estudo |
| Video | 320×224 NTSC @ 60 Hz |
| Audio | XGM2 (YM2612 + PSG + PCM 13.3/6.65 kHz) |

## Estado honesto (2026-08-08)

| Fase | Status |
|---|---|
| **FASE 0** contratos | **Feita** — `doc/ARCHITECTURE.md`, `VRAMMAP.md`, `PALETTES.md`, `SOUNDMAP.md` |
| **FASE 1** protótipo | **Buildado + testado em emulador** — título → fase → boss → game over |
| **FASE 3** harness | **Operacional** — BlastEm + `gates.py` |
| **FASE 2** arte | R4–R6 original + **arquivo TSR Tier S** (10 assets) + plano paralelo |
| Gates stage recentes | **PASS** (`stage_r6b`, scanline 18/20, p99 ~65%) |

Ainda não é AAA comercial: critic visual ~7.1; trilha ainda procedural; conteúdo 1 fase.

## Como buildar (Linux, este host)

```bash
bash /mnt/sdcard/Projects/Sgdk\ Forge/tools/sgdk_wrapper/build_sgdk_wine_bridge.sh \
  --project-root "/mnt/sdcard/Projects/Sgdk Forge/SGDK_projects/KIRBY_FAN GAME GROK BUILD [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]"
```

Ver `LESSONS.md` L-001 (PATH/`cp.exe`).

## Como capturar + gates

```bash
bash tools/harness/build_and_capture.sh title_smoke
bash tools/harness/build_and_capture.sh stage_playtest 5
bash tools/harness/build_and_capture.sh boss_playtest 7
```

| id | cena |
|---|---|
| 4 | STAGE |
| 5 | STAGE_PLAYTEST |
| 6 | BOSS |
| 7 | BOSS_PLAYTEST |
| 8 | GAMEOVER |
| 9 | TITLE |

## Pipeline de arte

```
# Original / gerado
data/source_art/ai_raw/ … tools/pipeline/build_kirby_procedural.py

# Referência TSR (estudo + fan)
python3 tools/pipeline/tsr_fetch_curated.py
python3 tools/pipeline/tsr_analyze_and_compare.py
# instalação em res/ para fan build: tools/pipeline/tsr_install_to_res.py (quando existir)
```

Ordem MD (PALETTES.md): reduzir cores → snap RGB333 → 4 bpp; index 0 = key.

## Documentos de autoridade

1. `doc/10-memory-bank.md` — estado operacional
2. `doc/ARCHITECTURE.md` / `VRAMMAP.md` / `PALETTES.md` / `SOUNDMAP.md`
3. `doc/plans/PARALLEL_TSR_REFERENCE_LEARNING_PLAN.md` — trilha referência
4. `data/reference_archive/LEGAL.md` — copyright + ToU
5. `CHANGES.md` / `LESSONS.md`

## Relação com CLOUDE

Prior art no forge: `KIRBY_FAN GAME CLOUDE [...]`. GROK BUILD herda arquitetura
e harness; evidência e arte vivem nesta árvore.
