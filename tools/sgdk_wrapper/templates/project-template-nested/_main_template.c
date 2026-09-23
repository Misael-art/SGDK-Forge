/**
 * AAA EFFECT LAB - Eixo 01: Profundidade & Movimento
 * Main.c - Tech Demo de Parallax e Scroll
 */

#include <genesis.h>

// Estrutura de estado global
typedef enum {
    SCENE_INTRO,
    SCENE_PARALLAX_BASIC,
    SCENE_PARALLAX_ADVANCED,
    SCENE_VERTICAL_SCROLL,
    SCENE_STREAMING,
    SCENE_MOMENTUM,
    SCENE_MAX
} SceneType;

// Variaveis globais
static SceneType g_scene;
static u16 g_frames;
static u16 g_scrollX_A;
static u16 g_scrollX_B;
static u16 g_scrollY;
static fix16 g_camX;
static fix16 g_camY;
static fix16 g_playerX;
static fix16 g_playerY;
static fix16 g_playerVelX;
static fix16 g_playerVelY;

// Paleta basica para teste
const u16 PALETTE_BG[16] = {
    0x0000, 0x0EEE, 0x00E0, 0x000E,
    0x0E00, 0x0EE0, 0x00EE, 0x0E0E,
    0x0888, 0x0444, 0x0CCC, 0x0884,
    0x0488, 0x0848, 0x0C84, 0x0FFF
};

// ---- Sistema de Input ----
static void handle_input(void) {
    u16 joy = JOY_readJoypad(JOY_1);

    // Movimento do jogador com momentum
    fix16 accel = FIX16(0.08);
    fix16 maxSpeed = FIX16(2.0);
    fix16 friction = FIX16(0.9);

    if (joy & BUTTON_LEFT) {
        g_playerVelX -= accel;
    } else if (joy & BUTTON_RIGHT) {
        g_playerVelX += accel;
    }

    if (joy & BUTTON_UP) {
        g_playerVelY -= accel;
    } else if (joy & BUTTON_DOWN) {
        g_playerVelY += accel;
    }

    // Aplicar friccao
    g_playerVelX = F16_mul(g_playerVelX, friction);
    g_playerVelY = F16_mul(g_playerVelY, friction);

    // Limitar velocidade
    if (g_playerVelX > maxSpeed) g_playerVelX = maxSpeed;
    if (g_playerVelX < -maxSpeed) g_playerVelX = -maxSpeed;
    if (g_playerVelY > maxSpeed) g_playerVelY = maxSpeed;
    if (g_playerVelY < -maxSpeed) g_playerVelY = -maxSpeed;

    // Atualizar posicao
    g_playerX += g_playerVelX;
    g_playerY += g_playerVelY;

    // Aplicar bounds
    if (g_playerX < FIX16(8)) g_playerX = FIX16(8);
    if (g_playerX > FIX16(312)) g_playerX = FIX16(312);
    if (g_playerY < FIX16(8)) g_playerY = FIX16(8);
    if (g_playerY > FIX16(216)) g_playerY = FIX16(216);
}

// ---- Sistema de Camera com Damping ----
static void update_camera_smooth(void) {
    fix16 targetX = g_playerX;
    fix16 targetY = g_playerY;

    fix16 damping = FIX16(0.1);
    fix16 diffX = targetX - g_camX;
    fix16 diffY = targetY - g_camY;

    g_camX += F16_mul(diffX, damping);
    g_camY += F16_mul(diffY, damping);
}

// ---- Sistema de Parallax ----
static void update_parallax_basic(void) {
    // BG_A moves at 1.0x speed
    g_scrollX_A = F16_toInt(g_camX);
    // BG_B moves at 0.5x speed
    g_scrollX_B = F16_toInt(g_camX / FIX16(2));

    VDP_setHorizontalScroll(BG_A, -g_scrollX_A);
    VDP_setHorizontalScroll(BG_B, -g_scrollX_B);
}

static void update_parallax_advanced(void) {
    // 3+ layers: BG_B (far), BG_A (mid), sprites (near)
    g_scrollX_A = F16_toInt(g_camX);
    g_scrollX_B = F16_toInt(F16_mul(g_camX, FIX16(0.5)));

    VDP_setHorizontalScroll(BG_A, -g_scrollX_A);
    VDP_setHorizontalScroll(BG_B, -g_scrollX_B);
}

// ---- Sistema de Scroll Vertical ----
static void update_vertical_scroll(void) {
    g_scrollY = F16_toInt(g_camY);
    VDP_setVerticalScroll(BG_A, g_scrollY);
    VDP_setVerticalScroll(BG_B, g_scrollY >> 1); // Half speed
}

// ---- Scenes ----
static void scene_intro_init(void) {
    VDP_clearPlane(BG_A, FALSE);
    VDP_clearPlane(BG_B, FALSE);
    PAL_setPalette(0, PALETTE_BG, CPU);

    VDP_drawText("AAA EFFECT LAB", 10, 5);
    VDP_drawText("Eixo 01: Profundidade & Movimento", 5, 7);
    VDP_drawText("Use D-PAD para mover", 8, 12);
    VDP_drawText("START para trocar cena", 7, 14);

    g_playerX = FIX16(160);
    g_playerY = FIX16(112);
    g_playerVelX = FIX16(0);
    g_playerVelY = FIX16(0);
    g_camX = g_playerX;
    g_camY = g_playerY;
}

