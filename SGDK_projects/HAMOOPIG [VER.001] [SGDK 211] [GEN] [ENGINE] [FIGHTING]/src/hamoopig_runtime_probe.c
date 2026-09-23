#include <genesis.h>
#include <sprite_eng.h>
#include "combat_event.h"
#include "globals.h"
#include "scene.h"
#include "hamoopig_runtime_probe.h"

#define HPRB_OFFSET 0x500u
#define HPRB_WORDS 31u
#define HPRB_SCHEMA 7u
#define HPRB_BYTES (8u + (HPRB_WORDS * 2u))
#define HSEM_OFFSET 0x580u
#define HSEM_WORDS 23u
#define HSEM_SCHEMA 1u
#define HSEM_BYTES (8u + (HSEM_WORDS * 2u))
#define HDBG_OFFSET 0x600u
#define HDBG_WORDS 24u
#define HDBG_SCHEMA 2u
#define HDBG_BYTES (8u + (HDBG_WORDS * 2u))
#define HCAD_OFFSET 0x640u
#define HCAD_WORDS 16u
#define HCAD_SCHEMA 1u
#define HCAD_BYTES (8u + (HCAD_WORDS * 2u))
#define HANC_OFFSET 0x1900u
#define HANC_WORDS 8u
#define HANC_SCHEMA 1u
#define HANC_BYTES (8u + (HANC_WORDS * 2u))
#define HAPE_OFFSET 0x1920u
#define HAPE_WORDS 26u
#define HAPE_SCHEMA 1u
#define HAPE_BYTES (8u + (HAPE_WORDS * 2u))
#define HSTR_OFFSET 0x700u
#define HSTR_SCHEMA 1u
#define HSTR_RECORD_WORDS 16u
#define HSTR_CAPACITY 128u
#define HSTR_BYTES (8u + 8u + (HSTR_CAPACITY * (2u + (HSTR_RECORD_WORDS * 2u))))
#define VLAB_OFFSET 0x200u
#define VLAB_SCHEMA 1u
#define VLAB_RANGE_CAPACITY 4u
#define VLAB_RANGE_WORDS (1u + (VLAB_RANGE_CAPACITY * 2u))
#define VLAB_EXTRA_WORDS 3u
#define VLAB_METRIC_WORDS (43u + VLAB_RANGE_WORDS + VLAB_EXTRA_WORDS)
#define VLAB_PALETTE_WORDS 64u
#define VLAB_BYTES (8u + ((VLAB_METRIC_WORDS + VLAB_PALETTE_WORDS) * 2u))
static u32 probeFrame;
static u32 probePeakDmaFrame, probePeakScanlineFrame;
static u16 probeMaxDma, probeMaxActive, probeMaxVdp, probeMaxScanline, probeSamples;
static u16 probeMaxPreSpriteDma, probeMaxSpriteDmaDelta;
static u16 probeMaxStageDma[5];
static u16 probeCurrentPreSpriteDma, probeCurrentSpriteDmaDelta;
static u16 probePeakPreAtMaxDma, probePeakSpriteDeltaAtMaxDma;
static u16 probeCombatTotalEvents, probeCombatTotalHits;
static u16 probeCombatTotalGuards, probeCombatTotalThrows;
static u16 probeCombatTotalProjectiles, probeCombatTotalDouble;
static u16 probeCombatTotalKo, probeCombatLastTickEvents, probeCombatLastTickKo;
static u16 probeScreenHeight;
static u16 probeOverBudget;
static u16 vlabPalette[VLAB_PALETTE_WORDS];
static u16 probeMaxCpuLoad, probeMaxCpuJitter;
static u32 probePeakCpuLoadFrame, probePeakActiveFrame;
static u16 probeMaxInitCpuLoad;
static u32 probePeakInitCpuLoadFrame;
static u32 probeFightWarmupUntilFrame;
static u16 probePreviousCpuLoad;
static u8 probeDiagnosticCooldown;
static bool probeHasPreviousCpuLoad;
typedef struct
{
    u16 start;
    u16 count;
} ProbeVramRange;
static ProbeVramRange probeVramRanges[VLAB_RANGE_CAPACITY];
static u16 probeVramRangeCount;
static bool probeVramRangeOverflow;
/* Aggregate combat-state telemetry lives in its own block so the established
   HPRB schema remains byte-compatible with existing P10 bundles. */
static u16 semSamples, semMinDistance, semMaxDistance;
static u16 semGuardFrames[2], semAttackFrames[2];
static u16 semFireballFrames[2], semThrowFrames[2];
static bool debugTerminalCaptured;
/* HCAD is a deliberately small cadence ledger. It answers a question the
   VDP/CPU peaks cannot answer: how many logical updates reached each video
   presentation, including frozen/zero-tick frames and PAL double-ticks. */
static u16 cadenceVideoFrames;
static u16 cadenceLogicTicks;
static u16 cadenceZeroTickFrames;
static u16 cadenceOneTickFrames;
static u16 cadenceTwoTickFrames;
static u8 cadenceMaxTicksPerFrame;
static u16 cadencePresentationCommits;
static u16 cadencePresentationWithoutLogic;
static u16 cadenceFightVideoFrames;
static u16 cadenceFightLogicTicks;
static u16 cadenceFightPresentationCommits;
static u16 cadenceFightZeroTickFrames;
static u8 cadenceLastLogicTicks;
static u8 cadenceLastScene;
#ifdef HAMOOPIG_CAPTURE_MARKER
static u16 captureMarkerId;
static u8 captureMarkerHold;
static u8 captureMarkerPulse;
static bool captureMarkerEventLatched;
static bool captureMarkerPreviousFireball;
#define CAPTURE_MARKER_PERIOD 120u
#define CAPTURE_MARKER_HOLD 6u
#define CAPTURE_MARKER_PSG_CHANNEL 3u
#define CAPTURE_MARKER_PSG_FREQUENCY 3500u
#define CAPTURE_MARKER_X 18u
#define CAPTURE_MARKER_Y 14u
#endif
/* Special-only state trace. It stays in RAM during play and is exported at
   the normal 30-frame diagnostic cadence, avoiding a full SRAM rewrite on
   every frame while still preserving the causal window in the final save. */
