# Appendix — Additional Lessons from SGDK_Engines Scan (Pass 2)

Status: `appendix / raw extraction log`

> Este arquivo preserva a pesquisa validada e os idioms observados nos engines.
> Ele NAO e o front door canonico do tema e NAO promove padroes a canon por si so.
> Use junto com o registry e o front door em `doc/05_technical`.

> **Scope.** This appendix extends the first-pass research on SGDK_Engines. It documents
> patterns extracted from engine folders not covered in the first pass, together with
> precise file references and the canonical idioms observed. Everything here is meant
> to be assimilated by the AAA curation agent and skills; nothing is to be treated as
> canon until promoted through the canonization gate (Sprint 1..N approval).
>
> **Tone.** Engineering reference, not tutorial. Each section names the file, names
> the pattern, and shows the minimal snippet you need to reproduce it. When the
> pattern exceeds the agent's working memory, follow the file reference.
>
> **Pairing.** Read together with `doc/05_technical/80_fx_combination_matrix.md`,
> `91_multi_plane_composition.md` and the Sprint 1 drafts in `doc/03_art/`.

---

## 1. LIZARDRIVE FX — Canonical H-Int / Per-line Scroll References

SGDK_LIZARDRIVE is the primary reference SDK sample collection. Its `sample/fx/*`
folder is the canonical source for horizontal interrupt and line scroll idioms.

### 1.1 H-Int Wobble (`sample/fx/h-int/wobble/src/main.c`)

Per-line vertical scroll driven by a fix16 buffer, menu-driven to swap between
wave presets (linear, wobble, zoom). This is the "template" for any visual
distortion that uses `SYS_setHIntCallback`.

```c
fix16 lineBuffer[224];      // one per scanline, typically a delta
vu16 lineDisplay = 0;       // current scanline index
vs16 lineGraphics = 0;      // running Y offset written to VDP

HINTERRUPT_CALLBACK HIntHandler() {
    VDP_setVerticalScroll(BG_B, fix16ToInt(lineGraphics) - lineDisplay);
    lineGraphics += lineBuffer[lineDisplay++];
}

void VBlankHandler() {
    lineDisplay = 0;
    lineGraphics = 0;
    VDP_setVerticalScroll(BG_B, 0);
}

// Setup:
SYS_setVBlankCallback(VBlankHandler);
SYS_setHIntCallback(HIntHandler);
VDP_setHIntCounter(0);     // fire every scanline
VDP_setHInterrupt(1);
```

**Discipline.** Both the VBlank and HInt callbacks must be symmetric — VBlank
resets state to line 0, HInt advances by exactly 1 per call. Any drift here
produces "rolling" glitches. `lineBuffer` is always exactly 224 entries for
PAL/NTSC 224-line mode.

### 1.2 H-Int Scaling (`sample/fx/h-int/scaling/src/main.c`)

Same framework, but the per-line delta decreases geometrically — producing a
bitmap-style "shrink toward horizon" effect.

```c
scale -= max(scale >> 6, FIX16(0.02));  // monotonic decrease per line
lineBuffer[i] = scale;
```

Canonical use: planet surface curvature, zoom-out transitions, tunnel effect
tops.

### 1.3 Spotlight Hilight-Shadow (`sample/fx/hilight-shadow/src/main.c`)

Combines `VDP_setHilightShadow(1)` with per-line HScroll to move a shadow/light
band. The trick: `HSCROLL_LINE` mode is enabled and `line_scroll_data[NUM_LINES]`
plus `line_speed_data[NUM_LINES]` bounce the scroll value off the screen edges.

```c
VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_PLANE);
VDP_setHilightShadow(1);   // enable Shadow/Highlight mode (32+32+1 colors)
// Per frame: update aux[] from line_scroll_data[] with rebound logic
VDP_setHorizontalScrollLine(BG_A, 0, aux, NUM_LINES, 1);
```

**Use case.** Classic "torch in a dark corridor", enemy spotlight pass, Streets
of Rage arcade intro spotlights.

### 1.4 Linear Linescroll (`sample/fx/scroll/linescroll/src/main.c`)

Three-zone speed gradient (base / offset / end) with wrap logic. This is the
canonical "parallax-per-line" effect used in every racing game and shmup
scanline star field.

```c
fix16 scrollSpeed[224];
fix16 scroll[224];
fix16 scrollLoop[224];

// initScrollTables(): set base speed, offset speed, end speed; interpolate.
// each frame:
for (u16 i = 0; i < 224; i++) {
    scroll[i] = fix16Add(scroll[i], scrollSpeed[i]);
    if (scroll[i] >= scrollLoop[i]) scroll[i] -= scrollLoop[i];
}
VDP_setHorizontalScrollLine(BG_A, 0, (s16*)scroll_int, 224, DMA_QUEUE);
```

**Canonization note.** Always commit to `DMA_QUEUE` — direct DMA starves the
rest of the frame. If you need line scroll + tile update + sprite DMA in the
same frame, the queue is how you avoid blowing the budget.

---

## 2. LIZARDRIVE Sonic Sample — Streaming Maps & HUD

`sample/sonic/src/*` is the canonical platformer streaming reference.

### 2.1 Camera (`sonic/src/camera.c`)

Dual-axis deadzone with clamping and parallax, with a parallax divisor on BGB.

```c
// Deadzone in screen-space, then project to world
if (px_scr > 240)      npx_cam = px - 240;
else if (px_scr < 40)  npx_cam = px - 40;
else                   npx_cam = camPosX;

// World clamp
if (npx_cam < 0)                       npx_cam = 0;
else if (npx_cam > (MAP_WIDTH - 320))  npx_cam = (MAP_WIDTH - 320);

MAP_scrollTo(bga, x, y);
MAP_scrollTo(bgb, x >> 3, y >> 5);    // BGB parallax: horizontally 1/8, vertically 1/32
```

**Lesson.** Parallax is achieved by bit-shift divisor on the target map pointer
— no extra math table needed. Different shifts per axis let sky scroll much
slower than foreground mountains.

### 2.2 Manual Map Streaming (`sonic/src/level.c`)

