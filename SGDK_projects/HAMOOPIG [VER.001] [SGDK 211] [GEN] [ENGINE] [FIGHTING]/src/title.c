#include <genesis.h>
#include "title.h"
#include "globals.h"
#include "gfx.h"
#include "hud_gfx.h"
#include "sprite.h"
#include "sound.h"
#include "init.h"
#include "debug.h"
#include "debug.h"

/* The title artwork occupies tiles 1..529.  Keep the 16x16 message atlas
   and the one cursor tile above it, outside both title planes. */
#define TITLE_FONT_TILE_BASE 620
#define TITLE_CURSOR_TILE (TITLE_FONT_TILE_BASE + 144)
#define TITLE_PANEL_X 1
#define TITLE_PANEL_W 18
/* Cada glifo ocupa 2 linhas, entao um painel de H linhas comporta H/2 slots.
   O menu normal cabe em 11 linhas (titulo + 4 itens); a pagina de debug tem
   9 itens e precisa de 19.  Os dois sao ancorados pela mesma base (linha 25)
   para que o painel cresca para cima, sobre a arte. */
#define TITLE_MENU_PANEL_Y 15
#define TITLE_MENU_PANEL_H 11
#define TITLE_DEBUG_PANEL_Y 6
#define TITLE_DEBUG_PANEL_H 20
#define TITLE_PANEL_MAX_H TITLE_DEBUG_PANEL_H
#define TITLE_OPENING_FRAMES 120

u8 titlePage = TITLE_PAGE_MAIN;
u8 titleCursor = TITLE_MAIN_START;

static u8 sPanelY = TITLE_MENU_PANEL_Y;
static u8 sPanelH = TITLE_MENU_PANEL_H;
static u16 sTitleMap[TITLE_PANEL_W * TITLE_PANEL_MAX_H];
static u16 sTitleBlackTile;
static bool sTitleReady;
static bool sTitleDirty;
static u8 sTitlePhase;

static void title_render_main(void);
static void title_menu_sfx(void);

enum
{
	TITLE_PHASE_OPENING = 0,
	TITLE_PHASE_ACTIVE = 1
};

/* A small, authorial-looking chevron uses the same PAL1 as the menu font.
   It is a UI marker, not gameplay art, and costs one tile only. */
static const u32 kTitleCursorTile[8] =
{
	0x20000000, 0x22000000, 0x22200000, 0x22220000,
	0x22200000, 0x22000000, 0x20000000, 0x00000000
};

static const u32 kTitleBlackTile[8] =
{
	0xBBBBBBBB, 0xBBBBBBBB, 0xBBBBBBBB, 0xBBBBBBBB,
	0xBBBBBBBB, 0xBBBBBBBB, 0xBBBBBBBB, 0xBBBBBBBB
};

static u8 title_glyph(const char c)
{
	if(c >= 'A' && c <= 'Z'){ return (u8)(c - 'A'); }
	if(c >= '0' && c <= '9'){ return (u8)(26 + c - '0'); }
	return 0xFF;
}

static void title_map_fill(void)
{
	u16 row;
	u16 col;
	for(row = 0; row < sPanelH; row++)
	{
		for(col = 0; col < TITLE_PANEL_W; col++)
		{
			sTitleMap[(row * TITLE_PANEL_W) + col] = TILE_ATTR_FULL(
				PAL1, FALSE, FALSE, FALSE, sTitleBlackTile);
		}
	}
}

static void title_put_text_at(const char *text, u8 col, u8 row)
{
	u8 glyph;
	u16 base;
	while(*text && col < TITLE_PANEL_W)
	{
		glyph = title_glyph(*text++);
		if(glyph != 0xFF && col + 1 < TITLE_PANEL_W && row + 1 < sPanelH)
		{
			base = TITLE_FONT_TILE_BASE + ((u16)glyph * 2);
			sTitleMap[(row * TITLE_PANEL_W) + col] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, base);
			sTitleMap[(row * TITLE_PANEL_W) + col + 1] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, base + 1);
			sTitleMap[((row + 1) * TITLE_PANEL_W) + col] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, base + 72);
			sTitleMap[((row + 1) * TITLE_PANEL_W) + col + 1] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, base + 73);
			col += 2;
		}
		else
		{
			col++;
		}
	}
}

static u8 title_text_width(const char *text)
{
	u8 length = 0;
	while(*text++){ length++; }
	return (u8)(length * 2);
}

static void title_put_centered(const char *text, u8 row)
{
	u8 width = title_text_width(text);
	u8 col = (width < TITLE_PANEL_W) ? (u8)((TITLE_PANEL_W - width) / 2) : 0;
	title_put_text_at(text, col, row);
}

