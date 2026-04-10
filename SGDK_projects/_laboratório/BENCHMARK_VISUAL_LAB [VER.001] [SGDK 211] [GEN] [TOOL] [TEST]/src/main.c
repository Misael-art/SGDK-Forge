#include <genesis.h>

#include "game_vars.h"
#include "resources.h"

#define VIEW_TILES_W 40
#define VIEW_TILES_H 28
#define HALF_TILES_W 20
#define ENABLE_VISUAL_CAPTURE 1
#define ENABLE_LAB_SPRITES 0
#define ENABLE_SENTINEL_IMAGES 1
#define ENABLE_BG_IMAGES 1
#define ENABLE_WINDOW_UI 1
#define ENABLE_INPUT_HANDLING 1
#define MANUAL_SENTINEL_TILE_COUNT 24
#define SENTINEL_TILE_X_LEFT 7
#define SENTINEL_TILE_X_RIGHT 27
#define SENTINEL_TILE_Y 14

#define LEFT_LANE_X 0
#define RIGHT_LANE_X 20

#define BASIC_SPRITE_X 56
#define ELITE_SPRITE_X 216
#define BASE_SPRITE_Y 112

#define EVIDENCE_MAGIC 0x564C4142
#define EVIDENCE_VERSION 0x0001
#define EVIDENCE_FLAG_OVERLAY 0x0001
#define EVIDENCE_FLAG_BG_A 0x0002
#define EVIDENCE_FLAG_BG_B 0x0004

#define SPRITE_TILE_WORDS 16
#define MAX_CAPTURED_SPRITE_TILES 64
#define MAX_CAPTURED_SPRITE_WORDS (MAX_CAPTURED_SPRITE_TILES * SPRITE_TILE_WORDS)

typedef struct
{
    u32 magic;
    u16 version;
    u16 total_bytes;
    u16 scene_id;
    u16 lab_mode;
    u32 frame_counter;
    u16 flags;
    u16 plane_width;
    u16 plane_height;
    u16 screen_width;
    u16 screen_height;
    u16 bg_a_addr;
    u16 bg_b_addr;
    u16 window_addr;
    u16 sprite_table_addr;
    u16 basic_bg_b_tile_index;
    u16 basic_bg_b_tile_count;
    u16 basic_bg_a_tile_index;
    u16 basic_bg_a_tile_count;
    u16 elite_bg_b_tile_index;
    u16 elite_bg_b_tile_count;
    u16 elite_bg_a_tile_index;
    u16 elite_bg_a_tile_count;
    u16 basic_sprite_tile_index;
    u16 basic_sprite_tile_count;
    u16 elite_sprite_tile_index;
    u16 elite_sprite_tile_count;
    u32 basic_bg_b_checksum;
    u32 basic_bg_a_checksum;
    u32 elite_bg_b_checksum;
    u32 elite_bg_a_checksum;
    u16 cram[64];
    u16 vsram[40];
    u16 bg_a_tiles[VIEW_TILES_W * VIEW_TILES_H];
    u16 bg_b_tiles[VIEW_TILES_W * VIEW_TILES_H];
    u16 sprite_table[80 * 4];
    u16 basic_sprite_tiles[MAX_CAPTURED_SPRITE_WORDS];
    u16 elite_sprite_tiles[MAX_CAPTURED_SPRITE_WORDS];
} VisualEvidenceBlock;

typedef struct
{
    const char* title;
    const char* basicHeadline;
    const char* eliteHeadline;
    const char* basicBody;
    const char* eliteBody;
} LabCopy;

static const LabCopy kLabCopy[LAB_MODE_COUNT] = {
    {
        "SILHOUETTE LAB",
        "BASIC: EDGE SOFT, VALUE FLAT",
        "ELITE: OUTLINE + INTERNAL READ",
        "BASIC some no fundo ruidoso.",
        "ELITE sustenta leitura em 1 frame."
    },
    {
        "LAYER CONTRAST LAB",
        "BASIC: BG_A e BG_B brigam",
        "ELITE: profundidade hierarquica",
        "BASIC divide a atencao com o fundo.",
        "ELITE protege o plano jogavel."
    },
    {
        "ANIMATION READABILITY LAB",
        "BASIC: 2 poses e massa dura",
        "ELITE: micro-motion e volume",
        "BASIC perde energia entre quadros.",
        "ELITE muda peso sem perder forma."
    }
};

