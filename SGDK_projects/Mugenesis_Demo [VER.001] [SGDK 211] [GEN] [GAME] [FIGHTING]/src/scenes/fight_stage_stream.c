#ifdef MG_STAGE_SOURCE_STREAM

#include <genesis.h>
#include "resources.h"
#include "mg/mg_runtime.h"
#include "scenes/fight_stage.h"
#include "scenes/suzaku_stream_maps_generated.h"
#include "scenes/suzaku_stream_camera_generated.h"

#define STREAM_WORLD_W       128
#define STREAM_WORLD_H       32
#define STREAM_PLANE_W       64
#define STREAM_PLANE_H       32
#define STREAM_VISIBLE_H     224
#define STREAM_VISIBLE_W     320
#define STREAM_HUD_Y0        200
#define STREAM_HUD_Y1        216
#define STREAM_MAX_CACHE     1024
#define STREAM_INVALID       0xFFFF
#define STREAM_FIXED_BANKS   4
#define STREAM_MAP_CELLS     (STREAM_PLANE_W * STREAM_PLANE_H)

/* The hardware maps stay 64x32 at C000/E000. HScroll and SAT own F000/F400;
 * the larger 128x32 source maps and their 1608 canonical patterns live in ROM. */
static u8 sLoaded, sSuper, sHudInvalidation;
static u8 sRowVisible[2][STREAM_PLANE_H];
static s16 sRowLeft[2][STREAM_PLANE_H], sRowRight[2][STREAM_PLANE_H];
static s16 sLineScroll[2][STREAM_VISIBLE_H], sPrevLineScroll[2][STREAM_VISIBLE_H];
static u16 sMapShadow[2][STREAM_PLANE_H][STREAM_PLANE_W];
static u16 sRowScratch[STREAM_PLANE_W];
static u16 sSlotVram[STREAM_MAX_CACHE], sSlotPattern[STREAM_MAX_CACHE];
static u16 sPatternSlot[SUZAKU_STREAM_PATTERN_COUNT];
static u8 sWanted[SUZAKU_STREAM_PATTERN_COUNT], sUpload[STREAM_MAX_CACHE];
static u16 sCapacity, sFixedCapacity, sResident, sPeakWanted;
static u16 sLoanBase, sLoanCount;
static u16 sOverflowCount, sRestoreCount, sLastUploadBytes, sLastMapBytes, sLastScrollBytes;
static u16 sPeakUploadBytes, sPeakMapBytes, sPeakScrollBytes, sPeakTotalBytes;
static s16 sLastCamera = -1, sLastShakeX = -128, sLastShakeY = -128;
static s16 sLastVScrollB = -1;

static void record_transfer_peaks(void)
{
    const u16 total = sLastUploadBytes + sLastMapBytes + sLastScrollBytes;
    if (sLastUploadBytes > sPeakUploadBytes) sPeakUploadBytes = sLastUploadBytes;
    if (sLastMapBytes > sPeakMapBytes) sPeakMapBytes = sLastMapBytes;
    if (sLastScrollBytes > sPeakScrollBytes) sPeakScrollBytes = sLastScrollBytes;
    if (total > sPeakTotalBytes) sPeakTotalBytes = total;
}

static const u16 *const sSourceMap[2] = {
    suzaku_stream_far_map,
    suzaku_stream_near_map
};

static s16 floor_tile(s16 pixels)
{
    if (pixels >= 0) return pixels / 8;
    return (s16)-(((-pixels) + 7) / 8);
}

/* This scene explicitly reclaims gaps above SGDK's automatic allocation ceiling.
 * TILE_MAX_NUM is NOT the physical VRAM limit. Keep the name tables, HScroll
 * and SAT excluded even when a caller supplies an otherwise physical range. */
