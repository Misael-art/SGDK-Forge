# Level Topology Map — SGDK_Engines
## Visao Espacial de Todas as Engines (Estilo Castlevania / Mapa do Mundo)

> Documento gerado por varredura profunda do codigo-fonte de todos os 92 projetos
> em `SGDK_Engines/`. Abaixo estao os mapas de topologia dos projetos que possuem
> estrutura de fases/salas/cenas implementada com progressao real.

---

## 1. MORTAL KOMBAT PLUS ENGINE

### Mapa de Salas (Room Flow)

```
 ╔═══════════════════════════════════════════════════════════════════════════╗
 ║  MORTAL KOMBAT PLUS — Fluxo de Telas (gRoom)                           ║
 ╚═══════════════════════════════════════════════════════════════════════════╝

  [TELA_DEMO_INTRO]                                                 (gRoom=0)
     │
     │ (Frame 1)     ┌──────────────────────┐
     ├──────────────>│ Brain At Work Logo    │ (gFrames 1~200)
     │               │ loadBrainAtWorkScreen │ PAL_fadeIn -> PAL_fadeOut
     │               └──────────────────────┘
     │ (Frame 230)   ┌──────────────────────┐
     ├──────────────>│ Midway Presents Logo  │ (gFrames 230)
     │               │ XGM2_playPCM(mus_midway)
     │               └──────────────────────┘
     │ (Frame 370)   ┌──────────────────────┐
     ├──────────────>│ MK Title Screen       │ (gFrames 370~700)
     │               │ XGM2_playPCM(mus_title)
     │               └──────────────────────┘
     │ (Frame 700)   ┌──────────────────────┐
     ├──────────────>│ "GORO LIVES" Screen   │ (gFrames 700~855)
     │               │ SND_PCM4(mus_goro_lives)
     │               └──────────────────────┘
     │ (Frame 855)   ┌──────────────────────┐
     ├──────────────>│ Goro Bio + Historia   │ (gFrames 855~1280)
     │               │ typewriterEffect()     │
     │               └──────────────────────┘
     │ (Frame 1300)  ┌──────────────────────────────────────────────────┐
     ├──────────────>│ Carousel de Bios (7 fighters)                    │
     │               │ JOHNNY -> KANO -> RAIDEN -> LIU_KANG ->          │
     │               │ SUBZERO -> SCORPION -> SONYA -> (loop)           │
     │               │ loadBioScreen(getFighterBio(id))                 │
     │               │ XGM2_play(mus_the_beginning)                     │
     │               └──────────────────────────────────────────────────┘
     │ (Frame 2100)  Reloop
     │
     │  *** START pressionado (gFrames > 410) ***
     v
  [TELA_START]                                                      (gRoom=2)
     │
     │  ┌────────────────────────────────────────────────────┐
     │  │  Main Menu (Press Start Screen)                    │
     │  │  processPressStart()                               │
     │  │                                                    │
     │  │  mainMenuOpt = 0: START ◄──────── (D-pad UP)      │
     │  │                     │                              │
     │  │              (D-pad DOWN)                          │
     │  │                     v                              │
     │  │  mainMenuOpt = 1: OPTIONS ──────► (D-pad UP)      │
     │  │                     │                              │
     │  │              (START pressed)                       │
     │  │                     v                              │
     │  │  mainMenuOpt = 2: LANGUAGE SELECT                  │
     │  │       LEFT/RIGHT: alterna EN <-> BR                │
     │  │       B: volta ao menu                             │
     │  │                                                    │
     │  │  BG Scroll: vecTilesScreen[] c/ ACELERACAO=2       │
     │  │  Sprites: GE[0]=spMainMenu, GE[1]=spOpt           │
     │  └────────────────────────────────────────────────────┘
     │
     │  B pressed (mainMenuOpt==0) --> volta TELA_DEMO_INTRO
     │  START pressed (mainMenuOpt==0)
     v
  [SELECAO_PERSONAGENS]                                             (gRoom=3)
     │
     │  ┌──────────────────────────────────────────────────────────────────┐
     │  │  Character Select Screen                                        │
     │  │  processSelecaoPersonagens()                                     │
     │  │                                                                  │
     │  │  Grid de Personagens (Navigation Map):                           │
     │  │                                                                  │
     │  │      ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
     │  │      │ J.CAGE   │──│  KANO    │──│ SUB-ZERO │──│  SONYA   │    │
     │  │      │(20,44)   │  │(76,44)   │  │(188,44)  │  │(244,44)  │    │
     │  │      └──────────┘  └────┬─────┘  └────┬─────┘  └──────────┘    │
     │  │        ^      \          │              │           /      ^     │
     │  │        │  (wrap)         v              v        (wrap)    │     │
     │  │        │          ┌──────────┐  ┌──────────┐              │     │
     │  │        └──────────│ RAIDEN   │──│ LIU KANG │──────────────┘     │
     │  │                   │(76,108)  │  │(132,108) │                    │
     │  │                   └──────────┘  └──────────┘                    │
     │  │                         ^              │                        │
     │  │                         │              v                        │
     │  │                   ┌──────────────────────────┐                  │
     │  │                   │      SCORPION            │                  │
     │  │                   │      (188,108)            │                  │
     │  │                   └──────────────────────────┘                  │
     │  │                                                                  │
     │  │  P1 Spawn: KANO (id default)    P2 Spawn: SUBZERO              │
     │  │  P1 pos: (10, 104) PAL2         P2 pos: (182, 104) PAL3        │
     │  │                                                                  │
     │  │  SFX: snd_gongo (efeito persiana), snd_cursor (move cursor)    │
     │  │  BGM: mus_select_player (XGM2_play)                             │
     │  │  Efeito: VenetianBlindsEffect (persiana de 7 faixas)           │
     │  │                                                                  │
     │  │  START: Seleciona personagem -> XGM2_playPCM(loc_xxx)          │
     │  │         SPR portrait blink effect (30 frames)                   │
     │  │  Ambos selecionados: countDown 150 -> PAL_fadeOutAll -> exit    │
     │  └──────────────────────────────────────────────────────────────────┘
     │
     │  Ambos selecionados + countdown=0
     v
  [BONUS_STAGE]                                                     (gRoom=4)
     │
     │  ┌────────────────────────────────────────────────┐
     │  │  Test Your Might (Bonus Stage)                 │
     │  │  processBonusStage()                           │
     │  │                                                │
     │  │  P1: spKanoBonus (24, 56)  PAL2                │
     │  │  P2: spKanoBonus (176, 56) PAL3                │
     │  │  Bloco P1: spWood (16, 128)                    │
     │  │  Bloco P2: spWood (168, 128)                   │
     │  │  Mensagem: spMessage1 (56, 24) [60 frames]     │
     │  │  BGs: tym_bga (BG_A), tym_bgb (BG_B)           │
     │  │                                                │
     │  │  ** Loop infinito (while TRUE) — sem saida **  │
     │  └────────────────────────────────────────────────┘
     │
     │  (Transicao manual/nao implementada ainda)
     v
  [PALACE_GATES]                                                    (gRoom=5)
     │
     │  ┌────────────────────────────────────────────────────────┐
     │  │  Palace Gates (Arena de Luta)                          │
     │  │  initPalaceGatesRoom()                                 │
     │  │                                                        │
     │  │  Cenario: 928 x 232 px (pg_bga + pg_bgb)              │
     │  │  Scroll: HSCROLL_LINE + auto-scroll (scrollOffset++)   │
     │  │                                                        │
     │  │  P1: spr_subzero (24, 96) PAL2  PARADO                │
     │  │  P2: spr_reptile (168, 96) PAL3 PARADO (flipped)      │
     │  │                                                        │
     │  │  ** Arena sem saida programada — luta ocorre aqui **   │
     │  └────────────────────────────────────────────────────────┘
```