static u16 stateTrace[HSTR_CAPACITY][HSTR_RECORD_WORDS];
static u16 stateTraceCount;
static u16 stateTraceWriteIndex;

static void satInc(u16 *value, u16 amount)
{
    if ((u32)(*value) + amount > 0xFFFFu) *value = 0xFFFFu;
    else *value = (u16)(*value + amount);
}

static void writeBE16(u32 offset, u16 value)
{
    SRAM_writeByte(offset, (u8)(value >> 8));
    SRAM_writeByte(offset + 1u, (u8)value);
}

void HAMOOPIG_probeVramRange(u16 start, u16 count)
{
    u16 index;
    u32 end;
    if(count == 0u) return;
    end = (u32)start + count;
    for(index = 0u; index < probeVramRangeCount; index++)
    {
        u32 rangeStart = probeVramRanges[index].start;
        u32 rangeEnd = rangeStart + probeVramRanges[index].count;
        if(end < rangeStart || (u32)start > rangeEnd) continue;
        if((u32)start < rangeStart) probeVramRanges[index].start = start;
        if(end > rangeEnd) probeVramRanges[index].count = (u16)(end - probeVramRanges[index].start);
        return;
    }
    if(probeVramRangeCount >= VLAB_RANGE_CAPACITY)
    {
        probeVramRangeOverflow = TRUE;
        return;
    }
    probeVramRanges[probeVramRangeCount].start = start;
    probeVramRanges[probeVramRangeCount].count = count;
    probeVramRangeCount++;
}

void HAMOOPIG_probeVramReset(void)
{
    u16 index;
    probeVramRangeCount = 0u;
    probeVramRangeOverflow = FALSE;
    for(index = 0u; index < VLAB_RANGE_CAPACITY; index++)
    {
        probeVramRanges[index].start = 0u;
        probeVramRanges[index].count = 0u;
    }
    /* SPR_init()/SPR_initEx() owns the top VRAM region even before the first
       sprite frame uploads; export that reservation as residency. */
    HAMOOPIG_probeVramRange(TILE_SPRITE_INDEX, spriteVramSize);
}

static u16 scanlinePeak(void)
{
    u8 lines[224];
    Sprite *sprite = firstSprite;
    u16 line, peak = 0;
    for (line = 0; line < 224u; line++) lines[line] = 0;
    while (sprite)
    {
        if (sprite->frame && sprite->visibility != HIDDEN)
        {
            u16 index, count = (u16)(sprite->frame->numSprite & 0x7F);
            for (index = 0; index < count; index++)
            {
                const FrameVDPSprite *part = &sprite->frame->frameVDPSprites[index];
                s16 start = (s16)(sprite->y - 0x80) + (s16)part->offsetY;
                s16 end = start + (s16)(((part->size & 0x03u) + 1u) << 3);
                if (end <= 0 || start >= 224) continue;
                if (start < 0) start = 0;
                if (end > 224) end = 224;
                for (line = (u16)start; line < (u16)end; line++)
                {
                    if (lines[line] < 0xFFu) lines[line]++;
                    if (lines[line] > peak) peak = lines[line];
                }
            }
        }
        sprite = sprite->next;
    }
    return peak;
}

static void exportProbe(u8 scene)
{
    u32 offset = HPRB_OFFSET;
    SRAM_enable();
    SRAM_writeByte(offset + 0u, 'H'); SRAM_writeByte(offset + 1u, 'P');
    SRAM_writeByte(offset + 2u, 'R'); SRAM_writeByte(offset + 3u, 'B');
    writeBE16(offset + 4u, HPRB_SCHEMA); writeBE16(offset + 6u, HPRB_BYTES);
    offset += 8u;
    writeBE16(offset, (u16)(probeFrame >> 16)); offset += 2u;
    writeBE16(offset, (u16)probeFrame); offset += 2u;
    writeBE16(offset, (u16)(probePeakDmaFrame >> 16)); offset += 2u;
    writeBE16(offset, (u16)probePeakDmaFrame); offset += 2u;
    writeBE16(offset, (u16)(probePeakScanlineFrame >> 16)); offset += 2u;
    writeBE16(offset, (u16)probePeakScanlineFrame); offset += 2u;
    writeBE16(offset, probeMaxDma); offset += 2u;
    writeBE16(offset, probeMaxActive); offset += 2u;
    writeBE16(offset, probeMaxVdp); offset += 2u;
    writeBE16(offset, probeMaxScanline); offset += 2u;
    writeBE16(offset, probeSamples); offset += 2u;
    writeBE16(offset, (u16)(scene | (SYS_isPAL() ? 0x8000u : 0u)));
    offset += 2u;
    writeBE16(offset, probeMaxPreSpriteDma); offset += 2u;
    writeBE16(offset, probeMaxSpriteDmaDelta); offset += 2u;
    writeBE16(offset, probeMaxStageDma[0]); offset += 2u;
    writeBE16(offset, probeMaxStageDma[1]); offset += 2u;
    writeBE16(offset, probeMaxStageDma[2]); offset += 2u;
    writeBE16(offset, probeMaxStageDma[3]); offset += 2u;
    writeBE16(offset, probeMaxStageDma[4]); offset += 2u;
    writeBE16(offset, probePeakPreAtMaxDma); offset += 2u;
    writeBE16(offset, probePeakSpriteDeltaAtMaxDma);
    offset += 2u;
    writeBE16(offset, probeCombatTotalEvents); offset += 2u;
    writeBE16(offset, probeCombatTotalHits); offset += 2u;
    writeBE16(offset, probeCombatTotalGuards); offset += 2u;
    writeBE16(offset, probeCombatTotalThrows); offset += 2u;
    writeBE16(offset, probeCombatTotalProjectiles); offset += 2u;
    writeBE16(offset, probeCombatTotalDouble); offset += 2u;
    writeBE16(offset, probeCombatTotalKo); offset += 2u;
    writeBE16(offset, probeCombatLastTickEvents); offset += 2u;
    writeBE16(offset, probeCombatLastTickKo);
    offset += 2u;
    writeBE16(offset, probeScreenHeight);
    SRAM_disable();
}

