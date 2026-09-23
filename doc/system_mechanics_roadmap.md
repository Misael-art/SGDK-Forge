# System Mechanics Roadmap - SGDK Engines Collection

**Tipo**: Logic Vision / Mind Map / Mario World-Style System Dissection
**Profundidade**: 3 Niveis (Design → Variables/Conditions → Execution/Code)
**Escopo**: 8 Engines — NEXZR MD, Mortal Kombat Plus, Goblin SGDK, Vigilante Tutorial, Town Quest, State Machine RPG, Mega Metroid, PlatformerEngine

---

# ══════════════════════════════════════════════════════════════════
# ENGINE 1: NEXZR MD [VER.001] [SGDK 211] [GEN] [GAME] [SHMUP]
# ══════════════════════════════════════════════════════════════════

## ARVORE MESTRA DE SISTEMAS

```
                    ╔════════════════════════════════════════╗
                    ║      NEXZR MD [VER.001] [SHMUP]       ║
                    ║  Vertical Shooter · SGDK 2.11 · 320x240║
                    ╚════════════════════╤═══════════════════╝
                                         │
       ┌──────────────┬─────────────┬────┴──────────┬──────────────┐
       │              │             │               │              │
  ┌────┴────┐  ┌──────┴──────┐ ┌───┴────┐  ┌──────┴──────┐ ┌────┴─────┐
  │  GAME   │  │  ENTITY     │ │ PLAYER │  │ BACKGROUND  │ │  MENU    │
  │  STATE  │  │  MANAGER    │ │ SHIP   │  │  STARFIELD  │ │  & I18N  │
  │  MACHINE│  │  SYSTEM     │ │ SYSTEM │  │  SYSTEM     │ │  SYSTEM  │
  └────┬────┘  └──────┬──────┘ └───┬────┘  └──────┬──────┘ └────┬─────┘
       │              │            │               │             │
    [SEC.1]        [SEC.2]      [SEC.3]         [SEC.4]       [SEC.5]
```

---

### SEC.1: GAME STATE MACHINE

#### Nivel 1 — Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GAME STATE MACHINE                                │
│                                                                     │
│  O jogo progride por telas sequenciais, com um callback de input    │
│  dinamico que muda conforme o estado atual.                         │
│                                                                     │
│  ┌───────┐   ┌───────┐   ┌──────┐   ┌─────────┐                   │
│  │ INTRO │ → │ MENU  │ → │LEVEL │ → │GAME OVER│                   │
│  │(logos)│   │(title)│   │ (1)  │   │ (empty) │                   │
│  │naxat→ │   │START/ │   │ ship │   │         │                   │
│  │intro  │   │OPT/   │   │+stars│   │         │                   │
│  └───────┘   │CARNIVAL│   └──────┘   └─────────┘                   │
│              └───────┘                                              │
└─────────────────────────────────────────────────────────────────────┘
```

#### Nivel 2 — Variables & Conditions

```
┌─ GAME STATE MACHINE ──────────────────────────────────────────────────────────┐
│                                                                                │
│  LEVELS ENUM (game.h:34):                                                      │
│    MENU = 0,  LEVEL_1 = 1                                                      │
│  currentLevel (u8) — tracks which state is active                              │
│                                                                                │
│  DIFFICULTIES ENUM (game.h:22): EASY, NORMAL, HARD                             │
│  game_options_struct: { language(u8), md_mode(bool), difficulty(u8) }           │
│                                                                                │
│  LIVES SYSTEM:                                                                 │
│    game_lives (u8) — starts at 4, max MAX_LIVES(9)                             │
│    Game_loseLive() → game_lives--, show_lives(), if <=0 → Game_over()          │
│    Game_addLive()  → game_lives++ (capped at 9)                                │
│                                                                                │
│  PAUSE SYSTEM:                                                                 │
│    game_paused (bool) — toggled by Game_pause()                                │
│    All entity updates check Game_isPaused() before executing                   │
│                                                                                │
│  INPUT HANDLER (dynamic callback):                                             │
│    currentInputHandler — function pointer, swapped per state:                  │
│      INTRO  → NULL (no input)                                                  │
│      MENU   → joyMenuHandler (menu navigation)                                 │
│      LEVEL_1 → level1_joyEventHandler (START = pause)                          │
│    Game_setJoyHandler(handler) swaps the callback                              │
│                                                                                │
│  FRAME COUNTER:                                                                │
│    currentFrame (u32) — incremented every Game_update()                        │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

#### Nivel 3 — Execution

```
┌─ Game_init() [src/game.c:19] ────────────────────────────────────────────────┐
│  initialize_screen() → 320x240                                               │
│  SPR_init(), JOY_setEventHandler(&_globalJoyEventHandler)                    │
│  currentFrame = 0, I18N_setLanguage(LANG_EN)                                 │
│  game_options = { LANG_EN, md_mode=false, NORMAL }                           │
│  Characters_init() → VDP_loadTileSet(&characters, TILE_FONT_INDEX, DMA)      │
│  Intro_init(&Menu_init) → show naxat(2s) → intro(2s) → Menu_init()          │
│  currentLevel = MENU, game_lives = 4                                         │
└───────────────────────────────────────────────────────────────────────────────┘

┌─ Game_update() [src/game.c:44] — called every frame in while(true) ──────────┐
│  currentFrame++                                                               │
│  Entity_executeAll() → iterates entities[0..entityCount-1], calls func(ctx)  │
│  SPR_update()                                                                 │
│  SYS_doVBlankProcess()                                                        │
└───────────────────────────────────────────────────────────────────────────────┘

┌─ Level1_init() [src/level_1.c:16] ──────────────────────────────────────────┐
│  Background_init() → star warp effect                                        │
│  PLAYER_init(&player) → spawn ship at center-bottom                          │
│  Game_setJoyHandler(level1_joyEventHandler) → START=pause                    │
│  Characters_prepareToPrint(), HUD_init()                                     │
│  Entity_add(NULL, level1_start) → level1_frame++ per tick                    │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

### SEC.2: ENTITY MANAGER SYSTEM

#### Nivel 1 — Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ENTITY MANAGER SYSTEM                             │
│                                                                     │
│  Sistema generico de entidades baseado em callbacks.                 │
│  Qualquer objeto (player, background, level) registra uma           │
│  funcao que sera chamada automaticamente a cada frame.              │
│                                                                     │
│  entities[0] = { ctx=NULL, func=update_background }  ← starfield   │
│  entities[1] = { ctx=&player, func=PLAYER_handleInput } ← ship     │
│  entities[2] = { ctx=NULL, func=level1_start }  ← level tick       │
│                                                                     │
│  Entity_executeAll() → itera e chama func(ctx) para cada ativo     │
└─────────────────────────────────────────────────────────────────────┘
```

#### Nivel 2 — Variables & Conditions

```
┌─ ENTITY MANAGER ──────────────────────────────────────────────────────────────┐
│                                                                                │
│  MAX_ENTITIES = 10                                                             │
│  Entity struct { void* context, Func func, bool active, u8 index }            │
│  Func = typedef void (*Func)(void* context)   [callback.h]                    │
│                                                                                │
│  entities[MAX_ENTITIES] — static array                                         │
│  entityCount (u8) — current count                                              │
│                                                                                │
│  Entity_add(ctx, func) → append to array, return &entity                      │
│  Entity_removeEntity(index) → swap-remove (last element fills gap)            │
│  Entity_removeByContext(ctx) → find by pointer, remove                        │
│  Entity_executeAll() → for 0..entityCount: if active, call func(ctx)          │
│  Entity_search(index, ctx) → find by index OR by context pointer              │
│                                                                                │
│  Pattern: Each subsystem registers itself via Entity_add():                    │
│    Background_init() → Entity_add(NULL, update_background)                    │
│    PLAYER_init()     → Entity_add(&player, PLAYER_handleInput)                │
│    Level1_init()     → Entity_add(NULL, level1_start)                         │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

### SEC.3: PLAYER SHIP SYSTEM

#### Nivel 1 — Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PLAYER SHIP (SLASHER)                             │
│                                                                     │
│  Nave controlada pelo jogador. Move em 4 direcoes com velocidade    │
│  fixa. Animacao de idle/moving com frames manuais.                  │
│                                                                     │
│  ┌───────────────────────────── 320px ────────────────────────────┐ │
│  │                                                               │ │
│  │                                                               │ │
│  │                                                       240px   │ │
│  │                                                               │ │
│  │                    ┌──┐                                       │ │
│  │                    │><│ ← slasher (4x4 tiles = 32x32px)      │ │
│  │                    └──┘   spawn: (144, 176)                   │ │
│  │                                                               │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  D-Pad: x/y += SLASHER_VELOCITY(2)   No screen boundary clamp!   │
└─────────────────────────────────────────────────────────────────────┘
```

#### Nivel 2 — Variables & Conditions

```
┌─ PLAYER SHIP ─────────────────────────────────────────────────────────────────┐
│                                                                                │
│  Player struct { Sprite* sprite, int x, int y, int moveFrame, int frameCtr }  │
│                                                                                │
│  SPAWN:                                                                        │
│    x = (320/2) - 16 = 144                                                     │
│    y = 240 - 64 = 176                                                          │
│                                                                                │
│  ANIMATIONS:                                                                   │
│    SLASHER_IDLE (0) — static frame                                             │
│    SLASHER_MOVING (1) — walking cycle                                          │
│    MOVE_HOLD_FRAME1 (2), MOVE_HOLD_FRAME2 (3) — manual frame loop            │
│    Frame cycling every 5 ticks (++frameCounter >= 5 → next frame)             │
│                                                                                │
│  MOVEMENT:                                                                     │
│    SLASHER_VELOCITY = 2 px/frame                                               │
│    BUTTON_RIGHT → x += 2, HFlip = FALSE, anim = MOVING                       │
│    BUTTON_LEFT  → x -= 2, HFlip = TRUE, anim = MOVING                        │
│    BUTTON_UP    → y -= 2 (independent, no anim change)                         │
│    BUTTON_DOWN  → y += 2 (independent, no anim change)                         │
│    No input     → anim = IDLE, moveFrame = 0                                  │
│                                                                                │
│  PAUSE CHECK: if Game_isPaused() return — no movement while paused            │
│  INPUT MODE: JOY_readJoypad(JOY_1) polled per entity tick (not callback)      │
│  NOTE: No screen boundary clamping (TODO in source code)                       │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

#### Nivel 3 — Execution

```
┌─ PLAYER_init() [src/player.c:13] ───────────────────────────────────────────┐
│  p->x = 144, p->y = 176, moveFrame = 0, frameCounter = 0                    │
│  SPR_addSprite(&slasher, x, y, TILE_ATTR(PAL1,...))                         │
│  SPR_setAnim(sprite, SLASHER_IDLE)                                           │
│  Entity_add(p, PLAYER_handleInput) → registered for per-frame callback      │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ PLAYER_handleInput() [src/player.c:26] — called every frame ───────────────┐
│  if Game_isPaused() → return                                                  │
│  JOY_readJoypad(JOY_1) → direct poll                                         │
│  RIGHT: x += 2, HFlip=FALSE, setAnim(MOVING), frame cycle 5-tick            │
│  LEFT:  x -= 2, HFlip=TRUE, setAnim(MOVING), frame cycle 5-tick             │
│  else:  moveFrame=0, setAnim(IDLE)                                           │
│  UP:    y -= 2 (always, additive with L/R)                                    │
│  DOWN:  y += 2 (always, additive with L/R)                                    │
│  SPR_setPosition(sprite, x, y)                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

### SEC.4: BACKGROUND STARFIELD SYSTEM

#### Nivel 1 — Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                    STARFIELD / WARP EFFECT                           │
│                                                                     │
│  Simula viagem espacial com estrelas caindo verticalmente.          │
│  Inicia com efeito warp (estrelas longas, alta velocidade).         │
│  Apos WARP_DURATION frames, desacelera gradualmente.               │
│  Estrelas piscam aleatoriamente e mudam de tamanho.                 │
│                                                                     │
│  ┌──────────── WARP PHASE ─────────────┐                           │
│  │  *    |    *     |      |     *      │ ← long star trails       │
│  │  |    *    |     *      *     |      │   speed = 3 + size*2     │
│  │  *    |    *     |      |     *      │   230 frames duration    │
│  └──────────── DECEL PHASE ────────────┘                           │
│  │  .    *    .     *      .     *      │ ← shrinking, slowing     │
│  │  *    .    *     .      *     .      │   7-frame decel per star │
│  └──────────── NORMAL PHASE ───────────┘                           │
│  │  .    .    .     .      .     .      │ ← 1x1 sprites, blinking │
│  │  .    .    .     .      .     .      │   speed = 1-2            │
│  └──────────────────────────────────────┘                           │
└─────────────────────────────────────────────────────────────────────┘
```

#### Nivel 2 — Variables & Conditions

```
┌─ STARFIELD SYSTEM ────────────────────────────────────────────────────────────┐
│                                                                                │
│  STAR_COUNT = 20         stars[20] — static array                              │
│  MAX_STAR_HEIGHT = 5     max sprites stacked vertically per star               │
│  WARP_DURATION = 230     frames before deceleration starts                     │
│  DEACELERATION_FRAMES_ANIM = 7   frames between shrink steps                  │
│                                                                                │
│  Star struct:                                                                  │
│    spr[5] — up to 5 stacked 1x1 sprites (8px each)                           │
│    x, y, size(1-5), speed, colorFrame(0-2), done, decelCounter, blinkCounter  │
│                                                                                │
│  INIT: random x(0-319), y(0-223), size(1-5), speed = 3+size*2+rand(0-1)      │
│  Each star = `size` stacked sprites of &star_warp                              │
│                                                                                │
│  PHASES:                                                                       │
│    isWarping=TRUE → full speed, warpTimer++, after 230f → isDeacelerating     │
│    isDeacelerating=TRUE → each star counts down decelCounter                  │
│      when 0: release last sprite, size--, speed = 2+size                       │
│      when size==1: switch to normal anim, speed=rand(1-2), done=TRUE          │
│      when all 20 done → isDeacelerating = FALSE (normal mode)                 │
│    Normal: update every 3rd frame only, blinking via SPR_setVisibility        │
│                                                                                │
│  WRAP: if y > 240 → y = 0, x = random(0-319)                                 │
│  Z-DEPTH: SPR_setZ(spr, SPR_MAX_DEPTH) → always behind ship                  │
│                                                                                │
│  Entity control: backgroundTask = Entity_add(NULL, update_background)         │
│    Background_stop() → active=false, Background_resume() → active=true        │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

### SEC.5: MENU & I18N SYSTEM

#### Nivel 2 — Variables & Conditions

