#include "project.h"

static s16 Player_abs(s16 value)
{
    return (value < 0) ? -value : value;
}

static fix32 Player_clampFix32(fix32 value, fix32 minValue, fix32 maxValue)
{
    if (value < minValue) return minValue;
    if (value > maxValue) return maxValue;
    return value;
}

static s16 Player_getGround(const GameContext *game, s16 x)
{
    s16 dx;

    switch (game->currentPlanet)
    {
        case PLANET_B612:
            dx = x - 160;
            return 164 + ((dx * dx) >> 10);
        case PLANET_KING:
            return 176;
        case PLANET_ACENDEDOR:
            return 172;
        case PLANET_DESERTO:
            return 178 + ((sinFix16((u16) ((x << 1) + 64)) + 64) >> 6);
        case PLANET_VAIDOSO:
        case PLANET_BEBADO:
        case PLANET_HOMEM_NEG:
        case PLANET_GEOGRAFO:
        case PLANET_SERPENTE:
        case PLANET_JARDIM:
        case PLANET_POCO:
        case PLANET_B612_RETORNO:
        default:
            return 176;
    }
}

bool Player_isNear(const GameContext *game, s16 x, s16 radius)
{
    return (Player_abs(game->player.screenX - x) <= radius);
}

static bool Player_getLandmarkSprite(const GameContext *game, s16 *x, s16 *y, u16 *tile)
{
    switch (game->currentPlanet)
    {
        case PLANET_B612:
            *x = 152;
            *y = 98;
            *tile = PP_TILE_ROSE_MARK;
            return true;

        case PLANET_KING:
            *x = 152;
            *y = 96;
            *tile = PP_TILE_THRONE_MARK;
            return true;

        case PLANET_ACENDEDOR:
            *x = 152;
            *y = 112;
            *tile = PP_TILE_LAMP_MARK;
            return true;

        case PLANET_DESERTO:
            *x = 240;
            *y = 112;
            *tile = PP_TILE_DESERT_MARK;
            return true;

        case PLANET_VAIDOSO:
        case PLANET_BEBADO:
        case PLANET_HOMEM_NEG:
        case PLANET_GEOGRAFO:
        case PLANET_SERPENTE:
        case PLANET_JARDIM:
        case PLANET_POCO:
        case PLANET_B612_RETORNO:
            *x = 160;
            *y = 112;
            *tile = PP_TILE_TRACE;
            return true;

        default:
            return false;
    }
}

static void Player_resetScarf(GameContext *game)
{
    u16 i;
    fix16 baseX = FIX16(game->player.screenX);
    fix16 baseY = FIX16(game->player.screenY + 6);

    for (i = 0; i < PP_SCARF_SEGMENTS; i++)
    {
        game->scarf[i].x = baseX - FIX16((i + 1) * 5);
        game->scarf[i].y = baseY;
        game->scarf[i].phase = i * 88;
        game->scarf[i].damping = FIX16(1);
    }
}

void Player_reset(GameContext *game, PlanetId planet)
{
    s16 startX;

    switch (planet)
    {
        case PLANET_B612: startX = 132; break;
        case PLANET_KING: startX = 92; break;
        case PLANET_ACENDEDOR: startX = 116; break;
        case PLANET_DESERTO: startX = 80; break;
        default: startX = 160; break;
    }

    game->player.x = FIX32(startX);
    game->player.y = FIX32(128);
    game->player.vx = 0;
    game->player.vy = 0;
    game->player.onGround = false;
    game->player.facingLeft = false;
    game->player.gliding = false;
    game->player.interacting = false;
    game->player.screenX = startX;
    game->player.screenY = 128;
    game->player.footY = Player_getGround(game, startX);

    Player_resetScarf(game);
}

