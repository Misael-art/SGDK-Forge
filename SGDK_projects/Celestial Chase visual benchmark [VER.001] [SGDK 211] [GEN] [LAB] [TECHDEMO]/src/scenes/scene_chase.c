#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "gameplay/chase_hud.h"
#include "gameplay/chase_obstacles.h"
#include "gameplay/chase_player.h"
#include "gameplay/chase_pursuer.h"
#include "gameplay/chase_road.h"
#include "gameplay/chase_rules.h"
#include "resources.h"
#include "system/audio.h"
#include "system/input.h"
#include "system/runtime_probe.h"
#include "system/save_data.h"

#define CHASE_BG_B_TILE_INDEX TILE_USER_INDEX
#define CHASE_PALETTE_ACCENT_INDEX 60
#define CHASE_PALETTE_LIGHT_INDEX 61
#define CHASE_HITSTOP_MAX_FRAMES 6
#define CHASE_SHAKE_MAX 5
#define CHASE_AFTERIMAGE_IMPACT_FRAMES 12
#define CHASE_AFTERIMAGE_PULSE_FRAMES 22

static const u16 CHASE_PHASE_ACCENT[3] = { 0x086A, 0x0A6E, 0x0E6E };
static const u16 CHASE_LIGHT_PULSE[4] = { 0x08AC, 0x0ACE, 0x0EEE, 0x0ACE };

static ChaseRulesState sRules;
static u16 sLetterboxTileIndex;
static u32 sMotionFrame;
static bool sResultHandled;

static void chaseResetScreen(void)
{
    SPR_reset();
    SPR_update();
    AUDIO_stopAll();
    VDP_setWindowOff();
    VDP_setHilightShadow(FALSE);
    VDP_setTextPlane(BG_A);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);
    VDP_clearTileMapRect(BG_A, 0, 0, 64, 32);
    VDP_clearTileMapRect(BG_B, 0, 0, 64, 32);
    PAL_setPalette(PAL0, palette_black, CPU);
    PAL_setPalette(PAL1, palette_black, CPU);
    PAL_setPalette(PAL2, palette_black, CPU);
    PAL_setPalette(PAL3, palette_black, CPU);
    VDP_setBackgroundColor(0);
}

static void chaseLoadBackgrounds(void)
{
    const u16 bgATileIndex = CHASE_BG_B_TILE_INDEX + img_chase_bg_b_v011.tileset->numTile;

    VDP_drawImageEx(
        BG_B,
        &img_chase_bg_b_v011,
        TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, CHASE_BG_B_TILE_INDEX),
        0,
        0,
        TRUE,
        FALSE
    );
    VDP_drawImageEx(
        BG_A,
        &img_chase_bg_a_v011,
        TILE_ATTR_FULL(PAL3, TRUE, FALSE, FALSE, bgATileIndex),
        0,
        0,
        TRUE,
        FALSE
    );

    sLetterboxTileIndex = bgATileIndex + img_chase_bg_a_v011.tileset->numTile;
    VDP_loadTileSet(&ts_chase_letterbox_v009, sLetterboxTileIndex, CPU);
    PAL_setPalette(PAL1, spr_chase_hero_run_v009.palette->data, CPU);
    PAL_setPalette(PAL2, spr_chase_pursuer_torso_v011.palette->data, CPU);
    VDP_setBackgroundColor(0);
}

static void chaseUpdatePalette(void)
{
    u8 phase = CHASE_RULES_phaseNumber(&sRules);

    PAL_setColors(CHASE_PALETTE_ACCENT_INDEX, &CHASE_PHASE_ACCENT[phase - 1], 1, DMA_QUEUE);
    if ((sMotionFrame & 7u) == 0) {
        PAL_setColors(CHASE_PALETTE_LIGHT_INDEX, &CHASE_LIGHT_PULSE[(sMotionFrame >> 3) & 3u], 1, DMA_QUEUE);
    }
    VDP_setHilightShadow(CHASE_PURSUER_isPulseActive());
}

