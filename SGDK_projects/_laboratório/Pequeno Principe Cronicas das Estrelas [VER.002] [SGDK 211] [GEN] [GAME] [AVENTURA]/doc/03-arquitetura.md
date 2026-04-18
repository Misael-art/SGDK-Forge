# Arquitetura — Pequeno Príncipe VER.002

## Visão Geral

Arquitetura de jogo contemplativo para Mega Drive com FSM de 8 estados,
VBlank callback centralizado, scroll buffers duplos e pipeline de arte modular.

---

## Estrutura de Diretórios

```
src/
  main.c              — entry point, game loop principal
  core/
    engine.c/.h       — GameCtx, FSM driver, transições de estado
    input.c/.h        — joypad, debounce, pressed/held/released
    vblank.c/.h       — VBlank callback, DMA flush, scroll apply
    audio.c/.h        — XGM2 wrapper, fade, SFX dispatch
  game/
    player.c/.h       — físicas fix32, cachecol spring chain
    dialogue.c/.h     — typewriter, speaker, input handling
    codex.c/.h        — entradas do codex, renderização
  planets/
    b612.c/.h         — line scroll + palette cycling + H-Int
    rei.c/.h          — parallax multicamada + column scroll
    vaidoso.c/.h      — sprite scaling + palette flash
    acendedor.c/.h    — H-Int line-level day/night
    geografo.c/.h     — MAP API + window HUD mini-map
    stub_planets.c/.h — stub para planetas não implementados
  travels/
    travel_common.c/.h — FSM de viagem, entrada/saída
    travel_a.c/.h      — pseudo-3D Space Harrier
    stub_travels.c/.h  — stub para viagens não implementadas
  ui/
    hud.c/.h          — Window Plane HUD
    menu.c/.h         — title, pause, codex, credits screens
    effects.c/.h      — screen shake, palette flash, fade in/out
inc/
  pp2.h               — header mestre (inclui tudo)
  types.h             — enums, structs (GameCtx, Player, Scarf...)
  constants.h         — defines de hardware, tile bases, limites
res/
  resources.res       — declaração de todos os recursos SGDK
  gfx/
    sprites/          — PNGs indexados do player, NPCs
    tilesets/         — PNGs de tilesets de planetas
    bg/               — PNGs de backgrounds
  audio/              — arquivos XGM2
```

---

## FSM — 8 Estados

```
BOOT → TITLE → INTRO → PLANET → TRAVEL → PAUSE → CODEX → CREDITS
          ↑_______________|         |
                           ←────────┘ (ao completar viagem)
```

| Estado | Enter | Update | Draw |
|--------|-------|--------|------|
| BOOT | init HW, fade in | — | splash |
| TITLE | play BGM_TITLE | handle input | title screen |
| INTRO | — | scroll text | story text |
| PLANET | load planet assets | physics+input+planet | bg+sprites+hud |
| TRAVEL | load travel | travel logic | travel render |
| PAUSE | freeze | menu nav | pause overlay |
| CODEX | freeze | nav | codex text |
| CREDITS | fade | scroll | credits text |

---

## VBlank Callback

```c
// vblank.c — registrado uma vez em Engine_init()
static void vblankCallback(void)
{
    // 1. Aplicar scroll buffers via DMA
    VDP_setHorizontalScrollLine(BG_B, 0, g_ctx.hscrollB, 224, DMA);
    VDP_setHorizontalScrollLine(BG_A, 0, g_ctx.hscrollA, 224, DMA);
    VDP_setVerticalScrollTile(BG_A, 0, g_ctx.vscrollA, 20, DMA);

    // 2. SPR_update (DMA de sprite table)
    SPR_update();

    // 3. Tick de audio
    XGM2_update();

    // 4. Incrementa frame counter
    g_ctx.frameCounter++;
}
```

---

## Player — Física fix32

```c
// Constantes (sem float)
#define GRAVITY         FIX32(0.25)
#define GRAVITY_GLIDE   FIX32(0.06)
#define JUMP_FORCE      FIX32(-5.5)
#define MAX_FALL        FIX32(5.0)
#define WALK_SPEED      FIX32(1.5)

// Update (core/player.c)
void Player_update(GameCtx *ctx, u16 held)
{
    bool gliding = (held & BUTTON_A) && !player->onGround;
    fix32 gravity = gliding ? GRAVITY_GLIDE : GRAVITY;

    player->vy = fix32Add(player->vy, gravity);
    if (fix32ToInt(player->vy) > fix32ToInt(MAX_FALL))
        player->vy = MAX_FALL;

    player->y = fix32Add(player->y, player->vy);
    player->x = fix32Add(player->x, player->vx);
    // ground collision, bounds...
}
```

