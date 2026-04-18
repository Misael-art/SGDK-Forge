#ifndef PP_PROJECT_H
#define PP_PROJECT_H

#include <genesis.h>

#define PP_SCREEN_LINES         224
#define PP_SCREEN_TILES_W       40
#define PP_SCREEN_TILES_H       28
#define PP_VSCROLL_COLUMNS      20
#define PP_SCARF_SEGMENTS       5
#define PP_HW_SPRITES           8

#define PP_SCROLL_LINE          0x0001
#define PP_SCROLL_COLUMN        0x0002
#define PP_HINT_SPLIT           0x0004
#define PP_HILIGHT_MODE         0x0008
#define PP_INTERLEAVED_PLANES   0x0010

#define PP_TILE_BASE                TILE_USER_INDEX
#define PP_TILE_PAPER               (PP_TILE_BASE + 0)
#define PP_TILE_DITHER              (PP_TILE_BASE + 1)
#define PP_TILE_HATCH               (PP_TILE_BASE + 2)
#define PP_TILE_STAR                (PP_TILE_BASE + 3)
#define PP_TILE_GROUND              (PP_TILE_BASE + 4)
#define PP_TILE_GROUND_ALT          (PP_TILE_BASE + 5)
#define PP_TILE_CROWN               (PP_TILE_BASE + 6)
#define PP_TILE_TOWER               (PP_TILE_BASE + 7)
#define PP_TILE_TOWER_WINDOW        (PP_TILE_BASE + 8)
#define PP_TILE_LAMP                (PP_TILE_BASE + 9)
#define PP_TILE_BEACON              (PP_TILE_BASE + 10)
#define PP_TILE_DUNE                (PP_TILE_BASE + 11)
#define PP_TILE_RING                (PP_TILE_BASE + 12)
#define PP_TILE_FILL                (PP_TILE_BASE + 13)
#define PP_TILE_SUN                 (PP_TILE_BASE + 14)
#define PP_TILE_TRACE               (PP_TILE_BASE + 15)
#define PP_TILE_PLAYER              (PP_TILE_BASE + 16)
#define PP_TILE_PLAYER_COUNT        6
#define PP_TILE_SCARF               (PP_TILE_BASE + 22)
#define PP_TILE_HALO                (PP_TILE_BASE + 23)
#define PP_TOTAL_GENERATED_TILES    27
#define PP_TILE_RESOURCE_BASE       (PP_TILE_BASE + PP_TOTAL_GENERATED_TILES)
#define PP_TILE_ROSE_MARK           (PP_TILE_RESOURCE_BASE + 0)
#define PP_TILE_THRONE_MARK         (PP_TILE_RESOURCE_BASE + 4)
#define PP_TILE_LAMP_MARK           (PP_TILE_RESOURCE_BASE + 8)
#define PP_TILE_DESERT_MARK         (PP_TILE_RESOURCE_BASE + 12)
#define PP_TOTAL_RESOURCE_TILES     16

typedef enum
{
    GAME_STATE_BOOT = 0,
    GAME_STATE_TITLE,
    GAME_STATE_STORY,
    GAME_STATE_PLANET,
    GAME_STATE_TRAVEL,
    GAME_STATE_PAUSE,
    GAME_STATE_CODEX,
    GAME_STATE_CREDITS
} GameStateId;

typedef enum
{
    PLANET_B612 = 0,
    PLANET_KING,
    PLANET_VAIDOSO,
    PLANET_BEBADO,
    PLANET_HOMEM_NEG,
    PLANET_ACENDEDOR,
    PLANET_GEOGRAFO,
    PLANET_SERPENTE,
    PLANET_DESERTO,
    PLANET_JARDIM,
    PLANET_POCO,
    PLANET_B612_RETORNO,
    PLANET_COUNT
} PlanetId;

typedef enum
{
    TRAVEL_A = 0,
    TRAVEL_B,
    TRAVEL_C,
    TRAVEL_D,
    TRAVEL_E,
    TRAVEL_F,
    TRAVEL_G,
    TRAVEL_H,
    TRAVEL_I,
    TRAVEL_J,
    TRAVEL_K,
    TRAVEL_COUNT
} TravelId;

typedef struct
{
    u16 flags;
    u16 vramBudgetTiles;
    u16 dmaBudgetBytes;
    u16 hintLine;
    s16 wind;
} FxProfile;

typedef struct
{
    fix32 x;
    fix32 y;
    fix16 vx;
    fix16 vy;
    bool onGround;
    bool facingLeft;
    bool gliding;
    bool interacting;
    s16 screenX;
    s16 screenY;
    s16 footY;
} PlayerController;

typedef struct
{
    fix16 x;
    fix16 y;
    u16 phase;
    fix16 damping;
} ScarfSegment;

struct GameContext;

