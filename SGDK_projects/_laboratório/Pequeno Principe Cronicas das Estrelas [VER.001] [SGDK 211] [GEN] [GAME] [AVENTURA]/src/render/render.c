#include "project.h"
#include "resources.h"

#include <string.h>

static u32 gTileBank[PP_TOTAL_GENERATED_TILES * 8];

static const char *const gPlanetShortLabels[PLANET_COUNT] =
{
    "B612",
    "REI",
    "VAIDOSO",
    "BEBADO",
    "HOMEM NEG",
    "ACENDEDOR",
    "GEOGRAFO",
    "SERPENTE",
    "DESERTO",
    "JARDIM",
    "POCO",
    "B612"
};

static const u16 gUiPalette[16] =
{
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0),
    RGB3_3_3_TO_VDPCOLOR(7, 7, 7),
    RGB3_3_3_TO_VDPCOLOR(6, 5, 4),
    RGB3_3_3_TO_VDPCOLOR(7, 6, 2),
    RGB3_3_3_TO_VDPCOLOR(4, 3, 5),
    RGB3_3_3_TO_VDPCOLOR(2, 2, 2),
    RGB3_3_3_TO_VDPCOLOR(0, 0, 1),
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0),
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0),
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0),
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0),
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0),
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0),
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0),
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0),
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0)
};

static const u16 gPresentationPal0[16] =
{
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0),
    RGB3_3_3_TO_VDPCOLOR(7, 7, 7),
    RGB3_3_3_TO_VDPCOLOR(6, 6, 7),
    RGB3_3_3_TO_VDPCOLOR(4, 5, 7),
    RGB3_3_3_TO_VDPCOLOR(7, 6, 2),
    RGB3_3_3_TO_VDPCOLOR(7, 4, 1),
    RGB3_3_3_TO_VDPCOLOR(1, 1, 3),
    RGB3_3_3_TO_VDPCOLOR(0, 0, 1),
    0, 0, 0, 0, 0, 0, 0, 0
};

static const u16 gPresentationPal1[16] =
{
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0),
    RGB3_3_3_TO_VDPCOLOR(7, 7, 6),
    RGB3_3_3_TO_VDPCOLOR(6, 5, 4),
    RGB3_3_3_TO_VDPCOLOR(7, 6, 2),
    RGB3_3_3_TO_VDPCOLOR(4, 3, 5),
    RGB3_3_3_TO_VDPCOLOR(2, 2, 2),
    RGB3_3_3_TO_VDPCOLOR(1, 2, 4),
    RGB3_3_3_TO_VDPCOLOR(0, 0, 1),
    0, 0, 0, 0, 0, 0, 0, 0
};

static const u16 gTravelPal0[16] =
{
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0),
    RGB3_3_3_TO_VDPCOLOR(7, 7, 7),
    RGB3_3_3_TO_VDPCOLOR(6, 6, 7),
    RGB3_3_3_TO_VDPCOLOR(5, 4, 6),
    RGB3_3_3_TO_VDPCOLOR(7, 6, 2),
    RGB3_3_3_TO_VDPCOLOR(6, 4, 2),
    RGB3_3_3_TO_VDPCOLOR(2, 2, 5),
    RGB3_3_3_TO_VDPCOLOR(0, 0, 1),
    0, 0, 0, 0, 0, 0, 0, 0
};

static const u16 gTravelPal1[16] =
{
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0),
    RGB3_3_3_TO_VDPCOLOR(7, 7, 6),
    RGB3_3_3_TO_VDPCOLOR(5, 5, 6),
    RGB3_3_3_TO_VDPCOLOR(7, 6, 2),
    RGB3_3_3_TO_VDPCOLOR(6, 4, 1),
    RGB3_3_3_TO_VDPCOLOR(3, 2, 1),
    RGB3_3_3_TO_VDPCOLOR(6, 6, 7),
    RGB3_3_3_TO_VDPCOLOR(0, 0, 1),
    0, 0, 0, 0, 0, 0, 0, 0
};

static const u16 gTitleSky0[6] =
{
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0),
    RGB3_3_3_TO_VDPCOLOR(7, 7, 7),
    RGB3_3_3_TO_VDPCOLOR(6, 6, 7),
    RGB3_3_3_TO_VDPCOLOR(4, 5, 7),
    RGB3_3_3_TO_VDPCOLOR(7, 6, 2),
    RGB3_3_3_TO_VDPCOLOR(7, 4, 1)
};

static const u16 gTitleSky1[6] =
{
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0),
    RGB3_3_3_TO_VDPCOLOR(7, 7, 7),
    RGB3_3_3_TO_VDPCOLOR(7, 6, 7),
    RGB3_3_3_TO_VDPCOLOR(5, 4, 7),
    RGB3_3_3_TO_VDPCOLOR(7, 6, 3),
    RGB3_3_3_TO_VDPCOLOR(7, 5, 2)
};