### Tabela de Traducao Tecnica — Mortal Kombat Plus

| Sala no Diagrama | Enum GAME_ROOM | Variavel | Arquivo de Codigo | Funcao Principal |
|---|---|---|---|---|
| Brain At Work | `TELA_DEMO_INTRO` (0) | `gRoom` | `src/rooms/intro_demo_room.c` | `loadBrainAtWorkScreen()` |
| Midway Logo | `TELA_DEMO_INTRO` (0) | `gRoom` | `src/rooms/intro_demo_room.c` | `loadMidwayTitleMKScreen()` |
| MK Title | `TELA_DEMO_INTRO` (0) | `gRoom` | `src/rooms/intro_demo_room.c` | `loadMidwayTitleMKScreen()` |
| Goro Lives | `TELA_DEMO_INTRO` (0) | `gRoom` | `src/rooms/intro_demo_room.c` | `loadGoroLivesScreen()` |
| Bio Carousel | `TELA_DEMO_INTRO` (0) | `gRoom` | `src/rooms/intro_demo_room.c` | `loadBioScreen()` |
| Main Menu | `TELA_START` (2) | `gRoom` | `src/rooms/press_start_room.c` | `processPressStart()` |
| Char Select | `SELECAO_PERSONAGENS` (3) | `gRoom` | `src/rooms/char_select_room.c` | `processSelecaoPersonagens()` |
| Bonus Stage | `BONUS_STAGE` (4) | `gRoom` | `src/rooms/bonus_stage_room.c` | `processBonusStage()` |
| Palace Gates | `PALACE_GATES` (5) | `gRoom` | `src/rooms/palace_gates_room.c` | `initPalaceGatesRoom()` |