static void title_put_cursor(u8 row, bool visible)
{
	if(visible && row + 1 < sPanelH)
	{
		sTitleMap[(row * TITLE_PANEL_W)] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, TITLE_CURSOR_TILE);
	}
}

static void title_commit_map(void)
{
	VDP_setTileMapDataRect(BG_A, sTitleMap, TITLE_PANEL_X, sPanelY,
		TITLE_PANEL_W, sPanelH, TITLE_PANEL_W, DMA_QUEUE_COPY);
	sTitleDirty = FALSE;
}

static void title_restore_artwork(void)
{
	VDP_setTileMapEx(BG_A, room_0_bga.tilemap,
		TILE_ATTR_FULL(PAL3, 0, FALSE, FALSE, 501),
		0, 0, 0, 0, 40, 28, DMA);
}

static void title_enter_menu(void)
{
	if(sTitlePhase != TITLE_PHASE_OPENING){ return; }
	/* Keep the opening artwork resident and reveal the menu in one VBlank-safe
	   tilemap update.  A nested full-palette fade here used to leave the title
	   half-dark on real hardware, so the transition is intentionally a clean
	   cut after the timed splash hold. */
	sTitlePhase = TITLE_PHASE_ACTIVE;
	title_restore_artwork();
	title_render_main();
}

static void title_render_main(void)
{
	title_map_fill();
	title_put_centered("MAIN MENU", 0);
	title_put_centered("START", 3);
	title_put_centered("OPTION", 6);
	title_put_cursor((titleCursor == TITLE_MAIN_START) ? 3 : 6, TRUE);
	title_commit_map();
}

static void title_render_options(void)
{
	title_map_fill();
	title_put_centered("OPTIONS", 0);
	title_put_centered(gAudioSfxEnabled ? "SFX ON" : "SFX OFF", 2);
	title_put_centered(gAudioMusicEnabled ? "MUSIC ON" : "MUSIC OFF", 4);
	title_put_centered("DEBUG", 6);
	title_put_centered("BACK", 8);
	title_put_cursor((titleCursor == TITLE_OPTION_SFX) ? 2 :
		(titleCursor == TITLE_OPTION_MUSIC) ? 4 :
		(titleCursor == TITLE_OPTION_DEBUG) ? 6 : 8, TRUE);
	title_commit_map();
}

static void title_render_debug(void)
{
	title_map_fill();
	title_put_centered("DEBUG", 0);
	title_put_centered((gDebugFlags & DBG_BBOX)     ? "BOX ON"  : "BOX OFF",  2);
	title_put_centered((gDebugFlags & DBG_HBOX)     ? "HIT ON"  : "HIT OFF",  4);
	title_put_centered((gDebugFlags & DBG_TEXT)     ? "TEXT ON" : "TEXT OFF", 6);
	title_put_centered((gDebugFlags & DBG_PERF)     ? "PERF ON" : "PERF OFF", 8);
	title_put_centered((gDebugFlags & DBG_FRAMEADV) ? "FRM ON"  : "FRM OFF",  10);
	title_put_centered(gFreeStepArmed               ? "STEP ON" : "STEP OFF", 12);
	title_put_centered((gTimingProfile == TIMING_PROFILE_NORMAL) ? "TICK NORM"
		: ((gLogicRate == LOGIC_RATE_50) ? "TICK L50" : "TICK L60"), 14);
	/* 240 linhas so existe em console PAL; em NTSC a opcao e inerte. */
	title_put_centered(!gRegionIsPal ? "240 NA" : (gScreen240 ? "240 ON" : "240 OFF"), 16);
	title_put_centered("BACK", 18);
	title_put_cursor((u8)(2 + (titleCursor * 2)), TRUE);
	title_commit_map();
}

/* Toda troca de pagina redesenha a arte antes de comitar o painel novo: as
   paginas tem alturas diferentes e sobraria lixo da pagina anterior. */
static void title_goto_page(u8 page, u8 cursor)
{
	titlePage = page;
	titleCursor = cursor;
	if(page == TITLE_PAGE_DEBUG)
	{
		sPanelY = TITLE_DEBUG_PANEL_Y;
		sPanelH = TITLE_DEBUG_PANEL_H;
	}
	else
	{
		sPanelY = TITLE_MENU_PANEL_Y;
		sPanelH = TITLE_MENU_PANEL_H;
	}
	title_menu_sfx();
	title_restore_artwork();
	if(page == TITLE_PAGE_MAIN){ title_render_main(); }
	else if(page == TITLE_PAGE_OPTIONS){ title_render_options(); }
	else { title_render_debug(); }
}

