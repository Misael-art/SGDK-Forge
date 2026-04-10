#ifndef TRIGONOMETRIC_H
#define TRIGONOMETRIC_H

#include <genesis.h>

// Definições de constantes
#define TABLE_SIZE 91
#define FIX16_PI           FIX16(3.14159265358979323846)
#define FIX16_HALF_PI      FIX16(1.57079632679489661923)
#define FIX16_180_OVER_PI  FIX16(57.29577951308232)
#define FIX16_TWO_PI       FIX16(6.28318530717958647692)

// Declaração da Tabela de Seno e Cosseno
extern fix16 TRIGONOMETRIC_TABLE[TABLE_SIZE];

// Funções Trigonométricas
fix16 CosValor(fix16 ang);
fix16 SinValor(fix16 ang);

fix16 NORMALIZE_ANGLE(fix16 a);
fix16 TRG_FIND_ANGLE(fix16 p1x, fix16 p1y, fix16 p2x, fix16 p2y);
void TRG_MXY_PAD(fix16 *x2, fix16 *y2, fix16 x1, fix16 y1, fix16 ang, fix16 dist);
void TRG_MXY_PAD_EX(fix16 *x2, fix16 *y2, fix16 x1, fix16 y1, fix16 ang, fix16 dist, fix16 cosAdjustment, fix16 sinAdjustment);

#endif
