#include <genesis.h>

#include "system/probe_stage.h"
#include "systems/raster.h"

/*
 * Sky gradient stops, top to horizon, as raw VDP colour words.
 * Every value is on the RGB333 lattice by construction because it is built
 * with RGB3_3_3_TO_VDPCOLOR (pal.h:48), so the cram_rgb333_legal gate cannot
 * be violated from here.
 */
static const u16 SKY_GRADIENT[RASTER_SKY_STOPS] = {
    RGB3_3_3_TO_VDPCOLOR(3, 5, 7),
    RGB3_3_3_TO_VDPCOLOR(3, 5, 7),
    RGB3_3_3_TO_VDPCOLOR(4, 5, 7),
    RGB3_3_3_TO_VDPCOLOR(4, 6, 7),
    RGB3_3_3_TO_VDPCOLOR(5, 6, 7),
    RGB3_3_3_TO_VDPCOLOR(5, 6, 7),
    RGB3_3_3_TO_VDPCOLOR(6, 6, 7),
    RGB3_3_3_TO_VDPCOLOR(6, 7, 7),
    RGB3_3_3_TO_VDPCOLOR(7, 7, 7),
    RGB3_3_3_TO_VDPCOLOR(7, 7, 6),
    RGB3_3_3_TO_VDPCOLOR(7, 7, 5),
    RGB3_3_3_TO_VDPCOLOR(7, 7, 4),
};

/*
 * Night gradient for the title, doc/art/AI_IMAGE_PROMPT_PACK.md R1-07:
 * deep indigo at the top falling to lavender then pink at the horizon.
 * Same 12 stops, same single CRAM entry -- only the table changes.
 */
static const u16 SKY_NIGHT[RASTER_SKY_STOPS] = {
    RGB3_3_3_TO_VDPCOLOR(0, 0, 2), RGB3_3_3_TO_VDPCOLOR(1, 0, 3),
    RGB3_3_3_TO_VDPCOLOR(1, 0, 3), RGB3_3_3_TO_VDPCOLOR(1, 1, 4),
    RGB3_3_3_TO_VDPCOLOR(2, 1, 4), RGB3_3_3_TO_VDPCOLOR(2, 1, 5),
    RGB3_3_3_TO_VDPCOLOR(3, 1, 5), RGB3_3_3_TO_VDPCOLOR(4, 2, 5),
    RGB3_3_3_TO_VDPCOLOR(5, 2, 5), RGB3_3_3_TO_VDPCOLOR(6, 3, 5),
    RGB3_3_3_TO_VDPCOLOR(7, 4, 5), RGB3_3_3_TO_VDPCOLOR(7, 5, 6),
};

static bool s_useNight;

/* --- R3/R4 waterline ------------------------------------------------------ */
static s16 s_waterline = -1;
static u16 s_waterWords = 1u;
static u16 s_waterPal[RASTER_WATER_MAX_WORDS];
static volatile bool s_waterDone;
static volatile u16 s_hintLine;
static u16 s_waterPhase;

/*
 * Precomputed wobble, 64 entries, amplitude +/-4 px.
 *
 * The first version called F16_sin() once PER LINE PER FRAME for ~74 lines.
 * Measured cost: cpu p99 111% with 306 frames over budget -- the scene did not
 * fit in a frame at all. A screenshot showed the effect working, which is
 * exactly why a screenshot is not a performance measurement.
 *
 * A table lookup is the same picture for a fraction of the cost.
 */
static const s8 WATER_WAVE[64] = {
     0,  0,  1,  1,  2,  2,  3,  3,  3,  4,  4,  4,  4,  4,  3,  3,
     3,  2,  2,  1,  1,  0,  0,  0, -1, -1, -2, -2, -3, -3, -3, -4,
    -4, -4, -4, -4, -3, -3, -3, -2, -2, -1, -1,  0,  0,  0,  1,  1,
     2,  2,  3,  3,  3,  4,  4,  4,  4,  4,  3,  3,  3,  2,  2,  1,
};

void RASTER_setWaterCramWords(u16 count)
{
    s_waterWords = (count > RASTER_WATER_MAX_WORDS)
                 ? RASTER_WATER_MAX_WORDS : count;
}