static const s16 kEliteBobOffsets[3] = { 0, -1, 0 };

static VisualEvidenceBlock gVisualEvidence;
static bool gOverlayVisible = TRUE;
static bool gBgAEnabled = TRUE;
static bool gBgBEnabled = TRUE;
static bool gSceneDirty = FALSE;
static bool gInputArmed = FALSE;
static bool gEvidenceDirty = TRUE;
static u16 gEvidenceCooldown = 30;
static u16 gInputUnlockFrames = 30;

static u16 gBasicBgBTileIndex = TILE_USER_INDEX;
static u16 gEliteBgBTileIndex = TILE_USER_INDEX;
static u16 gBasicBgATileIndex = TILE_USER_INDEX;
static u16 gEliteBgATileIndex = TILE_USER_INDEX;
static u16 gBasicSpriteTileIndex = TILE_USER_INDEX;
static u16 gEliteSpriteTileIndex = TILE_USER_INDEX;
static u16 gBasicCurrentFrame = 0;
static u16 gEliteCurrentFrame = 0;
static s16 gBasicCurrentY = BASE_SPRITE_Y;
static s16 gEliteCurrentY = BASE_SPRITE_Y;

static u16 min_u16(u16 a, u16 b)
{
    return (a < b) ? a : b;
}

static void read_vdp_words(u32 command, u16* destination, u16 count)
{
    vu32* ctrl = (vu32*) VDP_CTRL_PORT;
    vu16* data = (vu16*) VDP_DATA_PORT;
    u16 i;

    VDP_setAutoInc(2);
    *ctrl = command;
    for (i = 0; i < count; i++)
    {
        destination[i] = *data;
    }
}

static u32 hash_vram_region(u16 address, u16 wordCount)
{
    vu32* ctrl = (vu32*) VDP_CTRL_PORT;
    vu16* data = (vu16*) VDP_DATA_PORT;
    u32 hash = 2166136261UL;
    u16 i;

    VDP_setAutoInc(2);
    *ctrl = VDP_READ_VRAM_ADDR(address);
    for (i = 0; i < wordCount; i++)
    {
        hash ^= (u32)(*data);
        hash *= 16777619UL;
    }

    return hash;
}

static void capture_visible_plane(VDPPlane plane, u16* destination)
{
    const u16 planeAddress = (plane == BG_A) ? bga_addr : bgb_addr;
    u16 row;
    u16 col;

    for (row = 0; row < VIEW_TILES_H; row++)
    {
        for (col = 0; col < VIEW_TILES_W; col++)
        {
            const u16 vramAddress = planeAddress + (((row * planeWidth) + col) * 2);
            read_vdp_words(VDP_READ_VRAM_ADDR(vramAddress), &destination[(row * VIEW_TILES_W) + col], 1);
        }
    }
}

static void capture_sprite_tiles(u16 tileIndex, u16 tileCount, u16* buffer, u16* outIndex, u16* outCount)
{
    u16 i;
    const u16 clampedTileCount = min_u16(tileCount, MAX_CAPTURED_SPRITE_TILES);

    for (i = 0; i < MAX_CAPTURED_SPRITE_WORDS; i++)
    {
        buffer[i] = 0;
    }

    if (clampedTileCount > 0)
    {
        read_vdp_words(
            VDP_READ_VRAM_ADDR(tileIndex * TILE_SIZE),
            buffer,
            clampedTileCount * SPRITE_TILE_WORDS
        );
    }

    *outIndex = tileIndex;
    *outCount = clampedTileCount;
}

static void write_visual_evidence_to_sram(void)
{
    const u8* bytes = (const u8*) &gVisualEvidence;
    u32 i;

    SRAM_enable();
    for (i = 0; i < sizeof(gVisualEvidence); i++)
    {
        SRAM_writeByte(i, bytes[i]);
    }
    SRAM_disable();
}

