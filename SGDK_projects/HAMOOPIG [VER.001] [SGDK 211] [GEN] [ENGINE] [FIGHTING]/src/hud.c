#include <genesis.h>
#include "hud.h"
#include "globals.h"
#include "config.h"
#include "scene.h"
#include "timing.h"
#include "sprite.h"
#include "hud_gfx.h"
#include "hamoopig_runtime_probe.h"

static void hud_window_draw_clock(void);
static void hud_clock_background_update(void);
static void hud_combo_clear(void);
static void hud_combo_update(void);
static void hud_sync_segment_tile(void);
static void hud_identity_update(void);
static const SpriteDefinition *hud_portrait_definition(u8 id);
static void hud_draw_life_bar(u8 player, s8 energy);

void FUNCAO_RELOGIO()
{
	/* TIME LIMIT OFF nao para o relogio "visualmente": para a CONTAGEM, entao
	   nao existe time-over. Esconder o mostrador e outra opcao (hudTimer). */
	if(gMatchRules.timeLimit == CONFIG_TIME_OFF){ return; }

	if(gClockTimer>0 && (gClockLTimer>0 || gClockRTimer>0) && (P[1].energiaBase>0 && P[2].energiaBase>0) ){ gClockTimer--; }

	if(gClockTimer==0)
	{
		gClockRTimer--;
		if(gClockRTimer==-1)
		{
			if(gClockLTimer>0)
			{
				gClockLTimer--;
				gClockRTimer=9;
			}
			else
			{
				gClockRTimer=0;
			}
		}
		gClockTimer=(s8)TIMING_roundClockTicks();
		hud_window_draw_clock();
	}
}

#define HUD_P1_X            32
#define HUD_P2_X            176
#define HUD_BAR_SEGMENTS    8
#define HUD_BAR_Y           8
#define HUD_BAR_ROW         (HUD_BAR_Y / 8)
#define HUD_BAR_STEP        16
#define HUD_CLK_L_X         144
#define HUD_CLK_R_X         160
#define HUD_CLK_Y           0
#define HUD_CLK_BG_X        17
#define HUD_CLK_BG_ROW      0
#define HUD_CLK_BG_COLS     6
#define HUD_FRAME_P1_COL    4
#define HUD_FRAME_P2_COL    22
#define HUD_SPECIAL_P1_COL  4
#define HUD_SPECIAL_P2_COL 22
#define HUD_SPECIAL_ROW     27
#define HUD_SPECIAL_LABEL_ROW 26
#define HUD_MESSAGE_ROW     5
#define HUD_MESSAGE_ROWS    6
#define HUD_COMBO_ROW       13
#define HUD_COMBO_ROWS      4
#define HUD_KO_BANNER_X     136
#define HUD_KO_BANNER_Y     96
/* WINDOW is the fixed screen-space owner for combat HUD.  BG_A remains
   available to diagnostics and future scene overlays; writing transient HUD
   maps there was the source of patterned rectangles appearing over the stage
   when combo/special state changed. */
#define HUD_PLANE           WINDOW

static u16 sHudMessageTileBase;
static u16 sHudBlackTile;
static u16 sHudLifeTrackTileBase;
static u16 sHudSpecialTileBase;
static u16 sHudSpecialFilledTileBase;
static u8 sHudMessage = 0xFF;
static u16 sHudMessageMap[40 * HUD_MESSAGE_ROWS];
static Sprite *sHudP1Segments[HUD_BAR_SEGMENTS];
static Sprite *sHudP2Segments[HUD_BAR_SEGMENTS];
static Sprite *sHudP1Damage[HUD_BAR_SEGMENTS];
static Sprite *sHudP2Damage[HUD_BAR_SEGMENTS];
static Sprite *sHudLifeBarP1;
static Sprite *sHudLifeBarP2;
static Sprite *sHudClockSpriteL;
static Sprite *sHudClockSpriteR;
static s8  sHudClockDigitL = -1;
static s8  sHudClockDigitR = -1;
static u8  sHudWindowActive = 0;
static u8  sHudClockBgState = 0xFF;
static u8  sHudLifeTrackVisible = 0xFF;
static s8  sHudSpecialCount[2] = { -1, -1 };
static u8  sHudSpecialEnabled = 0xFF;
static u16 sHudComboMap[40 * HUD_COMBO_ROWS];
static u8  sHudComboValue = 0xFF;
static u8  sHudComboPlayer = 0;
static u8  sHudFighterId[2] = { 0xFF, 0xFF };
static u8  sHudWins[2] = { 0xFF, 0xFF };
static Sprite *sHudPortrait[2];
static Sprite *sHudKoBanner;