static const u16 gTitleSky2[6] =
{
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0),
    RGB3_3_3_TO_VDPCOLOR(7, 7, 6),
    RGB3_3_3_TO_VDPCOLOR(6, 5, 7),
    RGB3_3_3_TO_VDPCOLOR(4, 4, 6),
    RGB3_3_3_TO_VDPCOLOR(7, 5, 2),
    RGB3_3_3_TO_VDPCOLOR(6, 3, 1)
};

static const u16 *const gTitleSkyCycle[] = { gTitleSky0, gTitleSky1, gTitleSky2 };

static const u16 gTravelSky0[6] =
{
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0),
    RGB3_3_3_TO_VDPCOLOR(7, 7, 7),
    RGB3_3_3_TO_VDPCOLOR(6, 6, 7),
    RGB3_3_3_TO_VDPCOLOR(5, 4, 6),
    RGB3_3_3_TO_VDPCOLOR(7, 6, 2),
    RGB3_3_3_TO_VDPCOLOR(6, 4, 2)
};

static const u16 gTravelSky1[6] =
{
    RGB3_3_3_TO_VDPCOLOR(0, 0, 0),
    RGB3_3_3_TO_VDPCOLOR(7, 7, 6),
    RGB3_3_3_TO_VDPCOLOR(7, 6, 7),
    RGB3_3_3_TO_VDPCOLOR(6, 4, 6),
    RGB3_3_3_TO_VDPCOLOR(7, 6, 3),
    RGB3_3_3_TO_VDPCOLOR(7, 5, 1)
};

static const u16 *const gTravelSkyCycle[] = { gTravelSky0, gTravelSky1 };

static void Render_setTilePixel(u32 *tile, u16 x, u16 y, u8 color)
{
    u32 shift = (7 - x) << 2;
    u32 mask = 0xFu << shift;

    tile[y] = (tile[y] & (~mask)) | (((u32) color & 0xF) << shift);
}

static void Render_fillTile(u32 *tile, u8 color)
{
    u16 x;
    u16 y;

    for (y = 0; y < 8; y++)
    {
        tile[y] = 0;
        for (x = 0; x < 8; x++)
        {
            Render_setTilePixel(tile, x, y, color);
        }
    }
}

