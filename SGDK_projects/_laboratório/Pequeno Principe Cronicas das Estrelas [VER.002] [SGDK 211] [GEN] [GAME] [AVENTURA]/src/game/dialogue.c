/* =========================================================================
 * dialogue.c — Typewriter dialogue system with speaker name
 * ========================================================================= */

#include "pp2.h"

/* -------------------------------------------------------------------------
 * Box geometry (in tiles, relative to Window plane start)
 * Window plane row 0 = VDP row PP2_HUD_TILE_ROW = 24
 * DialogBox sits in rows 1-3 of the Window (rows 25-27 on screen)
 * ------------------------------------------------------------------------- */
#define DBOX_COL        1
#define DBOX_ROW        1   /* relative to Window */
#define DBOX_W          38
#define DBOX_LINES      3

void Dialogue_init(void)
{
    /* Nothing to allocate */
}

/* -------------------------------------------------------------------------
 * Dialogue_open
 * ------------------------------------------------------------------------- */
void Dialogue_open(GameCtx *ctx, const char *speaker,
                   const char * const *lines, u16 lineCount)
{
    DialogueState *d = &ctx->dialogue;

    d->active         = TRUE;
    d->dirty          = TRUE;
    d->speaker        = speaker;
    d->lines          = lines;
    d->lineCount      = lineCount;
    d->currentLine    = 0;
    d->typewriterPos  = 0;
    d->totalChars     = (u16)strlen(lines[0]);
    d->timer          = 0;
}

/* -------------------------------------------------------------------------
 * Dialogue_close
 * ------------------------------------------------------------------------- */
void Dialogue_close(GameCtx *ctx)
{
    ctx->dialogue.active = FALSE;
    ctx->dialogue.dirty  = FALSE;
    /* Clear dialogue rows on Window plane */
    for (u8 row = DBOX_ROW; row < DBOX_ROW + DBOX_LINES + 2; row++)
        VDP_clearTextLineBG(WINDOW, PP2_HUD_TILE_ROW + row);
}

/* -------------------------------------------------------------------------
 * Dialogue_update — advance typewriter
 * ------------------------------------------------------------------------- */
void Dialogue_update(GameCtx *ctx)
{
    DialogueState *d = &ctx->dialogue;
    if (!d->active) return;

    if (d->typewriterPos < d->totalChars)
    {
        d->typewriterPos++;
        d->dirty = TRUE;
    }
}

/* -------------------------------------------------------------------------
 * Dialogue_handleInput — A/C advances, START skips
 * ------------------------------------------------------------------------- */
void Dialogue_handleInput(GameCtx *ctx, u16 pressed)
{
    DialogueState *d = &ctx->dialogue;
    if (!d->active) return;

    if (pressed & (BUTTON_A | BUTTON_C | BUTTON_START))
    {
        if (d->typewriterPos < d->totalChars)
        {
            /* Skip typewriter — show full line */
            d->typewriterPos = d->totalChars;
            d->dirty = TRUE;
        }
        else
        {
            /* Advance to next line */
            d->currentLine++;
            if (d->currentLine >= d->lineCount)
            {
                Dialogue_close(ctx);
            }
            else
            {
                d->typewriterPos = 0;
                d->totalChars    = (u16)strlen(d->lines[d->currentLine]);
                d->dirty         = TRUE;
            }
        }
        Audio_playSfx(SFX_MENU_SELECT);
    }
}

/* -------------------------------------------------------------------------
 * Dialogue_draw — render to Window plane
 * ------------------------------------------------------------------------- */
void Dialogue_draw(GameCtx *ctx)
{
    DialogueState *d = &ctx->dialogue;
    if (!d->active || !d->dirty) return;
    d->dirty = FALSE;

    /* Background box (simple character-based) */
    /* Speaker name row */
    if (d->speaker)
    {
        char buf[42];
        /* Format: "[ SPEAKER ]" */
        snprintf(buf, sizeof(buf), "[ %s ]", d->speaker);
        VDP_drawTextBG(WINDOW, buf, DBOX_COL, PP2_HUD_TILE_ROW + DBOX_ROW);
    }

    /* Text row — show partial text based on typewriter position */
    const char *text = d->lines[d->currentLine];
    u16 visLen = d->typewriterPos;
    if (visLen > (u16)strlen(text)) visLen = (u16)strlen(text);

    /* Copy visible portion to buffer */
    char lineBuf[42];
    memset(lineBuf, ' ', DBOX_W);
    lineBuf[DBOX_W] = '\0';
    memcpy(lineBuf, text, visLen);
    lineBuf[DBOX_W] = '\0';

    VDP_drawTextBG(WINDOW, lineBuf, DBOX_COL, PP2_HUD_TILE_ROW + DBOX_ROW + 1);

    /* Continuation indicator */
    if (d->typewriterPos >= d->totalChars)
    {
        bool hasMore = (d->currentLine + 1 < d->lineCount);
        VDP_drawTextBG(WINDOW,
                       hasMore ? "  [ A/C: continuar ]" : "  [ A/C: fechar ]",
                       DBOX_COL, PP2_HUD_TILE_ROW + DBOX_ROW + 2);
    }
    else
    {
        VDP_clearTextLineBG(WINDOW, PP2_HUD_TILE_ROW + DBOX_ROW + 2);
    }
}
