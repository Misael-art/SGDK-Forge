#include <genesis.h>

#include "project_config.h"
#include "input_abstraction.h"
#include "scene_manager.h"
#include "system/qa_bootstrap.h"
#include "system/runtime_probe.h"

int main(bool hardReset)
{
    SceneId initial_scene;
    (void)hardReset;

    /* Inicializa subsistemas de tela e engine de sprites */
    VDP_setScreenWidth320();
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_setTextPlane(BG_A);
    VDP_setTextPalette(PAL0);
    VDP_setTextPriority(FALSE);
    SPR_init();

    /* Inicializa subsistemas autorais */
    IO_init();
    initial_scene = QA_bootstrapResolve(APP_SCENE_BRANDING);
    SM_init(initial_scene);
    MDRuntimeProbe_init();

    while (TRUE)
    {
        /* Polling do joystick */
        IO_update();

        /* Update do gerenciador de cena, salvo hold deterministico de QA */
        if (!MDRuntimeProbe_shouldHoldScene())
        {
            SM_update();
        }

        /* Flush da engine de sprites antes do VBlank */
        SPR_update();

        SYS_doVBlankProcess();
        MDRuntimeProbe_tick();
    }

    return 0;
}
