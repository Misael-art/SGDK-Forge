#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "system/audio.h"
#include "system/input.h"

#define BRAND_PHASE_ENGINE 0
#define BRAND_PHASE_AUTHOR 1
#define BRAND_PHASE_PROJECT 2

#define BRAND_ENGINE_END 150
#define BRAND_AUTHOR_END 300
#define BRAND_PROJECT_END 480

/*
 * VRAM Region Map — Branding Scene
 *
 * Region        Start tile   Capacity   Purpose
 * ─────────────────────────────────────────────────────────
 * BG            16           160        Slot background (BG_B tiled pattern or authored composition)
 * LOGO          176          340        Slot logo/signature (BG_A IMAGE, authored logotype)
 * SUBTITLE      516          80         PRESENTS text or secondary mark
 * FONT          596          80         Bitmap font for slot identity text
 * [free gap]    676          344        Available for future authored overlays
 * SPRITE RSV    1020         420        SPR_init() managed (monogram, shield, sparks, debris, glow, cursor)
 * SGDK FONT     1440         96         System font
 *
 * Total user tiles: 1004 (16..1019). Sprite reserve: 420 (1020..1439).
 * Each slot loads scene-local: one BG, one logo, optionally PRESENTS, one font.
 * Palettes: PAL0=BG, PAL1=logo, PAL2=sprites, PAL3=font. All reloaded per slot.
 *
 * For authored assets: replace PNGs in res/branding/, keep unique tiles within
 * the capacity column. rescomp deduplicates automatically.
 */
#define BRAND_TILE_BG        TILE_USER_INDEX
#define BRAND_REGION_BG_CAP  160
#define BRAND_TILE_LOGO      (TILE_USER_INDEX + 160)
#define BRAND_REGION_LOGO_CAP 340
#define BRAND_TILE_SUBTITLE  (TILE_USER_INDEX + 500)
#define BRAND_REGION_SUB_CAP 80
#define BRAND_TILE_FONT      (TILE_USER_INDEX + 580)
#define BRAND_REGION_FONT_CAP 80

#define BRAND_MAX_SPARKS 12
#define BRAND_MAX_DEBRIS 8
#define BRAND_FONT_COLUMNS 37
#define BRAND_AUTHOR_TEXT_X 12
#define BRAND_AUTHOR_TEXT_Y 20

static const char BRAND_ENGINE_SUBTEXT[] = "FORGED AT 60HZ";
static const char BRAND_AUTHOR_TEXT[] = "MISAEL OLIVEIRA";
static const char BRAND_PROJECT_TEXT[] = "SMOKE TEST LAB";

static const u16 BRAND_ENGINE_COOL[8] = {
    0x0200, 0x0600, 0x0E00, 0x0EE0,
    0x0EEE, 0x0AEE, 0x06CE, 0x04AC
};

static const u16 BRAND_ENGINE_SHIMMER[4] = {
    0x08AE, 0x0ACE, 0x0EEE, 0x0ACE
};

static const u16 BRAND_AUTHOR_GLOW[4] = {
    0x04A4, 0x08C8, 0x0AEA, 0x0EEE
};

static const u16 BRAND_PROJECT_FLASH[5] = {
    0x0E40, 0x0E80, 0x0EA0, 0x0EE0, 0x0EEE
};

static u8 sBrandPhase;
static s16 sBrandLineScroll[224];
static Sprite* sBrandPrimeSpark;
static Sprite* sBrandSparks[BRAND_MAX_SPARKS];
static Sprite* sBrandDebris[BRAND_MAX_DEBRIS];
static Sprite* sBrandMonogram;
static Sprite* sBrandShield;
static Sprite* sBrandGlow;
static Sprite* sBrandCursor;
static s16 sBrandSparkVX[BRAND_MAX_SPARKS];
static s16 sBrandSparkVY[BRAND_MAX_SPARKS];
static s16 sBrandDebrisVX[BRAND_MAX_DEBRIS];
static s16 sBrandDebrisVY[BRAND_MAX_DEBRIS];
static s16 sBrandGlowBaseY;
static s16 sBrandShakeIntensity;
static u16 sBrandShakeFrame;