static void hud_draw_text(const char *text, u16 x, u16 y)
{
	VDP_drawTextEx(HUD_PLANE, text,
		TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, 0), x, y, CPU);
}

/* PAL1 index 14 is unused by the source HUD atlas.  Reserve it for the
   charged special state; both states are opaque authored plates so the meter
   never falls through to BG_A tile zero (a black rectangle). */
/* CRAM words are BGR nibbles: 0x0EA0 is bright cyan, not peach. */
static const u16 kHudSpecialBrightColor = 0x0EA0;
static const u16 kHudIdentityWhite = 0x0EEE;

/* PAL1 index 11 = black. Kept only for the transient result-message panel;
   the life bars themselves no longer paint a full-width WINDOW rectangle. */
static const u32 kHudBlackTile[8] =
{
	0xBBBBBBBB, 0xBBBBBBBB, 0xBBBBBBBB, 0xBBBBBBBB,
	0xBBBBBBBB, 0xBBBBBBBB, 0xBBBBBBBB, 0xBBBBBBBB
};

static const char *hud_fighter_name(u8 id)
{
	if(id == 2){ return "KEN"; }
	if(id == 3){ return "MUSGO"; }
	return "RYO";
}

static const SpriteDefinition *hud_portrait_definition(u8 id)
{
	if(id == 2){ return &spr_hud_portrait_ken; }
	if(id == 3){ return &spr_hud_portrait_musgo; }
	return &spr_hud_portrait_ryo;
}

static void hud_ko_banner_set(u8 visible)
{
	if(visible && !sHudKoBanner)
	{
		const u16 flags = SPR_FLAG_DISABLE_DELAYED_FRAME_UPDATE |
			SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC |
			SPR_FLAG_AUTO_TILE_UPLOAD;
		sHudKoBanner = SPR_addSpriteExSafe(&spr_hud_ko_banner,
			HUD_KO_BANNER_X, HUD_KO_BANNER_Y,
			TILE_ATTR(PAL1, FALSE, FALSE, FALSE), flags);
		if(!sHudKoBanner){ SYS_die("HUD KO banner allocation failed"); return; }
		SPR_setDepth(sHudKoBanner, 1);
	}
	if(sHudKoBanner)
	{
		SPR_setVisibility(sHudKoBanner, visible ? VISIBLE : HIDDEN);
		if(!visible)
		{
			SPR_releaseSprite(sHudKoBanner);
			sHudKoBanner = NULL;
		}
	}
}

	/* Identity is anchored to the portrait, not to a debug-like text row. */
