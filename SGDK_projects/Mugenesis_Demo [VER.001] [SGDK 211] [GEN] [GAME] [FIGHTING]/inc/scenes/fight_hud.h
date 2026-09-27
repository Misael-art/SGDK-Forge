#ifndef FIGHT_HUD_H
#define FIGHT_HUD_H
void FIGHT_HUD_init(void);
u16 FIGHT_HUD_vramNext(void);
void FIGHT_HUD_update(void);   /* chamar apos MG_fightRender(); so escreve o que mudou */
void FIGHT_HUD_invalidateBGA(void); /* BG_A stage map was restored; redraw cached HUD cells */
void FIGHT_HUD_deferBGARebuild(void); /* wait one VBlank after a queued full-plane restore */
#endif