When the map is too big for `MAP_scrollTo` to handle smoothly (or when you want
per-row/per-column effects interleaved), streaming is manual.

```c
// 42x32 tile buffer, 21 metatiles wide
MAP_getTilemapRect(level_map, ...);
VDP_setTileMapDataColumnFast(BG_A, buf, x, y_start, height, DMA_QUEUE);
VDP_setTileMapDataRow(BG_A, buf, y, x_start, width, DMA_QUEUE);
```

Compare the two approaches:

| Method          | Ease        | Control    | Best For                              |
|-----------------|-------------|------------|---------------------------------------|
| `MAP_scrollTo`  | 1 call      | Low        | Normal platformer, racing, RPG exploration |
| Manual column/row | ~20 lines | Full       | Per-column palette swap, per-row FX, tile-cache eviction |

### 2.3 Sprite-Based HUD (`sonic/src/hud.c`)

Bars as sprites with 17 frames (0..16). No text, no tile math — just
`SPR_setFrame()`.

```c
SPR_setFrame(bar_sprite, health_level);   // health_level in [0..16]
```

**Canonical for.** Health bars, power bars, speed gauges, ammo bars. Also used
in `Lifebar` engine (see §10) but with window-plane tiles instead of sprites.

### 2.4 Multi-rate Deceleration (`sonic/src/player.c`)

Sonic-style friction ramp: 4 decel rates depending on current speed. This is
why Sonic/Sega platformers feel different from Mario-style linear friction.

```c
if (xOrder == 0) {
    if ((movX < FIX32(0.1)) && (movX > FIX32(-0.1)))       movX = 0;
    else if ((movX < FIX32(0.3)) && (movX > FIX32(-0.3)))  movX -= movX >> 2;
    else if ((movX < FIX32(1))   && (movX > FIX32(-1)))    movX -= movX >> 3;
    else                                                    movX -= movX >> 4;
}

// Brake animation on direction reversal
if (((movX >= BRAKE_SPEED) && (xOrder < 0)) ||
    ((movX <= -BRAKE_SPEED) && (xOrder > 0))) {
    XGM_startPlayPCM(SFX_STOP, 1, SOUND_PCM_CH2);
    SPR_setAnim(player, ANIM_BRAKE);
}
```

**Rationale.** Fast speeds bleed off slowly (the `>> 4` case) — feels
momentum-heavy. Slow speeds decay quickly (the `>> 2` case) — feels crisp. The
combined effect: dashing feels "fast" but you don't overshoot pickups.

---

## 3. LIZARDRIVE Platformer Sample — Modern Platformer Feel

`sample/platformer/src/*` — the reference implementation of modern
platformer game feel on SGDK. All constants below are the canonical defaults.

### 3.1 Coyote Time + Jump Buffer + Half-Jump Cancel

```c
const s16 coyoteTime = 10;                      // frames you can still jump after leaving ledge
const s16 jumpBufferTime = 10;                  // frames early jump press is remembered
const u16 oneWayPlatformErrorCorrection = 5;    // pixels of tolerance

// half-jump: release during upward arc cuts velocity
if (buttonReleased && isJumping && velocity.fixY < 0) {
    velocity.fixY = fix16Mul(velocity.fixY, FIX16(0.5));
}

// jump triggers on coyote AND buffer — feels "forgiving"
if (currentCoyoteTime > 0 && currentJumpBufferTime > 0) {
    doJump();
}
```

**Why 10 frames?** At 60fps this is ~166ms — slightly above the 150ms
perceptual threshold where players still feel "I jumped exactly when I pressed
the button". Any higher and jumps feel sloppy; any lower and the input buffer
doesn't help.

### 3.2 Deadzone Camera (`platformer/src/camera.c`)

Contrast with Sonic's camera: this one uses an explicit AABB deadzone struct,
which is easier to reason about and debug.

```c
cameraDeadzone.min.x = deadZoneCenter.x - (deadZoneWidth >> 1);
cameraDeadzone.max.x = deadZoneCenter.x + (deadZoneWidth >> 1);
// ...if player crosses deadzone edge, shift cameraPosition
cameraPosition.x = clamp(cameraPosition.x, 0, 448);  // level_w - screen_w
MAP_scrollTo(bga, cameraPosition.x, cameraPosition.y);

// On scene change / warp, force full refresh:
// MAP_scrollToEx(bga, x, y, TRUE);
```

### 3.3 Tile Helpers (`platformer/src/physics.c`)

The canonical 1-liner macros for 16-px tile math:

```c
#define getTileLeftEdge(x)   ((x) << 4)    // tile_x -> pixel_x
#define getTileRightEdge(x)  (((x) << 4) + 15)
#define posToTile(pos)       ((pos) >> 4)  // pixel_x -> tile_x
```

**Rule.** Never divide/multiply by 16 in hot code. Always shift. SGDK tile math
is carefully tuned to always be shiftable.

---

## 4. LIZARDRIVE Multitasking Sample — Official TSK_ API

`sample/multitasking/src/main.c` — the only canonical reference for SGDK's
built-in two-task cooperative scheduler.

```c
static vu32 count;

static void bg_tsk(void) {
    while (TRUE) {
        count++;
        if (count >= 0x100000)
            TSK_superPost(FALSE);   // yield to foreground
    }
}

static void fg_tsk(void) {
    while (TRUE) {
        draw_hex(count, 1, 2);
        SYS_doVBlankProcess();      // wait VSYNC in foreground
    }
}

int main() {
    SYS_setVIntCallback(vint_cb);
    TSK_userSet(bg_tsk);            // install user-level background task
    fg_tsk();                        // never returns
    return 0;
}

// Optional sleeps:
// TSK_superPend(180);                // sleep 180 frames
// TSK_superPend(TSK_PEND_FOREVER);   // block until TSK_superPost(TRUE)
```

**When to use.** Map decompression, audio streaming, AI pathfinding,
procedural generation — any work that can yield. Do **not** use it for
sub-frame effects; those need HInt callbacks.

---

## 5. LIZARDRIVE Bench Sample — Framework Shape

