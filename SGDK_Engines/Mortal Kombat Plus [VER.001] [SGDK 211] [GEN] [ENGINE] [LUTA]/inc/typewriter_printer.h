/**
 *  \file typewriter_printer.h
 *  \brief 
 *  \author Nil Obermuller Schaupp
 */
#ifndef _TYPEWRITER_P_H_
#define _TYPEWRITER_P_H_

#include "types.h"
#include "sys.h"
#include "vdp_tile.h"
#include "string.h"
#include "estruturas.h"

/**
 * @brief
 *
 * @param text The string
 * @param x X position (in tile).
 * @param y Y position (in tile).
 * @param delay time to delay
 * @param plane Plane where we want to load tilemap.<br>
 *      Accepted values are:<br>
 *      - BG_A<br>
 *      - BG_B<br>
 *      - WINDOW<br> - not tested yet
 * @param numPal Palette number: PAL0, PAL1, PAL2 or PAL3
 */
void typewriterEffect(const char *text, u16 x, u16 y, u16 delay, VDPPlane plane, u16 numPal);

void typewriterWriteAllLines(const TextLine *lines, u16 numLines, VDPPlane plane, u16 numPal);

#endif