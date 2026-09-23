#include <genesis.h>

static fix16 zmap[224];
static s16 hscrollA[224];

int main(void)
{
    for (u16 i = 0; i < 224; i++)
        zmap[i] = F16_div(FIX16(-75), FIX16(i) - FIX16(112));

    while (TRUE)
    {
        fix16 currentX = 0;

        for (u16 y = 0; y < 224; y++)
        {
            currentX += zmap[y] >> 5;
            hscrollA[223 - y] = 160 + F16_toInt(currentX);
        }

        VDP_setHorizontalScrollLine(BG_A, 0, hscrollA, 224, DMA_QUEUE);
        SYS_doVBlankProcess();
    }

    return 0;
}
