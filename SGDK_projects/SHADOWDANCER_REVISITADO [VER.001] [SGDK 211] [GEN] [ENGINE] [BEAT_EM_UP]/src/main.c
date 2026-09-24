#include <genesis.h>
#include <resources.h>

#include <map_handler.h>

#define ANIM_STAND 0
#define ANIM_WALK 4

/* Fixed-point gameplay keeps the runtime deterministic. */
#define PLAYER_SPEED FIX32(2)
#define JUMP_VELOCITY FIX32(-6)
#define GRAVITY (FIX32(1) / 5)
#define GRAVITY_MAX FIX32(8)
#define PLAYER_HALF_WIDTH 16
#define PLAYER_TOP_OFFSET 64
#define PLAYER_FOOT_OFFSET 4

#define MAP_COUNT 4
#define START_STAGE 1
#define TILE_CACHE_TILES 576
#define MAP_VRAM_BASE 1

static const u16 mapWidthPixels[MAP_COUNT] = {2048, 2000, 2048, 2560};
static const u16 mapHeightPixels[MAP_COUNT] = {256, 416, 256, 512};
static const MapDefinition *const stageMaps[MAP_COUNT] = {
    &mBigMap0, &mBigMap1, &mBigMap2, &mBigMap3
};
static const TileSet *const stageTilesets[MAP_COUNT] = {
    &tsBigMap0, &tsBigMap1, &tsBigMap2, &tsBigMap3
};
static const Palette *const stagePalettes[MAP_COUNT] = {
    &pBigMap0, &pBigMap1, &pBigMap2, &pBigMap3
};
static const Image *const stageCollisionImages[MAP_COUNT] = {
    &colisao0, &colisao1, &colisao2, &colisao3
};

typedef struct
{
    s8 axisX;
    s8 axisY;
    fix32 velocityX;
    fix32 velocityY;
    fix32 positionX;
    fix32 positionY;
    bool grounded;
    Sprite *sprite;
} PlayerState;

static PlayerState player;
static Map *stageMap;
static TileMap *collisionMap;
static fix32 cameraX;
static fix32 cameraY;
static u8 stageIndex = START_STAGE;
static bool gravityEnabled = TRUE;
static u16 inputState;
static u16 inputPressed;

static s16 fixedToPixel(fix32 value)
{
    return (s16) F32_toInt(value);
}

static u16 collisionAt(s16 pixelX, s16 pixelY)
{
    s16 tileX = (s16) (pixelX >> 3);
    s16 tileY = (s16) (pixelY >> 3);
    u16 mapWidthTiles = (u16) (mapWidthPixels[stageIndex] >> 3);
    u16 mapHeightTiles = (u16) (mapHeightPixels[stageIndex] >> 3);

    if (collisionMap == NULL) return 1;
    if ((tileX < 0) || (tileY < 0) ||
        (tileX >= (s16) mapWidthTiles) || (tileY >= (s16) mapHeightTiles))
        return 1;

    return collisionMap->tilemap[(u16) tileX + ((u16) tileY * mapWidthTiles)];
}

static void inputUpdate(void)
{
    u16 newState = JOY_readJoypad(JOY_1);

    inputPressed = (u16) (newState & (u16) ~inputState);
    inputState = newState;
    player.axisX = 0;
    player.axisY = 0;

    if (inputState & BUTTON_LEFT) player.axisX = -1;
    else if (inputState & BUTTON_RIGHT) player.axisX = 1;
    if (inputState & BUTTON_UP) player.axisY = -1;
    else if (inputState & BUTTON_DOWN) player.axisY = 1;

    if ((inputPressed & (BUTTON_B | BUTTON_C)) && gravityEnabled && player.grounded)
        player.velocityY = JUMP_VELOCITY;
    if (inputPressed & BUTTON_A) gravityEnabled = !gravityEnabled;
}

