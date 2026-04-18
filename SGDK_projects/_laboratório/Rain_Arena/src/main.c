#include <genesis.h>
#include "resources.h"

#define STATE_BASE 0
#define STATE_VARIATION 1
#define STATE_HIT_PAUSE 2
#define STATE_COOLDOWN 3

#define MODE_TITLE 0
#define MODE_PLAY 1
#define MODE_WIN 2
#define MODE_LOSE 3

#define MAX_RAINDROPS 40
#define FLOOR_LEVEL 180
#define TARGET_SCORE 6
#define MAX_MISSES 3
#define ROUND_TIME_FRAMES 1800
#define BASE_DURATION 90
#define VARIATION_DURATION 84
#define HIT_PAUSE_DURATION 4
#define COOLDOWN_DURATION 45
#define FLASH_CYCLE 20
#define FLASH_WINDOW 5

typedef struct
{
    Sprite* spr;
    u16 state;
    u16 splashTimer;
} RainDrop;

static RainDrop raindrops[MAX_RAINDROPS];
static u16 flashPalette[16];
static u16 blackPalette[16];
static u16 skyFlashPalette[16];
static u16 sceneState;
static u16 sceneTimer;
static u16 gameMode;
static u16 score;
static u16 misses;
static u16 timeLeft;
static u16 joyState;
static u16 joyPrev;
static u16 hudModeCache;
static u16 hudStateCache;
static u16 hudScoreCache;
static u16 hudMissesCache;
static u16 hudTimeCache;
static u16 hudWindowCache;
static s16 scrollBX;

static void restoreScenePalettes(void)
{
    PAL_setPalette(PAL0, bg_sky.palette->data, DMA);
    PAL_setPalette(PAL1, bg_temple.palette->data, DMA);
    PAL_setPalette(PAL2, sprite_rain.palette->data, DMA);
}

static void buildEffectPalettes(void)
{
    u16 i;

    for (i = 0; i < 16; i++)
    {
        flashPalette[i] = 0x0EEE;
        blackPalette[i] = 0x0000;
        skyFlashPalette[i] = (i & 1) ? 0x08EE : 0x0EEE;
    }
}

static void resetRainPositions(void)
{
    u16 i;

    for (i = 0; i < MAX_RAINDROPS; i++)
    {
        raindrops[i].state = 0;
        raindrops[i].splashTimer = 0;
        SPR_setPosition(raindrops[i].spr, random() % 320, random() % 224);
        SPR_setFrame(raindrops[i].spr, random() & 1);
    }
}

static void initRain(void)
{
    u16 i;

    for (i = 0; i < MAX_RAINDROPS; i++)
    {
        raindrops[i].spr = SPR_addSprite(&sprite_rain, random() % 320, random() % 224, TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
        raindrops[i].state = 0;
        raindrops[i].splashTimer = 0;
        SPR_setFrame(raindrops[i].spr, random() & 1);
    }
}

static void startRound(void)
{
    score = 0;
    misses = 0;
    timeLeft = ROUND_TIME_FRAMES;
    sceneState = STATE_BASE;
    sceneTimer = 0;
    scrollBX = 0;
    gameMode = MODE_PLAY;
    joyPrev = 0;
    resetRainPositions();
    restoreScenePalettes();
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);
}

static bool isFlashWindowActive(void)
{
    return (sceneState == STATE_VARIATION) && ((sceneTimer % FLASH_CYCLE) < FLASH_WINDOW);
}

static const char* getModeLabel(void)
{
    if (gameMode == MODE_PLAY)
    {
        if (sceneState == STATE_VARIATION)
        {
            return isFlashWindowActive() ? "FLASH" : "READ";
        }

        if (sceneState == STATE_COOLDOWN)
        {
            return "COOL";
        }

        if (sceneState == STATE_HIT_PAUSE)
        {
            return "HOLD";
        }

        return "WAIT";
    }

    if (gameMode == MODE_WIN)
    {
        return "CLEAR";
    }

    if (gameMode == MODE_LOSE)
    {
        return "FAIL";
    }

    return "READY";
}

