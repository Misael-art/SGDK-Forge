# 22 - Plano de Producao de Assets Refatorados

**Data:** 2026-03-16
**Contexto:** Arquivamento dos assets atuais e refatoracao completa conforme `doc/15-diretrizes-producao-assets.md`

---

## 1. ARQUIVO EXECUTADO

- **Arquivo:** `archives/asset_batches/20260316-054318_arquivo_diretoes/`
- **Manifest:** `ARCHIVE_MANIFEST.txt`
- **Script de copia:** `archive_res_assets.ps1` (executar se res/ existir com arquivos)

---

## 2. ASSETS A REFAZER (ordem de producao)

### 2.1. Prioridade 1 — Marcos e paleta (usados em resources.res)

| Asset | Dimensoes | Spec | Diretrizes doc/15 |
|-------|-----------|------|-------------------|
| pal_sprite_stage | 16x1 (ref) | 16 cores, index 0 = #FF00FF | Secao 3.2, 3.4 |
| rose_mark | 16x16 | 4 tiles, contorno sepia | Secao 2.4, 3.5 |
| throne_mark | 16x16 | 4 tiles, contorno sepia | Secao 2.4, 3.5 |
| lamp_mark | 16x16 | 4 tiles, contorno sepia | Secao 2.4, 3.5 |
| desert_mark | 16x16 | 4 tiles, contorno sepia | Secao 2.4, 3.5 |

### 2.2. Prioridade 2 — Player (corpo, cachecol, halo)

| Asset | Dimensoes | Spec |
|-------|-----------|------|
| pp_player_body | 16x24 ou 24x32 | doc/17-spec-sprite-player.md |
| pp_player_scarf | 8x8 | 1 tile segmento |
| pp_player_halo | 16x16 | 4 tiles, 2x2 |

### 2.3. Prioridade 3 — UI e orbit

| Asset | Dimensoes | Spec |
|-------|-----------|------|
| pp_ui_panels | 32x16 | doc/19-spec-tilesets-ui-travel.md |
| pp_orbit_icons | 32x8 | Icones B,R,V,O,H,A,G,S,D,J,P,C |

### 2.4. Prioridade 4 — Boards (referencia) e cenario

| Asset | Dimensoes | Uso |
|-------|-----------|-----|
| board_* | 320x224 | Conceito por cena |
| ts_b612_bg, ts_king_bg, etc. | 30 tiles | doc/18-spec-tilesets-planetas.md |

---

## 3. CHECKLIST DE CONFORMIDADE (doc/15 secao 7)

Para cada asset:

- [ ] Gate 1: Compatibilidade com cena e concept art
- [ ] Gate 2: PNG/BMP indexado, 16 cores, index 0 = #FF00FF, multiplos de 8
- [ ] Gate 3: Bordas nitidas, sem AA, dithering intencional
- [ ] Gate 4: Sem drop shadow, glow, checkerboard, grade
- [ ] Gate 5: Bounding box apertado, budget VRAM
- [ ] Gate 6: Barra de paleta, mapa de indices, dimensoes

---

## 4. PIPELINE

```
1. Gerar PNG em tmp/imagegen/inbox/pequeno_principe_v2/production/
   (prompt: tmp/imagegen/PROMPT_AGENTE_ASSETS_PEQUENO_PRINCIPE.md)

2. Redimensionar e indexar:
   python tools/image-tools/resize_and_index_pequeno_principe_batch.py

3. Validar:
   tools/image-tools/validate_pequeno_principe_asset_batch.ps1

4. Promover (se PASS):
   tools/image-tools/promote_pequeno_principe_asset_batch.ps1

5. Atualizar resources.res se novos recursos forem declarados
```

---

## 5. AUDIO

Os 8 WAVs (4 vozes + 4 SFX) nao sao regidos por doc/15. Manter os atuais ou substituir conforme necessidade de qualidade. Nao arquivar audio se nao houver alteracao planejada.