static void Render_buildTiles(void)
{
    u32 *tile;
    u16 x;
    u16 y;

    memset(gTileBank, 0, sizeof(gTileBank));

    tile = &gTileBank[(PP_TILE_PAPER - PP_TILE_BASE) * 8];
    Render_fillTile(tile, 1);

    tile = &gTileBank[(PP_TILE_DITHER - PP_TILE_BASE) * 8];
    for (y = 0; y < 8; y++)
    {
        for (x = 0; x < 8; x++)
        {
            Render_setTilePixel(tile, x, y, ((x + y) & 1) ? 2 : 1);
        }
    }

    tile = &gTileBank[(PP_TILE_HATCH - PP_TILE_BASE) * 8];
    for (y = 0; y < 8; y++)
    {
        for (x = 0; x < 8; x++)
        {
            Render_setTilePixel(tile, x, y, ((x == y) || ((x + y) == 7)) ? 3 : 1);
        }
    }

    tile = &gTileBank[(PP_TILE_STAR - PP_TILE_BASE) * 8];
    Render_setTilePixel(tile, 1, 2, 4);
    Render_setTilePixel(tile, 5, 1, 4);
    Render_setTilePixel(tile, 6, 6, 4);
    Render_setTilePixel(tile, 3, 4, 2);

    tile = &gTileBank[(PP_TILE_GROUND - PP_TILE_BASE) * 8];
    for (y = 0; y < 8; y++)
    {
        for (x = 0; x < 8; x++)
        {
            if ((y == 0) || (x == 0) || (x == 7))
            {
                Render_setTilePixel(tile, x, y, 5);
            }
            else
            {
                Render_setTilePixel(tile, x, y, ((x + (y << 1)) & 1) ? 2 : 1);
            }
        }
    }

    tile = &gTileBank[(PP_TILE_GROUND_ALT - PP_TILE_BASE) * 8];
    for (y = 0; y < 8; y++)
    {
        for (x = 0; x < 8; x++)
        {
            if ((y == 0) || (x == 0) || (x == 7))
            {
                Render_setTilePixel(tile, x, y, 5);
            }
            else
            {
                Render_setTilePixel(tile, x, y, ((x + y) & 1) ? 3 : 1);
            }
        }
    }

    tile = &gTileBank[(PP_TILE_CROWN - PP_TILE_BASE) * 8];
    for (x = 1; x < 7; x++)
    {
        Render_setTilePixel(tile, x, 5, 4);
    }
    Render_setTilePixel(tile, 1, 4, 4);
    Render_setTilePixel(tile, 3, 2, 4);
    Render_setTilePixel(tile, 5, 4, 4);
    Render_setTilePixel(tile, 3, 6, 5);

    tile = &gTileBank[(PP_TILE_TOWER - PP_TILE_BASE) * 8];
    for (y = 0; y < 8; y++)
    {
        for (x = 0; x < 8; x++)
        {
            Render_setTilePixel(tile, x, y, (x == 0 || x == 7) ? 6 : 1);
        }
    }

    tile = &gTileBank[(PP_TILE_TOWER_WINDOW - PP_TILE_BASE) * 8];
    for (y = 0; y < 8; y++)
    {
        for (x = 0; x < 8; x++)
        {
            if ((x == 0) || (x == 7))
            {
                Render_setTilePixel(tile, x, y, 6);
            }
            else if ((x > 2) && (x < 5) && (y > 1) && (y < 6))
            {
                Render_setTilePixel(tile, x, y, 4);
            }
            else
            {
                Render_setTilePixel(tile, x, y, 1);
            }
        }
    }

    tile = &gTileBank[(PP_TILE_LAMP - PP_TILE_BASE) * 8];
    for (y = 1; y < 8; y++)
    {
        Render_setTilePixel(tile, 3, y, 5);
    }
    Render_setTilePixel(tile, 2, 1, 4);
    Render_setTilePixel(tile, 3, 1, 4);
    Render_setTilePixel(tile, 4, 1, 4);
    Render_setTilePixel(tile, 2, 2, 3);
    Render_setTilePixel(tile, 3, 2, 3);
    Render_setTilePixel(tile, 4, 2, 3);

    tile = &gTileBank[(PP_TILE_BEACON - PP_TILE_BASE) * 8];
    for (y = 2; y < 8; y++)
    {
        Render_setTilePixel(tile, 4, y, 5);
    }
    for (x = 2; x < 7; x++)
    {
        Render_setTilePixel(tile, x, 1, 4);
    }

    tile = &gTileBank[(PP_TILE_DUNE - PP_TILE_BASE) * 8];
    for (y = 0; y < 8; y++)
    {
        for (x = 0; x < 8; x++)
        {
            Render_setTilePixel(tile, x, y, (y < 2) ? 4 : (((x + y) & 1) ? 2 : 1));
        }
    }

    tile = &gTileBank[(PP_TILE_RING - PP_TILE_BASE) * 8];
    for (x = 1; x < 7; x++)
    {
        Render_setTilePixel(tile, x, 2, 4);
        Render_setTilePixel(tile, x, 5, 4);
    }
    Render_setTilePixel(tile, 1, 3, 4);
    Render_setTilePixel(tile, 6, 3, 4);
    Render_setTilePixel(tile, 1, 4, 4);
    Render_setTilePixel(tile, 6, 4, 4);

    tile = &gTileBank[(PP_TILE_FILL - PP_TILE_BASE) * 8];
    Render_fillTile(tile, 2);

    tile = &gTileBank[(PP_TILE_SUN - PP_TILE_BASE) * 8];
    for (y = 1; y < 7; y++)
    {
        for (x = 1; x < 7; x++)
        {
            Render_setTilePixel(tile, x, y, ((x == 1) || (x == 6) || (y == 1) || (y == 6)) ? 5 : 4);
        }
    }

    tile = &gTileBank[(PP_TILE_TRACE - PP_TILE_BASE) * 8];
    for (x = 1; x < 7; x += 2)
    {
        Render_setTilePixel(tile, x, 5, 4);
        Render_setTilePixel(tile, x + 1, 4, 4);
    }

    tile = &gTileBank[(PP_TILE_PLAYER - PP_TILE_BASE) * 8];
    Render_fillTile(tile + (0 * 8), 0);
    Render_fillTile(tile + (1 * 8), 0);
    Render_fillTile(tile + (2 * 8), 0);
    Render_fillTile(tile + (3 * 8), 0);
    Render_fillTile(tile + (4 * 8), 0);
    Render_fillTile(tile + (5 * 8), 0);

    for (y = 1; y < 7; y++)
    {
        for (x = 2; x < 6; x++)
        {
            Render_setTilePixel(tile + (0 * 8), x, y, 1);
        }
    }
    Render_setTilePixel(tile + (0 * 8), 3, 1, 3);
    Render_setTilePixel(tile + (0 * 8), 4, 1, 3);
    Render_setTilePixel(tile + (1 * 8), 1, 2, 3);
    Render_setTilePixel(tile + (1 * 8), 2, 2, 3);
    Render_setTilePixel(tile + (1 * 8), 3, 2, 1);
    Render_setTilePixel(tile + (1 * 8), 4, 2, 1);
    Render_setTilePixel(tile + (1 * 8), 2, 4, 2);
    Render_setTilePixel(tile + (1 * 8), 3, 4, 2);
    Render_setTilePixel(tile + (1 * 8), 4, 4, 2);
    Render_setTilePixel(tile + (1 * 8), 5, 4, 2);
    for (y = 0; y < 8; y++)
    {
        Render_setTilePixel(tile + (2 * 8), 2, y, 2);
        Render_setTilePixel(tile + (2 * 8), 5, y, 2);
        Render_setTilePixel(tile + (3 * 8), 1, y, 2);
        Render_setTilePixel(tile + (3 * 8), 4, y, 2);
    }
    for (x = 2; x < 6; x++)
    {
        Render_setTilePixel(tile + (4 * 8), x, 1, 4);
        Render_setTilePixel(tile + (4 * 8), x, 2, 4);
    }
    for (y = 0; y < 8; y++)
    {
        Render_setTilePixel(tile + (4 * 8), 3, y, 5);
        Render_setTilePixel(tile + (5 * 8), 4, y, 5);
    }

    tile = &gTileBank[(PP_TILE_SCARF - PP_TILE_BASE) * 8];
    for (x = 1; x < 7; x++)
    {
        Render_setTilePixel(tile, x, 2 + ((x + 1) & 1), 4);
        Render_setTilePixel(tile, x, 3 + ((x + 1) & 1), 4);
    }
    Render_setTilePixel(tile, 6, 2, 3);
    Render_setTilePixel(tile, 6, 5, 3);

    tile = &gTileBank[(PP_TILE_HALO - PP_TILE_BASE) * 8];
    memset(tile, 0, sizeof(u32) * 4 * 8);
    for (y = 0; y < 8; y++)
    {
        for (x = 0; x < 8; x++)
        {
            s16 distTopRight = ((x - 7) * (x - 7)) + ((y - 7) * (y - 7));
            s16 distTopLeft = (x * x) + ((y - 7) * (y - 7));
            s16 distBottomRight = ((x - 7) * (x - 7)) + (y * y);
            s16 distBottomLeft = (x * x) + (y * y);

            if ((distTopRight > 12) && (distTopRight < 42))
            {
                Render_setTilePixel(tile + (0 * 8), x, y, 15);
            }
            if ((distTopLeft > 12) && (distTopLeft < 42))
            {
                Render_setTilePixel(tile + (1 * 8), x, y, 15);
            }
            if ((distBottomRight > 12) && (distBottomRight < 42))
            {
                Render_setTilePixel(tile + (2 * 8), x, y, 15);
            }
            if ((distBottomLeft > 12) && (distBottomLeft < 42))
            {
                Render_setTilePixel(tile + (3 * 8), x, y, 15);
            }
        }
    }
}

