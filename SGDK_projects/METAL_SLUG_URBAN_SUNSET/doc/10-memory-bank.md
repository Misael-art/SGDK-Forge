<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `validation_report.json`
- Ultima sincronizacao: `2026-04-13T22:58:42.6890869-03:00`
- Changelog canonico: `doc/changelog/changelog.md`
- Assets versionados rastreados: 6
- Ultimo build versionado: build_v001
- ROM vigente: `9f4c01bc281220d59cdd34275b4811da459446860bb2fed669bd5bf03f52bd9a` (`131072` bytes)
- Validation summary: errors=0 warnings=2
- Blockers vigentes: visual_gate_blocked, emulator_evidence_stale
- Evidencia de emulador: runtime_metrics_stale
<!-- SGDK GENERATED STATUS END -->
# 10 - Memory Bank & Context Tracker â€” METAL_SLUG_URBAN_SUNSET

**Ultima atualizacao:** 2026-04-13  
**Fase actual:** **Integracao full_core do Marco** (substituicao de placeholder + maquina de estados de animacao em runtime), com build e validacao tecnica OK.

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
- **Player** real `spr_player` (fonte: `res/data/Marco.gif` -> `res/gfx/spr_marco.png`), **PAL3**.
- `SPR_initEx(160)` â€” cobre pico VRAM simultaneo **101** tiles (debris + frame mais pesado do Marco); N maior que 160 quebraria o tecto BG (ver `hardware_budget_review.md`).
- **Validacao de recursos:** correcao de **paleta indice 0** com **alpha = 0** nos PNG 4bpp (evita falso positivo `INDEX0_VISIBLE_HIGH_RISK` do wrapper).
- **Build:** `build.bat` (wrapper) compila com sucesso; `out/rom.bin` gerado.
- **Wrapper:** `tools/sgdk_wrapper/build_inner.bat` passa a **antecipar `java.exe` no PATH** antes do `make` (MSYS/sh nao herdava Java apos winget).
- **Curadoria de rota visual:** `default_multi_plane_method` continua o default travado; o teste antigo `anime_style` foi rejeitado por leitura errada de traco/cor, e a nova referencia correta da familia anime passou a ser `Gemini_Generated_Image_riu4i2riu4i2riu4.png`, ainda em reducao estrutural.
- **Marco pipeline (novo):**
  - Gerador: `tools/image-tools/build_marco_player_sheet.py`
  - Relatorio: `out/logs/spr_marco_report.json`
  - Contrato da sheet: 5 linhas de animacao (`idle`, `walk`, `jump`, `land`, `shoot`) x 6 frames por linha
  - Frame: `40x48 px` (`5x6 tiles`), indexado 4bpp com `PLTE <= 16` e indice `0` transparente.
- **Runtime do player (novo):**
  - Estado explicito: `idle/walk/jump/land/shoot` via `SPR_setAnim`
  - Input: `LEFT/RIGHT` move, `B` jump, `C` shoot, `A` toggle overlay
  - Fisica: gravidade simples, aterragem com janela curta (`land ticks`), flip horizontal por direcao.

### O que e placeholder

- A semantica exata de cada frame do `Marco.gif` original nao vem etiquetada por estado; o mapeamento full_core actual usa selecao curada por componentes da folha fonte.
- Debris sao **recortes** da faixa inferior do `source.png`, nao animacao nem objectos interactaveis.

### Proximos passos sugeridos

- Opcional: **dithering funcional** na cidade (ver `doc/aesthetic_report.md`).
- Se a cidade crescer em largura ou detalhe: **streaming de segmentos** (arquitectura ja documentada em versoes anteriores deste memory bank) ou reducao de crop.
- Fechar estado `bootstrap_degradado: missing_tracked_path` da `.agent` local do projeto.
- Capturar evidencia fresca de emulador para remover `runtime_metrics_stale`.
- Evidencia de emulador fresca (`emulator_session.json` / `runtime_metrics`) apos alteracoes de cena ou novos sprites.
- Se o usuario quiser reabrir a direcao de arte da cena, usar `doc/route_comparison_matrix.md` e `doc/route_decision_record.md` como base; `anime_style` e a rota nova mais forte.

---

## 2. METRICAS DE BUILD (rescomp 2026-04-12 â€” cena estatica 448px)

| Recurso | Tiles unicos (raw/32) |
|---------|------------------------|
| sky_bg_b | 15 |
| city_bg_a | 1246 |
| spr_debris_01 | 28 |
| spr_debris_02 | 26 |
| spr_debris_03 | 24 |
| spr_player | **308** (raw ResComp 9872 bytes / 32 trunc.; sheet full_core `spr_marco.png`) |
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
3. **Indice 0:** no PNG indexado para SGDK, a entrada **0 da paleta deve ter alpha 0** (transparente) quando grandes areas usam indice 0 â€” o validador do wrapper distingue `paletteZeroAlpha`.
4. **Java no PATH do sub-processo MSYS:** se `rescomp` falhar com `java: command not found`, garantir directorio do `java.exe` no PATH **na mesma sessao** que invoca `make` (ver `build_inner.bat`).
5. **Prancha editorial:** nunca quantizar `source.png` inteiro â€” seguir `semantic_parse_report` (DROP mockup/creditos).
6. Se **margem BG < ~10 tiles**: parar de adicionar detalhe ou activar streaming / `compare_flat`.