static void chaseUpdateComposition(bool advance)
{
    ChaseCameraShake shake;
    u8 phase = CHASE_RULES_phaseNumber(&sRules);

    CHASE_PURSUER_consumeShake(&shake);
    if (shake.x > CHASE_SHAKE_MAX) shake.x = CHASE_SHAKE_MAX;
    if (shake.x < -CHASE_SHAKE_MAX) shake.x = -CHASE_SHAKE_MAX;
    if (shake.y > CHASE_SHAKE_MAX) shake.y = CHASE_SHAKE_MAX;
    if (shake.y < -CHASE_SHAKE_MAX) shake.y = -CHASE_SHAKE_MAX;
    if (advance) {
        sMotionFrame++;
    }

    CHASE_ROAD_update(sMotionFrame, phase, shake.x, shake.y, advance);
}

static void chaseStartImpactFeedback(void)
{
    CHASE_PURSUER_startImpact(CHASE_PLAYER_x(), CHASE_PLAYER_y());
    CHASE_PLAYER_triggerAfterimage(CHASE_AFTERIMAGE_IMPACT_FRAMES);
    AUDIO_playCue(AUDIO_CUE_STRIKE);
}

static void chaseStartPulseFeedback(void)
{
    CHASE_OBSTACLES_clearThreats();
    CHASE_PURSUER_startPulse(CHASE_PLAYER_x(), CHASE_PLAYER_y());
    CHASE_PLAYER_triggerAfterimage(CHASE_AFTERIMAGE_PULSE_FRAMES);
    AUDIO_playCue(AUDIO_CUE_PULSE);
}

static void chaseHandleResult(void)
{
    u32 score;
    u32 highscore;
    bool newRecord;

    if (!CHASE_RULES_isResult(&sRules) || sResultHandled) {
        return;
    }

    sResultHandled = TRUE;
    CHASE_OBSTACLES_clearThreats();
    CHASE_PURSUER_hideFx();
    CHASE_PLAYER_setVisible(FALSE);
    CHASE_PURSUER_setVisible(FALSE);
    VDP_setHilightShadow(FALSE);
    PAL_setPalette(PAL0, palette_black, DMA_QUEUE);
    PAL_setPalette(PAL3, palette_black, DMA_QUEUE);
    AUDIO_setMusicState((sRules.flow == CHASE_FLOW_VICTORY) ? AUDIO_MUSIC_VICTORY : AUDIO_MUSIC_FAILURE);

    score = (sRules.mode == CHASE_MODE_ENDLESS) ? sRules.score : 0;
    highscore = SAVE_DATA_highscore();
    newRecord = FALSE;
    if (sRules.mode == CHASE_MODE_ENDLESS) {
        newRecord = SAVE_DATA_trySubmitEndlessScore(score);
        highscore = SAVE_DATA_highscore();
    }
    CHASE_HUD_showResult(&sRules, score, highscore, newRecord);
}

static void chaseExit(void)
{
    AUDIO_stopAll();
    CHASE_HUD_exit();
    CHASE_OBSTACLES_exit();
    CHASE_PLAYER_exit();
    CHASE_PURSUER_exit();
    CHASE_ROAD_exit();
    VDP_setHilightShadow(FALSE);
}

static void chaseHandlePause(void)
{
    bool paused = CHASE_RULES_togglePause(&sRules);

    gApp.paused = paused;
    if (paused) {
        AUDIO_pause();
        AUDIO_playCue(AUDIO_CUE_PAUSE);
    } else {
        AUDIO_resume();
        AUDIO_playCue(AUDIO_CUE_PAUSE);
    }
    CHASE_HUD_showPause(paused);
}

