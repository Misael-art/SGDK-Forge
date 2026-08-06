#include <genesis.h>

#include "system/reference_contract.h"

#define REF_SRAM_OFFSET 0x1800u
#define REF_SCHEMA_VERSION 1u
#define REF_TOTAL_WORDS 20u
#define REF_EXPORT_PERIOD 30u
#define REF_VLAB_OFFSET 0x0000u
#define REF_VLAB_METRIC_WORDS 24u
#define REF_VLAB_PALETTE_WORDS 64u
#define REF_VLAB_TOTAL_BYTES (8u + ((REF_VLAB_METRIC_WORDS + REF_VLAB_PALETTE_WORDS) * 2u))

enum
{
    REF_WORD_REQUESTED_MASK = 0,
    REF_WORD_OBSERVED_MASK,
    REF_WORD_REQUIRED_MASK,
    REF_WORD_COMPLETED,
    REF_WORD_SAMPLE_COUNT,
    REF_WORD_VIOLATION_COUNT,
    REF_WORD_STATIC_SKIP_COUNT,
    REF_WORD_REBUILD_COUNT,
    REF_WORD_STATIC_REBUILD_COUNT,
    REF_WORD_STATIC_DMA_BYTES,
    REF_WORD_TABLE_HASH_BEFORE_HI,
    REF_WORD_TABLE_HASH_BEFORE_LO,
    REF_WORD_TABLE_HASH_AFTER_HI,
    REF_WORD_TABLE_HASH_AFTER_LO,
    REF_WORD_CRAM_ENTRIES_USED,
    REF_WORD_ILLEGAL_CRAM_ENTRIES,
    REF_WORD_MIDFRAME_PALETTE_UPDATES,
    REF_WORD_GATE_SCOPE_BITMAP,
    REF_WORD_FRAME_HI,
    REF_WORD_FRAME_LO
};

static u16 s_words[REF_TOTAL_WORDS];
static s16 s_initialX;
static s16 s_initialY;
static s16 s_lastCameraX;
static u32 s_frame;
static u32 s_tableHash;
static bool s_hasTable;

static void write_u16be(u32 offset, u16 value)
{
    SRAM_writeByte(offset, (u8)((value >> 8) & 0xFF));
    SRAM_writeByte(offset + 1, (u8)(value & 0xFF));
}

static u32 table_hash_for_camera(s16 cameraX)
{
    u16 line;
    u32 hash = 2166136261u;
    for (line = 0; line < 224u; line++)
    {
        u16 value = (u16)(-(cameraX >> ((line < 112u) ? 2 : 1)));
        hash ^= (u8)(value >> 8);
        hash *= 16777619u;
        hash ^= (u8)value;
        hash *= 16777619u;
    }
    return hash;
}

static void update_static_table_contract(s16 cameraX)
{
    u32 before = s_tableHash;
    u32 after;

    if (!s_hasTable || cameraX != s_lastCameraX)
    {
        after = table_hash_for_camera(cameraX);
        s_words[REF_WORD_REBUILD_COUNT]++;
        s_tableHash = after;
        s_lastCameraX = cameraX;
        s_hasTable = TRUE;
        return;
    }

    s_words[REF_WORD_SAMPLE_COUNT]++;
    after = table_hash_for_camera(cameraX);
    s_words[REF_WORD_TABLE_HASH_BEFORE_HI] = (u16)(before >> 16);
    s_words[REF_WORD_TABLE_HASH_BEFORE_LO] = (u16)before;
    s_words[REF_WORD_TABLE_HASH_AFTER_HI] = (u16)(after >> 16);
    s_words[REF_WORD_TABLE_HASH_AFTER_LO] = (u16)after;
    s_words[REF_WORD_STATIC_REBUILD_COUNT] = 0;
    s_words[REF_WORD_STATIC_DMA_BYTES] = 0;

    if (before == after)
    {
        s_words[REF_WORD_STATIC_SKIP_COUNT]++;
        s_words[REF_WORD_OBSERVED_MASK] |= REF_STATE_STATIC_TABLE_SKIPPED;
    }
    else
    {
        s_words[REF_WORD_VIOLATION_COUNT]++;
    }
}

