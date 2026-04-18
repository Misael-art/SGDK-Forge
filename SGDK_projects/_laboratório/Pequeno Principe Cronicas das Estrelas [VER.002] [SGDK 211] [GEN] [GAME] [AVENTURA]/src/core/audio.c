/* =========================================================================
 * audio.c — XGM2 wrapper: BGM management, SFX dispatch, fade
 * ========================================================================= */

#include "pp2.h"

/* -------------------------------------------------------------------------
 * BGM table — preenchido quando assets existirem
 * Por ora aponta para NULL (silêncio, XGM2 ignora NULL graciosamente)
 * ------------------------------------------------------------------------- */
static const u8 * const s_bgmTable[BGM_COUNT] = {
    NULL,   /* BGM_NONE */
    NULL,   /* BGM_TITLE   — TODO: bgm_title.xgm2 */
    NULL,   /* BGM_B612    — TODO: bgm_b612.xgm2 */
    NULL,   /* BGM_REI     — TODO: bgm_rei.xgm2 */
    NULL,   /* BGM_TRAVEL  — TODO: bgm_travel.xgm2 */
    NULL,   /* BGM_AMBIENT — TODO: bgm_ambient.xgm2 */
};

/* SFX table — placeholder, preenchido com assets PCM */
static const u8 * const s_sfxTable[SFX_COUNT] = {
    NULL,   /* SFX_STEP */
    NULL,   /* SFX_JUMP */
    NULL,   /* SFX_LAND */
    NULL,   /* SFX_INTERACT */
    NULL,   /* SFX_SOLVE */
    NULL,   /* SFX_TRAVEL_LAUNCH */
    NULL,   /* SFX_MENU_MOVE */
    NULL,   /* SFX_MENU_SELECT */
};

static const u8 s_sfxPriority[SFX_COUNT] = {
    0, 1, 0, 1, 2, 2, 0, 1
};

void Audio_init(void)
{
    XGM2_init();
}

void Audio_playBgm(BgmId id)
{
    if (id == g_ctx.currentBgm) return;
    if (id >= BGM_COUNT) return;

    if (g_ctx.currentBgm != BGM_NONE)
        Audio_fadeOutBgm();

    g_ctx.currentBgm = id;

    if (s_bgmTable[id])
        XGM2_play(s_bgmTable[id]);
}

void Audio_stopBgm(void)
{
    XGM2_stop();
    g_ctx.currentBgm = BGM_NONE;
}

void Audio_fadeOutBgm(void)
{
    XGM2_fadeOut(PP2_AUDIO_FADE_FRAMES);
    g_ctx.currentBgm = BGM_NONE;
}

void Audio_playSfx(SfxId id)
{
    if (id >= SFX_COUNT) return;
    if (!s_sfxTable[id]) return;
    XGM2_playPCM(s_sfxTable[id], s_sfxPriority[id], PP2_AUDIO_CH_SFX);
}