static void brandPulsePsg(u8 channel, u16 tone, u8 envelope)
{
    PSG_setFrequency(channel, tone);
    PSG_setEnvelope(channel, envelope);
}

static void brandTriggerShake(s16 intensity)
{
    sBrandShakeIntensity = intensity;
    sBrandShakeFrame = 0;
}

static s16 brandGetShakeOffset(void)
{
    s16 offset;
    if (sBrandShakeIntensity <= 0) return 0;

    offset = (sBrandShakeFrame & 1) ? sBrandShakeIntensity : -sBrandShakeIntensity;
    sBrandShakeFrame++;
    sBrandShakeIntensity--;
    return offset;
}

static void brandImpactFlash(u16 palBase, u16 count)
{
    u16 i;
    for (i = 0; i < count; i++) {
        PAL_setColor(palBase + i, 0x0EEE);
    }
}

static u16 brandGlyphIndex(char glyph)
{
    if (glyph >= 'A' && glyph <= 'Z') return (u16)(glyph - 'A');
    if (glyph >= '0' && glyph <= '9') return (u16)(26 + glyph - '0');
    return 36;
}

static void brandResetScreen(void);

/*
 * Unified slot asset loader.
 * Loads BG to BG_B (tiled), logo to BG_A, optional subtitle, font and sprite palette.
 * Palettes start black for fade-in; BG/logo palette data is stored for brandFadeIn.
 */
typedef struct {
    const Image* bg;
    const Image* logo;
    u16 logoX;
    u16 logoY;
    const Image* subtitle;
    u16 subtitleX;
    u16 subtitleY;
    const Image* font;
    const u16*   spritePalData;
} BrandSlotDef;

static void brandLoadSlot(const BrandSlotDef* slot)
{
    u16 x;
    u16 y;
    bool loadPal = TRUE;
    const u16 bgAttr = TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, BRAND_TILE_BG);

    brandResetScreen();

    /* BG_B: tile the background pattern across the full plane */
    for (y = 0; y < 32; y += 8) {
        for (x = 0; x < 48; x += 16) {
            VDP_drawImageEx(BG_B, slot->bg, bgAttr, x, y, loadPal, FALSE);
            loadPal = FALSE;
        }
    }

    /* BG_A: logo loaded but palette kept black for fade-in */
    PAL_setPalette(PAL0, palette_black, CPU);
    PAL_setPalette(PAL1, palette_black, CPU);
    if (slot->logo != NULL) {
        VDP_drawImageEx(
            BG_A, slot->logo,
            TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, BRAND_TILE_LOGO),
            slot->logoX, slot->logoY, FALSE, FALSE
        );
    }

    /* Optional subtitle (PRESENTS) */
    if (slot->subtitle != NULL) {
        VDP_drawImageEx(
            BG_A, slot->subtitle,
            TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, BRAND_TILE_SUBTITLE),
            slot->subtitleX, slot->subtitleY, TRUE, FALSE
        );
    }

    /* Font tileset */
    if (slot->font != NULL) {
        PAL_setPalette(PAL3, slot->font->palette->data, CPU);
        VDP_loadTileSet(slot->font->tileset, BRAND_TILE_FONT, CPU);
    }

    /* Sprite palette */
    if (slot->spritePalData != NULL) {
        PAL_setPalette(PAL2, slot->spritePalData, CPU);
    }
}

static void brandLoadFont(const Image* font)
{
    PAL_setPalette(PAL3, font->palette->data, CPU);
    VDP_loadTileSet(font->tileset, BRAND_TILE_FONT, CPU);
}

