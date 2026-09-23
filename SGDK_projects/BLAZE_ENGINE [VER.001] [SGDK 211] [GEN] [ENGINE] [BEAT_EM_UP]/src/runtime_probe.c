#include "runtime_probe.h"

#include <sprite_eng.h>

extern u32 frames;
extern u8 room;

static u16 s_words[BLAZE_PROBE_METRIC_WORDS];
static u16 s_palette[BLAZE_PROBE_PALETTE_WORDS];
static u32 s_totalFrames;
static u16 s_warmup;
static u16 s_previousCpu;
static u16 s_previousRoom;
static u16 s_lastExportFrame;

static u8 s_scanlinePressure[224];

static void write_u16_be(u32 offset, u16 value)
{
    SRAM_writeByte(offset, (u8)(value >> 8));
    SRAM_writeByte(offset + 1, (u8)value);
}

static void write_word(u32 *offset, u16 value)
{
    write_u16_be(*offset, value);
    *offset += 2;
}

static void note_peak_frame(u16 wordIndex)
{
    s_words[wordIndex] = (u16)(s_totalFrames >> 16);
    s_words[wordIndex + 1] = (u16)s_totalFrames;
}

static u16 measure_scanline_peak(void)
{
    Sprite *sprite = firstSprite;
    u16 peak = 0;
    u16 line;

    for (line = 0; line < 224; line++) s_scanlinePressure[line] = 0;

    while (sprite)
    {
        if (sprite->frame && sprite->visibility != HIDDEN)
        {
            u16 index;
            u16 count = sprite->frame->numSprite & 0x7F;

            for (index = 0; index < count; index++)
            {
                const FrameVDPSprite *part = &sprite->frame->frameVDPSprites[index];
                s16 start = (sprite->y - 0x80) + part->offsetY;
                s16 end = start + (s16)(((part->size & 0x3) + 1) << 3);

                if (end <= 0 || start >= 224) continue;
                if (start < 0) start = 0;
                if (end > 224) end = 224;

                for (line = (u16)start; line < (u16)end; line++)
                {
                    if (s_scanlinePressure[line] < 0xFF) s_scanlinePressure[line]++;
                    if (s_scanlinePressure[line] > peak) peak = s_scanlinePressure[line];
                }
            }
        }
        sprite = sprite->next;
    }

    return peak;
}

static void reset_scene_metrics(u16 sceneId)
{
    u16 i;
    for (i = 0; i < BLAZE_PROBE_METRIC_WORDS; i++) s_words[i] = 0;
    s_words[0] = sceneId;
    s_words[23] = SYS_isPAL() ? 50 : 60;
    s_words[BLAZE_PROBE_RANGE_WORD_OFFSET] = 0;
    s_warmup = BLAZE_PROBE_WARMUP_FRAMES;
    s_previousCpu = SYS_getCPULoad();
}

static void fill_vdp_words(void)
{
    s_words[0] = room;
    s_words[1] = (u16)(s_totalFrames >> 16);
    s_words[2] = (u16)s_totalFrames;
    s_words[3] = VDP_getScreenWidth();
    s_words[4] = VDP_getScreenHeight();
    s_words[5] = VDP_getPlaneWidth();
    s_words[6] = VDP_getPlaneHeight();
    s_words[7] = VDP_getHorizontalScrollingMode();
    s_words[8] = VDP_getVerticalScrollingMode();
    s_words[9] = VDP_getBGAAddress();
    s_words[10] = VDP_getBGBAddress();
    s_words[11] = VDP_getWindowAddress();
    s_words[12] = VDP_getSpriteListAddress();
    s_words[13] = VDP_getHScrollTableAddress();
    s_words[14] = VDP_getBackgroundColor();
    s_words[15] = (u16)s_totalFrames;
    s_words[23] = SYS_isPAL() ? 50 : 60;
}

static void export_vlab(void)
{
    u32 offset = BLAZE_PROBE_SRAM_OFFSET;
    u16 i;

    fill_vdp_words();
    PAL_getColors(0, s_palette, BLAZE_PROBE_PALETTE_WORDS);

    SRAM_enable();
    SRAM_writeByte(offset++, 'V');
    SRAM_writeByte(offset++, 'L');
    SRAM_writeByte(offset++, 'A');
    SRAM_writeByte(offset++, 'B');
    write_u16_be(offset, 1); offset += 2;
    write_u16_be(offset, 8 + ((BLAZE_PROBE_METRIC_WORDS + BLAZE_PROBE_PALETTE_WORDS) * 2)); offset += 2;

    for (i = 0; i < BLAZE_PROBE_METRIC_WORDS; i++) write_word(&offset, s_words[i]);
    for (i = 0; i < BLAZE_PROBE_PALETTE_WORDS; i++) write_word(&offset, s_palette[i]);
    SRAM_disable();
}

void BLAZE_RuntimeProbeInit(void)
{
    s_totalFrames = 0;
    s_lastExportFrame = 0;
    s_previousRoom = room;
    reset_scene_metrics(room);
}

void BLAZE_RuntimeProbeRecordTileRange(u16 startTile, u16 tileCount)
{
    u16 rawCount = s_words[BLAZE_PROBE_RANGE_WORD_OFFSET];
    u16 count = rawCount & 0x7FFF;

    if (count < BLAZE_PROBE_RANGE_CAPACITY)
    {
        u16 wordIndex = (u16)(BLAZE_PROBE_RANGE_WORD_OFFSET + 1 + (count * 2));
        s_words[wordIndex] = startTile;
        s_words[wordIndex + 1] = tileCount;
        s_words[BLAZE_PROBE_RANGE_WORD_OFFSET] = count + 1;
    }
    else
    {
        s_words[BLAZE_PROBE_RANGE_WORD_OFFSET] = (u16)(BLAZE_PROBE_RANGE_CAPACITY | 0x8000);
    }
}

u16 BLAZE_VDP_loadTileSet(const TileSet *tileset, u16 index, TransferMethod tm)
{
    if (tileset) BLAZE_RuntimeProbeRecordTileRange(index, tileset->numTile);
    return VDP_loadTileSet(tileset, index, tm);
}

void BLAZE_RuntimeProbeTick(void)
{
    u16 cpuLoad = SYS_getCPULoad();
    u16 activeSprites;
    u16 scanlinePeak;
    u16 jitter = (cpuLoad >= s_previousCpu) ? (cpuLoad - s_previousCpu) : (s_previousCpu - cpuLoad);

    s_totalFrames++;
    if (room != s_previousRoom)
    {
        s_previousRoom = room;
        reset_scene_metrics(room);
    }
    s_words[0] = room;
    s_words[15] = (u16)s_totalFrames;

    if (s_warmup)
    {
        s_warmup--;
        s_previousCpu = cpuLoad;
        return;
    }

    activeSprites = SPR_getNumActiveSprite();
    scanlinePeak = measure_scanline_peak();
    s_words[16]++;
    if (cpuLoad > 100) s_words[17]++;
    if (cpuLoad > s_words[18]) { s_words[18] = cpuLoad; note_peak_frame(26); }
    if (jitter > s_words[19]) s_words[19] = jitter;
    if (scanlinePeak > s_words[20]) { s_words[20] = scanlinePeak; note_peak_frame(24); }
    s_words[21] = activeSprites;
    if (activeSprites > s_words[22]) { s_words[22] = activeSprites; note_peak_frame(28); }
    s_previousCpu = cpuLoad;

    if ((s_totalFrames - s_lastExportFrame) >= BLAZE_PROBE_EXPORT_PERIOD)
    {
        export_vlab();
        s_lastExportFrame = s_totalFrames;
    }
}
