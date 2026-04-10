#include <genesis.h>
#include "resource.h"
#include "main.h"

int main() {
	datas Data;

    // VDPアクセス時の割り込みを無効にする
    SYS_disableInts();

    // initialization
    VDP_setScreenWidth320();
    VDP_setPlaneSize(64, 32, TRUE);
    SPR_init();

//    VDP_setWindowHPos(FALSE, 0);
//    VDP_setWindowVPos(FALSE, 6);
//    VDP_setTextPlane(VDP_WINDOW);
//    VDP_setTextPriority(TRUE);

    // BGMの初期化
    SND_PCM4_setVolume(
            SOUND_PCM_CH1, // @suppress("Symbol is not resolved")
            15    // Volume to set : 16 possible level from 0 (minimum) to 15 (maximum).
    );
    SND_PCM4_setVolume(
            SOUND_PCM_CH2, // @suppress("Symbol is not resolved")
            15    // Volume to set : 16 possible level from 0 (minimum) to 15 (maximum).
    );
    SND_PCM4_setVolume(
            SOUND_PCM_CH3, // @suppress("Symbol is not resolved")
            15    // Volume to set : 16 possible level from 0 (minimum) to 15 (maximum).
    );
    SND_PCM4_setVolume(
            SOUND_PCM_CH4, // @suppress("Symbol is not resolved")
            15    // Volume to set : 16 possible level from 0 (minimum) to 15 (maximum).
    );

    // いったん暗くする
	PAL_fadeOut(0,63,1,FALSE); // @suppress("Symbol is not resolved")

	SYS_enableInts();

    Data.gm = LOGO;

    while(1) {
        switch ( Data.gm ) {
        case LOGO:
            Data = logo(Data);
            break;
        case TITLE:
        	Data = title(Data);
            break;
        case DAY:
        	Data = day(Data);
        	break;
        case AFTERDAY:
        	Data = afterDay(Data);
        	break;
        case INIT:
        	Data = init(Data);
        	break;
        case GAME:
        	Data = game(Data);
            break;
        case WORK:
        	Data = work(Data);
        	break;
        case HOW_TO_PLAY:
        	Data = howToPlay(Data);
        	break;
        case GAME_CLEAR:
        	Data = gameClear(Data);
        	break;
        case GAME_OVER:
        	Data = gameOver(Data);
        	break;
        }

    	// 後処理

    	// スプライトは先に消さないとフェードアウト時に残ったように見える
    	s16 i = 0;
    	for (i = 0; i < SPRITE_NUM; i++) {
    		SPR_releaseSprite(sprites[i]);
    	}
    	SPR_update();

    	fadeOut();

    	VDP_clearPlane(BG_A, TRUE); // @suppress("Symbol is not resolved")
    	VDP_clearPlane(BG_B, TRUE); // @suppress("Symbol is not resolved")
    	VDP_setHorizontalScroll(BG_B, 0);
    	VDP_setVerticalScroll(BG_B, 0);
    	VDP_setHorizontalScroll(BG_A, 0);
    	VDP_setVerticalScroll(BG_A, 0);
    }

	return (0);
}