static bool append_slots(u16 base, u16 count, bool reject_overlap)
{
    const u32 end = (u32)base + count;
    if (end > 0x10000UL / TILE_SIZE || (u32)sCapacity + count > STREAM_MAX_CACHE)
        return FALSE;
    if (count && ((base < 0xD000 / TILE_SIZE && end > 0xC000 / TILE_SIZE) ||
                  (base < 0xF800 / TILE_SIZE && end > 0xE000 / TILE_SIZE)))
        return FALSE;
    /* Validate before committing: failure must leave the pool unchanged. */
    for (u16 i = 0; i < count; i++)
        for (u16 j = 0; j < sCapacity; j++)
            if (sSlotVram[j] == base + i) {
                if (reject_overlap) return FALSE;
            }
    for (u16 i = 0; i < count; i++) {
        bool present = FALSE;
        for (u16 j = 0; j < sCapacity; j++)
            if (sSlotVram[j] == base + i) { present = TRUE; break; }
        if (!present) sSlotVram[sCapacity++] = base + i;
    }
    return TRUE;
}

static bool build_slot_pool(u16 lowBase)
{
    const u16 base[STREAM_FIXED_BANKS] = {
        lowBase, TILE_FONT_INDEX, (u16)(0xD000 / TILE_SIZE), (u16)(0xF800 / TILE_SIZE)
    };
    const u16 count[STREAM_FIXED_BANKS] = {
        lowBase <= TILE_SPRITE_INDEX ? (u16)(TILE_SPRITE_INDEX - lowBase) : 0,
        FONT_LEN, 128, 64
    };
    sCapacity = sFixedCapacity = 0;
    if (lowBase > TILE_SPRITE_INDEX) return FALSE;
    for (u16 i = 0; i < STREAM_FIXED_BANKS; i++)
        if (!append_slots(base[i], count[i], TRUE)) return FALSE;
    sFixedCapacity = sCapacity;

    if (!MG_fightGetBgFxLoan(&sLoanBase, &sLoanCount) || !sLoanCount)
        return FALSE;
    if ((u32)sLoanBase + (u32)sLoanCount > (u32)TILE_SPRITE_INDEX ||
        !append_slots(sLoanBase, sLoanCount, TRUE)) return FALSE;
    return sCapacity >= sFixedCapacity && sCapacity <= STREAM_MAX_CACHE;
}

static s16 scroll_for(u8 plane, u16 y, u16 camera)
{
    const u8 id = plane == 0 ? suzaku_stream_far_speed_id[y]
                             : suzaku_stream_near_speed_id[y];
    if (id >= SUZAKU_STREAM_CAMERA_SPEED_COUNT) return 0;
    return suzaku_stream_scroll_offsets[id][camera];
}

/* Geometry is computed per visible line, then collapsed to the union of map
 * cells required by each 8px tile row. The same result feeds the cache and the
 * line-scroll registers, so VRAM residency cannot use a different camera. */
static bool build_visible_rows(u16 camera, s8 shakeX, s8 shakeY, s16 *vscrollB)
{
    for (u8 p = 0; p < 2; p++) {
        for (u8 row = 0; row < STREAM_PLANE_H; row++) {
            sRowVisible[p][row] = FALSE;
            sRowLeft[p][row] = 32767;
            sRowRight[p][row] = -32768;
        }
    }
    const s16 vscrollNear = 16; /* keeps BG_A power meter and SUPER label stationary */
    s16 farScroll = 16 - (s16)shakeY;
    if (farScroll < 0) farScroll = 0;
    if (farScroll > 32) farScroll = 32;
    *vscrollB = farScroll;

    for (u16 y = 0; y < STREAM_VISIBLE_H; y++) {
        const u16 mapY[2] = { (u16)(y + vscrollNear), (u16)(y + farScroll) };
        if (mapY[0] >= 256 || mapY[1] >= 256) return FALSE;
        for (u8 p = 0; p < 2; p++) {
            s16 scroll = scroll_for(p, y, camera);
            const bool hudLine = p == 1 && y >= STREAM_HUD_Y0 && y < STREAM_HUD_Y1;
            if (hudLine) scroll = 0;
            const s16 shake = hudLine ? 0 : shakeX;
            const s16 leftPixel = scroll - shake;
            const s16 rightPixel = leftPixel + STREAM_VISIBLE_W - 1;
            const s16 left = floor_tile(leftPixel);
            const s16 right = floor_tile(rightPixel);
            const u16 row = mapY[p] >> 3;
            if (row >= STREAM_PLANE_H || right - left >= STREAM_PLANE_W) return FALSE;
            sRowVisible[p][row] = TRUE;
            if (left < sRowLeft[p][row]) sRowLeft[p][row] = left;
            if (right > sRowRight[p][row]) sRowRight[p][row] = right;
            sLineScroll[p][y] = hudLine ? 0 : (s16)(left * 8 - scroll + shakeX);
        }
    }
    return TRUE;
}