static void hud_identity_update(void)
{
	u8 p;
	if(!sHudWindowActive){ return; }
	if(sHudFighterId[0] == P[1].id && sHudFighterId[1] == P[2].id &&
		sHudWins[0] == P[1].wins && sHudWins[1] == P[2].wins){ return; }
	/* Identity text has a different job from the portrait: it must remain
	   readable over both the pale sky and the dark vegetation. Keep it in the
	   HUD palette instead of inheriting a fighter's skin/material colors. */
	hud_draw_text("      ", 0, 3);
	hud_draw_text("      ", 34, 3);
	hud_draw_text("      ", 0, 4);
	hud_draw_text("      ", 34, 4);
	hud_draw_text("      ", 0, 5);
	hud_draw_text("      ", 34, 5);
	hud_draw_text(hud_fighter_name(P[1].id), 0, 4);
	hud_draw_text(hud_fighter_name(P[2].id), 34, 4);
	for(p = 0; p < 2; p++)
	{
		u8 x = (p == 0) ? 0 : 34;
		hud_draw_text((p == 0 && P[1].wins >= 1) || (p == 1 && P[2].wins >= 1) ? "*" : ".", x, 5);
		hud_draw_text((p == 0 && P[1].wins >= 2) || (p == 1 && P[2].wins >= 2) ? "*" : ".", x + 2, 5);
	}
	sHudFighterId[0] = P[1].id; sHudFighterId[1] = P[2].id;
	sHudWins[0] = P[1].wins; sHudWins[1] = P[2].wins;
}

void hud_window_load(void)
{
	/* Life chassis and fill are authored WINDOW plates. Keeping these static
	   pixels on the plane removes a whole bank of SAT entries from the
	   fighter's worst scanlines. */
	sHudMessageTileBase = gInd_tileset;
	VDP_loadTileSet(&ts_hud_message_font, sHudMessageTileBase, DMA);
	gInd_tileset += ts_hud_message_font.numTile;
	sHudLifeTrackTileBase = gInd_tileset;
	VDP_loadTileSet(&ts_hud_life_track, sHudLifeTrackTileBase, DMA);
	gInd_tileset += ts_hud_life_track.numTile;
	sHudSpecialTileBase = gInd_tileset;
	VDP_loadTileSet(&ts_hud_special_segment, sHudSpecialTileBase, DMA);
	sHudSpecialFilledTileBase = sHudSpecialTileBase + 2u;
	gInd_tileset += ts_hud_special_segment.numTile;
	sHudBlackTile = gInd_tileset;
	VDP_loadTileData(kHudBlackTile, sHudBlackTile, 1, CPU);
	HAMOOPIG_probeVramRange(sHudMessageTileBase,
		(u16)(ts_hud_message_font.numTile + ts_hud_life_track.numTile +
			ts_hud_special_segment.numTile + 1u));
	gInd_tileset += 1;
	sHudMessage = 0xFF;
	hud_combo_clear();
}

static u8 hud_clock_digit(s8 v)
{
	if(v < 0){ return 0; }
	if(v > 9){ return 9; }
	return (u8)v;
}

static void hud_window_put_digit(u8 side, u8 digit)
{
	Sprite *sprite = (side == 0) ? sHudClockSpriteL : sHudClockSpriteR;
	if(!sprite){ return; }
	SPR_setFrame(sprite, digit);
}

static void hud_combo_line(const char *str, u16 col, u16 row)
{
	while(*str)
	{
		u8 ch = *str++;
		u16 glyph, base;
		if(ch >= 'A' && ch <= 'Z'){ glyph = ch - 'A'; }
		else if(ch >= '0' && ch <= '9'){ glyph = 26 + ch - '0'; }
		else { col += 2; continue; }
		base = sHudMessageTileBase + glyph * 2;
		sHudComboMap[col] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, base);
		sHudComboMap[col+1] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, base+1);
		sHudComboMap[row * 40 + col] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, base);
		sHudComboMap[row * 40 + col + 1] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, base+1);
		sHudComboMap[(row + 1) * 40 + col] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, base+72);
		sHudComboMap[(row + 1) * 40 + col + 1] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, base+73);
		col += 2;
	}
}

static void hud_combo_clear(void)
{
	memset(sHudComboMap, 0, sizeof(sHudComboMap));
	/* Combo text is a transient, two-row overlay.  Keep it out of the
	   per-frame DMA queue: the queue is shared with sprite tile uploads and
	   can otherwise push the NTSC worst frame over the VBlank envelope. */
	VDP_setTileMapDataRect(HUD_PLANE, sHudComboMap, 0, HUD_COMBO_ROW, 40, HUD_COMBO_ROWS, 40, CPU);
	sHudComboValue = 0xFF;
	sHudComboPlayer = 0;
}

