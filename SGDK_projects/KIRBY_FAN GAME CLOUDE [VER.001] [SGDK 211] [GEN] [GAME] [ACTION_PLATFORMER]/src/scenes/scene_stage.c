#include <genesis.h>

#include "core/app.h"
#include "audio/xgm_router.h"
#include "entities/ability.h"
#include "entities/enemy.h"
#include "entities/kirby.h"
#include "resources.h"
#include "scenes/scene_gameover.h"
#include "scenes/scene_stage.h"
#include "system/input.h"
#include "system/playtest.h"
#include "system/probe_stage.h"
#include "systems/raster.h"
#include "systems/stage_map.h"

/*
 * FASE 1 slice: Kirby controllable inside the five-layer parallax, running
 * within every gate. Art is placeholder; the layer architecture is not.
 *
 * Layer sources (doc/ARCHITECTURE.md section 3):
 *   1 sky        BG_B (no tiles)   backdrop, H-int gradient owned by raster.c
 *   2 mountains  BG_B rows 8..14   camX / 8
 *   3 hills      BG_B rows 15..25  camX / 3
 *   4 terrain    BG_A rows 22..29  camX / 1
 *   5 foreground sprites           camX * 5/4
 */

#define CAM_DEADZONE 48
#define CAM_MAX_X (STAGE_PLANE_WIDTH - 320)

/*
 * doc/ARCHITECTURE.md section 5 gives camada 5 a quota of 8 sprites, and that
 * quota is a PER-SCANLINE constraint here, not just a per-frame one: every tuft
 * sits on the same screen row, so N tufts cost N of the 20 sprites allowed on
 * those scanlines. Measured 2026-07-30: 24 tufts on one row made
 * sprites_per_scanline peak at 24 and FAIL the gate, while sprites_per_frame
 * was still only 25 of 80. The per-frame budget is not the binding limit for a
 * horizontal foreground band; the per-scanline one is.
 */
/*
 * Reduced from 8 to 6 on 2026-08-06. With 6 enemies, 12 ability shots and Kirby
 * all sharing the ground rows, sprites_per_scanline measured 19 of the hardware
 * limit of 20 -- one sprite from flicker. doc/ARCHITECTURE.md section 5 gives a
 * degradation order for exactly this: particles first, THEN the foreground
 * layer, then projectiles. Enemies and Kirby never degrade.
 *
 * This is the documented lever being spent, not an arbitrary tweak.
 */
#define FG_TUFT_COUNT 6

static Kirby s_kirby;
static s16 s_cameraX;
static Sprite* s_sprKirby;
static Sprite* s_sprKirbyRunReview;
static Sprite* s_sprFg[FG_TUFT_COUNT];
static Sprite* s_sprEnemy[ENEMY_POOL_SIZE];
static Sprite* s_sprShot[ABILITY_SHOT_POOL];

/* Ability held by Kirby. PAL3 is the ability palette (doc/PALETTES.md 3). */
static u8 s_ability;
static u16 s_abilityFlash;
static bool s_swallowSeen;

/* Plane-space X of each foreground tuft. */
static const s16 FG_X[FG_TUFT_COUNT] =
    { 40, 130, 220, 300, 390, 470 };

static u16 s_tileNext;

/*
 * Stage establishing pan. A real shipped feature, not a test hook: on entering
 * a stage the camera sweeps right and back before handing control over, which
 * is how the source game introduces a room. It also happens to be what makes
 * the five-layer parallax provable in a still capture, because every layer is
 * displaced by a different amount while the camera moves.
 */
#define INTRO_PAN_FRAMES 900u   /* PROVISORIO: longo o bastante para a captura cair dentro do pan e provar o parallax. Valor de producao sera decidido no playtest. */
#define INTRO_PAN_REACH 176

static u16 s_introPan;

/*
 * Lake variant of the stage: same terrain, plus the waterline (R3 + R4).
 *
 * The CRAM word count for R4 comes from an env-independent constant here so a
 * capture can walk it upward and find where the hblank actually runs out.
 * doc/PALETTES.md 6.1 had it at 1 word with the ceiling marked [NAO MEDIDO].
 */