---

## 2. GOBLIN SGDK (Aventura / RPG Procedural)

### Mapa do Mundo Procedural

```
 ╔═══════════════════════════════════════════════════════════════════════════╗
 ║  GOBLIN SGDK — Mundo Procedural (9x9 World Grid)                       ║
 ╚═══════════════════════════════════════════════════════════════════════════╝

  [SEGA LOGO] ──> [TITLE SCREEN] ──> [OVERWORLD 9x9]
   showSegaLogo()   displayTitle()     makeMap() + bigMapCA()

                    OVERWORLD (WORLD_TILES[9][9][14][16])
    ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
    │(0,0)│(0,1)│(0,2)│(0,3)│(0,4)│(0,5)│(0,6)│(0,7)│(0,8)│
    ├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
    │(1,0)│(1,1)│     │     │     │     │     │     │(1,8)│
    ├─────┼─────┤     │     │     │     │     │     ├─────┤
    │(2,0)│     │ Cada sala = 14x16 tiles                 │(2,8)│
    ├─────┤     │ Gerado via Cellular Automata            ├─────┤
    │(3,0)│     │ (bigMapCA -> WORLD_LAYOUT_CA[112][128]) │(3,8)│
    ├─────┤     │                                         ├─────┤
    │(4,0)│     │  [CASA]  <-- Player House (showPlayerHouse)     │
    ├─────┤     │  [LOJA]  <-- Merchant (findMerchantPosition)   ├─────┤
    │(5,0)│     │  [CAVE]  <-- Cave Entrance (CAVE_ENTRANCE_TILE=15) │
    ├─────┤     │                                         ├─────┤
    │(6,0)│     │ Portas entre salas: makeDoorways()       │(6,8)│
    ├─────┤     │ Bordas: matchRoomEdges(roomY, roomX)     ├─────┤
    │(7,0)│     │                                         │(7,8)│
    ├─────┼─────┤                                         ├─────┤
    │(8,0)│(8,1)│(8,2)│(8,3)│(8,4)│(8,5)│(8,6)│(8,7)│(8,8)│
    └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
      ^                                               |
      |  currentWorldX / currentWorldY = posicao atual
      |  displayRoom() redesenha ao mudar de sala
      |
      v
    ┌─────────────────────────────────────┐
    │  DUNGEON (Cave System)              │
    │  enterCave(level)                   │
    │  generateCaveLevel(level)           │
    │  generateMaze() + enhanceMaze()     │
    │  ensurePathToExit()                 │
    │                                     │
    │  CAVE_ENTRANCE_TILE (15) = entrada  │
    │  EXIT_TILE (9) = saida              │
    │  Treasure sprites (checkTreasureCollisions) │
    │                                     │
    │  exitCave() -> retorna ao overworld │
    └─────────────────────────────────────┘

  ┌─────────────────────────────────────┐
  │  PLAYER HOUSE (Interior)            │
  │  showPlayerHouse()                  │
  │  - Press DOWN to Exit               │
  │  - Hold A to Rest (player_hp++)     │
  │  - Cooldown: PLAYER_HOUSE_COOLDOWN  │
  │  - Background: house image          │
  └─────────────────────────────────────┘

  ┌─────────────────────────────────────┐
  │  BATTLE SCREEN (Random Encounter)   │
  │  randomEncounter()                  │
  │  displayBattle()                    │
  │  - selection: Attack / Defend       │
  │  - attack() -> goblinAttack()       │
  │  - itemDrop() (loot)                │
  │  - levelUp() (exp -> player_level)  │
  │  - endBattle()                      │
  │  - gameOver() se player_hp <= 0     │
  └─────────────────────────────────────┘

  ┌─────────────────────────────────────┐
  │  MERCHANT MENU                      │
  │  showMerchMenu()                    │
  │  handleMerchantMenuInput()          │
  │  - buyItem(item, qty, price)        │
  │  - sellItem(item, qty, price)       │
  │  - MAX_MERCHANT_INTERACTIONS limit  │
  └─────────────────────────────────────┘
```