typedef struct PlanetScene
{
    PlanetId id;
    const char *name;
    const char *subtitle;
    const char *goalPending;
    const char *goalDone;
    const char *effectLine1;
    const char *effectLine2;
    const char *travelHint;
    const char *const *codexLines;
    u16 codexLineCount;
    FxProfile fx;
    void (*enter)(struct GameContext *game);
    void (*handleInput)(struct GameContext *game, u16 pressed, u16 held);
    void (*update)(struct GameContext *game);
    void (*draw)(struct GameContext *game);
    void (*exit)(struct GameContext *game);
} PlanetScene;

typedef struct GameContext
{
    GameStateId currentState;
    GameStateId previousState;
    GameStateId requestedState;
    bool stateChangePending;

    const PlanetScene *activeScene;
    PlanetId currentPlanet;
    PlanetId nextPlanet;
    TravelId currentTravel;

    u32 frameCounter;
    u16 stateTimer;
    u16 sceneTimer;
    u16 joy;
    u16 joyPrev;
    u16 joyPressed;
    u16 joyReleased;

    bool redrawScene;
    bool planetSolved[PLANET_COUNT];
    bool codexUnlocked[PLANET_COUNT];
    u16 codexIndex;
    u16 pauseSelection;
    u16 storyPage;
    bool dialogueActive;
    bool dialogueDirty;
    const char *dialogueSpeaker;
    const char *const *dialogueLines;
    u16 dialogueLineCount;

    bool lampLit;
    s16 windStrength;
    bool haloVisible;
    s16 haloX;
    s16 haloY;

    u16 travelFrame;
    u16 travelPrevRadius;
    u16 travelNextRadius;

    PlayerController player;
    ScarfSegment scarf[PP_SCARF_SEGMENTS];

    s16 hscrollA[PP_SCREEN_LINES];
    s16 hscrollB[PP_SCREEN_LINES];
    s16 vscrollA[PP_VSCROLL_COLUMNS];
    s16 vscrollB[PP_VSCROLL_COLUMNS];
} GameContext;

void Game_init(GameContext *game, bool hardReset);
void Game_update(GameContext *game);
void Game_draw(GameContext *game);
void Game_requestState(GameContext *game, GameStateId nextState);

void States_enter(GameContext *game, GameStateId nextState);
void States_update(GameContext *game);
void States_draw(GameContext *game);
void States_exit(GameContext *game, GameStateId state);

const PlanetScene *Planet_getScene(PlanetId id);

void Player_reset(GameContext *game, PlanetId planet);
void Player_update(GameContext *game, u16 held);
void Player_render(const GameContext *game);
void Player_hideSprites(void);
bool Player_isNear(const GameContext *game, s16 x, s16 radius);

void Dialogue_init(void);
void Dialogue_open(GameContext *game, const char *speaker, const char *const *lines, u16 lineCount);
void Dialogue_close(GameContext *game);
void Dialogue_handleInput(GameContext *game, u16 pressed);
void Dialogue_draw(GameContext *game);

void Audio_init(void);
void Audio_playDialogueVoice(PlanetId planet);
void Audio_playSolveFx(PlanetId planet);

void Render_init(void);
void Render_clearScroll(GameContext *game);
void Render_applyScroll(const GameContext *game);
void Render_clearPlayfield(void);
void Render_beginScene(const u16 *pal0, const u16 *pal1);
void Render_drawSky(u16 baseTile, bool stars, u16 palette);
void Render_drawDisc(VDPPlane plane, s16 cx, s16 cy, s16 radius, u16 fillTile, u16 outlineTile, u16 palette);
void Render_drawTower(s16 x, s16 baseY, s16 height, u16 palette);
void Render_drawLamppost(s16 x, s16 y, bool lit, u16 palette);
void Render_drawBeacon(s16 x, s16 y, u16 palette);
void Render_drawDunes(s16 startY, u16 palette);
void Render_drawPlanetHud(const GameContext *game);
void Render_drawTextScreen(u16 palette, const char *title, const char *const *lines, u16 lineCount, u16 startRow);
void Render_drawPauseScreen(GameContext *game);
void Render_drawCodexScreen(GameContext *game);
void Render_drawCreditsScreen(GameContext *game);
void Render_drawTitleScene(GameContext *game);
void Render_drawStoryScene(GameContext *game, const char *title, const char *const *lines, u16 lineCount);
void Render_drawTravelScene(GameContext *game);

void Travel_update(GameContext *game);
void Travel_draw(const GameContext *game);
TravelId Travel_getFromPlanets(PlanetId from, PlanetId to);

void HintFx_init(void);
void HintFx_disable(void);
void HintFx_configure(const u16 *topColors, const u16 *bottomColors, u16 count, u16 splitLine);
void HintFx_onVBlank(void);

#endif
