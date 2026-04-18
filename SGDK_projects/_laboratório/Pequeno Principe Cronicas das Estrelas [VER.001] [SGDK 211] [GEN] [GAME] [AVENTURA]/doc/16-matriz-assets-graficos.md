# 16 - Matriz de Assets Graficos

**Versao:** 1.0
**Data:** 2026-03-16
**Contexto:** Fase 1 — Referencia rapida de sprites e TILESETs por cena

> Tabela consolidada para producao e integracao. Detalhes em doc/16-auditoria-placeholders-assets.md,
> doc/17-spec-sprite-player.md, doc/18-spec-tilesets-planetas.md, doc/19-spec-tilesets-ui-travel.md.

---

## 1. SPRITES

| Recurso | Tiles | Paleta | Uso | Cenas |
|---------|-------|--------|-----|-------|
| spr_prince_planet | 16 | PAL2 | Corpo do principe | B-612, Rei, Lampiao, Deserto |
| spr_scarf_segment | 1 | PAL2/PAL3 | Cachecol (5 ou 3 segmentos) | Planetas, viagens |
| spr_halo_quad | 4 | PAL2/PAL3 | Halo de luz | B-612, Lampiao |
| ts_rose_mark (marco) | 4 | PAL3 | Rosa | B-612 |
| ts_throne_mark (marco) | 4 | PAL3 | Trono | Rei |
| ts_lamp_mark (marco) | 4 | PAL3 | Lampiao | Lampiao |
| ts_desert_mark (marco) | 4 | PAL3 | Marco deserto | Deserto |

---

## 2. TILESETs DE CENARIO

| Recurso | Tiles | Paletas | Planos | Cena |
|---------|-------|---------|--------|------|
| ts_b612_bg | 30 | PAL0, PAL1 | BG_A, BG_B | B-612 |
| ts_king_bg | 30 | PAL0, PAL1 | BG_A, BG_B | Rei |
| ts_lamp_bg | 30 | PAL0, PAL1 | BG_A, BG_B | Lampiao |
| ts_desert_bg | 30 | PAL0, PAL1 | BG_A, BG_B | Deserto |
| ts_travel_bg | 20 | PAL0, PAL1 | BG_A, BG_B | Travel |
| ts_ui_panels | 16 | PAL0, PAL2 | BG_A, BG_B, WINDOW | Title, Story, Pause, Codex, Credits, Boot, Dialogos |

---

## 3. RESUMO POR CENA

| Cena | Sprites | TILESETs | Tiles total (max) |
|------|---------|----------|------------------|
| B-612 | prince, scarf, halo, rose_mark | ts_b612_bg | 30 + 4 + 21 = 55 |
| Rei | prince, scarf, throne_mark | ts_king_bg | 30 + 4 + 18 = 52 |
| Lampiao | prince, scarf, halo, lamp_mark | ts_lamp_bg | 30 + 4 + 21 = 55 |
| Deserto | prince, scarf, desert_mark | ts_desert_bg | 30 + 4 + 18 = 52 |
| Travel | (player oculto) | ts_travel_bg | 20 |
| Title/Story/Pause/Codex/Credits/Boot | 0 | ts_ui_panels | 16 |
| Dialogos | 0 | ts_ui_panels | 4 (paper, dither, hatch, fill) |

---

## 4. ORDEM DE PRODUCAO SUGERIDA

1. spr_prince_planet + spr_scarf_segment + spr_halo_quad
2. ts_b612_bg
3. ts_king_bg
4. ts_lamp_bg
5. ts_desert_bg
6. ts_travel_bg
7. ts_ui_panels
