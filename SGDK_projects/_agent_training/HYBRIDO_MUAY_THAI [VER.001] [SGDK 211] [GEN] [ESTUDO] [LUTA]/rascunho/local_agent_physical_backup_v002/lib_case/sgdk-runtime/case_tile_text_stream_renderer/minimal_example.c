#include <genesis.h>

typedef struct
{
    u16 baseTile;
    u16 maxTile;
    u16 cursor;
    u16 preshift;
} TileTextRenderer;

static TileTextRenderer renderer = { TILE_USER_INDEX, TILE_USER_INDEX + 15, TILE_USER_INDEX, 0 };

void emitChar(TileTextRenderer* r, u16 chr);

int main(void)
{
    const char* text = "WELCOME\\xFF\\x04";

    while (*text)
        emitChar(&renderer, (u8)*text++);

    while (TRUE)
        SYS_doVBlankProcess();

    return 0;
}