```
┌─ MENU SYSTEM ─────────────────────────────────────────────────────────────────┐
│                                                                                │
│  TWO MENUS (enum menus): MAIN, SECONDARY                                      │
│                                                                                │
│  MAIN MENU (menu_options_main):                                                │
│    GAME_START (0), CARNIVAL_MODE (1), OPTIONS (2)                              │
│    UP/DOWN → navigate option_selected                                         │
│    START on GAME_START → PAL_fadeOut → Level1_init()                           │
│    START on OPTIONS → switch to SECONDARY menu                                │
│                                                                                │
│  SECONDARY MENU (menu_options_secondary):                                      │
│    LANGUAGE (0), MD_MODE (1), DIFFICULTY (2), CREDITS (3), BACK (4)           │
│    START on LANGUAGE → cycle language (EN→PT→ES→EN)                           │
│    START on MD_MODE → toggle md_mode bool                                     │
│    START on BACK → return to MAIN menu                                        │
│                                                                                │
│  I18N SYSTEM:                                                                  │
│    Languages: LANG_EN(0), LANG_PT(1), LANG_ES(2)                             │
│    I18N_setLanguage(lang) → switch on lang, set 11 TXT_* string pointers     │
│    Strings: TXT_START, TXT_OPTIONS, TXT_LANGUAGE, TXT_DIFFICULTY, etc.        │
│    Each language defined in lang_en.h, lang_pt.h, lang_es.h                   │
│                                                                                │
│  CUSTOM FONT RENDERER (Characters):                                            │
│    characters tileset loaded at TILE_FONT_INDEX                               │
│    Characters_print(str, x, y, FONT_ACTIVE|FONT_INACTIVE)                    │
│    A-Z (index 0-25), 0-9 (index 28-37), ! (special)                          │
│    FONT_INACTIVE offset = +47 tiles (dimmed version)                          │
│    Renders on BG_B plane via VDP_setTileMapXY()                               │
│                                                                                │
│  TITLESCREEN:                                                                  │
│    VDP_drawImageEx(BG_B, &titlescreen, ...) → title image on BG_B            │
│    PAL_fadeIn(0, 63, data, 20, FALSE) → smooth entrance                       │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

### TABELA DE CONSTANTES — NEXZR MD

| Constante | Valor | Arquivo | Uso |
|---|---|---|---|
| `GAME_WINDOW_WIDTH` | 320 | `game.h:14` | Largura da tela |
| `GAME_WINDOW_HEIGHT` | 240 | `game.h:15` | Altura da tela |
| `MAX_ENTITIES` | 10 | `entitymanager.h:7` | Limite de entidades |
| `MAX_LIVES` | 9 | `game.h:19` | Vidas maximas |
| `FRAMES_PER_SECOND` | 60 | `game.h:20` | FPS para calculos de timing |
| `SLASHER_VELOCITY` | 2 | `player.c:11` | Velocidade da nave |
| `STAR_COUNT` | 20 | `background.c:6` | Numero de estrelas |
| `MAX_STAR_HEIGHT` | 5 | `background.c:7` | Sprites empilhados por estrela |
| `WARP_DURATION` | 230 | `background.c:8` | Frames de warp antes de desacelerar |
| `DEACELERATION_FRAMES_ANIM` | 7 | `background.c:9` | Frames entre shrink steps |
| `SLASHER_PALLETE` | 1 (PAL1) | `game.h:16` | Paleta do player e fonte |
| `BACKGROUND_PALLETE` | 0 (PAL0) | `game.h:18` | Paleta do background |

### MAPA DE DEPENDENCIAS — NEXZR MD

```
  main.c ──► game.c ──┬─► intro.c ──► utils.c
                       ├─► menu.c ──► level_1.c
                       ├─► player.c
                       ├─► entitymanager.c
                       ├─► background.c
                       ├─► hud.c
                       ├─► characters.c
                       └─► i18n.c ──► lang_en/pt/es.h

  callback.h: typedef void (*Func)(void* context) — core pattern
  resources.res: titlescreen, intro, naxat (IMAGEs)
                 slasher 4x4 (SPRITE), star_warp 1x1 (SPRITE)
                 hud_slasher 2x2 (SPRITE), characters (TILESET)
```

---

# ══════════════════════════════════════════════════════════════════
# ENGINE 2: MORTAL KOMBAT PLUS [VER.001] [SGDK 211] [GEN] [ENGINE] [LUTA]
# ══════════════════════════════════════════════════════════════════

## ARVORE MESTRA

```
              ╔═════════════════════════════════════════╗
              ║   MORTAL KOMBAT PLUS [VER.001] [LUTA]   ║
              ║  Fighting Game · SGDK 2.11 · 320x224    ║
              ╚════════════════╤════════════════════════╝
                               │
      ┌──────────┬─────────────┼──────────────┬──────────────┐
      │          │             │              │              │
  ┌───┴───┐ ┌───┴────┐ ┌─────┴──────┐ ┌────┴─────┐ ┌─────┴────┐
  │ ROOM  │ │ INPUT  │ │  FIGHTER   │ │ CHAR     │ │ VFX &    │
  │ STATE │ │ SYSTEM │ │  SYSTEM    │ │ SELECT   │ │ AUDIO    │
  │ MACHINE│ │ (4-state│ │ (10 chars)│ │ (venetian│ │ (XGM2)   │
  └───┬───┘ │ joypad)│ └─────┬──────┘ │  blinds) │ └──────────┘
      │     └────────┘       │        └──────────┘
   [SEC.1]              [SEC.2]         [SEC.3]
```

### SEC.1: ROOM STATE MACHINE

```
┌─ ROOM STATE MACHINE ─────────────────────────────────────────────────────────┐
│                                                                                │
│  gRoom (u8) — global room/scene index [game_vars.h:17]                        │
│  enum GAME_ROOM { TELA_DEMO_INTRO, TELA_TITULO, TELA_START,                  │
│                   SELECAO_PERSONAGENS, BONUS_STAGE, PALACE_GATES }            │
│                                                                                │
│  FLOW:                                                                         │
│    TELA_DEMO_INTRO → processIntro()                                           │
│      Timed sequence: Brain At Work → Midway → MK Title → Goro Lives → Bio    │
│    TELA_START → processPressStart()                                           │
│      Menu: START / OPTIONS / LANGUAGE                                         │
│    SELECAO_PERSONAGENS → processSelecaoPersonagens()                          │
│      7-character grid, 2 cursors (P1/P2), venetian blind reveal               │
│    BONUS_STAGE → processBonusStage()                                          │
│      "Test Your Might" bonus                                                  │
│    PALACE_GATES → initPalaceGatesRoom()                                      │
│      Fighting arena 928x232px, line scrolling on BG_B                         │
│                                                                                │
│  TRANSITIONS:                                                                  │
│    Intro completes → gRoom = TELA_START                                       │
│    Press START → gRoom = SELECAO_PERSONAGENS                                  │
│    Both selected + 150f countdown → PAL_fadeOutAll → gRoom = TELA_DEMO_INTRO  │
│                                                                                │
│  gFrames (u32) — global frame counter, reset on room change [game_vars.c]     │
│  gFrames == 1 triggers CLEAR_VDP() for fresh room setup                       │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

### SEC.2: FIGHTER / PLAYER SYSTEM

```
┌─ FIGHTER SYSTEM ──────────────────────────────────────────────────────────────┐
│                                                                                │
│  Player struct [estruturas.h:64]:                                              │
│    id (u8) — enum Fighters: JOHNNY_CAGE(0)..REPTILE(9)                        │
│    sprite, paleta (PAL2/PAL3), x, y, w, h, axisX, axisY                      │
│    direcao (s8) — +1 right, -1 left                                           │
│    state (u16) — enum PLAYER_STATUS:                                          │
│      PARADO, ABAIXANDO, ANDAR_FRENTE, ANDAR_TRAS,                            │
│      INI_PULO_TRAS, INI_PULO_NEUTRO, INI_PULO_FRENTE                         │
│    hSpeed — horizontal movement speed                                         │
│    animFrame, animFrameTotal, frameTimeAtual, frameTimeTotal                  │
│    dataAnim[60] — frame counts per state                                      │
│    key_JOY_status[12] — per-button state machine:                             │
│      0=not pressed, 1=just pressed, 2=held, 3=just released                   │
│    key_JOY_countdown[10] — input buffer for combos                            │
│                                                                                │
│  player[2] — global array for P1 and P2                                       │
│  GE[25] — GraphicElement array for misc sprites                               │
│                                                                                │
│  10 FIGHTERS: Separate files per fighter                                       │
│    fighters/johnny.c, kano.c, liukang.c, raiden.c, reptile.c,                │
│    scorpion.c, sonya.c, subzero.c                                             │
│                                                                                │
│  PALACE GATES ARENA:                                                           │
│    928x232 px, BGA + BGB, line scrolling via scrollValues[48]                 │
│    P1 at x=24, P2 at x=168, floor at y=96                                    │
│    gAlturaDoPiso — Y position of ground plane                                 │
│    gBG_Width/gBG_Height — arena dimensions                                    │
│    gScrollValue — horizontal scroll center                                    │
│    gMeioDaTela — camera midpoint between players                              │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

### SEC.3: CHARACTER SELECT (Venetian Blinds VFX)

```
┌─ CHARACTER SELECT SYSTEM ─────────────────────────────────────────────────────┐
│                                                                                │
│  7 CHARACTERS in 2x4 grid:                                                     │
│    OPTIONS_X[7] = {20, 76, 76, 132, 188, 188, 244}                           │
│    OPTIONS_Y[7] = {44, 44, 108, 108, 44, 108, 44}                            │
│    Navigation via switch/case per character ID                                 │
│                                                                                │
│  VENETIAN BLIND EFFECT [revealBackground()]:                                   │
│    7 horizontal bands (persiana[7]), each 32 lines                            │
│    VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_PLANE)                          │
│    scrollLine[224] = -320 (all offscreen)                                     │
│    Progressive reveal: band N starts when band N-1 reaches nextLine           │
│    Each iteration: scrollLine[currentLine] = 0 → 2 lines revealed            │
│    VDP_setHorizontalScrollLine(BG_A/BG_B, line, data, 2, DMA)               │
│                                                                                │
│  SELECTION:                                                                    │
│    cursor sprites (GE[0], GE[1]) — &player_seletor                           │
│    D-pad navigates grid via player[ind].key_JOY_*_status == 1                │
│    START → play character locutor voice via XGM2_playPCMEx()                  │
│    → show B&W portrait blink (GE[ind+2]), visibility = HIDDEN for cursor     │
│    Both selected → 150f countdown → fadeOut → exit to intro                   │
│                                                                                │
│  AUDIO:                                                                        │
│    snd_gongo — gong SFX at reveal start                                       │
│    snd_cursor — cursor move SFX                                               │
│    mus_select_player — BGM via XGM2_play()                                    │
│    loc_jc, loc_kano, etc. — character announcer voices (PCM)                  │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

# ══════════════════════════════════════════════════════════════════
# ENGINE 3: GOBLIN SGDK [VER.001] [SGDK 211] [GEN] [GAME] [AVENTURA]
# ══════════════════════════════════════════════════════════════════

## ARVORE MESTRA

```
              ╔═════════════════════════════════════════════╗
              ║   GOBLIN SGDK [VER.001] [AVENTURA]          ║
              ║  Top-Down RPG · SGDK 2.11 · 256x224         ║
              ╚════════════════════╤════════════════════════╝
                                   │
      ┌──────────┬─────────────┬───┴───────┬──────────────┐
      │          │             │           │              │
  ┌───┴───┐ ┌───┴────┐ ┌─────┴──┐ ┌─────┴──────┐ ┌────┴──────┐
  │ WORLD │ │ BATTLE │ │ CAVE   │ │ MERCHANT   │ │   SAVE    │
  │ MAP   │ │ SYSTEM │ │ DUNGEON│ │ & INVENTORY│ │   SYSTEM  │
  │PROCGEN│ │(random │ │(Cellular│ │ & HOUSE   │ │  (SRAM)   │
  └───┬───┘ │ enctr) │ │Automata)│ └────────────┘ └───────────┘
   [SEC.1]  └────────┘  └────────┘
            [SEC.2]      [SEC.3]      [SEC.4]        [SEC.5]
```

### SEC.1: PROCEDURAL WORLD MAP

```
┌─ PROCEDURAL WORLD ────────────────────────────────────────────────────────────┐
│                                                                                │
│  WORLD_TILES[9][9][14][16] — 9x9 grid of rooms, each 14x16 tiles            │
│  WORLD_LAYOUT_CA[112][128] — cellular automata generated large map            │
│  LEVEL_TILES[14][16] — current room collision data                            │
│                                                                                │
│  makeMap() → generates initial room set                                        │
│  bigMapCA() → cellular automata pass over WORLD_LAYOUT_CA                     │
│  worldSeed — random seed, saved/loaded via SRAM                               │
│                                                                                │
│  currentWorldX, currentWorldY — player's room position in 9x9 grid           │
│  Room transition: edge detection → load adjacent room data                    │
│  displayRoom() — renders current room tiles from LEVEL_TILES                  │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

### SEC.2: RANDOM ENCOUNTER BATTLE SYSTEM

```
┌─ BATTLE SYSTEM ───────────────────────────────────────────────────────────────┐
│                                                                                │
│  TRIGGER: randomEncounter() — called when bIsMoving && canFight               │
│    Random chance each frame while player walks in overworld                   │
│                                                                                │
│  PLAYER STATS:                                                                 │
│    player_hp/hp_max, player_attack, player_defense                            │
│    player_level, player_exp, player_exp_needed, player_gold                   │
│                                                                                │
│  GOBLIN STATS (per encounter):                                                 │
│    goblin_hp, goblin_attack, goblin_defense, goldDrop, experience_gained      │
│    7 goblin types (goblin_sprite1..7) with different sprites                  │
│    nameGenerator() → random goblin name                                       │
│                                                                                │
│  COMBAT FLOW:                                                                  │
│    initBattle() → displayBattle() → turn-based (selection=TRUE/FALSE)         │
│    attack() → player attacks goblin (damage = attack - defense)               │
│    goblinAttack() → goblin attacks player                                     │
│    endBattle() → award gold + exp, itemDrop()                                 │
│    levelUp() → increase stats when exp >= exp_needed                          │
│                                                                                │
│  AUDIO: SFX_SWOOSH (64) — attack sound                                        │
│  Animation: isAnimating, battleAnimationTimer, updateBattleAnimation()        │
│  Death: bPlayerDead → gameOver() → bGameOverScreen + bAwaitingRestartInput    │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

### SEC.3-4: CAVE DUNGEON & MERCHANT/INVENTORY

