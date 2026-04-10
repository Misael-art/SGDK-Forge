/* =========================================================================
 * player.c — Player physics (fix32), animation, cachecol spring chain
 * ========================================================================= */

#include "pp2.h"

/* -------------------------------------------------------------------------
 * Internal state
 * ------------------------------------------------------------------------- */
static s16 s_groundY = PP2_PLAYER_GROUND_Y;

/* -------------------------------------------------------------------------
 * Player_init — one-time init
 * ------------------------------------------------------------------------- */
void Player_init(GameCtx *ctx)
{
    memset(&ctx->player, 0, sizeof(PlayerCtrl));
    memset(ctx->scarf, 0, sizeof(ctx->scarf));

    /* Allocate sprite */
    ctx->player.spr = SPR_addSprite(&spr_player, 0, 0,
        TILE_ATTR(PP2_PAL_PLAYER, TRUE, FALSE, FALSE));

    /* Scarf sprites */
    for (u8 i = 0; i < PP2_SCARF_SEGMENTS; i++)
    {
        ctx->scarf[i].spr = SPR_addSprite(&spr_scarf, 0, 0,
            TILE_ATTR(PP2_PAL_PLAYER, TRUE, FALSE, FALSE));
        SPR_setVisibility(ctx->scarf[i].spr, HIDDEN);
    }
}

/* -------------------------------------------------------------------------
 * Player_reset — called on entering a planet
 * ------------------------------------------------------------------------- */
void Player_reset(GameCtx *ctx, s16 startX, s16 groundY)
{
    s_groundY = groundY;

    ctx->player.x          = FIX32(startX);
    ctx->player.y          = FIX32(groundY - PP2_PLAYER_SPRITE_H * 8);
    ctx->player.vx         = FIX16(0);
    ctx->player.vy         = FIX16(0);
    ctx->player.onGround   = TRUE;
    ctx->player.facingLeft = FALSE;
    ctx->player.gliding    = FALSE;
    ctx->player.interacting = FALSE;
    ctx->player.animFrame  = 0;
    ctx->player.animTimer  = 0;
    ctx->player.screenX    = startX;
    ctx->player.screenY    = groundY - PP2_PLAYER_SPRITE_H * 8;

    /* Init scarf positions */
    for (u8 i = 0; i < PP2_SCARF_SEGMENTS; i++)
    {
        ctx->scarf[i].x = FIX16(startX + 8);
        ctx->scarf[i].y = FIX16(ctx->player.screenY + 4);
    }

    SPR_setVisibility(ctx->player.spr, VISIBLE);
    for (u8 i = 0; i < PP2_SCARF_SEGMENTS; i++)
        SPR_setVisibility(ctx->scarf[i].spr, VISIBLE);
}

/* -------------------------------------------------------------------------
 * Player_update — physics + input
 * ------------------------------------------------------------------------- */
void Player_update(GameCtx *ctx, u16 held)
{
    PlayerCtrl *p = &ctx->player;

    /* Horizontal movement */
    if (held & BUTTON_LEFT)
    {
        p->vx          = FIX16(-fix16ToInt(FIX16(PP2_WALK_SPEED)));
        p->facingLeft  = TRUE;
    }
    else if (held & BUTTON_RIGHT)
    {
        p->vx         = FIX16(fix16ToInt(FIX16(PP2_WALK_SPEED)));
        p->facingLeft = FALSE;
    }
    else
    {
        /* Friction */
        p->vx = fix16Mul(p->vx, FIX16(0.75));
    }

    /* Jump */
    if ((held & BUTTON_C) && p->onGround)
    {
        p->vy        = FIX16(fix32ToInt(PP2_JUMP_FORCE));
        p->onGround  = FALSE;
        Audio_playSfx(SFX_JUMP);
    }

    /* Gravity */
    bool gliding = (held & BUTTON_A) && !p->onGround;
    p->gliding = gliding;

    fix16 gravity = gliding ? FIX16(fix32ToInt(PP2_GRAVITY_GLIDE))
                             : FIX16(fix32ToInt(PP2_GRAVITY));

    p->vy = fix16Add(p->vy, gravity);

    /* Clamp fall speed */
    fix16 maxFall = FIX16(fix32ToInt(PP2_MAX_FALL));
    if (fix16Cmp(p->vy, maxFall) > 0)
        p->vy = maxFall;

    /* Integrate position */
    p->x = fix32Add(p->x, FIX32(fix16ToInt(p->vx)));
    p->y = fix32Add(p->y, FIX32(fix16ToInt(p->vy)));

    /* Ground collision */
    s32 floorY = FIX32(s_groundY - PP2_PLAYER_SPRITE_H * 8);
    if (fix32Cmp(p->y, floorY) >= 0)
    {
        p->y        = floorY;
        p->vy       = FIX16(0);
        p->onGround = TRUE;
    }

    /* Screen bounds (horizontal) */
    if (fix32ToInt(p->x) < 8)
        p->x = FIX32(8);
    if (fix32ToInt(p->x) > PP2_SCREEN_W - PP2_PLAYER_SPRITE_W * 8 - 8)
        p->x = FIX32(PP2_SCREEN_W - PP2_PLAYER_SPRITE_W * 8 - 8);

    /* Update screen coords */
    p->screenX = (s16)fix32ToInt(p->x);
    p->screenY = (s16)fix32ToInt(p->y);

    /* Animation */
    p->animTimer++;
    if (p->onGround)
    {
        if (fix16ToInt(p->vx) != 0)
        {
            /* Walk: 4 frames at 8 fps */
            if (p->animTimer >= 8)
            {
                p->animTimer = 0;
                p->animFrame = (p->animFrame < 3) ? p->animFrame + 1 : 0;
            }
            SPR_setAnim(p->spr, 1);     /* walk animation */
        }
        else
        {
            /* Idle: 2 frames at 30 fps */
            if (p->animTimer >= 30)
            {
                p->animTimer = 0;
                p->animFrame ^= 1;
            }
            SPR_setAnim(p->spr, 0);     /* idle animation */
        }
    }
    else
    {
        SPR_setAnim(p->spr, gliding ? 2 : 3); /* glide or jump */
    }
}

