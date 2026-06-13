#include <genesis.h>

#include "system/save_data.h"

#define SAVE_DATA_SCHEMA_VERSION 1

static u32 s_highscore;
static bool s_initialized;

static void sram_write_u16be(u32 offset, u16 value)
{
    SRAM_writeByte(offset, (u8)((value >> 8) & 0xFFu));
    SRAM_writeByte(offset + 1, (u8)(value & 0xFFu));
}

static void sram_write_u32be(u32 offset, u32 value)
{
    SRAM_writeByte(offset, (u8)((value >> 24) & 0xFFu));
    SRAM_writeByte(offset + 1, (u8)((value >> 16) & 0xFFu));
    SRAM_writeByte(offset + 2, (u8)((value >> 8) & 0xFFu));
    SRAM_writeByte(offset + 3, (u8)(value & 0xFFu));
}

static u16 sram_read_u16be(u32 offset)
{
    return (u16)(((u16)SRAM_readByte(offset) << 8) | SRAM_readByte(offset + 1));
}

static u32 sram_read_u32be(u32 offset)
{
    return ((u32)SRAM_readByte(offset) << 24)
        | ((u32)SRAM_readByte(offset + 1) << 16)
        | ((u32)SRAM_readByte(offset + 2) << 8)
        | (u32)SRAM_readByte(offset + 3);
}

void SAVE_DATA_init(void)
{
    u32 offset = SAVE_DATA_SRAM_OFFSET;
    bool valid = FALSE;

    if (s_initialized) {
        return;
    }
    s_initialized = TRUE;
    s_highscore = 0;

    SRAM_enableRO();
    valid = SRAM_readByte(offset + 0) == (u8) 'C'
        && SRAM_readByte(offset + 1) == (u8) 'C'
        && SRAM_readByte(offset + 2) == (u8) 'S'
        && SRAM_readByte(offset + 3) == (u8) 'V'
        && sram_read_u16be(offset + 4) == (u16) SAVE_DATA_SCHEMA_VERSION;

    if (valid) {
        s_highscore = sram_read_u32be(offset + 6);
    }
    SRAM_disable();
}

u32 SAVE_DATA_highscore(void)
{
    if (!s_initialized) {
        SAVE_DATA_init();
    }
    return s_highscore;
}

bool SAVE_DATA_trySubmitEndlessScore(u32 score)
{
    u32 offset = SAVE_DATA_SRAM_OFFSET;

    if (!s_initialized) {
        SAVE_DATA_init();
    }

    if (score <= s_highscore) {
        return FALSE;
    }

    SRAM_enable();
    SRAM_writeByte(offset + 0, (u8) 'C');
    SRAM_writeByte(offset + 1, (u8) 'C');
    SRAM_writeByte(offset + 2, (u8) 'S');
    SRAM_writeByte(offset + 3, (u8) 'V');
    sram_write_u16be(offset + 4, (u16) SAVE_DATA_SCHEMA_VERSION);
    sram_write_u32be(offset + 6, score);
    SRAM_disable();

    s_highscore = score;
    return TRUE;
}