```
┌─ CAVE DUNGEON (Cellular Automata) ────────────────────────────────────────────┐
│                                                                                │
│  generateCaveLevel() — procedural cave generation                             │
│  enterCave() / exitCave() — transition in/out                                 │
│  inCave flag — toggles VDP_setHilightShadow(0) for dark palette              │
│  updateCaves() — called every frame to check cave entrance collision          │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘

┌─ MERCHANT & INVENTORY ────────────────────────────────────────────────────────┐
│                                                                                │
│  inventory[4][4] — item grid                                                   │
│  8 item types: SKULLS(0), MEAT(1), BONES(2), SKIN(3),                        │
│                EYES(4), FANG(5), HORN(6), TAIL(7)                             │
│  Each item has: name, amount, base_price                                      │
│                                                                                │
│  Merchant: showMerchMenu(), handleMerchantMenuInput()                         │
│  merchantInteractions — limited by MAX_MERCHANT_INTERACTIONS (random 5-15)    │
│  bShowMerchMenu flag → disables movement, shows buy/sell UI                   │
│                                                                                │
│  PLAYER HOUSE: showPlayerHouse()                                               │
│    Hold A to rest → player_hp++ per 750ms until hp_max                        │
│    BUTTON_DOWN exits house                                                     │
│    500ms cooldown after exit (PLAYER_HOUSE_COOLDOWN_MS)                       │
│    bInsideHouse flag → hides player sprite, disables combat                   │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

### SEC.5: SRAM SAVE SYSTEM

```
┌─ SRAM SAVE SYSTEM ────────────────────────────────────────────────────────────┐
│                                                                                │
│  3 SAVE SLOTS, SAVE_SLOT_SIZE = 68 bytes each                                 │
│  Base address = slot * 68                                                      │
│                                                                                │
│  LAYOUT (offset → field):                                                      │
│    +0:  player_hp          +2:  player_hp_max                                 │
│    +4:  player_level       +6:  player_attack                                 │
│    +8:  player_defense     +10: player_exp                                    │
│    +12: player_exp_needed  +14: player_gold                                   │
│    +16: goblinsKilled      +18: skulls                                        │
│    +20: meat               +22: bones                                         │
│    +24: skin               +26: tail                                          │
│    +28: horn               +30: eyes                                          │
│    +32: fang               +34: worldSeed (u32, 4 bytes)                      │
│    +38: player_name[11]    (byte-by-byte)                                     │
│                                                                                │
│  sramSave(slot): SRAM_enable → SRAM_writeWord/Long/Byte → SRAM_disable       │
│  sramLoad(slot): SRAM_enable → SRAM_readWord/Long/Byte → SRAM_disable        │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

# ══════════════════════════════════════════════════════════════════
# ENGINE 4: VIGILANTE TUTORIAL [VER.001] [SGDK 211] [GEN] [ESTUDO] [BRIGA DE RUA]
# ══════════════════════════════════════════════════════════════════

## ARVORE MESTRA

```
              ╔═════════════════════════════════════════════════╗
              ║  VIGILANTE TUTORIAL [VER.001] [BRIGA DE RUA]    ║
              ║  Beat'em Up · SGDK 2.11 · 5 Levels · 320x224   ║
              ╚════════════════════╤════════════════════════════╝
                                   │
      ┌──────────────┬─────────────┼──────────────┐
      │              │             │              │
  ┌───┴────┐  ┌─────┴──────┐ ┌───┴────┐  ┌─────┴──────┐
  │SEQUENCE│  │  PLAYER    │ │ ENEMY  │  │ SPAWN &    │
  │ STATE  │  │  COMBAT    │ │ TYPE   │  │ WAVE       │
  │MACHINE │  │  SYSTEM    │ │ SYSTEM │  │ SYSTEM     │
  └───┬────┘  └─────┬──────┘ └───┬────┘  └─────┬──────┘
   [SEC.1]       [SEC.2]      [SEC.3]        [SEC.4]
```

### SEC.1: SEQUENCE STATE MACHINE

```
┌─ SEQUENCE STATE MACHINE ─────────────────────────────────────────────────────┐
│                                                                                │
│  G_SEQUENCE — global state variable [variables.h:40-45]                       │
│    SEQUENCE_LOGO (0) → SEQUENCE_TITLE (1) → SEQUENCE_RANKING (2)             │
│    → SEQUENCE_INTERMEDE (3) → SEQUENCE_GAME (4) → SEQUENCE_HI_SCORE (5)     │
│                                                                                │
│  G_SEQUENCE_LOADED (bool) — prevents re-init on same sequence                 │
│  G_LEVEL (1-5) — current level number                                         │
│  G_PAUSE — pause flag                                                         │
│                                                                                │
│  PATTERN: Each sequence has init_*() + sequence_*() pair                      │
│    init sets G_SEQUENCE_LOADED = TRUE, loads graphics/audio                   │
│    sequence runs per-frame logic                                              │
│    JOY callback swapped per state via JOY_setEventHandler()                   │
│                                                                                │
│  PER-LEVEL INTERMEDE: init_INTERMEDE_1()..5() + sequence_INTERMEDE_1()..5()  │
│  PER-LEVEL GAMEPLAY: sequence_LEVEL_1()..5()                                 │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

### SEC.2: PLAYER COMBAT SYSTEM

```
┌─ PLAYER COMBAT ───────────────────────────────────────────────────────────────┐
│                                                                                │
│  struct_PLAYER_ [structures.h:21]:                                             │
│    pos_X, pos_Y (s16), axis (bool: RIGHT=0/LEFT=1)                           │
│    state (u8): IDLE(0), WALK(1), CROUCH(2), PUNCH(3), KICK(4),               │
│      PUNCH_CROUCH(5), KICK_CROUCH(6), JUMP_V(7), JUMP_H(8),                 │
│      JUMP_KICK(9), JUMP_KICK_BW(10), HIT_UP(11), HIT_DOWN(12),              │
│      GRAB(14), DEAD(15)                                                       │
│    life (fix32), counter_ANIM_SPRITE, counter_ANIM_H/V                       │
│    pos_X_RESPAWN, counter_UNGRAB, armed, vulnerable, invincible              │
│    spr_PLAYER (Sprite*)                                                       │
│                                                                                │
│  JUMP: struct_JUMP_ { frame, pos_VALUE }                                      │
│    JUMP_HIGH_POINT = 15, JUMP_KICK_COLL_START/END = 11/21                    │
│    JUMP_PUNCH_COLL_START/END = 11/19                                          │
│                                                                                │
│  ATTACK MARGINS: PLAYER_PUNCH_MARGIN = 2, PLAYER_KICK_MARGIN = 4            │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

### SEC.3-4: ENEMY & SPAWN SYSTEM

```
┌─ ENEMY SYSTEM ────────────────────────────────────────────────────────────────┐
│                                                                                │
│  struct_ENEMY_ [structures.h:65]:                                              │
│    enemy_ID, pos_X, pos_Y, width, state, axis, life, points                  │
│    counter_ANIM, index_ANIM, index_FRAME, spr_ENEMY, vulnerable              │
│                                                                                │
│  struct_ENEMY_TYPE [structures.h:97]:                                          │
│    6 types: DUDE, PUNK, KNIFE_MAN, CHAIN_MAN, GUN_MAN, STICK_MAN            │
│    Each: life, width, pal, points, tiles_SPRITE, damages(fix32), vulnerable  │
│                                                                                │
│  SPAWN SYSTEM:                                                                 │
│    struct_SPAWN_DATA_ { enemy_ID, spawn_TIME, special }                       │
│    TABLE_SPAWN_LEVEL_1[72] — 8 waves x 9 enemies per wave                   │
│    Timed spawn: when gFrames >= spawn_TIME → create enemy                    │
│                                                                                │
│  RANKING: struct_RANK_ { score(u16), letter_1/2/3 }                          │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

# ══════════════════════════════════════════════════════════════════
# ENGINE 5: TOWN QUEST [VER.001] [SGDK 211] [GEN] [GAME] [RPG]
# ══════════════════════════════════════════════════════════════════

## ARVORE MESTRA

```
              ╔═════════════════════════════════════════╗
              ║   TOWN QUEST [VER.001] [RPG]            ║
              ║  Action Mini-Game · SGDK 2.11 · 320x224 ║
              ╚════════════════╤════════════════════════╝
                               │
      ┌────────────┬───────────┴──────────┬──────────────┐
      │            │                      │              │
  ┌───┴────┐  ┌───┴──────┐  ┌───────────┴──┐  ┌───────┴─────┐
  │ STAGE  │  │ PLAYER   │  │  ENEMY &     │  │ COLLISION   │
  │ STATE  │  │ "VARAZO" │  │  PERSON      │  │ & SCORE     │
  │ MACHINE│  │ SYSTEM   │  │  SPAWNER     │  │ SYSTEM      │
  └────────┘  └──────────┘  └──────────────┘  └─────────────┘
```

### SISTEMA COMPLETO

```
┌─ TOWN QUEST SYSTEMS ─────────────────────────────────────────────────────────┐
│                                                                                │
│  STAGE STATE MACHINE:                                                          │
│    current_stage: 0=vara(splash), 1=titulo, 2-9=gameplay, 10=game_over        │
│    loaded_stage tracks previous state — change triggers init_stage()           │
│    Stage 0→1 at frame 400, Stage 1→2 at frame 600 (auto-advance)             │
│    Victory: all enemies disabled → change_stage = frame + STAGE_DELAY(300)    │
│                                                                                │
│  PLAYER "VARAZO" SYSTEM:                                                       │
│    struct player { x, y, lifes, score, player_sprite, end_varazo_frame, ... } │
│    PLAYER_SPEED = 5 px/frame, INITIAL_LIFES = 3                               │
│    L/R movement only (no vertical), A/B/C = attack ("varazo")                 │
│    VARAZO_DURATION = 15 frames — attack animation lock                        │
│    GRACE_PERIOD = 30 frames — invulnerability after hit                       │
│    Animations: ANIM_VARA(0), RIGHT(1), LEFT(2), FAIL(3), VICTORY(4), IDLE(5)│
│                                                                                │
│  ENEMY & PERSON SPAWNER:                                                       │
│    ENEMY_SIZE = 10, PERSON_SIZE = 10 (max concurrent)                         │
│    Enemies: fall from above (y += vy=1), random x, re-randomized on reset    │
│    Persons: innocents — hitting them costs a life                             │
│    On hit enemy: SPR_setAnim → transformed sprite, end_transform timer        │
│    TRANSFORMATION_DURATION — enemy shows transformed state then disables      │
│                                                                                │
│  COLLISION:                                                                    │
│    check_collision(): abs(player.x - enemy.x) < 30 && abs(y-y) < 30         │
│    Hit enemy → disable, play SFX_HIT, show transform                         │
│    Hit person → ANIM_FAIL, lose life (with grace period)                      │
│    SFX: SFX_START(start.wav), SFX_FAIL(fallo.wav), SFX_HIT(hit.wav)         │
│    BGM: XGM_startPlay(fondo1) — per level                                    │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

# ══════════════════════════════════════════════════════════════════
# ENGINE 6: STATE MACHINE RPG [VER.001] [SGDK 211] [GEN] [ENGINE] [RPG]
# ══════════════════════════════════════════════════════════════════

## ARVORE MESTRA

```
              ╔═══════════════════════════════════════════╗
              ║   STATE MACHINE RPG [VER.001] [RPG]       ║
              ║  Top-Down Action RPG · Single File Engine  ║
              ║  SGDK 2.11 · 480x448 world · 320x224 view ║
              ╚════════════════╤══════════════════════════╝
                               │
       ┌───────────────┬───────┴──────────┬──────────────┐
       │               │                  │              │
  ┌────┴────┐  ┌──────┴──────┐  ┌───────┴───────┐ ┌───┴─────┐
  │ PLAYER  │  │ COLLISION   │  │   CAMERA      │ │  ATTACK │
  │ 4-DIR   │  │ 1D ARRAY    │  │   CLAMPED     │ │  SWING  │
  │MOVEMENT │  │ TILE MAP    │  │   FOLLOW      │ │  SYSTEM │
  └─────────┘  └─────────────┘  └───────────────┘ └─────────┘
```

### SISTEMA COMPLETO

```
┌─ STATE MACHINE RPG — ALL SYSTEMS ─────────────────────────────────────────────┐
│                                                                                │
│  SINGLE FILE ENGINE: Everything in main.c (~263 lines)                        │
│                                                                                │
│  ┌─ WORLD MAP ───────────────────────────────────────────────────────────────┐ │
│  │  level[3360] (u32 array) — 60 columns x 56 rows = 480x448 px             │ │
│  │  Tile value: 6959 = solid wall, 0 = free space                            │ │
│  │  Tile size: 8x8 px (bitshift >>3 for conversion)                          │ │
│  │  Map created via MAP_create(&l_m, BG_A, ...) + VDP_loadTileSet            │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌─ ENTITY ──────────────────────────────────────────────────────────────────┐ │
│  │  Entity struct: { x, y, w(24), h(24), sentx, senty, health,              │ │
│  │                   sent_anim(enum step), sprite, name[6] }                 │ │
│  │  enum step: down(0), right(1), top(2), left(3)                            │ │
│  │  vel = 2 px/frame, swinging(bool), moving(bool)                           │ │
│  │  Spawn: x=160, y=112 (center of initial view)                            │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌─ MOVEMENT & INPUT ────────────────────────────────────────────────────────┐ │
│  │  FUNCAO_INPUT_SYSTEM() — polls JOY_readJoypad(JOY_1)                      │ │
│  │  Sets 12 boolean flags: JOY1_UP..JOY1_MODE                               │ │
│  │  positionPlayer():                                                        │ │
│  │    if !swinging:                                                          │ │
│  │      if JOY1_A → swinging=TRUE, attack anim (4-7 based on direction)     │ │
│  │      else: D-pad → set sentx/senty = ±vel, sent_anim = direction         │ │
│  │      No input → sentx=senty=0, timer=0 (stop walk anim)                  │ │
│  │      Moving → timer=4 (walk anim speed)                                   │ │
│  │    if swinging: wait 8 frames of last animation frame → reset             │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌─ COLLISION ───────────────────────────────────────────────────────────────┐ │
│  │  checkCollision(x, y):                                                    │ │
│  │    Convert px→tile: y_tile = y>>3, x_tile = x>>3                         │ │
│  │    leftTile = x_tile, rightTile = x_tile + (w>>3)                         │ │
│  │    topTile = y_tile, bottomTile = y_tile + (h>>3)                         │ │
│  │    For each tile in bounds: if level[j*60 + i] == 6959 → TRUE            │ │
│  │                                                                           │ │
│  │  COLLISION RESOLUTION (axis-separated):                                    │ │
│  │    First try full movement → if blocked:                                  │ │
│  │    Try X-axis pixel-by-pixel → advance until collision                    │ │
│  │    Try Y-axis pixel-by-pixel → advance until collision                    │ │
│  │    Clamp: x=[0, 480-w], y=[0, 448-h]                                     │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌─ CAMERA ──────────────────────────────────────────────────────────────────┐ │
│  │  setCameraPosition(x, y):                                                 │ │
│  │    camPosX = x - 160, camPosY = y - 112 (center player)                  │ │
│  │    clamp(camPosX, 0, 160) — (60cols-40screen)*8 = 160                    │ │
│  │    clamp(camPosY, 0, 224) — (56rows-28screen)*8 = 224                    │ │
│  │    SPR_setPosition(sprite, x-camPosX, y-camPosY)                         │ │
│  │    MAP_scrollTo(map, camPosX, camPosY)                                    │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  RESOURCES:                                                                    │
│    SPRITE hero "sprites/hero.png" 4 4 NONE 8  (32x32 px, 8 animations)       │
│    TILESET l_tileset "tiles/state1.png" NONE                                  │
│    MAP l_m "tiles/state1.png" l_tileset NONE                                  │
│    PALETTE pal_map "tiles/state1.png"                                         │
│    PAL0 = map tiles, PAL1 = hero sprite                                       │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

# ══════════════════════════════════════════════════════════════════
# ENGINE 7: MEGA METROID [VER.001] [SGDK 211] [GEN] [GAME] [PLATAFORMA]
# ══════════════════════════════════════════════════════════════════

## ARVORE MESTRA DE SISTEMAS

```
                    ╔═══════════════════════════════════════════════╗
                    ║   MEGA METROID [VER.001] [PLATAFORMA]         ║
                    ║  Metroidvania · SGDK 2.11 · 256x224 · 8px    ║
                    ╚═══════════════════════╤═══════════════════════╝
                                            │
          ┌──────────────┬──────────────┬───┴────────────┬──────────────┐
          │              │              │                │              │
   ┌──────┴──────┐ ┌────┴─────┐ ┌─────┴──────┐  ┌─────┴──────┐ ┌────┴─────┐
   │  PLAYER     │ │ COLLISION│ │   CAMERA    │  │   LEVEL    │ │  ENTITY  │
   │  MOVEMENT   │ │ & SLOPE  │ │   CENTER    │  │   LOADER   │ │  SYSTEM  │
   │  & GRAVITY  │ │ SYSTEM   │ │   FOLLOW    │  │   & DEFS   │ │  (BASE)  │
   └──────┬──────┘ └────┬─────┘ └─────┬──────┘  └─────┬──────┘ └────┬─────┘
          │              │             │                │             │
       [SEC.1]        [SEC.2]       [SEC.3]          [SEC.4]       [SEC.5]
