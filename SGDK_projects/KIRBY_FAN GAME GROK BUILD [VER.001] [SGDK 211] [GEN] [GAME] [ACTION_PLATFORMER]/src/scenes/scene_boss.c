#include <genesis.h>

#include "audio/xgm_router.h"
#include "core/app.h"
#include "entities/boss_whispy.h"
#include "entities/kirby.h"
#include "resources.h"
#include "scenes/scene_boss.h"
#include "scenes/scene_gameover.h"
#include "system/input.h"
#include "system/playtest.h"
#include "system/probe_stage.h"
#include "systems/journey.h"
#include "systems/raster.h"

/*
 * Boss arena. The sprite budget from doc/ARCHITECTURE.md section 5.1 is the
 * whole point of this scene: 28 branch segments + 6 face + 8 apples + Kirby.
 * The trunk is BG_A TILES, not sprites -- that is what keeps the budget legal.
 */

static Boss s_boss;
static Kirby s_kirby;
static Sprite* s_sprSeg[BOSS_SEGMENT_SPRITES];
static Sprite* s_sprApple[BOSS_APPLE_POOL];
static Sprite* s_sprFace;
static Sprite* s_sprKirby;
static u16 s_tileNext;
static u16 s_defeatTimer;

/*
 * R5: the spotlight, and the gameplay rule that justifies it.
 *
 * doc/ARCHITECTURE.md section 4 requires every raster effect to carry a
 * gameplay side effect -- FILOSOFIA MAXIMALISTA. So the spotlight is not decor:
 * WHISPY ONLY TAKES DAMAGE WHILE HE IS LIT. The player has to time the
 * counter-attack to the sweep instead of spamming it.
 *
 * The pool is built from HIGHLIGHT operator sprites (PAL3 index 14). See the
 * generator comment for why it brightens instead of darkening.
 */
/*
 * 3, not 5. The spotlight is what pushed the arena from 92% to 106% CPU, so it
 * pays for itself before the boss gets cut further: the newest feature should
 * fund its own cost, not spend the degradation ladder that exists to protect
 * the boss. Three 32x32 operator sprites still read as a pool of light.
 */
#define BOSS_LIGHT_SPRITES 3
#define BOSS_LIGHT_SWEEP 220        /* half-width of the sweep, px */

static Sprite* s_sprLight[BOSS_LIGHT_SPRITES];
static s16 s_lightX;
static u16 s_lightPhase;
static bool s_bossLit;

/*
 * Contact damage. Everything is AABB against Kirby's 24x24 body box.
 *
 * The branch TIPS are what hurt: a whipping branch reads as a weapon, the base
 * segments read as part of the tree. Only the last two segments of each branch
 * carry a hitbox, and only while the boss is actually lashing (BOSS_WHIP).
 * That is a design rule, not an optimisation -- a branch that hurts while
 * resting would be unreadable.
 */
static bool overlaps(s16 ax, s16 ay, s16 aw, s16 ah,
                     s16 bx, s16 by, s16 bw, s16 bh)
{
    return (ax < (bx + bw)) && ((ax + aw) > bx) &&
           (ay < (by + bh)) && ((ay + ah) > by);
}

void SCENE_bossPlaytestEnter(void)
{
    SCENE_bossEnter();
    PLAYTEST_beginBoss();
}

