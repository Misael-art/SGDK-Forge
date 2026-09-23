#include "system/telemetry.h"
#include "core/app.h"

static TelemetryData sTelemetry;

void TELEMETRY_init(void)
{
    sTelemetry.cpuLoad = 0;
    sTelemetry.fps = 60;
    sTelemetry.activeSprites = 0;
    sTelemetry.activeObjects = 0;
    sTelemetry.dmaBytesQueued = 0;
    sTelemetry.showDetailedOverlay = TRUE;
}

void TELEMETRY_toggleOverlay(void)
{
    sTelemetry.showDetailedOverlay = !sTelemetry.showDetailedOverlay;
    if (!sTelemetry.showDetailedOverlay) {
        VDP_clearTextArea(0, 0, 40, 2);
    }
}

void TELEMETRY_update(void)
{
    sTelemetry.cpuLoad = SYS_getCPULoad();
    sTelemetry.fps = (gApp.region == APP_REGION_PAL) ? 50 : 60;
}

void TELEMETRY_drawHud(GothamPlayer* player, GothamBoss* boss, u16 activeProjectiles, u16 activeEnemies)
{
    char buf[42];
    u16 totalSprites;

    // Count HW Sprites: 1 (Player) + 5 (Boss) + Enemies + Projectiles/Particles
    totalSprites = 1 + (boss->active ? 5 : 0) + activeEnemies + activeProjectiles;
    sTelemetry.activeSprites = totalSprites;
    sTelemetry.activeObjects = 1 + (boss->active ? 1 : 0) + activeEnemies + activeProjectiles;

    if (sTelemetry.showDetailedOverlay) {
        // Top diagnostic bar (Row 0 & 1)
        sprintf(buf, "GOTHAM OVERDRIVE [60FPS]  CPU:%02d%%", sTelemetry.cpuLoad);
        VDP_drawTextFill(buf, 1, 0, 38);

        sprintf(buf, "SPR:%02d/80  OBJ:%02d  RASTER:224  DMA:OK", sTelemetry.activeSprites, sTelemetry.activeObjects);
        VDP_drawTextFill(buf, 1, 1, 38);
    }

    // Status bar at bottom (Row 26 & 27)
    {
        s16 php = (player != NULL) ? player->health : 0;
        s16 peng = (player != NULL) ? player->energy : 0;
        s16 bhp = (boss != NULL && boss->active) ? (boss->health * 10 / boss->maxHealth) : 0;

        char barP[6];
        char barE[6];
        char barB[11];
        u8 i;

        for (i = 0; i < 5; i++) {
            barP[i] = (i < (php / 20)) ? '=' : '.';
            barE[i] = (i < (peng / 20)) ? '=' : '.';
        }
        barP[5] = '\0';
        barE[5] = '\0';

        for (i = 0; i < 10; i++) {
            barB[i] = (i < bhp) ? '#' : '.';
        }
        barB[10] = '\0';

        sprintf(buf, "HP:[%s] TURBO:[%s] BOSS:[%s]", barP, barE, barB);
        VDP_drawTextFill(buf, 1, HUD_ROW_HUD_GLOBAL, 38);

        VDP_drawTextFill("A:VULCAN  B:MISSILE  C:BOOST  MODE:DEBUG", 1, HUD_ROW_HINT_PRIMARY, 38);
    }
}
