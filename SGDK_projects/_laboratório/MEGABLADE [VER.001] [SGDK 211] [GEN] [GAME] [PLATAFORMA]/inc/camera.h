#ifndef CAMERA_H
#define CAMERA_H

#include <genesis.h>

/* =========================================================================
 * CAMERA — Dead-zone tracking, dual-layer parallax
 * ========================================================================= */

extern s16 camX, camY;

void CAMERA_init(void);
void CAMERA_centerOn(s16 worldX, s16 worldY);
void CAMERA_onVBlank(void);   /* sine-wave line scroll effect */

#endif /* CAMERA_H */
