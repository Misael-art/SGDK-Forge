#ifndef HAMOOPIG_RUNTIME_PROBE_H
#define HAMOOPIG_RUNTIME_PROBE_H
#include <genesis.h>
void HAMOOPIG_probeInit(void);
void HAMOOPIG_probeSpriteDma(u16 dmaBeforeSpriteUpdate);
void HAMOOPIG_probeStageDma(u8 stage, u16 dmaBeforeStage);
void HAMOOPIG_probeTick(u8 scene);
/* Leitura dos mesmos picos que o probe ja exporta para a SRAM.  O overlay de
   debug le daqui em vez de recalcular, para nao divergir da evidencia. */
u16 HAMOOPIG_probePeakDma(void);
u16 HAMOOPIG_probePeakActiveSprites(void);
u16 HAMOOPIG_probePeakScanlineSprites(void);
u16 HAMOOPIG_probePeakVdpSprites(void);
#endif
