#include <genesis.h>
#include "resources.h"
#include "mg/mg_runtime.h"
#include "scenes/fight_stage.h"

#ifndef MG_STAGE_SOURCE_STREAM

/* Physical VRAM allocation, not a reduction of the source art.
 * C000-CFFF B map; E000-EFFF stationary A/WINDOW map;
 * F000-F3FF hscroll; F400-F7FF SAT reservation. */
#define STAGE_MAP_W 42
#define STAGE_MAP_H 32
#define STAGE_MAP_CELLS (STAGE_MAP_W * STAGE_MAP_H)
#define STAGE_BLEED_X 8
#define STAGE_BLEED_Y 16

static u8 sLoaded, sSuper;
static u16 sRestores;
static u8 sHudInvalidation;
static s16 sLastScrollX, sLastScrollY;

#ifdef MG_STAGE_SOURCE_PLANES
static u16 sFarMap[STAGE_MAP_CELLS];
static u16 sNearMap[STAGE_MAP_CELLS];
static u16 sNearBlankMap[STAGE_MAP_CELLS];
#else
static u16 sMap[STAGE_MAP_CELLS];
#endif

static void set_stage_scroll(s16 x, s16 y)
{
    if (x != sLastScrollX) {
        VDP_setHorizontalScroll(BG_B, x);
#ifdef MG_STAGE_SOURCE_PLANES
        VDP_setHorizontalScroll(BG_A, x);
#endif
        sLastScrollX = x;
    }
    if (y != sLastScrollY) {
        VDP_setVerticalScroll(BG_B, y);
#ifdef MG_STAGE_SOURCE_PLANES
        VDP_setVerticalScroll(BG_A, y);
#endif
        sLastScrollY = y;
    }
}

void FIGHT_STAGE_setup(void)
{
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_setWindowAddress(0xE000);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);
    sLoaded = sSuper = 0;
    sRestores = 0;
    sHudInvalidation = 0;
    sLastScrollX = sLastScrollY = 0;
}

#ifdef MG_STAGE_SOURCE_PLANES
static u16 stage_tile_address(const u16 *base, const u16 *count, u16 logical)
{
    for (u16 bank = 0; bank < 4; bank++) {
        if (logical < count[bank]) return base[bank] + logical;
        logical -= count[bank];
    }
    return 0xFFFF;
}

static void load_stage_patterns(const TileSet *farSet, const TileSet *nearSet,
                                const u16 *base, const u16 *count, u16 total)
{
    u16 used = 0;
    for (u16 bank = 0; bank < 4 && used < total; bank++) {
        u16 left = count[bank];
        u16 destination = base[bank];
        while (left && used < total) {
            if (used < farSet->numTile) {
                u16 n = farSet->numTile - used;
                if (n > left) n = left;
                VDP_loadTileData(farSet->tiles + used * 8, destination, n, CPU);
                used += n;
                destination += n;
                left -= n;
            } else {
                u16 nearOffset = used - farSet->numTile;
                u16 n = nearSet->numTile - nearOffset;
                if (n > left) n = left;
                VDP_loadTileData(nearSet->tiles + nearOffset * 8, destination, n, CPU);
                used += n;
                destination += n;
                left -= n;
            }
        }
    }
}

static s16 find_transparent_tile(const TileSet *set)
{
    const u32 *pixels = set->tiles;
    for (u16 tile = 0; tile < set->numTile; tile++) {
        u8 blank = TRUE;
        for (u8 word = 0; word < 8; word++) {
            if (pixels[(u32)tile * 8 + word] != 0) {
                blank = FALSE;
                break;
            }
        }
        if (blank) return (s16)tile;
    }
    return -1;
}

static bool build_stage_map(const TileMap *map, u16 tileOffset,
                            const u16 *base, const u16 *count, u16 *output,
                            u16 blankLogicalTile)
{
    for (u16 i = 0; i < STAGE_MAP_CELLS; i++) {
        const u16 entry = map->tilemap[i];
        const u16 index = entry & TILE_INDEX_MASK;
        const u16 global = stage_tile_address(base, count, tileOffset + index);
        if (global == 0xFFFF) return FALSE;
        output[i] = (entry & TILE_ATTR_MASK) | global;
    }
    if (blankLogicalTile != 0xFFFF) {
        const u16 blankTile = stage_tile_address(base, count, blankLogicalTile);
        if (blankTile == 0xFFFF) return FALSE;
        const u16 blankAttr = TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, blankTile);
        for (u16 i = 0; i < STAGE_MAP_CELLS; i++) sNearBlankMap[i] = blankAttr;
    }
    return TRUE;
}
#endif