static void brandDrawFontGlyph(const Image* font, char glyph, u16 x, u16 y)
{
    const u16 glyphIndex = brandGlyphIndex(glyph);
    const u16 baseTile = TILE_ATTR_FULL(PAL3, TRUE, FALSE, FALSE, BRAND_TILE_FONT);

    VDP_setTileMapDataEx(
        VDP_getPlaneAddress(BG_A, x, y),
        &font->tilemap->tilemap[glyphIndex],
        baseTile,
        0,
        1,
        2
    );
    VDP_setTileMapDataEx(
        VDP_getPlaneAddress(BG_A, x, y + 1),
        &font->tilemap->tilemap[BRAND_FONT_COLUMNS + glyphIndex],
        baseTile,
        0,
        1,
        2
    );
}

static void brandDrawFontText(const Image* font, const char* text, u16 x, u16 y)
{
    while (*text != '\0') {
        brandDrawFontGlyph(font, *text, x, y);
        text++;
        x++;
    }
}

static void brandResetScroll(void)
{
    u16 i;

    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);
    for (i = 0; i < 224; i++) sBrandLineScroll[i] = 0;
}

static void brandResetScreen(void)
{
    SPR_reset();
    SPR_update();
    AUDIO_stopAll();
    brandResetScroll();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    PAL_setPalette(PAL0, palette_black, CPU);
    PAL_setPalette(PAL1, palette_black, CPU);
    PAL_setPalette(PAL2, palette_black, CPU);
    PAL_setPalette(PAL3, palette_black, CPU);
    VDP_setBackgroundColor(0);
}

/* brandDrawSlotBackground removed — replaced by brandLoadSlot */

static void brandFadeIn(const u16* targetPal, u16 palIndex, u16 frame, u16 duration)
{
    if (frame >= duration) {
        PAL_setPalette(palIndex, targetPal, CPU);
        return;
    }
    {
        u16 i;
        u16 step = (frame * 16) / duration;
        if (step > 15) step = 15;
        for (i = 0; i < 16; i++) {
            u16 target = targetPal[i];
            u16 r = ((target >> 1) & 7) * step / 15;
            u16 g = ((target >> 5) & 7) * step / 15;
            u16 b = ((target >> 9) & 7) * step / 15;
            PAL_setColor(palIndex * 16 + i, (b << 9) | (g << 5) | (r << 1));
        }
    }
}

static u16 sBrandFadeCache[64];
static bool sBrandFadeCached;

static void brandFadeOut(u16 frame, u16 startFrame, u16 duration)
{
    u16 elapsed;
    u16 step;
    u16 i;

    if (frame < startFrame) return;
    elapsed = frame - startFrame;
    if (elapsed >= duration) {
        PAL_setPalette(PAL0, palette_black, CPU);
        PAL_setPalette(PAL1, palette_black, CPU);
        PAL_setPalette(PAL2, palette_black, CPU);
        PAL_setPalette(PAL3, palette_black, CPU);
        sBrandFadeCached = FALSE;
        return;
    }
    if (!sBrandFadeCached) {
        PAL_getColors(0, sBrandFadeCache, 64);
        sBrandFadeCached = TRUE;
    }
    step = 15 - (elapsed * 15) / duration;
    for (i = 0; i < 64; i++) {
        u16 src = sBrandFadeCache[i];
        u16 r = (((src >> 1) & 7) * step) / 15;
        u16 g = (((src >> 5) & 7) * step) / 15;
        u16 b = (((src >> 9) & 7) * step) / 15;
        PAL_setColor(i, (b << 9) | (g << 5) | (r << 1));
    }
}

static void brandAnimateBackground(u16 frame, s16 speed)
{
    s16 shakeOff = brandGetShakeOffset();
    s16 hScroll = (s16)((frame >> 1) & 63) * speed;
    s16 vBob = (s16)((frame >> 3) & 7) - 3;
    VDP_setHorizontalScroll(BG_B, hScroll);
    VDP_setVerticalScroll(BG_B, vBob + shakeOff);
}

static s16 brandWaveOffset(u16 frame, u16 line, u16 amplitude)
{
    const u16 phase = (u16)((line + (frame << 2)) & 31);
    s16 centered = (phase < 16) ? (s16)phase : (s16)(31 - phase);
    centered -= 8;
    return (centered * (s16)amplitude) >> 3;
}