static void Render_u16ToStr(u16 value, char *out)
{
    char buffer[6];
    u16 count = 0;
    u16 i;

    if (value == 0)
    {
        out[0] = '0';
        out[1] = 0;
        return;
    }

    while ((value > 0) && (count < 5))
    {
        buffer[count++] = (char) ('0' + (value % 10));
        value /= 10;
    }

    for (i = 0; i < count; i++)
    {
        out[i] = buffer[count - i - 1];
    }

    out[count] = 0;
}

static void Render_drawPanel(s16 x, s16 y, s16 width, s16 height, u16 palette)
{
    if ((width < 3) || (height < 3))
    {
        return;
    }

    VDP_fillTileMapRect(BG_A, TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, PP_TILE_PAPER), x, y, width, height);
    VDP_fillTileMapRect(BG_A, TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, PP_TILE_HATCH), x, y, width, 1);
    VDP_fillTileMapRect(BG_A, TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, PP_TILE_HATCH), x, y + height - 1, width, 1);
    VDP_fillTileMapRect(BG_A, TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, PP_TILE_DITHER), x, y + 1, 1, height - 2);
    VDP_fillTileMapRect(BG_A, TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, PP_TILE_DITHER), x + width - 1, y + 1, 1, height - 2);
    VDP_fillTileMapRect(BG_A, TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, PP_TILE_FILL), x + 1, y + 1, width - 2, 2);
}

static void Render_applyBackdropDrift(GameContext *game, s16 startLine, s16 speedShift, s16 waveShift)
{
    s16 line;

    Render_clearScroll(game);

    for (line = startLine; line < PP_SCREEN_LINES; line++)
    {
        s16 wave = sinFix16((line << 2) + (game->frameCounter << waveShift)) >> 6;
        game->hscrollB[line] = -((game->frameCounter >> speedShift) + (line >> 5) + wave);
    }
}

static const s16 gOrbitXPos[PLANET_COUNT] =
{
    2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35
};

static const char *const gOrbitLabels[PLANET_COUNT] =
{
    "B", "R", "V", "O", "H", "A", "G", "S", "D", "J", "P", "C"
};

