#ifndef PP2_TYPES_H
#define PP2_TYPES_H

#include <genesis.h>
#include "constants.h"

/* =========================================================================
 * Pequeno Príncipe VER.002 — Core Types
 * ========================================================================= */

/* -------------------------------------------------------------------------
 * Enumerations
 * ------------------------------------------------------------------------- */

typedef enum
{
    STATE_BOOT = 0,
    STATE_TITLE,
    STATE_INTRO,
    STATE_PLANET,
    STATE_TRAVEL,
    STATE_PAUSE,
    STATE_CODEX,
    STATE_CREDITS,
    STATE_COUNT
} GameStateId;

typedef enum
{
    PLANET_B612 = 0,
    PLANET_REI,
    PLANET_VAIDOSO,
    PLANET_BEBADO,
    PLANET_CONTADOR,
    PLANET_ACENDEDOR,
    PLANET_GEOGRAFO,
    PLANET_SERPENTE,
    PLANET_DESERTO,
    PLANET_JARDIM,
    PLANET_POCO,
    PLANET_B612_RET,
    PLANET_COUNT
} PlanetId;

typedef enum
{
    TRAVEL_A = 0,   /* B-612 → Rei        — CORAGEM */
    TRAVEL_B,       /* Rei → Vaidoso       — DETERMINACAO */
    TRAVEL_C,       /* Vaidoso → Bebado    — HUMILDADE */
    TRAVEL_D,       /* Bebado → Contador   — COMPAIXAO */
    TRAVEL_E,       /* Contador → Acend.   — CONFIANCA */
    TRAVEL_F,       /* Acend. → Geografo   — PERSEVERANCA */
    TRAVEL_G,       /* Geografo → Serpente — CRIATIVIDADE */
    TRAVEL_H,       /* Serpente → Deserto  — ESPERANCA */
    TRAVEL_I,       /* Deserto → Jardim    — AMIZADE */
    TRAVEL_J,       /* Jardim → Poco       — FIDELIDADE */
    TRAVEL_K,       /* Poco → B-612 Ret    — SABEDORIA */
    TRAVEL_COUNT
} TravelId;

typedef enum
{
    BGM_NONE = 0,
    BGM_TITLE,
    BGM_B612,
    BGM_REI,
    BGM_TRAVEL,
    BGM_AMBIENT,
    BGM_COUNT
} BgmId;

typedef enum
{
    SFX_STEP = 0,
    SFX_JUMP,
    SFX_LAND,
    SFX_INTERACT,
    SFX_SOLVE,
    SFX_TRAVEL_LAUNCH,
    SFX_MENU_MOVE,
    SFX_MENU_SELECT,
    SFX_COUNT
} SfxId;

/* -------------------------------------------------------------------------
 * Scene FX Profile
 * ------------------------------------------------------------------------- */

typedef struct
{
    bool    useLineScroll;
    bool    useColumnScroll;
    bool    useHInt;
    bool    usePaletteCycle;
    u16     hintLine;           /* scanline for H-Int palette split */
    u16     palCycleRate;       /* frames between palette cycle steps */
    s16     windStrength;       /* wind for scarf physics */
} FxProfile;

/* -------------------------------------------------------------------------
 * Player
 * ------------------------------------------------------------------------- */

typedef struct
{
    fix32   x, y;
    fix16   vx, vy;
    bool    onGround;
    bool    facingLeft;
    bool    gliding;
    bool    interacting;
    s16     screenX, screenY;
    u16     animFrame;
    u16     animTimer;
    Sprite *spr;
} PlayerCtrl;

/* -------------------------------------------------------------------------
 * Cachecol (Scarf)
 * ------------------------------------------------------------------------- */

typedef struct
{
    fix16   x, y;
    Sprite *spr;
} ScarfSeg;

/* -------------------------------------------------------------------------
 * Dialogue System
 * ------------------------------------------------------------------------- */

#define DIALOGUE_BUF_LINES  4
#define DIALOGUE_BUF_CHARS  41  /* 40 chars + null */

typedef struct
{
    bool        active;
    bool        dirty;
    const char *speaker;
    const char * const *lines;
    u16         lineCount;
    u16         currentLine;
    u16         typewriterPos;
    u16         totalChars;
    u16         timer;
} DialogueState;

