#include <genesis.h>
#include "characters.h"
#include "game.h"

#define FONT_WIDTH        8
#define FONT_HEIGHT       4
#define CHARS_ACTIVE_OFFSET     47

void Characters_init() {
    VDP_loadTileSet(&characters, TILE_FONT_INDEX, DMA);
}

void Characters_prepareToPrint() {
    PAL_setPalette(CHARACTER_PALLETE, slasher.palette->data, DMA);
}

void Characters_print(const char* str, u16 x, u16 y, FontState state) {
    u16 i = 0;

    while (str[i] != '\0') {
        char c = str[i];
        u16 tileIndex = 0;

        // Letras A-Z
        if (c >= 'A' && c <= 'Z') {
            tileIndex = (c - 'A');   // índice dentro do alfabeto
        }
        // Dígitos 0-9
        else if (c >= '0' && c <= '9') {
            tileIndex = 28 + (c - '0');  // supondo que 0-9 vêm logo após A-Z
        }
        else if (c == '!') {
            tileIndex = state == FONT_ACTIVE ? 45 : 89;
        }
        else {
            // caractere não suportado → pula
            i++;
            x++;
            continue;
        }

        if (state == FONT_INACTIVE && c != '!')
            tileIndex += CHARS_ACTIVE_OFFSET;

        // Desenha o tile na tela
        VDP_setTileMapXY(BG_B,
            TILE_ATTR_FULL(CHARACTER_PALLETE, TRUE, FALSE, FALSE, TILE_FONT_INDEX + tileIndex),
            x + i, y);

        i++;
    }

}

void Characters_clearXY(u16 x, u16 y, u16 width) {
    u16 i;
    for (i = 0; i < width; i++) {
        VDP_setTileMapXY(BG_B,
            TILE_ATTR_FULL(CHARACTER_PALLETE, FALSE, FALSE, FALSE, 0),
            x + i, y);
    }
}