### Tabela de Traducao Tecnica — Goblin SGDK

| Local no Mapa | Variavel/Array | Arquivo | Funcao |
|---|---|---|---|
| World Grid 9x9 | `WORLD_TILES[9][9][14][16]` | `inc/makemap.h` | `makeMap()` |
| Sala Atual | `LEVEL_TILES[14][16]` | `inc/makemap.h` | `displayRoom()` |
| World Layout (CA) | `WORLD_LAYOUT_CA[112][128]` | `inc/makemap.h` | `bigMapCA()` |
| Posicao no Mundo | `currentWorldX`, `currentWorldY` | `inc/makemap.h` | `updateCurrentRoom()` |
| Cave/Dungeon | `inCave` (bool) | `inc/dungeonGenerator.h` | `enterCave(level)`, `exitCave()` |
| Cave Entrance | `caveEntranceRow`, `caveEntranceCol` | `inc/makemap.h` | `spawnCaveEntrances()` |
| Player House | `bInsideHouse` (bool) | `inc/globals.h` | `showPlayerHouse()` |
| Battle | `bBattleStarted`, `bBattleOngoing` | `inc/globals.h` | `randomEncounter()`, `displayBattle()` |
| Merchant | `bShowMerchMenu` (bool) | `inc/player.h` | `showMerchMenu()` |
| Inventario | `inventory[4][4]` | `inc/inventory.h` | `addItem()`, `removeItem()` |
| Save/Load | Slot 0-2 (SRAM 68 bytes each) | `src/gamemanager.c` | `sramSave(slot)`, `sramLoad(slot)` |
| Player Spawn | `playerPosX`, `playerPosY` | `inc/player.h` | `displayPlayer()` |

---

## 3. MEGA METROID (Plataforma / Metroidvania)

### Mapa de Areas (Crateria)

