#include <genesis.h>

#include "../res/resources.h"

#define SPEED 2
#define GRAVITY 1
#define JUMP_FORCE -8
#define GROUND_Y 200
#define SPRITE_WIDTH 32
#define SPRITE_HEIGHT 32

int main(u16 resetType) {
    // Soft resets don't clear RAM, this can bring some bugs so we hard reset every time we detect a soft reset
    if (!resetType)
        SYS_hardReset();

    // Initialize joypad and sprite engine
    JOY_init();
    SPR_init();

    // Load player sprite resources
    PAL_setPalette(PAL0, player_sprite.palette->data, DMA);
    VDP_loadTileSet(player_sprite.animations[0]->frames[0]->tileset, 1, DMA);

    // Create player sprite
    Sprite* playerSpr = SPR_addSprite(&player_sprite, 100, 100, TILE_ATTR(PAL0, 0, FALSE, FALSE));

    // Player variables
    s16 x = 100;
    s16 y = 100;
    s16 vx = 0;
    s16 vy = 0;
    bool onGround = FALSE;

    // Infinite loop
    while (TRUE) {
        // Read input
        u16 joy = JOY_readJoypad(JOY_1);

        // Handle horizontal movement
        vx = 0;
        if (joy & BUTTON_LEFT) vx = -SPEED;
        if (joy & BUTTON_RIGHT) vx = SPEED;

        // Handle jump
        if ((joy & BUTTON_A) && onGround) {
            vy = JUMP_FORCE;
            onGround = FALSE;
        }

        // Update position
        x += vx;
        y += vy;

        // Apply gravity
        vy += GRAVITY;

        // Basic collision with ground
        if (y >= GROUND_Y) {
            y = GROUND_Y;
            vy = 0;
            onGround = TRUE;
        } else {
            onGround = FALSE;
        }

        // Basic collision with screen edges
        if (x < 0) x = 0;
        if (x > 320 - SPRITE_WIDTH) x = 320 - SPRITE_WIDTH;

        // Update sprite position
        SPR_setPosition(playerSpr, x, y);

        // Update sprites and VBlank
        SPR_update();
        SYS_doVBlankProcess();
    }

    return 0;
}