static void capture_visual_evidence(void)
{
    SYS_disableInts();
    VDP_waitDMACompletion();

    gVisualEvidence.magic = EVIDENCE_MAGIC;
    gVisualEvidence.version = EVIDENCE_VERSION;
    gVisualEvidence.total_bytes = sizeof(gVisualEvidence);
    gVisualEvidence.scene_id = (u16) gLabMode + 1;
    gVisualEvidence.lab_mode = (u16) gLabMode;
    gVisualEvidence.frame_counter = gFrames;
    gVisualEvidence.flags = (gOverlayVisible ? EVIDENCE_FLAG_OVERLAY : 0)
        | (gBgAEnabled ? EVIDENCE_FLAG_BG_A : 0)
        | (gBgBEnabled ? EVIDENCE_FLAG_BG_B : 0);
    gVisualEvidence.plane_width = planeWidth;
    gVisualEvidence.plane_height = planeHeight;
    gVisualEvidence.screen_width = screenWidth;
    gVisualEvidence.screen_height = screenHeight;
    gVisualEvidence.bg_a_addr = bga_addr;
    gVisualEvidence.bg_b_addr = bgb_addr;
    gVisualEvidence.window_addr = window_addr;
    gVisualEvidence.sprite_table_addr = slist_addr;

    gVisualEvidence.basic_bg_b_tile_index = gBasicBgBTileIndex;
    gVisualEvidence.basic_bg_b_tile_count = img_basic_bg_b.tileset->numTile;
    gVisualEvidence.basic_bg_a_tile_index = gBasicBgATileIndex;
    gVisualEvidence.basic_bg_a_tile_count = img_basic_bg_a.tileset->numTile;
    gVisualEvidence.elite_bg_b_tile_index = gEliteBgBTileIndex;
    gVisualEvidence.elite_bg_b_tile_count = img_elite_bg_b.tileset->numTile;
    gVisualEvidence.elite_bg_a_tile_index = gEliteBgATileIndex;
    gVisualEvidence.elite_bg_a_tile_count = img_elite_bg_a.tileset->numTile;

    read_vdp_words(VDP_READ_CRAM_ADDR(0), gVisualEvidence.cram, 64);
    read_vdp_words(VDP_READ_VSRAM_ADDR(0), gVisualEvidence.vsram, 40);
    capture_visible_plane(BG_A, gVisualEvidence.bg_a_tiles);
    capture_visible_plane(BG_B, gVisualEvidence.bg_b_tiles);
    read_vdp_words(VDP_READ_VRAM_ADDR(slist_addr), gVisualEvidence.sprite_table, 80 * 4);
    capture_sprite_tiles(gBasicSpriteTileIndex, MANUAL_SENTINEL_TILE_COUNT, gVisualEvidence.basic_sprite_tiles, &gVisualEvidence.basic_sprite_tile_index, &gVisualEvidence.basic_sprite_tile_count);
    capture_sprite_tiles(gEliteSpriteTileIndex, MANUAL_SENTINEL_TILE_COUNT, gVisualEvidence.elite_sprite_tiles, &gVisualEvidence.elite_sprite_tile_index, &gVisualEvidence.elite_sprite_tile_count);

    gVisualEvidence.basic_bg_b_checksum = hash_vram_region(gBasicBgBTileIndex * TILE_SIZE, img_basic_bg_b.tileset->numTile * SPRITE_TILE_WORDS);
    gVisualEvidence.basic_bg_a_checksum = hash_vram_region(gBasicBgATileIndex * TILE_SIZE, img_basic_bg_a.tileset->numTile * SPRITE_TILE_WORDS);
    gVisualEvidence.elite_bg_b_checksum = hash_vram_region(gEliteBgBTileIndex * TILE_SIZE, img_elite_bg_b.tileset->numTile * SPRITE_TILE_WORDS);
    gVisualEvidence.elite_bg_a_checksum = hash_vram_region(gEliteBgATileIndex * TILE_SIZE, img_elite_bg_a.tileset->numTile * SPRITE_TILE_WORDS);

    write_visual_evidence_to_sram();
    SYS_enableInts();
}

static void mark_evidence_dirty(u16 cooldown)
{
    gEvidenceDirty = TRUE;
    gEvidenceCooldown = cooldown;
}