static void drawHud(void)
{
    char value[8];
    u16 secondsLeft = (timeLeft + 59) / 60;
    u16 flashWindowActive = isFlashWindowActive() ? 1 : 0;

    if ((hudModeCache == gameMode) &&
        (hudStateCache == sceneState) &&
        (hudScoreCache == score) &&
        (hudMissesCache == misses) &&
        (hudTimeCache == secondsLeft) &&
        (hudWindowCache == flashWindowActive))
    {
        return;
    }

    hudModeCache = gameMode;
    hudStateCache = sceneState;
    hudScoreCache = score;
    hudMissesCache = misses;
    hudTimeCache = secondsLeft;
    hudWindowCache = flashWindowActive;

    VDP_setTextPlane(WINDOW);
    VDP_clearTextArea(0, 0, 40, 4);

    VDP_drawText("RAIN ARENA", 1, 0);
    VDP_drawText("S", 18, 0);
    uintToStr(score, value, 1);
    VDP_drawText(value, 20, 0);
    VDP_drawText("/", 21, 0);
    VDP_drawText("6", 22, 0);

    VDP_drawText("M", 25, 0);
    uintToStr(misses, value, 1);
    VDP_drawText(value, 27, 0);
    VDP_drawText("/", 28, 0);
    VDP_drawText("3", 29, 0);

    VDP_drawText("T", 32, 0);
    uintToStr(secondsLeft, value, 1);
    VDP_drawText(value, 34, 0);

    if (gameMode == MODE_TITLE)
    {
        VDP_drawText("APERTE START", 1, 1);
        VDP_drawText("A B C NO FLASH", 1, 2);
        VDP_drawText("6 ACERTOS EM 30S", 1, 3);
        return;
    }

    if (gameMode == MODE_WIN)
    {
        VDP_drawText("OBJETIVO CUMPRIDO", 1, 1);
        VDP_drawText("START REINICIA", 1, 2);
        return;
    }

    if (gameMode == MODE_LOSE)
    {
        VDP_drawText("TEMPESTADE VENCEU", 1, 1);
        VDP_drawText("START REINICIA", 1, 2);
        return;
    }

    VDP_drawText("ESTADO", 1, 1);
    VDP_drawText(getModeLabel(), 8, 1);
    VDP_drawText("JANELA", 1, 2);
    VDP_drawText(flashWindowActive ? "ATIVA" : "FECHADA", 8, 2);
    VDP_drawText("A B C DISPARAM O FLASH", 1, 3);
}

static void updateRainSystem(s16 speedX, s16 speedY)
{
    u16 i;

    for (i = 0; i < MAX_RAINDROPS; i++)
    {
        if (raindrops[i].state == 0)
        {
            s16 y = raindrops[i].spr->y + speedY;
            s16 x = raindrops[i].spr->x + speedX;

            SPR_setFrame(raindrops[i].spr, (y >> 3) & 1);

            if (y >= FLOOR_LEVEL + (random() % 30))
            {
                raindrops[i].state = 1;
                raindrops[i].splashTimer = 0;
                SPR_setFrame(raindrops[i].spr, 2);
            }
            else if (y >= 224)
            {
                y = -32;
                x = random() % 320;
            }

            if (x < -16)
            {
                x += 336;
            }
            else if (x > 320)
            {
                x -= 336;
            }

            SPR_setPosition(raindrops[i].spr, x, y);
        }
        else
        {
            raindrops[i].splashTimer++;

            if (raindrops[i].splashTimer > 3)
            {
                SPR_setFrame(raindrops[i].spr, 3);
            }

            if (raindrops[i].splashTimer > 6)
            {
                raindrops[i].state = 0;
                raindrops[i].splashTimer = 0;
                SPR_setPosition(raindrops[i].spr, random() % 320, -32);
                SPR_setFrame(raindrops[i].spr, 0);
            }
        }
    }
}

static void updateSceneState(void)
{
    if (sceneState == STATE_BASE)
    {
        if (sceneTimer > BASE_DURATION)
        {
            sceneState = STATE_VARIATION;
            sceneTimer = 0;
        }
    }
    else if (sceneState == STATE_VARIATION)
    {
        if (sceneTimer > VARIATION_DURATION)
        {
            sceneState = STATE_COOLDOWN;
            sceneTimer = 0;
            restoreScenePalettes();
        }
    }
    else if (sceneState == STATE_HIT_PAUSE)
    {
        if (sceneTimer > HIT_PAUSE_DURATION)
        {
            sceneState = STATE_COOLDOWN;
            sceneTimer = 0;
            restoreScenePalettes();
            VDP_setVerticalScroll(BG_A, 0);
            VDP_setHorizontalScroll(BG_A, 0);
        }
    }
    else if (sceneState == STATE_COOLDOWN)
    {
        if (sceneTimer > COOLDOWN_DURATION)
        {
            sceneState = STATE_BASE;
            sceneTimer = 0;
            restoreScenePalettes();
            VDP_setVerticalScroll(BG_A, 0);
            VDP_setHorizontalScroll(BG_A, 0);
            VDP_setVerticalScroll(BG_B, 0);
        }
    }
}

