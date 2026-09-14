#include <genesis.h>
#include "opening.h"
#include "scene.h"
#include "globals.h"
#include "gfx.h"
#include "graphics.h"

static u8  sPhase;
static u16 sPhaseTicks;
static bool sSkipRequested;

static void opening_copy_palette(u16 *destination, const Palette *source)
{
	u16 colorCount = 0;
	memset(destination, 0, 16 * sizeof(u16));
	if(source && source->data)
	{
		colorCount = (source->length < 16) ? source->length : 16;
		memcpy(destination, source->data, colorCount * sizeof(u16));
	}
}

void FUNCAO_OPENING_INIT(void)
{
	sPhase = OPENING_PHASE_FADE_IN;
	sPhaseTicks = 0;
	sSkipRequested = FALSE;

	/* Carrega com a tela ja preta: PAL_fadeIn abaixo e quem revela.  Sem isto
	   o primeiro frame mostraria a arte em brilho total antes do fade. */
	PAL_setColors(0, (u16*)palette_black, 64, CPU);

	VDP_loadTileSet(room_0_bgb.tileset, 1, DMA);
	VDP_setTileMapEx(BG_B, room_0_bgb.tilemap,
		TILE_ATTR_FULL(PAL2, 0, FALSE, FALSE, 1), 0, 0, 0, 0, 40, 28, DMA);
	VDP_loadTileSet(room_0_bga.tileset, 501, DMA);
	VDP_setTileMapEx(BG_A, room_0_bga.tilemap,
		TILE_ATTR_FULL(PAL3, 0, FALSE, FALSE, 501), 0, 0, 0, 0, 40, 28, DMA);

	opening_copy_palette(&palette[32], room_0_bgb.palette);
	opening_copy_palette(&palette[48], room_0_bga.palette);

	/* Um unico dono de CRAM: o fade e assincrono e conduzido por esta maquina
	   de estados.  Nenhuma outra cena inicia fade enquanto a abertura roda. */
	PAL_fadeIn(0, (4 * 16) - 1, palette, OPENING_FADE_IN_TICKS, TRUE);
}

void FUNCAO_OPENING_UPDATE(void)
{
	sPhaseTicks++;

	/* A borda e consumida AQUI.  O titulo so le input depois do proprio
	   fade-in, entao o mesmo toque nunca confirma START na tela seguinte. */
	if(sPhase == OPENING_PHASE_HOLD &&
	   (P[1].key_JOY_A_status == KEY_PRESSED ||
	    P[1].key_JOY_START_status == KEY_PRESSED ||
	    P[1].key_JOY_B_status == KEY_PRESSED))
	{
		sSkipRequested = TRUE;
		P[1].key_JOY_A_status = KEY_FREE;
		P[1].key_JOY_START_status = KEY_FREE;
		P[1].key_JOY_B_status = KEY_FREE;
	}

	switch(sPhase)
	{
		case OPENING_PHASE_FADE_IN:
			/* O HOLD so comeca quando o fade termina de fato; contar os dois
			   juntos encurtaria a leitura dos creditos. */
			if(sPhaseTicks >= OPENING_FADE_IN_TICKS && !PAL_isDoingFade())
			{
				sPhase = OPENING_PHASE_HOLD;
				sPhaseTicks = 0;
			}
			break;

		case OPENING_PHASE_HOLD:
			if(sSkipRequested || sPhaseTicks >= OPENING_HOLD_TICKS)
			{
				sPhase = OPENING_PHASE_FADE_OUT;
				sPhaseTicks = 0;
				PAL_fadeOutAll(OPENING_FADE_OUT_TICKS, TRUE);
			}
			break;

		case OPENING_PHASE_FADE_OUT:
			if(sPhaseTicks >= OPENING_FADE_OUT_TICKS && !PAL_isDoingFade())
			{
				sPhase = OPENING_PHASE_DONE;
				/* CLEAR_VDP antes de entregar: o titulo carrega a composicao
				   dele com a tela protegida, nao por cima desta. */
				CLEAR_VDP();
				SCENE_request(SCENE_TITLE);
			}
			break;

		default:
			break;
	}
}

u8  OPENING_phase(void) { return sPhase; }
u16 OPENING_phaseTicks(void) { return sPhaseTicks; }