static void title_menu_sfx(void)
{
	if(gAudioSfxEnabled)
	{
		XGM_setPCM(INGAME_SFX, snd_confirm, sizeof(snd_confirm));
		XGM_startPlayPCM(INGAME_SFX, 1, SOUND_PCM_CH3);
	}
}

static void title_start_game(void)
{
	title_menu_sfx();
	PAL_fadeOutAll(8, FALSE);
	FUNCAO_TITLE_EXIT();
	CLEAR_VDP();
	gRoom = 2;
	gFrames = 1;
}

void FUNCAO_TITLE_INIT(void)
{
	if(501 + room_0_bga.tileset->numTile >= TITLE_FONT_TILE_BASE)
	{
		SYS_die("Title font overlaps title artwork");
		return;
	}
	if(!sTitleReady)
	{
		VDP_loadTileSet(&ts_hud_message_font, TITLE_FONT_TILE_BASE, DMA);
		VDP_loadTileData(kTitleCursorTile, TITLE_CURSOR_TILE, 1, CPU);
		sTitleBlackTile = TITLE_CURSOR_TILE + 1;
		VDP_loadTileData(kTitleBlackTile, sTitleBlackTile, 1, CPU);
		PAL_setPalette(PAL1, spr_hud_energy_y.palette->data, CPU);
		sTitleReady = TRUE;
	}
	titlePage = TITLE_PAGE_MAIN;
	titleCursor = TITLE_MAIN_START;
	/* A pagina de debug usa um painel maior; reentrar no titulo tem de voltar
	   a geometria do menu, senao o primeiro commit desenha no lugar errado. */
	sPanelY = TITLE_MENU_PANEL_Y;
	sPanelH = TITLE_MENU_PANEL_H;
	sTitlePhase = TITLE_PHASE_OPENING;
	sTitleDirty = TRUE;
}

