/* =========================================================================
 * codex.c — Codex entry display (unlocked per planet)
 * ========================================================================= */

#include "pp2.h"

/* -------------------------------------------------------------------------
 * Codex text data (all 12 planets)
 * ------------------------------------------------------------------------- */

static const char * const s_b612Lines[] = {
    "Planeta B-612.",
    "Tao pequeno que o por do sol",
    "pode ser visto 43 vezes por dia",
    "movendo a cadeira.",
    "Tecnica: HSCROLL_LINE + palette cycling."
};

static const char * const s_reiLines[] = {
    "Planeta do Rei.",
    "Governado por um monarca solitario",
    "cujos subditos eram as estrelas.",
    "Tecnica: Parallax multicamada,",
    "VSCROLL_COLUMN por coluna de tiles."
};

static const char * const s_vaidosoLines[] = {
    "Planeta do Vaidoso.",
    "Habitado por um ser que vivia",
    "de aplausos que nunca chegavam.",
    "Tecnica: Sprite scaling simulado,",
    "palette flash."
};

static const char * const s_bebadoLines[] = {
    "Planeta do Bebado.",
    "Ele bebia para esquecer",
    "a vergonha de beber.",
    "Tecnica: Sine wave no hscroll,",
    "flicker de sprites."
};

static const char * const s_contadorLines[] = {
    "Planeta do Contador.",
    "Ele contava estrelas para possuir.",
    "Nunca as via — so contava.",
    "Tecnica: Tilemap dinamico,",
    "estrelas atualizadas em tempo real."
};

static const char * const s_acendedorLines[] = {
    "Planeta do Acendedor.",
    "Um planeta tao rapido que",
    "o dia durava um minuto.",
    "Tecnica: H-Int line-level",
    "palette swap dia/noite."
};

static const char * const s_geografoLines[] = {
    "Planeta do Geografo.",
    "Ele conhecia todos os rios",
    "mas nunca tinha saido de sua mesa.",
    "Tecnica: MAP API com mapa",
    "maior que a tela (512x224)."
};

static const char * const s_serpenteLines[] = {
    "Planeta da Serpente.",
    "Ela podia enviar qualquer um",
    "de volta a terra em seis segundos.",
    "Tecnica: Raster interrupt,",
    "deformacao de background."
};

static const char * const s_desertoLines[] = {
    "Planeta do Deserto.",
    "O deserto e belo porque",
    "em algum lugar esconde um poco.",
    "Tecnica: Dithering de paleta,",
    "particles de areia."
};

static const char * const s_jardimLines[] = {
    "Jardim das Rosas.",
    "Havia cem rosas iguais a sua.",
    "E nenhuma era a sua.",
    "Tecnica: Sprites em grid,",
    "palette morph gradual."
};

static const char * const s_pocoLines[] = {
    "O Poco no Deserto.",
    "O que torna o poco belo",
    "nao e a agua — e o esforco.",
    "Tecnica: Zoom-in simulado,",
    "echo de audio espacial."
};

static const char * const s_b612RetLines[] = {
    "B-612 — Retorno.",
    "Ele havia partido e voltado.",
    "E nada havia mudado — exceto tudo.",
    "Tecnica: Todos os FX combinados.",
    "Momento culminante."
};

static const CodexEntry s_codex[PP2_PLANET_COUNT] = {
    { "B-612",            s_b612Lines,     5 },
    { "Planeta do Rei",   s_reiLines,      5 },
    { "Vaidoso",          s_vaidosoLines,  5 },
    { "Bebado",           s_bebadoLines,   5 },
    { "Contador",         s_contadorLines, 5 },
    { "Acendedor",        s_acendedorLines,5 },
    { "Geografo",         s_geografoLines, 5 },
    { "Serpente",         s_serpenteLines, 5 },
    { "Deserto",          s_desertoLines,  5 },
    { "Jardim das Rosas", s_jardimLines,   5 },
    { "O Poco",           s_pocoLines,     5 },
    { "B-612 Retorno",    s_b612RetLines,  5 },
};

/* -------------------------------------------------------------------------
 * Public API
 * ------------------------------------------------------------------------- */

void Codex_init(void)
{
    /* Nothing to init */
}

void Codex_unlock(GameCtx *ctx, PlanetId planet)
{
    if (planet < PP2_PLANET_COUNT)
        ctx->codexUnlocked[planet] = TRUE;
}

void Codex_draw(GameCtx *ctx)
{
    u16 idx = ctx->codexIndex;
    if (idx >= PP2_PLANET_COUNT) return;
    if (!ctx->codexUnlocked[idx]) return;

    const CodexEntry *e = &s_codex[idx];

    VDP_clearPlane(BG_A, TRUE);
    VDP_drawTextBG(BG_A, "=== CODEX ===", 14, 2);
    VDP_drawTextBG(BG_A, e->title, 2, 4);

    for (u16 i = 0; i < e->lineCount && i < 10; i++)
        VDP_drawTextBG(BG_A, e->lines[i], 2, (u16)(6 + i));

    /* Navigation hint */
    VDP_drawTextBG(BG_A, "< L/R: navegar >   [START: fechar]", 3, 24);

    /* Planet counter */
    char buf[24];
    snprintf(buf, sizeof(buf), "Desbloqueado: %u/%u", idx + 1, PP2_PLANET_COUNT);
    VDP_drawTextBG(BG_A, buf, 2, 26);
}

void Codex_handleInput(GameCtx *ctx, u16 pressed)
{
    if (pressed & BUTTON_RIGHT)
    {
        u16 next = ctx->codexIndex;
        do {
            next = (next + 1) % PP2_PLANET_COUNT;
        } while (!ctx->codexUnlocked[next] && next != ctx->codexIndex);
        ctx->codexIndex = next;
        Audio_playSfx(SFX_MENU_MOVE);
    }
    else if (pressed & BUTTON_LEFT)
    {
        u16 prev = ctx->codexIndex;
        do {
            prev = (prev == 0) ? PP2_PLANET_COUNT - 1 : prev - 1;
        } while (!ctx->codexUnlocked[prev] && prev != ctx->codexIndex);
        ctx->codexIndex = prev;
        Audio_playSfx(SFX_MENU_MOVE);
    }
    else if (pressed & BUTTON_START)
    {
        Engine_requestState(STATE_PAUSE);
    }
}
