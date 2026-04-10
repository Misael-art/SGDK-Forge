#include <genesis.h>

// Game states
typedef enum {
    GAME_MENU,
    GAME_PLAYING,
    GAME_OVER
} GameState;

// Game variables
static GameState gameState = GAME_MENU;
static s16 playerX = 160;
static s16 playerY = 180;
static s16 playerLane = 1; // 0=left, 1=center, 2=right
static u32 score = 0;
static u16 speed = 2;
static u16 frameCount = 0;

// Scroll effects
static s16 roadOffset = 0;
static s16 roadScroll[224]; // Line scroll for road effect
static s16 backgroundOffset = 0;

// Palette animation
static u16 palettePhase = 0;

// Simple player representation (colored tile)
static u16 playerTileIndex;

// Obstacles system
#define MAX_OBSTACLES 8
typedef struct {
    s16 x, y;
    s16 lane;
    u16 active;
    u16 tileIndex;
} Obstacle;

static Obstacle obstacles[MAX_OBSTACLES];
static u16 obstacleSpawnTimer = 0;
static u16 obstacleTileIndex;

void initGame(void) {
    // Setup video mode
    VDP_setScreenWidth320();
    VDP_setScreenHeight224();
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_PLANE);
    
    // Create simple neon palette
    u16 neonColors[16];
    neonColors[0] = 0x0000; // Transparent
    neonColors[1] = 0x0000; // Black
    neonColors[2] = 0x0222; // Dark blue
    neonColors[3] = 0x0444; // Medium blue
    neonColors[4] = 0x0666; // Light blue
    neonColors[5] = 0x0444; // Dark green
    neonColors[6] = 0x0888; // Medium green
    neonColors[7] = 0x0CCC; // Light green
    neonColors[8] = 0x4440; // Dark red
    neonColors[9] = 0x8880; // Medium red
    neonColors[10] = 0xCCC0; // Light red
    neonColors[11] = 0x8888; // Yellow
    neonColors[12] = 0x0AAA; // Cyan
    neonColors[13] = 0xA0A0; // Magenta
    neonColors[14] = 0xEEE0; // White (will be animated)
    neonColors[15] = 0xEEE8; // Light gray
    
    PAL_setPalette(0, neonColors, DMA);
    
    // Setup background planes
    VDP_setTextPlane(BG_B);
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    
    // Create simple player tile
    playerTileIndex = TILE_USER_INDEX;
    VDP_fillTileData(playerTileIndex, 0x0EEE, 1, CPU); // Bright cyan tile
    
    // Create obstacle tile
    obstacleTileIndex = TILE_USER_INDEX + 1;
    VDP_fillTileData(obstacleTileIndex, 0xE00, 1, CPU); // Red obstacle tile
    
    // Initialize obstacles
    for (u16 i = 0; i < MAX_OBSTACLES; i++) {
        obstacles[i].active = FALSE;
    }
    
    // Initialize scroll arrays
    for (s16 i = 0; i < 224; i++) {
        roadScroll[i] = 0;
    }
    
    gameState = GAME_MENU;
}

void updatePlayer(void) {
    u16 joy = JOY_readJoypad(JOY_1);
    
    // Lane switching
    if (joy & BUTTON_LEFT && playerLane > 0) {
        playerLane--;
        playerX = 80 + (playerLane * 80);
    }
    if (joy & BUTTON_RIGHT && playerLane < 2) {
        playerLane++;
        playerX = 80 + (playerLane * 80);
    }
    
    // Clear previous position and draw new one
    VDP_clearTileMapRect(BG_A, (playerX - 8) >> 3, (playerY - 8) >> 3, 2, 2);
    VDP_setTileMapXY(BG_A, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, playerTileIndex), playerX >> 3, playerY >> 3);
}

void updateRoadEffect(void) {
    // Create perspective road effect with simple waves
    roadOffset -= speed;
    
    for (s16 y = 0; y < 224; y++) {
        // Calculate perspective factor
        s16 perspective = (y * 8) / 224;
        
        // Apply simple wave for road curves (using frameCount for animation)
        s16 wave = (frameCount + perspective) & 63;
        if (wave > 32) wave = 64 - wave;
        wave -= 16;
        
        // Combine with base scroll
        roadScroll[y] = roadOffset + wave;
    }
    
    // Apply line scroll
    VDP_setHorizontalScrollLine(BG_A, 0, roadScroll, 224, CPU);
}

void updateBackground(void) {
    // Parallax background scroll
    backgroundOffset -= speed / 2;
    VDP_setHorizontalScroll(BG_B, backgroundOffset);
}

