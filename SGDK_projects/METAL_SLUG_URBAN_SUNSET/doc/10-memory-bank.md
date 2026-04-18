<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `validation_report.json`
- Ultima sincronizacao: `2026-04-17T10:51:44.3290851-03:00`
- Changelog canonico: `doc/changelog/changelog.md`
- Assets versionados rastreados: 10
- Ultimo build versionado: build_v005
- ROM vigente: `22398477a18be069243b612daaa0e1b197cfae7d618353b900ab40a06a957e05` (`262144` bytes)
- Validation summary: errors=0 warnings=1
- Blockers vigentes: gameplay_gate_incomplete
- Evidencia de emulador: ok
- Gate visual: visual_lab_aprovado=True
- Gate gameplay: gameplay_rom_aprovada=False
- Gate AAA: ready_for_aaa=False
- QA runtime: gameplay=funcional performance=nao_testado audio=nao_testado hardware_real=nao_testado
<!-- SGDK GENERATED STATUS END -->
# 10 - Memory Bank & Context Tracker Ã¢â‚¬â€ METAL_SLUG_URBAN_SUNSET

**Ultima atualizacao:** 2026-04-17  
**Fase actual:** **Viewer comparativo em ROM** (URBAN SUNSET + MISSION 1, 3 variantes por cena), com fila `needs_review` zerada, build OK, evidencia BlastEm rastreavel e gate final semanticamente separado entre laboratorio visual e ROM jogavel.

> **DIRETRIZ:** Este e o bloco de memoria primario do projeto.  
> Leia integralmente antes de qualquer codigo ou decisao.  
> Atualize ao encerrar sessoes relevantes.

---

## 1. ESTADO ACTUAL DO PROJECTO

### O que existe e funciona

- **Fluxo de arte alinhado ao plano:** `doc/semantic_parse_report.md`, `doc/composition_deliverables.md`, `doc/translation_report.md`, `doc/aesthetic_report.md`, `doc/hardware_budget_review.md`.
- **Viewer atual sem sprites/gameplay:** `src/main.c` foi convertido para um exibidor de cenas usando apenas `BG_A + BG_B + WINDOW`, com controles `LEFT/RIGHT` scroll, `A` troca de cena, `B` troca de variante, `C` overlay e `START` reset.
- **Cena 1 â€” URBAN SUNSET:** 3 variantes navegaveis
  - `default_multi_plane_method`
  - `anime_linefirst_balanced`
  - `anime_linefirst_cohesive`
- **Cena 2 â€” MISSION 1:** 3 variantes navegaveis
  - `flat_strict15`
  - `flat_snap700`
  - `default_skylift`
- **Budget do viewer:** a remocao de sprites elevou o tecto util de BG para aproximadamente **1424 tiles user** (`1536 - 16 sistema - 96 fonte`), viabilizando as seis variantes dentro da ROM comparativa.
- **Normalizacao de assets SGDK:** `tools/image-tools/normalize_indexed_sgdk_png.py` foi criado para:
  - compactar `PLTE` inflada sem alterar o resultado visual
  - promover `index 0` para transparencia estrutural quando necessario
  - reservar `index 0` como slot opaco nao usado nos flats que nao dependem de alpha
- **Validacao de recursos:** os blockers `PALETTE_INFLATED` e `INDEX0_VISIBLE_HIGH_RISK` do viewer foram eliminados; `validate_resources.ps1` agora fecha com **0 erros**.
- **Build:** `build.bat` (wrapper) compila com sucesso; ROM vigente `build_v005`, `out/rom.bin`, `sha256 = 22398477a18be069243b612daaa0e1b197cfae7d618353b900ab40a06a957e05`.
- **Evidencia BlastEm:** `blastem_gate = true` apos sessao coerente com a ROM atual; capturas manuais rastreaveis em:
  - `out/captures/viewer_urban_default_20260417_pw.png`
  - `out/captures/viewer_urban_linefirst_cohesive_20260417_pw.png`
  - `out/captures/viewer_mission1_flat_snap700_20260417_pw.png`
  - `out/captures/viewer_mission1_default_skylift_20260417_pw.png`