static void exportSemanticProbe(void)
{
    u32 offset = HSEM_OFFSET;
    SRAM_enable();
    SRAM_writeByte(offset + 0u, 'H'); SRAM_writeByte(offset + 1u, 'S');
    SRAM_writeByte(offset + 2u, 'E'); SRAM_writeByte(offset + 3u, 'M');
    writeBE16(offset + 4u, HSEM_SCHEMA); writeBE16(offset + 6u, HSEM_BYTES);
    offset += 8u;
    writeBE16(offset, (u16)(probeFrame >> 16)); offset += 2u;
    writeBE16(offset, (u16)probeFrame); offset += 2u;
    writeBE16(offset, semSamples); offset += 2u;
    writeBE16(offset, semMinDistance); offset += 2u;
    writeBE16(offset, semMaxDistance); offset += 2u;
    writeBE16(offset, semGuardFrames[0]); offset += 2u;
    writeBE16(offset, semGuardFrames[1]); offset += 2u;
    writeBE16(offset, semAttackFrames[0]); offset += 2u;
    writeBE16(offset, semAttackFrames[1]); offset += 2u;
    writeBE16(offset, semFireballFrames[0]); offset += 2u;
    writeBE16(offset, semFireballFrames[1]); offset += 2u;
    writeBE16(offset, semThrowFrames[0]); offset += 2u;
    writeBE16(offset, semThrowFrames[1]); offset += 2u;
    writeBE16(offset, (u16)P[1].x); offset += 2u;
    writeBE16(offset, (u16)P[2].x); offset += 2u;
    writeBE16(offset, P[1].state); offset += 2u;
    writeBE16(offset, P[2].state); offset += 2u;
    writeBE16(offset, P[1].guardFlag); offset += 2u;
    writeBE16(offset, P[2].guardFlag); offset += 2u;
    writeBE16(offset, P[1].attackButton); offset += 2u;
    writeBE16(offset, P[2].attackButton); offset += 2u;
    writeBE16(offset, (u16)(u8)P[1].energiaSP); offset += 2u;
    writeBE16(offset, (u16)(u8)P[2].energiaSP);
    SRAM_disable();
}

/* Debug-only terminal snapshot. It is intentionally outside HPRB/HSEM/VLAB:
   those blocks are consumed by existing decoders and their layouts are closed.
   HDBG answers one narrow question during time-over diagnosis: whether the
   visible result agrees with the live clock, health and FSM state. */
static void exportDebugState(bool forceLiveFrame)
{
    u32 offset = HDBG_OFFSET;
    bool terminal = ((P[1].state >= 611u && P[1].state <= 615u) ||
                     (P[2].state >= 611u && P[2].state <= 615u) ||
                     (gClockLTimer == 0 && gClockRTimer == 0));
    if (debugTerminalCaptured && !forceLiveFrame) return;
    SRAM_enable();
    SRAM_writeByte(offset + 0u, 'H'); SRAM_writeByte(offset + 1u, 'D');
    SRAM_writeByte(offset + 2u, 'B'); SRAM_writeByte(offset + 3u, 'G');
    writeBE16(offset + 4u, HDBG_SCHEMA); writeBE16(offset + 6u, HDBG_BYTES);
    offset += 8u;
    writeBE16(offset, gRoom); offset += 2u;
    writeBE16(offset, (u16)gClockLTimer); offset += 2u;
    writeBE16(offset, (u16)gClockRTimer); offset += 2u;
    writeBE16(offset, (u16)gClockTimer); offset += 2u;
    writeBE16(offset, (u16)(u8)P[1].energiaBase); offset += 2u;
    writeBE16(offset, (u16)(u8)P[2].energiaBase); offset += 2u;
    writeBE16(offset, P[1].state); offset += 2u;
    writeBE16(offset, P[2].state); offset += 2u;
    writeBE16(offset, gResultTimer); offset += 2u;
    writeBE16(offset, gPauseKoTimer); offset += 2u;
    writeBE16(offset, (u16)gFrames); offset += 2u;
    writeBE16(offset, (u16)(gFrames >> 16));
    offset += 2u;
    writeBE16(offset, P[1].animFrame); offset += 2u;
    writeBE16(offset, P[1].animFrameTotal); offset += 2u;
    writeBE16(offset, P[1].frameTimeAtual); offset += 2u;
    writeBE16(offset, P[1].frameTimeTotal); offset += 2u;
    writeBE16(offset, P[1].fball.active ? 1u : 0u); offset += 2u;
    writeBE16(offset, (u16)P[1].fball.x); offset += 2u;
    writeBE16(offset, (u16)P[1].fball.y); offset += 2u;
    writeBE16(offset, P[1].attackButton); offset += 2u;
    writeBE16(offset, P[1].key_JOY_DOWN_status); offset += 2u;
    writeBE16(offset, P[1].key_JOY_RIGHT_status); offset += 2u;
    writeBE16(offset, P[1].key_JOY_X_status); offset += 2u;
    writeBE16(offset, cadenceVideoFrames);
    SRAM_disable();
    if (terminal && !forceLiveFrame) debugTerminalCaptured = TRUE;
}

static void exportCadenceProbe(void)
{
    u32 offset = HCAD_OFFSET;
    SRAM_enable();
    SRAM_writeByte(offset + 0u, 'H'); SRAM_writeByte(offset + 1u, 'C');
    SRAM_writeByte(offset + 2u, 'A'); SRAM_writeByte(offset + 3u, 'D');
    writeBE16(offset + 4u, HCAD_SCHEMA); writeBE16(offset + 6u, HCAD_BYTES);
    offset += 8u;
    writeBE16(offset, cadenceVideoFrames); offset += 2u;
    writeBE16(offset, cadenceLogicTicks); offset += 2u;
    writeBE16(offset, cadenceZeroTickFrames); offset += 2u;
    writeBE16(offset, cadenceOneTickFrames); offset += 2u;
    writeBE16(offset, cadenceTwoTickFrames); offset += 2u;
    writeBE16(offset, cadenceMaxTicksPerFrame); offset += 2u;
    writeBE16(offset, cadencePresentationCommits); offset += 2u;
    writeBE16(offset, cadencePresentationWithoutLogic); offset += 2u;
    writeBE16(offset, cadenceFightVideoFrames); offset += 2u;
    writeBE16(offset, cadenceFightLogicTicks); offset += 2u;
    writeBE16(offset, cadenceFightPresentationCommits); offset += 2u;
    writeBE16(offset, cadenceFightZeroTickFrames); offset += 2u;
    writeBE16(offset, cadenceLastLogicTicks); offset += 2u;
    writeBE16(offset, cadenceLastScene); offset += 2u;
    writeBE16(offset, gRegionIsPal ? 50u : 60u); offset += 2u;
    writeBE16(offset, (u16)gTimingProfile);
    SRAM_disable();
}