void SCENE_bossEnter(void)
{
    u16 i;

    SPR_reset();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);

    s_tileNext = TILE_USER_INDEX;

    /* L-011: load absolute masters so layer indices stay on the canonical
     * PAL0/PAL1 slots (rescomp may reorder partial tileset palettes). */
    PAL_setPalette(PAL0, img_pal0_master.palette->data, DMA);
    PAL_setPalette(PAL1, img_pal1_master.palette->data, DMA);
    PAL_setPalette(PAL2, spr_ph_kirby.palette->data, DMA);
    PAL_setPalette(PAL3, img_ph_trunk.palette->data, DMA);

    /*
     * The arena carries the same five-layer contract as the stage. Layers 1-3
     * come from BG_B split by per-scanline HScroll; the trunk and the floor
     * share BG_A. The trunk is drawn AFTER the floor so it owns the rows it
     * occupies.
     */
    VDP_drawImageEx(BG_B, &img_ph_mount,
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, s_tileNext),
                    0, 8, FALSE, TRUE);
    s_tileNext += img_ph_mount.tileset->numTile;

    VDP_drawImageEx(BG_B, &img_ph_hills,
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, s_tileNext),
                    0, 15, FALSE, TRUE);
    s_tileNext += img_ph_hills.tileset->numTile;

    VDP_drawImageEx(BG_A, &img_ph_terrain,
                    TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, s_tileNext),
                    0, 22, FALSE, TRUE);
    s_tileNext += img_ph_terrain.tileset->numTile;

    /* Trunk on BG_A: tiles, zero sprite cost. */
    VDP_drawImageEx(BG_A, &img_ph_trunk,
                    TILE_ATTR_FULL(PAL3, TRUE, FALSE, FALSE, s_tileNext),
                    16, 8, FALSE, TRUE);
    s_tileNext += img_ph_trunk.tileset->numTile;

    RASTER_initStage();
    RASTER_updateScroll(0);

    /*
     * NOTE: with RASTER_initStage() active the H-interrupt drives CRAM 0 as the
     * sky gradient, so this explicit backdrop colour is overwritten every frame.
     * It is kept because it is still correct for any frame before the first
     * H-int fires, and because the reasoning below is the rule for S/H scenes.
     *
     * The backdrop must NOT be left pointing at a transparency key. The first
     * capture showed the whole arena in dark purple: PAL0[0] is the magenta key
     * (255,0,255), and with Shadow/Highlight on an uncovered backdrop renders
     * SHADOWED, i.e. at half brightness -- magenta halved is exactly that purple.
     * Give index 0 a real colour instead. The arena still owes its 4-layer
     * background; this only stops the placeholder from lying about the bug.
     */
    PAL_setColor(0, RGB3_3_3_TO_VDPCOLOR(1, 2, 4));

    VDP_setHilightShadow(TRUE);
    PROBE_STAGE_publishShadowHighlight(TRUE);

    BOSS_init(&s_boss, 160, 96);
    /*
     * MISSAO 2026-08-24: o boss final (Fury) e a mesma arvore com o dobro de
     * vida. Zero arte nova, zero sprite novo; o spotlight R5 continua sendo o
     * verbo de dano. Declarado como placeholder no memory bank ate o loop
     * FASE 2 produzir um boss final autoral.
     */
    if (gJourney.finalBoss && gJourney.bossPending)
    {
        s_boss.hp = BOSS_MAX_HP * 2u;
    }
    KIRBY_init(&s_kirby, FIX16(60), FIX16(150));

    for (i = 0u; i < BOSS_SEGMENT_SPRITES; i++)
    {
        s_sprSeg[i] = SPR_addSprite(&spr_ph_branch, 0, 0,
                                    TILE_ATTR(PAL3, TRUE, FALSE, FALSE));
        SPR_setVisibility(s_sprSeg[i], HIDDEN);
    }
    for (i = 0u; i < BOSS_APPLE_POOL; i++)
    {
        s_sprApple[i] = SPR_addSprite(&spr_ph_apple, 0, 0,
                                      TILE_ATTR(PAL3, TRUE, FALSE, FALSE));
        SPR_setVisibility(s_sprApple[i], HIDDEN);
    }
    for (i = 0u; i < BOSS_LIGHT_SPRITES; i++)
    {
        s_sprLight[i] = SPR_addSprite(&spr_ph_light, 0, 0,
                                      TILE_ATTR(PAL3, TRUE, FALSE, FALSE));
        SPR_setVisibility(s_sprLight[i], HIDDEN);
    }
    s_lightX = 160;
    s_lightPhase = 0u;
    s_bossLit = FALSE;

    s_sprFace = SPR_addSprite(&spr_ph_boss_face, 136, 80,
                              TILE_ATTR(PAL3, TRUE, FALSE, FALSE));
    s_sprKirby = SPR_addSprite(&spr_ph_kirby, 60, 150,
                               TILE_ATTR(PAL2, TRUE, FALSE, FALSE));

    /*
     * PROBE_STAGE_reset() zeroes every published field, so anything published
     * before it is lost. The Shadow/Highlight flag was being set earlier in this
     * function and silently wiped here -- the gate caught it as sh_enabled=0.
     * Publish AFTER the reset.
     */
    s_defeatTimer = 0u;
    AUDIO_playMusic(mus_stage_valley);
    PROBE_STAGE_reset();
    PROBE_STAGE_publishShadowHighlight(TRUE);
    PROBE_STAGE_publishCamera(0);
}

