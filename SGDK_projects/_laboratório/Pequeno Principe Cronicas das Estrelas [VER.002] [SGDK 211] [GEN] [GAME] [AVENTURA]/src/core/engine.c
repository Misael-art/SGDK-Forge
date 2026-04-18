/* =========================================================================
 * engine.c — Game context, FSM driver, main loop
 * ========================================================================= */

#include "pp2.h"

/* -------------------------------------------------------------------------
 * Global singleton
 * ------------------------------------------------------------------------- */
GameCtx g_ctx;

/* -------------------------------------------------------------------------
 * Forward declarations (state handlers)
 * ------------------------------------------------------------------------- */
static void State_enterBoot(void);
static void State_updateBoot(void);
static void State_drawBoot(void);

static void State_enterTitle(void);
static void State_updateTitle(void);
static void State_drawTitle(void);

static void State_enterIntro(void);
static void State_updateIntro(void);
static void State_drawIntro(void);

static void State_enterPlanet(void);
static void State_updatePlanet(void);
static void State_drawPlanet(void);
static void State_exitPlanet(void);

static void State_enterTravel(void);
static void State_updateTravel(void);
static void State_drawTravel(void);
static void State_exitTravel(void);

static void State_enterPause(void);
static void State_updatePause(void);
static void State_drawPause(void);

static void State_enterCodex(void);
static void State_updateCodex(void);
static void State_drawCodex(void);

static void State_enterCredits(void);
static void State_updateCredits(void);
static void State_drawCredits(void);

/* -------------------------------------------------------------------------
 * Engine_init
 * ------------------------------------------------------------------------- */
void Engine_init(void)
{
    /* Hardware init */
    VDP_setScreenWidth320();
    VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_COLUMN);
    VDP_setPaletteColors(0, (u16 *)palette_black, 64);
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_clearPlane(WINDOW, TRUE);

    /* Window plane: bottom 4 rows for HUD */
    VDP_setWindowVPos(TRUE, PP2_HUD_TILE_ROW);

    /* Sprites off */
    SPR_init();

    /* Zero context */
    memset(&g_ctx, 0, sizeof(GameCtx));
    g_ctx.state              = STATE_BOOT;
    g_ctx.nextState          = STATE_BOOT;
    g_ctx.stateChangePending = FALSE;
    g_ctx.currentPlanet      = PLANET_B612;
    g_ctx.currentBgm         = BGM_NONE;

    /* Sub-system init */
    Input_init();
    VBlank_init();
    Audio_init();
    Effects_init();
    Dialogue_init();
    Codex_init();
    Hud_init();
    Player_init(&g_ctx);
}

/* -------------------------------------------------------------------------
 * Engine_requestState
 * ------------------------------------------------------------------------- */
void Engine_requestState(GameStateId next)
{
    g_ctx.nextState          = next;
    g_ctx.stateChangePending = TRUE;
}

/* -------------------------------------------------------------------------
 * Engine_doTransition — exit current, enter next
 * ------------------------------------------------------------------------- */
static void Engine_doTransition(void)
{
    /* Exit current */
    switch (g_ctx.state)
    {
        case STATE_PLANET:  State_exitPlanet();  break;
        case STATE_TRAVEL:  State_exitTravel();  break;
        default: break;
    }

    g_ctx.state      = g_ctx.nextState;
    g_ctx.stateTimer = 0;
    g_ctx.stateChangePending = FALSE;

    /* Enter next */
    switch (g_ctx.state)
    {
        case STATE_BOOT:    State_enterBoot();    break;
        case STATE_TITLE:   State_enterTitle();   break;
        case STATE_INTRO:   State_enterIntro();   break;
        case STATE_PLANET:  State_enterPlanet();  break;
        case STATE_TRAVEL:  State_enterTravel();  break;
        case STATE_PAUSE:   State_enterPause();   break;
        case STATE_CODEX:   State_enterCodex();   break;
        case STATE_CREDITS: State_enterCredits(); break;
        default: break;
    }
}

/* -------------------------------------------------------------------------
 * Engine_tick — one frame
 * ------------------------------------------------------------------------- */