static void Render_drawOrbitMap(const GameContext *game, PlanetId active, bool revealAll, s16 y)
{
    u16 i;
    u16 x;

    for (i = 0; i < PLANET_COUNT; i++)
    {
        bool visible = revealAll || (game != NULL && game->codexUnlocked[i]) || ((PlanetId) i == active);
        u16 tile = visible ? (((PlanetId) i == active) ? PP_TILE_SUN : PP_TILE_RING) : PP_TILE_STAR;

        VDP_setTileMapXY(BG_B, TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, tile), gOrbitXPos[i], y);

        if (i + 1 < PLANET_COUNT)
        {
            for (x = gOrbitXPos[i] + 1; x < gOrbitXPos[i + 1]; x++)
            {
                VDP_setTileMapXY(BG_B, TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, PP_TILE_TRACE), x, y);
            }
        }
    }

    for (i = 0; i < PLANET_COUNT; i++)
    {
        VDP_drawText(gOrbitLabels[i], gOrbitXPos[i], y + 1);
    }
}

static void Render_drawBudgetLine(const FxProfile *fx, s16 x, s16 y)
{
    char vramText[6];
    char dmaText[6];

    Render_u16ToStr(fx->vramBudgetTiles, vramText);
    Render_u16ToStr(fx->dmaBudgetBytes, dmaText);

    VDP_drawText("VRAM", x, y);
    VDP_drawText(vramText, x + 5, y);
    VDP_drawText("tiles", x + 9, y);
    VDP_drawText("DMA", x + 16, y);
    VDP_drawText(dmaText, x + 20, y);
    VDP_drawText("B", x + 26, y);
}

static void Render_drawFxFlags(const FxProfile *fx, s16 x, s16 y)
{
    if (fx->flags & PP_SCROLL_LINE)
    {
        VDP_drawText("LINE_SCROLL", x, y);
    }
    if (fx->flags & PP_SCROLL_COLUMN)
    {
        VDP_drawText("COLUMN", x + 15, y);
    }
    if (fx->flags & PP_HINT_SPLIT)
    {
        VDP_drawText("H-INT", x, y + 1);
    }
    if (fx->flags & PP_HILIGHT_MODE)
    {
        VDP_drawText("HILIGHT", x + 15, y + 1);
    }
    if (fx->flags & PP_INTERLEAVED_PLANES)
    {
        VDP_drawText("INTERLEAVED", x, y + 2);
    }
}

static void Render_drawPresentationBase(const u16 *pal0, const u16 *pal1)
{
    PAL_setPalette(PAL0, pal0, DMA_QUEUE);
    PAL_setPalette(PAL1, pal1, DMA_QUEUE);
    Render_drawSky(PP_TILE_PAPER, true, PAL0);
}

void Render_init(void)
{
    Render_buildTiles();
    VDP_loadTileData(gTileBank, PP_TILE_BASE, PP_TOTAL_GENERATED_TILES, DMA);
    VDP_loadTileSet(&ts_rose_mark, PP_TILE_ROSE_MARK, DMA);
    VDP_loadTileSet(&ts_throne_mark, PP_TILE_THRONE_MARK, DMA);
    VDP_loadTileSet(&ts_lamp_mark, PP_TILE_LAMP_MARK, DMA);
    VDP_loadTileSet(&ts_desert_mark, PP_TILE_DESERT_MARK, DMA);
    PAL_setPalette(PAL2, gUiPalette, DMA);
    PAL_setPalette(PAL3, pal_sprite_stage.data, DMA);
    Render_clearPlayfield();
}

void Render_clearScroll(GameContext *game)
{
    memset(game->hscrollA, 0, sizeof(game->hscrollA));
    memset(game->hscrollB, 0, sizeof(game->hscrollB));
    memset(game->vscrollA, 0, sizeof(game->vscrollA));
    memset(game->vscrollB, 0, sizeof(game->vscrollB));
}

void Render_applyScroll(const GameContext *game)
{
    VDP_setHorizontalScrollLine(BG_A, 0, (s16 *) game->hscrollA, PP_SCREEN_LINES, DMA_QUEUE);
    VDP_setHorizontalScrollLine(BG_B, 0, (s16 *) game->hscrollB, PP_SCREEN_LINES, DMA_QUEUE);
    VDP_setVerticalScrollTile(BG_A, 0, (s16 *) game->vscrollA, PP_VSCROLL_COLUMNS, DMA_QUEUE);
    VDP_setVerticalScrollTile(BG_B, 0, (s16 *) game->vscrollB, PP_VSCROLL_COLUMNS, DMA_QUEUE);
}

void Render_clearPlayfield(void)
{
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
}

void Render_beginScene(const u16 *pal0, const u16 *pal1)
{
    PAL_setPalette(PAL0, pal0, DMA_QUEUE);
    PAL_setPalette(PAL1, pal1, DMA_QUEUE);
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
}