static void updateSceneMotion(void)
{
    s16 rainXSpeed = 0;
    s16 rainYSpeed = 8;

    if (sceneState == STATE_HIT_PAUSE)
    {
        PAL_setPalette(PAL0, skyFlashPalette, DMA);
        PAL_setPalette(PAL1, blackPalette, DMA);
        PAL_setPalette(PAL2, flashPalette, DMA);
        return;
    }

    scrollBX--;
    VDP_setHorizontalScroll(BG_B, scrollBX);

    if (sceneState == STATE_VARIATION)
    {
        if (isFlashWindowActive())
        {
            PAL_setPalette(PAL0, skyFlashPalette, DMA);
            PAL_setPalette(PAL2, flashPalette, DMA);
        }
        else
        {
            restoreScenePalettes();
        }

        rainXSpeed = -3;
        rainYSpeed = 9;
        scrollBX -= 2;
        VDP_setHorizontalScroll(BG_B, scrollBX);
    }
    else if (sceneState == STATE_COOLDOWN)
    {
        if (sceneTimer < 15)
        {
            s16 offsetY = (random() % 4) - 2;
            s16 offsetX = (random() % 4) - 2;

            VDP_setVerticalScroll(BG_A, offsetY);
            VDP_setHorizontalScroll(BG_A, offsetX);
            VDP_setVerticalScroll(BG_B, offsetY);
        }
        else
        {
            VDP_setVerticalScroll(BG_A, 0);
            VDP_setHorizontalScroll(BG_A, 0);
            VDP_setVerticalScroll(BG_B, 0);
        }
    }
    else
    {
        restoreScenePalettes();
        VDP_setVerticalScroll(BG_A, 0);
        VDP_setHorizontalScroll(BG_A, 0);
        VDP_setVerticalScroll(BG_B, 0);
    }

    updateRainSystem(rainXSpeed, rainYSpeed);
}

static void updateGameplay(u16 actionPressed, u16 startPressed)
{
    if (gameMode == MODE_TITLE)
    {
        if (startPressed || actionPressed)
        {
            startRound();
        }

        return;
    }

    if (gameMode == MODE_WIN || gameMode == MODE_LOSE)
    {
        if (startPressed)
        {
            startRound();
        }

        return;
    }

    if (actionPressed)
    {
        if (isFlashWindowActive())
        {
            score++;
            sceneState = STATE_HIT_PAUSE;
            sceneTimer = 0;
        }
        else
        {
            if (misses < MAX_MISSES)
            {
                misses++;
            }

            sceneState = STATE_COOLDOWN;
            sceneTimer = 0;
            restoreScenePalettes();
        }
    }

    if (score >= TARGET_SCORE)
    {
        gameMode = MODE_WIN;
        restoreScenePalettes();
        return;
    }

    if (misses >= MAX_MISSES)
    {
        gameMode = MODE_LOSE;
        restoreScenePalettes();
        return;
    }

    if (timeLeft > 0)
    {
        timeLeft--;
    }

    if (timeLeft == 0)
    {
        gameMode = (score >= TARGET_SCORE) ? MODE_WIN : MODE_LOSE;
        restoreScenePalettes();
    }
}

int main(bool hardReset)
{
    u16 actionPressed;
    u16 startPressed;
    u16 tileIndex = 16;

    VDP_init();
    SPR_init();
    buildEffectPalettes();
    restoreScenePalettes();

    VDP_drawImageEx(BG_B, &bg_sky, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, tileIndex), 0, 0, FALSE, TRUE);
    tileIndex += bg_sky.tileset->numTile;
    VDP_drawImageEx(BG_A, &bg_temple, TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, tileIndex), 0, 0, FALSE, TRUE);

    VDP_setWindowOnTop(4);
    VDP_clearPlane(WINDOW, TRUE);
    initRain();

    gameMode = MODE_TITLE;
    sceneState = STATE_BASE;
    sceneTimer = 0;
    score = 0;
    misses = 0;
    timeLeft = ROUND_TIME_FRAMES;
    joyPrev = 0;
    scrollBX = 0;
    hudModeCache = 0xFFFF;
    hudStateCache = 0xFFFF;
    hudScoreCache = 0xFFFF;
    hudMissesCache = 0xFFFF;
    hudTimeCache = 0xFFFF;
    hudWindowCache = 0xFFFF;

    while (TRUE)
    {
        joyState = JOY_readJoypad(JOY_1);
        actionPressed = (joyState & (BUTTON_A | BUTTON_B | BUTTON_C)) && !(joyPrev & (BUTTON_A | BUTTON_B | BUTTON_C));
        startPressed = (joyState & BUTTON_START) && !(joyPrev & BUTTON_START);
        joyPrev = joyState;

        drawHud();
        updateGameplay(actionPressed, startPressed);

        sceneTimer++;
        updateSceneState();
        updateSceneMotion();

        SPR_update();
        SYS_doVBlankProcess();
    }

    return 0;
}
