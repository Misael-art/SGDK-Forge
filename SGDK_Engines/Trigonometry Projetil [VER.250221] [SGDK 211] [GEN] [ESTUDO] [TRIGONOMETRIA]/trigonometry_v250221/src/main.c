
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                                                                                                                                  //
// --------------------------------------  ESTUDO DE TRIGONOMETRIA by GAMEDEVBOSS, SGDK 2.0  -------------------------------------- //
//                                                                                                                                  //
// TRG_FIND_ANGLE(fix16 p1x, fix16 p1y, fix16 p2x, fix16 p2y)                                                                       //
// retorna o Angulo entre 2 pontos no plano artesiano                                                                               //
//                                                                                                                                  //
// TRG_MXY_PAD(fix16 *x2, fix16 *y2, fix16 x1, fix16 y1, fix16 ang, fix16 dist)                                                     //
// projeta (move) a posicao X e Y de um objeto. Requer o xy do objeto, xy do ponto pivot, angulo e a distancia                      //
//                                                                                                                                  //
// TRG_MXY_PAD_EX(fix16 *x2, fix16 *y2, fix16 x1, fix16 y1, fix16 ang, fix16 dist, fix16 cosAdjustment, fix16 sinAdjustment)        //
// Faz o mesmo que o anterior, mas permite ajustar o modulo do Coseno e do Seno, influenciando o movimento orbital                  //
//                                                                                                                                  //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#include <genesis.h>
#include "trigonometric.h" //<< IMPORTANTE ADICIONAR !!!
#include "sprite.h"
#include "gfx.h"

//=== DEFINES =====================================================================================================================

//...

//=== VARIAVEIS ===================================================================================================================

// Definicao dos sprites
Sprite *OBJ1_sprite;
Sprite *OBJ2_sprite;
Sprite *OBJ3_sprite;

// Posicao OBJ1
fix16 OBJ1x = FIX16(160);
fix16 OBJ1y = FIX16(112);
fix16 OBJ1_distancia = FIX16(100);
fix16 OBJ1_angulo = FIX16(0); //<< 0  graus aponta para o lado direito

// Posicao OBJ2
fix16 OBJ2x = FIX16(160);
fix16 OBJ2y = FIX16(112);

fix16 OBJ3x = FIX16(-1);
fix16 OBJ3y = FIX16(-1);

fix16 OBJ3xCentro;
fix16 OBJ3yCentro;

fix16 OBJ3_distancia;
fix16 OBJ3_angulo;

u8 ExampleChoice = 2;

//=== FUNCOES =====================================================================================================================

//...

//=== MAIN ========================================================================================================================

