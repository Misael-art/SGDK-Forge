/**
 * @file cenarios.h
 * @author Paulo Linhares 
 * @version 0.1
 * @date 2022-06-03
 * 
 * @copyright Copyright (c) 2023
 * 
 * 
 * Para utilizar essa biblioteca você deve criar as imagens dos cenarios
 * com os frames sobrepostos entao se o cenario tiver 512x240 e dois frames
 * a imagem ficara com tamanho 512x480.
 */

#ifndef __CENARIOS_H__
#define __CENARIOS_H__

#include <genesis.h>
#include "commun.h"


/**
 * @brief lista de cenarios
 * 
 */
enum CENARIOS{
    CENARIO_7_1 =1,
    CENARIO_LONDON,
    CENARIO_KOREA,
    CENARIO_GEESE,
    CENARIO_KRAUZER,
    CENARIO_MAI,
    CENARIO_JOE,
    CENARIO_TOTAL,
};
/**
 * @brief Anima o cenario escolhido
 * 
 * @param gBG_Choice cemario escolhido 
 * @param ping se ping == 9 então muda o frame do cenario
 */
void CEN_Anima(enum CENARIOS gBG_Choice, u8 ping);

/**
 * @brief Anima o cenario
 * 
 * @param x posição x do plano
 * @param y posição y do plano
 * @param x_len compimento no eixo x
 * @param y_len comprimento no eixo y
 * @param frames_num numéro de frames da animação
 */
void CEN_AnimaEx(u16 x, u16 y, u16 x_len, u16 y_len, u8 frames_num);

/**
 * @brief inicia a animação do cenario
 * 
 * @param gBG_Choice cenário escolhido
 * @return u16 total de tiles do cenario 
 */
u16 CEN_init( enum CENARIOS gBG_Choice);

#endif