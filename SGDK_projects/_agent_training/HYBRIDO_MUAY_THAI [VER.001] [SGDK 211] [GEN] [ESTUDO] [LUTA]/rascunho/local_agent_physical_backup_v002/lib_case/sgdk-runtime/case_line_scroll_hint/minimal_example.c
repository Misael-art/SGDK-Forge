#include <genesis.h>

static s16 offsets[224];

static void hint_cb(void)
{
    /* split or per-line effect hook */
}

int main(void)
{
    SYS_setHIntCallback(hint_cb);
    VDP_setHIntCounter(128);
    VDP_setHInterrupt(TRUE);

    while (TRUE)
    {
        VDP_setHorizontalScrollLine(BG_B, 0, offsets, 224, DMA);
        SYS_doVBlankProcess();
    }

    return 0;
}
