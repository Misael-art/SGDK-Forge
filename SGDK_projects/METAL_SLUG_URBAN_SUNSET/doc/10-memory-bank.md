# 10 - Memory Bank & Context Tracker — METAL_SLUG_URBAN_SUNSET

**Ultima atualizacao:** 2026-04-12  
**Fase actual:** **Pipeline de skills (Jornada de Mestria)** — diagnostico, composicao multi-plano, traducao semantica do `source.png`, excelencia visual, budget VDP, integracao SGDK e **build OK** com ROM estatica (sem streaming de strips).

> **DIRETRIZ:** Este e o bloco de memoria primario do projeto.  
> Leia integralmente antes de qualquer codigo ou decisao.  
> Atualize ao encerrar sessoes relevantes.

---

## 1. ESTADO ACTUAL DO PROJECTO

### O que existe e funciona

- **Fluxo de arte alinhado ao plano:** `doc/semantic_parse_report.md`, `doc/composition_deliverables.md`, `doc/translation_report.md`, `doc/aesthetic_report.md`, `doc/hardware_budget_review.md`.
- **BG_B** (`sky_bg_b.png`): gradiente sunset **bandado** 256x224, **15 tiles** unicos (rescomp), parallax **0.25x**.
- **BG_A** (`city_bg_a.png`): cidade 512x224 (**448 px** uteis + padding transparente), **1246 tiles** unicos, parallax **1.0x**, topo transparente sobre o ceu.
- **Layer C (foreground composicional):** tres sprites `spr_debris_01/02/03` (64x48, 8x6 celulas), **PAL2**, parallax **1.25x** (`gCameraX + (gCameraX >> 2)`).
- **Player** placeholder `spr_player`, **PAL3**.
- `SPR_initEx(160)` para acomodar debris + jogador com margem.
- **Validacao de recursos:** correcao de **paleta indice 0** com **alpha = 0** nos PNG 4bpp (evita falso positivo `INDEX0_VISIBLE_HIGH_RISK` do wrapper).
- **Build:** `build.bat` (wrapper) compila com sucesso; `out/rom.bin` gerado.
- **Wrapper:** `tools/sgdk_wrapper/build_inner.bat` passa a **antecipar `java.exe` no PATH** antes do `make` (MSYS/sh nao herdava Java apos winget).

### O que e placeholder

- Silhueta do jogador (`player_placeholder.png`).
- Debris sao **recortes** da faixa inferior do `source.png`, nao animacao nem objectos interactaveis.

### Proximos passos sugeridos

- Opcional: **dithering funcional** na cidade (ver `doc/aesthetic_report.md`).
- Se a cidade crescer em largura ou detalhe: **streaming de segmentos** (arquitectura ja documentada em versoes anteriores deste memory bank) ou reducao de crop.
- Corrigir **Python no PATH** do processo de validacao (wrapper chama `analyze_aesthetic.py`; alias da Store devolve 9009).
- Corrigir invocacao **ImageMagick** no validador (erro `O termo 'C' nao e reconhecido` — path / cmdlet).

---

## 2. METRICAS DE BUILD (rescomp 2026-04-12 — cena estatica 448px)

| Recurso | Tiles unicos (raw/32) |
|---------|------------------------|
| sky_bg_b | 15 |
| city_bg_a | 1246 |
| spr_debris_01 | 28 |
| spr_debris_02 | 26 |
| spr_debris_03 | 24 |
| spr_player | 20 |
| **BG_B + BG_A** | **1261** |
| **Tecto user BG** (SPR_initEx 160) | **1264** |
| **Margem BG** | **3 tiles** |

Paletas: **PAL0** ceu, **PAL1** cidade, **PAL2** debris (paleta partilhada entre os 3 PNG), **PAL3** player.

---

## 3. BUDGET VRAM (resumo)

Ver **`doc/hardware_budget_review.md`** para a decisao formal **`cabe`** e tabela completa.

---

## 4. REFERENCIAS RAPIDAS

- Composicao: `doc/composition_deliverables.md`
- Semantica source: `doc/semantic_parse_report.md`
- Traducao: `doc/translation_report.md`
- Julgamento estetico: `doc/aesthetic_report.md`
- Budget: `doc/hardware_budget_review.md`
- GDD: `doc/11-gdd.md`
- Spec cenas: `doc/13-spec-cenas.md`

---

## 5. LICCOES APRENDIDAS (ANTI-REGRESSAO)

1. **Orcar com rescomp:** `tileset_data` raw size / 32 = tiles unicos do `IMAGE`/`SPRITE`.
2. **1536 - 16 - 96 - SPR_initEx(N)** e o tecto real para **soma BG_A + BG_B** antes de corrupcao.
3. **Indice 0:** no PNG indexado para SGDK, a entrada **0 da paleta deve ter alpha 0** (transparente) quando grandes areas usam indice 0 — o validador do wrapper distingue `paletteZeroAlpha`.
4. **Java no PATH do sub-processo MSYS:** se `rescomp` falhar com `java: command not found`, garantir directorio do `java.exe` no PATH **na mesma sessao** que invoca `make` (ver `build_inner.bat`).
5. **Prancha editorial:** nunca quantizar `source.png` inteiro — seguir `semantic_parse_report` (DROP mockup/creditos).
6. Se **margem BG < ~10 tiles**: parar de adicionar detalhe ou activar streaming / `compare_flat`.