static void chaseHandleGameplayEvents(ChaseObstacleEvents events)
{
    if (events.pickup) {
        CHASE_RULES_collectEnergy(&sRules);
        AUDIO_playCue(AUDIO_CUE_PICKUP);
    }

    if (events.damage && CHASE_RULES_damage(&sRules)) {
        chaseStartImpactFeedback();
    }
}

void SCENE_chaseEnter(void)
{
    gApp.showDebugHud = FALSE;
    gApp.paused = FALSE;
    sMotionFrame = 0;
    sResultHandled = FALSE;

    chaseResetScreen();
    chaseLoadBackgrounds();
    SAVE_DATA_init();
    CHASE_RULES_reset(&sRules, gApp.targetFps, gApp.chaseMode);
    CHASE_ROAD_enter(sLetterboxTileIndex);
    CHASE_PURSUER_enter();
    CHASE_OBSTACLES_enter();
    CHASE_PLAYER_enter();
    CHASE_HUD_enter();
    AUDIO_setIntensity(1);
    chaseUpdateComposition(FALSE);
    chaseUpdatePalette();

    if (MDRuntimeProbe_consumeChaseFailureBootstrap()) {
        sRules.mode = CHASE_MODE_ENDLESS;
        sRules.score = 1234;
        sRules.flow = CHASE_FLOW_FAILURE;
        sRules.integrity = 0;
        sRules.pressure = CHASE_MAX_PRESSURE;
        sRules.energy = 0;
        sRules.pulsesUsed = 0;
        chaseHandleResult();
    } else {
        CHASE_HUD_update(&sRules);
    }
}

void SCENE_chaseUpdate(void)
{
    ChaseObstacleEvents obstacleEvents;
    bool allowHeroUpload;
    bool allowPursuerUpload;

    if (CHASE_RULES_isResult(&sRules)) {
        if (INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START)) {
            chaseExit();
            APP_changeScene(APP_SCENE_CHASE);
            return;
        }
        if (INPUT_pressed(BUTTON_B) || INPUT_pressed(BUTTON_MODE)) {
            chaseExit();
            APP_changeScene(APP_SCENE_MENU);
        }
        return;
    }

    if (INPUT_pressed(BUTTON_START)) {
        chaseHandlePause();
        return;
    }

    if (sRules.flow == CHASE_FLOW_PAUSED) {
        return;
    }

    if (sRules.hitstopFrames > CHASE_HITSTOP_MAX_FRAMES) {
        sRules.hitstopFrames = CHASE_HITSTOP_MAX_FRAMES;
    }
    if (CHASE_RULES_tickHitstop(&sRules)) {
        chaseUpdateComposition(FALSE);
        chaseUpdatePalette();
        CHASE_HUD_update(&sRules);
        return;
    }

    if (INPUT_pressed(BUTTON_B) && CHASE_RULES_usePulse(&sRules)) {
        chaseStartPulseFeedback();
    }

    allowHeroUpload = (sMotionFrame & 1u) == 0;
    allowPursuerUpload = !allowHeroUpload;
    CHASE_PLAYER_update(TRUE, allowHeroUpload);
    obstacleEvents = CHASE_OBSTACLES_update(&sRules, (sMotionFrame & 3u) == 2u);
    chaseHandleGameplayEvents(obstacleEvents);
    CHASE_RULES_update(&sRules);
    CHASE_PURSUER_update(sRules.pressure, allowPursuerUpload);
    chaseUpdateComposition(TRUE);
    chaseUpdatePalette();

    if (sRules.phaseChanged) {
        CHASE_ROAD_setClimax(sRules.flow == CHASE_FLOW_CLIMAX);
        CHASE_HUD_setCinematic(sRules.flow == CHASE_FLOW_CLIMAX);
        AUDIO_setIntensity(CHASE_RULES_phaseNumber(&sRules));
        AUDIO_playCue(AUDIO_CUE_PRESSURE);
    }

    chaseHandleResult();
    CHASE_HUD_update(&sRules);
}