static bool mark_wanted(void)
{
    memset(sWanted, 0, sizeof(sWanted));
    sWanted[0] = TRUE; /* canonical all-transparent cell */
    u16 count = 1;
    for (u8 plane = 0; plane < 2; plane++) {
        for (u8 row = 0; row < STREAM_PLANE_H; row++) {
            if (!sRowVisible[plane][row]) continue;
            const s16 left = sRowLeft[plane][row];
            const s16 right = sRowRight[plane][row];
            for (s16 worldX = left; worldX <= right; worldX++) {
                if (worldX < 0 || worldX >= STREAM_WORLD_W) continue;
                const u16 entry = sSourceMap[plane][row * STREAM_WORLD_W + (u16)worldX];
                const u16 id = entry & SUZAKU_STREAM_ENTRY_ID_MASK;
                if (id >= SUZAKU_STREAM_PATTERN_COUNT) return FALSE;
                if (!sWanted[id]) { sWanted[id] = TRUE; count++; }
            }
        }
    }
    if (count > sPeakWanted) sPeakWanted = count;
    return count <= sCapacity;
}

static bool upload_runs(TransferMethod method, bool forceLoan)
{
    memset(sUpload, 0, sizeof(sUpload));
    for (u16 id = 0; id < SUZAKU_STREAM_PATTERN_COUNT; id++) {
        if (!sWanted[id]) continue;
        if (sPatternSlot[id] == STREAM_INVALID) {
            u16 slot = STREAM_INVALID;
            for (u16 i = 0; i < sCapacity; i++)
                if (sSlotPattern[i] == STREAM_INVALID) { slot = i; break; }
            if (slot == STREAM_INVALID) { sOverflowCount++; return FALSE; }
            sPatternSlot[id] = slot;
            sSlotPattern[slot] = id;
            sUpload[slot] = TRUE;
            sResident++;
        }
    }
    for (u16 slot = 0; slot < sCapacity; slot++) {
        const bool inLoan = sLoanCount && sSlotVram[slot] >= sLoanBase &&
                            sSlotVram[slot] < (u16)(sLoanBase + sLoanCount);
        if (forceLoan && inLoan && sSlotPattern[slot] != STREAM_INVALID)
            sUpload[slot] = TRUE;
    }

    u16 uploaded = 0;
    u16 slot = 0;
    while (slot < sCapacity) {
        if (!sUpload[slot]) { slot++; continue; }
        const u16 start = slot;
        const u16 firstId = sSlotPattern[slot];
        u16 length = 1;
        while (start + length < sCapacity && sUpload[start + length] &&
               sSlotVram[start + length] == (u16)(sSlotVram[start] + length) &&
               sSlotPattern[start + length] == (u16)(firstId + length))
            length++;
        VDP_loadTileData(suzaku_stream_patterns.tiles + (u32)firstId * 8,
                         sSlotVram[start], length, method);
        uploaded += length;
        slot = start + length;
    }
    sLastUploadBytes = uploaded * 32;
    return TRUE;
}