static void hud_combo_update(void)
{
	u8 p1 = P[1].hitCounter;
	u8 p2 = P[2].hitCounter;
	u8 player = (p1 >= p2) ? 1 : 2;
	u8 value = (player == 1) ? p1 : p2;
	char text[] = "00 HITS";
	const u16 col = (player == 1) ? 1 : 25;
	if(!gConfig.hudHitCount){ if(sHudComboValue != 0){ hud_combo_clear(); sHudComboValue = 0; } return; }
	if(value < 2)
	{
		if(sHudComboValue != 0){ hud_combo_clear(); sHudComboValue = 0; }
		return;
	}
	if(value > 99){ value = 99; }
	if(value < 10){ text[0] = ' '; text[1] = '0' + value; }
	else { text[0] = '0' + (value / 10); text[1] = '0' + (value % 10); }
	if(value == sHudComboValue && player == sHudComboPlayer){ return; }
	memset(sHudComboMap, 0, sizeof(sHudComboMap));
	/* The combo is an attacker-owned callout: it lives above the fighter
	   lanes and is anchored to the attacking side instead of crossing the
	   silhouettes at the old centered row.  The first line gives the event
	   a visual identity; the second line carries the exact count. */
	hud_combo_line("RUSH", col + ((player == 1) ? 0 : 6), 0);
	hud_combo_line(text, col, 2);
	VDP_setTileMapDataRect(HUD_PLANE, sHudComboMap, 0, HUD_COMBO_ROW, 40, HUD_COMBO_ROWS, 40, CPU);
	sHudComboValue = value;
	sHudComboPlayer = player;
}

static void hud_window_draw_clock(void)
{
	s8 left;
	s8 right;

	if(!sHudWindowActive){ return; }

	/* Esconder e so apresentacao: gClockLTimer/gClockRTimer continuam correndo
	   e o time-over continua valendo. */
	{
		SpriteVisibility v = gConfig.hudTimer ? VISIBLE : HIDDEN;
		if(sHudClockSpriteL){ SPR_setVisibility(sHudClockSpriteL, v); }
		if(sHudClockSpriteR){ SPR_setVisibility(sHudClockSpriteR, v); }
	}

	left = (s8)hud_clock_digit(gClockLTimer);
	right = (s8)hud_clock_digit(gClockRTimer);
	if(left == sHudClockDigitL && right == sHudClockDigitR){ return; }
	sHudClockDigitL = left;
	sHudClockDigitR = right;
	hud_window_put_digit(0, (u8)left);
	hud_window_put_digit(1, (u8)right);
}

/* TIMER BG é uma moldura compacta opcional, nunca uma faixa WINDOW global.
   O relógio ocupa as colunas 18..21; seis colunas por duas linhas dão apenas
   uma margem de 8 px e deixam o cenário visível no restante da tela. */
static void hud_clock_background_update(void)
{
	u8 row;
	u8 col;
	if(!sHudWindowActive){ return; }
	if(sHudClockBgState == (u8)gConfig.hudTimerBg){ return; }
	for(row = 0; row < 2; row++)
	{
		for(col = 0; col < HUD_CLK_BG_COLS; col++)
		{
			VDP_setTileMapXY(HUD_PLANE,
				gConfig.hudTimerBg ? TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, sHudBlackTile) : 0,
				HUD_CLK_BG_X + col, HUD_CLK_BG_ROW + row);
		}
	}
	sHudClockBgState = (u8)gConfig.hudTimerBg;
}

static void hud_life_track_draw(u8 player)
{
	u8 col;
	u8 base = (player == 0) ? HUD_FRAME_P1_COL : HUD_FRAME_P2_COL;
	for(col = 0; col < 16; col++)
	{
		u8 sourceCol;
		if(col == 0u){ sourceCol = (player == 0) ? 0u : 2u; }
		else if(col == 15u){ sourceCol = (player == 0) ? 2u : 0u; }
		else { sourceCol = 1u; }
		u16 tile = (u16)(sHudLifeTrackTileBase + sourceCol);
		VDP_setTileMapXY(HUD_PLANE,
			TILE_ATTR_FULL(PAL1, TRUE, FALSE, player != 0, tile),
			base + col, HUD_BAR_ROW);
	}
}