```

---

### SEC.1: PLAYER MOVEMENT & GRAVITY

#### Nivel 1 — Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PLAYER MOVEMENT & GRAVITY                        │
│                                                                     │
│  Samus se movimenta em 4 direcoes com velocidade fixa.             │
│  A gravidade puxa constantemente para baixo com limite maximo.      │
│  O pulo e iniciado apenas quando no chao (is_on_floor).            │
│  Animacoes refletem 3 estados: parada, andando, pulando.           │
│                                                                     │
│  ┌─────────┐         ┌─────────┐         ┌─────────┐              │
│  │  STAND  │ ──D-Pad→│  WALK   │ ──Jump─→│  JUMP   │              │
│  │ (idle)  │ ←──────│(moving) │ ←──land─│ (air)   │              │
│  └─────────┘  no vel └─────────┘         └─────────┘              │
│       │                   │                   │                     │
│  ANIM_STAND(0)      ANIM_WALK(1)        ANIM_JUMP(2)              │
│                     + HFlip dir          + HFlip dir               │
│                                          + SFX jump                │
└─────────────────────────────────────────────────────────────────────┘
```

#### Nivel 2 — Variables/Conditions

```
┌─────────────────────────────────────────────────────────────────────┐
│  MOVEMENT VARIABLES                                                 │
│                                                                     │
│  control.d_pad.x  →  {-1, 0, +1}   Set by JOY_setEventHandler     │
│  control.d_pad.y  →  {-1, 0, +1}   (D-pad up/down/left/right)     │
│                                                                     │
│  player.velocity.x = FIX16(2.3)    if d_pad.x > 0                 │
│  player.velocity.x = FIX16(-2.3)   if d_pad.x < 0                 │
│  player.velocity.x = 0             if d_pad.x == 0                 │
│                                                                     │
│  GRAVITY:                                                           │
│    GRAVITY = FIX16(0.22)           Per frame increment              │
│    GRAVITY_MAX = 300               Terminal velocity (fix16 units)  │
│    JUMP = FIX16(6.6)              Initial jump impulse             │
│                                                                     │
│  JUMP CONDITION:                                                    │
│    BUTTON_C pressed && player.is_on_floor == TRUE                  │
│    → player.velocity.y = -JUMP                                     │
│    → player.is_on_floor = FALSE                                    │
│                                                                     │
│  PLAYER DIMENSIONS:                                                 │
│    tile_width = 5, tile_height = 6 (40x48 px sprite)              │
│    collision_size = AABB(8, 32, 8, 48) (inner hitbox)              │
│    Spawn: tile(32, map_height - 6tiles - 24px)                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### Nivel 3 — Execution/Code

```
┌─────────────────────────────────────────────────────────────────────┐
│  playerUpdate() [src/main.c:173]                                    │
│    │                                                                │
│    ├─ playerApplyGravity() [main.c:165]                            │
│    │    if (player.velocity.y < GRAVITY_MAX)                       │
│    │        player.velocity.y += GRAVITY  // FIX16(0.22)          │
│    │                                                                │
│    ├─ Read control.d_pad.x → set player.velocity.x                │
│    │    +1 → FIX16(2.3)                                            │
│    │    -1 → FIX16(-2.3)                                           │
│    │     0 → 0                                                      │
│    │                                                                │
│    ├─ Entity_setPosition(&player,                                  │
│    │      pos.x + F16_toInt(vel.x),                                │
│    │      pos.y + F16_toInt(vel.y))  [entity.c:10]                 │
│    │                                                                │
│    ├─ checkTileCollisions()  ←──── [SEC.2 detalha]                 │
│    │                                                                │
│    ├─ Entity_moveSprite(&player,                                   │
│    │      pos.x - camera.x, pos.y - camera.y)  [entity.c:16]      │
│    │    → SPR_setPosition(sprite, screen_x, screen_y)              │
│    │                                                                │
│    ├─ playerUpdateAnimation()  [main.c:455]                        │
│    │    if (!is_on_floor) → ANIM_JUMP + playSoundJump()            │
│    │    else if (vel.x != 0) → ANIM_WALK + HFlip                  │
│    │    else → ANIM_STAND                                           │
│    │                                                                │
│    └─ updateCamera()  ←──── [SEC.3 detalha]                        │
│                                                                     │
│  handleInput(joy, changed, state) [main.c:543]                     │
│    JOY_setEventHandler callback (event-driven, not polling)        │
│    BUTTON_RIGHT/LEFT → control.d_pad.x = ±1                       │
│    BUTTON_UP/DOWN → control.d_pad.y = ±1                           │
│    (changed & BUTTON_*) → reset to 0                               │
│    BUTTON_C && is_on_floor → vel.y = -JUMP, is_on_floor = FALSE   │
│                                                                     │
│  playSoundJump() [main.c:443]                                      │
│    if (!XGM_isPlayingPCM(SOUND_PCM_CH2_MSK))                      │
│        XGM_startPlayPCM(64, 15, SOUND_PCM_CH2)                    │
│    PCM index 64 registered at playerInit via XGM_setPCM()          │
└─────────────────────────────────────────────────────────────────────┘
```

---

### SEC.2: COLLISION & SLOPE SYSTEM

#### Nivel 1 — Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                  COLLISION & SLOPE SYSTEM                            │
│                                                                     │
│  O mapa usa tiles de 8x8px com 3 tipos de colisao:                │
│                                                                     │
│  ┌─────┐  ┌─────┐  ┌─────┐                                        │
│  │  0  │  │  2  │  │  3  │                                        │
│  │GROUND│  │SLOPE│  │SLOPE│                                        │
│  │solid │  │RIGHT│  │LEFT │                                        │
│  └─────┘  └──/──┘  └──\──┘                                        │
│                                                                     │
│  A colisao verifica PRIMEIRO eixo horizontal,                      │
│  DEPOIS eixo vertical. Slopes ajustam a altura Y                   │
│  do jogador baseado na posicao X dentro do tile.                   │
│                                                                     │
│  Crateria 1: 288x156 tiles (2304x1248 px)                         │
│  Crateria 2: 160x160 tiles (1280x1280 px)                         │
│                                                                     │
│  Sistema anti-wall-detection nas slopes:                            │
│    - Antes de tratar tile como parede, verifica se                 │
│      o tile esta dentro do hitbox real (head/feet)                 │
│    - Slopes usam x_dif = deslocamento horizontal × 2              │
│      com cap em 8px para suavizar a transicao                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### Nivel 2 — Variables/Conditions

```
┌─────────────────────────────────────────────────────────────────────┐
│  TILE TYPES (inc/map.h)                                             │
│    GROUND_TILE = 0         (solid block, wall/floor/ceiling)       │
│    SLOPE_RIGHT_TILE = 2    (ascending right /  )                   │
│    SLOPE_LEFT_TILE = 3     (ascending left  \  )                   │
│    Air = implicit (any non-0,2,3 value)                            │
│                                                                     │
│  NOTE: Inverted convention! GROUND_TILE = 0 here                   │
│  (compare: PlatformerEngine uses GROUND_TILE = 1, Air = 0)        │
│                                                                     │
│  COLLISION GRID:                                                    │
│    map_collision[row][col] — const u8 2D array in ROM              │
│    Crateria 1: map_collision_crateria_1[156][288]                  │
│    Crateria 2: map_collision_crateria_2[160][160]                  │
│    extern const u8 map_collision[156][288] (main map.h)            │
│                                                                     │
│  TILE SIZE: 8x8px                                                   │
│    pixelToTile: position >> 3                                      │
│    tileToPixel: tile << 3                                          │
│    getTileBounds(x,y): AABB(x<<3, x<<3+8, y<<3, y<<3+8)          │
│                                                                     │
│  COLLISION POSITION:                                                │
│    collision_position = AABB(                                      │
│      pos.x + collision_size.min.x,  // pos.x + 8                  │
│      pos.x + collision_size.max.x,  // pos.x + 32                 │
│      pos.y + collision_size.min.y,  // pos.y + 8                  │
│      pos.y + collision_size.max.y)  // pos.y + 48                 │
│                                                                     │
│  SKIN WIDTH:                                                        │
│    yIntVelocity = F16_toRoundedInt(velocity.y)                     │
│    playerHeadPos = collision_size.min.y - yIntVelocity + pos.y    │
│    playerFeetPos = collision_size.max.y - yIntVelocity + pos.y    │
│    → Prevents detecting ground tiles as wall during high velocity  │
│                                                                     │
│  SLOPE FORMULA:                                                     │
│    x_dif = (collision_edge - tile_edge) << 1                       │
│    if (x_dif > 8) x_dif = 8    ← cap to 1 tile height            │
│    levelLimits.max.y = tileBounds.max.y - x_dif                   │
│    if feet >= limit - 2 → is_on_floor = TRUE                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### Nivel 3 — Execution/Code

```
┌─────────────────────────────────────────────────────────────────────┐
│  checkTileCollisions() [src/main.c:220]                            │
│    │                                                                │
│    ├─ PHASE 0: Setup                                               │
│    │    levelLimits = roomSize (full map bounds)                   │
│    │    collision_position = pos + collision_size offsets           │
│    │    yIntVelocity = F16_toRoundedInt(vel.y)                     │
│    │    minTilePos = posToTile(collision.min)                      │
│    │    maxTilePos = posToTile(collision.max)                      │
│    │    tileBoundDifference = max - min                             │
│    │                                                                │
│    ├─ PHASE 1: HORIZONTAL SCAN (per tile row in hitbox)            │
│    │    for i = 0..tileBoundDifference.y:                          │
│    │      ┌─ RIGHT: rTileValue = map_collision[y][maxTilePos.x]   │
│    │      │   if GROUND_TILE(0):                                   │
│    │      │     if tileBounds within head/feet range:              │
│    │      │       levelLimits.max.x = tileBounds.min.x → break    │
│    │      │                                                        │
│    │      ├─ LEFT: lTileValue = map_collision[y][minTilePos.x]    │
│    │      │   if GROUND_TILE(0):                                   │
│    │      │     levelLimits.min.x = tileBounds.max.x → break      │
│    │      │                                                        │
│    │      ├─ SLOPE RIGHT (type 2): on right tile                  │
│    │      │   x_dif = (player.right - tile.left) << 1             │
│    │      │   cap at 8                                             │
│    │      │   levelLimits.max.y = tile.bottom - x_dif             │
│    │      │   if feet >= limit - 2 → is_on_floor = TRUE           │
│    │      │                                                        │
│    │      └─ SLOPE LEFT (type 3): on left tile                    │
│    │          x_dif = ((player.left - tile.right) << 1) * -1      │
│    │          cap at 8                                             │
│    │          levelLimits.max.y = tile.bottom - x_dif             │
│    │          if feet >= limit - 2 → is_on_floor = TRUE           │
│    │                                                                │
│    ├─ APPLY H-CORRECTION:                                          │
│    │    if limits.max.x < collision.max.x → push left             │
│    │    if limits.min.x > collision.min.x → push right            │
│    │    Recalculate collision_position & tile positions            │
│    │                                                                │
│    ├─ PHASE 2: VERTICAL SCAN                                      │
│    │    if yIntVelocity >= 0 (falling/grounded):                  │
│    │      for each tile column at maxTilePos.y (feet row):        │
│    │        skip if tile is at wall edge                           │
│    │        if GROUND_TILE → bottomEdge = getTileTopEdge(y)       │
│    │        if bottomEdge < limits.max.y → update limit           │
│    │                                                                │
│    │    else (rising):                                              │
│    │      for each tile column at minTilePos.y (head row):        │
│    │        if GROUND_TILE → upperEdge = getTileBottomEdge(y)     │
│    │        if upperEdge < limits.max.y → limits.min.y = edge     │
│    │                                                                │
│    └─ PHASE 3: APPLY V-CORRECTION                                 │
│         if limits.min.y > collision.min.y:                         │
│           pos.y = limits.min.y - collision_size.min.y              │
│           velocity.y = 0  (hit ceiling)                            │
│                                                                     │
│         if limits.max.y <= collision.max.y:                        │
│           if limits.max.y == roomSize.max.y:                       │
│             is_on_floor = FALSE (fell off map)                     │
│           else:                                                     │
│             is_on_floor = TRUE                                     │
│             pos.y = limits.max.y - collision_size.max.y            │
│             velocity.y = 0  (landed)                               │
│                                                                     │
│         else if is_on_floor && vel.y < FIX16(3.0):                │
│           velocity.y = FIX16(3.0)  (slope sticking force)         │
│                                                                     │
│         else:                                                       │
│           is_on_floor = FALSE (airborne)                           │
│                                                                     │
│  PHYSICS HELPERS [src/physics.c]:                                   │
│    pixelToTile(pos) → pos >> 3                                     │
│    tileToPixel(tile) → tile << 3                                   │
│    getTileLeftEdge(x) → x << 3                                    │
│    getTileRightEdge(x) → (x << 3) + 8                             │
│    getTileTopEdge(y) → y << 3                                     │
│    getTileBottomEdge(y) → (y << 3) + 8                            │
│    getTileBounds(x,y) → AABB(x<<3, x<<3+8, y<<3, y<<3+8)        │
│    posToTile(pos) → (pos.x >> 3, pos.y >> 3)                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

### SEC.3: CAMERA CENTER-FOLLOW

#### Nivel 1 — Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CAMERA CENTER-FOLLOW                            │
│                                                                     │
│  A camera segue Samus mantendo-a centralizada na tela.             │
│  Limites da camera sao clampeados pelas bordas do mapa.            │
│  O background (BG_B) fica fixo em (0,0) — sem parallax scroll.    │
│                                                                     │
│  ┌──────────────────────────────────────────┐                      │
│  │               MAP (2304x1248)             │                      │
│  │  ┌───────────────────┐                    │                      │
│  │  │  SCREEN (256x224) │                    │                      │
│  │  │      ┌───┐        │                    │                      │
│  │  │      │ S │ center  │                    │                      │
│  │  │      └───┘        │                    │                      │
│  │  └───────────────────┘                    │                      │
│  │   cam.x = player.x - 128 + halfSprite    │                      │
│  │   cam.y = player.y - 112 + halfSprite    │                      │
│  │   clamp: [0, map_width - 256]             │                      │
│  │   clamp: [0, map_height - 224]            │                      │
│  └──────────────────────────────────────────┘                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### Nivel 2 — Variables/Conditions

```
┌─────────────────────────────────────────────────────────────────────┐
│  CAMERA CONSTANTS                                                   │
│    SCREEN_WIDTH = 256     (VDP_setScreenWidth256)                  │
│    SCREEN_HEIGHT = 224                                              │
│                                                                     │
│  CAMERA FORMULA:                                                    │
│    cam_x = player.pos.x - (SCREEN_WIDTH >> 1)                     │
│          + (tileToPixel(tile_width) >> 1)                          │
│    cam_x = player.x - 128 + 20 = player.x - 108                  │
│                                                                     │
│    cam_y = player.pos.y - (SCREEN_HEIGHT >> 1)                     │
│          + (tileToPixel(tile_height) >> 1)                         │
│    cam_y = player.y - 112 + 24 = player.y - 88                    │
│                                                                     │
│  CLAMP:                                                             │
│    cam_x: [0, map_width - SCREEN_WIDTH]                            │
│    cam_y: [0, map_height - SCREEN_HEIGHT]                          │
│    map_width/height from all_level_defs[curr_level_index]          │
│                                                                     │
│  SCROLL:                                                            │
│    MAP_scrollTo(current_map, cam_x, cam_y)  — foreground BG_A     │
│    MAP_scrollTo(current_map_bg, 0, 0)       — background BG_B     │
│    (BG_B is static — no parallax implemented)                      │
│                                                                     │
│  DIRTY CHECK:                                                       │
│    Only scrolls if (x != camera.x) || (y != camera.y)             │
│    Avoids redundant MAP_scrollTo calls                             │
└─────────────────────────────────────────────────────────────────────┘
```

#### Nivel 3 — Execution/Code

```
┌─────────────────────────────────────────────────────────────────────┐
│  updateCamera() [src/main.c:494]                                    │
│    │                                                                │
│    ├─ new_cam_x = player.pos.x - (256>>1) + (tileToPixel(5)>>1)  │
│    │            = player.pos.x - 128 + 20                          │
│    ├─ new_cam_y = player.pos.y - (224>>1) + (tileToPixel(6)>>1)  │
│    │            = player.pos.y - 112 + 24                          │
│    │                                                                │
│    ├─ Clamp X: max(0, min(new_cam_x, map_width - 256))           │
│    ├─ Clamp Y: max(0, min(new_cam_y, map_height - 224))          │
│    │                                                                │
│    └─ setCameraPosition(new_cam_x, new_cam_y) [main.c:528]       │
│         if (x != camera.x || y != camera.y):                      │
│           camera.position.x = x                                    │
│           camera.position.y = y                                    │
│           MAP_scrollTo(current_map, x, y)     // BG_A             │
│           MAP_scrollTo(current_map_bg, 0, 0)  // BG_B fixed       │
│                                                                     │
│  cameraInit() [main.c:102]                                         │
│    camera.position = (-1, -1)   // force first-frame refresh       │
│    MAP_scrollTo(current_map, -1, -1)                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