static bool refresh_cache(TransferMethod method, bool forceLoan)
{
    for (u16 id = 0; id < SUZAKU_STREAM_PATTERN_COUNT; id++) {
        const u16 slot = sPatternSlot[id];
        if (slot != STREAM_INVALID && !sWanted[id]) {
            sPatternSlot[id] = STREAM_INVALID;
            sSlotPattern[slot] = STREAM_INVALID;
            if (sResident) sResident--;
        }
    }
    return upload_runs(method, forceLoan);
}

static u16 tile_attr_for_entry(u16 entry)
{
    const u16 id = entry & SUZAKU_STREAM_ENTRY_ID_MASK;
    if (id >= SUZAKU_STREAM_PATTERN_COUNT || sPatternSlot[id] == STREAM_INVALID) return 0;
    const u16 slot = sPatternSlot[id];
    const u16 tile = sSlotVram[slot];
    return TILE_ATTR_FULL(PAL0, FALSE,
                          (entry & SUZAKU_STREAM_ENTRY_VFLIP) != 0,
                          (entry & SUZAKU_STREAM_ENTRY_HFLIP) != 0, tile);
}

static void write_map_rows(bool initial, bool forceRestore)
{
    sLastMapBytes = 0;
    for (u8 plane = 0; plane < 2; plane++) {
        for (u8 row = 0; row < STREAM_PLANE_H; row++) {
            for (u8 col = 0; col < STREAM_PLANE_W; col++)
                sRowScratch[col] = TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, 0);
            u16 width = 0;
            if (sRowVisible[plane][row]) {
                const s16 left = sRowLeft[plane][row];
                const s16 right = sRowRight[plane][row];
                width = (u16)(right - left + 1);
                for (u16 col = 0; col < width; col++) {
                    const s16 worldX = left + col;
                    if (worldX < 0 || worldX >= STREAM_WORLD_W) continue;
                    const u16 entry = sSourceMap[plane][row * STREAM_WORLD_W + (u16)worldX];
                    sRowScratch[col] = tile_attr_for_entry(entry);
                }
            }
            if (initial) {
                for (u8 col = 0; col < STREAM_PLANE_W; col++)
                    sMapShadow[plane][row][col] = sRowScratch[col];
                continue;
            }
            if (forceRestore) {
                if (!width) continue;
                for (u16 col = 0; col < width; col++)
                    sMapShadow[plane][row][col] = sRowScratch[col];
                VDP_setTileMapDataRow(plane == 0 ? BG_B : BG_A,
                                      sMapShadow[plane][row], row, 0, width, DMA_QUEUE_COPY);
                sLastMapBytes += width * 2;
                continue;
            }
            u16 col = 0;
            while (col < STREAM_PLANE_W) {
                if (sMapShadow[plane][row][col] == sRowScratch[col]) { col++; continue; }
                const u16 start = col;
                while (col < STREAM_PLANE_W &&
                       sMapShadow[plane][row][col] != sRowScratch[col]) {
                    sMapShadow[plane][row][col] = sRowScratch[col];
                    col++;
                }
                const u16 length = col - start;
                VDP_setTileMapDataRow(plane == 0 ? BG_B : BG_A,
                                      &sMapShadow[plane][row][start], row, start, length,
                                      DMA_QUEUE_COPY);
                sLastMapBytes += length * 2;
            }
        }
    }
    if (initial) {
        VDP_setTileMapDataRect(BG_B, &sMapShadow[0][0][0], 0, 0,
                               STREAM_PLANE_W, STREAM_PLANE_H, STREAM_PLANE_W, CPU);
        VDP_setTileMapDataRect(BG_A, &sMapShadow[1][0][0], 0, 0,
                               STREAM_PLANE_W, STREAM_PLANE_H, STREAM_PLANE_W, CPU);
        sLastMapBytes = STREAM_MAP_CELLS * 4;
    }
}

