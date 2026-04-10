# System Mechanics Roadmap - PlatformerEngine [VER.1.0] [SGDK 211] [GEN] [ENGINE] [PLATAFORMA]

**Tipo**: Logic Vision / Mind Map / Mario World-Style System Dissection
**Profundidade**: 3 Niveis (Design → Variables/Conditions → Execution/Code)
**Fonte**: Upstream completo em `PlatformerEngine Toolkit/.../upstream/PlatformerEngine/`

---

## ARVORE MESTRA DE SISTEMAS

```
                    ╔══════════════════════════════════════╗
                    ║   PLATFORMER ENGINE [VER.1.0]        ║
                    ║   SGDK 2.11 | Mega Drive / Genesis   ║
                    ╚══════════════════╤═══════════════════╝
                                       │
          ┌────────────────┬───────────┴──────────┬──────────────────┐
          │                │                      │                  │
    ┌─────┴─────┐   ┌─────┴──────┐   ┌──────────┴────────┐  ┌─────┴──────┐
    │  PLAYER   │   │  CAMERA    │   │    COLLISION      │  │   LEVEL    │
    │ MOVEMENT  │   │  DEADZONE  │   │    SYSTEM         │  │  LOADING   │
    │  SYSTEM   │   │  SYSTEM    │   │                   │  │   SYSTEM   │
    └─────┬─────┘   └─────┬──────┘   └──────────┬────────┘  └─────┬──────┘
          │               │                      │                 │
     [SEC.1]          [SEC.2]               [SEC.3]           [SEC.4]
```

---

## SECAO 1: PLAYER MOVEMENT SYSTEM

### Nivel 1 — Design (O que o jogador ve)

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
└─────────────────────────────────────────────────────────────────────┘
```

### Nivel 2 — Variables & Conditions (Regras do sistema)

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
│  │                                                                           │ │
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

### Nivel 3 — Execution (Funcoes exatas e fluxo de codigo)

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
│     │  → checkCollisions()  [see SECTION 3]                                   │
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
│  Called by: inGameJoyEvent() [src/main.c:41] (JOY callback, "pseudo-parallel")│
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

## SECAO 2: CAMERA DEADZONE SYSTEM

### Nivel 1 — Design

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

### Nivel 2 — Variables & Conditions

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

### Nivel 3 — Execution

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

## SECAO 3: COLLISION SYSTEM

### Nivel 1 — Design

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

### Nivel 2 — Variables & Conditions

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

### Nivel 3 — Execution

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

## SECAO 4: LEVEL LOADING SYSTEM

### Nivel 1 — Design

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

### Nivel 2 — Variables & Conditions

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

### Nivel 3 — Execution

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

## MAPA COMPLETO DE DEPENDENCIAS

```
 ┌──────────┐     ┌──────────┐     ┌───────────────┐     ┌───────────┐
 │ main.c   │────►│ levels.c │────►│levelgenerator.c│────►│   map.c   │
 │ (entry)  │     │(loadLevel│     │(generateColMap)│     │(collisionMap
 │          │     │ XGM play)│     │(getTileValue)  │     │ levelStart)│
 └──┬───┬───┘     └──────────┘     └───────────────┘     └───────────┘
    │   │                                  ▲
    │   │         ┌──────────┐             │
    │   └────────►│ camera.c │             │
    │             │(deadzone)│             │
    │             │(scrollTo)│             │
    │             └──────────┘             │
    │                                      │
    │             ┌──────────┐     ┌───────┴───┐
    └────────────►│ player.c │────►│ physics.c │
                  │(movement)│     │(tileEdge) │
                  │(collision│     │(posToTile) │
                  │(animation│     │(tileBounds)│
                  │(death)   │     └───────────┘
                  └──────────┘
                       │
                  ┌────┴────┐
                  │global.c │
                  │(gravity)│
                  │(input)  │
                  │(roomSize│
                  │ bga,VDP)│
                  └─────────┘

 HEADERS:
   types.h ← AABB, Vect2D_u8, Vect2D_s8, newAABB(), newVector2D_*()
   global.h ← GROUND_TILE(1), LADDER_TILE(2), ONE_WAY_PLATFORM_TILE(4)
              TILEMAP_PLANE(BG_A), PLAYER_PALETTE(PAL1), LEVEL_PALETTE(PAL0)
              InputState, gravityScale, roomSize, playerBounds, bga, VDPTilesFilled
   player.h ← struct pBody (sprite, aabb, velocity, states, position)
   camera.h ← cameraPosition, setupCamera(), updateCamera()
   physics.h ← getTile*Edge(), getTileBounds(), posToTile()
   levelgenerator.h ← getTileValue(), generateCollisionMap(), freeCollisionMap()
   levels.h ← Level struct, loadLevel()
   map.h ← levelStartPos, collisionMap[48][48]
```

---

## TABELA DE CONSTANTES CRITICAS

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
| `SFX priority` | `15` (max) | `player.c:136` | Prioridade maxima |