### SEC.4: LEVEL LOADER & DEFINITIONS

#### Nivel 1 — Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                  LEVEL LOADER & DEFINITIONS                         │
│                                                                     │
│  Cada nivel e definido por uma struct level_def que encapsula      │
│  TODOS os assets necessarios: tilesets, mapas, paletas,            │
│  dimensoes, e a collision grid completa.                           │
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐                              │
│  │ CRATERIA 1   │    │ CRATERIA 2   │                              │
│  │ 2304x1248 px │    │ 1280x1280 px │                              │
│  │ 288x156 tiles│    │ 160x160 tiles│                              │
│  │ FG + BG      │    │ FG + BG      │                              │
│  │ + collision  │    │ + collision   │                              │
│  └──────────────┘    └──────────────┘                              │
│         │                    │                                      │
│         └─── all_level_defs[0..1] ───┘                             │
│                    │                                                │
│              curr_level_index                                       │
│                    │                                                │
│            ┌───────┴───────┐                                        │
│            │  levelInit()  │                                        │
│            │  Load FG+BG   │                                        │
│            │  PAL + TILES  │                                        │
│            │  + MAP_create │                                        │
│            └───────────────┘                                        │
│                                                                     │
│  Dois planos VDP: BG_A (foreground tilemap), BG_B (static BG)     │
│  DMA buffer ampliado para 10000 bytes durante levelInit            │
│  (restaurado para default apos init completo)                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### Nivel 2 — Variables/Conditions

```
┌─────────────────────────────────────────────────────────────────────┐
│  level_def STRUCT [inc/types.h:33]                                  │
│    ├─ TileSet *tileset_fg       Foreground tiles                   │
│    ├─ TileSet *tileset_bg       Background tiles                   │
│    ├─ Image *image_fg           FG image data                      │
│    ├─ Image *image_bg           BG image data                      │
│    ├─ MapDefinition *map_fg     FG map layout                      │
│    ├─ MapDefinition *map_bg     BG map layout                      │
│    ├─ Palette *palette_fg       FG palette (PAL0)                  │
│    ├─ Palette *palette_bg       BG palette (PAL1)                  │
│    ├─ u16 map_width             Map width in pixels                │
│    ├─ u16 map_height            Map height in pixels               │
│    ├─ u8 *map_collision         1D collision source (unused?)      │
│    ├─ AABB room_size            Level bounds                       │
│    ├─ Sprite *level_elements    Decorative sprites                 │
│    ├─ u8 *num_level_elements    Element count                      │
│    ├─ Sprite enemies            Enemy sprite                       │
│    ├─ u8 num_enemies            Enemy count                        │
│    └─ Vect2D_s16 player_initial_pos  Spawn position                │
│                                                                     │
│  LEVEL ARRAY:                                                       │
│    all_level_defs[2] — pointer array                               │
│    curr_level_index = 0 (start at Crateria 1)                      │
│                                                                     │
│  COLLISION GRIDS (in ROM, const):                                   │
│    map_collision_crateria_1[156][288]  → 44,928 bytes              │
│    map_collision_crateria_2[160][160]  → 25,600 bytes              │
│                                                                     │
│  PALETTE ALLOCATION:                                                │
│    PAL0 = LEVEL_PALETTE  (foreground tileset)                      │
│    PAL1 = BG_PALETTE     (background tileset)                      │
│    PAL2 = PLAYER_PALETTE (Samus sprite)                            │
│                                                                     │
│  DMA TUNING:                                                        │
│    DMA_setBufferSize(10000) → during levelInit                     │
│    DMA_setMaxTransferSize(10000)                                   │
│    DMA_setMaxQueueSize(120)                                        │
│    → DMA_setBufferSizeToDefault() after init                       │
│                                                                     │
│  VDP PLANES:                                                        │
│    TILEMAP_PLANE = BG_A  (foreground map)                          │
│    BACKGROUND_PLANE = BG_B (background image)                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### Nivel 3 — Execution/Code

```
┌─────────────────────────────────────────────────────────────────────┐
│  boot() [src/main.c:69]                                            │
│    │                                                                │
│    ├─ SYS_disableInts()                                            │
│    ├─ VDP_setScreenWidth256()     // 256-pixel wide mode           │
│    ├─ SPR_init()                                                    │
│    ├─ JOY_init() + JOY_setEventHandler(&handleInput)              │
│    │                                                                │
│    ├─ DMA_setBufferSize(10000)    // enlarge for init              │
│    │  DMA_setMaxTransferSize(10000)                                │
│    │  DMA_setMaxQueueSize(120)                                     │
│    │                                                                │
│    ├─ curr_level_index = 0                                         │
│    │  all_level_defs[0] = &level_crateria_1                        │
│    │                                                                │
│    ├─ VDPTilesFilled += levelInit(VDPTilesFilled)                  │
│    ├─ playerInit()                                                  │
│    ├─ cameraInit()                                                  │
│    │                                                                │
│    └─ DMA_setBufferSizeToDefault()  // restore                     │
│       DMA_setMaxTransferSizeToDefault()                            │
│                                                                     │
│  levelInit(vram_index) [main.c:111]                                │
│    │                                                                │
│    ├─ roomSize = newAABB(0, map_width, 0, map_height)             │
│    │                                                                │
│    ├─ FOREGROUND:                                                   │
│    │   PAL_setPalette(PAL0, palette_fg, DMA)                      │
│    │   VDP_loadTileSet(tileset_fg, index, DMA)                    │
│    │   current_map = MAP_create(map_fg, BG_A, TILE_ATTR(...))     │
│    │   index += tileset_fg->numTile                                │
│    │                                                                │
│    ├─ BACKGROUND:                                                   │
│    │   PAL_setPalette(PAL1, palette_bg, DMA)                      │
│    │   VDP_loadTileSet(tileset_bg, index, DMA)                    │
│    │   current_map_bg = MAP_create(map_bg, BG_B, TILE_ATTR(...))  │
│    │   index += tileset_bg->numTile                                │
│    │                                                                │
│    └─ return index (total VRAM tiles consumed)                     │
│                                                                     │
│  playerInit() [main.c:132]                                         │
│    player.collision_size = AABB(8, 32, 8, 48)                     │
│    Entity_setPosition(&player,                                     │
│      tileToPixel(32),                                              │
│      map_height - tileToPixel(6) - 24)                             │
│    XGM_setPCM(64, jump_sfx, sizeof(jump_sfx))                     │
│    PAL_setPalette(PAL2, player_sprite.palette, DMA)               │
│    player.sprite = SPR_addSprite(&player_sprite, ...)             │
│    Entity_setAnimation(&player, ANIM_STAND)                       │
│                                                                     │
│  RESOURCES [res/]:                                                  │
│    resources.res:                                                   │
│      SPRITE player_sprite "samus_defaul_suit.png" 5 6 FAST 5 BOX │
│      WAV jump_sfx "sound/jump.wav" XGM                             │
│    crateria_1.res:                                                  │
│      IMAGE/PALETTE/TILESET/MAP × 2 (fg + bg) — BEST compression  │
│    crateria_2.res:                                                  │
│      IMAGE/PALETTE/TILESET/MAP × 2 (fg + bg) — BEST compression  │
└─────────────────────────────────────────────────────────────────────┘
```

---

### SEC.5: ENTITY SYSTEM (BASE)

#### Nivel 1 — Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                     ENTITY SYSTEM (BASE)                            │
│                                                                     │
│  Entidades sao objetos com posicao, velocidade, colisao,           │
│  e sprite. O sistema base fornece operacoes atomicas:              │
│  setar posicao, mover sprite na tela, trocar animacao.             │
│                                                                     │
│  Atualmente so o player usa o sistema. A struct level_def          │
│  ja preve campos para enemies e level_elements mas nao             │
│  estao implementados — preparado para expansao.                    │
│                                                                     │
│  ┌─────────────── Entity ───────────────────┐                      │
│  │  position (Vect2D_s16)   — world coords  │                      │
│  │  velocity (Vect2D_f16)   — fix16 speed   │                      │
│  │  collision_position      — world AABB    │                      │
│  │  collision_size          — local AABB    │                      │
│  │  tile_width/height       — sprite size   │                      │
│  │  is_on_floor (bool)      — grounded flag │                      │
│  │  is_flipped (bool)       — facing dir    │                      │
│  │  sprite (Sprite*)        — SGDK sprite   │                      │
│  │  current_animation (u16) — anim index    │                      │
│  └──────────────────────────────────────────┘                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### Nivel 2 — Variables/Conditions

```
┌─────────────────────────────────────────────────────────────────────┐
│  Entity STRUCT [inc/entity.h:6]                                     │
│    Vect2D_s16 position     — Integer world position                │
│    Vect2D_f16 velocity     — Fixed-point velocity (FIX16)          │
│    AABB collision_position — Recalculated each frame               │
│    AABB collision_size     — Offset from entity origin             │
│    s16 tile_width          — Sprite width in tiles                 │
│    s16 tile_height         — Sprite height in tiles                │
│    bool is_on_floor        — Set by checkTileCollisions()          │
│    bool is_flipped         — Horizontal flip state                 │
│    Sprite* sprite          — SGDK sprite handle                    │
│    u16 current_animation   — Current anim index                    │
│                                                                     │
│  SUPPORT TYPES [inc/types.h]:                                       │
│    Camera { Vect2D_s16 position }                                  │
│    AABB { Vect2D_s16 min, Vect2D_s16 max }                        │
│    Vect2D_u8, Vect2D_s8  — Compact vector types                   │
│    control { d_pad, a, b, c, x, y, z } — Global input state       │
│                                                                     │
│  ENTITY FUNCTIONS [src/entity.c]:                                   │
│    Entity_setPosition(entity, x, y) → direct assignment            │
│    Entity_moveSprite(entity, x, y)  → SPR_setPosition              │
│    Entity_setAnimation(entity, anim) → SPR_setAnim + cache         │
│    Entity_setCollisionPosition(entity, x, y) → setPos(x-8, y-8)  │
└─────────────────────────────────────────────────────────────────────┘
```

#### Nivel 3 — Execution/Code

```
┌─────────────────────────────────────────────────────────────────────┐
│  Entity_setPosition(entity, x, y) [src/entity.c:10]               │
│    entity->position.x = x                                          │
│    entity->position.y = y                                          │
│                                                                     │
│  Entity_moveSprite(entity, x, y) [entity.c:16]                    │
│    SPR_setPosition(entity->sprite, x, y)                           │
│    (x, y are screen-space: world_pos - camera_pos)                 │
│                                                                     │
│  Entity_setAnimation(entity, anim) [entity.c:21]                  │
│    SPR_setAnim(entity->sprite, anim)                               │
│    entity->current_animation = anim  (cached for comparison)       │
│                                                                     │
│  Entity_setCollisionPosition(entity, x, y) [entity.c:5]           │
│    Entity_setPosition(entity, x - 8, y - 8)                       │
│    (offsets by collision_size.min defaults)                         │
│                                                                     │
│  CONSTRUCTOR HELPERS [src/types.c]:                                 │
│    newAABB(x1, x2, y1, y2) → (AABB){{x1,y1},{x2,y2}}            │
│    newVector2D_f16(x, y)   → (Vect2D_f16){x, y}                  │
│    newVector2D_s16(x, y)   → (Vect2D_s16){x, y}                  │
│    newVector2D_u16(x, y)   → (Vect2D_u16){x, y}                  │
│    (+ variants: s8, u8, s32, u32, f32)                             │
└─────────────────────────────────────────────────────────────────────┘
```

---

### MAPA DE DEPENDENCIAS — MEGA METROID

```
┌──────────────────────────────────────────────────────────────────────┐
│                     DEPENDENCY MAP                                   │
│                                                                      │
│   main.c ─────────────┬──────────┬──────────┬────────────┐          │
│   (game loop,         │          │          │            │          │
│    player, camera,    │          │          │            │          │
│    collision, input)  │          │          │            │          │
│          │            │          │          │            │          │
│          ▼            ▼          ▼          ▼            ▼          │
│     entity.c      physics.c   map.c   types.c    resources.res     │
│     (set pos,     (tile       (tile   (AABB,     (player_sprite,   │
│      move spr,    math,       types,  Camera,     jump_sfx)        │
│      set anim)    bounds)     extern  Vectors,                     │
│                               grid)   control)                     │
│                     │                    │                           │
│                     ▼                    ▼                           │
│               map_crateria_1.c    map_crateria_2.c                  │
│               (collision grid     (collision grid                   │
│                156×288 +           160×160 +                        │
│                level_def)          level_def)                       │
│                     │                    │                           │
│                     ▼                    ▼                           │
│               crateria_1.res      crateria_2.res                    │
│               (IMAGE, TILESET,    (IMAGE, TILESET,                  │
│                MAP, PALETTE       MAP, PALETTE                      │
│                fg + bg)           fg + bg)                          │
│                                                                      │
│  TOTAL: 5 .c source + 2 level data + 3 .res + 6 .h headers         │
└──────────────────────────────────────────────────────────────────────┘
```

### TABELA DE CONSTANTES — MEGA METROID

| Constante | Valor | Arquivo | Uso |
|---|---|---|---|
| `SCREEN_WIDTH` | 256 | main.c:11 | VDP_setScreenWidth256 |
| `SCREEN_HEIGHT` | 224 | main.c:12 | Camera centering |
| `ANIM_STAND` | 0 | main.c:14 | Idle animation |
| `ANIM_WALK` | 1 | main.c:15 | Walking animation |
| `ANIM_JUMP` | 2 | main.c:16 | Jumping animation |
| `GRAVITY` | FIX16(0.22) | main.c:18 | Per-frame gravity |
| `GRAVITY_MAX` | 300 | main.c:19 | Terminal velocity |
| `JUMP` | FIX16(6.6) | main.c:20 | Jump impulse |
| `TILEMAP_PLANE` | BG_A | main.c:22 | Foreground plane |
| `BACKGROUND_PLANE` | BG_B | main.c:23 | Background plane |
| `LEVEL_PALETTE` | PAL0 | main.c:24 | Foreground palette |
| `BG_PALETTE` | PAL1 | main.c:25 | Background palette |
| `PLAYER_PALETTE` | PAL2 | main.c:26 | Samus palette |
| `GROUND_TILE` | 0 | map.h:7 | Solid collision |
| `SLOPE_RIGHT_TILE` | 2 | map.h:8 | Right slope / |
| `SLOPE_LEFT_TILE` | 3 | map.h:9 | Left slope \ |
| `player.tile_width` | 5 | main.c:137 | 40px sprite width |
| `player.tile_height` | 6 | main.c:138 | 48px sprite height |
| `collision_size` | AABB(8,32,8,48) | main.c:140 | Inner hitbox |
| `velocity.x` | FIX16(2.3) | main.c:181 | Movement speed |
| `slope x_dif cap` | 8 | main.c:296 | Max slope offset |
| `slope stick vel` | FIX16(3.0) | main.c:431 | Slope adhesion |
| `PCM jump index` | 64 | main.c:153 | Jump SFX slot |
| `PCM channel` | SOUND_PCM_CH2 | main.c:446 | Audio channel |
| `DMA init buffer` | 10000 | main.c:81 | Init-time DMA size |
| `DMA queue size` | 120 | main.c:86 | Max DMA queue |
| Crateria 1 grid | 156×288 | map_crateria_1.h:5 | 44,928 tiles (8px) |
| Crateria 2 grid | 160×160 | map_crateria_2.h:5 | 25,600 tiles (8px) |

---

# ══════════════════════════════════════════════════════════════════
# ENGINE 8: PLATFORMER ENGINE [VER.1.0] [SGDK 211] [GEN] [ENGINE] [PLATAFORMA]
# ══════════════════════════════════════════════════════════════════

## ARVORE MESTRA DE SISTEMAS

```
                    ╔══════════════════════════════════════╗
                    ║   PLATFORMER ENGINE [VER.1.0]        ║
                    ║  Plataforma · SGDK 2.11 · 320x224    ║
                    ║  16px tiles · Coyote+Buffer · Ladder  ║
                    ╚══════════════════╤═══════════════════╝
                                       │
          ┌────────────────┬───────────┴──────────┬──────────────────┐
          │                │                      │                  │
    ┌─────┴─────┐   ┌─────┴──────┐   ┌──────────┴────────┐  ┌─────┴──────┐
    │  PLAYER   │   │  CAMERA    │   │    COLLISION      │  │   LEVEL    │
    │ MOVEMENT  │   │  DEADZONE  │   │    SYSTEM         │  │  LOADING   │
    │  SYSTEM   │   │  SYSTEM    │   │  Ground/OneWay/   │  │   SYSTEM   │
    │ Accel/    │   │  20x20 px  │   │  Ladder/SkinWidth │  │  ROM→RAM   │
    │ Decel/    │   │            │   │                   │  │  +Audio    │
    │ Jump/     │   │            │   │                   │  │            │
    │ Ladder    │   │            │   │                   │  │            │
    └─────┬─────┘   └─────┬──────┘   └──────────┬────────┘  └─────┬──────┘
          │               │                      │                 │
     [SEC.1]          [SEC.2]               [SEC.3]           [SEC.4]