static void scene_intro_update(void) {
    handle_input();
    update_camera_smooth();

    if (JOY_readJoypad(JOY_1) & BUTTON_START) {
        g_scene = SCENE_PARALLAX_BASIC;
    }
}

static void scene_parallax_basic_init(void) {
    VDP_clearPlane(BG_A, FALSE);
    VDP_clearPlane(BG_B, FALSE);

    // Desenhar tiles de teste para parallax
    for (u16 i = 0; i < 40; i++) {
        VDP_setTileMapXY(BG_A, TILE_ATTR_FULL(PAL0, 0, 0, 0, 1), i, 20);
        VDP_setTileMapXY(BG_B, TILE_ATTR_FULL(PAL0, 0, 0, 0, 2), i, 15);
    }

    VDP_drawText("Parallax Basico", 12, 3);
    VDP_drawText("BG_A=1x BG_B=0.5x", 10, 5);
}

static void scene_parallax_basic_update(void) {
    handle_input();
    update_camera_smooth();
    update_parallax_basic();

    if (JOY_readJoypad(JOY_1) & BUTTON_START) {
        g_scene = SCENE_PARALLAX_ADVANCED;
    }
}

static void scene_parallax_advanced_init(void) {
    VDP_clearPlane(BG_A, FALSE);
    VDP_clearPlane(BG_B, FALSE);

    VDP_drawText("Parallax Avancado", 11, 3);
    VDP_drawText("3+ camadas", 12, 5);

    for (u16 i = 0; i < 40; i++) {
        VDP_setTileMapXY(BG_B, TILE_ATTR_FULL(PAL0, 0, 0, 0, 3), i, 10);
        VDP_setTileMapXY(BG_A, TILE_ATTR_FULL(PAL0, 0, 0, 0, 2), i, 18);
    }
}

static void scene_parallax_advanced_update(void) {
    handle_input();
    update_camera_smooth();
    update_parallax_advanced();

    if (JOY_readJoypad(JOY_1) & BUTTON_START) {
        g_scene = SCENE_VERTICAL_SCROLL;
    }
}

static void scene_vertical_scroll_init(void) {
    VDP_clearPlane(BG_A, FALSE);
    VDP_clearPlane(BG_B, FALSE);

    VDP_drawText("Scroll Vertical", 12, 3);
    VDP_drawText("Torre Ascendente", 11, 5);

    for (u16 i = 0; i < 28; i++) {
        VDP_setTileMapXY(BG_A, TILE_ATTR_FULL(PAL0, 0, 0, 0, 2), 10, i);
        VDP_setTileMapXY(BG_A, TILE_ATTR_FULL(PAL0, 0, 0, 0, 2), 30, i);
    }
}

static void scene_vertical_scroll_update(void) {
    handle_input();
    update_camera_smooth();
    update_vertical_scroll();

    if (JOY_readJoypad(JOY_1) & BUTTON_START) {
        g_scene = SCENE_MOMENTUM;
    }
}

static void scene_momentum_init(void) {
    VDP_clearPlane(BG_A, FALSE);
    VDP_clearPlane(BG_B, FALSE);

    VDP_drawText("Momentum & Inercia", 10, 3);
    VDP_drawText("Aceleracao + Friccao", 10, 5);

    g_playerVelX = FIX16(0);
    g_playerVelY = FIX16(0);
}

static void scene_momentum_update(void) {
    handle_input();

    // Desenhar jogador como sprite simples (simulado com tile)
    VDP_setTileMapXY(BG_A, TILE_ATTR_FULL(PAL0, 0, 0, 0, 1),
                     F16_toInt(g_playerX) >> 3, F16_toInt(g_playerY) >> 3);

    if (JOY_readJoypad(JOY_1) & BUTTON_START) {
        g_scene = SCENE_INTRO;
    }
}

// ---- Main ----
int main(bool hardReset) {
    // System init
    SYS_disableInts();
    VDP_setScreenWidth320();
    VDP_setScreenHeight240();
    VDP_setPlaneSize(64, 32, FALSE);
    VDP_setBackgroundColor(0);

    SPR_init();
    JOY_init();

    g_scene = SCENE_INTRO;
    g_frames = 0;

    SYS_enableInts();

    // Scene init
    scene_intro_init();

    while (TRUE) {
        switch (g_scene) {
            case SCENE_INTRO:
                scene_intro_update();
                break;
            case SCENE_PARALLAX_BASIC:
                scene_parallax_basic_update();
                break;
            case SCENE_PARALLAX_ADVANCED:
                scene_parallax_advanced_update();
                break;
            case SCENE_VERTICAL_SCROLL:
                scene_vertical_scroll_update();
                break;
            case SCENE_MOMENTUM:
                scene_momentum_update();
                break;
            default:
                g_scene = SCENE_INTRO;
                break;
        }

        g_frames++;
        VDP_waitVSync();
    }

    return 0;
}
