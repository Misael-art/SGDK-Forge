# Level Topology Map - PlatformerEngine [VER.1.0] [SGDK 211] [GEN] [ENGINE] [PLATAFORMA]

**Tipo**: Spatial / Castlevania-Style Topology Map
**Fonte**: `PlatformerEngine Toolkit/.../upstream/PlatformerEngine/src/map.c`
**Grid**: 48x48 tiles (16x16px cada) = 768x768px total
**Tile Types**: 0=Air, 1=Ground(GROUND_TILE), 2=Ladder(LADDER_TILE), 4=One-Way Platform(ONE_WAY_PLATFORM_TILE)

---

## 1. Mapa Topologico Espacial Completo (48x48 Collision Grid)

Legenda:
```
  . = Air (0)         # = Ground (1)       = = One-Way Platform (4)       H = Ladder (2)
  S = Spawn Point (74, 665 px → tile ~4, ~41)
  X = Death Pit (y >= 768 → falling == TRUE)
```

```
     0         1         2         3         4
     0123456789012345678901234567890123456789012345678

 0:  ................................................
 1:  ................................................
 2:  ................................................
 3:  ................................................
 4:  ..........................===.....................
 5:  .........................=====....................
 6:  ................................................
 7:  ......................=======.....................
 8:  ................................................
 9:  ................................................
10:  ........................=========.................
11:  ................................................
12:  ................................................
13:  .....................=========....................
14:  ................................................
15:  ................................................
16:  ................................................
17:  ................................................
18:  ................................................
19:  ................................................
20:  ....................#=====================#.......
21:  ........============....................##.......
22:  .......................................###......
23:  .......===..............................====.====
24:  ................................................
25:  ................................................
26:  .....============...................====.====.H=.
27:  ............................===..............H...
28:  ..=========..........===....................H...
29:  ............................===......===.....H...
30:  ................................................
31:  ##############.##.........................====H===
32:  ##############.##.........................===.H...
33:  ###########.................................H...
34:  #######...............===..........====.....H...
35:  ######............=..===...................H...
36:  ######...........===......................H...
37:  ######.....................................====H=
38:  ####..........................==..............H...
39:  ####...............====..........................
40:  #...............=====....=======..........=====H==
41:  #S......===.=====...=====........=========.......
42:  #...====.===..................................
43:  #......=====..............======..............
44:  #..........########.............===..........
45:  ##########..##############..###..========...=====.
46:  ##########..##..............###.................
47:  ##########..##..........##...........########
48:  ##########..############################........

     ^^^^^^^^^^^  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^  ^^^^^^^^
     LEFT CLIFF  CENTRAL CAVERN (open rooms)   RIGHT TOWER
     Rows 37-47  Rows 37-47, Cols 14-39         Cols 40-47
```

### Vista Macro: Zonas de Navegacao

```
     ┌─────────────────────────────── 768px ─────────────────────────────────┐
     │                                                                       │
     │           ┌──────── UPPER SKY ZONE ────────┐                          │
     │           │  Floating One-Way Platforms     │                          │
     │           │  Rows 4-17 (px 64-287)          │                          │
     │           │  Cols 20-33                      │                          │
     │           │  Stepped descent pattern:        │                          │
     │           │   Row  4: [26-28]                │                          │
     │           │   Row  5: [25-29]                │                          │
     │           │   Row  7: [22-28]                │                          │
     │           │   Row 10: [24-32]                │                          │
     │           │   Row 13: [21-29]                │                          │
     │           └──────────────────────────────────┘                          │
     │                                                                       │
     │  ┌──────────── MIDDLE BRIDGE ZONE ──────────────┐                      │
     │  │  Row 20: Ground walls at [20] and [41]        │                      │
     │  │  Row 20: Long one-way bridge [21-40]          │   ┌── RIGHT WALL ──┐│
     │  │  Row 21: Left extension [8-19]                │   │  Rows 20-28    ││
     │  │  Rows 22-29: Scattered platforms              │   │  Cols 41-47    ││
     │  │  connecting left to right                      │   │  ##/==/ladder  ││
     │  └──────────────────────────────────────────────┘   └────────────────┘│
     │                                                                       │
     │  ┌── LEFT CLIFF ──┐  ┌── CENTRAL CAVERN ──┐  ┌── LADDER TOWER ──┐    │
     │  │  Rows 37-48     │  │  Rows 43-48         │  │  Col 44/46       │    │
     │  │  Cols 0-10      │  │  Cols 14-27         │  │  Rows 26-42      │    │
     │  │  Solid ground   │  │  Mixed ground +     │  │  Continuous H    │    │
     │  │  Stepped left   │  │  open corridors     │  │  climb route     │    │
     │  │  wall descends  │  │  Bottom: row 48     │  │  16 tiles tall   │    │
     │  │                 │  │  solid floor         │  │                  │    │
     │  │  S ← SPAWN      │  │                      │  │                  │    │
     │  │  (74,665)px     │  │                      │  │                  │    │
     │  │  ~tile(4,41)    │  │                      │  │                  │    │
     │  └─────────────────┘  └──────────────────────┘  └──────────────────┘    │
     │                                                                       │
     │  ─ ─ ─ ─ ─ ─ ─ ─ ─ y=768 ─ ─ ─ ─ ─ DEATH PIT ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │
     └───────────────────────────────────────────────────────────────────────┘
```