static void build_vram_layout(void)
{
    gBasicBgBTileIndex = TILE_USER_INDEX;
    gEliteBgBTileIndex = gBasicBgBTileIndex + img_basic_bg_b.tileset->numTile;
    gBasicBgATileIndex = gEliteBgBTileIndex + img_elite_bg_b.tileset->numTile;
    gEliteBgATileIndex = gBasicBgATileIndex + img_basic_bg_a.tileset->numTile;
    gBasicSpriteTileIndex = gEliteBgATileIndex + img_elite_bg_a.tileset->numTile;
    gEliteSpriteTileIndex = gBasicSpriteTileIndex + MANUAL_SENTINEL_TILE_COUNT;
}

static void load_palettes(void)
{
    PAL_setPalette(PAL0, pal_basic_bg.data, DMA);
    PAL_setPalette(PAL1, pal_basic_sprite.data, DMA);
    PAL_setPalette(PAL2, pal_elite_bg.data, DMA);
    PAL_setPalette(PAL3, pal_elite_sprite.data, DMA);
}

static void draw_benchmark_planes(void)
{
    VDP_clearPlane(BG_B, TRUE);
    VDP_clearPlane(BG_A, TRUE);

    if (!ENABLE_BG_IMAGES)
    {
        return;
    }

    if (gBgBEnabled)
    {
        VDP_drawImageEx(BG_B, &img_basic_bg_b, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, gBasicBgBTileIndex), LEFT_LANE_X, 0, FALSE, FALSE);
        VDP_drawImageEx(BG_B, &img_elite_bg_b, TILE_ATTR_FULL(PAL2, FALSE, FALSE, FALSE, gEliteBgBTileIndex), RIGHT_LANE_X, 0, FALSE, FALSE);
    }

    if (gBgAEnabled)
    {
        VDP_drawImageEx(BG_A, &img_basic_bg_a, TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, gBasicBgATileIndex), LEFT_LANE_X, 0, FALSE, FALSE);
        VDP_drawImageEx(BG_A, &img_elite_bg_a, TILE_ATTR_FULL(PAL2, TRUE, FALSE, FALSE, gEliteBgATileIndex), RIGHT_LANE_X, 0, FALSE, FALSE);
    }
}

static void resolve_sprite_pose(u16* basicFrame, u16* eliteFrame)
{
    *basicFrame = 0;
    *eliteFrame = 0;

    if (gLabMode == ANIMATION_READABILITY_LAB)
    {
        *basicFrame = ((gFrames / 18) & 1);
        *eliteFrame = (gFrames / 10) % 3;
    }
    else if (gLabMode == LAYER_CONTRAST_LAB)
    {
        *basicFrame = 2;
        *eliteFrame = 2;
    }
}

static void update_sprite_frames(void)
{
    u16 basicFrame;
    u16 eliteFrame;

    resolve_sprite_pose(&basicFrame, &eliteFrame);
    if ((basicFrame != gBasicCurrentFrame) || (eliteFrame != gEliteCurrentFrame))
    {
        gBasicCurrentFrame = basicFrame;
        gEliteCurrentFrame = eliteFrame;
        gSceneDirty = TRUE;
    }
}

static void draw_sentinel_images(void)
{
    if (!ENABLE_SENTINEL_IMAGES)
    {
        return;
    }

    const Image* basicImage = &img_basic_sentinel_f0;
    const Image* eliteImage = &img_elite_sentinel_f0;

    if (gBasicCurrentFrame == 1)
    {
        basicImage = &img_basic_sentinel_f1;
    }
    else if (gBasicCurrentFrame >= 2)
    {
        basicImage = &img_basic_sentinel_f2;
    }

    if (gEliteCurrentFrame == 1)
    {
        eliteImage = &img_elite_sentinel_f1;
    }
    else if (gEliteCurrentFrame >= 2)
    {
        eliteImage = &img_elite_sentinel_f2;
    }

    VDP_drawImageEx(BG_A, basicImage, TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, gBasicSpriteTileIndex), SENTINEL_TILE_X_LEFT, SENTINEL_TILE_Y, FALSE, FALSE);
    VDP_drawImageEx(BG_A, eliteImage, TILE_ATTR_FULL(PAL3, TRUE, FALSE, FALSE, gEliteSpriteTileIndex), SENTINEL_TILE_X_RIGHT, SENTINEL_TILE_Y, FALSE, FALSE);
}