static void brandSparksClear(void)
{
    u16 i;
    for (i = 0; i < BRAND_MAX_SPARKS; i++) {
        if (sBrandSparks[i] != NULL) {
            SPR_releaseSprite(sBrandSparks[i]);
            sBrandSparks[i] = NULL;
        }
    }
}

static void brandSparksSpawn(s16 originX, s16 originY)
{
    u16 i;

    brandSparksClear();
    for (i = 0; i < BRAND_MAX_SPARKS; i++) {
        sBrandSparks[i] = SPR_addSprite(
            &spr_brand_spark_v3,
            originX - 4,
            originY - 4,
            TILE_ATTR(PAL2, TRUE, FALSE, FALSE)
        );
        if (sBrandSparks[i] != NULL) {
            sBrandSparkVX[i] = (s16)((i * 13 + 7) & 15) - 7;
            sBrandSparkVY[i] = -((s16)(((i * 11 + 5) & 15) | 1));
            SPR_setFrame(sBrandSparks[i], (s16)(i & 3));
        }
    }
}

static void brandSparksUpdate(u16 frame)
{
    u16 i;

    for (i = 0; i < BRAND_MAX_SPARKS; i++) {
        s16 x;
        s16 y;
        if (sBrandSparks[i] == NULL) continue;

        x = SPR_getPositionX(sBrandSparks[i]) + sBrandSparkVX[i];
        y = SPR_getPositionY(sBrandSparks[i]) + sBrandSparkVY[i];
        sBrandSparkVY[i] += 1;
        if (y > 224 || x < -8 || x > 320) {
            SPR_releaseSprite(sBrandSparks[i]);
            sBrandSparks[i] = NULL;
        } else {
            SPR_setPosition(sBrandSparks[i], x, y);
            SPR_setFrame(sBrandSparks[i], (s16)(((frame >> 2) + i) & 3));
        }
    }
}

static void brandPrimeSparkExit(void)
{
    if (sBrandPrimeSpark != NULL) {
        SPR_releaseSprite(sBrandPrimeSpark);
        sBrandPrimeSpark = NULL;
    }
}

static void brandDebrisClear(void)
{
    u16 i;
    for (i = 0; i < BRAND_MAX_DEBRIS; i++) {
        if (sBrandDebris[i] != NULL) {
            SPR_releaseSprite(sBrandDebris[i]);
            sBrandDebris[i] = NULL;
        }
    }
}

static void brandDebrisSpawn(s16 originX, s16 originY)
{
    u16 i;

    brandDebrisClear();
    for (i = 0; i < BRAND_MAX_DEBRIS; i++) {
        sBrandDebris[i] = SPR_addSprite(
            &spr_brand_debris_v3,
            originX - 4,
            originY - 4,
            TILE_ATTR(PAL2, TRUE, FALSE, FALSE)
        );
        if (sBrandDebris[i] != NULL) {
            sBrandDebrisVX[i] = (s16)((i * 9 + 3) & 15) - 7;
            sBrandDebrisVY[i] = -((s16)(((i * 7 + 5) & 7) | 3));
        }
    }
}

static void brandDebrisUpdate(u16 frame)
{
    u16 i;
    for (i = 0; i < BRAND_MAX_DEBRIS; i++) {
        s16 x;
        s16 y;
        if (sBrandDebris[i] == NULL) continue;

        x = SPR_getPositionX(sBrandDebris[i]) + sBrandDebrisVX[i];
        y = SPR_getPositionY(sBrandDebris[i]) + sBrandDebrisVY[i];
        sBrandDebrisVY[i] += 1;
        if (y > 224 || x < -8 || x > 320) {
            SPR_releaseSprite(sBrandDebris[i]);
            sBrandDebris[i] = NULL;
        } else {
            SPR_setPosition(sBrandDebris[i], x, y);
            SPR_setFrame(sBrandDebris[i], (s16)(((frame >> 2) + i) & 3));
        }
    }
}

