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
	TITLE_OPTION_SFX = 0,
	TITLE_OPTION_MUSIC = 1,
	TITLE_OPTION_DEBUG = 2,
	TITLE_OPTION_BACK = 3
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
