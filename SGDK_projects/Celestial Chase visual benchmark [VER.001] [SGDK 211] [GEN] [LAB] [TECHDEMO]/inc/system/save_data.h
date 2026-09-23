#ifndef SYSTEM_SAVE_DATA_H
#define SYSTEM_SAVE_DATA_H

#include <genesis.h>

#define SAVE_DATA_SRAM_OFFSET 0x600

void SAVE_DATA_init(void);
u32 SAVE_DATA_highscore(void);
bool SAVE_DATA_trySubmitEndlessScore(u32 score);

#endif