static void recordStateTrace(void)
{
    u16 *record;
    u16 inputBits = (u16)(
        (P[1].key_JOY_DOWN_status ? 0x0001u : 0u) |
        (P[1].key_JOY_RIGHT_status ? 0x0002u : 0u) |
        (P[1].key_JOY_X_status ? 0x0004u : 0u));
    record = stateTrace[stateTraceWriteIndex];
    record[0] = cadenceVideoFrames;
    record[1] = (u16)probeFrame;
    record[2] = (u16)gFrames;
    record[3] = (u16)gRoom;
    record[4] = cadenceLastLogicTicks;
    record[5] = P[1].state;
    record[6] = P[1].animFrame;
    record[7] = P[1].animFrameTotal;
    record[8] = P[1].frameTimeAtual;
    record[9] = P[1].frameTimeTotal;
    record[10] = P[1].fball.active ? 1u : 0u;
    record[11] = (u16)P[1].fball.x;
    record[12] = (u16)P[1].fball.y;
    record[13] = inputBits;
    record[14] = P[1].attackButton;
    record[15] = P[1].hitPause;
    stateTraceWriteIndex = (u16)((stateTraceWriteIndex + 1u) % HSTR_CAPACITY);
    if (stateTraceCount < HSTR_CAPACITY) stateTraceCount++;
}

static void exportStateTrace(void)
{
    u32 offset = HSTR_OFFSET;
    u16 i, recordIndex;
    SRAM_enable();
    SRAM_writeByte(offset + 0u, 'H'); SRAM_writeByte(offset + 1u, 'S');
    SRAM_writeByte(offset + 2u, 'T'); SRAM_writeByte(offset + 3u, 'R');
    writeBE16(offset + 4u, HSTR_SCHEMA); writeBE16(offset + 6u, HSTR_BYTES);
    offset += 8u;
    writeBE16(offset, stateTraceCount); offset += 2u;
    writeBE16(offset, stateTraceWriteIndex); offset += 2u;
    writeBE16(offset, HSTR_RECORD_WORDS); offset += 2u;
    writeBE16(offset, HSTR_CAPACITY); offset += 2u;
    for (i = 0u; i < HSTR_CAPACITY; i++)
    {
        if (i < stateTraceCount)
        {
            recordIndex = (u16)((stateTraceWriteIndex + HSTR_CAPACITY - stateTraceCount + i) % HSTR_CAPACITY);
            SRAM_writeByte(offset + 0u, (u8)(recordIndex >> 8));
            SRAM_writeByte(offset + 1u, (u8)recordIndex);
            offset += 2u;
            /* The record index is followed by the fixed-width state record. */
            for (u16 word = 0u; word < HSTR_RECORD_WORDS; word++)
            {
                writeBE16(offset, stateTrace[recordIndex][word]);
                offset += 2u;
            }
        }
        else
        {
            writeBE16(offset, 0xFFFFu); offset += 2u;
            for (u16 word = 0u; word < HSTR_RECORD_WORDS; word++)
            {
                writeBE16(offset, 0u);
                offset += 2u;
            }
        }
    }
    SRAM_disable();
}

/* VLAB is the canonical visual snapshot consumed by the evidence sealer.
   HPRB/HSEM remain separate diagnostic blocks at 0x500/0x580 so existing
   decoders and P10 bundles keep their byte layout. */