`sample/bench/src/main.c` — 9-test benchmark framework, useful as the
reference shape for our own `BENCHMARK_VISUAL_LAB` scene scoring.

```c
// Memory diagnostics shown per test:
u16 mem_free   = MEM_getFree();
u16 dma_buf    = DMA_getBufferSize();
u16 dma_queue  = DMA_getMaxQueueSize() * sizeof(DMAOpInfo);
u16 vram_free  = TILE_USER_MAX_INDEX;    // see vdp_tile.h
```

**Takeaway for our lab.** Every benchmark frame should include a
diagnostic strip: CPU% (`VDP_showCPULoad`), FPS (`VDP_showFPS`), free heap,
DMA queue size, VRAM cursor. Our FASE 2 POC ROM already does the first two;
add the other three for FASE 3.

---

## 6. Mega Metroid — Slope Collision With Gradient

`Mega Metroid [VER.001]…/src/main.c` — slope tiles contribute a per-column
Y offset.

```c
else if (map_collision[y][rx] == SLOPE_RIGHT_TILE) {
    AABB tileBounds = getTileBounds(rx, y);
    s16 x_dif = (player.collision_position.max.x - tileBounds.min.x) << 1;
    if (x_dif > 8) x_dif = 8;

    levelLimits.max.y = tileBounds.max.y - x_dif;
    if (player.collision_position.max.y >= tileBounds.max.y - x_dif - 2)
        player.is_on_floor = TRUE;
}
```

**Notes.**
- `<< 1` gives a 2:1 slope. For 1:1 use plain `x_dif`.
- Clamp at 8 so one tile never produces more than 8px rise.
- The `-2` gives sub-pixel attachment tolerance — stops the "floating above
  slope" bug.

Plus two global tunings worth copying:

```c
DMA_setBufferSize(10000);       // temporarily during heavy init
DMA_setMaxTransferSize(10000);
// ... heavy map/tile uploads ...
// restore defaults after init

// Input model: use JOY event handler + control.d_pad.x/y as signed {-1,0,1}
```

---

## 7. NEXZR MD — Entity Manager, Star Warp, Custom Font

### 7.1 Minimal Entity Manager (`NEXZR/src/entitymanager.c`)

The simplest working entity manager: function pointer + context pointer +
active flag. ~65 lines, no OOP, no vtables.

```c
typedef void (*Func)(void*);

typedef struct {
    void*  context;
    Func   func;
    bool   active;
} Entity;

Entity entities[MAX_ENTITIES];
u16    entityCount;

Entity* Entity_add(void* ctx, Func func) {
    if (entityCount >= MAX_ENTITIES) return NULL;
    entities[entityCount] = (Entity){ctx, func, TRUE};
    return &entities[entityCount++];
}

void Entity_executeAll(void) {
    for (u16 i = 0; i < entityCount; i++)
        if (entities[i].func && entities[i].active)
            entities[i].func(entities[i].context);
}
```

**Why this beats a switch/case monster.** Zero branch mispredicts on the 68k
(function pointer is a single `jsr`). Adding a new entity type means writing
one update function — no enum, no central dispatcher.

### 7.2 Star Warp (`NEXZR/src/background.c`)

20 stars, 5 size variants, deceleration phase. Uses `SPR_setZ(spr,
SPR_MAX_DEPTH)` to keep stars behind the player ship. Blink via
`SPR_setVisibility(HIDDEN)` driven by a random timer. Larger stars use **sprite
chains** (multiple sprites stacked vertically) to exceed 32-px height.

### 7.3 Custom Font by Tile Index Math (`NEXZR/src/characters.c`)

```c
if (c >= 'A' && c <= 'Z')      tileIndex = (c - 'A');
else if (c >= '0' && c <= '9') tileIndex = 28 + (c - '0');
if (state == FONT_INACTIVE)    tileIndex += CHARS_ACTIVE_OFFSET;

VDP_setTileMapXY(BG_B,
    TILE_ATTR_FULL(PAL, TRUE /*prio*/, 0, 0, TILE_FONT_INDEX + tileIndex),
    x + i, y);
```

**Takeaway.** If your font is fixed-width 8x8 and your character set is
contiguous, don't bother with `VDP_drawText` — go straight to
`VDP_setTileMapXY`. You get priority bit, flip, and palette control per char.

---

## 8. MegaDriving — Pseudo-3D Racing Stack (Lou's Method)

`MegaDriving/upstream/lou/*` is a progressive tutorial from flat road to
full-featured racing engine. The 4 stages worth studying in order:

### 8.1 `01_basic_road` — ZMAP + Horizontal Per-line Scroll

```c
// Z-map init: perspective projection Z = Yworld / (Yscreen - (H/2))
for (u16 i = 0; i < ZMAP_LENGTH; ++i)
    zmap[i] = F16_div(FIX16(-75), FIX16(i) - FIX16(112));

// Per frame, draw road curves:
for (u16 y = 0; y < ZMAP_LENGTH; ++y) {
    fix16 z = zmap[y];
    if (z < segment_position) dx = segments[bottom_segments_index].dx;
    else                      dx = segments[segments_index].dx;

    ddx += dx;
    current_x += ddx;
    HscrollA[223 - y] = SCROLL_CENTER + F16_toInt(current_x);
}
VDP_setHorizontalScrollLine(BG_A, 0, HscrollA, 224, DMA_QUEUE);
VDP_setHorizontalScrollLine(BG_B, 0, HscrollB, 120, DMA_QUEUE);
```

Two important things:
- `-75 / (i - 112)` is the tuned perspective focal distance for 224-line
  output with the camera "eye" at y=112.
- Background (`BG_B`) only updates 120 lines — the sky doesn't need per-line
  scroll because it's a far-distance parallax layer.

### 8.2 `02_hills` — Vertical Scroll Line Variant

Hills are done by **vertical** per-line scroll, not horizontal. The key insight:
you iterate from the bottom of the screen toward the horizon, and for each row
you compute a `bgY - cdp` vertical offset that "stretches" image rows.

