#include <genesis.h>

#include "system/probe_stage.h"

static s16 s_cameraX;
static s16 s_hsSky;
static s16 s_hsMount;
static s16 s_hsHill;
static s16 s_hsTerrain;
static u16 s_kirbyState;
static s16 s_kirbyX;
static s16 s_kirbyY;
static u16 s_enemiesAlive;
static bool s_shEnabled;

/*
 * Raw diagnostic reads. The priority audit reports 0 sampled entries on BG_A
 * even though the terrain is drawn there, so instead of theorising about the
 * VDP read protocol these capture the actual words that come back from four
 * known addresses. BG_B row 0 col 0 is the control: it is known to read fine.
 */
static u16 s_rawBgaTerrain;   /* BG_A row 22 col 0 -- terrain, must be non-zero */
static u16 s_rawBgaRow0;      /* BG_A row 0  col 0 -- expected empty */
static u16 s_rawBgbRow0;      /* BG_B row 0  col 0 -- control, sky */
static u16 s_rawBgaSecond;    /* BG_A row 22 col 0, read a second time */

/* Scripted-playtest coverage, published by the scene. */
static u16 s_ptVisited;
static u16 s_ptStep;
static u16 s_ptFinished;

static u16 s_dmaPeakBytes;
static u16 s_dmaPeakCount;
static u16 s_prioViolA;
static u16 s_prioSampledA;
static u16 s_prioViolB;
static u16 s_prioSampledB;

void PROBE_STAGE_reset(void)
{
    s_cameraX = 0;
    s_hsSky = 0; s_hsMount = 0; s_hsHill = 0; s_hsTerrain = 0;
    s_kirbyState = 0u; s_kirbyX = 0; s_kirbyY = 0;
    s_enemiesAlive = 0u;
    s_shEnabled = FALSE;
    s_dmaPeakBytes = 0u;
    s_dmaPeakCount = 0u;
    s_prioViolA = 0u; s_prioSampledA = 0u;
    s_prioViolB = 0u; s_prioSampledB = 0u;
    s_ptVisited = 0u; s_ptStep = 0u; s_ptFinished = 0u;
}

void PROBE_STAGE_publishCamera(s16 cameraX) { s_cameraX = cameraX; }

void PROBE_STAGE_publishHScroll(s16 sky, s16 mount, s16 hill, s16 terrain)
{
    s_hsSky = sky; s_hsMount = mount; s_hsHill = hill; s_hsTerrain = terrain;
}

void PROBE_STAGE_publishActors(u16 kirbyState, s16 kirbyX, s16 kirbyY,
                               u16 enemiesAlive)
{
    s_kirbyState = kirbyState;
    s_kirbyX = kirbyX;
    s_kirbyY = kirbyY;
    s_enemiesAlive = enemiesAlive;
}

void PROBE_STAGE_publishShadowHighlight(bool enabled) { s_shEnabled = enabled; }

void PROBE_STAGE_publishPlaytest(u16 visited, u16 step, bool finished)
{
    s_ptVisited = visited;
    s_ptStep = step;
    s_ptFinished = finished ? 1u : 0u;
}

/*
 * Sampled priority-bit audit. doc/PALETTES.md gate P5 requires zero background
 * tiles at priority 0 while Shadow/Highlight is on.
 *
 * Interrupts are masked around the raw VDP port sequence. This is the direct
 * lesson from the CRAM corruption bug of 2026-07-30: an interrupt that writes
 * VDP_CTRL_PORT in the middle of someone else's port sequence redirects the
 * transfer. Our own H-int does exactly that, so it must not fire here.
 *
 * RESOLVED 2026-07-30. An earlier version of this comment claimed BG_A reads
 * "returned zero for an unexplained reason" and suspected a VDP read delay.
 * That was WRONG. The reads always worked -- the raw diagnostics below return
 * 0xA083 (tile 131, priority 1, palette 1) for BG_A row 22. The real cause was a
 * sampling stride of one row, which only reached rows 0..15 where BG_A is empty.
 * With stride 2 rows the audit reports 0 violations of 17 sampled entries and is
 * no longer vacuous. The wrong claim is kept visible here on purpose: it was
 * repeated in three documents before being caught.
 */
static u16 vdp_read_vram(u16 addr)
{
    *((vu32*) VDP_CTRL_PORT) = VDP_READ_VRAM_ADDR((u32) addr);
    return *((vu16*) VDP_DATA_PORT);
}