static void brandGlowEnter(s16 x, s16 y)
{
    sBrandGlowBaseY = y - 16;
    sBrandGlow = SPR_addSprite(
        &spr_brand_glow_v3,
        x - 16,
        sBrandGlowBaseY,
        TILE_ATTR(PAL2, FALSE, FALSE, FALSE)
    );
}

static void brandGlowUpdate(u16 frame)
{
    if (sBrandGlow == NULL) return;
    SPR_setPosition(
        sBrandGlow,
        SPR_getPositionX(sBrandGlow),
        sBrandGlowBaseY + ((s16)((frame >> 2) & 3) - 2)
    );
}

static void brandGlowExit(void)
{
    if (sBrandGlow != NULL) {
        SPR_releaseSprite(sBrandGlow);
        sBrandGlow = NULL;
    }
}

static const BrandSlotDef SLOT_ENGINE = {
    &img_brand_engine_bg_v3,
    &img_brand_engine_logo_v4, 5, 8,
    NULL, 0, 0,
    NULL,
    NULL
};

static const BrandSlotDef SLOT_AUTHOR = {
    &img_brand_author_bg_v3,
    NULL, 0, 0,
    NULL, 0, 0,
    NULL,
    NULL
};

static const BrandSlotDef SLOT_PROJECT = {
    &img_brand_project_bg_v3,
    NULL, 0, 0,
    &img_brand_presents_v4, 12, 23,
    NULL,
    NULL
};

static void brandEnterEngine(void)
{
    brandLoadSlot(&SLOT_ENGINE);
    PAL_setPalette(PAL2, spr_brand_spark_v3.palette->data, CPU);
    VDP_setVerticalScroll(BG_A, 56);
    sBrandPrimeSpark = SPR_addSprite(
        &spr_brand_spark_v3,
        156,
        -8,
        TILE_ATTR(PAL2, TRUE, FALSE, FALSE)
    );
}

static void brandUpdateEngine(u16 frame)
{
    s16 rise = 0;

    if (frame < 20) {
        brandFadeIn(img_brand_engine_bg_v3.palette->data, PAL0, frame, 20);
        brandFadeIn(img_brand_engine_logo_v4.palette->data, PAL1, frame, 20);
    }
    if (frame == 1) {
        if (sBrandPrimeSpark != NULL) SPR_setPosition(sBrandPrimeSpark, 156, 72);
    }
    if (frame == 2) {
        brandPrimeSparkExit();
        brandSparksSpawn(160, 104);
        AUDIO_playCue(AUDIO_CUE_BRAND_ENGINE_HIT);
        brandPulsePsg(0, 110, 2);
        brandPulsePsg(1, 220, 4);
        brandTriggerShake(4);
        brandImpactFlash(0, 4);
    }
    if (frame >= 3 && frame <= 6) {
        PAL_setPalette(PAL0, img_brand_engine_bg_v3.palette->data, CPU);
    }

    if (frame < 30) {
        if (frame >= 2) rise = 56 - (s16)(((s32)(frame - 2) * 56) / 28);
        else rise = 56;
    }
    VDP_setVerticalScroll(BG_A, rise);
    brandAnimateBackground(frame, -1);
    brandSparksUpdate(frame);

    if (frame >= 2 && frame < 30) {
        u16 i;
        const s16 amplitude = 8 - (s16)(((s32)(frame - 2) * 8) / 28);
        for (i = 0; i < 224; i++) sBrandLineScroll[i] = brandWaveOffset(frame, i, amplitude);
        VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_PLANE);
        VDP_setHorizontalScrollLine(BG_A, 0, sBrandLineScroll, 224, DMA_QUEUE);
    } else {
        VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
        VDP_setHorizontalScroll(BG_A, 0);
    }

    if (frame == 31) {
        brandLoadFont(&img_font_forge_v4);
        brandDrawFontText(&img_font_forge_v4, BRAND_ENGINE_SUBTEXT, 13, 24);
    }
    if (frame >= 31 && frame < 71 && ((frame - 31) % 5) == 0) {
        const u16 step = (frame - 31) / 5;
        PAL_setColor(16 + 9, BRAND_ENGINE_COOL[step]);
        PAL_setColor(16 + 10, BRAND_ENGINE_COOL[step]);
    }
    if (frame >= 71 && (frame & 3) == 0) {
        PAL_setColor(16 + 8, BRAND_ENGINE_SHIMMER[(frame >> 2) & 3]);
    }
    if (frame == 70) {
        brandPulsePsg(2, 55, 8);
    } else if (frame == 124) {
        AUDIO_stopAll();
    }
    if (frame >= 40 && frame <= 50 && (frame & 1) == 0) {
        brandSparksSpawn(80 + (s16)((frame - 40) * 16), 120);
    }
    brandFadeOut(frame, 130, 20);
}