static void movePlayer(void)
{
    s16 sideX;
    s16 verticalOffset;
    u16 p1;
    u16 p2;
    u16 p3;
    u16 p4;

    if (gravityEnabled)
    {
        if (player.axisX > 0)
        {
            player.velocityX = PLAYER_SPEED;
            SPR_setHFlip(player.sprite, FALSE);
        }
        else if (player.axisX < 0)
        {
            player.velocityX = -PLAYER_SPEED;
            SPR_setHFlip(player.sprite, TRUE);
        }
        else player.velocityX = 0;

        if (player.velocityY < GRAVITY_MAX) player.velocityY += GRAVITY;

        sideX = (player.axisX < 0) ? -PLAYER_HALF_WIDTH : PLAYER_HALF_WIDTH;
        if (collisionAt(fixedToPixel(player.positionX) + sideX + fixedToPixel(player.velocityX),
                        fixedToPixel(player.positionY) - 8) == 1)
            player.velocityX = 0;

        player.positionX += player.velocityX;
        player.positionX = clamp(player.positionX, FIX32(0),
                                 FIX32(mapWidthPixels[stageIndex] - 1));

        verticalOffset = (player.velocityY >= 0) ? 0 : PLAYER_TOP_OFFSET;
        p1 = collisionAt(fixedToPixel(player.positionX) - PLAYER_HALF_WIDTH,
                         fixedToPixel(player.positionY) - verticalOffset);
        p2 = collisionAt(fixedToPixel(player.positionX) + PLAYER_HALF_WIDTH,
                         fixedToPixel(player.positionY) - verticalOffset);
        p3 = collisionAt(fixedToPixel(player.positionX),
                         fixedToPixel(player.positionY) - verticalOffset);
        p4 = collisionAt(fixedToPixel(player.positionX), fixedToPixel(player.positionY));

        if ((fixedToPixel(player.positionY) - verticalOffset > verticalOffset + 8) &&
            (((p1 == 1) && (p3 == 1)) || ((p1 == 2) && (p4 == 2) && (verticalOffset == 0)) ||
             ((p2 == 1) && (p3 == 1)) || ((p2 == 2) && (p4 == 2) && (verticalOffset == 0))))
        {
            player.velocityY = 0;
            if ((verticalOffset == 0) && ((fixedToPixel(player.positionY) % 8) != 0))
                player.positionY -= FIX32(fixedToPixel(player.positionY) % 8);
            if (verticalOffset == 0) player.grounded = TRUE;
        }

        player.positionY += player.velocityY;
        p1 = collisionAt(fixedToPixel(player.positionX) - PLAYER_HALF_WIDTH,
                         fixedToPixel(player.positionY) + PLAYER_FOOT_OFFSET);
        p2 = collisionAt(fixedToPixel(player.positionX) + PLAYER_HALF_WIDTH,
                         fixedToPixel(player.positionY) + PLAYER_FOOT_OFFSET);
        p3 = collisionAt(fixedToPixel(player.positionX),
                         fixedToPixel(player.positionY) + PLAYER_FOOT_OFFSET);

        if (player.velocityY < 0) player.grounded = FALSE;
        else if (((p1 == 0) && (p2 == 0)) || (p3 == 0)) player.grounded = FALSE;
    }
    else
    {
        if (player.axisY > 0) player.positionY += FIX32(4);
        else if (player.axisY < 0) player.positionY -= FIX32(4);
        if (player.axisX > 0) player.positionX += FIX32(4);
        else if (player.axisX < 0) player.positionX -= FIX32(4);
        player.velocityX = 0;
        player.velocityY = 0;
    }

    SPR_setPosition(player.sprite,
                    fixedToPixel(player.positionX - cameraX) - (player.sprite->definition->w >> 1),
                    fixedToPixel(player.positionY - cameraY) - player.sprite->definition->h);
    SPR_setAnim(player.sprite, (player.axisX || player.axisY) ? ANIM_WALK : ANIM_STAND);
}

static void updateCamera(void)
{
    fix32 oldX = cameraX;
    fix32 oldY = cameraY;
    fix32 screenX = player.positionX - cameraX;
    fix32 screenY = player.positionY - cameraY;
    fix32 nextX = cameraX;
    fix32 nextY = cameraY;
    s16 cameraPixelX;
    s16 cameraPixelY;

    if (screenX > FIX32(180)) nextX = player.positionX - FIX32(180);
    else if (screenX < FIX32(140)) nextX = player.positionX - FIX32(140);
    if (screenY > FIX32(140)) nextY = player.positionY - FIX32(140);
    else if (screenY < FIX32(112)) nextY = player.positionY - FIX32(112);

    cameraX = clamp(nextX, FIX32(0), FIX32(mapWidthPixels[stageIndex] - 320));
    cameraY = clamp(nextY, FIX32(0), FIX32(mapHeightPixels[stageIndex] - 224));
    cameraPixelX = fixedToPixel(cameraX);
    cameraPixelY = fixedToPixel(cameraY);

    if ((cameraX != oldX) || (cameraY != oldY))
        MAP_scrollTo(stageMap, cameraPixelX, cameraPixelY);
}

static void showFatalError(const char *message)
{
    VDP_drawText(message, 2, 12);
    while (TRUE) SYS_doVBlankProcess();
}

int main(bool resetType)
{
    u16 vram;

    if (!resetType) SYS_hardReset();
    VDP_setScreenHeight224();
    VDP_setScreenWidth320();
    DMA_setBufferSize(10000);
    DMA_setMaxTransferSize(10000);

    PAL_setPalette(PAL1, stagePalettes[stageIndex]->data, DMA);
    PAL_setPalette(PAL2, playerSpr.palette->data, DMA);

    stageMap = MAP_create(stageMaps[stageIndex], BG_A,
                          TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, 0));
    if (stageMap == NULL) showFatalError("MAP_CREATE_FAILED");

    vram = tileCache_init(MAP_VRAM_BASE, stageTilesets[stageIndex], TILE_CACHE_TILES);
    if (vram == 0xFFFF) showFatalError("TILE_CACHE_FAILED");
    MAP_setDataPatchCallback(stageMap, tileCache_callback);
    collisionMap = stageCollisionImages[stageIndex]->tilemap;

    SPR_init();
    player.positionX = FIX32(128);
    player.positionY = FIX32(112);
    player.velocityX = 0;
    player.velocityY = 0;
    player.grounded = FALSE;
    player.sprite = SPR_addSprite(&playerSpr, fixedToPixel(player.positionX),
                                  fixedToPixel(player.positionY),
                                  TILE_ATTR(PAL2, FALSE, FALSE, FALSE));
    if (player.sprite == NULL) showFatalError("SPRITE_CREATE_FAILED");

    while (TRUE)
    {
        inputUpdate();
        movePlayer();
        updateCamera();
        SPR_update();
        SYS_doVBlankProcess();
    }
}
