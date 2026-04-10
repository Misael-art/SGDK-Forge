#include <genesis.h>

//variáveis
Sprite *score_digits[6] = {NULL, NULL, NULL, NULL, NULL, NULL}; // Para até 6 dígitos
int score = 000000; // Variável para armazenar a pontuação

// Declaração da função
void initializeScoreSprites();
void updateScoreSprite(int score);
void updateScore(int points);

// ---------------------------------------------------------------------------
void initializeScoreSprites() {
    for (int i = 0; i < 6; i++) {
        score_digits[i] = SPR_addSprite(&spr_score_number, 67 + (i * 8), 10, TILE_ATTR(PAL3, FALSE, FALSE, FALSE));
        SPR_setVRAMTileIndex(score_digits[i], 1456 + i); // Define a posição na VRAM
        SPR_setAnimAndFrame(score_digits[i], 0, 0); // Inicia todos os dígitos como 0
    }
}


void updateScoreSprite(int score) {
    int spriteFrame;
    int digitCount = 0; // Contador de dígitos

    // Converte a pontuação em uma string para iterar sobre os dígitos
    char scoreStr[7]; // Para até 6 dígitos + 1 para o terminador
    sprintf(scoreStr, "%06d", score); // Formata a pontuação com zeros à esquerda

    // Limpa sprites existentes
    for (int i = 0; i < 6; i++) {
        if (score_digits[i]) {
            SPR_releaseSprite(score_digits[i]);
            score_digits[i] = NULL;
        }
    }

    // Adiciona cada dígito como um sprite
    for (int i = 0; i < strlen(scoreStr) && digitCount < 6; i++) {
        int digit = scoreStr[i] - '0'; // Converte o caractere para inteiro
        spriteFrame = digit; // O quadro do sprite é o próprio dígito

        // Adiciona o sprite do número na posição correta
        score_digits[digitCount] = SPR_addSprite(&spr_score_number, 67 + (digitCount * 8), 10, TILE_ATTR(PAL3, FALSE, FALSE, FALSE));

        // Define a posição específica na VRAM para cada dígito
        SPR_setVRAMTileIndex(score_digits[digitCount], 1456 + digitCount); // 1456 + índice do dígito
        SPR_setAnimAndFrame(score_digits[digitCount], 0, spriteFrame); // 0 é a animação, digit é o quadro
        digitCount++;
    }

    SPR_update(); // Atualiza a tela com os sprites adicionados
}

void updateScore(int points) {
    score += points; // Atualiza a pontuação

    // Limita a pontuação a 999999
    if (score > 999999) {
        score = 999999;
    }
    updateScoreSprite(score); // Atualiza os sprites com base na nova pontuação
}

// ---------------------------------------------------------------------------

int main(bool hardReset) //--- MAIN ---//
{

    SYS_disableInts();
     VDP_init();
     VDP_setScreenWidth320();
     VDP_setScreenHeight224();
    SYS_enableInts();
    initializeScoreSprites();// inicializa o score com pontuação 000000
    
}

/* Exemplo de uso:  //coloque essa função na parte do seu jogo que vc gostaria que fosse gerado um score, tipo ao derrotar um inimigo, ou recolher um item, etc..
updateScore(1) aumenta no score 1  ponto
updateScore(10);aumenta no score 10  pontos
updateScore(15);aumenta no score 15  pontos
updateScore(100);aumenta no score 100  pontos*/

//-------------------------------------------------------------\\

coloque no arquivo sprite.res:
SPRITE spr_score_number "sprite/score_number.png"  1  1 NONE 0 