---

## Cachecol Spring Chain

```c
// 5 segmentos, sem float
void Player_updateScarf(GameCtx *ctx)
{
    ScarfSegment *scarf = ctx->scarf;
    s16 anchorX = ctx->player.screenX - (ctx->player.facingLeft ? -8 : 8);
    s16 anchorY = ctx->player.screenY + 4;

    // Segmento 0 segue o pescoço
    scarf[0].x = FIX16(anchorX);
    scarf[0].y = FIX16(anchorY);

    for (u8 i = 1; i < PP2_SCARF_SEGMENTS; i++)
    {
        fix16 dx = fix16Sub(scarf[i-1].x, scarf[i].x);
        fix16 dy = fix16Sub(scarf[i-1].y, scarf[i].y);
        // spring damping
        scarf[i].x = fix16Add(scarf[i].x, fix16Div(dx, FIX16(4)));
        scarf[i].y = fix16Add(scarf[i].y, fix16Div(dy, FIX16(4)));
        // wind effect
        fix16 wind = fix16Mul(sinFix16((ctx->frameCounter * 3) + (i << 4)),
                              FIX16(0.3));
        scarf[i].x = fix16Add(scarf[i].x, wind);
    }
}
```

---

## Diálogo — Typewriter

```c
// Exibe 1 caractere por tick do typewriter counter
void Dialogue_update(GameCtx *ctx)
{
    if (!ctx->dialogue.active) return;
    if (ctx->dialogue.typewriterPos < ctx->dialogue.totalChars)
    {
        ctx->dialogue.typewriterPos++;
        ctx->dialogue.dirty = TRUE;
    }
}
```

---

## H-Int Split (B-612 / Acendedor)

```c
// hint.c — callback registrado com SYS_setHIntCallback
static u16 g_hintLine = 192;
static const u16 *g_palTop;
static const u16 *g_palBottom;

static void hintCallback(void)
{
    u16 scanline = GET_VCOUNTER; // ler VCounter
    if (scanline == g_hintLine)
        PAL_setPalette(PAL0, g_palBottom, DMA);
}

void HintFx_configure(const u16 *top, const u16 *bot, u16 line)
{
    g_palTop    = top;
    g_palBottom = bot;
    g_hintLine  = line;
    PAL_setPalette(PAL0, top, DMA);
    VDP_setHIntCounter(line);
    VDP_setHInterrupt(TRUE);
    SYS_setHIntCallback(hintCallback);
}
```

---

## MAP API — Geógrafo

```c
// geografo.c
static Map *g_map;

void Geografo_enter(GameCtx *ctx)
{
    // Carregar tileset + mapa (512×224 px = 64×28 tiles)
    PAL_setPalette(PAL0, geografo_tileset_pal.data, DMA);
    g_map = MAP_create(&geografo_map, BG_A, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, TILE_USER_INDEX));
}

void Geografo_update(GameCtx *ctx)
{
    // Scroll câmera
    ctx->cameraX = fix32Add(ctx->cameraX, ctx->player.vx);
    MAP_scrollTo(g_map, fix32ToInt(ctx->cameraX), 0);
}

void Geografo_exit(GameCtx *ctx)
{
    MAP_release(g_map);
    g_map = NULL;
}
```

---

## XGM2 Audio

```c
// audio.c
void Audio_playBgm(BgmId id)
{
    if (id == g_currentBgm) return;
    if (g_currentBgm != BGM_NONE)
        XGM2_fadeOut(60); // 60 frames fade
    g_currentBgm = id;
    XGM2_play(bgm_table[id]);
}

void Audio_playSfx(SfxId id)
{
    XGM2_playPCM(sfx_table[id], sfx_priority[id], SOUND_PCM_CH2);
}
```

---

## Pseudo-3D Travel A

```c
// travel_a.c — floor line scroll
void TravelA_updateFloor(GameCtx *ctx)
{
    u16 frame = ctx->travelFrame;
    // Horizonte em y=112
    for (u16 y = 112; y < 224; y++)
    {
        // perspectiva: distância do horizonte
        u16 depth = y - 112;
        // rotação do floor baseada no frame
        ctx->hscrollB[y] = (s16)(-(s32)(depth * frame) >> 5);
    }
    // Céu: sem scroll
    for (u16 y = 0; y < 112; y++)
        ctx->hscrollB[y] = 0;
}
```
