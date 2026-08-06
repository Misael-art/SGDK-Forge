#include <genesis.h>

/*
 * Minimal ROM-side specimen. A future portable build route may compile this
 * source and extract FREF from SRAM; this backport intentionally claims no ROM.
 */
#define FREF_OFFSET 0x1800u

static void write_word(u32 offset, u16 value)
{
    SRAM_writeByte(offset, (u8)(value >> 8));
    SRAM_writeByte(offset + 1u, (u8)value);
}

static void export_fixture_contract(void)
{
    const u16 words[20] = {
        3u, 3u, 3u, 1u, 8u, 0u, 0u, 0u, 0u, 0u,
        0x1234u, 0x5678u, 0x1234u, 0x5678u, 16u, 0u, 0u, 0u, 0u, 0u
    };
    u16 index;
    SRAM_enable();
    SRAM_writeByte(FREF_OFFSET + 0u, 'F');
    SRAM_writeByte(FREF_OFFSET + 1u, 'R');
    SRAM_writeByte(FREF_OFFSET + 2u, 'E');
    SRAM_writeByte(FREF_OFFSET + 3u, 'F');
    write_word(FREF_OFFSET + 4u, 1u);
    write_word(FREF_OFFSET + 6u, 20u);
    for (index = 0u; index < 20u; index++) write_word(FREF_OFFSET + 8u + (index * 2u), words[index]);
    SRAM_disable();
}

int main(bool hardReset)
{
    (void)hardReset;
    export_fixture_contract();
    VDP_drawText("FORGE REFERENCE", 12u, 13u);
    while (TRUE) SYS_doVBlankProcess();
    return 0;
}