### Rota Critica do Jogador

```
     [SPAWN: tile(4,41)]
            │
            ▼
     LEFT CLIFF (solid ground, rows 37-48, cols 0-10)
            │  walk right ──►
            ▼
     STEP PLATFORMS (rows 39-41, cols 7-17)
     ═══ One-way chains descending left to right
            │
            ▼
     CENTRAL FLOOR (row 43-48, cols 14-27)
     ######  Solid ground section
            │
       ┌────┴────┐
       │         │
       ▼         ▼
    [ROUTE A]  [ROUTE B]
     Jump up    Climb RIGHT LADDER
     via ===    (col 44/46, rows 26-42)
     platforms       │
     to UPPER        ▼
     SKY ZONE   RIGHT TOWER ZONE
       │        (cols 40-47, rows 20-32)
       │        ═══ + ### platforms
       ▼             │
     MIDDLE          ▼
     BRIDGE      ┌───────────┐
     (row 20)    │ TOP RIGHT │
     ═══════     │ Platform  │
       │         │ row 29    │
       ▼         │ cols 39-47│
     Can reach   └───────────┘
     RIGHT WALL
     (cols 41-43, rows 20-22)
```

---

## 2. Tabela de Traducao Tecnica

| Elemento Visual | Var/Funcao no Codigo | Arquivo | Valor |
|---|---|---|---|
| **Collision Grid** | `collisionMap[48][48]` | `src/map.c:6` | `const u8`, copiada para RAM |
| **Dynamic 2D Map** | `currentMap` (u8**) | `src/levelgenerator.c:9` | `MEM_alloc` → copia de ROM |
| **Room Size** | `roomSize` | `src/levelgenerator.c:23` | `AABB(0, 768, 0, 768)` |
| **Tile Size** | Implicit (bitshift) | `src/physics.c:5-27` | 16x16px (`<<4` / `>>4`) |
| **Room Tile Size** | `roomTileSize` | `src/levelgenerator.c:26` | `768>>4 = 48` tiles |
| **Spawn Point** | `levelStartPos` | `src/map.c:3` | `{74, 665}` px → tile ~(4,41) |
| **Ground Tile** | `GROUND_TILE` | `inc/global.h:12` | `1` |
| **Ladder Tile** | `LADDER_TILE` | `inc/global.h:13` | `2` |
| **One-Way Platform** | `ONE_WAY_PLATFORM_TILE` | `inc/global.h:14` | `4` |
| **Death Trigger** | `levelLimits.max.y == 768` | `src/player.c:402` | `playerBody.falling = TRUE` |
| **Death Reset** | `SYS_hardReset()` | `src/player.c:201` | After `dieDelay=10` frames |
| **Tile Value Query** | `getTileValue(x, y)` | `src/levelgenerator.c:36` | `currentMap[y][x]` |
| **Tile→Pixel** | `getTileLeftEdge(x)` | `src/physics.c:4-6` | `x << 4` |
| **Pixel→Tile** | `posToTile(position)` | `src/physics.c:25-27` | `x >> 4, y >> 4` |
| **Tile Bounds** | `getTileBounds(x, y)` | `src/physics.c:20-22` | `AABB(x<<4, x<<4+16, y<<4, y<<4+16)` |
| **Generate Map** | `generateCollisionMap()` | `src/levelgenerator.c:22` | Copies ROM→RAM via `MEM_alloc` |
| **Free Map** | `freeCollisionMap()` | `src/levelgenerator.c:14` | Loop `MEM_free` rows + base |
| **Level Tileset** | `level_tileset` | `res/resources.res:4` | `"images/level.png" FAST ALL` |
| **Level Map** | `level_map` | `res/resources.res:5` | MAP referencing `level_tileset` |
| **Level Palette** | `level_palette` | `res/resources.res:6` | PAL0 (`LEVEL_PALETTE`) |
| **BGM** | `song` | `res/resources.res:8` | `sonic2Emerald.vgm` XGM format |
| **BGA Plane** | `bga` (Map*) | `src/global.c:10` | `TILEMAP_PLANE = BG_A` |
| **VDP Fill Index** | `VDPTilesFilled` | `src/global.c:18` | `TILE_USER_INDEX`, incremented |