```
 ╔═══════════════════════════════════════════════════════════════════════════╗
 ║  MEGA METROID — Mapa de Crateria (2 areas definidas)                    ║
 ╚═══════════════════════════════════════════════════════════════════════════╝

  [BOOT] ──> boot() ──> levelInit(TILE_USER_INDEX) ──> playerInit() ──> cameraInit()
                               │
                    curr_level_index = 0
                               │
                               v
  ┌───────────────────────────────────────────────────────────────────┐
  │  CRATERIA 1 (level_crateria_1)                                    │
  │  Collision Map: map_collision_crateria_1[156][288]                │
  │  Tamanho: 2304 x 1248 pixels (288*8 x 156*8)                    │
  │                                                                   │
  │  Tiles de Colisao:                                                │
  │    0 = GROUND_TILE (solido)                                       │
  │    2 = SLOPE_RIGHT_TILE (rampa direita)                           │
  │    3 = SLOPE_LEFT_TILE (rampa esquerda)                           │
  │                                                                   │
  │  Player Spawn: tileToPixel(32) = x256,                           │
  │                map_height - tileToPixel(6) - 24 = fundo           │
  │                                                                   │
  │  ┌────────────────────────────────────────────────────────┐       │
  │  │  Mapa Fisico (288 tiles largura x 156 tiles altura)   │       │
  │  │                                                        │       │
  │  │  ████████████████████░░░░░░░░████████████████████████  │       │
  │  │  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░████████  │       │
  │  │  ████░░░░░░░░SPAWN░░░░░░░░░░░░░░░░░░░░░░░░░████████  │       │
  │  │  ████░░░░░░░░░(P)░░░░░/▓▓\░░░░░░░░░░░░░░░░█████████  │       │
  │  │  ████████░░░░░░░░░░░░/rampa\░░░░░░░░░████████████████  │       │
  │  │  ████████████████████████████████░░░░░████████████████  │       │
  │  │       ^slope_left    ^slope_right                      │       │
  │  │                                                        │       │
  │  │  Gravidade: GRAVITY = FIX16(0.22), max = 300           │       │
  │  │  Pulo: JUMP = FIX16(6.6)                               │       │
  │  │  Velocidade: FIX16(2.3) px/frame                       │       │
  │  └────────────────────────────────────────────────────────┘       │
  └───────────────────────────────────────────────────────────────────┘
        │
        │  (curr_level_index = 1 — preparado mas nao ativado)
        v
  ┌───────────────────────────────────────────────────────────────────┐
  │  CRATERIA 2 (level_crateria_2)         ** NAO CARREGADO AINDA ** │
  │  Collision Map: map_collision_crateria_2[160][160]                │
  │  Tamanho: 1280 x 1280 pixels (160*8 x 160*8)                    │
  │  Slot: all_level_defs[1] (disponivel para ativacao)              │
  └───────────────────────────────────────────────────────────────────┘

  Notas:
  - Camera segue player com limites de borda
  - Background (BG_B) fixo (scroll 0,0)
  - Foreground (BG_A) com MAP_scrollTo
  - SFX: jump_sfx (XGM PCM channel 2, index 64)
  - Sem sistema de portas/transicoes entre areas implementado
```

### Tabela de Traducao Tecnica — Mega Metroid

| Elemento | Variavel/Struct | Arquivo | Funcao |
|---|---|---|---|
| Nivel Atual | `curr_level_index` (u8) | `src/main.c` | `boot()` |
| Array de Niveis | `all_level_defs[2]` (const level_def*) | `src/main.c` | `levelInit()` |
| Def. Crateria 1 | `level_crateria_1` (level_def) | `inc/map_crateria_1.h` | — |
| Def. Crateria 2 | `level_crateria_2` (level_def) | `inc/map_crateria_2.h` | — |
| Mapa Colisao | `map_collision[156][288]` | `inc/map.h` | `checkTileCollisions()` |
| Tamanho da Sala | `roomSize` (AABB) | `src/main.c` | `levelInit()` |
| Jogador | `player` (Entity) | `src/main.c` | `playerInit()`, `playerUpdate()` |
| Camera | `camera` (Camera) | `src/main.c` | `updateCamera()`, `setCameraPosition()` |
| Tile Ground | `GROUND_TILE = 0` | `inc/map.h` | — |
| Tile Slope R | `SLOPE_RIGHT_TILE = 2` | `inc/map.h` | — |
| Tile Slope L | `SLOPE_LEFT_TILE = 3` | `inc/map.h` | — |

