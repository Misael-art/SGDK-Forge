#ifndef GAME_CONFIG_H
#define GAME_CONFIG_H

#include <genesis.h>

/* =========================================================================
 * MEGABLADE MD — Game Configuration
 * All constants in one place. Change here, not scattered in code.
 * ========================================================================= */

/* World dimensions */
#define WORLD_WIDTH_PX      3328    /* fg map width in pixels (tilemap * 8) */
#define WORLD_HEIGHT_PX     224     /* screen height */

/* Physics (fix32) */
#define GRAVITY             FIX32(0.3)
#define JUMP_SPEED          FIX32(-6.5)
#define WALK_SPEED          FIX32(2.5)
#define RUN_SPEED           FIX32(4.5)
#define BRAKE_SPEED         FIX32(2.0)
#define MAX_MOVE_X          FIX32(5.0)
#define ACCEL               FIX32(0.12)
#define DEACCEL             FIX32(0.18)
#define GROUND_Y            FIX32(152)  /* world Y of ground surface */
#define MIN_WORLD_X         FIX32(16)
#define MAX_WORLD_X         FIX32(WORLD_WIDTH_PX - 16)

/* Player */
#define PLAYER_MAX_HP       3
#define PLAYER_INVULN_TIME  90      /* frames of invulnerability after hit */
#define PLAYER_HITBOX_W     20
#define PLAYER_HITBOX_H     32
#define PLAYER_HITBOX_OX    -10     /* hitbox offset from posX */
#define PLAYER_HITBOX_OY    -32     /* hitbox offset from posY (ground-based) */

/* Player animation indices (matching sonic.png sheet) */
#define ANIM_STAND          0
#define ANIM_WAIT           1
#define ANIM_WALK           2
#define ANIM_RUN            3
#define ANIM_BRAKE          4
#define ANIM_UP             5
#define ANIM_CROUCH         6
#define ANIM_ROLL           7

/* Enemies */
#define MAX_ENEMIES         6
#define ENEMY_HITBOX_W      24
#define ENEMY_HITBOX_H      24
#define ENEMY_HITBOX_OX     -12
#define ENEMY_HITBOX_OY     -24
#define ENEMY_PATROL_SPEED  FIX32(1.2)
#define ENEMY_CHASE_SPEED   FIX32(2.0)
#define ENEMY_CHASE_DIST    120     /* pixels — chase player within this range */
#define ENEMY_HP            2

/* Camera dead-zone (player moves this far before camera follows) */
#define CAM_LEAD_X_RIGHT    240
#define CAM_LEAD_X_LEFT     40
#define CAM_LEAD_Y_DOWN     150
#define CAM_LEAD_Y_UP       60

/* Effects */
#define SHAKE_MAGNITUDE     3
#define SHAKE_DURATION      16
#define FLASH_DURATION      8

/* Scoring */
#define SCORE_PER_ENEMY     100

/* Game states */
typedef void (*StateFunction)(void);
extern StateFunction currentStateUpdate;
void set_state(StateFunction nextState);

/* State prototypes */
void state_title_update(void);
void state_gameplay_update(void);
void state_gameover_update(void);

#endif /* GAME_CONFIG_H */
