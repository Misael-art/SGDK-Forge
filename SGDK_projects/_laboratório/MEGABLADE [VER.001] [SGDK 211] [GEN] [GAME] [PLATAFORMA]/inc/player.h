#ifndef PLAYER_H
#define PLAYER_H

#include <genesis.h>
#include "game_config.h"

/* =========================================================================
 * PLAYER — Physics, animation, input
 * ========================================================================= */

/* World position (fix32 for sub-pixel accuracy) */
extern fix32 playerPosX;
extern fix32 playerPosY;
extern fix32 playerMovX;
extern fix32 playerMovY;

/* State flags */
extern bool  playerOnGround;
extern bool  playerFacingRight;
extern s16   playerInvulnTimer;   /* invulnerability frames after hit */
extern u8    playerHP;
extern u8    playerLives;
extern u32   playerScore;

/* Sprite handle */
extern Sprite* playerSpr;

/* Public API */
u16  PLAYER_init(u16 vramIndex);
void PLAYER_update(void);
void PLAYER_updateScreenPos(void);
void PLAYER_handleInput(u16 pad);
void PLAYER_doJoyEvent(u16 joy, u16 changed, u16 state);
void PLAYER_takeDamage(void);
void PLAYER_addScore(u32 points);
void PLAYER_reset(void);

#endif /* PLAYER_H */