static void hud_life_track_clear(u8 player)
{
	const u8 base = (player == 0) ? HUD_FRAME_P1_COL : HUD_FRAME_P2_COL;
	VDP_fillTileMapRect(HUD_PLANE, 0, base, HUD_BAR_ROW, 16, 1);
}

static void hud_life_track_update(void)
{
	u8 enabled = gConfig.hudLifeBar ? 1u : 0u;
	if(sHudLifeTrackVisible == enabled){ return; }
	if(enabled)
	{
		hud_life_track_draw(0);
		hud_life_track_draw(1);
	}
	else
	{
		hud_life_track_clear(0);
		hud_life_track_clear(1);
	}
	sHudLifeTrackVisible = enabled;
}

static void hud_draw_life_bar(u8 player, s8 energy)
{
	Sprite *sprite = (player == 0) ? sHudLifeBarP1 : sHudLifeBarP2;
	u16 e = (energy < 0) ? 0u : (energy > 96 ? 96u : (u16)energy);
	u8 frame = (e == 0u) ? 12u : (u8)(11u - (((u32)e * 11u + 95u) / 96u));
	if(!gConfig.hudLifeBar){ frame = 12u; }
	if(sprite){ SPR_setFrame(sprite, frame); }
}

	/* A barra de especial usa uma família azul autoral derivada do mesmo
	   segmento, mas com índice de acento distinto no PAL1. Fica no rodapé para
	   não parecer uma segunda vida. */
static u8 hud_special_count(s8 energy)
{
	u16 e = (energy < 0) ? 0 : (energy > 32 ? 32 : (u16)energy);
	return (u8)((e * HUD_BAR_SEGMENTS + 31) / 32);
}

static void hud_draw_special(u8 player, u8 count)
{
	u8 i;
	u8 base = (player == 0) ? HUD_SPECIAL_P1_COL : HUD_SPECIAL_P2_COL;
	u8 reverse = (player != 0);
	if(!gConfig.hudSpecialBar){ count = 0; }
	for(i = 0; i < HUD_BAR_SEGMENTS; i++)
	{
		u8 logical = reverse ? (HUD_BAR_SEGMENTS - 1 - i) : i;
		u16 tile = (i < count) ? sHudSpecialFilledTileBase : sHudSpecialTileBase;
		VDP_setTileMapXY(HUD_PLANE, TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, tile),
			base + logical * 2, HUD_SPECIAL_ROW);
		VDP_setTileMapXY(HUD_PLANE, TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE,
			i < count ? (u16)(tile + 1u) : 0u),
			base + logical * 2 + 1, HUD_SPECIAL_ROW);
	}
}

/* Life bars are plane-owned now; invalidate only the special strip when a
   fighter resource changes and the scene is rebuilt. */
static void hud_sync_segment_tile(void)
{
	sHudSpecialCount[0] = -1;
	sHudSpecialCount[1] = -1;
}

