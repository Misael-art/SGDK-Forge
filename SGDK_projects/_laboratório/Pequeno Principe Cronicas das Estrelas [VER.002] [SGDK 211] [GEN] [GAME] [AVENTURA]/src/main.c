/* =========================================================================
 * Pequeno Príncipe: Crônicas das Estrelas — VER.002
 * main.c — Entry point
 *
 * Plataforma: Sega Mega Drive / Genesis
 * SDK:        SGDK 2.11
 * ========================================================================= */

#include "pp2.h"

int main(bool hardReset)
{
    (void)hardReset;

    Engine_init();
    Engine_run();   /* never returns */

    return 0;
}