```

---

### SEC.1: PLAYER MOVEMENT SYSTEM

#### Nivel 1 — Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PLAYER MOVEMENT SYSTEM                            │
│                                                                     │
│  O personagem corre, pula, escala escadas e morre ao cair no vazio  │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────┐  ┌──────────┐ │
│  │  PARADO  │→ │ CORRENDO │→ │ PULANDO  │  │ESCADA│  │  MORTE   │ │
│  │  (idle)  │  │  (run)   │  │  (jump)  │  │(climb│  │  (fall)  │ │
│  │  anim 0  │  │  anim 1  │  │ mid-air  │  │anim 2│  │ hardReset│ │
│  └──────────┘  └──────────┘  └──────────┘  └──────┘  └──────────┘ │
│       ↑              ↑              ↑           ↑          ↑       │
│   sem input     D-Pad L/R     A/B/C btn    UP/DOWN    y >= 768    │
│                                                                     │
│  Mecanicas avancadas de game feel:                                 │
│    Coyote Time: 10 frames de pulo apos sair do chao               │
│    Jump Buffer: 10 frames de input pre-aterrissagem                │
│    Variable Jump: soltar botao = meio impulso (pulo curto)         │
│    Aceleracao/Desaceleracao: curva suave, nao instantanea          │
│    Escada: hitbox estreito, sem gravidade, snap X ao centro        │
└─────────────────────────────────────────────────────────────────────┘
```

#### Nivel 2 — Variables/Conditions

```
┌─ PLAYER MOVEMENT SYSTEM ──────────────────────────────────────────────────────┐
│                                                                                │
│  ┌─ HORIZONTAL MOVEMENT ─────────────────────────────────────────────────────┐ │
│  │                                                                           │ │
│  │  INPUT:  playerBody.input.x = {-1, 0, +1}                                │ │
│  │          Set via: inGameJoyEvent() → playerInputChanged()                 │ │
│  │          BUTTON_LEFT → input.x = -1                                       │ │
│  │          BUTTON_RIGHT → input.x = +1                                      │ │
│  │          Released → input.x = 0                                           │ │
│  │                                                                           │ │
│  │  ACCELERATION:                                                            │ │
│  │    if input.x > 0 && velocity.x != speed:                                │ │
│  │      velocity.fixX += acceleration     [FIX16(0.25) per frame]            │ │
│  │    if input.x < 0 && velocity.x != -speed:                               │ │
│  │      velocity.fixX -= acceleration     [FIX16(0.25) per frame]            │ │
│  │                                                                           │ │
│  │  DECELERATION (only onGround):                                            │ │
│  │    if input.x == 0 && onGround:                                           │ │
│  │      if velocity.x > 0: fixX -= deceleration  [FIX16(0.2)]               │ │
│  │      if velocity.x < 0: fixX += deceleration  [FIX16(0.2)]               │ │
│  │      if velocity.x == 0: fixX = 0  (full stop)                           │ │
│  │                                                                           │ │
│  │  CLAMP:  velocity.x = clamp(F16_toInt(fixX), -speed, +speed)             │ │
│  │          speed = 2 px/frame → max 120 px/sec @ 60fps                      │ │
│  │                                                                           │ │
│  │  POSITION: globalPosition.x += velocity.x                                │ │
│  │  FACING:  facingDirection = +1 (right) or -1 (left)                       │ │
│  │           SPR_setHFlip(sprite, TRUE/FALSE)                                │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌─ JUMP SYSTEM (Coyote Time + Jump Buffer) ─────────────────────────────────┐ │
│  │                                                                           │ │
│  │  JUMP TRIGGER: currentCoyoteTime > 0 && currentJumpBufferTime > 0        │ │
│  │                                                                           │ │
│  │  ┌── COYOTE TIME ──────────────────────────────────────┐                  │ │
│  │  │  coyoteTime = 10 frames (const)                     │                  │ │
│  │  │  currentCoyoteTime = coyoteTime  (when onGround)    │                  │ │
│  │  │  currentCoyoteTime--             (when airborne)    │                  │ │
│  │  │  Allows jump for 10 frames after leaving ground     │                  │ │
│  │  └─────────────────────────────────────────────────────┘                  │ │
│  │                                                                           │ │
│  │  ┌── JUMP BUFFER ──────────────────────────────────────┐                  │ │
│  │  │  jumpBufferTime = 10 frames (const)                 │                  │ │
│  │  │  currentJumpBufferTime = jumpBufferTime (on press)  │                  │ │
│  │  │  currentJumpBufferTime-- per frame (clamped to 0)   │                  │ │
│  │  │  Allows pre-landing jump input for 10 frames        │                  │ │
│  │  └─────────────────────────────────────────────────────┘                  │ │
│  │                                                                           │ │
│  │  ON JUMP:                                                                 │ │
│  │    playerBody.jumping = TRUE                                              │ │
│  │    velocity.fixY = FIX16(-jumpSpeed)   [-7.0 = strong upward]             │ │
│  │    XGM_startPlayPCM(64, 15, SOUND_PCM_CH1)  [jump SFX]                   │ │
│  │    currentCoyoteTime = 0                                                  │ │
│  │    currentJumpBufferTime = 0                                              │ │
│  │                                                                           │ │
│  │  VARIABLE JUMP HEIGHT (button release):                                   │ │
│  │    if jumping && velocity.fixY < 0:                                       │ │
│  │      velocity.fixY *= 0.5   [F16_mul(fixY, FIX16(.5))]                   │ │
│  │    → Short tap = low jump, hold = full jump                               │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌─ GRAVITY ─────────────────────────────────────────────────────────────────┐ │
│  │                                                                           │ │
│  │  CONDITION: !onGround && !climbingStair                                   │ │
│  │                                                                           │ │
│  │  if F16_toInt(velocity.fixY) <= maxFallSpeed:                             │ │
│  │    velocity.fixY += gravityScale         [FIX16(0.5) per frame]           │ │
│  │  else:                                                                    │ │
│  │    velocity.fixY = FIX16(maxFallSpeed)   [terminal = 6 px/frame]          │ │
│  │                                                                           │ │
│  │  POSITION: globalPosition.y += F16_toInt(velocity.fixY)                   │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌─ STAIR/LADDER CLIMBING ───────────────────────────────────────────────────┐ │
│  │                                                                           │ │
│  │  DETECTION: collidingAgainstStair = TRUE (set in checkCollisions)         │ │
│  │             When tile value == LADDER_TILE (2) at player bounds           │ │
│  │                                                                           │ │
│  │  ENTER CLIMB:                                                             │ │
│  │    UP pressed + collidingAgainstStair + !onStair → climbingStair = TRUE   │ │
│  │    DOWN pressed + onStair → climbingStair = TRUE                          │ │
│  │                                                                           │ │
│  │  WHILE CLIMBING:                                                          │ │
│  │    velocity.x = velocity.fixX = 0  (no horizontal movement)              │ │
│  │    globalPosition.x = stairLeftEdge - stairPositionOffset (4px)           │ │
│  │    velocity.fixY = FIX16(climbingSpeed * input.y)                         │ │
│  │    climbingSpeed = 1 px/frame                                             │ │
│  │    Narrower AABB: climbingStairAABB(8,20,4,24) vs normal(4,20,4,24)      │ │
│  │    SPR_setAnim(sprite, 2) → climb animation                              │ │
│  │                                                                           │ │
│  │  EXIT CLIMB:                                                              │ │
│  │    A/B/C pressed while climbing → climbingStair = FALSE (jump off)        │ │
│  │    !collidingAgainstStair → climbingStair = FALSE (ran out of ladder)     │ │
│  │    No gravity applied while climbingStair == TRUE                         │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌─ DEATH SYSTEM ────────────────────────────────────────────────────────────┐ │
│  │                                                                           │ │
│  │  TRIGGER:  levelLimits.max.y == 768 (bottom of room)                      │ │
│  │            → playerBody.falling = TRUE                                    │ │
│  │                                                                           │ │
│  │  DELAY:    dyingSteps++ each frame while falling == TRUE                  │ │
│  │            When dyingSteps > dieDelay (10 frames):                        │ │
│  │            → SYS_hardReset()  (full system reset)                         │ │
│  │                                                                           │ │
│  │  No lives system, no checkpoints, no score — instant full restart         │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────┘
```

#### Nivel 3 — Execution/Code