void Render_drawSky(u16 baseTile, bool stars, u16 palette)
{
    s16 x;
    s16 y;

    VDP_fillTileMapRect(BG_B, TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, baseTile), 0, 0, PP_SCREEN_TILES_W, PP_SCREEN_TILES_H);

    if (!stars)
    {
        return;
    }

    for (y = 1; y < 14; y += 2)
    {
        for (x = (y & 2) ? 1 : 3; x < 39; x += 6)
        {
            VDP_setTileMapXY(BG_B, TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, (x & 4) ? PP_TILE_STAR : PP_TILE_TRACE), x, y);
        }
    }
}

void Render_drawDisc(VDPPlane plane, s16 cx, s16 cy, s16 radius, u16 fillTile, u16 outlineTile, u16 palette)
{
    s16 y;

    for (y = -radius; y <= radius; y++)
    {
        s16 yy = cy + y;
        s16 half = 0;
        s16 limit = (radius * radius) - (y * y);
        s16 xStart;
        s16 xEnd;

        while (((half + 1) * (half + 1)) <= limit)
        {
            half++;
        }

        if ((yy < 0) || (yy >= PP_SCREEN_TILES_H))
        {
            continue;
        }

        xStart = cx - half;
        xEnd = cx + half;

        if ((xEnd < 0) || (xStart >= PP_SCREEN_TILES_W))
        {
            continue;
        }

        if (xStart < 0) xStart = 0;
        if (xEnd >= PP_SCREEN_TILES_W) xEnd = PP_SCREEN_TILES_W - 1;

        VDP_setTileMapXY(plane, TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, outlineTile), xStart, yy);
        VDP_setTileMapXY(plane, TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, outlineTile), xEnd, yy);

        if (xEnd > xStart + 1)
        {
            VDP_fillTileMapRect(plane, TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, fillTile), xStart + 1, yy, xEnd - xStart - 1, 1);
        }
    }
}

void Render_drawTower(s16 x, s16 baseY, s16 height, u16 palette)
{
    s16 row;

    for (row = 0; row < height; row++)
    {
        u16 tile = (row & 1) ? PP_TILE_TOWER_WINDOW : PP_TILE_TOWER;
        VDP_setTileMapXY(BG_A, TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, tile), x, baseY - row);
        VDP_setTileMapXY(BG_A, TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, tile), x + 1, baseY - row);
        VDP_setTileMapXY(BG_A, TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, tile), x + 2, baseY - row);
    }
}

void Render_drawLamppost(s16 x, s16 y, bool lit, u16 palette)
{
    VDP_setTileMapXY(BG_A, TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, lit ? PP_TILE_SUN : PP_TILE_LAMP), x, y);
    VDP_setTileMapXY(BG_A, TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, PP_TILE_LAMP), x, y + 1);
}

void Render_drawBeacon(s16 x, s16 y, u16 palette)
{
    VDP_setTileMapXY(BG_A, TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, PP_TILE_BEACON), x, y);
}

void Render_drawDunes(s16 startY, u16 palette)
{
    s16 y;

    for (y = startY; y < PP_SCREEN_TILES_H; y++)
    {
        VDP_fillTileMapRect(BG_A, TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, (y & 1) ? PP_TILE_DUNE : PP_TILE_GROUND_ALT), 0, y, PP_SCREEN_TILES_W, 1);
    }
}

void Render_drawPlanetHud(const GameContext *game)
{
    const PlanetScene *scene = game->activeScene;
    const char *goalLine;

    if (scene == NULL)
    {
        return;
    }

    goalLine = game->planetSolved[scene->id] ? scene->goalDone : scene->goalPending;

    VDP_clearTextArea(0, 0, PP_SCREEN_TILES_W, 6);
    VDP_drawText(scene->name, 1, 0);
    VDP_drawText(scene->subtitle, 1, 1);
    VDP_drawText(goalLine, 1, 2);
    VDP_drawText(scene->effectLine1, 1, 3);
    VDP_drawText(scene->effectLine2, 1, 4);
    VDP_drawText(game->planetSolved[scene->id] ? scene->travelHint : "START pausa. A interage. Segure A para planar.", 1, 5);
}

void Render_drawTextScreen(u16 palette, const char *title, const char *const *lines, u16 lineCount, u16 startRow)
{
    u16 i;

    PAL_setPalette(PAL0, gUiPalette, DMA_QUEUE);
    PAL_setPalette(PAL1, gUiPalette, DMA_QUEUE);
    VDP_fillTileMapRect(BG_B, TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, PP_TILE_PAPER), 0, 0, PP_SCREEN_TILES_W, PP_SCREEN_TILES_H);
    VDP_fillTileMapRect(BG_A, TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, PP_TILE_DITHER), 0, 0, PP_SCREEN_TILES_W, PP_SCREEN_TILES_H);
    VDP_drawText(title, 9, startRow - 2);

    for (i = 0; i < lineCount; i++)
    {
        VDP_drawText(lines[i], 2, startRow + i);
    }
}