void FUNCAO_TITLE_UPDATE(void)
{
	if(!sTitleReady){ return; }
	if(sTitlePhase == TITLE_PHASE_OPENING)
	{
		/* Any first button press skips only the splash.  It is deliberately not
		   reused as a menu confirmation on the same frame. */
		if(gFrames >= TITLE_OPENING_FRAMES ||
			P[1].key_JOY_UP_status == KEY_PRESSED || P[1].key_JOY_DOWN_status == KEY_PRESSED ||
			P[1].key_JOY_A_status == KEY_PRESSED || P[1].key_JOY_START_status == KEY_PRESSED ||
			P[1].key_JOY_B_status == KEY_PRESSED)
		{
			title_enter_menu();
		}
		return;
	}
	if(titlePage == TITLE_PAGE_MAIN)
	{
		if(P[1].key_JOY_UP_status == KEY_PRESSED || P[1].key_JOY_DOWN_status == KEY_PRESSED)
		{
			titleCursor = (titleCursor == TITLE_MAIN_START) ? TITLE_MAIN_OPTION : TITLE_MAIN_START;
			title_menu_sfx();
			title_render_main();
		}
		if(P[1].key_JOY_A_status == KEY_PRESSED || P[1].key_JOY_START_status == KEY_PRESSED)
		{
			if(titleCursor == TITLE_MAIN_START){ title_start_game(); }
			else
			{
				titlePage = TITLE_PAGE_OPTIONS;
				titleCursor = TITLE_OPTION_SFX;
				title_menu_sfx();
				title_render_options();
			}
		}
		return;
	}

	if(titlePage == TITLE_PAGE_OPTIONS)
	{
		bool confirm = (P[1].key_JOY_A_status == KEY_PRESSED || P[1].key_JOY_START_status == KEY_PRESSED);
		bool adjust = (P[1].key_JOY_LEFT_status == KEY_PRESSED || P[1].key_JOY_RIGHT_status == KEY_PRESSED);

		if(P[1].key_JOY_UP_status == KEY_PRESSED && titleCursor > TITLE_OPTION_SFX){ titleCursor--; title_menu_sfx(); title_render_options(); }
		if(P[1].key_JOY_DOWN_status == KEY_PRESSED && titleCursor < TITLE_OPTION_BACK){ titleCursor++; title_menu_sfx(); title_render_options(); }

		if(titleCursor == TITLE_OPTION_DEBUG && confirm)
		{
			title_goto_page(TITLE_PAGE_DEBUG, TITLE_DEBUG_BBOX);
			return;
		}
		if(titleCursor == TITLE_OPTION_BACK && confirm)
		{
			title_goto_page(TITLE_PAGE_MAIN, TITLE_MAIN_OPTION);
			return;
		}
		if(P[1].key_JOY_B_status == KEY_PRESSED)
		{
			title_goto_page(TITLE_PAGE_MAIN, TITLE_MAIN_OPTION);
			return;
		}
		/* SFX/MUSIC alternam com esquerda/direita ou com o botao de confirmar;
		   DEBUG e BACK ja retornaram acima, entao nao caem aqui. */
		if(adjust || (confirm && titleCursor < TITLE_OPTION_DEBUG))
		{
			if(titleCursor == TITLE_OPTION_SFX){ gAudioSfxEnabled = !gAudioSfxEnabled; }
			else if(titleCursor == TITLE_OPTION_MUSIC){ gAudioMusicEnabled = !gAudioMusicEnabled; }
			title_menu_sfx();
			title_render_options();
		}
		return;
	}

	/* --- PAGINA DEBUG --- */
	{
		bool confirm = (P[1].key_JOY_A_status == KEY_PRESSED || P[1].key_JOY_START_status == KEY_PRESSED);
		bool adjust = (P[1].key_JOY_LEFT_status == KEY_PRESSED || P[1].key_JOY_RIGHT_status == KEY_PRESSED);

		if(P[1].key_JOY_UP_status == KEY_PRESSED && titleCursor > TITLE_DEBUG_BBOX){ titleCursor--; title_menu_sfx(); title_render_debug(); }
		if(P[1].key_JOY_DOWN_status == KEY_PRESSED && titleCursor < TITLE_DEBUG_BACK){ titleCursor++; title_menu_sfx(); title_render_debug(); }

		if(P[1].key_JOY_B_status == KEY_PRESSED ||
			(confirm && titleCursor == TITLE_DEBUG_BACK))
		{
			title_goto_page(TITLE_PAGE_OPTIONS, TITLE_OPTION_DEBUG);
			return;
		}

		if(adjust || (confirm && titleCursor < TITLE_DEBUG_BACK))
		{
			switch(titleCursor)
			{
				case TITLE_DEBUG_BBOX:     gDebugFlags ^= DBG_BBOX; break;
				case TITLE_DEBUG_HBOX:     gDebugFlags ^= DBG_HBOX; break;
				case TITLE_DEBUG_TEXT:     gDebugFlags ^= DBG_TEXT; break;
				case TITLE_DEBUG_PERF:     gDebugFlags ^= DBG_PERF; break;
				case TITLE_DEBUG_FRAMEADV: gDebugFlags ^= DBG_FRAMEADV; break;
				case TITLE_DEBUG_FREESTEP:
					gFreeStepArmed = !gFreeStepArmed;
					gFreeStepAdvance = FALSE;
					break;
				case TITLE_DEBUG_TICK:
					/* NORM -> L60 -> L50 -> NORM.  NORM e a politica de
					   entrega (60 ticks/s nas duas regioes); os dois LEGACY
					   existem para comparar com o comportamento antigo e sao
					   diagnostico, nao opcao de jogo. */
					if(gTimingProfile == TIMING_PROFILE_NORMAL)
					{
						gTimingProfile = TIMING_PROFILE_LEGACY;
						gLogicRate = LOGIC_RATE_60;
					}
					else if(gLogicRate == LOGIC_RATE_60){ gLogicRate = LOGIC_RATE_50; }
					else { gTimingProfile = TIMING_PROFILE_NORMAL; gLogicRate = LOGIC_RATE_60; }
					break;
				case TITLE_DEBUG_H240:
					/* Inerte em NTSC: 240 linhas so existem no timing PAL.
					   A altura NAO e aplicada aqui: o proprio menu de titulo
					   desenha um tilemap de 28 linhas e mostraria lixo na
					   faixa extra. Quem aplica e FUNCAO_SCREEN_HEIGHT_APPLY,
					   ja dentro da luta e so se o cenario for alto o bastante. */
					if(gRegionIsPal){ gScreen240 = !gScreen240; }
					break;
				default: break;
			}
			DEBUG_syncMaster();
			title_menu_sfx();
			title_render_debug();
		}
	}
}

void FUNCAO_TITLE_EXIT(void)
{
	sTitleDirty = FALSE;
	/* The caller tears the title down with CLEAR_VDP, which hands the whole
	   tile range to the next scene.  Drop the "already uploaded" latch so a
	   later return to gRoom 1 re-uploads the font, cursor and black tile
	   instead of drawing the menu with whatever now lives at those indices. */
	sTitleReady = FALSE;
}