static void brandExitEngine(void)
{
    brandPrimeSparkExit();
    brandSparksClear();
}

static void brandEnterAuthor(void)
{
    brandLoadSlot(&SLOT_AUTHOR);
    PAL_setPalette(PAL2, spr_brand_monogram_v3.palette->data, CPU);
    brandLoadFont(&img_font_terminal_v4);
}

static void brandUpdateAuthor(u16 frame)
{
    if (frame < 15) {
        brandFadeIn(img_brand_author_bg_v3.palette->data, PAL0, frame, 15);
    }
    brandAnimateBackground(frame, 1);

    if (frame == 11) {
        sBrandMonogram = SPR_addSprite(
            &spr_brand_monogram_v3,
            144,
            60,
            TILE_ATTR(PAL2, TRUE, FALSE, FALSE)
        );
        brandGlowEnter(160, 76);
        sBrandCursor = SPR_addSprite(
            &spr_brand_cursor_v3,
            BRAND_AUTHOR_TEXT_X * 8,
            BRAND_AUTHOR_TEXT_Y * 8,
            TILE_ATTR(PAL2, TRUE, FALSE, FALSE)
        );
        AUDIO_playCue(AUDIO_CUE_BRAND_AUTHOR_CLICK);
    }

    brandGlowUpdate(frame);
    if (sBrandMonogram != NULL) {
        u16 animFrame;
        if (frame < 71) {
            animFrame = ((frame - 11) * 12) / 60;
            if (animFrame > 11) animFrame = 11;
        } else {
            animFrame = 11;
        }
        SPR_setFrame(sBrandMonogram, (s16)animFrame);
        SPR_setPosition(sBrandMonogram, 144, 60 + ((s16)((frame >> 2) & 3) - 2));
    }

    if (frame >= 11 && frame <= 30 && ((frame - 11) % 6) == 0) {
        AUDIO_playCue(AUDIO_CUE_BRAND_AUTHOR_CLICK);
        PSG_setNoise(PSG_NOISE_TYPE_PERIODIC, PSG_NOISE_FREQ_CLOCK8);
        PSG_setEnvelope(2, 5);
    }

    if (frame >= 50 && frame < 110) {
        u16 visibleChars = (frame - 50) >> 2;
        const u16 textLength = sizeof(BRAND_AUTHOR_TEXT) - 1;
        if (visibleChars > textLength) visibleChars = textLength;
        if (visibleChars > 0 && ((frame - 50) & 3) == 0) {
            brandDrawFontGlyph(
                &img_font_terminal_v4,
                BRAND_AUTHOR_TEXT[visibleChars - 1],
                BRAND_AUTHOR_TEXT_X + visibleChars - 1,
                BRAND_AUTHOR_TEXT_Y
            );
            AUDIO_playCue(AUDIO_CUE_BRAND_AUTHOR_CLICK);
        }
        if (sBrandCursor != NULL) {
            SPR_setPosition(
                sBrandCursor,
                (BRAND_AUTHOR_TEXT_X + visibleChars) * 8,
                BRAND_AUTHOR_TEXT_Y * 8
            );
            SPR_setFrame(sBrandCursor, (s16)((frame >> 2) % 3));
        }
    }

    if (frame == 110) {
        VDP_drawImageEx(
            BG_A,
            &img_brand_author_signature_v4,
            TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, BRAND_TILE_LOGO),
            5,
            17,
            TRUE,
            FALSE
        );
        AUDIO_playCue(AUDIO_CUE_BRAND_AUTHOR_BELL);
        if (sBrandCursor != NULL) {
            SPR_releaseSprite(sBrandCursor);
            sBrandCursor = NULL;
        }
    }
    if (frame >= 120 && (frame & 3) == 0) {
        PAL_setColor(32 + 14, BRAND_AUTHOR_GLOW[(frame >> 2) & 3]);
    }
    brandFadeOut(frame, 130, 20);
}