void Render_drawPauseScreen(GameContext *game)
{
    static const char *const labels[] =
    {
        "RETOMAR",
        "CODEX TECNICO",
        "VOLTAR AO TITULO"
    };
    const PlanetScene *scene = game->activeScene;
    u16 i;

    if (game->redrawScene)
    {
        Render_clearPlayfield();
        Render_drawPresentationBase(gPresentationPal0, gPresentationPal1);
        Render_drawPanel(4, 6, 32, 15, PAL1);
        Render_drawOrbitMap(game, game->currentPlanet, true, 3);
        VDP_drawText("Pausa", 18, 7);
        VDP_drawText((game->previousState == GAME_STATE_TRAVEL) ? "Em rota entre mundos" : (scene != NULL ? scene->name : "Intervalo"), 8, 9);

        for (i = 0; i < 3; i++)
        {
            VDP_drawText((i == game->pauseSelection) ? "*" : "-", 7, 12 + (i * 2));
            VDP_drawText(labels[i], 10, 12 + (i * 2));
        }

        VDP_drawText("B volta ao jogo.", 8, 19);
        VDP_drawText("START confirma a opcao.", 8, 20);
    }

    Render_applyBackdropDrift(game, 24, 2, 3);
    PAL_setColors(0, gTitleSkyCycle[(game->frameCounter >> 4) % 3], 6, DMA_QUEUE);
}

void Render_drawCodexScreen(GameContext *game)
{
    const PlanetScene *scene = Planet_getScene((PlanetId) game->codexIndex);

    if (scene == NULL)
    {
        return;
    }

    if (game->redrawScene)
    {
        Render_clearPlayfield();
        Render_drawPresentationBase(gPresentationPal0, gPresentationPal1);
        Render_drawPanel(2, 5, 36, 19, PAL1);
        Render_drawOrbitMap(game, scene->id, true, 2);
        VDP_drawText("Codex Tecnico", 13, 6);
        VDP_drawText(scene->name, 4, 8);
        VDP_drawText(scene->subtitle, 4, 9);
        VDP_drawText(scene->effectLine1, 4, 11);
        VDP_drawText(scene->effectLine2, 4, 12);
        {
            u16 row = 14;
            u16 idx;
            for (idx = 1; idx < scene->codexLineCount && idx < 5; idx++)
            {
                VDP_drawText(scene->codexLines[idx], 4, row);
                row++;
            }
        }
        VDP_drawText("FLAGS", 4, 19);
        Render_drawFxFlags(&scene->fx, 4, 20);
        Render_drawBudgetLine(&scene->fx, 4, 23);
        VDP_drawText("LEFT/RIGHT troca. B volta.", 7, 25);
    }

    Render_applyBackdropDrift(game, 18, 2, 3);
    PAL_setColors(0, gTitleSkyCycle[(game->frameCounter >> 5) % 3], 6, DMA_QUEUE);
}

void Render_drawCreditsScreen(GameContext *game)
{
    static const char *const lines[] =
    {
        "Capitulo 1 concluido em hardware consciente.",
        "Cada planeta abriu uma familia de tecnica",
        "sem romper o ritmo do jogo nem do estudo.",
        "",
        "Slice base: line scroll, column scroll,",
        "H-Int, hilight, paleta viva e travel.",
        "",
        "START retorna ao titulo e reinicia a rota."
    };
    u16 i;

    if (game->redrawScene)
    {
        Render_clearPlayfield();
        Render_drawPresentationBase(gPresentationPal0, gPresentationPal1);
        Render_drawDisc(BG_B, 31, 18, 6, PP_TILE_GROUND_ALT, PP_TILE_HATCH, PAL1);
        Render_drawPanel(3, 5, 30, 18, PAL1);
        Render_drawOrbitMap(game, PLANET_COUNT, true, 3);
        VDP_drawText("Fim do Capitulo 1", 11, 6);

        for (i = 0; i < 8; i++)
        {
            VDP_drawText(lines[i], 5, 9 + i);
        }
    }

    Render_applyBackdropDrift(game, 16, 2, 4);
    PAL_setColors(0, gTitleSkyCycle[(game->frameCounter >> 4) % 3], 6, DMA_QUEUE);
}