---

## 4. VIGILANTE TUTORIAL (Beat-em-up / Briga de Rua)

### Mapa de Progressao (5 Levels + Intermedes)

```
 ╔═══════════════════════════════════════════════════════════════════════════╗
 ║  VIGILANTE TUTORIAL — Fluxo Completo (G_SEQUENCE + G_LEVEL)             ║
 ╚═══════════════════════════════════════════════════════════════════════════╝

  [SEQUENCE_LOGO] ─────> [SEQUENCE_TITLE] ─────> [SEQUENCE_RANKING]
   init_LOGO()            init_TITLE()            init_RANKING()
   sequence_LOGO()        sequence_TITLE()        sequence_RANKING()
   logo_Callback          title_Callback          ranking_Callback
        │                      │                        │
        │                      │                        │
        │          ┌───────────┴───────────┐            │
        │          │  TITLE MENU           │            │
        │          │  mainMenuOpt:          │            │
        │          │  LEVEL_OPTION (0)      │            │
        │          │  LIVES_OPTION (1)      │            │
        │          └───────────┬───────────┘            │
        │                      │ START                   │
        v                      v                         v

  ┌─────────────────────────────────────────────────────────────────────┐
  │                        GAME LOOP (5 Levels)                         │
  │                                                                     │
  │  LEVEL 1                                                            │
  │  ┌────────────────────────┐    ┌────────────────────────┐          │
  │  │ INTERMEDE_1            │───>│ LEVEL_1                │          │
  │  │ init_INTERMEDE_1()     │    │ init_LEVEL()           │          │
  │  │ sequence_INTERMEDE_1() │    │ sequence_LEVEL_1()     │          │
  │  │ (Cutscene/Story)       │    │ player_Callback        │          │
  │  │ sprite_MADONNA         │    │ TABLE_SPAWN_LEVEL_1[72]│          │
  │  └────────────────────────┘    │                        │          │
  │                                │  Waves (8 groups x 9): │          │
  │                                │   8x DUDE + 1x BOSS    │          │
  │                                │                        │          │
  │                                │  Wave 1: 8 DUDE +      │          │
  │                                │          KNIFE_MAN(boss)│         │
  │                                │  Wave 2: 8 DUDE +      │          │
  │                                │          STICK_MAN(boss)│         │
  │                                │  Wave 3: 8 DUDE +      │          │
  │                                │          CHAIN_MAN(boss)│         │
  │                                │  Wave 4: 8 DUDE +      │          │
  │                                │          PUNK (boss)    │         │
  │                                │  Waves 5-8: repeat...   │         │
  │                                │                        │          │
  │                                │  Weapon: nunchuk at     │          │
  │                                │  (216, 168) pixels     │          │
  │                                └───────────┬────────────┘          │
  │                                             │ G_LEVEL++            │
  │                                             v                      │
  │  LEVEL 2                                                            │
  │  ┌────────────────────────┐    ┌────────────────────────┐          │
  │  │ INTERMEDE_2            │───>│ LEVEL_2                │          │
  │  │ init_INTERMEDE_2()     │    │ sequence_LEVEL_2()     │          │
  │  └────────────────────────┘    └───────────┬────────────┘          │
  │                                             │                      │
  │  LEVEL 3                                    v                      │
  │  ┌────────────────────────┐    ┌────────────────────────┐          │
  │  │ INTERMEDE_3            │───>│ LEVEL_3                │          │
  │  │ init_INTERMEDE_3()     │    │ sequence_LEVEL_3()     │          │
  │  └────────────────────────┘    └───────────┬────────────┘          │
  │                                             │                      │
  │  LEVEL 4                                    v                      │
  │  ┌────────────────────────┐    ┌────────────────────────┐          │
  │  │ INTERMEDE_4            │───>│ LEVEL_4                │          │
  │  │ init_INTERMEDE_4()     │    │ sequence_LEVEL_4()     │          │
  │  └────────────────────────┘    └───────────┬────────────┘          │
  │                                             │                      │
  │  LEVEL 5 (FINAL)                            v                      │
  │  ┌────────────────────────┐    ┌────────────────────────┐          │
  │  │ INTERMEDE_5            │───>│ LEVEL_5                │          │
  │  │ init_INTERMEDE_5()     │    │ sequence_LEVEL_5()     │          │
  │  └────────────────────────┘    └───────────┬────────────┘          │
  │                                             │                      │
  └─────────────────────────────────────────────┼──────────────────────┘
                                                │
                                                v
                                   [SEQUENCE_HI_SCORE]
                                    init_HI_SCORE()
                                    hi_score_Callback
                                    - G_RANK
                                    - TABLE_SELECTED_LETTERS[3]
                                    -> volta ao SEQUENCE_TITLE
```