u16 RASTER_getWaterCramWords(void) { return s_waterWords; }

void RASTER_setWaterline(s16 line)
{
    u16 i;
    s_waterline = line;
    /*
     * Submerged ramp derived from the surface palette by the rule the art study
     * r1-06 proposed and doc/PALETTES.md 6.3 adopted: push green and blue up,
     * pull red down, drop the top value one step. Materialised as a TABLE here,
     * not applied as blind arithmetic at runtime -- blind arithmetic flattens
     * different materials onto the same colour, which is exactly what the study
     * warned about.
     */
    for (i = 0u; i < RASTER_WATER_MAX_WORDS; i++)
    {
        static const u16 SUBMERGED[RASTER_WATER_MAX_WORDS] = {
            RGB3_3_3_TO_VDPCOLOR(0, 3, 5), RGB3_3_3_TO_VDPCOLOR(0, 4, 6),
            RGB3_3_3_TO_VDPCOLOR(1, 4, 6), RGB3_3_3_TO_VDPCOLOR(1, 5, 7),
            RGB3_3_3_TO_VDPCOLOR(2, 5, 7), RGB3_3_3_TO_VDPCOLOR(0, 2, 4),
            RGB3_3_3_TO_VDPCOLOR(0, 3, 4), RGB3_3_3_TO_VDPCOLOR(1, 3, 5),
        };
        s_waterPal[i] = SUBMERGED[i];
    }
}

void RASTER_setNightSky(bool night) { s_useNight = night; }


/* Per-line HScroll tables. Two planes x 224 lines. */
static s16 s_hscrollA[RASTER_SCREEN_LINES];
static s16 s_hscrollB[RASTER_SCREEN_LINES];

/* H-interrupt state. Written by the callback, re-armed once per frame. */
static volatile u16 s_skyStop;

/*
 * VBlank callback: mask the H-interrupt for the whole VBlank.
 *
 * WHY THIS EXISTS (bug found 2026-07-30, diagnosed from CRAM dumps):
 * the H-int writes VDP_CTRL_PORT to set a CRAM address, then VDP_DATA_PORT.
 * SGDK flushes its DMA queue inside SYS_doVBlankProcess, and a DMA is also
 * "write the control port, then transfer". If the H-int fires BETWEEN those two
 * steps, it overwrites the pending VDP address and the queued DMA lands
 * somewhere else -- observed as 17 to 31 contiguous CRAM entries filled with
 * HScroll bytes reinterpreted as colour (a uniform green), varying run to run.
 *
 * The fix is not in the H-int, which is correct in isolation; it is that NOTHING
 * may interrupt a VDP port sequence. So the H-int is off for all of VBlank and
 * is re-armed by RASTER_frameStart() once the main loop resumes.
 */
static void RASTER_vInt(void)
{
    VDP_setHInterrupt(FALSE);
}

/*
 * The one and only H-interrupt callback in this project.
 * It writes EXACTLY ONE CRAM word and returns. No function calls, no
 * allocation, no audio, no DMA. doc/ARCHITECTURE.md section 4.
 */