void Player_update(GameContext *game, u16 held)
{
    PlayerController *player = &game->player;
    fix16 accel = FIX16(1) / 4;
    fix16 maxSpeed = FIX16(2) + (FIX16(1) / 2);
    fix16 gravity = FIX16(1) / 5;
    fix16 glideGravity = FIX16(1) / 16;
    fix16 jumpSpeed = 0 - (FIX16(4) + (FIX16(1) / 2));
    s16 i;
    fix16 anchorX;
    fix16 anchorY;
    s16 wind = game->windStrength;

    if (held & BUTTON_LEFT)
    {
        player->vx -= accel;
        player->facingLeft = true;
    }
    else if (held & BUTTON_RIGHT)
    {
        player->vx += accel;
        player->facingLeft = false;
    }
    else
    {
        player->vx = (player->vx * 3) >> 2;
    }

    if (player->vx > maxSpeed) player->vx = maxSpeed;
    if (player->vx < 0 - maxSpeed) player->vx = 0 - maxSpeed;

    if ((game->joyPressed & BUTTON_A) && player->onGround)
    {
        player->vy = jumpSpeed;
        player->onGround = false;
    }

    player->gliding = (!player->onGround && (held & BUTTON_A));
    player->vy += player->gliding ? glideGravity : gravity;

    player->x += F16_toFix32(player->vx);
    player->y += F16_toFix32(player->vy);
    player->x = Player_clampFix32(player->x, FIX32(24), FIX32(296));

    player->screenX = F32_toInt(player->x);
    player->screenY = F32_toInt(player->y);
    player->footY = Player_getGround(game, player->screenX);

    if (player->screenY + 24 >= player->footY)
    {
        player->y = FIX32(player->footY - 24);
        player->vy = 0;
        player->onGround = true;
        player->screenY = player->footY - 24;
    }
    else
    {
        player->onGround = false;
    }

    anchorX = FIX16(player->screenX + (player->facingLeft ? 10 : 3));
    anchorY = FIX16(player->screenY + 8);

    for (i = 0; i < PP_SCARF_SEGMENTS; i++)
    {
        fix16 targetX = anchorX + FIX16(player->facingLeft ? ((i + 1) * 6) : -((i + 1) * 6));
        fix16 targetY = anchorY + FIX16(i + (player->gliding ? -1 : 1));
        fix16 wave = sinFix16((game->frameCounter * 18 + game->scarf[i].phase + (i * 40)) & 1023) >> 4;

        targetX -= FIX16(wind * (i + 1)) / 2;
        targetY += wave;

        game->scarf[i].x += (targetX - game->scarf[i].x) / 3;
        game->scarf[i].y += (targetY - game->scarf[i].y) / 3;
    }
}

void Player_hideSprites(void)
{
    u16 index;

    for (index = 0; index + 1 < PP_HW_SPRITES; index++)
    {
        VDP_setSpriteFull(index, -32, -32, SPRITE_SIZE(1, 1), TILE_ATTR_FULL(PAL3, TRUE, FALSE, FALSE, PP_TILE_SCARF), index + 1);
    }

    /* last sprite terminates the link chain */
    VDP_setSpriteFull(PP_HW_SPRITES - 1, -32, -32, SPRITE_SIZE(1, 1), TILE_ATTR_FULL(PAL3, TRUE, FALSE, FALSE, PP_TILE_SCARF), 0);

    VDP_updateSprites(PP_HW_SPRITES, DMA_QUEUE);
}

void Player_render(const GameContext *game)
{
    u16 index;
    u16 bodyAttr = TILE_ATTR_FULL(PAL3, TRUE, FALSE, game->player.facingLeft, PP_TILE_PLAYER);
    s16 markX = -32;
    s16 markY = -32;
    u16 markTile = PP_TILE_ROSE_MARK;
    bool showLandmark = Player_getLandmarkSprite(game, &markX, &markY, &markTile);

    VDP_setSpriteFull(0, game->player.screenX, game->player.screenY, SPRITE_SIZE(2, 3), bodyAttr, 1);

    for (index = 0; index < PP_SCARF_SEGMENTS; index++)
    {
        s16 scarfX = F16_toInt(game->scarf[index].x);
        s16 scarfY = F16_toInt(game->scarf[index].y);
        VDP_setSpriteFull(index + 1, scarfX, scarfY, SPRITE_SIZE(1, 1), TILE_ATTR_FULL(PAL3, TRUE, FALSE, FALSE, PP_TILE_SCARF), index + 2);
    }

    if (game->haloVisible)
    {
        VDP_setSpriteFull(6, game->haloX, game->haloY, SPRITE_SIZE(2, 2), TILE_ATTR_FULL(PAL3, TRUE, FALSE, FALSE, PP_TILE_HALO), 7);
    }
    else
    {
        VDP_setSpriteFull(6, -32, -32, SPRITE_SIZE(2, 2), TILE_ATTR_FULL(PAL3, TRUE, FALSE, FALSE, PP_TILE_HALO), 7);
    }

    VDP_setSpriteFull(7,
        showLandmark ? markX : -32,
        showLandmark ? markY : -32,
        SPRITE_SIZE(2, 2),
        TILE_ATTR_FULL(PAL3, TRUE, FALSE, FALSE, markTile),
        0);

    VDP_updateSprites(PP_HW_SPRITES, DMA_QUEUE);
}