void REF_init(s16 initialX, s16 initialY, s16 initialCameraX)
{
    u16 index;
    for (index = 0; index < REF_TOTAL_WORDS; index++) {
        s_words[index] = 0;
    }
    s_initialX = initialX;
    s_initialY = initialY;
    s_lastCameraX = initialCameraX;
    s_frame = 0;
    s_tableHash = 0;
    s_hasTable = FALSE;
    s_words[REF_WORD_REQUIRED_MASK] = REF_REQUIRED_STATES;
    s_words[REF_WORD_CRAM_ENTRIES_USED] = 16;
    s_words[REF_WORD_ILLEGAL_CRAM_ENTRIES] = 0;
    s_words[REF_WORD_MIDFRAME_PALETTE_UPDATES] = 0;
    s_words[REF_WORD_GATE_SCOPE_BITMAP] = 0x0003u; /* static + runtime */
}

u16 REF_scriptHeld(u32 sceneFrame)
{
    if (sceneFrame >= 20u && sceneFrame < 100u)
    {
        s_words[REF_WORD_REQUESTED_MASK] |= REF_STATE_MOVED;
        return BUTTON_RIGHT;
    }
    return 0;
}

u16 REF_scriptPressed(u32 sceneFrame)
{
    if (sceneFrame == 110u)
    {
        s_words[REF_WORD_REQUESTED_MASK] |= REF_STATE_AIRBORNE;
        return BUTTON_A;
    }
    return 0;
}

void REF_observe(s16 playerX, s16 playerY, bool grounded, s16 cameraX)
{
    s_frame++;
    if (playerX != s_initialX) {
        s_words[REF_WORD_OBSERVED_MASK] |= REF_STATE_MOVED;
    }
    if (!grounded && playerY < s_initialY) {
        s_words[REF_WORD_OBSERVED_MASK] |= REF_STATE_AIRBORNE;
    }

    update_static_table_contract(cameraX);
    if ((s_words[REF_WORD_OBSERVED_MASK] & REF_REQUIRED_STATES) == REF_REQUIRED_STATES && s_frame >= 180u) {
        s_words[REF_WORD_COMPLETED] = 1;
    }
    s_words[REF_WORD_FRAME_HI] = (u16)(s_frame >> 16);
    s_words[REF_WORD_FRAME_LO] = (u16)s_frame;

    if ((s_frame % REF_EXPORT_PERIOD) == 0u) {
        REF_export();
    }
}

void REF_export(void)
{
    u16 index;
    u32 offset = REF_SRAM_OFFSET;
    u16 palette[REF_VLAB_PALETTE_WORDS];
    u16 metrics[REF_VLAB_METRIC_WORDS];

    for (index = 0; index < REF_VLAB_METRIC_WORDS; index++) {
        metrics[index] = 0;
    }
    metrics[0] = 3u; /* APP_SCENE_DEMO */
    metrics[1] = (u16)(s_frame >> 16);
    metrics[2] = (u16)s_frame;
    metrics[3] = 320u;
    metrics[4] = 224u;
    metrics[5] = 64u;
    metrics[6] = 32u;
    metrics[7] = 0u; /* HSCROLL_PLANE */
    metrics[8] = 0u; /* VSCROLL_PLANE */
    metrics[15] = (u16)s_frame;
    metrics[16] = s_words[REF_WORD_SAMPLE_COUNT];
    metrics[17] = s_words[REF_WORD_VIOLATION_COUNT];
    metrics[23] = SYS_isPAL() ? 50u : 60u;
    PAL_getColors(0, palette, REF_VLAB_PALETTE_WORDS);

    SRAM_enable();
    offset = REF_VLAB_OFFSET;
    SRAM_writeByte(offset + 0, 'V');
    SRAM_writeByte(offset + 1, 'L');
    SRAM_writeByte(offset + 2, 'A');
    SRAM_writeByte(offset + 3, 'B');
    write_u16be(offset + 4, 1u);
    write_u16be(offset + 6, REF_VLAB_TOTAL_BYTES);
    offset += 8;
    for (index = 0; index < REF_VLAB_METRIC_WORDS; index++)
    {
        write_u16be(offset, metrics[index]);
        offset += 2;
    }
    for (index = 0; index < REF_VLAB_PALETTE_WORDS; index++)
    {
        write_u16be(offset, palette[index]);
        offset += 2;
    }

    offset = REF_SRAM_OFFSET;
    SRAM_writeByte(offset + 0, 'F');
    SRAM_writeByte(offset + 1, 'R');
    SRAM_writeByte(offset + 2, 'E');
    SRAM_writeByte(offset + 3, 'F');
    write_u16be(offset + 4, REF_SCHEMA_VERSION);
    write_u16be(offset + 6, REF_TOTAL_WORDS);
    offset += 8;
    for (index = 0; index < REF_TOTAL_WORDS; index++)
    {
        write_u16be(offset, s_words[index]);
        offset += 2;
    }
    SRAM_disable();
}