```c
fix32 current_drawing_pos = FIX32(223);
fix32 dy = dy1, ddy = FIX32(0);
s16 horizon_line = 223;

for (u16 bgY = 223; bgY > 115; bgY--) {
    s16 cdp = F32_toInt(current_drawing_pos);
    if (bgY == segmentLine) dy = dy2;  // transition to segment 2

    if (cdp <= horizon_line) {
        VscrollA[cdp] = bgY - cdp;
        horizon_line = cdp;
    }

    ddy = dy + ddy;
    current_drawing_pos -= (FIX32(1) + ddy);
}

// hide everything above horizon (push off-screen)
for (s16 h = horizon_line - 1; h >= 16; --h)
    VscrollA[h] = -h;
```

Button A/B/C/X toggle between preset slopes — useful pattern for our
BENCHMARK_VISUAL_LAB style "swap preset, observe effect" scenes.

### 8.3 `04_colors` — Combined Curves + Hills + Color Banding

Merges both techniques (HScroll for curves, VScroll for hills) plus a color
banding array driven by `zmapval & 1`:

```c
u8 zmapval = (u8)F16_toInt(segment_position - z);
colors[cdp] = zmapval & 1;   // alternating road stripe
```

The commented-out HInt block shows (disabled, broken) how to swap palette
entry 1/2/3 mid-scanline via raw 68k VDP register writes — leave this disabled
until we have the scanline budget to check properly.

**Lesson for our Racing skill.** Curves = HScroll, Hills = VScroll, Stripes =
palette-swap per scanline or color-bit on tile. Never try to combine all three
on the same H-Int callback; split into two or use `HSCROLL_LINE` + `VSCROLL_PLANE`
with pre-computed tables.

---

## 9. Shadow Dancer — Tile Refcount Cache For Huge Maps

`Shadow Dancer Revisitado/src/mapHandler.c` — solves the "map bigger than
VRAM" problem with a refcounted tile cache wired into SGDK's `MAP_` callback.

```c
typedef struct {
    u16 mapTile;    // index in source tilemap
    u16 planeTile;  // index in plane
    u16 count;      // refcount
} TileMatch_t;

TileMatch_t* tileCache;                         // ACTIVE_TILES entries
u16          planeCache[42][32];                // plane_x,y -> planeTile
u16*         mapTileToPlaneTile;                // inverse lookup
u16          bump, lowestFree, highestFree;     // allocator cursors

u16 tileCache_fetchTile(u16 mapTile) {
    u16 planeTile = mapTileToPlaneTile[mapTile];
    if (planeTile != 0xFFFF) { tileCache[planeTile].count++; return planeTile; }

    // bump allocate or scan for refcount==0 slot
    if (bump < ACTIVE_TILES) planeTile = bump++;
    else { /* scan from lowestFree */ }

    mapTileToPlaneTile[mapTile]          = planeTile;
    tileCache[planeTile] = (TileMatch_t){mapTile, planeTile, 1};

    DMA_transfer(DMA, DMA_VRAM, &tileSet->tiles[mapTile * 8],
                 (tileVram + planeTile) * 32, 16, 2);
    return planeTile;
}

void tileCache_releaseTile(u16 planeTile) {
    if (--tileCache[planeTile].count == 0) {
        mapTileToPlaneTile[tileCache[planeTile].mapTile] = 0xFFFF;
        /* update lowestFree / highestFree / bump */
    }
}

// Wire into MAP_ engine:
void tileCache_callback(Map* map, u16* buf, u16 x, u16 y,
                        MapUpdateType updateType, u16 size) {
    while (size--) {
        u16 tileData  = *buf;
        u16 tileIndex = tileData & TILE_INDEX_MASK;
        u16 oldTile   = planeCache[xt][yt];
        if (oldTile != 0xFFFF) tileCache_releaseTile(oldTile);
        tileIndex = tileCache_fetchTile(tileIndex);
        planeCache[xt][yt] = tileIndex;
        *buf++ = (tileData & ~TILE_INDEX_MASK) | (tileVram + tileIndex);
        /* advance xt/yt depending on ROW_UPDATE vs COL_UPDATE */
    }
}
```

**This is the workaround for huge levels.** Without it you cap at ~1500
unique tiles in VRAM. With it, as long as any *visible window* has ≤ N unique
tiles (N = `ACTIVE_TILES`), the map can be arbitrarily large.

**Caveat.** The tileCache callback is called on every scroll row/column — it
*must* be fast. The `DMA_transfer` per new tile is 16 bytes and is the
expensive part; batch them through `DMA_QUEUE` if you see frame drops.

---

## 10. Lifebar — Window-Plane HUD with Graded Tiles

`Lifebar/src/main.c` + `lifebar.h` — HUD rendered on the Window plane, with
intermediate (25%/50%/75%) tiles for partial fill.

```c
VDP_setWindowFullScreen();
loadLifeBarTiles();

// Percentage-based fill with remainder:
u16 percent   = (currentLife * 100) / maxLife;
u8  filled    = (percent * length) / 100;
u8  remainder = (percent * length) % 100;

for (u8 i = 0; i < filled; i++)      draw_full_tile(x + i, y);
if (remainder > 75)      draw_partial(BOSS_75, x + filled, y);
else if (remainder > 50) draw_partial(BOSS_50, x + filled, y);
else if (remainder > 25) draw_partial(BOSS_25, x + filled, y);
else                     draw_partial(EMPTY,    x + filled, y);

drawLifeBar(WINDOW, x, y, currentLife, maxLife, length, isBoss, isEnemy);
```

**Why Window plane?** It doesn't scroll with BG_A, so the bar stays anchored
while the level scrolls. Cost: you lose some BG_A real estate (Window and
BG_A share plane memory).

---

## 11. TidyText — Variable-Width Font via Runtime Tile Composition

`TidyText/src/tidyText.c` (452 lines) — **major discovery**. Solves the
variable-width font problem on 8x8 tile hardware by *building tiles at runtime*
that pack multiple characters across tile boundaries with bit masking.

Key mechanics:

```c
// Per-character widths (3..5 px typical for lowercase, 6..8 for uppercase)
u8 charWidthLookup[MAX_CHAR_ASCII + 1];

// Static buffer — no heap:
static u32 tileData[MAX_TILES_PER_STRING << 3];   // 64 tiles max

// Packs the string into runtime tiles, handling cross-tile spans:
u16 tidyText_BuildStringTiles(const char* str, u32* outTileData);
// - tidyText_PlaceCharPixels()  handles the cross-tile overlap
// - tidyText_MaskCharData()     builds mask: 0xFFFFFFFF << (32 - (width << 2))
// - tidyText_RemapPaletteIndices() swaps primary / secondary colors

// Allocates VRAM backwards from TILE_SPRITE_INDEX for temporary string tiles.
```

**When to use.** Dialog boxes where font must feel "real", credits screens,
RPG name tags. NOT for HUD numerics (those want monospace).

**Canonization note.** This is the cleanest solution we've found for
variable-width text. Should become the Dialog skill's canonical text renderer
if Sprint 1 passes.

---

## 12. RPG Text — Tile Text Renderer With Preshift / Ring Buffer

`RPG Text/src/tile_text_renderer.c` (260 lines) — different approach from
TidyText: a **streaming** tile renderer that uses a ring buffer and builds one
tile at a time, shifting pixels into a `preshift` register and shipping
completed tiles directly to VRAM via raw VDP ports.

Key idea — a single `u32` tile row accumulates pixel data with a rolling
shift/mask:

```c
static void char_to_buffer(TileTextRenderer* r, u16 chr) {
    chr |= r->font_plane;                       // allows 256-char planes
    const TFont* font = r->font;
    const u8*    src  = font->data + 8*chr;
    u32*         dest = r->buffer;

    u16  preshift = r->preshift;
    u32  mask     = ~(0xF << ((7 - preshift)*4));
    u32  fg1      = r->fg_color << ((7 - preshift)*4);
    u8   width    = font->widths[chr];

    for (u16 i = 0; i < width; i++) {
        u8 data = *src++;
        for (u16 j = 0; j < 8; j++) {
            if (data & 0x80) { *dest &= mask; *dest |= fg1; }
            dest++; data <<= 1;
        }
        fg1  >>= 4;
        mask  = 0xF0000000 | (mask >> 4);
        r->preshift++; r->preshift &= 7;

        if (~mask == 0) {                       // tile column full
            ship_and_clear_buffer(r);           // flush + new vpos
            mask = ~0xF0000000;
            fg1  = r->fg_color << 28;
        }
        dest -= 8;
    }
}

static void ship_and_clear_buffer(TileTextRenderer* r) {
    VDP_loadTileData(r->buffer, r->vpos, 1, CPU);
    if (++r->vpos >= r->max_vpos) r->vpos = r->base_vpos;  // ring wrap
    clear_buffer(r);
}

// Control codes in the script stream (like TTY):
#define ESCAPE_CHAR 0xFF
// set_font_plane, set_fg_color, advance_by, get_next_byte/word, new_line

// Escape dispatch:
if (chr_id == ESCAPE_CHAR) { chr_id = *r->text++; r->callback(r, chr_id); }
```

Plus **word wrapping** detection done *before* emission:

```c
u16 width = get_word_width(r->font, r->font_plane, r->text);
if (r->new_word && r->pixel_x + width > r->pixel_width)
    TTR_new_line(r);
```

**When to use.** Long scripts with control codes (RPG dialogue, cutscene
narration). Supports multiple font planes (up to 255 × 256 chars = 65K
glyphs — enough for Japanese).

**Contrast with TidyText.** TidyText builds the whole string upfront into a
static buffer; tile_text_renderer streams letter-by-letter with a ring
buffer that reuses VRAM slots — lower memory, higher cost per char,
suitable for typewriter-style animation.

---

## 13. RPG Text — Paseo (Phantasy Star II Port) Script Format

`RPG Text/src/paseo_dialog.c` — the Phantasy Star II intro ported to SGDK.
The script is a raw `u8[]` with 2-byte control codes and **three languages
packed into the same array** via offsets.

```c
const u16 intro_english  = 0x0000;
const u16 intro_japanese = 0x0327;
const u16 intro_french   = 0x05C4;

const u8 paseo_data[] = {
    0xFF, 0x0C, 0x00, 0x00,   // 0xFF 0x0C = conditional branch
    0xFF, 0x06,               // 0xFF 0x06 = load scene
    0xFF, 0x04,               // 0xFF 0x04 = pause
    0xFF, 0x02,               // 0xFF 0x02 = close box
    0xFF, 0x09, 0x07,         // 0xFF 0x09 0x07 = color tag
    /* ... text bytes ... */
};
```

**Lesson.** For multi-language RPGs, don't use multiple arrays — use a single
byte pool with per-language start offsets. Control codes are 2-byte so the
renderer stays fast; the dispatch happens in a single `ESCAPE_CHAR` switch.

---

## 14. State-Machine RPG — Axis-by-Axis Sub-pixel Slide Collision

`state machine RPG/state_machine/src/main.c` — top-down RPG with axis-by-axis
collision resolution. When a diagonal move collides, it tries to slide along
each axis independently, one pixel at a time.

```c
bool checkCollision(s16 x, s16 y) {
    s16 y_tile = y >> 3;
    s16 x_tile = x >> 3;
    s16 leftTile   = x_tile;
    s16 rightTile  = x_tile + (player.w >> 3);
    s16 topTile    = y_tile;
    s16 bottomTile = y_tile + (player.h >> 3);
    for (s16 j = topTile; j <= bottomTile; ++j)
        for (s16 i = leftTile; i <= rightTile; ++i)
            if (level[j*60 + i] == 6959) return TRUE;  // 6959 = solid marker
    return FALSE;
}

// In movement update:
if (!checkCollision(player.x + player.sentx, player.y + player.senty)) {
    player.x += player.sentx;
    player.y += player.senty;
} else {
    // Slide along X alone
    s16 testX = player.x;
    for (u8 i = 1; i < player.sentx; ++i) {
        testX++;
        if (!checkCollision(testX, player.y)) player.x = testX;
        else break;
    }
    // Slide along Y alone
    s16 testY = player.y;
    for (u8 i = 1; i < player.senty; ++i) {
        testY++;
        if (!checkCollision(player.x, testY)) player.y = testY;
        else break;
    }
}

player.x = clamp(player.x, LEFT_EDGE, 480 - player.w);
player.y = clamp(player.y, TOP_EDGE, 448 - player.h);
```