void updateObstacles(void) {
    // Spawn new obstacles
    obstacleSpawnTimer++;
    if (obstacleSpawnTimer > (60 - speed * 3)) { // Spawn rate based on speed
        obstacleSpawnTimer = 0;
        
        // Find inactive obstacle slot
        for (u16 i = 0; i < MAX_OBSTACLES; i++) {
            if (!obstacles[i].active) {
                obstacles[i].active = TRUE;
                obstacles[i].lane = random() % 3; // Random lane
                obstacles[i].x = 80 + (obstacles[i].lane * 80);
                obstacles[i].y = -16; // Start above screen
                obstacles[i].tileIndex = obstacleTileIndex;
                break;
            }
        }
    }
    
    // Update existing obstacles
    for (u16 i = 0; i < MAX_OBSTACLES; i++) {
        if (obstacles[i].active) {
            // Move obstacle down
            obstacles[i].y += speed;
            
            // Remove if off screen
            if (obstacles[i].y > 240) {
                obstacles[i].active = FALSE;
            }
        }
    }
}

void drawObstacles(void) {
    // Clear all obstacle positions first
    for (u16 i = 0; i < MAX_OBSTACLES; i++) {
        if (obstacles[i].active) {
            VDP_clearTileMapRect(BG_A, (obstacles[i].x - 8) >> 3, (obstacles[i].y - 8) >> 3, 2, 2);
        }
    }
    
    // Draw obstacles at new positions
    for (u16 i = 0; i < MAX_OBSTACLES; i++) {
        if (obstacles[i].active) {
            VDP_setTileMapXY(BG_A, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, obstacles[i].tileIndex), 
                            obstacles[i].x >> 3, obstacles[i].y >> 3);
        }
    }
}

u8 checkCollision(void) {
    // Check collision with obstacles
    for (u16 i = 0; i < MAX_OBSTACLES; i++) {
        if (obstacles[i].active) {
            // Simple box collision (16x16 tiles)
            s16 dx = abs(playerX - obstacles[i].x);
            s16 dy = abs(playerY - obstacles[i].y);
            
            if (dx < 16 && dy < 16) {
                return TRUE; // Collision detected
            }
        }
    }
    return FALSE; // No collision
}

void resetObstacles(void) {
    for (u16 i = 0; i < MAX_OBSTACLES; i++) {
        obstacles[i].active = FALSE;
    }
    obstacleSpawnTimer = 0;
}

void updatePalettes(void) {
    // Animate neon colors with simple pulse
    palettePhase += 2;
    
    // Create simple pulsing neon effect
    u16 pulse = palettePhase & 63;
    if (pulse > 32) pulse = 64 - pulse;
    
    // Modify palette colors for neon effect
    PAL_setColor(14, RGB24_TO_VDPCOLOR(0xff0000 + (pulse << 4)));
    PAL_setColor(13, RGB24_TO_VDPCOLOR(0x00ff00 + (pulse << 8)));
    PAL_setColor(12, RGB24_TO_VDPCOLOR(0x0000ff + pulse));
}

void drawHUD(void) {
    char buffer[32];
    
    // Draw score
    sprintf(buffer, "SCORE: %06lu", score);
    VDP_drawText(buffer, 1, 1);
    
    // Draw speed
    sprintf(buffer, "SPEED: %d", speed);
    VDP_drawText(buffer, 25, 1);
    
    // Draw instructions
    if (gameState == GAME_MENU) {
        VDP_drawText("NEON WAVE RUNNER", 10, 10);
        VDP_drawText("PRESS START TO PLAY", 9, 12);
        VDP_drawText("LEFT/RIGHT - MOVE", 10, 15);
        VDP_drawText("C - TOGGLE DEBUG", 10, 17);
    }
    
    if (gameState == GAME_OVER) {
        VDP_drawText("GAME OVER", 13, 12);
        VDP_drawText("PRESS START TO RETRY", 8, 14);
    }
}

void updateGame(void) {
    u16 joy = JOY_readJoypad(JOY_1);
    
    switch (gameState) {
        case GAME_MENU:
            if (joy & BUTTON_START) {
                gameState = GAME_PLAYING;
                score = 0;
                speed = 2;
                frameCount = 0;
                VDP_clearTextArea(0, 10, 40, 10);
            }
            break;
            
        case GAME_PLAYING:
            updatePlayer();
            updateRoadEffect();
            updateBackground();
            updateObstacles();
            updatePalettes();
            
            // Check collision
            if (checkCollision()) {
                gameState = GAME_OVER;
                resetObstacles();
            }
            
            // Update score and difficulty
            if (frameCount % 60 == 0) {
                score += speed;
                if (score % 100 == 0 && speed < 8) {
                    speed++;
                }
            }
            
            frameCount++;
            break;
            
        case GAME_OVER:
            if (joy & BUTTON_START) {
                gameState = GAME_PLAYING;
                score = 0;
                speed = 2;
                frameCount = 0;
                VDP_clearTextArea(0, 12, 40, 4);
            }
            break;
    }
}

int main(bool hardReset) {
    (void)hardReset;
    
    JOY_init();
    initGame();
    
    while (TRUE) {
        updateGame();
        drawHUD();
        drawObstacles();
        
        SYS_doVBlankProcess();
    }
    
    return 0;
}