- **Wrapper:** `tools/sgdk_wrapper/build_inner.bat` passa a **antecipar `java.exe` no PATH** antes do `make` (MSYS/sh nao herdava Java apos winget).
- **Curadoria de rota visual:** `default_multi_plane_method` continua o default travado; o teste antigo `anime_style` foi rejeitado por leitura errada de traco/cor, e a nova referencia correta da familia anime passou a ser `Gemini_Generated_Image_riu4i2riu4i2riu4.png`, ainda em reducao estrutural.
- **Anime line-first pipeline (novo):**
  - Gerador canonico: `tools/image-tools/generate_linefirst_anime_route.py`
  - Processo: `crop -> anime style -> line art only -> promocao Mega Drive do traco -> pintura inteligente por massas`
  - Perfil `balanced`: `1261` tiles totais (`1260 + 1`), score `0.7184`
  - Perfil `cohesive`: `1248` tiles totais (`1243 + 5`), score `0.6988`
  - Estado: primeira familia anime do projeto a fechar budget de forma reproduzivel; ainda depende de congelamento humano para substituir o default
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

- O viewer atual e uma ROM de comparacao visual; ele nao representa ainda a volta do gameplay com player, debris ou HUD final.
- O overlay do viewer cumpre papel tecnico de comparacao, mas ainda nao e uma apresentacao polida de benchmark.
- O viewer atual segue como **laboratorio visual aprovado** (`visual_lab_aprovado=True`), mas ainda **nao** prova ROM jogavel fechada: `performance`, `audio` e `hardware_real` continuam `nao_testado`, portanto `gameplay_rom_aprovada=False` e `ready_for_aaa=False`.

### Proximos passos sugeridos

- Decidir quais variantes do viewer devem ser promovidas para a proxima integracao jogavel.
- Reintegrar gameplay numa cena separada, sem perder o viewer como prova canÃ´nica de curadoria.
- Se o usuario quiser uma prova mais forte do `MISSION 1`, capturar tambem `default_skylift` e/ou `flat_strict15` dentro do BlastEm com navegacao automatizada.
- Capturar `runtime_metrics.json` e evidencia de audio/hardware_real quando a cena jogavel voltar, para transformar o viewer aprovado em gate completo de ROM.
- Se a composicao final voltar a incluir sprites, recalcular budget da cena jogavel fora do viewer sem reaproveitar cegamente o teto de 1424 tiles.

---

## 2. METRICAS DE BUILD (viewer comparativo 2026-04-16)

| Recurso | Tiles unicos (raw/32) |
|---------|------------------------|
| urban_default | 15 (BG_B) + 1291 (BG_A) = **1306** |
| urban_linefirst_balanced | 1 (BG_B) + 1260 (BG_A) = **1261** |
| urban_linefirst_cohesive | 5 (BG_B) + 1243 (BG_A) = **1248** |
| mission1_flat_strict15 | 5 (BG_B) + 1363 (BG_A) = **1368** |
| mission1_flat_snap700 | 5 (BG_B) + 1239 (BG_A) = **1244** |
| mission1_default_skylift | 5 (BG_B) + 1317 (BG_A) = **1322** |
| **Tecto user BG do viewer** | **~1424** |

Paletas activas por variante: **PAL0** BG_B, **PAL1** BG_A. O viewer atual nao reserva `PAL2/PAL3` porque nao usa sprites.

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
3. **Indice 0:** no PNG indexado para SGDK, a entrada **0 da paleta deve ter alpha 0** (transparente) quando grandes areas usam indice 0 Ã¢â‚¬â€ o validador do wrapper distingue `paletteZeroAlpha`.
4. **Java no PATH do sub-processo MSYS:** se `rescomp` falhar com `java: command not found`, garantir directorio do `java.exe` no PATH **na mesma sessao** que invoca `make` (ver `build_inner.bat`).
5. **Prancha editorial:** nunca quantizar `source.png` inteiro Ã¢â‚¬â€ seguir `semantic_parse_report` (DROP mockup/creditos).
6. Se **margem BG < ~10 tiles**: parar de adicionar detalhe ou activar streaming / `compare_flat`.






