**Why this feels good.** When you hit a wall diagonally, you still slide along
it. When you walk into a corner, you stop cleanly. Standard top-down RPG
behavior.

Input mapping: the engine exposes `JOY1_UP/DOWN/LEFT/RIGHT/A/B/C/X/Y/Z/START/MODE`
bool flags updated once per frame via `FUNCAO_INPUT_SYSTEM()` — simple but
portable pattern for scenes that don't need event-driven input.

---

## 15. Bitmap Sine Wave — BMP Mode Trig Demo

`Bitmap Sine Wave/src/main.c` — the 2-line answer to "how do I use BMP mode".

```c
BMP_init(FALSE, BG_A, PAL0, FALSE);
BMP_setBufferCopy(TRUE);           // avoids flicker while drawing

// Left-shift palette entry to fill both nibbles (BMP mode requirement)
int pal_red = 14;
pal_red |= pal_red << 4;

// Draw
BMP_drawLine(&line);
BMP_setPixel(x, y, pal_red);
BMP_flip(FALSE);

// Trig:
y = 80 + sinFix16(i * 8);
y = 80 + cosFix16(i * 8);
// tangent (avoid div-by-zero):
if (cosFix16(a) != 0) y = 80 + F16_div(sinFix16(a), cosFix16(a));
```

**Key gotcha.** In BMP mode you *must* fill both nibbles of a palette index
(`pal |= pal << 4`) or you get gaps in drawn pixels. This is not obvious from
the docs — memorize it.

---

## 16. Two Colors Demo — 2-Color 256×128 Frame Buffer via Palette Masking

`Two Colors Demo/src/main.c` — exotic pseudo-bitmap mode: packs 256×128 pixels
in 2 colors into the tilemap with bit interleaving and palette masking. Tiles
are reused 4 times (each time revealing a different 32-row band) via 4
palettes where each palette bit selects a different row group.

```c
// Bit interleaving (8-bit tile byte):
// 0b10001000  // 2 pixels in bloc 1 (rows 0..31)
// 0b01000100  // 2 pixels in bloc 2 (rows 32..63)
// 0b00100010  // 2 pixels in bloc 3 (rows 64..95)
// 0b00010001  // 2 pixels in bloc 4 (rows 96..127)

// Palette masking (one color per bit):
// pal0: 0000000011111111
// pal1: 0000111100001111
// pal2: 0011001100110011
// pal3: 0101010101010101

inline static void draw_pixel_faster(u32* dest, u16 x, u16 y) {
    u32 value = _tab_value[x & 7] >> (y / 32);
    u16 index = _tab_tile_v[y & 31] + ((x / 8) * 8);
    dest[index] |= value;
}

// Tilemap setup: tile with palette 0 at 4 rows, palette 1 at 4 rows, etc.
DMA_doDmaFast(DMA_VRAM, tile_addr, VDP_getPlaneAddress(BG_B, 0,  6), 32*4, 2);
DMA_doDmaFast(DMA_VRAM, tile_addr, VDP_getPlaneAddress(BG_B, 0, 10), 32*4, 2);
DMA_doDmaFast(DMA_VRAM, tile_addr, VDP_getPlaneAddress(BG_B, 0, 14), 32*4, 2);
DMA_doDmaFast(DMA_VRAM, tile_addr, VDP_getPlaneAddress(BG_B, 0, 18), 32*4, 2);

// 60fps frame buffer via one DMA:
u32 frame_buffer[1024] = {0};
// ... draw into buffer ...
DMA_doDmaFast(DMA_VRAM, frame_buffer, TILE_USER_INDEX*32, 2048, 2);
```

**Use case.** Monochrome cutscene art, wireframe demos, vector-style title
screens. 1024 u32 = 4KB frame buffer. At 60fps and ~2KB DMA per frame it fits
comfortably in VBlank.

---

## 17. Change Screen Effect — Fade In/Out via Tile Data Masking

`Change Screen Effect/src/main.c` — four distinct fade transitions composed
on the same screen:

1. **TileFadeOut**: row-based, replaces rows top-to-bottom with a black tile
   via `VDP_fillTileMapRect`.
2. **TileFadeIn**: symmetric — pulls rows back from a preloaded tile.
3. **TileFideOutMosic1**: zeros entire rows of the tileset data (
   `t->tiles[row + i] = 0`) and re-uploads via `VDP_loadTileSet`. Result:
   horizontal stripes vanish.
4. **TileFideOutMosic2**: bit-mask fade — `u32 mask = (0x0FFFFFF0 >> (12*row))
   << (8*row)` applied to every tile.

```c
bool TileFadeOut(s16 row, u16 tileIndex) {
    if (row < 14) {
        VDP_fillTileMapRect(BG_A, TILE_ATTR_FULL(PAL0,TRUE,0,0,tileIndex), 0,row,    40, 1);
        VDP_fillTileMapRect(BG_A, TILE_ATTR_FULL(PAL0,TRUE,0,0,tileIndex), 0,28-row, 40, 1);
    } else if (row == 14) {
        VDP_fillTileMapRect(BG_A, TILE_ATTR_FULL(PAL0,TRUE,0,0,tileIndex), 0,row,    40, 1);
        return TRUE;
    }
    return FALSE;
}

// Mosaic by zeroing tile rows:
void TileFideOutMosic1(s16 row, TileSet* t, u16 index) {
    for (u32 i = 0; i < t->numTile*8; i += 8)
        t->tiles[row + i] = 0;
    VDP_loadTileSet(t, index, DMA);
}
```

**Lesson.** For scene transitions, a `memcpy` of the original tileset at the
start of the transition lets you restore it cheaply when the transition ends:

```c
memcpy(tileset.tiles, bgb.tileset->tiles, sizeof(u32) * bgb.tileset->numTile * 8);
VDP_loadTileSet(bgb.tileset, 1, DMA);
```

