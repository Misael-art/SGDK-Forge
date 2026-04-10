#include "project.h"

static bool gHintEnabled = false;
static const u16 *gTopColors = NULL;
static const u16 *gBottomColors = NULL;
static u16 gColorCount = 0;
static u16 gSplitLine = 0;

HINTERRUPT_CALLBACK HintFx_callback()
{
    if (!gHintEnabled)
    {
        return;
    }

    PAL_setColors(0, gBottomColors, gColorCount, CPU);
    VDP_setHIntCounter(0xFF);
}

void HintFx_init(void)
{
    SYS_disableInts();
    SYS_setHIntCallback(HintFx_callback);
    VDP_setHInterrupt(FALSE);
    SYS_enableInts();
}

void HintFx_disable(void)
{
    gHintEnabled = false;
    SYS_disableInts();
    VDP_setHInterrupt(FALSE);
    SYS_enableInts();
}

void HintFx_configure(const u16 *topColors, const u16 *bottomColors, u16 count, u16 splitLine)
{
    gTopColors = topColors;
    gBottomColors = bottomColors;
    gColorCount = count;
    gSplitLine = splitLine;
    gHintEnabled = true;
}

void HintFx_onVBlank(void)
{
    if (!gHintEnabled || (gTopColors == NULL) || (gBottomColors == NULL) || (gColorCount == 0))
    {
        VDP_setHInterrupt(FALSE);
        return;
    }

    PAL_setColors(0, gTopColors, gColorCount, CPU);
    VDP_setHIntCounter((u8) gSplitLine);
    VDP_setHInterrupt(TRUE);
}