void main()
{
    //Inicializacao da VDP (Video Display Processor)
	SYS_disableInts();
	VDP_init();                    // Inicializa a VDP (Video Display Processor)
	VDP_setScreenWidth320();       // Resolução padrão de 320x224 (Largura)
	VDP_setScreenHeight224();      // Resolução padrão de 320x224 (Altura)
	VDP_setPlaneSize(64,32,TRUE);  // Recomendado para BGs grandes "512 x 256 px"
	VDP_setTextPlane(BG_A);        // Textos serão desenhados no BG_A
	VDP_setTextPalette(PAL2);      // Textos serão desenhados com a última cor da PAL0
	SPR_initEx(500);               // SPR_initEx(u16 vramSize)
	VDP_setBackgroundColor(0);     // Cor de fundo
	SYS_enableInts();

	//carregar o background
	//VDP_loadTileSet(bg_bgb.tileset,0,DMA);
	//VDP_setTileMapEx(BG_B,bg_bgb.tilemap,TILE_ATTR_FULL(PAL0,FALSE,FALSE,FALSE,0),0,0,0,0,40,28,DMA_QUEUE);
	//PAL_setPalette(PAL0, bg_bgb.palette->data,DMA);

    // Carregamento dos Sprites
    OBJ1_sprite = SPR_addSprite(&spr_marker1, 320, 224, TILE_ATTR(PAL1, 0, 0, 0));
    OBJ2_sprite = SPR_addSprite(&spr_marker2, 320, 224, TILE_ATTR(PAL1, 0, 0, 0));

    OBJ3_sprite = SPR_addSprite(&spr_marker2, 320, 224, TILE_ATTR(PAL1, 0, 0, 0));

    PAL_setPalette(PAL1, spr_marker1.palette->data, DMA);

    // LOOP PRINCIPAL
    while(1)
    {
		//------------------------------------------------------------------------------------------------------------
		//JOY - CONTROLE

		//move OBJ1 com o controle 1
        if (JOY_readJoypad(JOY_1) & BUTTON_UP   ) { OBJ1y -= FIX16(1); }
		if (JOY_readJoypad(JOY_1) & BUTTON_DOWN ) { OBJ1y += FIX16(1); }
		if (JOY_readJoypad(JOY_1) & BUTTON_LEFT ) { OBJ1x -= FIX16(1); }
		if (JOY_readJoypad(JOY_1) & BUTTON_RIGHT) { OBJ1x += FIX16(1); }

		//move OBJ2 com o controle 2
		if (JOY_readJoypad(JOY_2) & BUTTON_UP   ) { OBJ2y -= FIX16(1); }
		if (JOY_readJoypad(JOY_2) & BUTTON_DOWN ) { OBJ2y += FIX16(1); }
		if (JOY_readJoypad(JOY_2) & BUTTON_LEFT ) { OBJ2x -= FIX16(1); }
		if (JOY_readJoypad(JOY_2) & BUTTON_RIGHT) { OBJ2x += FIX16(1); }

		// botao B do controle 1 dispara o projetil (OBJ3) do OBJ2
		if (JOY_readJoypad(JOY_1) & BUTTON_B    )
        {
            // OBJ2 = objeto que atira
            // OBJ1 = objeto player

            // angulo do OBJ3 que eh o angulo do OBJ2 em referencia ao OBJ1
            OBJ3_angulo = TRG_FIND_ANGLE(OBJ2x -FIX16(8) ,OBJ2y -FIX16(8) ,OBJ1x -FIX16(8) ,OBJ1y -FIX16(8) );
            // o motivo de ter o -FIX16(8) eh para alinhar com os centros dos objetos no jogo

            OBJ3xCentro = OBJ2x; // o objeto 3 parte do OBJ2
            OBJ3yCentro = OBJ2y; // o objeto 3 parte do OBJ2

            // zera a distancia do OBJ3
            OBJ3_distancia = FIX16(0);
        }

		//------------------------------------------------------------------------------------------------------------


		if ((OBJ3x > FIX16(0) || OBJ3x < FIX16(320)) &&
            (OBJ3y > FIX16(0) || OBJ3y < FIX16(224)))
        {
            OBJ3_distancia += FIX16(1); //soma mais 1 na distancia do OBJ3, desde que fique limitado a tela do jogo
        }

        // Sprites Position
        SPR_setPosition(OBJ1_sprite, F16_toInt(OBJ1x - FIX16(8)), F16_toInt(OBJ1y - FIX16(8))); // Atualiza a posição do sprite 1
        SPR_setPosition(OBJ2_sprite, F16_toInt(OBJ2x - FIX16(8)), F16_toInt(OBJ2y - FIX16(8))); // Atualiza a posição do sprite 2

        // foram criadas as variaveis CosValor e SinValor, a partir de adaptacao do codigo original
        // objetivo eh para obter apenas os valores de seno e cosseno
        OBJ3x = OBJ3xCentro+F16_mul(OBJ3_distancia, CosValor(OBJ3_angulo) );
        OBJ3y = OBJ3yCentro+F16_mul(OBJ3_distancia, SinValor(OBJ3_angulo) );

        SPR_setPosition(OBJ3_sprite, F16_toInt(OBJ3x - FIX16(8)), F16_toInt(OBJ3y - FIX16(8))); // Atualiza a posição do sprite 2

		// --- DEBUG, OPCIONAL --- //
		//char str[64];
		//sprintf(str, "OBJ3 Angulo: %03d", F16_toInt(OBJ3_angulo)); VDP_drawText(str, 1, 1);
		// --- DEBUG, OPCIONAL --- //

        // Atualiza a tela de sprites
        SPR_update();

        // Processo de VBlank
        SYS_doVBlankProcess();
    }
}