/* -------------------------------------------------------------------------
 * Player_updateScarf — spring chain physics (no float)
 * ------------------------------------------------------------------------- */
void Player_updateScarf(GameCtx *ctx)
{
    PlayerCtrl *p = &ctx->player;
    ScarfSeg   *s = ctx->scarf;
    u32         f = ctx->frameCounter;

    /* Anchor: right side of neck, offset by facing direction */
    s16 anchorX = p->screenX + (p->facingLeft ? 4 : PP2_PLAYER_SPRITE_W * 8 - 4);
    s16 anchorY = p->screenY + 6;

    s[0].x = FIX16(anchorX);
    s[0].y = FIX16(anchorY);

    /* Wind effect from scene */
    fix16 windF = FIX16(ctx->activeFx.windStrength);

    for (u8 i = 1; i < PP2_SCARF_SEGMENTS; i++)
    {
        /* Spring toward previous segment */
        fix16 dx = fix16Sub(s[i-1].x, s[i].x);
        fix16 dy = fix16Sub(s[i-1].y, s[i].y);

        /* Damped spring: multiply by 1/4 (right shift 2) */
        s[i].x = fix16Add(s[i].x, fix16Div(dx, FIX16(4)));
        s[i].y = fix16Add(s[i].y, fix16Div(dy, FIX16(4)));

        /* Wind wave: sinFix16 with phase offset per segment */
        fix16 windOscX = sinFix16((u16)((f * 4) + (i << 4)));
        fix16 windOscY = sinFix16((u16)((f * 3) + (i << 3) + 64));

        /* Scale oscillation by wind strength (small amplitude) */
        windOscX = fix16Mul(windOscX, windF);
        windOscY = fix16Mul(windOscY, FIX16(0.1));

        s[i].x = fix16Add(s[i].x, windOscX);
        s[i].y = fix16Add(s[i].y, windOscY);
    }
}

/* -------------------------------------------------------------------------
 * Player_render
 * ------------------------------------------------------------------------- */
void Player_render(GameCtx *ctx)
{
    PlayerCtrl *p = &ctx->player;
    if (!p->spr) return;

    SPR_setPosition(p->spr, p->screenX, p->screenY);
    SPR_setHFlip(p->spr, p->facingLeft);
}

/* -------------------------------------------------------------------------
 * Player_renderScarf
 * ------------------------------------------------------------------------- */
void Player_renderScarf(GameCtx *ctx)
{
    for (u8 i = 0; i < PP2_SCARF_SEGMENTS; i++)
    {
        if (!ctx->scarf[i].spr) continue;
        SPR_setPosition(ctx->scarf[i].spr,
                        fix16ToInt(ctx->scarf[i].x),
                        fix16ToInt(ctx->scarf[i].y));
    }
}

/* -------------------------------------------------------------------------
 * Player_hide — hide all sprites
 * ------------------------------------------------------------------------- */
void Player_hide(void)
{
    if (g_ctx.player.spr)
        SPR_setVisibility(g_ctx.player.spr, HIDDEN);
    for (u8 i = 0; i < PP2_SCARF_SEGMENTS; i++)
        if (g_ctx.scarf[i].spr)
            SPR_setVisibility(g_ctx.scarf[i].spr, HIDDEN);
}

/* -------------------------------------------------------------------------
 * Player_isNear — proximity check for interaction trigger
 * ------------------------------------------------------------------------- */
bool Player_isNear(const GameCtx *ctx, s16 x, s16 y, s16 radius)
{
    s16 dx = ctx->player.screenX - x;
    s16 dy = ctx->player.screenY - y;
    /* Integer distance² vs radius² (no sqrt needed) */
    return (dx * dx + dy * dy) <= (radius * radius);
}
