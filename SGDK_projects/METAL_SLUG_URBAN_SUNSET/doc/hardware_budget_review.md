# Hardware Budget Review — METAL_SLUG_URBAN_SUNSET (medicao rescomp)

**Data:** 2026-04-12  
**Fonte de verdade:** `out/logs/build_output.log` (ResComp 3.95, `IMAGE`/`SPRITE` BEST)

---

## Formula (SGDK 2.11, maps_addr = 0xC000)

```
TILE_MAX_NUM     = 0xC000 / 32 = 1536
User tiles (BG)  = 1536 - 16 (sistema) - 96 (fonte) - SPR_initEx(N)
```

**Configuracao actual:** `VDP_setPlaneSize(64, 32)`, `SPR_initEx(160)`

```
User tiles para fundos = 1536 - 112 - 160 = 1264 tiles
```

---

## Tiles unicos por recurso (tileset raw = bytes / 32)

| Recurso | Bytes raw tileset | Tiles unicos |
|---------|-------------------|--------------|
| sky_bg_b | 480 | **15** |
| city_bg_a | 39 872 | **1246** |
| spr_debris_01 | 896 | 28 |
| spr_debris_02 | 832 | 26 |
| spr_debris_03 | 768 | 24 |
| spr_player | 640 | 20 |

**Soma BG_B + BG_A:** 15 + 1246 = **1261 tiles**

**Margem vs tecto de fundo (1264):** **3 tiles** — apertado mas **cabe**.

**Sprites (regiao SPR_initEx):** 28 + 26 + 24 + 20 = **98 tiles** (reserva 160 → margem **62**).

---

## Decisao

**`cabe`** — A soma `BG_B + BG_A` nao excede `User tiles` com `SPR_initEx(160)`.

**Recuos ja aplicados:**

1. Cidade limitada a **448 px** de conteudo util (padding transparente a 512 px para o plano).
2. Ceiu **bandado** para **15 tiles** unicos.
3. `SPR_initEx(160)` em vez de 128 para margem de sprites (3 debris 64x48 + player).

**Sinais monitorados:**

- `MANUAL_VRAM_PARTITION_CANDIDATE`: qualquer aumento de detalhe em `city_bg_a` pode estourar o tecto; medir rescomp antes de promover arte nova.
- Se `BG_A` ultrapassar ~1260 tiles: considerar **streaming de segmentos** ou `compare_flat` (ver `doc/composition_deliverables.md`).

---

## VDP sprites por frame (metadados rescomp)

| Sprite | VDP sprites (links) | Tiles |
|--------|---------------------|-------|
| spr_debris_01 | 2 | 28 |
| spr_debris_02 | 3 | 26 |
| spr_debris_03 | 2 | 24 |
| spr_player | 2 | 20 |

Total links na SAT: verificar scanline pressure em cenas com mais entidades; para esta demo, aceitavel.