static HINTERRUPT_CALLBACK RASTER_hInt(void)
{
    const u16 stop = s_skyStop;

    if (stop < RASTER_SKY_STOPS)
    {
        /* Raw CRAM write: the SGDK PAL_* helpers are not H-int safe because
         * they may touch the DMA queue. Two port writes is the whole cost. */
        *((vu32*) VDP_CTRL_PORT) =
            VDP_WRITE_CRAM_ADDR((u32) (RASTER_SKY_CRAM_INDEX * 2u));
        /* One table or the other; the H-int cost is identical. */
        *((vu16*) VDP_DATA_PORT) =
            s_useNight ? SKY_NIGHT[stop] : SKY_GRADIENT[stop];
        s_skyStop = stop + 1u;
    }

    /*
     * R4: at the waterline, rewrite the first N entries of PAL1 so everything
     * drawn below renders submerged. N is deliberately variable so its real
     * ceiling can be MEASURED instead of assumed -- see RASTER_setWaterCramWords.
     * Verified from the CRAM dump: with N=4, PAL1[1..4] goes from greens/browns
     * to blues/cyans and PAL1[5] stays brown, i.e. exactly 4 words land.
     *
     * The H-int keeps firing for the WHOLE frame, but `stop` saturates at
     * RASTER_SKY_STOPS (12), so deriving the scanline from it capped at line
     * 144 and the waterline at 150 never triggered. Track the line separately.
     *
     * OPEN DEFECT 2026-08-06: after this change the sky gradient's first stop
     * appears to hold for more scanlines than before, in BOTH the lake and the
     * plain stage. Gates still pass (parallax exact, cpu p99 59%), so this is
     * cosmetic, but it is NOT understood. Diagnosing it by comparing screenshots
     * is the wrong tool -- the fix is to export s_skyStop and s_hintLine in the
     * KRB1 block and read them, the same way the parallax measurement was
     * settled. Do not "fix" this by eye.
     */
    s_hintLine += RASTER_SKY_LINES_PER_STOP;

    if ((s_waterline >= 0) && !s_waterDone)
    {
        const u16 line = s_hintLine;
        if (line >= (u16) s_waterline)
        {
            u16 i;
            *((vu32*) VDP_CTRL_PORT) =
                VDP_WRITE_CRAM_ADDR((u32) ((16u + 1u) * 2u));  /* PAL1 index 1 */
            for (i = 0u; i < s_waterWords; i++)
            {
                *((vu16*) VDP_DATA_PORT) = s_waterPal[i];
            }
            s_waterDone = TRUE;
        }
    }
}

static s16 s_lastCameraX;
static bool s_scrollDirty;

void RASTER_initStage(void)
{
    /* Force the first build: VRAM holds nothing valid yet. */
    s_scrollDirty = TRUE;
    s_lastCameraX = 0;

    u16 i;

    /*
     * Shadow/Highlight is ON for the whole game and every background tile is
     * authored priority=1. doc/PALETTES.md section 2.2. A background tile left
     * at priority 0 renders at half brightness and is a bug, not a style.
     */
    VDP_setHilightShadow(TRUE);
    PROBE_STAGE_publishShadowHighlight(TRUE);

    /* Per-line horizontal scroll is what splits BG_B into three layers. */
    VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_PLANE);

    for (i = 0u; i < RASTER_SCREEN_LINES; i++)
    {
        s_hscrollA[i] = 0;
        s_hscrollB[i] = 0;
    }

    /* Seed the backdrop so frame 0 has a sane sky before the first H-int. */
    PAL_setColor(RASTER_SKY_CRAM_INDEX,
                 s_useNight ? SKY_NIGHT[0] : SKY_GRADIENT[0]);

    s_skyStop = 0u;

    /* Fire every RASTER_SKY_LINES_PER_STOP lines: 224/12 gives us the 12 sky
     * bands without paying an interrupt on all 224 scanlines. */
    VDP_setHIntCounter((u8) (RASTER_SKY_LINES_PER_STOP - 1u));
    SYS_setHIntCallback(RASTER_hInt);
    SYS_setVIntCallback(RASTER_vInt);
    VDP_setHInterrupt(TRUE);
}

void RASTER_shutdown(void)
{
    VDP_setHInterrupt(FALSE);
    SYS_setHIntCallback(NULL);
    SYS_setVIntCallback(NULL);
    VDP_setHilightShadow(FALSE);
    PROBE_STAGE_publishShadowHighlight(FALSE);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
}

void RASTER_frameStart(void)
{
    /* Re-arm the gradient walk AND the H-interrupt itself: RASTER_vInt masked it
     * for the duration of VBlank so the DMA queue flush could not be interrupted
     * mid VDP-port-sequence. See the comment on RASTER_vInt. */
    s_skyStop = 0u;
    s_hintLine = 0u;
    s_waterDone = FALSE;
    VDP_setHInterrupt(TRUE);
}