---

## 3. Mapeamento de Tiles Notaveis por Zona

### LEFT CLIFF (Solid Ground Zone)
```
Rows 37-48, Cols 0-17 (com gaps)
Row 37: ################## (cols 0-17, solid)
Row 38: ################## (cols 0-17, solid)
Row 39: ###########        (cols 0-10)
Row 40: #######            (cols 0-6)
Row 41: ######             (cols 0-5) ← SPAWN at col 4
Row 42: ######             (cols 0-5)
Row 43: ######             (cols 0-5)
Row 44: ####               (cols 0-3)
Row 45: ####               (cols 0-3)
Row 46: #                  (col 0)
Row 47: #                  (col 0)
→ Terrain descends like a staircase from right to left
→ Player spawns on the top step (row 41)
```

### LADDER TOWER (Vertical Climb Route)
```
Col 46 (rows 26-42): Continuous LADDER_TILE (value=2)
Entry: From right side platforms (row 37 or row 43)
Exit:  Connects to upper right platform (row 26)
Height: 17 tiles = 272px of vertical climbing
Adjacent one-way platforms at rows 26, 32, 37, 40, 43
```

### UPPER SKY PLATFORMS (Floating One-Way Zone)
```
Rows 4-13, Cols 20-33
Stepped descending pattern (no ground, pure air below):
  Row  4: ===       (cols 26-28)
  Row  5: =====     (cols 25-29)
  Row  7: =======   (cols 22-28)
  Row 10: =========  (cols 24-32)
  Row 13: =========  (cols 21-29)
→ Reachable only by chaining jumps from Middle Bridge Zone upward
→ One-way pass-through from below, solid from above
```

---

## 4. Diagrama de Conexao entre Zonas

```
                    ┌──────────────────────┐
                    │   UPPER SKY ZONE     │
                    │   Rows 4-13          │
                    │   Floating ===       │
                    └──────────┬───────────┘
                               │ fall down
                               ▼
      ┌────────────────────────────────────────────┐
      │          MIDDLE BRIDGE ZONE                 │
      │  Row 20-21: Long bridge ═══ + walls #       │
      │  Row 22-29: Scattered step platforms        │
      └──┬─────────────────────────────────────┬───┘
         │ fall left                   climb ▲ │
         ▼                                   │ │
   ┌──────────────┐                    ┌─────┴─┴────┐
   │  LEFT CLIFF  │                    │ RIGHT TOWER │
   │  Rows 37-48  │                    │ Cols 40-47  │
   │  Solid ###   │                    │ ### + ===   │
   │  SPAWN (S)   │                    │ LADDER (H)  │
   └──────┬───────┘                    │ col 44/46   │
          │ walk right                 └──────┬──────┘
          ▼                                   │
   ┌──────────────────────────────────────────┴────┐
   │            CENTRAL CAVERN / FLOOR              │
   │  Rows 43-48, Cols 14-39                        │
   │  Ground ### + corridors + gaps                  │
   │  Row 48: ########################## (floor)     │
   └───────────────────────────────────────────────┘
          │ fall past y=768
          ▼
   ╔═══════════════════════════════════╗
   ║         DEATH PIT (void)          ║
   ║  playerBody.falling = TRUE        ║
   ║  → SYS_hardReset() after 10f      ║
   ╚═══════════════════════════════════╝
```