/* -------------------------------------------------------------------------
 * Codex
 * ------------------------------------------------------------------------- */

typedef struct
{
    const char *title;
    const char * const *lines;
    u16 lineCount;
} CodexEntry;

/* -------------------------------------------------------------------------
 * Pause Menu
 * ------------------------------------------------------------------------- */

typedef struct
{
    u16 selection;      /* 0=Continuar 1=Codex 2=Sair */
    bool active;
} PauseState;

/* -------------------------------------------------------------------------
 * Travel State
 * ------------------------------------------------------------------------- */

typedef struct
{
    TravelId    id;
    u16         frame;
    u16         phase;          /* 0=intro text, 1=gameplay, 2=outro text */
    bool        complete;
    fix32       playerX, playerY;
    fix16       playerVx, playerVy;
} TravelState;

/* -------------------------------------------------------------------------
 * Screen Effects
 * ------------------------------------------------------------------------- */

typedef struct
{
    s16     shakeX, shakeY;
    u16     shakeDuration;
    u16     shakeTimer;
    u16     shakeAmplitude;

    bool    flashing;
    u16     flashTimer;
    u16     flashDuration;
    u16     flashColor;

    bool    fading;
    s16     fadeLevel;      /* 0=clear, 15=black */
    s16     fadeDir;        /* +1 or -1 */
    u16     fadeTimer;
    u16     fadeSpeed;
} EffectState;

/* -------------------------------------------------------------------------
 * Game Context (global singleton)
 * ------------------------------------------------------------------------- */

struct PlanetScene;
struct TravelScene;

typedef struct GameCtx
{
    /* FSM */
    GameStateId     state;
    GameStateId     nextState;
    bool            stateChangePending;
    u32             frameCounter;
    u16             stateTimer;

    /* Planet */
    PlanetId        currentPlanet;
    PlanetId        nextPlanet;
    TravelId        currentTravel;
    bool            planetSolved[PP2_PLANET_COUNT];
    bool            codexUnlocked[PP2_PLANET_COUNT];
    u16             codexIndex;     /* which entry to display */
    FxProfile       activeFx;

    /* Input */
    u16             joyHeld;
    u16             joyPressed;
    u16             joyReleased;

    /* Camera */
    fix32           cameraX, cameraY;

    /* Player */
    PlayerCtrl      player;
    ScarfSeg        scarf[PP2_SCARF_SEGMENTS];

    /* Scroll buffers (filled by scene, applied by VBlank) */
    s16             hscrollA[PP2_HSCROLL_LINES];
    s16             hscrollB[PP2_HSCROLL_LINES];
    s16             vscrollA[PP2_VSCROLL_COLS];
    s16             vscrollB[PP2_VSCROLL_COLS];

    /* Dialogue */
    DialogueState   dialogue;

    /* Pause */
    PauseState      pause;

    /* Travel */
    TravelState     travel;

    /* Effects */
    EffectState     fx;

    /* HUD */
    bool            hudDirty;

    /* Audio */
    BgmId           currentBgm;

    /* Scene-specific payload (opaque pointer, cast in scene files) */
    void           *sceneData;

} GameCtx;

/* -------------------------------------------------------------------------
 * Scene interface
 * ------------------------------------------------------------------------- */

typedef struct PlanetScene
{
    PlanetId        id;
    const char     *name;
    const char     *subtitle;
    FxProfile       fx;
    void          (*enter)(GameCtx *ctx);
    void          (*update)(GameCtx *ctx);
    void          (*draw)(GameCtx *ctx);
    void          (*exit)(GameCtx *ctx);
    void          (*handleInput)(GameCtx *ctx, u16 pressed, u16 held);
} PlanetScene;

typedef struct TravelScene
{
    TravelId        id;
    const char     *virtue;
    const char     *openingLine1;
    const char     *openingLine2;
    const char     *closingLine1;
    const char     *closingLine2;
    void          (*enter)(GameCtx *ctx);
    void          (*update)(GameCtx *ctx);
    void          (*draw)(GameCtx *ctx);
    void          (*exit)(GameCtx *ctx);
} TravelScene;

#endif /* PP2_TYPES_H */