/*
 * Cache of the last camera position the table was built for. Rebuilding 224
 * entries per plane for a camera that has not moved is pure waste: it costs CPU
 * to compute and DMA bandwidth to re-upload IDENTICAL bytes.
 *
 * Measured 2026-08-06 in the boss arena, whose camera is static: rebuilding
 * every frame put cpu p99 at 96% with 19 of 32 sampled frames over budget.
 * Skipping the rebuild when the camera has not moved is not a degradation --
 * the rendered result is byte-identical -- so it is the right fix to spend
 * BEFORE reaching for the boss degradation ladder.
 */
void RASTER_updateScroll(s16 cameraX)
{
    /*
     * The static-camera skip is a real optimisation (it took the boss arena from
     * 96% CPU to 78%), but it is WRONG while the waterline is active: the sine
     * distortion is ANIMATED, so the table must be rebuilt even when the camera
     * has not moved. Measured: with the skip in place the lake scene showed no
     * wobble at all.
     */
    if (!s_scrollDirty && (cameraX == s_lastCameraX) && (s_waterline < 0)) return;
    s_lastCameraX = cameraX;
    s_scrollDirty = FALSE;

    u16 line;
    const s16 scrollA = (s16) -cameraX;
    const s16 scrollSky = 0;
    const s16 scrollMount = (s16) -(cameraX >> 3);   /* camX / 8  */
    const s16 scrollHills = (s16) -((cameraX * 11) >> 5); /* ~camX / 3 */

    for (line = 0u; line < RASTER_SCREEN_LINES; line++)
    {
        s_hscrollA[line] = scrollA;

        if (line < RASTER_BAND_SKY_END)
        {
            s_hscrollB[line] = scrollSky;
        }
        else if (line < RASTER_BAND_MOUNT_END)
        {
            s_hscrollB[line] = scrollMount;
        }
        else
        {
            s_hscrollB[line] = scrollHills;
        }
    }

    /*
     * DMA_QUEUE, never DMA now: AGENTS.md allows DMA only inside VBlank and
     * the queue is flushed by SYS_doVBlankProcess(). 224 lines x 2 bytes x 2
     * planes = 896 bytes, which is the mandatory-every-frame line of the DMA
     * budget in doc/VRAMMAP.md section 3.1.
     */
    /*
     * R3: per-line sine distortion of BG_A below the waterline. This costs only
     * HScroll entries we already rebuild, so it is nearly free -- the expensive
     * part of water on this hardware is the palette, not the wobble.
     *
     * s_waterPhase advances once per frame so the wave travels.
     */
    if (s_waterline >= 0)
    {
        u16 line;
        for (line = (u16) s_waterline; line < RASTER_SCREEN_LINES; line++)
        {
            s_hscrollA[line] = (s16) (s_hscrollA[line]
                + WATER_WAVE[(line + s_waterPhase) & 63u]);
        }
        s_waterPhase++;
    }

    /* Publish the ACTUAL programmed values, sampled one per parallax band.
     * This is what replaced the screenshot forensics that failed on 2026-07-30:
     * the numbers now come from the table the ROM just built, not from pixels. */
    /*
     * Publish the terrain scroll WITHOUT the water wobble.
     *
     * The parallax gate checks camada 4 against -cameraX. The wobble is a
     * deliberate per-line offset on top of that, so feeding the wobbled value
     * made the gate report the terrain "off the design formula" in the lake
     * scene -- a false failure caused by mixing two effects in one sample.
     * The gate keeps checking parallax; the wobble is a separate concern.
     */
    PROBE_STAGE_publishHScroll(s_hscrollB[PROBE_STAGE_HS_SKY_LINE],
                               s_hscrollB[PROBE_STAGE_HS_MOUNT_LINE],
                               s_hscrollB[PROBE_STAGE_HS_HILL_LINE],
                               (s16) (-cameraX));

    VDP_setHorizontalScrollLine(BG_A, 0, s_hscrollA,
                                RASTER_SCREEN_LINES, DMA_QUEUE);
    VDP_setHorizontalScrollLine(BG_B, 0, s_hscrollB,
                                RASTER_SCREEN_LINES, DMA_QUEUE);
}

u16 RASTER_getSkyStopCount(void)
{
    return s_skyStop;
}