void SCENE_bossUpdate(void)
{
    u16 i, b, s;

    RASTER_frameStart();

    {
        u16 held = gInput.held;
        u16 pressed = gInput.pressed;
        if (PLAYTEST_active()) held = PLAYTEST_poll(&pressed);
        KIRBY_update(&s_kirby, held, pressed);
    }
    BOSS_update(&s_boss, s_kirby.x);

    /* --- contact damage: boss hurts Kirby -------------------------------- */
    {
        const s16 kx = (s16) (F16_toInt(s_kirby.x) - 12);
        const s16 ky = (s16) (F16_toInt(s_kirby.y) - 12);

        /* Branch tips, only while lashing. */
        if (s_boss.phase == BOSS_WHIP)
        {
            for (b = 0u; b < BOSS_BRANCH_COUNT; b++)
            {
                for (s = BOSS_SEGMENTS_PER_BRANCH - 2u;
                     s < BOSS_SEGMENTS_PER_BRANCH; s++)
                {
                    const BossSegment* seg = &s_boss.branch[b].seg[s];
                    if (overlaps(kx, ky, 24, 24,
                                 (s16) (seg->x - 8), (s16) (seg->y - 8), 16, 16))
                    {
                        if (KIRBY_damage(&s_kirby, seg->x < F16_toInt(s_kirby.x)))
                        {
                            PLAYTEST_mark(PLAYTEST_STATE_KIRBY_HURT);
                            AUDIO_playSfx(SFX_HURT, SFX_PRIO_DAMAGE);
                        }
                    }
                }
            }
        }

        /* Falling apples. */
        for (i = 0u; i < BOSS_APPLE_POOL; i++)
        {
            const BossApple* a = &s_boss.apple[i];
            if (!a->active) continue;
            if (overlaps(kx, ky, 24, 24,
                         (s16) (F16_toInt(a->x) - 8),
                         (s16) (F16_toInt(a->y) - 8), 16, 16))
            {
                if (KIRBY_damage(&s_kirby, F16_toInt(a->x) < F16_toInt(s_kirby.x)))
                {
                    PLAYTEST_mark(PLAYTEST_STATE_KIRBY_HURT);
                    AUDIO_playSfx(SFX_HURT, SFX_PRIO_DAMAGE);
                }
            }
        }

        /* --- Kirby hurts the boss: inhale an apple, spit it back ---------- */
        if (s_kirby.inhaling)
        {
            for (i = 0u; i < BOSS_APPLE_POOL; i++)
            {
                BossApple* a = &s_boss.apple[i];
                if (!a->active) continue;
                if (overlaps(kx - 40, ky - 8, 104, 40,
                             (s16) (F16_toInt(a->x) - 8),
                             (s16) (F16_toInt(a->y) - 8), 16, 16))
                {
                    /* Swallowing the apple is what damages Whispy: the player
                     * turns the boss's own projectile against it, which is the
                     * Kirby verb. No sword needed. */
                    a->active = FALSE;
                    /* R5's gameplay side effect: the counter only lands while
                     * Whispy is inside the pool of light. */
                    if (s_bossLit)
                    {
                        BOSS_damage(&s_boss, 1u);
                        PLAYTEST_mark(PLAYTEST_STATE_BOSS_HURT);
                    }
                    AUDIO_playSfx(SFX_SWALLOW, SFX_PRIO_DAMAGE);
                }
            }
        }
    }

    /* --- R5: sweep the pool and decide whether the boss is lit ----------- */
    {
        s16 dx;
        s_lightPhase++;
        /* Triangle sweep across the arena: no trig, no table, just a fold. */
        {
            const s16 t = (s16) (s_lightPhase % (BOSS_LIGHT_SWEEP * 2));
            s_lightX = (s16) (50 + ((t < BOSS_LIGHT_SWEEP)
                                    ? t : (BOSS_LIGHT_SWEEP * 2 - t)));
        }
        dx = (s16) (s_lightX - s_boss.x);
        if (dx < 0) dx = (s16) -dx;
        s_bossLit = (dx < 56);

        for (i = 0u; i < BOSS_LIGHT_SPRITES; i++)
        {
            SPR_setVisibility(s_sprLight[i], VISIBLE);
            SPR_setPosition(s_sprLight[i],
                            (s16) (s_lightX - 48 + (s16) (i * 32)),
                            (s16) (60 + (((i & 1u) != 0u) ? 24 : 0)));
            SPR_setFrame(s_sprLight[i], (u16) ((s_lightPhase >> 4) & 1u));
        }
    }

    i = 0u;
    for (b = 0u; b < BOSS_BRANCH_COUNT; b++)
    {
        for (s = 0u; s < BOSS_SEGMENTS_PER_BRANCH; s++, i++)
        {
            const BossSegment* seg = &s_boss.branch[b].seg[s];
            SPR_setVisibility(s_sprSeg[i], VISIBLE);
            SPR_setPosition(s_sprSeg[i], seg->x - 8, seg->y - 8);
        }
    }

    for (i = 0u; i < BOSS_APPLE_POOL; i++)
    {
        const BossApple* a = &s_boss.apple[i];
        if (!a->active) { SPR_setVisibility(s_sprApple[i], HIDDEN); continue; }
        SPR_setVisibility(s_sprApple[i], VISIBLE);
        SPR_setPosition(s_sprApple[i], (s16) (F16_toInt(a->x) - 8),
                        (s16) (F16_toInt(a->y) - 8));
    }

    SPR_setFrame(s_sprFace, s_boss.faceFrame);
    SPR_setPosition(s_sprKirby, (s16) (F16_toInt(s_kirby.x) - 16),
                    (s16) (F16_toInt(s_kirby.y) - 16));
    SPR_setFrame(s_sprKirby, KIRBY_animIndex(&s_kirby));
    SPR_setHFlip(s_sprKirby, s_kirby.facingLeft);
    /* i-frame blink: 2 frames on, 2 off. Visible feedback that the hit
     * registered and that Kirby is briefly safe. */
    SPR_setVisibility(s_sprKirby,
                      ((s_kirby.invuln > 0u) && ((s_kirby.invuln & 2u) != 0u))
                      ? HIDDEN : VISIBLE);

    /* --- outcome --------------------------------------------------------- */
    if (s_kirby.defeated || (s_boss.phase == BOSS_DEFEATED))
    {
        s_defeatTimer++;
        if (s_boss.phase == BOSS_DEFEATED) PLAYTEST_mark(PLAYTEST_STATE_BOSS_DEAD);

        /*
         * Hold for 2 seconds before handing over so the death or the wilt reads
         * on screen. The playtest scene never transitions: it must stay in the
         * arena for the capture to sample the combat states.
         */
        if ((s_defeatTimer > 120u) && !PLAYTEST_active())
        {
            if (!s_kirby.defeated)
            {
                /* MISSAO 2026-08-24: vitoria. Boss final vai direto para o
                 * ENDING; Whispy passa pelo painel de vitoria do gameover,
                 * que roteia a fase seguinte no continue. */
                if (gJourney.finalBoss && gJourney.bossPending)
                {
                    const AppScene next = JOURNEY_sceneAfterBossVictory();

                    AUDIO_playSfx(SFX_SWALLOW, SFX_PRIO_STATE);
                    RASTER_shutdown();
                    APP_changeScene(next);
                    return;
                }
                SCENE_setOutcome(OUTCOME_VICTORY);
                AUDIO_playSfx(SFX_SWALLOW, SFX_PRIO_STATE);
                RASTER_shutdown();
                APP_changeScene(APP_SCENE_GAMEOVER);
                return;
            }

            SCENE_setOutcome(OUTCOME_DEFEAT);
            RASTER_shutdown();
            APP_changeScene(APP_SCENE_GAMEOVER);
            return;
        }
    }

    PROBE_STAGE_publishActors((u16) s_boss.phase,
                              (s16) F16_toInt(s_kirby.x),
                              (s16) F16_toInt(s_kirby.y),
                              (u16) (s_boss.hp
                                     | (BOSS_activeAppleCount(&s_boss) << 4)
                                     | (s_kirby.health << 8)
                                     | (s_kirby.defeated ? 0x4000u : 0u)
                                     | ((s_boss.phase == BOSS_DEFEATED)
                                        ? 0x8000u : 0u)));
    /*
     * The arena camera is STATIC, so the parallax bands do not move and the
     * parallax_layer_speeds gate will pass VACUOUSLY here and say so. That is
     * correct and deliberate: parallax is proven by the scene 4 capture, where
     * the camera actually pans. Adding fake drift purely to make the gate look
     * non-vacuous would be gaming our own metric.
     */
    RASTER_updateScroll(0);

    PROBE_STAGE_publishCamera(0);
    PROBE_STAGE_publishPlaytest(PLAYTEST_visited(), PLAYTEST_step(),
                                PLAYTEST_finished());
    PROBE_STAGE_tick();
    if ((gApp.sceneFrames % 60u) == 59u) PROBE_STAGE_exportToSram();
}