void hud_window_init(void)
{
	const u16 autoFlags = SPR_FLAG_DISABLE_DELAYED_FRAME_UPDATE | SPR_FLAG_AUTO_VISIBILITY |
		SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD;

	memset(sHudP1Segments, 0, sizeof(sHudP1Segments));
	memset(sHudP2Segments, 0, sizeof(sHudP2Segments));
	memset(sHudP1Damage, 0, sizeof(sHudP1Damage));
	memset(sHudP2Damage, 0, sizeof(sHudP2Damage));
	memset(sHudPortrait, 0, sizeof(sHudPortrait));
	sHudKoBanner = NULL;
	/* One pre-rendered 128px frame per fighter replaces sixteen independent
	   life-cell links. The authored frame strip stays readable while freeing
	   the SAT for fighter metasprites and transient impact/KO art. */
	sHudLifeBarP1 = SPR_addSpriteExSafe(&spr_hud_energy_y, HUD_P1_X, HUD_BAR_Y,
		TILE_ATTR(PAL1, FALSE, FALSE, FALSE), autoFlags);
	sHudLifeBarP2 = SPR_addSpriteExSafe(&spr_hud_energy_y_p2, HUD_P2_X, HUD_BAR_Y,
		TILE_ATTR(PAL1, FALSE, FALSE, FALSE), autoFlags);
	if(!sHudLifeBarP1 || !sHudLifeBarP2){ SYS_die("HUD life bar allocation failed"); return; }
	SPR_setDepth(sHudLifeBarP1, 3);
	SPR_setDepth(sHudLifeBarP2, 3);
	sHudClockSpriteL = SPR_addSpriteExSafe(&spr_hud_clock_digit, HUD_CLK_L_X, HUD_CLK_Y,
		TILE_ATTR(PAL1, FALSE, FALSE, FALSE), autoFlags);
	if(!sHudClockSpriteL){ SYS_die("HUD clock sprite allocation failed"); return; }
	sHudClockSpriteR = SPR_addSpriteExSafe(&spr_hud_clock_digit, HUD_CLK_R_X, HUD_CLK_Y,
		TILE_ATTR(PAL1, FALSE, FALSE, FALSE), autoFlags);
	if(!sHudClockSpriteR){ SYS_die("HUD clock sprite allocation failed"); return; }
	if(sHudClockSpriteL){ SPR_setDepth(sHudClockSpriteL, 3); }
	if(sHudClockSpriteR){ SPR_setDepth(sHudClockSpriteR, 3); }
	sHudPortrait[0] = SPR_addSpriteExSafe(hud_portrait_definition(P[1].id), 0, 0,
		TILE_ATTR(PAL2, FALSE, FALSE, FALSE), autoFlags);
	sHudPortrait[1] = SPR_addSpriteExSafe(hud_portrait_definition(P[2].id), 288, 0,
		TILE_ATTR(PAL3, FALSE, FALSE, FALSE), autoFlags);
	if(!sHudPortrait[0] || !sHudPortrait[1]){ SYS_die("HUD portrait allocation failed"); return; }
	SPR_setHFlip(sHudPortrait[1], TRUE);
	SPR_setDepth(sHudPortrait[0], 4);
	SPR_setDepth(sHudPortrait[1], 4);
	/* KO is a transient result layer.  Do not reserve its 12x6 metasprite
	   during the whole fight; instantiate it only for the KO message. */
	sHudKoBanner = NULL;
	sHudClockDigitL = -1;
	sHudClockDigitR = -1;
	sHudSpecialCount[0] = -1;
	sHudSpecialCount[1] = -1;
	sHudSpecialEnabled = 0xFF;
	sHudClockBgState = 0xFF;
	sHudLifeTrackVisible = 0xFF;
	sHudWindowActive = 1;
	PAL_setColors(16u + 15u, &kHudIdentityWhite, 1u, CPU);
	PAL_setColors(16u + 14u, &kHudSpecialBrightColor, 1u, CPU);
	/* Keep the special meter label tied to each fighter's authored accent
	   palette; PAL1 index 11 is black on the dark lower strip. */
	hud_draw_text("SP", HUD_SPECIAL_P1_COL, HUD_SPECIAL_LABEL_ROW);
	hud_draw_text("SP", HUD_SPECIAL_P2_COL + 1, HUD_SPECIAL_LABEL_ROW);
	hud_window_update();
	hud_identity_update();
	hud_combo_update();
	hud_window_draw_clock();
}