bool FIGHT_STAGE_init(u16 lowBase)
{
    const u16 base[4] = { lowBase, TILE_FONT_INDEX, 0xD000 / 32, 0xF800 / 32 };
    const u16 count[4] = { lowBase <= TILE_SPRITE_INDEX ? TILE_SPRITE_INDEX - lowBase : 0,
                          96, 128, 64 };

#ifdef MG_STAGE_SOURCE_PLANES
    const TileSet *farSet = img_suzaku_far.tileset;
    const TileMap *farMap = img_suzaku_far.tilemap;
    const TileSet *nearSet = img_suzaku_near.tileset;
    const TileMap *nearMap = img_suzaku_near.tilemap;
    const u16 total = farSet->numTile + nearSet->numTile;
    const s16 nearBlankLocal = find_transparent_tile(nearSet);
    if (lowBase > TILE_SPRITE_INDEX || farSet->compression || farMap->compression ||
        nearSet->compression || nearMap->compression ||
        farMap->w != STAGE_MAP_W || farMap->h != STAGE_MAP_H ||
        nearMap->w != STAGE_MAP_W || nearMap->h != STAGE_MAP_H ||
        nearBlankLocal < 0 || total > (u16)(count[0] + 288))
        return FALSE;

    load_stage_patterns(farSet, nearSet, base, count, total);
    if (!build_stage_map(farMap, 0, base, count, sFarMap, 0xFFFF) ||
        !build_stage_map(nearMap, farSet->numTile, base, count, sNearMap,
                         (u16)(farSet->numTile + nearBlankLocal)))
        return FALSE;

    PAL_setColors(0, img_suzaku_far.palette->data, 9, CPU);
    VDP_setTileMapDataRect(BG_B, sFarMap, 0, 0, STAGE_MAP_W, STAGE_MAP_H, STAGE_MAP_W, CPU);
    VDP_setTileMapDataRect(BG_A, sNearMap, 0, 0, STAGE_MAP_W, STAGE_MAP_H, STAGE_MAP_W, CPU);
    sHudInvalidation = 1;
#else
    const TileSet *ts = img_suzaku_anchor.tileset;
    const TileMap *tm = img_suzaku_anchor.tilemap;
    if (lowBase > TILE_SPRITE_INDEX || ts->compression || tm->compression ||
        tm->w != STAGE_MAP_W || tm->h != STAGE_MAP_H || ts->numTile > (u16)(count[0] + 288))
        return FALSE;
    u16 used = 0;
    for (u16 bank = 0; bank < 4 && used < ts->numTile; bank++) {
        u16 n = ts->numTile - used;
        if (n > count[bank]) n = count[bank];
        /* Scene loading only: display is disabled by the caller. */
        VDP_loadTileData(ts->tiles + used * 8, base[bank], n, CPU);
        used += n;
    }
    for (u16 i = 0; i < STAGE_MAP_CELLS; i++) {
        const u16 entry = tm->tilemap[i];
        u16 index = entry & TILE_INDEX_MASK;
        if (index >= ts->numTile) return FALSE;
        u16 bank = 0;
        while (bank < 3 && index >= count[bank]) index -= count[bank++];
        sMap[i] = (entry & (TILE_ATTR_HFLIP_MASK | TILE_ATTR_VFLIP_MASK)) | (base[bank] + index);
    }
    PAL_setColors(0, img_suzaku_anchor.palette->data, 9, CPU);
    VDP_setTileMapDataRect(BG_B, sMap, 0, 0, STAGE_MAP_W, STAGE_MAP_H, STAGE_MAP_W, CPU);
#endif

    /* Move the authored anchor back to the viewport; reflected borders cover
     * bounded hit shake. In two-plane mode both layers stay registered. */
    set_stage_scroll(-STAGE_BLEED_X, STAGE_BLEED_Y);
    sLoaded = TRUE;
    return TRUE;
}

void FIGHT_STAGE_update(void)
{
    const u8 active = mg_fight.bgfx_active;
    if (sLoaded && sSuper && !active) {
#ifdef MG_STAGE_SOURCE_PLANES
        VDP_setTileMapDataRect(BG_B, sFarMap, 0, 0, STAGE_MAP_W, STAGE_MAP_H, STAGE_MAP_W, DMA_QUEUE);
        VDP_setTileMapDataRect(BG_A, sNearMap, 0, 0, STAGE_MAP_W, STAGE_MAP_H, STAGE_MAP_W, DMA_QUEUE);
        sHudInvalidation = 1;
#else
        /* Super uses separate tiles. Restore the stage map; PAL0 is restored
         * by bgfx_end, and the queued map source remains valid until VBlank. */
        VDP_setTileMapDataRect(BG_B, sMap, 0, 0, STAGE_MAP_W, STAGE_MAP_H, STAGE_MAP_W, DMA_QUEUE);
#endif
        sRestores++;
    }
#ifdef MG_STAGE_SOURCE_PLANES
    if (sLoaded && !sSuper && active)
        VDP_setTileMapDataRect(BG_A, sNearBlankMap, 0, 0, STAGE_MAP_W, STAGE_MAP_H, STAGE_MAP_W, DMA_QUEUE);
#endif
    if (sLoaded) {
        /* Full-screen super backgrounds own BG_B temporarily and are aligned
         * at the viewport origin. Normal play restores the source anchor and
         * adds the bounded gameplay shake inside reflected edge bleed. */
        const s16 targetX = active ? mg_fight.shake_x : (s16)(-STAGE_BLEED_X + mg_fight.shake_x);
        const s16 targetY = active ? (s16)-mg_fight.shake_y : (s16)(STAGE_BLEED_Y - mg_fight.shake_y);
        set_stage_scroll(targetX, targetY);
    }
    sSuper = active;
}

u16 FIGHT_STAGE_restoreCount(void) { return sRestores; }

bool FIGHT_STAGE_takeHudInvalidation(void)
{
    const bool changed = sHudInvalidation != 0;
    sHudInvalidation = 0;
    return changed;
}

#endif /* !MG_STAGE_SOURCE_STREAM */
