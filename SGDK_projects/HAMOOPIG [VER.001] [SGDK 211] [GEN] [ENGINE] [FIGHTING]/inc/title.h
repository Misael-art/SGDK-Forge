#ifndef TITLE_H
#define TITLE_H

#include <genesis.h>

typedef enum
{
	TITLE_PAGE_MAIN = 0,
	TITLE_PAGE_OPTIONS = 1,
	TITLE_PAGE_DEBUG = 2
} TitlePage;

typedef enum
{
	TITLE_MAIN_START = 0,
	TITLE_MAIN_OPTION = 1
} TitleMainItem;

typedef enum
{
	/* Ordem de leitura: audio, HUD, regra, ferramentas.  DEFAULTS e acao, nao
	   toggle, e por isso fica junto de BACK.

	   So existem aqui opcoes cujo efeito e OBSERVAVEL, nao so implementado --
	   o plano proibe botao inativo sem destino (secao 3).  Tres grupos ficam
	   de fora por motivos diferentes:

	     sistema ausente   SPECIAL BAR e SPECIAL RULES (P05), HIT COUNT (P06),
	                       TIMER BG (P07), STAGE COLOR/MOTION/2 (P08, P09).

	     efeito inalcancavel  INTRO e FADE.  gConfig.showOpening e
	                       gConfig.useFade estao implementados e corretos, mas
	                       a abertura e o fade do titulo so rodam no BOOT, e o
	                       unico produtor de SCENE_TITLE e a propria abertura.
	                       Sem persistencia em SRAM a preferencia morre no
	                       reset, entao o jogador jamais veria a diferenca.
	                       Voltam ao menu junto com a persistencia ou com um
	                       caminho de retorno ao titulo.
	*/
	TITLE_OPTION_SFX      = 0,
	TITLE_OPTION_MUSIC    = 1,
	TITLE_OPTION_LIFEBAR  = 2,
	TITLE_OPTION_TIMER    = 3,
	TITLE_OPTION_TIMELIM  = 4,
	TITLE_OPTION_DEBUG    = 5,
	TITLE_OPTION_DEFAULTS = 6,
	TITLE_OPTION_BACK     = 7
} TitleOptionItem;

typedef enum
{
	TITLE_DEBUG_BBOX = 0,
	TITLE_DEBUG_HBOX = 1,
	TITLE_DEBUG_TEXT = 2,
	TITLE_DEBUG_PERF = 3,
	TITLE_DEBUG_FRAMEADV = 4,
	TITLE_DEBUG_FREESTEP = 5,
	TITLE_DEBUG_TICK = 6,
	TITLE_DEBUG_H240 = 7,
	TITLE_DEBUG_BACK = 8
} TitleDebugItem;

extern u8 titlePage;
extern u8 titleCursor;

void FUNCAO_TITLE_INIT(void);
void FUNCAO_TITLE_UPDATE(void);
void FUNCAO_TITLE_EXIT(void);

#endif