static void brandExitAuthor(void)
{
    if (sBrandMonogram != NULL) {
        SPR_releaseSprite(sBrandMonogram);
        sBrandMonogram = NULL;
    }
    if (sBrandCursor != NULL) {
        SPR_releaseSprite(sBrandCursor);
        sBrandCursor = NULL;
    }
    brandGlowExit();
}

static void brandEnterProject(void)
{
    brandLoadSlot(&SLOT_PROJECT);
    PAL_setPalette(PAL2, spr_brand_shield_v3.palette->data, CPU);
    brandLoadFont(&img_font_crest_v4);
    VDP_setVerticalScroll(BG_A, 40);
    AUDIO_playCue(AUDIO_CUE_BRAND_PROJECT_WHOOSH);
}

static void brandUpdateProject(u16 frame)
{
    u16 i;
    u16 amplitude = 0;

    if (frame < 15) {
        brandFadeIn(img_brand_project_bg_v3.palette->data, PAL0, frame, 15);
    }
    brandAnimateBackground(frame, -1);
    brandDebrisUpdate(frame);

    if (frame < 16) {
        VDP_setVerticalScroll(BG_A, 40 - (s16)(((s32)frame * 40) / 15));
    } else {
        VDP_setVerticalScroll(BG_A, 0);
    }

    if (frame == 16) {
        sBrandShield = SPR_addSprite(
            &spr_brand_shield_v3,
            128,
            -32,
            TILE_ATTR(PAL2, TRUE, FALSE, FALSE)
        );
    }
    if (sBrandShield != NULL && frame >= 16 && frame < 26) {
        const u16 local = frame - 16;
        SPR_setFrame(sBrandShield, (s16)((local * 4) / 10));
        SPR_setPosition(sBrandShield, 128, -32 + (s16)(local * 8));
    }

    if (frame == 26) {
        if (sBrandShield != NULL) {
            SPR_setFrame(sBrandShield, 3);
            SPR_setPosition(sBrandShield, 128, 48);
        }
        brandDebrisSpawn(160, 82);
        VDP_drawImageEx(
            BG_A,
            &img_brand_project_logo_v4,
            TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, BRAND_TILE_LOGO),
            5,
            8,
            TRUE,
            FALSE
        );
        brandDrawFontText(&img_font_crest_v4, BRAND_PROJECT_TEXT, 13, 24);
        AUDIO_playCue(AUDIO_CUE_BRAND_PROJECT_TAIL);
        brandPulsePsg(0, 55, 1);
        brandPulsePsg(1, 110, 3);
        brandPulsePsg(2, 220, 5);
        PSG_setNoise(PSG_NOISE_TYPE_WHITE, PSG_NOISE_FREQ_CLOCK2);
        PSG_setEnvelope(3, 2);
        brandTriggerShake(3);
        brandImpactFlash(0, 4);
    }
    if (frame >= 27 && frame <= 30) {
        PAL_setPalette(PAL0, img_brand_project_bg_v3.palette->data, CPU);
    }

    if (frame >= 26 && frame < 38) amplitude = (u16)(3 - ((frame - 26) / 4));
    for (i = 0; i < 224; i++) {
        sBrandLineScroll[i] = (i < 42 || i > 205) ? 0 : brandWaveOffset(frame, i, amplitude);
    }
    if (amplitude > 0) {
        VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_PLANE);
        VDP_setHorizontalScrollLine(BG_A, 0, sBrandLineScroll, 224, DMA_QUEUE);
    } else {
        VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
        VDP_setHorizontalScroll(BG_A, 0);
    }

    if (frame >= 26 && frame < 80 && (frame & 7) == 0) {
        PAL_setColor(16 + 13, BRAND_PROJECT_FLASH[(frame >> 3) % 5]);
    }
    if (frame == 80) {
        brandPulsePsg(0, 440, 5);
    } else if (frame == 88) {
        brandPulsePsg(0, 554, 5);
    } else if (frame == 96) {
        brandPulsePsg(0, 659, 5);
    } else if (frame == 104) {
        brandPulsePsg(0, 880, 4);
    }

    if (frame >= 150 && ((frame - 150) & 1) == 0) {
        const u16 color = (frame - 150) >> 1;
        if (color < 16) {
            PAL_setColor(color, 0);
            PAL_setColor(16 + color, 0);
            PAL_setColor(32 + color, 0);
            PAL_setColor(48 + color, 0);
        }
    }
}

