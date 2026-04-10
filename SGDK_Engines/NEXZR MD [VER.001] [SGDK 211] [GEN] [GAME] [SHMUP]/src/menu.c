#include "menu.h"
#include "game.h"
#include "i18n.h"
#include "level_1.h"

typedef enum {
  GAME_START,
  CARNIVAL_MODE,
  OPTIONS
} menu_options_main;

typedef enum {
  LANGUAGE,
  MD_MODE,
  DIFFICULTY,
  CREDITS,
  BACK
} menu_options_secondary;

typedef enum {
  MAIN,
  SECONDARY
} menus;

u8 option_selected = GAME_START;
u8 menu_current = MAIN;

void drawMainMenu();
void drawMainBackground();
void print_options();
void handleMainMenu(u16 joy, u16 changed, u16 state);
void joyMenuHandler(u16 joy, u16 changed, u16 state);
void redrawMainMenu();
void drawSecondaryBackground();
void drawMenuSecondary();
void handleSecondaryMenu(u16 joy, u16 changed, u16 state);

void Menu_init() {
    drawMainMenu();
 	Game_setJoyHandler(&joyMenuHandler);
}

void drawMainMenu() {
  	Game_resetScreen();

// tem q ter essa ordem desenha a imagem na paleta preta e comeca o fate depois carreg aa palheta
 	drawMainBackground();
 	// funciona na PAL0
 	PAL_fadeIn(0, 63, titlescreen.palette->data, 20, FALSE);
 	PAL_setPalette(BACKGROUND_PALLETE, titlescreen.palette->data, DMA);

	while (PAL_isDoingFade())
		SYS_doVBlankProcess();

 	Characters_prepareToPrint();
	redrawMainMenu();
}
// To deixando no BG_B pra botar o paralax das estrelas caindo no fundo como no original
void drawMainBackground() {
//  	PAL_setPalette(BACKGROUND_PALLETE, titlescreen.palette->data, DMA);
	VDP_drawImageEx(BG_B,
                  &titlescreen,
                  TILE_ATTR_FULL(BACKGROUND_PALLETE, FALSE, FALSE, FALSE, TILE_USER_INDEX),
                  GAME_WINDOW_START_POSITION_LEFT,
                  GAME_WINDOW_START_POSITION_TOP,
                  FALSE,
                  TRUE);
}

void joyMenuHandler(u16 joy, u16 changed, u16 state) {
  if (menu_current == MAIN) {
 	handleMainMenu(joy, changed, state);

  } else if (menu_current == SECONDARY) {
 	handleSecondaryMenu(joy, changed, state);

  }
}

void handleMainMenu(u16 joy, u16 changed, u16 state) {
  if (joy == JOY_1) {
  	if (changed & state & BUTTON_DOWN) {
    	if (option_selected < OPTIONS) option_selected++;
    }
    if (changed & state & BUTTON_UP) {
    	if (option_selected > GAME_START) option_selected--;
    }
 	if (changed & state & BUTTON_START) {
   		if (option_selected == OPTIONS) {
		  menu_current = SECONDARY;
    	  option_selected = LANGUAGE;
		  VDP_clearPlane(BG_B, TRUE);
    	  drawMenuSecondary();

		  return;
  		}
  		else if (option_selected == GAME_START) {
    		PAL_fadeOut(0, 63, 40, FALSE);

		   while (PAL_isDoingFade())
				SYS_doVBlankProcess();

   			Level1_init();
   			return;
  		}
 	}

 	redrawMainMenu();
  }
}

void redrawMainMenu() {
	Characters_print(TXT_START, game_options.language == LANG_EN ? 15 : 17, 13, option_selected == GAME_START ? FONT_ACTIVE : FONT_INACTIVE);
	Characters_print("CARNIVAL MODE!", 13, 15, option_selected == CARNIVAL_MODE ? FONT_ACTIVE : FONT_INACTIVE);
	Characters_print(TXT_OPTIONS, 17, 17, option_selected == OPTIONS ? FONT_ACTIVE : FONT_INACTIVE);
}

void handleSecondaryMenu(u16 joy, u16 changed, u16 state) {
  if (joy == JOY_1) {
  	if (changed & state & BUTTON_DOWN) {
    	if (option_selected < BACK) option_selected++;
    }
    if (changed & state & BUTTON_UP) {
    	if (option_selected > LANGUAGE) option_selected--;
    }
 	if (changed & state & BUTTON_START) {
   		if (option_selected == BACK) {
		  menu_current = MAIN;
    	  option_selected = GAME_START;

    	  drawMainMenu();
		  return;
  		}
  		else if (option_selected == LANGUAGE) {
    		game_options.language = game_options.language > 1 ? 0 : game_options.language + 1;
			I18N_setLanguage(game_options.language);
   			VDP_clearPlane(BG_B, TRUE);
  		}
  		else if (option_selected == MD_MODE) {
    		game_options.md_mode = !game_options.md_mode;
   			VDP_clearPlane(BG_B, TRUE);
  		}
 	}

 	drawMenuSecondary();
  }
}

void drawMenuSecondary() {

  	Characters_print(TXT_LANGUAGE, 5, 3, option_selected == LANGUAGE ? FONT_ACTIVE : FONT_INACTIVE);
	Characters_print("MD MODE", 5, 6, option_selected == MD_MODE ? FONT_ACTIVE : FONT_INACTIVE);
	Characters_print(TXT_DIFFICULTY, 5, 9, option_selected == DIFFICULTY ? FONT_ACTIVE : FONT_INACTIVE);
 	Characters_print(TXT_CREDITS, 5, 12, option_selected == CREDITS ? FONT_ACTIVE : FONT_INACTIVE);
 	Characters_print(TXT_BACK, 5, 18, option_selected == BACK ? FONT_ACTIVE : FONT_INACTIVE);

 	Characters_print(TXT_CURRENT_LANGUAGE, 20, 3, option_selected == LANGUAGE ? FONT_ACTIVE : FONT_INACTIVE);
	Characters_print(game_options.md_mode ? TXT_ON : TXT_OFF, 20, 6, option_selected == MD_MODE ? FONT_ACTIVE : FONT_INACTIVE);
	Characters_print("NORMAL", 20, 9, option_selected == DIFFICULTY ? FONT_ACTIVE : FONT_INACTIVE);
}