static void exportVisualProbe(u8 scene)
{
    u32 offset = VLAB_OFFSET;
    u32 frame = probeFrame;
    u16 i;

    PAL_getColors(0, vlabPalette, VLAB_PALETTE_WORDS);
    SRAM_enable();
    SRAM_writeByte(offset + 0u, 'V'); SRAM_writeByte(offset + 1u, 'L');
    SRAM_writeByte(offset + 2u, 'A'); SRAM_writeByte(offset + 3u, 'B');
    writeBE16(offset + 4u, VLAB_SCHEMA);
    writeBE16(offset + 6u, VLAB_BYTES);
    offset += 8u;

    /* words[0..23] follow seal_fresh_evidence_bundle.py exactly. */
    writeBE16(offset, scene); offset += 2u;
    writeBE16(offset, (u16)(frame >> 16)); offset += 2u;
    writeBE16(offset, (u16)frame); offset += 2u;
    writeBE16(offset, VDP_getScreenWidth()); offset += 2u;
    writeBE16(offset, VDP_getScreenHeight()); offset += 2u;
    writeBE16(offset, VDP_getPlaneWidth()); offset += 2u;
    writeBE16(offset, VDP_getPlaneHeight()); offset += 2u;
    writeBE16(offset, VDP_getHorizontalScrollingMode()); offset += 2u;
    writeBE16(offset, VDP_getVerticalScrollingMode()); offset += 2u;
    writeBE16(offset, VDP_getBGAAddress()); offset += 2u;
    writeBE16(offset, VDP_getBGBAddress()); offset += 2u;
    writeBE16(offset, VDP_getWindowAddress()); offset += 2u;
    writeBE16(offset, VDP_getSpriteListAddress()); offset += 2u;
    writeBE16(offset, VDP_getHScrollTableAddress()); offset += 2u;
    writeBE16(offset, VDP_getBackgroundColor()); offset += 2u;
    writeBE16(offset, (u16)frame); offset += 2u;
    writeBE16(offset, probeSamples); offset += 2u;
    writeBE16(offset, probeOverBudget); offset += 2u;
    writeBE16(offset, probeMaxCpuLoad); offset += 2u;
    writeBE16(offset, probeMaxCpuJitter); offset += 2u;
    writeBE16(offset, probeMaxScanline); offset += 2u;
    writeBE16(offset, SPR_getNumActiveSprite()); offset += 2u;
    writeBE16(offset, probeMaxActive); offset += 2u;
    writeBE16(offset, gRegionIsPal ? 50u : 60u); offset += 2u;

    /* words[24..42] preserve the extended VLAB positions. */
    writeBE16(offset, 0u); offset += 2u; /* sprite allocations spawned */
    writeBE16(offset, 0u); offset += 2u; /* sprite allocation failures */
    writeBE16(offset, (u16)(probePeakScanlineFrame >> 16)); offset += 2u;
    writeBE16(offset, (u16)probePeakScanlineFrame); offset += 2u;
    writeBE16(offset, (u16)(probePeakCpuLoadFrame >> 16)); offset += 2u;
    writeBE16(offset, (u16)probePeakCpuLoadFrame); offset += 2u;
    writeBE16(offset, (u16)(probePeakActiveFrame >> 16)); offset += 2u;
    writeBE16(offset, (u16)probePeakActiveFrame); offset += 2u;
    writeBE16(offset, probeMaxDma); offset += 2u;
    writeBE16(offset, 0u); offset += 2u;
    writeBE16(offset, probeMaxDma); offset += 2u;
    writeBE16(offset, (u16)(probePeakDmaFrame >> 16)); offset += 2u;
    writeBE16(offset, (u16)probePeakDmaFrame); offset += 2u;
    writeBE16(offset, 0u); offset += 2u;
    writeBE16(offset, 0u); offset += 2u;
    writeBE16(offset, 0u); offset += 2u;
    writeBE16(offset, 0u); offset += 2u;
    writeBE16(offset, 0u); offset += 2u;
    writeBE16(offset, 0u); offset += 2u;

    /* words[43..51] are scene-local VRAM ranges: count/overflow followed by
       four start/count pairs. The fixed capacity keeps SRAM deterministic. */
    writeBE16(offset, (u16)(probeVramRangeCount |
        (probeVramRangeOverflow ? 0x8000u : 0u))); offset += 2u;
    for(i = 0u; i < VLAB_RANGE_CAPACITY; i++)
    {
        if(i < probeVramRangeCount)
        {
            writeBE16(offset, probeVramRanges[i].start); offset += 2u;
            writeBE16(offset, probeVramRanges[i].count); offset += 2u;
        }
        else
        {
            writeBE16(offset, 0u); offset += 2u;
            writeBE16(offset, 0u); offset += 2u;
        }
    }

    /* words[52..54] retain the one-time fight-entry load separately from the
       steady gameplay claim.  The initialization frame performs stage,
       fighter and HUD allocation/upload together and is a load-time budget,
       not a sustained combat frame. */
    writeBE16(offset, probeMaxInitCpuLoad); offset += 2u;
    writeBE16(offset, (u16)(probePeakInitCpuLoadFrame >> 16)); offset += 2u;
    writeBE16(offset, (u16)probePeakInitCpuLoadFrame); offset += 2u;

    for(i = 0u; i < VLAB_PALETTE_WORDS; i++)
    {
        writeBE16(offset, vlabPalette[i]);
        offset += 2u;
    }
    probeDiagnosticCooldown = 9u;
    SRAM_disable();
}

static void sampleSemanticState(u8 scene)
{
    u8 player;
    /* Title/select fighters retain zeroed coordinates; exclude them so the
       diagnostic range describes only the active fight scene. */
    if (scene != SCENE_FIGHT) return;
    u16 distance = gDistancia;
    if (semSamples == 0u || distance < semMinDistance) semMinDistance = distance;
    if (semSamples == 0u || distance > semMaxDistance) semMaxDistance = distance;
    if (semSamples != 0xFFFFu) semSamples++;
    for (player = 0u; player < 2u; player++)
    {
        const struct PlayerDEF *p = &P[player + 1u];
        if ((p->state >= 107u && p->state <= 110u) ||
            (p->state >= 207u && p->state <= 210u))
            satInc(&semGuardFrames[player], 1u);
        if (p->stateMoveType == 1u)
            satInc(&semAttackFrames[player], 1u);
        if (p->fball.active)
            satInc(&semFireballFrames[player], 1u);
        if (p->state == 800u || p->state == 801u || p->state == 802u || p->state == 803u)
            satInc(&semThrowFrames[player], 1u);
    }
}

static void sampleFrameTiming(void)
{
    const u16 cpuLoad = SYS_getCPULoad();
    u16 jitter = 0u;
    if(probeHasPreviousCpuLoad)
    {
        const s32 delta = (s32) cpuLoad - (s32) probePreviousCpuLoad;
        jitter = (u16) ((delta < 0) ? -delta : delta);
    }
    probePreviousCpuLoad = cpuLoad;
    probeHasPreviousCpuLoad = TRUE;

    /* VLAB/HPRB/HSEM export writes a large SRAM snapshot every 30 frames.
       SYS_getCPULoad() is an 8-frame mean, so the following nine samples can
       still include diagnostic I/O rather than gameplay. Keep that probe
       overhead out of the gameplay claim while retaining the raw dump. */
    if(probeDiagnosticCooldown != 0u)
    {
        probeDiagnosticCooldown--;
        return;
    }

    /* SYS_getCPULoad() is an 8-frame rolling mean.  Marking only gFrames==1
       would let the entry cost leak into the sustained metric for several
       video frames, especially on a 50 Hz console.  The explicit marker is
       placed immediately after FUNCAO_INICIALIZACAO and keeps a 16-frame
       window, covering the initialization frame plus the measurement tail. */
    if(gRoom == SCENE_FIGHT && probeFrame <= probeFightWarmupUntilFrame)
    {
        if(cpuLoad > probeMaxInitCpuLoad)
        {
            probeMaxInitCpuLoad = cpuLoad;
            probePeakInitCpuLoadFrame = probeFrame;
        }
        return;
    }

    /* The sustained claim is specifically for the active fight.  Title and
       selection have different ownership and asset lifetimes, so keeping
       their CPU peaks in the combat aggregate would make the report answer a
       different question than the VDP/sprite metrics beside it. */
    if(gRoom != SCENE_FIGHT) return;

    if(cpuLoad > probeMaxCpuLoad)
    {
        probeMaxCpuLoad = cpuLoad;
        probePeakCpuLoadFrame = probeFrame;
    }
    if(jitter > probeMaxCpuJitter) probeMaxCpuJitter = jitter;
}