```
┌─ updatePlayer() [src/player.c:125] ──────────────────────────────────────────┐
│                                                                               │
│  FRAME TICK ORDER (called every frame from main loop):                        │
│                                                                               │
│  1. STAIR CHECK                                                               │
│     │  if collidingAgainstStair && ((onStair && input.y>0)                    │
│     │     || (!onStair && input.y<0)):                                        │
│     │    climbingStair = TRUE                                                 │
│     │    velocity.fixY = FIX16(climbingSpeed * input.y)                       │
│     │                                                                         │
│  2. JUMP CHECK (Coyote + Buffer)                                              │
│     │  if currentCoyoteTime > 0 && currentJumpBufferTime > 0:                 │
│     │    jumping = TRUE                                                       │
│     │    XGM_startPlayPCM(64, 15, SOUND_PCM_CH1) ◄── SFX: jump.wav          │
│     │    velocity.fixY = FIX16(-7)  (jumpSpeed)                               │
│     │    reset both counters to 0                                             │
│     │  currentJumpBufferTime = clamp(currentJumpBufferTime - 1, 0, 10)       │
│     │                                                                         │
│  3. HORIZONTAL MOVEMENT                                                       │
│     │  if climbingStair:                                                      │
│     │    velocity.x = fixX = 0                                                │
│     │    snap X to stairLeftEdge - 4                                          │
│     │  else:                                                                  │
│     │    input.x > 0 → fixX += FIX16(0.25) [acceleration]                    │
│     │    input.x < 0 → fixX -= FIX16(0.25)                                   │
│     │    input.x == 0 && onGround → fixX ±= FIX16(0.2) [deceleration]       │
│     │    velocity.x = clamp(F16_toInt(fixX), -2, +2)                         │
│     │                                                                         │
│  4. GRAVITY                                                                   │
│     │  if !onGround && !climbingStair:                                        │
│     │    if F16_toInt(fixY) <= 6: fixY += FIX16(0.5)                         │
│     │    else: fixY = FIX16(6) [terminal velocity]                            │
│     │                                                                         │
│  5. APPLY POSITION                                                            │
│     │  globalPosition.x += velocity.x                                         │
│     │  globalPosition.y += F16_toInt(velocity.fixY)                           │
│     │                                                                         │
│  6. COLLISION CHECK                                                           │
│     │  → checkCollisions()  [see SEC.3]                                       │
│     │                                                                         │
│  7. STAIR EXIT CHECK                                                          │
│     │  if !collidingAgainstStair && climbingStair:                             │
│     │    climbingStair = FALSE, input.y = 0                                   │
│     │                                                                         │
│  8. CAMERA OFFSET + SPRITE POSITION                                           │
│     │  position.x = globalPosition.x - cameraPosition.x                      │
│     │  position.y = globalPosition.y - cameraPosition.y                      │
│     │  SPR_setPosition(sprite, position.x, position.y)                       │
│     │                                                                         │
│  9. ANIMATIONS                                                                │
│     │  → updateAnimations()                                                   │
│     │    input.x > 0 → SPR_setHFlip(sprite, TRUE)                            │
│     │    input.x < 0 → SPR_setHFlip(sprite, FALSE)                           │
│     │    fixY==0 && !climbing:                                                │
│     │      velocity.x != 0 && onGround → SPR_setAnim(sprite, 1) [run]       │
│     │      velocity.x == 0 && onGround → SPR_setAnim(sprite, 0) [idle]      │
│     │    climbingStair → SPR_setAnim(sprite, 2) [climb]                      │
│     │                                                                         │
│ 10. DEATH CHECK                                                               │
│     │  if falling: dyingSteps++                                               │
│     │  if dyingSteps > 10: SYS_hardReset()                                   │
│     │                                                                         │
└───────────────────────────────────────────────────────────────────────────────┘

┌─ playerInputChanged() [src/player.c:59] ─────────────────────────────────────┐
│  Called by: inGameJoyEvent() [src/main.c:41] (JOY callback)                  │
│                                                                               │
│  JOY_1 only:                                                                  │
│    BUTTON_RIGHT held  → input.x = +1                                          │
│    BUTTON_LEFT held   → input.x = -1                                          │
│    Either released    → input.x = 0                                           │
│                                                                               │
│    A/B/C pressed:                                                             │
│      if climbingStair → climbingStair = FALSE (exit stair)                    │
│      else → currentJumpBufferTime = 10 (start jump buffer)                    │
│    A/B/C released:                                                            │
│      if jumping && fixY < 0 → fixY *= 0.5 (variable jump cut)                │
│                                                                               │
│    BUTTON_DOWN pressed:                                                       │
│      input.y = +1                                                             │
│      if climbingStair → fixY = FIX16(+1)  (descend)                          │
│      if onStair → fixY = FIX16(+1), climbingStair = TRUE                     │
│    BUTTON_DOWN released:                                                      │
│      input.y = 0, if climbing → fixY = 0  (stop on stair)                    │
│                                                                               │
│    BUTTON_UP pressed:                                                         │
│      input.y = -1                                                             │
│      if collidingAgainstStair && !onStair:                                    │
│        climbingStair = TRUE, fixY = FIX16(-1) (ascend)                        │
│    BUTTON_UP released:                                                        │
│      input.y = 0, if climbing → fixY = 0                                     │
└───────────────────────────────────────────────────────────────────────────────┘

┌─ playerInit() [src/player.c:29] ─────────────────────────────────────────────┐
│                                                                               │
│  SPR_addSprite(&player_sprite, 74, 665, TILE_ATTR(PAL1, FALSE, FALSE, FALSE))│
│  PAL_setPalette(PAL1, player_sprite.palette->data, DMA)                      │
│  globalPosition = {74, 665}                                                   │
│  aabb = AABB(4, 20, 4, 24)          [16x20 px hitbox]                        │
│  climbingStairAABB = AABB(8, 20, 4, 24)  [12x20 px narrow hitbox]           │
│  centerOffset = (12, 14)             [midpoint of AABB]                       │
│  speed = 2, climbingSpeed = 1, maxFallSpeed = 6, jumpSpeed = 7               │
│  acceleration = FIX16(0.25), deceleration = FIX16(0.2)                       │
│  facingDirection = +1 (right)                                                 │
│  XGM_setPCM(64, jump, sizeof(jump))  [register jump SFX at index 64]         │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

### SEC.2: CAMERA DEADZONE SYSTEM

#### Nivel 1 — Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CAMERA DEADZONE SYSTEM                            │
│                                                                     │
│  A camera so se move quando o jogador sai de uma "zona morta"       │
│  centralizada na tela. Evita micro-scrolling durante movimentos     │
│  pequenos. Camera limitada aos limites do nivel.                    │
│                                                                     │
│       ┌───────────────── 320px SCREEN ──────────────────┐           │
│       │                                                 │           │
│       │           ┌───── DEADZONE ──────┐               │           │
│       │           │   center: 160,112   │               │           │
│       │           │   width: 20px       │               │           │
│  224px│           │   height: 20px      │               │           │
│       │           │   ┌──┐              │               │           │
│       │           │   │PL│ ← player     │               │           │
│       │           │   └──┘  inside =    │               │           │
│       │           │   no cam movement   │               │           │
│       │           └─────────────────────┘               │           │
│       │                                                 │           │
│       └─────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────┘
```

#### Nivel 2 — Variables/Conditions

```
┌─ CAMERA DEADZONE SYSTEM ──────────────────────────────────────────────────────┐
│                                                                                │
│  SETUP (once, after playerInit):                                               │
│    setupCamera(center={160,112}, width=20, height=20)                          │
│    cameraDeadzone.min.x = 160 - 10 = 150                                      │
│    cameraDeadzone.max.x = 160 + 10 = 170                                      │
│    cameraDeadzone.min.y = 112 - 10 = 102                                      │
│    cameraDeadzone.max.y = 112 + 10 = 122                                      │
│                                                                                │
│  UPDATE (every frame):                                                         │
│    playerCenter = globalPosition + centerOffset                                │
│                                                                                │
│    HORIZONTAL:                                                                 │
│      if playerCenter.x > cameraPosition.x + deadzone.max.x:                   │
│        camera.x = playerCenter.x - deadzone.max.x  (player pushes right)      │
│      if playerCenter.x < cameraPosition.x + deadzone.min.x:                   │
│        camera.x = playerCenter.x - deadzone.min.x  (player pushes left)       │
│                                                                                │
│    VERTICAL:                                                                   │
│      if playerCenter.y > cameraPosition.y + deadzone.max.y:                    │
│        camera.y = playerCenter.y - deadzone.max.y  (player pushes down)        │
│      if playerCenter.y < cameraPosition.y + deadzone.min.y:                    │
│        camera.y = playerCenter.y - deadzone.min.y  (player pushes up)          │
│                                                                                │
│  CLAMP:                                                                        │
│    camera.x = clamp(camera.x, 0, 448)   [768 - 320 = 448]                     │
│    camera.y = clamp(camera.y, 0, 544)   [768 - 224 = 544]                     │
│                                                                                │
│  RENDER:                                                                       │
│    MAP_scrollTo(bga, cameraPosition.x, cameraPosition.y)                      │
│    Initial: MAP_scrollToEx(bga, x, y, TRUE) [force full tile refresh]          │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

#### Nivel 3 — Execution/Code

```
┌─ setupCamera() [src/camera.c:11] ────────────────────────────────────────────┐
│  Called once from main() after playerInit()                                   │
│  Params: deadZoneCenter={160,112}, width=20, height=20                       │
│  Calculates AABB deadzone bounds via bit-shift: width >> 1 = 10              │
│  Calls updateCamera() to set initial position                                │
│  MAP_scrollToEx(bga, x, y, TRUE) → force-loads all visible tiles             │
└───────────────────────────────────────────────────────────────────────────────┘

┌─ updateCamera() [src/camera.c:24] ───────────────────────────────────────────┐
│  Called every frame from main loop (after updatePlayer)                       │
│                                                                               │
│  1. Horizontal deadzone check (playerBody.globalPosition.x + centerOffset.x) │
│  2. Vertical deadzone check (playerBody.globalPosition.y + centerOffset.y)   │
│  3. clamp(x, 0, 448), clamp(y, 0, 544)                                      │
│  4. MAP_scrollTo(bga, cameraPosition.x, cameraPosition.y)                    │
│                                                                               │
│  No smoothing/lerp — camera snaps to deadzone edge instantly                 │
│  No parallax BG_B scrolling in this engine (single plane only)               │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

### SEC.3: COLLISION SYSTEM

#### Nivel 1 — Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TILE-BASED COLLISION SYSTEM                       │
│                                                                     │
│  O jogador colide com tiles solidos (chao/parede),                  │
│  pode pular atraves de plataformas one-way por baixo,               │
│  e detecta escadas para ativar o modo de escalada.                  │
│                                                                     │
│           ═══  ← One-Way Platform (passavel por baixo)              │
│           ↑↑↑                                                       │
│           │PL│ ← Pode pular atraves                                 │
│           └──┘                                                      │
│                                                                     │
│    ###│    │H│ ← Ladder (escada vertical)                           │
│    ###│ PL │H│                                                      │
│    ###│    │H│                                                      │
│    ████████████ ← Ground (solido em todas as direcoes)              │
└─────────────────────────────────────────────────────────────────────┘
```

#### Nivel 2 — Variables/Conditions

```
┌─ COLLISION SYSTEM ────────────────────────────────────────────────────────────┐
│                                                                                │
│  ┌─ TILE TYPES ───────────────────────────────────────────────────────────┐   │
│  │  GROUND_TILE (1)           — Solid wall/floor in all directions        │   │
│  │  LADDER_TILE (2)           — Triggers stair detection, top = floor     │   │
│  │  ONE_WAY_PLATFORM_TILE (4) — Solid only from above (feet collision)    │   │
│  │  0 (air)                   — No collision                              │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                                │
│  ┌─ COLLISION PHASES ─────────────────────────────────────────────────────┐   │
│  │                                                                        │   │
│  │  PHASE 1: HORIZONTAL (walls)                                           │   │
│  │    For each tile row in player bounds:                                  │   │
│  │      Check RIGHT edge tiles → if GROUND_TILE:                          │   │
│  │        Is it within head-to-feet range? (skin width correction)        │   │
│  │        YES → levelLimits.max.x = tileBounds.min.x (block right)       │   │
│  │      Check LEFT edge tiles → same logic                                │   │
│  │        YES → levelLimits.min.x = tileBounds.max.x (block left)        │   │
│  │      LADDER_TILE → stairLeftEdge = tile left edge, flag stair          │   │
│  │                                                                        │   │
│  │    Apply: snap player X if exceeding limits, zero velocity.x           │   │
│  │                                                                        │   │
│  │  PHASE 2: VERTICAL (floor/ceiling)                                     │   │
│  │    Separated by velocity direction:                                    │   │
│  │                                                                        │   │
│  │    IF FALLING (yIntVelocity >= 0):                                     │   │
│  │      For each tile col in player bounds:                                │   │
│  │        GROUND_TILE or ONE_WAY_PLATFORM_TILE:                           │   │
│  │          Skip if tile is already a confirmed wall                      │   │
│  │          bottomEdgePos = getTileTopEdge(y)                             │   │
│  │          Error correction: bottomEdgePos >= playerFeetPos - 5          │   │
│  │          → levelLimits.max.y = bottomEdgePos                           │   │
│  │        LADDER_TILE (top of ladder, tile above != LADDER):              │   │
│  │          → Mark onStair, set levelLimits.max.y                         │   │
│  │                                                                        │   │
│  │    IF RISING (yIntVelocity < 0):                                       │   │
│  │      Only GROUND_TILE blocks upward (not one-way or ladder)            │   │
│  │      → levelLimits.min.y = getTileBottomEdge(y)                        │   │
│  │                                                                        │   │
│  │  PHASE 3: RESOLVE                                                      │   │
│  │    if min.y > playerBounds.min.y → snap Y down, zero fixY (ceiling)   │   │
│  │    if max.y <= playerBounds.max.y:                                     │   │
│  │      if max.y == 768 → falling = TRUE (death pit)                     │   │
│  │      else → onGround=TRUE, coyoteTime=10, jumping=FALSE               │   │
│  │    else → onGround = onStair = FALSE, coyoteTime--                    │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                                │
│  ┌─ SKIN WIDTH (Wall vs Floor Disambiguation) ────────────────────────────┐   │
│  │  yIntVelocity = F16_toRoundedInt(velocity.fixY)                        │   │
│  │  playerHeadPos = aabb.min.y - yIntVelocity + globalPosition.y          │   │
│  │  playerFeetPos = aabb.max.y - yIntVelocity + globalPosition.y          │   │
│  │                                                                        │   │
│  │  Purpose: Prevents a ground tile from being detected as a wall         │   │
│  │  by offsetting the head/feet range based on current velocity.          │   │
│  │  A tile is only a wall if it overlaps between head and feet.           │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                                │
│  ┌─ ONE-WAY PLATFORM ERROR CORRECTION ────────────────────────────────────┐   │
│  │  oneWayPlatformErrorCorrection = 5 px                                  │   │
│  │  Condition: bottomEdgePos >= (playerFeetPos - 5)                       │   │
│  │  Allows snapping to platform if player is within 5px above it          │   │
│  │  Prevents "falling through" at high speeds or frame boundary           │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

#### Nivel 3 — Execution/Code