### Tabela de Traducao Tecnica — Vigilante Tutorial

| Elemento | Define/Variavel | Arquivo | Funcao |
|---|---|---|---|
| Sequencia Atual | `G_SEQUENCE` (u8) | `src/include/variables.h` | `main()` switch |
| LOGO | `SEQUENCE_LOGO = 0` | `src/include/variables.h` | `init_LOGO()`, `sequence_LOGO()` |
| TITLE | `SEQUENCE_TITLE = 1` | `src/include/variables.h` | `init_TITLE()`, `sequence_TITLE()` |
| RANKING | `SEQUENCE_RANKING = 2` | `src/include/variables.h` | `init_RANKING()` |
| INTERMEDE | `SEQUENCE_INTERMEDE = 3` | `src/include/variables.h` | `init_INTERMEDE_N()` |
| GAME | `SEQUENCE_GAME = 4` | `src/include/variables.h` | `init_LEVEL()`, `sequence_LEVEL_N()` |
| HI_SCORE | `SEQUENCE_HI_SCORE = 5` | `src/include/variables.h` | `init_HI_SCORE()` |
| Level Atual | `G_LEVEL` (u8, 1-5) | `src/include/variables.h` | — |
| Fase do Level | `G_PHASE_LEVEL` (ENTER/PLAY/END) | `src/include/variables.h` | — |
| Enemy Spawn Data | `TABLE_SPAWN_LEVEL_1[72]` | `src/include/tables_LEVELS.c` | — |
| Enemy Types | `TABLE_ENEMY_TYPE[6]` | `src/include/tables_LEVELS.c` | — |
| Spawn Index | `G_SPAWN_INDEX`, `G_SPAWN_MAX_INDEX` | `src/include/variables.h` | — |
| Enemies Active | `LIST_ENEMIES[4]` (struct_ENEMY_) | `src/include/variables.h` | — |
| Weapon Spawn | `TABLE_SPAWN_WEAPON_LEVEL_1[2][2]` | `src/include/tables_LEVELS.c` | — |
| Jump Tables | `TABLE_JUMP_V[27]`, `TABLE_JUMP_H[31]` | `src/include/tables_LEVELS.c` | — |

---

## 5. NEXZR MD (Shmup / Shoot-em-up)

### Mapa de Telas

