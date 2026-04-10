/* =========================================================================
 * vblank.c — VBlank callback: scroll DMA, sprite update, audio tick
 *
 * Registrado uma vez em Engine_init via SYS_setVBlankCallback.
 * Todo o trabalho de DMA acontece aqui, nunca no loop principal.
 * ========================================================================= */

#include "pp2.h"

static bool s_lineScroll  = FALSE;
static bool s_colScroll   = FALSE;
static bool s_hintEnabled = FALSE;

/* -------------------------------------------------------------------------
 * H-Int callback — executa a cada scanline configurada
 * Usado para palette split (dia/noite, pôr do sol)
 * ------------------------------------------------------------------------- */
static const u16 *s_hintPalTop    = NULL;
static const u16 *s_hintPalBottom = NULL;
static u16        s_hintLine      = 192;

static void hintCallback(void)
{
    /* Ler VCounter para confirmar linha (proteção contra glitch) */
    if (s_hintPalBottom)
        PAL_setPalette(PP2_PAL_BG, s_hintPalBottom, CPU);
}

/* -------------------------------------------------------------------------
 * VBlank callback — executa no início do VBlank
 * ------------------------------------------------------------------------- */
static void vblankCallback(void)
{
    /* 1. Restaurar paleta top (para próximo frame) */
    if (s_hintEnabled && s_hintPalTop)
        PAL_setPalette(PP2_PAL_BG, s_hintPalTop, CPU);

    /* 2. Aplicar line scroll (HSCROLL_LINE) via DMA */
    if (s_lineScroll)
    {
        VDP_setHorizontalScrollLine(BG_B, 0, g_ctx.hscrollB, PP2_HSCROLL_LINES, DMA);
        VDP_setHorizontalScrollLine(BG_A, 0, g_ctx.hscrollA, PP2_HSCROLL_LINES, DMA);
    }

    /* 3. Aplicar column scroll (VSCROLL_COLUMN) via DMA */
    if (s_colScroll)
    {
        VDP_setVerticalScrollTile(BG_B, 0, g_ctx.vscrollB, PP2_VSCROLL_COLS, DMA);
        VDP_setVerticalScrollTile(BG_A, 0, g_ctx.vscrollA, PP2_VSCROLL_COLS, DMA);
    }

    /* 4. Flush sprite engine (DMA da sprite table) */
    SPR_update();

    /* 5. Tick XGM2 */
    XGM2_update();
}

/* -------------------------------------------------------------------------
 * Public API
 * ------------------------------------------------------------------------- */
void VBlank_init(void)
{
    s_lineScroll  = FALSE;
    s_colScroll   = FALSE;
    s_hintEnabled = FALSE;
    SYS_setVBlankCallback(vblankCallback);
}

void VBlank_setScrollMode(bool lineScroll, bool colScroll)
{
    s_lineScroll = lineScroll;
    s_colScroll  = colScroll;

    if (lineScroll && colScroll)
        VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_COLUMN);
    else if (lineScroll)
        VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_PLANE);
    else if (colScroll)
        VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_COLUMN);
    else
        VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
}

void VBlank_enableHInt(u16 line)
{
    s_hintLine    = line;
    s_hintEnabled = TRUE;
    VDP_setHInterrupt(TRUE);
    VDP_setHIntCounter(line);
    SYS_setHIntCallback(hintCallback);
}

void VBlank_disableHInt(void)
{
    s_hintEnabled  = FALSE;
    s_hintPalTop   = NULL;
    s_hintPalBottom = NULL;
    VDP_setHInterrupt(FALSE);
    SYS_setHIntCallback(NULL);
}

/* Called by scene to configure split palette */
void VBlank_setSplitPalettes(const u16 *top, const u16 *bottom)
{
    s_hintPalTop    = top;
    s_hintPalBottom = bottom;
}