```
┌─ checkCollisions() [src/player.c:233] ───────────────────────────────────────┐
│                                                                               │
│  EXECUTION ORDER:                                                             │
│                                                                               │
│  1. collidingAgainstStair = FALSE (reset each frame)                          │
│  2. levelLimits = roomSize (AABB(0,768,0,768))                               │
│  3. Calculate playerBounds from globalPosition + aabb (or climbingStairAABB)  │
│  4. Calculate skin width: yIntVelocity, playerHeadPos, playerFeetPos          │
│  5. Convert bounds to tile coords: posToTile() → minTilePos, maxTilePos      │
│  6. tileBoundDifference = max - min (limits iteration count)                  │
│                                                                               │
│  7. HORIZONTAL LOOP (i = 0..tileBoundDifference.y):                           │
│     │  y = minTilePos.y + i                                                   │
│     │  RIGHT: getTileValue(maxTilePos.x, y)                                   │
│     │    GROUND → check skin width → levelLimits.max.x = tile.min.x          │
│     │    LADDER → stairLeftEdge, collidingAgainstStair = TRUE                 │
│     │  LEFT: getTileValue(minTilePos.x, y)                                    │
│     │    GROUND → check skin width → levelLimits.min.x = tile.max.x          │
│     │    LADDER → stairLeftEdge, collidingAgainstStair = TRUE                 │
│     │                                                                         │
│  8. APPLY HORIZONTAL: snap X, zero velocity if colliding                      │
│  9. RECALCULATE playerBounds and tile positions                               │
│                                                                               │
│ 10. VERTICAL LOOP (direction-dependent):                                      │
│     │  yIntVelocity >= 0 (falling/standing):                                  │
│     │    GROUND/ONE_WAY → error correction check → levelLimits.max.y         │
│     │    LADDER (top only) → onStair, levelLimits.max.y                      │
│     │  yIntVelocity < 0 (rising):                                             │
│     │    GROUND only → levelLimits.min.y (ceiling hit)                        │
│     │    LADDER → stairLeftEdge, collidingAgainstStair                        │
│     │                                                                         │
│ 11. RESOLVE:                                                                  │
│     │  Ceiling hit → snap Y, fixY = 0                                         │
│     │  Floor hit:                                                             │
│     │    y == 768 → falling = TRUE                                            │
│     │    else → onGround=TRUE, coyoteTime=10, jumping=FALSE, snap Y          │
│     │  Airborne → onGround=onStair=FALSE, coyoteTime--                       │
│                                                                               │
│  KEY HELPER FUNCTIONS:                                                        │
│    getTileValue(x,y) [levelgenerator.c:36] → currentMap[y][x]                │
│    getTileBounds(x,y) [physics.c:20] → AABB(x<<4, x<<4+16, y<<4, y<<4+16)  │
│    getTileLeftEdge(x) [physics.c:4] → x << 4                                 │
│    getTileRightEdge(x) [physics.c:8] → (x<<4) + 16                           │
│    getTileTopEdge(y) [physics.c:12] → y << 4                                  │
│    getTileBottomEdge(y) [physics.c:16] → (y<<4) + 16                          │
│    posToTile(pos) [physics.c:25] → (x>>4, y>>4)                              │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

### SEC.4: LEVEL LOADING SYSTEM

#### Nivel 1 — Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LEVEL LOADING SYSTEM                              │
│                                                                     │
│  Carrega um nivel completo: tileset visual, mapa, paleta,           │
│  gera o mapa de colisao na RAM, e inicia a musica.                  │
│                                                                     │
│  ┌─────┐    ┌─────────┐    ┌──────────┐    ┌──────────┐           │
│  │ ROM │ →  │ VDP/VRAM│ →  │  BG_A    │ →  │ DISPLAY  │           │
│  │tiles│    │ tileset │    │  tilemap  │    │ scrolled │           │
│  │.png │    │ loaded  │    │  created  │    │ by camera│           │
│  └─────┘    └─────────┘    └──────────┘    └──────────┘           │
│                                                                     │
│  ┌─────┐    ┌──────────┐                                           │
│  │ ROM │ →  │ RAM (2D) │   collisionMap[48][48] → currentMap       │
│  │const│    │ MEM_alloc│   48 rows × MEM_alloc(48 bytes each)      │
│  │array│    │ memcpy   │                                           │
│  └─────┘    └──────────┘                                           │
│                                                                     │
│  ┌─────┐    ┌──────────┐                                           │
│  │ VGM │ →  │ XGM_start│   sonic2Emerald.vgm (BGM)                │
│  │ WAV │    │ XGM_setPCM│  jump.wav (SFX, index 64)               │
│  └─────┘    └──────────┘                                           │
└─────────────────────────────────────────────────────────────────────┘
```

#### Nivel 2 — Variables/Conditions

```
┌─ LEVEL LOADING SYSTEM ────────────────────────────────────────────────────────┐
│                                                                                │
│  VISUAL PIPELINE:                                                              │
│    level_palette → PAL_setPalette(PAL0, data, DMA)                            │
│    level_tileset → VDP_loadTileSet(tileset, VDPTilesFilled, DMA)              │
│    level_map    → MAP_create(map, BG_A, TILE_ATTR_FULL(PAL0, ...))            │
│    VDPTilesFilled += level_tileset.numTile  (track VRAM usage)                │
│                                                                                │
│  COLLISION PIPELINE:                                                           │
│    collisionMap[48][48] (ROM, const u8) → LDtk + MadeWithUnity converter     │
│    generateCollisionMap():                                                     │
│      roomSize = AABB(0, 768, 0, 768)                                          │
│      roomTileSize = (48, 48)   [768 >> 4 = 48]                                │
│      currentMap = MEM_alloc(48 * sizeof(u8*))                                 │
│      for each row: MEM_alloc(48), memcpy from ROM                             │
│    → currentMap[y][x] is the runtime collision lookup                         │
│                                                                                │
│  AUDIO PIPELINE:                                                               │
│    XGM_startPlay(song) → sonic2Emerald.vgm as BGM                            │
│    XGM_setPCM(64, jump, sizeof(jump)) → registers jump SFX (in playerInit)   │
│                                                                                │
│  RESOURCES (res/resources.res):                                                │
│    SPRITE  player_sprite  "images/player.png"  3 3  FAST 5                    │
│    TILESET level_tileset  "images/level.png"   FAST ALL                        │
│    MAP     level_map      "images/level.png"   level_tileset FAST 0            │
│    PALETTE level_palette  "images/level.png"                                   │
│    XGM     song           "sound/sonic2Emerald.vgm"  AUTO                     │
│    WAV     jump           "sound/jump.wav"  XGM                                │
│                                                                                │
│  PALETTES:                                                                     │
│    PAL0 (LEVEL_PALETTE)  → level tiles                                        │
│    PAL1 (PLAYER_PALETTE) → player sprite                                      │
│    PAL2, PAL3            → unused (available for expansion)                   │
│                                                                                │
│  PLANES:                                                                       │
│    BG_A (TILEMAP_PLANE)  → level tilemap (scrolled by camera)                 │
│    BG_B                  → unused (no parallax background)                    │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

#### Nivel 3 — Execution/Code

```
┌─ BOOT SEQUENCE [src/main.c:9] ───────────────────────────────────────────────┐
│                                                                               │
│  main(resetType):                                                             │
│    if !resetType → SYS_hardReset()  (prevent soft-reset RAM bugs)            │
│    JOY_init()                                                                 │
│    SPR_init()                                                                 │
│    loadLevel()      ← [src/levels.c:9]                                        │
│    playerInit()     ← [src/player.c:29]                                       │
│    setupCamera()    ← [src/camera.c:11]                                       │
│    JOY_setEventHandler(inGameJoyEvent)                                        │
│    while(TRUE):                                                               │
│      updatePlayer()   ← [src/player.c:125]                                    │
│      updateCamera()   ← [src/camera.c:24]                                     │
│      SPR_update()     ← SGDK sprite engine flush                              │
│      SYS_doVBlankProcess() ← sync to VBlank                                  │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

┌─ loadLevel() [src/levels.c:9] ───────────────────────────────────────────────┐
│                                                                               │
│  1. PAL_setPalette(PAL0, level_palette.data, DMA)                            │
│  2. VDP_loadTileSet(&level_tileset, VDPTilesFilled, DMA)                     │
│  3. bga = MAP_create(&level_map, BG_A, TILE_ATTR_FULL(PAL0,...,VDPTilesFilled))│
│  4. VDPTilesFilled += level_tileset.numTile                                   │
│  5. generateCollisionMap(collisionMap)  → ROM to RAM copy                     │
│  6. XGM_startPlay(song)                                                       │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

┌─ generateCollisionMap() [src/levelgenerator.c:22] ───────────────────────────┐
│                                                                               │
│  Input: const u8 map[48][48] (from ROM, src/map.c)                           │
│  roomSize = AABB(0, 768, 0, 768)                                             │
│  roomTileSize = (48, 48)                                                     │
│  currentMap = MEM_alloc(48 * sizeof(u8*))  [48 pointers]                     │
│  for i in 0..47:                                                              │
│    currentMap[i] = MEM_alloc(48)           [48 bytes per row]                │
│    memcpy(currentMap[i], map[i], 48)       [copy from ROM]                   │
│  Total RAM: 48*4 + 48*48 = 192 + 2304 = 2496 bytes                          │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

### MAPA DE DEPENDENCIAS — PLATFORMER ENGINE

```
┌──────────────────────────────────────────────────────────────────────┐
│                     DEPENDENCY MAP                                   │
│                                                                      │
│  ┌──────────┐     ┌──────────┐     ┌───────────────┐     ┌────────┐ │
│  │ main.c   │────►│ levels.c │────►│levelgenerator │────►│ map.c  │ │
│  │ (entry)  │     │(loadLevel│     │ .c            │     │(colMap │ │
│  │          │     │ XGM play)│     │(generateColMap│     │ start) │ │
│  │          │     │          │     │ getTileValue) │     │        │ │
│  └──┬───┬───┘     └──────────┘     └───────────────┘     └────────┘ │
│     │   │                                ▲                           │
│     │   │         ┌──────────┐           │                           │
│     │   └────────►│ camera.c │           │                           │
│     │             │(deadzone)│           │                           │
│     │             │(scrollTo)│           │                           │
│     │             └──────────┘           │                           │
│     │                                    │                           │
│     │             ┌──────────┐    ┌──────┴────┐                      │
│     └────────────►│ player.c │───►│ physics.c │                      │
│                   │(movement)│    │(tileEdge) │                      │
│                   │(collision│    │(posToTile)│                      │
│                   │(animation│    │(tileBounds│                      │
│                   │(death)   │    └───────────┘                      │
│                   └────┬─────┘                                       │
│                        │                                             │
│                   ┌────┴─────┐                                       │
│                   │ global.c │                                       │
│                   │(gravity) │                                       │
│                   │(input)   │                                       │
│                   │(roomSize,│                                       │
│                   │ bga, VDP)│                                       │
│                   └──────────┘                                       │
│                                                                      │
│  HEADERS:                                                            │
│    types.h  — AABB, Vect2D_u8/s8, newAABB(), newVector2D_*()       │
│    global.h — GROUND(1), LADDER(2), ONE_WAY(4), TILEMAP_PLANE=BG_A │
│               InputState, gravityScale, roomSize, bga, VDPTilesFilled│
│    player.h — struct pBody (sprite, aabb, velocity, states, pos)    │
│    camera.h — cameraPosition, setupCamera(), updateCamera()         │
│    physics.h — getTile*Edge(), getTileBounds(), posToTile()         │
│    levelgenerator.h — getTileValue(), generateCollisionMap()        │
│    levels.h — Level struct, loadLevel()                             │
│    map.h    — levelStartPos, collisionMap[48][48]                   │
│                                                                      │
│  TOTAL: 7 .c source + 8 .h headers + 1 .res                        │
└──────────────────────────────────────────────────────────────────────┘
```

### TABELA DE CONSTANTES — PLATFORMER ENGINE

| Constante | Valor | Arquivo | Uso |
|---|---|---|---|
| `gravityScale` | `FIX16(0.5)` | `global.c:4` | Aceleracao vertical por frame |
| `speed` | `2` | `player.c:47` | Vel. horizontal max (px/frame) |
| `jumpSpeed` | `7` | `player.c:50` | Vel. inicial do pulo (px/frame) |
| `maxFallSpeed` | `6` | `player.c:49` | Terminal velocity (px/frame) |
| `climbingSpeed` | `1` | `player.c:48` | Vel. na escada (px/frame) |
| `acceleration` | `FIX16(0.25)` | `player.c:52` | Aceleracao horizontal |
| `deceleration` | `FIX16(0.2)` | `player.c:53` | Desaceleracao no chao |
| `coyoteTime` | `10` frames | `player.c:13` | Janela de pulo apos sair do chao |
| `jumpBufferTime` | `10` frames | `player.c:15` | Buffer de input de pulo |
| `dieDelay` | `10` frames | `player.c:22` | Delay antes do hard reset |
| `oneWayPlatformErrorCorrection` | `5` px | `player.c:24` | Tolerancia de snap em one-way |
| `stairPositionOffset` | `4` px | `player.c:27` | Offset X ao escalar |
| `AABB (normal)` | `(4,20,4,24)` | `player.c:38` | Hitbox 16x20 px |
| `AABB (climbing)` | `(8,20,4,24)` | `player.c:40` | Hitbox 12x20 px (narrower) |
| `GROUND_TILE` | `1` | `global.h:12` | Tile solido |
| `LADDER_TILE` | `2` | `global.h:13` | Tile escada |
| `ONE_WAY_PLATFORM_TILE` | `4` | `global.h:14` | Plataforma unidirecional |
| `levelStartPos` | `{74, 665}` | `map.c:3` | Spawn point (px) |
| `roomSize` | `(0,768,0,768)` | `levelgenerator.c:23` | Limites do nivel (px) |
| `Screen` | `320x224` | implicit | Resolucao Mega Drive |
| `Tile size` | `16x16` px | `physics.c` | Via bitshift `<<4` / `>>4` |
| `Deadzone center` | `(160,112)` | `main.c:21` | Centro da tela |
| `Deadzone size` | `20x20` px | `main.c:21` | Zona morta da camera |
| `Camera clamp X` | `0..448` | `camera.c:41` | 768-320 |
| `Camera clamp Y` | `0..544` | `camera.c:42` | 768-224 |
| `SFX index` | `64` | `player.c:56` | PCM index do jump.wav |
| `SFX channel` | `SOUND_PCM_CH1` | `player.c:136` | Canal PCM do pulo |

---

# TABELA COMPARATIVA GERAL

| Engine | Genero | Resolucao | State Machine | Collision | Audio | Save |
|---|---|---|---|---|---|---|
| **NEXZR MD** | SHMUP | 320x240 | Entity callbacks | None (TODO) | - | - |
| **Mortal Kombat Plus** | Luta | 320x224 | gRoom enum switch | BBox (TODO) | XGM2 PCM+BGM | - |
| **Goblin SGDK** | Aventura RPG | 256x224 | Flags/booleans | Tile-based | XGM PCM | SRAM 3 slots |
| **Vigilante Tutorial** | Beat'em Up | 320x224 | G_SEQUENCE enum | BBox + margins | Music+SFX | - |
| **Town Quest** | Action Mini | 320x224 | current_stage int | Distance-based | XGM PCM+BGM | - |
| **State Machine RPG** | Action RPG | 320x224 | Single loop | 1D array tile | - | - |
| **Mega Metroid** | Metroidvania | 256x224 | Single boot loop | 2D tile grid + slopes | XGM PCM | - |
| **PlatformerEngine** | Plataforma | 320x224 | Single boot loop | 2D tile 16px + one-way + ladder | XGM PCM+BGM | - |

| Engine | Player Physics | Camera | Enemy System | Unique Feature |
|---|---|---|---|---|
| **NEXZR MD** | Fixed vel(2), 4-dir | None (fixed) | Entity manager | Starfield warp VFX |
| **MK Plus** | State machine + anims | Midpoint scroll | 10 fighters | Venetian blind reveal |
| **Goblin SGDK** | Grid movement | Room-based | Random encounter | Cellular Automata procgen |
| **Vigilante** | 15 states, jump+kick | Side-scroll | 6 types, wave spawn | Combo-ready input buffer |
| **Town Quest** | L/R + varazo attack | Fixed | Fall from top, 10 max | Grace period + transform |
| **State Machine RPG** | 4-dir + swing | Center-follow clamp | None (single file) | 1D collision array |
| **Mega Metroid** | Gravity+jump, fix16 vel | Center-follow clamp | None (struct ready) | Slope tiles (L/R) + 8px grid |
| **PlatformerEngine** | Accel/decel+coyote+buffer | Deadzone 20x20 | None (engine base) | Coyote time + variable jump + ladder climb |