```
 ╔═══════════════════════════════════════════════════════════════════════════╗
 ║  NEXZR MD — Fluxo de Estados (levels enum)                              ║
 ╚═══════════════════════════════════════════════════════════════════════════╝

  [Naxat Logo] ──> [Intro Screen] ──> [MAIN MENU]
   Intro_init()     1s fade each       Menu_init()
        │                                   │
        │                          ┌────────┴─────────┐
        │                          │  MAIN MENU       │
        │                          │  GAME_START ◄──┐ │
        │                          │  CARNIVAL_MODE │ │
        │                          │  OPTIONS ──────┘ │
        │                          │                  │
        │                          │  OPTIONS:        │
        │                          │  LANGUAGE (EN/PT/ES)
        │                          │  MD_MODE (on/off)│
        │                          │  DIFFICULTY      │
        │                          │  CREDITS         │
        │                          │  BACK            │
        │                          └────────┬─────────┘
        │                                   │ GAME_START
        v                                   v
                              ┌─────────────────────────────────┐
                              │  LEVEL_1 (currentLevel = 1)     │
                              │  Level1_init()                  │
                              │                                 │
                              │  Background: warp star effect   │
                              │   (20 stars, parallax depth)    │
                              │  Player: "slasher" sprite       │
                              │  HUD: lives, score              │
                              │                                 │
                              │  ** Enemies/Bosses: NOT IMPL ** │
                              │  ** Bullets: NOT IMPL **        │
                              │  ** Score: NOT IMPL **          │
                              │                                 │
                              │  START -> Game_pause() toggle   │
                              │  Lives: max 9                   │
                              └─────────────────────────────────┘

  NOTA: Apenas MENU e LEVEL_1 existem. Enemies, bosses, scoring,
  e niveis adicionais estao marcados como TODO no codigo.
```

---

## 6. TOWN QUEST (RPG Acao Simples)

### Mapa de Stages

```
 ╔═══════════════════════════════════════════════════════════════════════════╗
 ║  TOWN QUEST — Progressao Linear de Stages                               ║
 ╚═══════════════════════════════════════════════════════════════════════════╝

  [Stage 0: Splash] ──(400 frames)──> [Stage 1: Loading] ──(600 frames)──>
   titulo image           vara image

  [Stage 2: JOGO] ──> [Stage 3] ──> ... ──> [Stage 9]
   stage1 bg               stage2 bg
   10 enemies (gente)       handlestate() avanca
   10 NPCs (person)         se victory == TRUE
   tiovara (player)
   Life: 3 (INITIAL_LIFES)

   Victory: todos 10 enemies.enabled == 0
   Game Over: player lifes <= 0

  [Stage 10: GAME OVER]
   game_over image (estado final)
```

---

## 7. STATE MACHINE RPG (Top-Down RPG Prototype)

### Mapa de Dungeon (Array 60x56)

```
 ╔═══════════════════════════════════════════════════════════════════════════╗
 ║  STATE MACHINE RPG — Mapa Unico (level[3360] = 60 cols x 56 rows)      ║
 ╚═══════════════════════════════════════════════════════════════════════════╝

  Mapa em array 1D: level[j*60 + i]
  6959 = parede solida    0 = area livre

  ┌────────────────────────────────────────────────────────────┐
  │████████████████████████████████████████░░░░░░░░░░░░░░█████│
  │████████████████████████████████████████░░░░░░░░░░░░░░█████│
  │████████████████████████████████████████░░░░░██░░░░░░░█████│
  │██████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░█████│
  │████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█████│
  │████████████████░░░░(SPAWN)░░░░░░░░░░░░░░░░░░░░░░░██░█████│
  │████████████████░░░░░Player░░░░░░░░░░░░░░░░░░░░░░░██░░████│
  │                    (160,112)                              │
  │  Limites: 480x448 pixels (60*8 x 56*8)                   │
  │  Camera: clamp(0..160, 0..224)                            │
  │  Velocidade: 2 px/frame                                   │
  │  Ataque: SPR_setAnim(4-7) por direcao                    │
  └────────────────────────────────────────────────────────────┘

  Sem transicoes de tela. Mapa unico com scroll de camera.
```

---

## LEGENDA GLOBAL

```
  [NOME]     = Sala / Tela / Area jogavel
  ──>        = Transicao automatica (timer/frame)
  ──(cond)─> = Transicao condicional (input/flag)
  (P)        = Player Spawn
  ████       = Paredes / Solido
  ░░░░       = Area livre / walkable
  ** **      = Funcionalidade nao implementada
  BGM:       = Musica de fundo (XGM/XGM2)
  SFX:       = Efeito sonoro (PCM)
```