Classic pattern for "fade to flash and come back".

**Canonical reading.** This is now a reference for
`tile_mask_mosaic_transition` inside `scene_transition_card`, not a universal
scene-change default. Approve only with backup/restore of tileset, DMA budget,
`teardown_reset_plan` and fallback in `palette_fade_bridge`.

---

## 18. Raycasting Anael — Precomputed Column Tiles + Inline ASM DMA Flush

`Raycasting Anael/src/main.c` + `render.c` — a DOOM-style ray marching renderer
optimized for 320×224 at 60fps. The key tricks:

### 18.1 Precomputed column tiles (`render.c::render_loadTiles`)

Tiles are generated at startup so each "wall column" is a single tile pick.
Each tile encodes a column of fixed height with a 4-pixel-wide color strip on
the left 4 columns (leaving the right 4 empty so BG_B can be offset by 4 px
to double the horizontal resolution).

```c
// 9 possible column heights per "shade" group
// 8 shade groups for PAL0, another 8 shades for PAL1 (via two passes)
for (u8 pass = 0; pass < 2; ++pass) {
    for (u16 t = 1; t <= 8; t++) {
        memset(tile, 0, 32);
        for (u16 c = 0; c < 8; c++) {
            for (u16 h = t-1; h < 8; h++) {
                for (u16 b = 0; b < 2; b++) {
                    u8 color = (c+1 == 8 ? c : c+1);
                    tile[4*h + b] = (c) | (color << 4);
                }
            }
            VDP_loadTileData((u32*)tile, t + c*8 + pass*64, 1, CPU);
        }
    }
}
```

This gives 2×64 = 128 unique column tiles covering the full wall rendering
grammar. Per frame you just pick `tile = f(distance, palette)` and drop it in
the tilemap — no per-pixel rendering.

### 18.2 Two-plane horizontal shift (`main.c`)

```c
VDP_setHorizontalScroll(BG_A, 0);
VDP_setHorizontalScroll(BG_B, 4);   // 4-pixel offset doubles effective h-resolution
```

BG_A and BG_B draw interleaved 4-px columns → effective 320/4 = 80 columns
looks like 160 columns from the player's eye.

### 18.3 H-Int palette swap per scanline

```c
VDP_setHIntCounter(HINT_SCANLINE_START_PALETTE_SWAP - 1);
SYS_setHIntCallback(hint_load_hud_pals_callback);
VDP_setHInterrupt(TRUE);
```

Top half of the screen uses wall palettes, bottom half uses HUD palettes. The
H-Int callback rewrites the palette registers the instant the scanline
reaches the HUD — true mid-frame palette swap.

### 18.4 Inline ASM DMA queue flush (`render.c::render_DMA_flushQueue`)

```c
vu32* vdpCtrl_ptr_l = (u32*)VDP_CTRL_PORT;
__asm volatile (
    "subq.w  #1,%2\n"
    ".fq_loop_%=:\n\t"
    "move.l  (%0)+,(%1)\n\t"
    "move.l  (%0)+,(%1)\n\t"
    "move.l  (%0)+,(%1)\n\t"
    "move.w  (%0)+,(%1)\n\t"
    "move.w  (%0)+,(%1)\n\t"      // word write triggers DMA per SEGA note
    "dbra    %2,.fq_loop_%="
    :
    : "a" (dmaQueues), "a" (vdpCtrl_ptr_l), "d" (queueIndex)
    : );
DMA_clearQueue();
```

**Key gotcha in the comment.** "*Important to use word write for command
triggering DMA (see SEGA notes)*". The command register is 32-bit but must be
triggered with a word write — otherwise DMA silently fails on some hardware
revisions.

### 18.5 Fixed RAM addresses

`consts_ext.h` pins `vdpSpriteCache` and DMA queues to **fixed RAM
addresses** — `checkConstantsCorrectValues()` verifies them at boot. This is
how Anael squeezes out a few extra cycles: no indirection through a global
pointer, the assembler encodes the address directly.

**When to copy this pattern.** Only for projects where you've exhausted
every other optimization. The fixed-address trick is fragile and
anti-portable.

---

## 19. Trigonometry Projetil — sin/cos Table + atan2 Polynomial

`Trigonometry Projetil/src/trigonometric.c` — a complete trig library: 91-entry
sin table (0..90°), polynomial atan, and full 360° helpers.

```c
// 91 entries, 1° resolution, covers first quadrant:
fix16 TRIGONOMETRIC_TABLE[TABLE_SIZE] = {
    FIX16(0.0000), FIX16(0.0175), FIX16(0.0349), /* ... */ FIX16(1.0000)
};

// atan via 4-term odd polynomial (Chebyshev-fit):
fix16 FIX16ATAN(fix16 x) {
    const fix16 a1 = FIX16( 0.999999999999999);
    const fix16 a3 = FIX16(-0.333333333333196);
    const fix16 a5 = FIX16( 0.199999975760886);
    const fix16 a7 = FIX16(-0.142356622678549);
    fix16 x2 = F16_mul(x, x);
    fix16 x3 = F16_mul(x2, x);
    fix16 x5 = F16_mul(x3, x2);
    fix16 x7 = F16_mul(x5, x2);
    return F16_mul(a1,x) + F16_mul(a3,x3) + F16_mul(a5,x5) + F16_mul(a7,x7);
}

// atan2 with quadrant handling:
fix16 FIX16ATAN2(fix16 y, fix16 x);

// Use from game code: find angle between two points
fix16 angle = TRG_FIND_ANGLE(p1x, p1y, p2x, p2y);

// Project from pivot along angle by distance (move entity forward):
void TRG_MXY_PAD(fix16* out_x, fix16* out_y,
                 fix16 px, fix16 py, fix16 ang, fix16 dist);
```

**Use cases.** Bullet trajectories, enemy homing, radial menus, dash angles,
physics projection.

**Lesson.** A 91-entry table + quadrant reflection is enough for any 68k
game — you will never need full 360° tables (waste of ROM). The atan2
polynomial is ~6µs on 68000, well within a frame budget.

---

## 20. Summary — Pattern Index