static void write_scroll_lines(bool initial, bool force)
{
    sLastScrollBytes = 0;
    for (u8 plane = 0; plane < 2; plane++) {
        u16 y = 0;
        while (y < STREAM_VISIBLE_H) {
            if (!initial && !force && sLineScroll[plane][y] == sPrevLineScroll[plane][y]) {
                y++;
                continue;
            }
            const u16 start = y;
            while (y < STREAM_VISIBLE_H &&
                   (initial || force || sLineScroll[plane][y] != sPrevLineScroll[plane][y]))
                y++;
            const u16 length = y - start;
            VDP_setHorizontalScrollLine(plane == 0 ? BG_B : BG_A, start,
                                        &sLineScroll[plane][start], length,
                                        initial ? CPU : DMA_QUEUE_COPY);
            sLastScrollBytes += length * 2;
        }
        memcpy(sPrevLineScroll[plane], sLineScroll[plane], sizeof(sPrevLineScroll[plane]));
    }
}

void FIGHT_STAGE_setup(void)
{
    VDP_setPlaneSize(STREAM_PLANE_W, STREAM_PLANE_H, TRUE);
    VDP_setWindowAddress(0xE000);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);
    sLoaded = sSuper = sHudInvalidation = FALSE;
    sOverflowCount = sRestoreCount = sPeakWanted = sResident = 0;
    sLastUploadBytes = sLastMapBytes = sLastScrollBytes = 0;
    sPeakUploadBytes = sPeakMapBytes = sPeakScrollBytes = sPeakTotalBytes = 0;
    sLastCamera = -1;
    sLastShakeX = sLastShakeY = -128;
    sLastVScrollB = -1;
    sCapacity = sFixedCapacity = sLoanBase = sLoanCount = 0;
    memset(sPatternSlot, 0xFF, sizeof(sPatternSlot));
    memset(sSlotPattern, 0xFF, sizeof(sSlotPattern));
    memset(sMapShadow, 0, sizeof(sMapShadow));
    memset(sPrevLineScroll, 0x80, sizeof(sPrevLineScroll));
}

bool FIGHT_STAGE_init(u16 lowBase)
{
    if (suzaku_stream_patterns.compression ||
        suzaku_stream_patterns.numTile < SUZAKU_STREAM_PATTERN_COUNT ||
        !build_slot_pool(lowBase)) return FALSE;

    s16 camera = mg_fight.camx;
    if (camera < SUZAKU_STREAM_RUNTIME_CAM_MIN || camera > SUZAKU_STREAM_RUNTIME_CAM_MAX)
        return FALSE;
    s16 vscrollB = 16;
    if (!build_visible_rows((u16)camera, mg_fight.shake_x, mg_fight.shake_y, &vscrollB) ||
        !mark_wanted()) return FALSE;

    /* Display is disabled by SCENE_demoEnter. The first view is resident before
     * enable, and the only temporary loan is the already-reserved super-BG bank. */
    refresh_cache(CPU, FALSE);
    if (sResident != sPeakWanted || sResident > sCapacity) return FALSE;
    PAL_setColors(0, img_suzaku_anchor.palette->data, 9, CPU);
    write_map_rows(TRUE, FALSE);
    VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_PLANE);
    VDP_setVerticalScroll(BG_A, 16);
    VDP_setVerticalScroll(BG_B, vscrollB);
    write_scroll_lines(TRUE, TRUE);
    sLastCamera = camera;
    sLastShakeX = mg_fight.shake_x;
    sLastShakeY = mg_fight.shake_y;
    sLastVScrollB = vscrollB;
    sHudInvalidation = TRUE;
    sLoaded = TRUE;
    return TRUE;
}