static void brandExitProject(void)
{
    if (sBrandShield != NULL) {
        SPR_releaseSprite(sBrandShield);
        sBrandShield = NULL;
    }
    brandDebrisClear();
}

static void brandSetPhase(u8 phase)
{
    if (sBrandPhase == phase) return;

    if (sBrandPhase == BRAND_PHASE_ENGINE) brandExitEngine();
    else if (sBrandPhase == BRAND_PHASE_AUTHOR) brandExitAuthor();
    else if (sBrandPhase == BRAND_PHASE_PROJECT) brandExitProject();

    sBrandPhase = phase;
    if (phase == BRAND_PHASE_ENGINE) brandEnterEngine();
    else if (phase == BRAND_PHASE_AUTHOR) brandEnterAuthor();
    else brandEnterProject();
}

static void brandExitToBoot(void)
{
    brandExitEngine();
    brandExitAuthor();
    brandExitProject();
    AUDIO_stopAll();
    brandResetScroll();
    APP_changeScene(APP_SCENE_BOOT);
}

void SCENE_brandingEnter(void)
{
    u16 i;

    gApp.showDebugHud = FALSE;
    sBrandPhase = 0xFF;
    sBrandPrimeSpark = NULL;
    sBrandMonogram = NULL;
    sBrandShield = NULL;
    sBrandGlow = NULL;
    sBrandCursor = NULL;
    for (i = 0; i < BRAND_MAX_SPARKS; i++) sBrandSparks[i] = NULL;
    for (i = 0; i < BRAND_MAX_DEBRIS; i++) sBrandDebris[i] = NULL;
    sBrandShakeIntensity = 0;
    sBrandShakeFrame = 0;
    sBrandFadeCached = FALSE;
    brandResetScreen();
}

void SCENE_brandingUpdate(void)
{
    const u16 frame = gApp.sceneFrames;

    if (INPUT_pressed(BUTTON_START) || INPUT_pressed(BUTTON_A)) {
        brandExitToBoot();
        return;
    }
    if (frame < BRAND_ENGINE_END) {
        brandSetPhase(BRAND_PHASE_ENGINE);
        brandUpdateEngine(frame);
        return;
    }
    if (frame < BRAND_AUTHOR_END) {
        brandSetPhase(BRAND_PHASE_AUTHOR);
        brandUpdateAuthor(frame - BRAND_ENGINE_END);
        return;
    }
    if (frame < BRAND_PROJECT_END) {
        brandSetPhase(BRAND_PHASE_PROJECT);
        brandUpdateProject(frame - BRAND_AUTHOR_END);
        return;
    }
    brandExitToBoot();
}