static void sample_priority_bits(void)
{
    const u16 planes[2] = { (u16) VDP_BG_A, (u16) VDP_BG_B };
    u16 p, i;

    s_prioViolA = 0u; s_prioSampledA = 0u;
    s_prioViolB = 0u; s_prioSampledB = 0u;

    SYS_disableInts();

    /* Diagnostics first, while interrupts are already masked.
     * BG_A row 22 = byte offset 22*64*2 = 2816. */
    s_rawBgaRow0    = vdp_read_vram((u16) (planes[0] + 0u));
    s_rawBgaTerrain = vdp_read_vram((u16) (planes[0] + 2816u));
    /* Same address again, to test whether a second read after programming the
     * address returns something different (i.e. a required-delay effect). */
    (void) vdp_read_vram((u16) (planes[0] + 2816u));
    s_rawBgaSecond  = *((vu16*) VDP_DATA_PORT);
    s_rawBgbRow0    = vdp_read_vram((u16) (planes[1] + 0u));

    for (p = 0u; p < 2u; p++)
    {
        for (i = 0u; i < 16u; i++)
        {
            /*
             * Stride 256 bytes = 128 entries = 2 nametable rows, so 16 samples
             * cover rows 0..30 of the 32-row plane.
             *
             * The first version used stride 128 (one row) and only reached rows
             * 0..15. On BG_A the terrain lives at rows 22..29, so every sample
             * hit an empty entry and the audit reported "0 of 0 sampled" --
             * which looked like a VDP read failure and got misdiagnosed as one.
             * The raw diagnostics below prove reads were always fine: BG_A row
             * 22 col 0 returns 0xA083 (tile 131, priority 1, palette 1).
             */
            const u16 addr = (u16) (planes[p] + (i * 256u));
            u16 entry;

            entry = vdp_read_vram(addr);

            /* Empty entries (tile 0) are transparent and carry no priority
             * meaning, so they are not violations. */
            if ((entry & 0x07FFu) != 0u)
            {
                if (p == 0u)
                {
                    s_prioSampledA++;
                    if ((entry & 0x8000u) == 0u) s_prioViolA++;
                }
                else
                {
                    s_prioSampledB++;
                    if ((entry & 0x8000u) == 0u) s_prioViolB++;
                }
            }
        }
    }
    SYS_enableInts();
}

void PROBE_STAGE_tick(void)
{
    const u16 bytes = DMA_getQueueTransferSize();
    const u16 count = DMA_getQueueSize();

    if (bytes > s_dmaPeakBytes) s_dmaPeakBytes = bytes;
    if (count > s_dmaPeakCount) s_dmaPeakCount = count;
}

static void write_u16be(u32 offset, u16 value)
{
    SRAM_writeByte(offset, (u8) ((value >> 8) & 0xFFu));
    SRAM_writeByte(offset + 1u, (u8) (value & 0xFFu));
}

void PROBE_STAGE_exportToSram(void)
{
    u32 offset = PROBE_STAGE_SRAM_OFFSET;
    const u16 total = (u16) (8u + (PROBE_STAGE_WORDS * 2u));

    sample_priority_bits();

    SRAM_enable();
    SRAM_writeByte(offset + 0u, (u8) 'K');
    SRAM_writeByte(offset + 1u, (u8) 'R');
    SRAM_writeByte(offset + 2u, (u8) 'B');
    SRAM_writeByte(offset + 3u, (u8) '1');
    write_u16be(offset + 4u, PROBE_STAGE_SCHEMA);
    write_u16be(offset + 6u, total);

    offset += 8u;
    write_u16be(offset +  0u, (u16) s_cameraX);
    write_u16be(offset +  2u, (u16) s_hsSky);
    write_u16be(offset +  4u, (u16) s_hsMount);
    write_u16be(offset +  6u, (u16) s_hsHill);
    write_u16be(offset +  8u, (u16) s_hsTerrain);
    write_u16be(offset + 10u, s_dmaPeakBytes);
    write_u16be(offset + 12u, s_dmaPeakCount);
    write_u16be(offset + 14u, s_shEnabled ? 1u : 0u);
    write_u16be(offset + 16u, s_prioViolA);
    write_u16be(offset + 18u, s_prioSampledA);
    write_u16be(offset + 20u, s_prioViolB);
    write_u16be(offset + 22u, s_prioSampledB);
    write_u16be(offset + 24u, s_kirbyState);
    write_u16be(offset + 26u, (u16) s_kirbyX);
    write_u16be(offset + 28u, (u16) s_kirbyY);
    write_u16be(offset + 30u, s_enemiesAlive);
    write_u16be(offset + 32u, s_rawBgaRow0);
    write_u16be(offset + 34u, s_rawBgaTerrain);
    write_u16be(offset + 36u, s_rawBgaSecond);
    write_u16be(offset + 38u, s_rawBgbRow0);
    write_u16be(offset + 40u, s_ptVisited);
    write_u16be(offset + 42u, s_ptStep);
    write_u16be(offset + 44u, s_ptFinished);
    SRAM_disable();
}