void FIGHT_STAGE_update(void)
{
    if (!sLoaded) return;
    sLastUploadBytes = sLastMapBytes = sLastScrollBytes = 0;
    const bool active = mg_fight.bgfx_active != 0;
    if (active && !sSuper) {
        /* BGFX expects ordinary plane scrolling; its map and tiles temporarily
         * occupy BG_B and the declared loan bank. Keep only the visible A window clear. */
        VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
        VDP_setVerticalScroll(BG_A, 0);
        VDP_setVerticalScroll(BG_B, 0);
        VDP_setTileMapDataRect(BG_A, sMapShadow[1][0], 0, 0, 40, 28,
                               STREAM_PLANE_W, DMA_QUEUE_COPY);
        sLastMapBytes = 40 * 28 * 2;
        sHudInvalidation = TRUE;
        sSuper = TRUE;
        record_transfer_peaks();
        return;
    }
    if (active) return;

    const bool restoring = sSuper != 0;
    s16 camera = mg_fight.camx;
    if (camera < SUZAKU_STREAM_RUNTIME_CAM_MIN) camera = SUZAKU_STREAM_RUNTIME_CAM_MIN;
    if (camera > SUZAKU_STREAM_RUNTIME_CAM_MAX) camera = SUZAKU_STREAM_RUNTIME_CAM_MAX;
    s16 vscrollB = 16;
    if (!build_visible_rows((u16)camera, mg_fight.shake_x, mg_fight.shake_y, &vscrollB) ||
        !mark_wanted()) {
        sOverflowCount++;
        return; /* preserve the last complete image instead of aliasing live VRAM */
    }

    if (restoring) VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_PLANE);
    if (!refresh_cache(DMA_QUEUE, restoring)) {
        sOverflowCount++;
        return;
    }
    write_map_rows(FALSE, restoring);
    if (restoring || camera != sLastCamera || mg_fight.shake_x != sLastShakeX ||
        mg_fight.shake_y != sLastShakeY)
        write_scroll_lines(FALSE, restoring);
    VDP_setVerticalScroll(BG_A, 16); /* power meter and label stay at screen y=200/208 */
    if (vscrollB != sLastVScrollB)
        VDP_setVerticalScroll(BG_B, vscrollB);
    sLastVScrollB = vscrollB;

    if (restoring) {
        sRestoreCount++;
        sHudInvalidation = TRUE;
    }
    sSuper = FALSE;
    sLastCamera = camera;
    sLastShakeX = mg_fight.shake_x;
    sLastShakeY = mg_fight.shake_y;
    record_transfer_peaks();
}

u16 FIGHT_STAGE_restoreCount(void) { return sRestoreCount; }

bool FIGHT_STAGE_takeHudInvalidation(void)
{
    const bool changed = sHudInvalidation != 0;
    sHudInvalidation = 0;
    return changed;
}

void FIGHT_STAGE_streamStats(u16 *capacity, u16 *resident, u16 *peakWanted,
                             u16 *overflows, u16 *restores, u16 *uploadBytes,
                             u16 *mapBytes, u16 *scrollBytes,
                             u16 *peakUploadBytes, u16 *peakMapBytes,
                             u16 *peakScrollBytes, u16 *peakTotalBytes)
{
    if (capacity) *capacity = sCapacity;
    if (resident) *resident = sResident;
    if (peakWanted) *peakWanted = sPeakWanted;
    if (overflows) *overflows = sOverflowCount;
    if (restores) *restores = sRestoreCount;
    if (uploadBytes) *uploadBytes = sLastUploadBytes;
    if (mapBytes) *mapBytes = sLastMapBytes;
    if (scrollBytes) *scrollBytes = sLastScrollBytes;
    if (peakUploadBytes) *peakUploadBytes = sPeakUploadBytes;
    if (peakMapBytes) *peakMapBytes = sPeakMapBytes;
    if (peakScrollBytes) *peakScrollBytes = sPeakScrollBytes;
    if (peakTotalBytes) *peakTotalBytes = sPeakTotalBytes;
}

#endif /* MG_STAGE_SOURCE_STREAM */