void HAMOOPIG_probeInit(void)
{
    probeFrame = 0; probePeakDmaFrame = 0; probePeakScanlineFrame = 0;
    probeMaxDma = 0; probeMaxActive = 0;
    probeMaxVdp = 0; probeMaxScanline = 0; probeSamples = 0;
    probeMaxPreSpriteDma = 0; probeMaxSpriteDmaDelta = 0;
    probeMaxStageDma[0] = 0; probeMaxStageDma[1] = 0; probeMaxStageDma[2] = 0;
    probeMaxStageDma[3] = 0; probeMaxStageDma[4] = 0;
    probeCurrentPreSpriteDma = 0; probeCurrentSpriteDmaDelta = 0;
    probePeakPreAtMaxDma = 0; probePeakSpriteDeltaAtMaxDma = 0;
    probeCombatTotalEvents = 0; probeCombatTotalHits = 0;
    probeCombatTotalGuards = 0; probeCombatTotalThrows = 0;
    probeCombatTotalProjectiles = 0; probeCombatTotalDouble = 0;
    probeCombatTotalKo = 0; probeCombatLastTickEvents = 0;
    probeCombatLastTickKo = 0;
    probeScreenHeight = 224;
    probeOverBudget = 0;
    probeMaxCpuLoad = 0; probeMaxCpuJitter = 0;
    probePeakCpuLoadFrame = 0; probePeakActiveFrame = 0;
    probeMaxInitCpuLoad = 0;
    probePeakInitCpuLoadFrame = 0;
    probePreviousCpuLoad = 0;
    probeDiagnosticCooldown = 0;
    probeHasPreviousCpuLoad = FALSE;
    HAMOOPIG_probeVramReset();
    semSamples = 0; semMinDistance = 0; semMaxDistance = 0;
    semGuardFrames[0] = 0; semGuardFrames[1] = 0;
    semAttackFrames[0] = 0; semAttackFrames[1] = 0;
    semFireballFrames[0] = 0; semFireballFrames[1] = 0;
    semThrowFrames[0] = 0; semThrowFrames[1] = 0;
    debugTerminalCaptured = FALSE;
    cadenceVideoFrames = 0u;
    cadenceLogicTicks = 0u;
    cadenceZeroTickFrames = 0u;
    cadenceOneTickFrames = 0u;
    cadenceTwoTickFrames = 0u;
    cadenceMaxTicksPerFrame = 0u;
    cadencePresentationCommits = 0u;
    cadencePresentationWithoutLogic = 0u;
    cadenceFightVideoFrames = 0u;
    cadenceFightLogicTicks = 0u;
    cadenceFightPresentationCommits = 0u;
    cadenceFightZeroTickFrames = 0u;
    cadenceLastLogicTicks = 0u;
    cadenceLastScene = 0u;
    stateTraceCount = 0u;
    stateTraceWriteIndex = 0u;
#ifdef HAMOOPIG_CAPTURE_MARKER
    captureMarkerEventLatched = FALSE;
    captureMarkerPreviousFireball = FALSE;
#endif
}

void HAMOOPIG_probeFightInit(void)
{
    /* Eight samples flush SYS_getCPULoad's rolling mean; the extra margin
       keeps the first post-upload sample out of the sustained claim. */
    probeFightWarmupUntilFrame = probeFrame + 16u;
    /* HDBG is a terminal snapshot, but terminal ownership is round-scoped.
       Keeping this latch from the first KO made the second round invisible to
       the same-match evidence route and left AFTER_MATCH/revenge unprovable. */
    debugTerminalCaptured = FALSE;
}

void HAMOOPIG_probeSpriteDma(u16 dmaBeforeSpriteUpdate)
{
    u16 dmaAfter = DMA_getQueueTransferSize();
    u16 delta = (dmaAfter >= dmaBeforeSpriteUpdate) ? (u16)(dmaAfter - dmaBeforeSpriteUpdate) : 0;
    probeCurrentPreSpriteDma = dmaBeforeSpriteUpdate;
    probeCurrentSpriteDmaDelta = delta;
    if (dmaBeforeSpriteUpdate > probeMaxPreSpriteDma) probeMaxPreSpriteDma = dmaBeforeSpriteUpdate;
    if (delta > probeMaxSpriteDmaDelta) probeMaxSpriteDmaDelta = delta;
}

void HAMOOPIG_probeStageDma(u8 stage, u16 dmaBeforeStage)
{
    u16 dmaAfter = DMA_getQueueTransferSize();
    u16 delta = (dmaAfter >= dmaBeforeStage) ? (u16)(dmaAfter - dmaBeforeStage) : 0;
    if (stage >= 1u && stage <= 5u && delta > probeMaxStageDma[stage - 1u])
        probeMaxStageDma[stage - 1u] = delta;
}