void hud_window_update(void)
{
	if(!sHudWindowActive){ return; }
	hud_sync_segment_tile();
	hud_identity_update();
	hud_clock_background_update();
	hud_life_track_update();
	/* The authored frame strip is the canonical life read. */
	hud_draw_life_bar(0, P[1].energiaBase);
	hud_draw_life_bar(1, P[2].energiaBase);
	{
		u8 c1 = hud_special_count(P[1].energiaSP);
		u8 c2 = hud_special_count(P[2].energiaSP);
		if(c1 != (u8)sHudSpecialCount[0] || sHudSpecialEnabled != (u8)gConfig.hudSpecialBar){ hud_draw_special(0, c1); sHudSpecialCount[0] = (s8)c1; }
		if(c2 != (u8)sHudSpecialCount[1] || sHudSpecialEnabled != (u8)gConfig.hudSpecialBar){ hud_draw_special(1, c2); sHudSpecialCount[1] = (s8)c2; }
		sHudSpecialEnabled = (u8)gConfig.hudSpecialBar;
	}
}

void hud_window_off(void)
{
	u8 i;
	hud_message_clear();
	hud_combo_clear();
	for(i = 0; i < HUD_BAR_SEGMENTS; i++)
	{
		if(sHudP1Segments[i]){ SPR_releaseSprite(sHudP1Segments[i]); sHudP1Segments[i] = NULL; }
		if(sHudP2Segments[i]){ SPR_releaseSprite(sHudP2Segments[i]); sHudP2Segments[i] = NULL; }
		if(sHudP1Damage[i]){ SPR_releaseSprite(sHudP1Damage[i]); sHudP1Damage[i] = NULL; }
		if(sHudP2Damage[i]){ SPR_releaseSprite(sHudP2Damage[i]); sHudP2Damage[i] = NULL; }
	}
	if(sHudLifeBarP1){ SPR_releaseSprite(sHudLifeBarP1); sHudLifeBarP1 = NULL; }
	if(sHudLifeBarP2){ SPR_releaseSprite(sHudLifeBarP2); sHudLifeBarP2 = NULL; }
	hud_life_track_clear(0);
	hud_life_track_clear(1);
	if(sHudClockSpriteL){ SPR_releaseSprite(sHudClockSpriteL); sHudClockSpriteL = NULL; }
	if(sHudClockSpriteR){ SPR_releaseSprite(sHudClockSpriteR); sHudClockSpriteR = NULL; }
	if(sHudPortrait[0]){ SPR_releaseSprite(sHudPortrait[0]); sHudPortrait[0] = NULL; }
	if(sHudPortrait[1]){ SPR_releaseSprite(sHudPortrait[1]); sHudPortrait[1] = NULL; }
	if(sHudKoBanner){ SPR_releaseSprite(sHudKoBanner); sHudKoBanner = NULL; }
	sHudWindowActive = 0;
	sHudClockDigitL = -1;
	sHudClockDigitR = -1;
	sHudSpecialCount[0] = -1;
	sHudSpecialCount[1] = -1;
	sHudSpecialEnabled = 0xFF;
	sHudClockBgState = 0xFF;
	sHudLifeTrackVisible = 0xFF;
	sHudFighterId[0] = 0xFF; sHudFighterId[1] = 0xFF;
	sHudWins[0] = 0xFF; sHudWins[1] = 0xFF;
}

/* Atlas cells are 16x16 (2x2 tiles), 36 cells across in ROW order.
   PAL1 belongs to the HUD; fighter palettes can change independently. */
static void hud_message_line(const char *str, u16 row)
{
	u16 col = (40 - strlen(str) * 2) / 2;
	while(*str)
	{
		u8 ch = *str++;
		u16 glyph;
		u16 base;
		if(ch >= 'A' && ch <= 'Z'){ glyph = ch - 'A'; }
		else if(ch >= '0' && ch <= '9'){ glyph = 26 + ch - '0'; }
		else { col += 2; continue; }
		base = sHudMessageTileBase + glyph * 2;
		sHudMessageMap[(row-HUD_MESSAGE_ROW)*40+col] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, base);
		sHudMessageMap[(row-HUD_MESSAGE_ROW)*40+col+1] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, base+1);
		sHudMessageMap[(row-HUD_MESSAGE_ROW+1)*40+col] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, base+72);
		sHudMessageMap[(row-HUD_MESSAGE_ROW+1)*40+col+1] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, base+73);
		col += 2;
	}
}