void Engine_tick(void)
{
    if (g_ctx.stateChangePending)
        Engine_doTransition();

    Input_update();
    Effects_update(&g_ctx);

    /* Update */
    switch (g_ctx.state)
    {
        case STATE_BOOT:    State_updateBoot();    break;
        case STATE_TITLE:   State_updateTitle();   break;
        case STATE_INTRO:   State_updateIntro();   break;
        case STATE_PLANET:  State_updatePlanet();  break;
        case STATE_TRAVEL:  State_updateTravel();  break;
        case STATE_PAUSE:   State_updatePause();   break;
        case STATE_CODEX:   State_updateCodex();   break;
        case STATE_CREDITS: State_updateCredits(); break;
        default: break;
    }

    /* Draw */
    switch (g_ctx.state)
    {
        case STATE_BOOT:    State_drawBoot();    break;
        case STATE_TITLE:   State_drawTitle();   break;
        case STATE_INTRO:   State_drawIntro();   break;
        case STATE_PLANET:  State_drawPlanet();  break;
        case STATE_TRAVEL:  State_drawTravel();  break;
        case STATE_PAUSE:   State_drawPause();   break;
        case STATE_CODEX:   State_drawCodex();   break;
        case STATE_CREDITS: State_drawCredits(); break;
        default: break;
    }

    g_ctx.stateTimer++;
}

/* -------------------------------------------------------------------------
 * Engine_run — main loop (never returns)
 * ------------------------------------------------------------------------- */
void Engine_run(void)
{
    Engine_requestState(STATE_BOOT);

    while (TRUE)
    {
        Engine_tick();
        SYS_doVBlankProcess();
    }
}

/* =========================================================================
 * STATE: BOOT
 * ========================================================================= */
static void State_enterBoot(void)
{
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setPaletteColors(0, (u16 *)palette_black, 64);
    Effects_fadeIn(&g_ctx, 2);
}

static void State_updateBoot(void)
{
    if (g_ctx.stateTimer >= 90)
        Engine_requestState(STATE_TITLE);
}

static void State_drawBoot(void)
{
    /* Splash — draw developer name in center */
    if (g_ctx.stateTimer == 1)
    {
        VDP_drawTextBG(BG_A, "Pequeno Principe", 12, 13);
        VDP_drawTextBG(BG_A, "Cronicas das Estrelas", 10, 15);
        VDP_drawTextBG(BG_A, "VER.002", 17, 17);
    }
}

/* =========================================================================
 * STATE: TITLE
 * ========================================================================= */
static void State_enterTitle(void)
{
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    Audio_playBgm(BGM_TITLE);
    g_ctx.hudDirty = TRUE;
}

static void State_updateTitle(void)
{
    if (g_ctx.joyPressed & (BUTTON_A | BUTTON_C | BUTTON_START))
        Engine_requestState(STATE_INTRO);
}

static void State_drawTitle(void)
{
    Menu_drawTitle(&g_ctx);
}

/* =========================================================================
 * STATE: INTRO
 * ========================================================================= */
static void State_enterIntro(void)
{
    VDP_clearPlane(BG_A, TRUE);
    g_ctx.stateTimer = 0;
}

static void State_updateIntro(void)
{
    if (g_ctx.joyPressed & (BUTTON_A | BUTTON_C | BUTTON_START))
    {
        g_ctx.currentPlanet = PLANET_B612;
        Engine_requestState(STATE_PLANET);
    }
}

static void State_drawIntro(void)
{
    Menu_drawIntro(&g_ctx);
}

/* =========================================================================
 * STATE: PLANET
 * ========================================================================= */
static void State_enterPlanet(void)
{
    const PlanetScene *scene = Planet_getScene(g_ctx.currentPlanet);
    if (!scene) return;

    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    SPR_reset();

    g_ctx.activeFx = scene->fx;
    VBlank_setScrollMode(scene->fx.useLineScroll, scene->fx.useColumnScroll);
    if (scene->fx.useHInt)
        VBlank_enableHInt(scene->fx.hintLine);
    else
        VBlank_disableHInt();

    Hud_setPlanet(g_ctx.currentPlanet);
    g_ctx.hudDirty = TRUE;

    scene->enter(&g_ctx);
    Player_reset(&g_ctx, 80, PP2_PLAYER_GROUND_Y);
}