void HAMOOPIG_probeVideoFrame(u8 scene, u8 logicTicks)
{
    if (cadenceVideoFrames != 0xFFFFu) cadenceVideoFrames++;
    if ((u16)cadenceLogicTicks + logicTicks > 0xFFFFu)
        cadenceLogicTicks = 0xFFFFu;
    else
        cadenceLogicTicks = (u16)(cadenceLogicTicks + logicTicks);
    if (logicTicks == 0u)
    {
        if (cadenceZeroTickFrames != 0xFFFFu) cadenceZeroTickFrames++;
        if (cadencePresentationWithoutLogic != 0xFFFFu) cadencePresentationWithoutLogic++;
    }
    else if (logicTicks == 1u)
    {
        if (cadenceOneTickFrames != 0xFFFFu) cadenceOneTickFrames++;
    }
    else
    {
        if (cadenceTwoTickFrames != 0xFFFFu) cadenceTwoTickFrames++;
    }
    if (logicTicks > cadenceMaxTicksPerFrame) cadenceMaxTicksPerFrame = logicTicks;
    if (cadencePresentationCommits != 0xFFFFu) cadencePresentationCommits++;
    if (scene == SCENE_FIGHT)
    {
        if (cadenceFightVideoFrames != 0xFFFFu) cadenceFightVideoFrames++;
        if ((u16)cadenceFightLogicTicks + logicTicks > 0xFFFFu)
            cadenceFightLogicTicks = 0xFFFFu;
        else
            cadenceFightLogicTicks = (u16)(cadenceFightLogicTicks + logicTicks);
        if (cadenceFightPresentationCommits != 0xFFFFu) cadenceFightPresentationCommits++;
        if (logicTicks == 0u && cadenceFightZeroTickFrames != 0xFFFFu)
            cadenceFightZeroTickFrames++;
    }
    cadenceLastLogicTicks = logicTicks;
    cadenceLastScene = scene;
}

void HAMOOPIG_captureMarker(u8 scene)
{
#ifdef HAMOOPIG_CAPTURE_MARKER
    char marker[8];
    bool emit;
    bool gameplayEvent;
    u16 emittedMarkerId;

    if (scene != SCENE_FIGHT) return;

    /* The periodic marker proves media identity/synchronization only.  This
       second, reserved marker is emitted once at the first observed
       fball.active transition.  It is deliberately instrumentation: it does
       not change the FSM, projectile position, sprite ownership or audio
       mix.  Suppressing later periodic markers keeps the terminal HANC record
       bound to the gameplay event instead of silently replacing it. */
    gameplayEvent = P[1].fball.active && !captureMarkerPreviousFireball &&
        !captureMarkerEventLatched;
    captureMarkerPreviousFireball = P[1].fball.active;

    /* One presentation boundary owns both media signals.  The marker is
       deliberately diagnostic: it is not an authored HUD or gameplay art. */
    if (captureMarkerPulse != 0u)
    {
        PSG_setEnvelope(CAPTURE_MARKER_PSG_CHANNEL, PSG_ENVELOPE_MIN);
        captureMarkerPulse--;
    }
    if (captureMarkerHold != 0u)
    {
        captureMarkerHold--;
        if (captureMarkerHold == 0u)
            VDP_fillTileMapRect(BG_A, 0u, CAPTURE_MARKER_X, CAPTURE_MARKER_Y, 6u, 1u);
    }

    emit = gameplayEvent || (!captureMarkerEventLatched &&
        ((captureMarkerId == 0u) ||
         ((cadenceVideoFrames % CAPTURE_MARKER_PERIOD) == 0u)));
    if (!emit) return;
    captureMarkerId++;
    emittedMarkerId = gameplayEvent ? (u16)(0x8000u | captureMarkerId) : captureMarkerId;
    if (gameplayEvent) captureMarkerEventLatched = TRUE;
    captureMarkerHold = CAPTURE_MARKER_HOLD;
    captureMarkerPulse = 1u;

    sprintf(marker, "M%04X", emittedMarkerId);
    VDP_fillTileMapRect(BG_A, 0u, CAPTURE_MARKER_X, CAPTURE_MARKER_Y, 6u, 1u);
    /* VDP_drawTextEx adds TILE_FONT_INDEX internally.  Passing it again
       selects scene tiles instead of glyphs and makes the diagnostic marker
       invisible while the HANC/audio side still claims it was emitted. */
    VDP_drawTextEx(BG_A, marker,
        TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, 0),
        CAPTURE_MARKER_X, CAPTURE_MARKER_Y, CPU);
    PSG_setTone(CAPTURE_MARKER_PSG_CHANNEL, CAPTURE_MARKER_PSG_FREQUENCY);
    PSG_setEnvelope(CAPTURE_MARKER_PSG_CHANNEL, PSG_ENVELOPE_MAX);

    /* SRAM is a terminal runtime record, not a media timestamp.  The
       analyzer later binds this marker id to decoded video PTS and audio
       sample index, preserving the distinction explicitly. */
    SRAM_enable();
    SRAM_writeByte(HANC_OFFSET + 0u, 'H'); SRAM_writeByte(HANC_OFFSET + 1u, 'A');
    SRAM_writeByte(HANC_OFFSET + 2u, 'N'); SRAM_writeByte(HANC_OFFSET + 3u, 'C');
    writeBE16(HANC_OFFSET + 4u, HANC_SCHEMA);
    writeBE16(HANC_OFFSET + 6u, HANC_BYTES);
    writeBE16(HANC_OFFSET + 8u, emittedMarkerId);
    writeBE16(HANC_OFFSET + 10u, (u16)(cadenceVideoFrames >> 16));
    writeBE16(HANC_OFFSET + 12u, (u16)cadenceVideoFrames);
    writeBE16(HANC_OFFSET + 14u, gameplayEvent ? 0xFFFFu : CAPTURE_MARKER_PERIOD);
    writeBE16(HANC_OFFSET + 16u, CAPTURE_MARKER_HOLD);
    writeBE16(HANC_OFFSET + 18u, CAPTURE_MARKER_PSG_CHANNEL);
    writeBE16(HANC_OFFSET + 20u, CAPTURE_MARKER_PSG_FREQUENCY);
    writeBE16(HANC_OFFSET + 22u, scene);

    /* HAPE is the state-side companion of HANC.  It is written at the same
       presentation boundary and is deliberately separate from the legacy
       24-byte HANC block.  This records the game state that produced the
       marker without changing the FSM, sprite data or audio route. */
    SRAM_writeByte(HAPE_OFFSET + 0u, 'H'); SRAM_writeByte(HAPE_OFFSET + 1u, 'A');
    SRAM_writeByte(HAPE_OFFSET + 2u, 'P'); SRAM_writeByte(HAPE_OFFSET + 3u, 'E');
    writeBE16(HAPE_OFFSET + 4u, HAPE_SCHEMA);
    writeBE16(HAPE_OFFSET + 6u, HAPE_BYTES);
    writeBE16(HAPE_OFFSET + 8u, emittedMarkerId);
    writeBE16(HAPE_OFFSET + 10u, (u16)(cadenceVideoFrames >> 16));
    writeBE16(HAPE_OFFSET + 12u, (u16)cadenceVideoFrames);
    writeBE16(HAPE_OFFSET + 14u, (u16)(probeFrame >> 16));
    writeBE16(HAPE_OFFSET + 16u, (u16)probeFrame);
    writeBE16(HAPE_OFFSET + 18u, (u16)(gFrames >> 16));
    writeBE16(HAPE_OFFSET + 20u, (u16)gFrames);
    writeBE16(HAPE_OFFSET + 22u, scene);
    writeBE16(HAPE_OFFSET + 24u, cadenceLastLogicTicks);
    writeBE16(HAPE_OFFSET + 26u, gameplayEvent ? 1u : 0u);
    writeBE16(HAPE_OFFSET + 28u, P[1].state);
    writeBE16(HAPE_OFFSET + 30u, P[1].animFrame);
    writeBE16(HAPE_OFFSET + 32u, P[1].animFrameTotal);
    writeBE16(HAPE_OFFSET + 34u, P[1].frameTimeAtual);
    writeBE16(HAPE_OFFSET + 36u, P[1].frameTimeTotal);
    writeBE16(HAPE_OFFSET + 38u, P[1].fball.active ? 1u : 0u);
    writeBE16(HAPE_OFFSET + 40u, (u16)P[1].fball.x);
    writeBE16(HAPE_OFFSET + 42u, (u16)P[1].fball.y);
    writeBE16(HAPE_OFFSET + 44u,
        (u16)((P[1].key_JOY_DOWN_status ? 0x0001u : 0u) |
              (P[1].key_JOY_RIGHT_status ? 0x0002u : 0u) |
              (P[1].key_JOY_X_status ? 0x0004u : 0u)));
    writeBE16(HAPE_OFFSET + 46u, P[1].attackButton);
    writeBE16(HAPE_OFFSET + 48u, P[1].hitPause);
    writeBE16(HAPE_OFFSET + 50u, probeCurrentPreSpriteDma);
    writeBE16(HAPE_OFFSET + 52u, probeCurrentSpriteDmaDelta);
    writeBE16(HAPE_OFFSET + 54u, SPR_getNumActiveSprite());
    writeBE16(HAPE_OFFSET + 56u, SPR_getUsedVDPSprite());
    writeBE16(HAPE_OFFSET + 58u, scanlinePeak());
    SRAM_disable();