void hud_message_clear(void)
{
	hud_ko_banner_set(0);
	memset(sHudMessageMap, 0, sizeof(sHudMessageMap));
	VDP_setTileMapDataRect(HUD_PLANE, sHudMessageMap, 0, HUD_MESSAGE_ROW, 40, HUD_MESSAGE_ROWS, 40, CPU);
	sHudMessage = 0;
}

void hud_message_update(void)
{
	u8 message = 0;
	if(gRoom == SCENE_AFTER_MATCH){ message = (gWinnerID == 1) ? 7 : 8; }
	else if(gPauseKoTimer > 0 && gPauseKoTimer < 330){ message = 3; }
	else if(P[1].state == 611 || P[1].state == 612){ message = 4; }
	else if(P[2].state == 611 || P[2].state == 612){ message = 5; }
	else if(P[1].state == 615 && P[2].state == 615){ message = 6; }
	else if(gFrames < 180){ message = 1; }
	else if(gFrames < 300){ message = 2; }
	hud_ko_banner_set(message == 3);
	if(message == sHudMessage){ return; }
	memset(sHudMessageMap, 0, sizeof(sHudMessageMap));
	sHudMessage = message;
	if(!message){ hud_message_clear(); return; }
	/* Round/FIGHT/KO are overlaid on the stage with transparent cells.  The
	   old implementation filled a 36-column black strip for every transient
	   message, which visually interrupted the scene and was especially harsh
	   over the timer area.  Result screens keep their compact black panel so
	   the two-line rematch prompt remains readable. */
	if(message >= 7)
	{
		u16 row, col;
		for(row=0; row < HUD_MESSAGE_ROWS; row++)
			for(col=2; col<38; col++)
				sHudMessageMap[row*40+col] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, sHudBlackTile);
	}
	if(message == 1){
		char roundText[] = "ROUND 0";
		roundText[6] = '0' + ((gRound > 9) ? 9 : gRound);
		hud_message_line(roundText, HUD_MESSAGE_ROW);
	}
	if(message == 2){ hud_message_line("FIGHT", HUD_MESSAGE_ROW); }
	if(message == 3){ /* Authored sprite banner replaces the old atlas text. */ }
	if(message == 4 || message == 7){ hud_message_line("PLAYER 1 WINS", HUD_MESSAGE_ROW); }
	if(message == 5 || message == 8){ hud_message_line("PLAYER 2 WINS", HUD_MESSAGE_ROW); }
	if(message == 6){ hud_message_line("DRAW", HUD_MESSAGE_ROW); }
	if(message >= 7){
		hud_message_line("A REMATCH", HUD_MESSAGE_ROW+2);
		hud_message_line("START SELECT", HUD_MESSAGE_ROW+4);
	}
	VDP_setTileMapDataRect(HUD_PLANE, sHudMessageMap, 0, HUD_MESSAGE_ROW, 40, HUD_MESSAGE_ROWS, 40, CPU);
}

void FUNCAO_BARRAS_DE_ENERGIA()
{
	
	for(i=1; i<=2; i++)
	{
		if( P[i].energia != P[i].energiaBase )
		{ 
			if(P[i].energia > P[i].energiaBase){ P[i].energia--; } //decrementa a 'energia' aos poucos, até igualar a 'energiaBase'
			if(P[i].energia < P[i].energiaBase){ P[i].energia++; } //incrementa a 'energia' aos poucos, até igualar a 'energiaBase'
		} 
		
		/* P1/P2 vida usam células compactas; a barra de especial é atualizada
		   uma vez abaixo no plano BG_A. */
		
	}

	hud_window_update();
	hud_combo_update();
	
}