static void State_updatePlanet(void)
{
    const PlanetScene *scene = Planet_getScene(g_ctx.currentPlanet);
    if (!scene) return;

    /* Pause intercept */
    if (g_ctx.joyPressed & BUTTON_START)
    {
        Engine_requestState(STATE_PAUSE);
        return;
    }

    if (g_ctx.dialogue.active)
    {
        Dialogue_update(&g_ctx);
        Dialogue_handleInput(&g_ctx, g_ctx.joyPressed);
    }
    else
    {
        scene->handleInput(&g_ctx, g_ctx.joyPressed, g_ctx.joyHeld);
        Player_update(&g_ctx, g_ctx.joyHeld);
        Player_updateScarf(&g_ctx);
        scene->update(&g_ctx);
    }

    /* Check if planet solved → go to travel */
    if (g_ctx.planetSolved[g_ctx.currentPlanet] &&
        !g_ctx.dialogue.active &&
        (g_ctx.joyPressed & BUTTON_C))
    {
        if (g_ctx.currentPlanet < PLANET_B612_RET)
        {
            g_ctx.currentTravel = Travel_fromPlanets(g_ctx.currentPlanet,
                                                     (PlanetId)(g_ctx.currentPlanet + 1));
            g_ctx.nextPlanet    = (PlanetId)(g_ctx.currentPlanet + 1);
            Engine_requestState(STATE_TRAVEL);
        }
        else
        {
            Engine_requestState(STATE_CREDITS);
        }
    }
}

static void State_drawPlanet(void)
{
    const PlanetScene *scene = Planet_getScene(g_ctx.currentPlanet);
    if (!scene) return;

    scene->draw(&g_ctx);
    Player_render(&g_ctx);
    Player_renderScarf(&g_ctx);
    Hud_draw(&g_ctx);

    if (g_ctx.dialogue.active)
        Dialogue_draw(&g_ctx);

    Effects_applyShake(&g_ctx);
}

static void State_exitPlanet(void)
{
    const PlanetScene *scene = Planet_getScene(g_ctx.currentPlanet);
    if (scene) scene->exit(&g_ctx);

    Player_hide();
    VBlank_disableHInt();
    SPR_reset();
}

/* =========================================================================
 * STATE: TRAVEL
 * ========================================================================= */
static void State_enterTravel(void)
{
    const TravelScene *scene = Travel_getScene(g_ctx.currentTravel);
    if (!scene) return;

    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    SPR_reset();

    memset(&g_ctx.travel, 0, sizeof(TravelState));
    g_ctx.travel.id = g_ctx.currentTravel;

    Audio_playBgm(BGM_TRAVEL);
    Audio_playSfx(SFX_TRAVEL_LAUNCH);

    scene->enter(&g_ctx);
}

static void State_updateTravel(void)
{
    const TravelScene *scene = Travel_getScene(g_ctx.currentTravel);
    if (!scene) return;

    if (g_ctx.joyPressed & BUTTON_START)
    {
        Engine_requestState(STATE_PAUSE);
        return;
    }

    scene->update(&g_ctx);

    if (g_ctx.travel.complete)
    {
        g_ctx.currentPlanet = g_ctx.nextPlanet;
        Engine_requestState(STATE_PLANET);
    }
}

static void State_drawTravel(void)
{
    const TravelScene *scene = Travel_getScene(g_ctx.currentTravel);
    if (scene) scene->draw(&g_ctx);
}

static void State_exitTravel(void)
{
    const TravelScene *scene = Travel_getScene(g_ctx.currentTravel);
    if (scene) scene->exit(&g_ctx);
    SPR_reset();
}

/* =========================================================================
 * STATE: PAUSE
 * ========================================================================= */
static void State_enterPause(void)
{
    g_ctx.pause.selection = 0;
    g_ctx.pause.active    = TRUE;
}

static void State_updatePause(void)
{
    Menu_handleInput(&g_ctx, g_ctx.joyPressed);
}

static void State_drawPause(void)
{
    Menu_drawPause(&g_ctx);
}

/* =========================================================================
 * STATE: CODEX
 * ========================================================================= */
static void State_enterCodex(void)
{
    g_ctx.codexIndex = 0;
    /* Find first unlocked codex if index 0 isn't unlocked */
    for (u16 i = 0; i < PP2_PLANET_COUNT; i++)
    {
        if (g_ctx.codexUnlocked[i])
        {
            g_ctx.codexIndex = i;
            break;
        }
    }
}

static void State_updateCodex(void)
{
    Codex_handleInput(&g_ctx, g_ctx.joyPressed);
}

static void State_drawCodex(void)
{
    Codex_draw(&g_ctx);
}

/* =========================================================================
 * STATE: CREDITS
 * ========================================================================= */
static void State_enterCredits(void)
{
    VDP_clearPlane(BG_A, TRUE);
    Audio_fadeOutBgm();
    Effects_fadeIn(&g_ctx, 3);
}

static void State_updateCredits(void)
{
    if (g_ctx.stateTimer > 600 || (g_ctx.joyPressed & (BUTTON_A | BUTTON_C | BUTTON_START)))
        Engine_requestState(STATE_TITLE);
}

static void State_drawCredits(void)
{
    Menu_drawCredits(&g_ctx);
}
