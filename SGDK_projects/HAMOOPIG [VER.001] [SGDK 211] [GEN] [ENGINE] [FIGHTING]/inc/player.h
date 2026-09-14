#ifndef PLAYER_H
#define PLAYER_H

#include "globals.h"

void PLAYER_STATE(u8 Player, u16 State);
void PLAYER_STATE_KEN(u8 Player, u16 State);
void PLAYER_STATE_MUSGO(u8 Player, u16 State);
void FUNCAO_PLAY_SND(u8 Player, u16 State);
void FUNCAO_DEPTH(u8 Player);
void FUNCAO_UPDATE_LIFESP(u8 Player, u8 EnergyType, s8 Value);
void FUNCAO_APPLY_FIGHTER_PALETTE(u8 Player);
void FUNCAO_CYCLE_FIGHTER(u8 Player);

#endif // PLAYER_H