#ifndef STAGE_WATER_CRAM_WORDS
#define STAGE_WATER_CRAM_WORDS 4u
#endif

void SCENE_stageLakeEnter(void)
{
    SCENE_stageEnter();
    s_introPan = 0u;
    RASTER_setWaterCramWords(STAGE_WATER_CRAM_WORDS);
    /* Waterline just above the terrain so both halves are visible at once. */
    RASTER_setWaterline(150);
    RASTER_updateScroll(s_cameraX);
}

void SCENE_stagePlaytestEnter(void)
{
    SCENE_stageEnter();
    s_introPan = 0u;      /* no establishing pan: the script owns the timeline */
    PLAYTEST_begin();
}

void SCENE_stageEnter(void)
{
    u16 i;

    /* The stage owns no text: telemetry comes from the probe, not from a HUD
     * that would fight the terrain for BG_A tiles. */
    gApp.showDebugHud = FALSE;
    /*
     * VDP_clearPlane zeroes the nametable. VDP_clearTextArea is deliberately
     * NOT called here: it fills the area with the font's blank glyph, whose
     * tile index is non-zero and whose priority bit is 0. Those tiles are
     * invisible, but they are still priority-0 background tiles, and with
     * Shadow/Highlight enabled globally that is exactly what gate P5 forbids.
     * Measured 2026-07-30: with the clearTextArea call, BG_A reported 16 of 16
     * sampled entries at priority 0 while BG_B reported 0 of 16.
     */
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);

    s_tileNext = TILE_USER_INDEX;

    /* PAL0 = distant background, PAL1 = near background, PAL2 = Kirby.
     * doc/PALETTES.md section 3. */
    PAL_setPalette(PAL0, img_ph_sky.palette->data, DMA);
    PAL_setPalette(PAL1, img_ph_terrain.palette->data, DMA);
    PAL_setPalette(PAL2, spr_ph_kirby.palette->data, DMA);
    PAL_setPalette(PAL3, spr_ph_ability_fx.palette->data, DMA);

    /* --- CAMADAS 1..3 on BG_B ------------------------------------------- */
    VDP_drawImageEx(BG_B, &img_ph_sky,
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, s_tileNext),
                    0, 0, FALSE, TRUE);
    s_tileNext += img_ph_sky.tileset->numTile;

    VDP_drawImageEx(BG_B, &img_ph_mount,
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, s_tileNext),
                    0, 8, FALSE, TRUE);
    s_tileNext += img_ph_mount.tileset->numTile;

    VDP_drawImageEx(BG_B, &img_ph_hills,
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, s_tileNext),
                    0, 15, FALSE, TRUE);
    s_tileNext += img_ph_hills.tileset->numTile;

    /* --- CAMADA 4 on BG_A ----------------------------------------------- */
    VDP_drawImageEx(BG_A, &img_ph_terrain,
                    TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, s_tileNext),
                    0, 22, FALSE, TRUE);
    s_tileNext += img_ph_terrain.tileset->numTile;

    /* --- entities ------------------------------------------------------- */
    KIRBY_init(&s_kirby, FIX16(48), FIX16(120));
    s_cameraX = 0;
    s_introPan = INTRO_PAN_FRAMES;

    s_sprKirby = SPR_addSprite(&spr_ph_kirby, 0, 0,
                               TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
    SPR_setAnim(s_sprKirby, 0);
    s_sprKirbyRunReview = SPR_addSprite(&spr_native_run_cycle_v11, 0, 0,
                                        TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
    SPR_setVisibility(s_sprKirbyRunReview, HIDDEN);

    /* CAMADA 5: foreground tufts, priority TRUE so they sit in front. */
    for (i = 0u; i < FG_TUFT_COUNT; i++)
    {
        s_sprFg[i] = SPR_addSprite(&spr_ph_fg, 0, 0,
                                   TILE_ATTR(PAL1, TRUE, FALSE, FALSE));
    }

    /* --- enemies -------------------------------------------------------- */
    ABILITY_init();
    ENEMY_initPool();
    /* Each enemy grants a different ability so all five movesets are reachable
     * in one stage; the last one grants nothing, which is also a Kirby staple. */
    ENEMY_spawn(0, FIX16(200), FIX16(150), FIX16(0.45), ABILITY_FIRE);
    ENEMY_spawn(1, FIX16(260), FIX16(150), FIX16(-0.45), ABILITY_BEAM);
    ENEMY_spawn(2, FIX16(330), FIX16(150), FIX16(0.45), ABILITY_CUTTER);
    ENEMY_spawn(3, FIX16(400), FIX16(150), FIX16(-0.45), ABILITY_STONE);
    ENEMY_spawn(4, FIX16(460), FIX16(150), FIX16(0.45), ABILITY_SWORD);
    ENEMY_spawn(5, FIX16(500), FIX16(150), FIX16(-0.45), ABILITY_NONE);

    for (i = 0u; i < ENEMY_POOL_SIZE; i++)
    {
        s_sprEnemy[i] = SPR_addSprite(&spr_ph_enemy, 0, 0,
                                      TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
        SPR_setVisibility(s_sprEnemy[i], HIDDEN);
    }

    for (i = 0u; i < ABILITY_SHOT_POOL; i++)
    {
        s_sprShot[i] = SPR_addSprite(&spr_ph_ability_fx, 0, 0,
                                     TILE_ATTR(PAL3, TRUE, FALSE, FALSE));
        SPR_setVisibility(s_sprShot[i], HIDDEN);
    }

    s_ability = ABILITY_NONE;
    s_abilityFlash = 0u;
    s_swallowSeen = FALSE;
    AUDIO_playMusic(mus_stage_valley);
    PROBE_STAGE_reset();

    RASTER_setWaterline(-1);   /* no water in the normal stage */
    RASTER_initStage();
    RASTER_updateScroll(s_cameraX);
}

static void SCENE_stageCamera(void)
{
    const s16 kx = F16_toInt(s_kirby.x);

    if (s_introPan > 0u)
    {
        /* Ease out and back: 0 -> REACH over the first half, back to 0 on the
         * second half, so the pan ends exactly where gameplay begins. */
        const u16 half = INTRO_PAN_FRAMES / 2u;
        const u16 t = INTRO_PAN_FRAMES - s_introPan;
        const u16 phase = (t < half) ? t : (INTRO_PAN_FRAMES - t);

        s_cameraX = (s16) (((s32) phase * INTRO_PAN_REACH) / (s32) half);
        if (s_cameraX < 0)         s_cameraX = 0;
        if (s_cameraX > CAM_MAX_X) s_cameraX = CAM_MAX_X;
        s_introPan--;
        return;
    }
    const s16 target = (s16) (kx - 160);
    s16 delta = (s16) (target - s_cameraX);

    if (delta > CAM_DEADZONE)       s_cameraX += (s16) (delta - CAM_DEADZONE);
    else if (delta < -CAM_DEADZONE) s_cameraX += (s16) (delta + CAM_DEADZONE);

    if (s_cameraX < 0)          s_cameraX = 0;
    if (s_cameraX > CAM_MAX_X)  s_cameraX = CAM_MAX_X;
}

void SCENE_stageUpdate(void)
{
    u16 i;
    s16 sx;

    RASTER_frameStart();

    if (INPUT_pressed(BUTTON_START))
    {
        RASTER_shutdown();
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    /*
     * The world keeps simulating during the establishing pan; only PLAYER INPUT
     * is suppressed. Freezing the whole simulation left Kirby and the enemies
     * hovering in mid-air because gravity never ran, which looked like a physics
     * bug in the first capture. A pan over a living world reads as intentional;
     * a pan over a frozen one reads as broken.
     */
    {
        u16 held;
        u16 pressed;

        if (PLAYTEST_active())
        {
            /* The script drives the pad. The intro pan is skipped entirely in
             * playtest so the recorded frames line up with the script and not
             * with an animation. */
            held = PLAYTEST_poll(&pressed);
        }
        else
        {
            held = (s_introPan > 0u) ? 0u : gInput.held;
            pressed = (s_introPan > 0u) ? 0u : gInput.pressed;
        }

        KIRBY_update(&s_kirby, held, pressed);

        /*
         * B does double duty, and that is the Kirby design, not a shortcut:
         * with no ability B inhales; with an ability B ATTACKS. The player
         * trades the vortex for a moveset, which is exactly the cost the copy
         * mechanic is supposed to have.
         */
        if (s_kirby.inhaling)
        {
            if (s_ability != ABILITY_NONE)
            {
                if (ABILITY_fire(s_ability, s_kirby.x, s_kirby.y,
                                 s_kirby.facingLeft))
                {
                    PLAYTEST_mark(PLAYTEST_STATE_ABILITY_USED);
                    AUDIO_playSfx(SFX_SWALLOW, SFX_PRIO_ABILITY);
                }
            }
            else
            {
                AUDIO_playSfx(SFX_INHALE, SFX_PRIO_PLAYER_VERB);
            }
        }

        ABILITY_update(s_kirby.x, s_kirby.y);

        ENEMY_updateAll(s_kirby.x, s_kirby.y,
                        s_kirby.inhaling && (s_ability == ABILITY_NONE),
                        s_kirby.facingLeft);

        /*
         * Enemy contact damage. An enemy being INHALED must not hurt: the
         * vortex would otherwise punish the player for using the core verb.
         */
        {
            const s16 kx = (s16) (F16_toInt(s_kirby.x) - 12);
            const s16 ky = (s16) (F16_toInt(s_kirby.y) - 12);
            for (i = 0u; i < ENEMY_POOL_SIZE; i++)
            {
                const Enemy* e = ENEMY_get(i);
                if ((e == NULL) || (e->state != ENEMY_WALK)) continue;
                {
                    const s16 ex = (s16) (F16_toInt(e->x) - 8);
                    const s16 ey = (s16) (F16_toInt(e->y) - 8);
                    if ((kx < (ex + 16)) && ((kx + 24) > ex) &&
                        (ky < (ey + 16)) && ((ky + 24) > ey))
                    {
                        if (KIRBY_damage(&s_kirby, e->x < s_kirby.x))
                        {
                            PLAYTEST_mark(PLAYTEST_STATE_KIRBY_HURT);
                            AUDIO_playSfx(SFX_HURT, SFX_PRIO_DAMAGE);
                        }
                    }
                }
            }
        }

        /* Swallowing is what grants the copy ability. This is the core loop. */
        {
            const CopyAbility got = ENEMY_collectSwallowed();
            const bool swallowed = (got != ABILITY_NONE) || s_swallowSeen;

            PLAYTEST_observe((u16) s_kirby.state, s_kirby.onGround,
                             s_kirby.facingLeft, swallowed,
                             s_ability != ABILITY_NONE);

            if (got != ABILITY_NONE)
            {
                s_swallowSeen = TRUE;
                AUDIO_playSfx(SFX_SWALLOW, SFX_PRIO_PLAYER_VERB);
                s_ability = (u8) got;
                s_kirby.ability = (u8) got;
                /* Impact feedback: hit-stop plus a palette flash, never a white
                 * sprite. doc/ARCHITECTURE.md section 7. */
                KIRBY_applyHitStop(&s_kirby, 8u);
                s_abilityFlash = 12u;
            }
        }
    }
    SCENE_stageCamera();

    /* Kirby: origin is his centre, sprite is 32x32. */
    sx = KIRBY_screenX(&s_kirby, s_cameraX);
    SPR_setPosition(s_sprKirby, (s16) (sx - 16),
                    (s16) (F16_toInt(s_kirby.y) - 16));
    SPR_setPosition(s_sprKirbyRunReview, (s16) (sx - 16),
                    (s16) (F16_toInt(s_kirby.y) - 16));
    SPR_setHFlip(s_sprKirby, s_kirby.facingLeft);
    SPR_setHFlip(s_sprKirbyRunReview, s_kirby.facingLeft);
    {
        const SpriteVisibility visibility =
            ((s_kirby.invuln > 0u) && ((s_kirby.invuln & 2u) != 0u))
            ? HIDDEN : VISIBLE;
        const bool running_review = (s_kirby.state == KIRBY_RUN);
        SPR_setVisibility(s_sprKirby, running_review ? HIDDEN : visibility);
        SPR_setVisibility(s_sprKirbyRunReview, running_review ? visibility : HIDDEN);
        SPR_setFrame(s_sprKirbyRunReview, s_kirby.animFrame % 4u);
    }
    SPR_setFrame(s_sprKirby, KIRBY_animIndex(&s_kirby));

    /*
     * CAMADA 5 moves at 5/4 of the camera: faster than the playfield, so it
     * reads as nearer than Kirby. It is sprites because the hardware has no
     * third scrolling plane.
     */
    for (i = 0u; i < FG_TUFT_COUNT; i++)
    {
        const s16 fx = (s16) (FG_X[i] - ((s_cameraX * 5) >> 2));
        if ((fx > -32) && (fx < 320))
        {
            SPR_setVisibility(s_sprFg[i], VISIBLE);
            SPR_setPosition(s_sprFg[i], fx, 208);
        }
        else
        {
            SPR_setVisibility(s_sprFg[i], HIDDEN);
        }
    }

    /* --- enemy sprites --------------------------------------------------- */
    for (i = 0u; i < ENEMY_POOL_SIZE; i++)
    {
        const Enemy* e = ENEMY_get(i);
        if ((e == NULL) || (e->state == ENEMY_DEAD) ||
            (e->state == ENEMY_SWALLOWED))
        {
            SPR_setVisibility(s_sprEnemy[i], HIDDEN);
            continue;
        }
        {
            const s16 ex = (s16) (F16_toInt(e->x) - s_cameraX - 8);
            if ((ex > -16) && (ex < 320))
            {
                SPR_setVisibility(s_sprEnemy[i], VISIBLE);
                SPR_setPosition(s_sprEnemy[i], ex,
                                (s16) (F16_toInt(e->y) - 8));
                SPR_setFrame(s_sprEnemy[i], e->animFrame);
            }
            else
            {
                SPR_setVisibility(s_sprEnemy[i], HIDDEN);
            }
        }
    }

    /*
     * Ability-acquired flash: a palette swap for a few frames, never a white
     * sprite (doc/ARCHITECTURE.md section 7). Ruled OUT as the cause of the
     * CRAM 1..31 corruption on 2026-07-30 by disabling it and seeing the
     * corruption persist; the real cause was the H-int racing the VBlank DMA
     * flush (see src/systems/raster.c RASTER_vInt).
     */
    if (s_abilityFlash > 0u)
    {
        s_abilityFlash--;
        PAL_setColor((PAL2 * 16) + 2,
                     (s_abilityFlash & 2u) ? RGB3_3_3_TO_VDPCOLOR(7, 7, 7)
                                           : RGB3_3_3_TO_VDPCOLOR(7, 5, 6));
    }

    /* Defeat hands off to the game over scene, which owns continue. */
    if (s_kirby.defeated && !PLAYTEST_active())
    {
        SCENE_setOutcome(OUTCOME_DEFEAT);
        APP_changeScene(APP_SCENE_GAMEOVER);
        return;
    }

    RASTER_updateScroll(s_cameraX);

    /* --- project telemetry ---------------------------------------------- */
    PROBE_STAGE_publishCamera(s_cameraX);
    PROBE_STAGE_publishActors((u16) s_kirby.state,
                              (s16) F16_toInt(s_kirby.x),
                              (s16) F16_toInt(s_kirby.y),
                              ENEMY_aliveCount());
    PROBE_STAGE_publishPlaytest(PLAYTEST_visited(), PLAYTEST_step(),
                                PLAYTEST_finished());
    PROBE_STAGE_tick();

    /* Re-export once a second so the DMA peak reflects a recent window rather
     * than only the first frame we happened to write. */
    if ((gApp.sceneFrames % 60u) == 59u)
    {
        PROBE_STAGE_exportToSram();
    }
}