static void draw_window_text_fill(const char* text, u16 x, u16 y, u16 width)
{
    // VDP_drawTextBGFill() overflows when str is longer than len, so we pre-truncate safely.
    char buffer[VIEW_TILES_W + 1];
    u16 i = 0;

    while ((i < width) && text[i])
    {
        buffer[i] = text[i];
        i++;
    }

    while (i < width)
    {
        buffer[i++] = ' ';
    }

    buffer[width] = '\0';
    VDP_drawTextBG(WINDOW, buffer, x, y);
}

static void draw_window_ui(void)
{
    if (!ENABLE_WINDOW_UI)
    {
        return;
    }

    const LabCopy* copy = &kLabCopy[gLabMode];

    VDP_clearTextAreaBG(WINDOW, 0, 0, VIEW_TILES_W, VIEW_TILES_H);
    draw_window_text_fill("BENCHMARK VISUAL LAB", 10, 0, 20);
    draw_window_text_fill(copy->title, 12, 1, 18);
    draw_window_text_fill("BASIC", 6, 3, 5);
    draw_window_text_fill("ELITE", 27, 3, 5);
    draw_window_text_fill("< > prova  A overlay  B BG_A  C BG_B", 1, 26, 38);
    draw_window_text_fill("Se nao foi visto no BlastEm, nao existe.", 1, 27, 38);

    if (!gOverlayVisible)
    {
        return;
    }

    draw_window_text_fill(copy->basicHeadline, 1, 21, 19);
    draw_window_text_fill(copy->eliteHeadline, 21, 21, 19);
    draw_window_text_fill(copy->basicBody, 1, 23, 19);
    draw_window_text_fill(copy->eliteBody, 21, 23, 19);
}

static void create_sprites(void)
{
    (void) 0;
}

static void redraw_scene(void)
{
    draw_benchmark_planes();
    draw_sentinel_images();
    draw_window_ui();
    mark_evidence_dirty(24);
}

static void update_input(void)
{
    if (!ENABLE_INPUT_HANDLING)
    {
        return;
    }

    const u16 state = JOY_readJoypad(JOY_1);

    if (!gInputArmed)
    {
        if (gInputUnlockFrames > 0)
        {
            gInputUnlockFrames--;
        }
        else if (state == 0)
        {
            gInputArmed = TRUE;
        }

        gPrevInput = state;
        return;
    }

    const u16 pressed = state & ~gPrevInput;

    if (pressed & BUTTON_LEFT)
    {
        gLabMode = (gLabMode == SILHOUETTE_LAB) ? (LAB_MODE_COUNT - 1) : (gLabMode - 1);
        gSceneDirty = TRUE;
    }

    if (pressed & BUTTON_RIGHT)
    {
        gLabMode = (gLabMode + 1) % LAB_MODE_COUNT;
        gSceneDirty = TRUE;
    }

    if (pressed & BUTTON_A)
    {
        gOverlayVisible = !gOverlayVisible;
        gSceneDirty = TRUE;
    }

    if (pressed & BUTTON_B)
    {
        gBgAEnabled = !gBgAEnabled;
        gSceneDirty = TRUE;
    }

    if (pressed & BUTTON_C)
    {
        gBgBEnabled = !gBgBEnabled;
        gSceneDirty = TRUE;
    }

    gPrevInput = state;
}

static void init_lab(void)
{
    VDP_setScreenWidth320();
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_setBackgroundColor(0);
    VDP_setWindowFullScreen();
    VDP_setTextPlane(WINDOW);
    VDP_setTextPalette(PAL0);
    VDP_setTextPriority(TRUE);

    build_vram_layout();
    load_palettes();

    create_sprites();
    redraw_scene();
    SYS_doVBlankProcess();
    gPrevInput = JOY_readJoypad(JOY_1);
}

int main(bool hardReset)
{
    (void) hardReset;

    init_lab();

    while (TRUE)
    {
        gFrames++;
        update_sprite_frames();
        SYS_doVBlankProcess();
        update_input();
        if (gSceneDirty)
        {
            redraw_scene();
            gSceneDirty = FALSE;
        }

        if (ENABLE_VISUAL_CAPTURE && gEvidenceDirty)
        {
            if (gEvidenceCooldown > 0)
            {
                gEvidenceCooldown--;
            }
            else
            {
                capture_visual_evidence();
                gEvidenceDirty = FALSE;
            }
        }
    }

    return 0;
}
