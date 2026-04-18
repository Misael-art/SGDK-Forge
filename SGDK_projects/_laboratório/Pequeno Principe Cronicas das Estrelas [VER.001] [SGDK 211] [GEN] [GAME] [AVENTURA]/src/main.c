/**
 * ============================================================================
 *  MEGA DRIVE / GENESIS - Projeto Template
 * ============================================================================
 *
 *  Este arquivo e o ponto de partida do seu jogo para Mega Drive.
 *  Ele demonstra a estrutura basica de um programa SGDK:
 *
 *    1. Incluir genesis.h (biblioteca principal do SGDK)
 *    2. Inicializar hardware e subsistemas
 *    3. Rodar o game loop (laco infinito que roda a cada frame)
 *    4. Chamar SYS_doVBlankProcess() no final de cada frame
 *
 *  O Mega Drive roda a 60fps (NTSC) ou 50fps (PAL). Cada iteracao do
 *  while(TRUE) corresponde a 1 frame de jogo.
 *
 *  SGDK v2.11 - https://github.com/Stephane-D/SGDK
 * ============================================================================
 */

#include "project.h"

static GameContext gGame;

int main(bool hardReset)
{
    Game_init(&gGame, hardReset);

    while (TRUE)
    {
        Game_update(&gGame);
        Game_draw(&gGame);
        SYS_doVBlankProcess();
    }

    return 0;
}