void Render_drawTitleScene(GameContext *game)
{
    static const char *const lines[] =
    {
        "Slice pedagogico e autoral para SGDK 211.",
        "4 micro-planetas apresentam scroll, H-Int,",
        "hilight, paleta viva e travel entre mundos.",
        "",
        "A ou START inicia a travessia."
    };
    u16 i;

    if (game->redrawScene)
    {
        Render_clearPlayfield();
        Render_drawPresentationBase(gPresentationPal0, gPresentationPal1);
        Render_drawDisc(BG_B, 9, 19, 5, PP_TILE_GROUND, PP_TILE_HATCH, PAL1);
        Render_drawDisc(BG_B, 31, 11, 4, PP_TILE_GROUND_ALT, PP_TILE_HATCH, PAL1);
        Render_drawPanel(5, 6, 30, 14, PAL1);
        Render_drawOrbitMap(game, PLANET_B612, true, 22);
        VDP_drawText("Pequeno Principe", 12, 7);
        VDP_drawText("Cronicas das Estrelas", 9, 8);

        for (i = 0; i < 5; i++)
        {
            VDP_drawText(lines[i], 7, 11 + i);
        }
    }

    Render_applyBackdropDrift(game, 20, 2, 4);
    PAL_setColors(0, gTitleSkyCycle[(game->frameCounter >> 4) % 3], 6, DMA_QUEUE);
}

void Render_drawStoryScene(GameContext *game, const char *title, const char *const *lines, u16 lineCount)
{
    u16 i;

    if (game->redrawScene)
    {
        Render_clearPlayfield();
        Render_drawPresentationBase(gPresentationPal0, gPresentationPal1);
        Render_drawPanel(3, 5, 34, 18, PAL1);
        VDP_drawText(title, 10, 6);

        if (game->storyPage == 0)
        {
            Render_drawDisc(BG_B, 31, 18, 5, PP_TILE_GROUND, PP_TILE_HATCH, PAL1);
            Render_drawBeacon(31, 13, PAL1);
            VDP_setTileMapXY(BG_B, TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, PP_TILE_SUN), 28, 8);
        }
        else
        {
            Render_drawOrbitMap(game, PLANET_B612, true, 8);
            VDP_drawText("Capitulo 1", 15, 10);
        }

        for (i = 0; i < lineCount; i++)
        {
            VDP_drawText(lines[i], 5, 12 + i);
        }
    }

    Render_applyBackdropDrift(game, 18, 2, 3);
    PAL_setColors(0, gTitleSkyCycle[(game->frameCounter >> 5) % 3], 6, DMA_QUEUE);
}

void Render_drawTravelScene(GameContext *game)
{
    const PlanetScene *currentScene = Planet_getScene(game->currentPlanet);
    const char *fromLabel = (game->currentPlanet < PLANET_COUNT) ? gPlanetShortLabels[game->currentPlanet] : "ORIGEM";
    const char *toLabel = (game->nextPlanet < PLANET_COUNT) ? gPlanetShortLabels[game->nextPlanet] : "FIM";
    s16 line;

    if (game->redrawScene)
    {
        Render_clearPlayfield();
        PAL_setPalette(PAL0, gTravelPal0, DMA_QUEUE);
        PAL_setPalette(PAL1, gTravelPal1, DMA_QUEUE);
        Render_drawSky(PP_TILE_PAPER, true, PAL0);
        Render_drawOrbitMap(game, (game->nextPlanet < PLANET_COUNT) ? game->nextPlanet : PLANET_DESERTO, true, 4);
        Render_drawPanel(6, 6, 28, 8, PAL1);
        Render_drawDisc(BG_A, 11, 18, game->travelPrevRadius, PP_TILE_GROUND, PP_TILE_HATCH, PAL1);

        if (game->nextPlanet != PLANET_COUNT)
        {
            Render_drawDisc(BG_A, 29, 18, game->travelNextRadius, PP_TILE_GROUND_ALT, PP_TILE_HATCH, PAL1);
        }
        else
        {
            Render_drawDisc(BG_A, 29, 18, game->travelNextRadius, PP_TILE_SUN, PP_TILE_RING, PAL1);
        }

        VDP_drawText("Rota entre estrelas", 11, 7);
        VDP_drawText("Scroll de linhas e escala predefinida", 7, 9);
        VDP_drawText("DE", 8, 21);
        VDP_drawText(fromLabel, 11, 21);
        VDP_drawText("PARA", 23, 21);
        VDP_drawText(toLabel, 28, 21);

        if (currentScene != NULL)
        {
            VDP_drawText(currentScene->travelHint, 3, 23);
        }
        else
        {
            VDP_drawText("A ou C acelera a travessia.", 7, 23);
        }
    }

    Render_clearScroll(game);
    PAL_setColors(0, gTravelSkyCycle[(game->frameCounter >> 4) & 1], 6, DMA_QUEUE);

    for (line = 24; line < PP_SCREEN_LINES; line++)
    {
        s16 drift = (sinFix16((line << 2) + (game->frameCounter << 3)) + 64) >> 5;
        game->hscrollB[line] = -((game->frameCounter >> 1) + ((line - 24) >> 2));

        if ((line > 72) && (line < 168))
        {
            game->hscrollA[line] = drift;
        }
    }
}