#else
    (void)scene;
#endif
}

void HAMOOPIG_probeCombatEvents(void)
{
    u8 index;
    u8 count = COMBAT_EVENTS_COUNT();
    u16 lastKo = 0;
    probeCombatLastTickEvents = count;
    for (index = 0; index < count; index++)
    {
        const CombatEvent *event = COMBAT_EVENTS_AT(index);
        if (!event) continue;
        satInc(&probeCombatTotalEvents, 1);
        if (event->kind == COMBAT_EVENT_GUARD)
        {
            satInc(&probeCombatTotalGuards, 1);
        }
        else if (event->kind == COMBAT_EVENT_THROW)
        {
            satInc(&probeCombatTotalThrows, 1);
            satInc(&probeCombatTotalHits, 1);
        }
        else if (event->kind == COMBAT_EVENT_HIT)
        {
            satInc(&probeCombatTotalHits, 1);
        }
        if (event->source == COMBAT_EVENT_SOURCE_PROJECTILE)
            satInc(&probeCombatTotalProjectiles, 1);
        else if (event->source == COMBAT_EVENT_SOURCE_DOUBLE)
            satInc(&probeCombatTotalDouble, 1);
        if (event->result == COMBAT_EVENT_RESULT_KO)
        {
            satInc(&probeCombatTotalKo, 1);
            lastKo++;
        }
    }
    probeCombatLastTickKo = lastKo;
}

void HAMOOPIG_probeTick(u8 scene)
{
    u16 dma = DMA_getQueueTransferSize();
    u16 active = SPR_getNumActiveSprite();
    u16 vdp = SPR_getUsedVDPSprite();
    u16 scanline = scanlinePeak();
    probeScreenHeight = gScreenH;
    probeFrame++;
    sampleFrameTiming();
    sampleSemanticState(scene);
    if (dma > probeMaxDma) {
        probeMaxDma = dma; probePeakDmaFrame = probeFrame;
        probePeakPreAtMaxDma = probeCurrentPreSpriteDma;
        probePeakSpriteDeltaAtMaxDma = probeCurrentSpriteDmaDelta;
    }
    if (active > probeMaxActive)
    {
        probeMaxActive = active;
        probePeakActiveFrame = probeFrame;
    }
    if (vdp > probeMaxVdp) probeMaxVdp = vdp;
    if (scanline > probeMaxScanline) { probeMaxScanline = scanline; probePeakScanlineFrame = probeFrame; }
    if (dma > (gRegionIsPal ? 8024u : 7782u) || vdp > 80u || scanline > 20u)
        satInc(&probeOverBudget, 1u);
    if (probeSamples != 0xFFFFu) probeSamples++;
    if ((probeFrame % 30u) == 0u)
    {
        exportProbe(scene);
        exportSemanticProbe();
        exportDebugState(FALSE);
        exportVisualProbe(scene);
        exportCadenceProbe();
        exportStateTrace();
    }
    /* The regular snapshot is intentionally sparse. During a special, write
       the same hash-bound debug block once per presented frame so a queried
       image sequence can be correlated with the live FSM/animation state.
       This is diagnostic instrumentation, not a performance claim; the
       special route records that this live trace was enabled. */
    if (scene == SCENE_FIGHT &&
        ((P[1].state >= 700u && P[1].state <= 790u) || P[1].fball.active))
    {
        recordStateTrace();
        exportDebugState(TRUE);
    }
}

u16 HAMOOPIG_probePeakDma(void) { return probeMaxDma; }
u16 HAMOOPIG_probePeakActiveSprites(void) { return probeMaxActive; }
u16 HAMOOPIG_probePeakScanlineSprites(void) { return probeMaxScanline; }
u16 HAMOOPIG_probePeakVdpSprites(void) { return probeMaxVdp; }