Quick reference, grouped by system:

**Scrolling & Parallax**
- Per-line HScroll preset buffer — §1.1, §1.4, §8.1
- Per-line VScroll for hills — §8.2, §1.2
- Dual-plane parallax via bit shift — §2.1 (`x >> 3, y >> 5`)
- `MAP_scrollTo` vs manual column/row streaming — §2.2

**H-Int Effects**
- Wobble / sine distortion — §1.1
- Bitmap zoom — §1.2
- Spotlight (Hilight-Shadow) — §1.3
- Mid-frame palette swap (HUD reveal) — §18.3

**Physics & Game Feel**
- Multi-rate deceleration — §2.4
- Coyote time + jump buffer + half-jump — §3.1
- Deadzone camera (struct-based) — §3.2
- Slope collision with per-column gradient — §6
- Axis-by-axis slide collision — §14

**Entity / Scene Management**
- Minimal function-pointer entity manager — §7.1
- SGDK TSK_ multitasking — §4
- Benchmark framework shape — §5

**HUD & Text**
- Sprite-bar HUD with SPR_setFrame — §2.3
- Window plane HUD with graded tiles — §10
- Custom font via tile-index math — §7.3
- Variable-width font (batch compose) — §11 (TidyText)
- Streaming tile text renderer with preshift — §12
- Multi-language packed script with control codes — §13

**Large Maps / VRAM Pressure**
- Refcounted tile cache via `MAP_` callback — §9

**Racing / Pseudo-3D**
- ZMAP perspective projection — §8.1
- Hills via VScroll delta — §8.2
- Curves via HScroll delta — §8.3
- Color banding per Z-stripe — §8.3

**Bitmap & Non-standard Modes**
- BMP mode + palette nibble fill — §15
- 2-color 256×128 frame buffer via palette masking — §16
- Tile fade with bit-mask — §17

**3D / Ray Marching**
- Precomputed column tiles for raycasting — §18.1
- Two-plane 4-px offset horizontal doubling — §18.2
- Inline ASM DMA queue flush — §18.4
- Fixed RAM address optimization — §18.5

**Math**
- Sin/cos table (91 entries) + quadrant reflection — §19
- atan2 via 4-term polynomial — §19
- Pivot + angle + distance projection — §19

---

## 21. Canonization Priority Queue

These patterns should be promoted to canonical skills, in order of impact on
the 10 AAA art skills roadmap:

| Rank | Pattern | Target Skill | Source |
|------|---------|--------------|--------|
| 1 | Variable-width font (TidyText) | Dialog / RPG Text skill | §11 |
| 2 | Per-line HScroll for pseudo-3D | Racing / Road skill | §8.1-§8.3 |
| 3 | Tile refcount cache | Streaming Map / Huge Level skill | §9 |
| 4 | H-Int wobble/scale/spotlight | FX Combination skill | §1 |
| 5 | Coyote + buffer + half-jump | Platformer Feel skill | §3.1 |
| 6 | Multi-rate deceleration | Character Physics skill | §2.4 |
| 7 | Entity manager (function ptr) | Scene Management skill | §7.1 |
| 8 | Sprite-bar / Window HUD | HUD skill | §2.3, §10 |
| 9 | Slope collision | Level Collision skill | §6 |
| 10 | Trig library | Projectile / Combat skill | §19 |

None of these are canon until their Sprint passes approval. Sprint 1 draft
(Sprite Animation / Character Design / Multi-plane) remains blocked on human
review. The patterns in this appendix inform Sprint 2+ draft content.

---

## 22. File Reference Index

Every snippet above is quotable via these exact paths (brackets in directory
names — see `tools/sgdk_wrapper/build_inner.bat` for the 8.3 path
workaround).

- `SGDK_Engines/SGDK_LIZARDRIVE/sample/fx/h-int/wobble/src/main.c`
- `SGDK_Engines/SGDK_LIZARDRIVE/sample/fx/h-int/scaling/src/main.c`
- `SGDK_Engines/SGDK_LIZARDRIVE/sample/fx/hilight-shadow/src/main.c`
- `SGDK_Engines/SGDK_LIZARDRIVE/sample/fx/scroll/linescroll/src/main.c`
- `SGDK_Engines/SGDK_LIZARDRIVE/sample/sonic/src/{camera,level,hud,player}.c`
- `SGDK_Engines/SGDK_LIZARDRIVE/sample/platformer/src/{camera,physics,player,map}.c`
- `SGDK_Engines/SGDK_LIZARDRIVE/sample/multitasking/src/main.c`
- `SGDK_Engines/SGDK_LIZARDRIVE/sample/bench/src/main.c`
- `SGDK_Engines/Mega Metroid [VER.001] .../src/main.c`
- `SGDK_Engines/NEXZR MD [VER.001] .../src/{background,entitymanager,characters}.c`
- `SGDK_Engines/MegaDriving [VER.1.0] .../upstream/lou/{01_basic_road,02_hills,04_colors}/src/main.c`
- `SGDK_Engines/Shadow Dancer Revisitado [VER.001] .../src/mapHandler.c`
- `SGDK_Engines/Lifebar [VER.001] .../src/{main.c,lifebar.h}`
- `SGDK_Engines/TidyText [VER.001] .../src/tidyText.c`
- `SGDK_Engines/RPG Text [VER.001] .../src/{tile_text_renderer.c,paseo_dialog.c}`
- `SGDK_Engines/state machine RPG [VER.001] .../state_machine/src/main.c`
- `SGDK_Engines/Bitmap Sine Wave [VER.001] .../src/main.c`
- `SGDK_Engines/Two Colors Demo [VER.001] .../src/main.c`
- `SGDK_Engines/Change Screen Effect [VER.001] .../src/main.c`
- `SGDK_Engines/Raycasting Anael [VER.001] .../src/{main.c,render.c}`
- `SGDK_Engines/Trigonometry Projetil [VER.250221] .../trigonometry_v250221/src/trigonometric.c`

---

*End of appendix. Pair with the first-pass research report when complete,
merge into `06_AI_MEMORY_BANK.md` only after canonization gate approval.*
