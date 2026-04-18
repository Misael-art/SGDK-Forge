#include <genesis.h>
#include "resources.h"

// Função para mapear o caractere para o índice da tile no tileset
size_t getCharacterTile(char character) {
    char characters[] = {
        ' ', '!', '?', '#', '$', '%', '¨', '&', '*', '(', ')', '-', '+', ',', '.', '/',
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', 'á', 'é', 'í', 'ó',
        'ú', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
        'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', 'Ç', 'ç',
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
        'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'ã', 'õ', 'â', 'ê', 'ô', 'ñ'
    };

    size_t index = -1;

    // Busca o índice do caractere na tabela
    for (size_t i = 1; i < sizeof(characters) / sizeof(characters[0]); i++) {
        if (characters[i] == character) {
            index = i;
            break;
        }
    }

    return index;  // Retorna o índice do caractere no tileset (0 a 95)
}

// Função para desenhar um caractere com seu tileset
void drawCharacter(int x, int y, char character) {
    size_t tileIndex = getCharacterTile(character);  // Obtém o índice do caractere no seu tileset

    if (tileIndex != (size_t)-1) {
        // Ajusta o índice com base no endereço de memória correto para o tileset
        u16 adjustedIndex = 0x5A0 + tileIndex;  // Adiciona o deslocamento para o início do tileset

        // Usamos a função VDP_setTileMapXY para desenhar o tile no mapa de fundo (ou onde for necessário)
        VDP_setTileMapXY(BG_A, adjustedIndex, x, y);  // Ajuste para renderizar o tile corretamente no plano de fundo A
    }
}

// Função para desenhar texto com quebra de linha
void drawText(int x, int y, const char* text) {
    int currentX = x;
    int currentY = y;

    // Itera sobre cada caractere da string
    for (int i = 0; text[i] != '\0'; i++) {
        // Verifica se encontrou a sequência de quebra de linha "/n"
        if (text[i] == '/' && text[i + 1] == 'n') {
            currentX = x;     // Volta para a primeira coluna
            currentY += 1;    // Move para a linha abaixo
            i++;  // Pula o 'n' após o '/'
        } else {
            drawCharacter(currentX, currentY, text[i]);
            currentX += 1;  // Move para a direita

            if (currentX >= 40) {  // Verifica a quebra de linha após 40 caracteres
                currentX = x;  // Volta para a primeira coluna
                currentY += 1;  // Move para a linha abaixo
            }
        }
    }
}

// Carrega uma fonte alternativa para o jogo
void initFont(const TileSet *font_tileset, u8 palette_num) {
    // Carrega o tileset da fonte usando o tipo correto
    VDP_loadFont(font_tileset, DMA);

    // Define a paleta de texto
    VDP_setTextPalette(palette_num);  // Usa a paleta especificada pelo número
}

// Exibir uma mensagem
void showMessage() {
    // Carrega a Font alternativa
    initFont(&customFont, 0);

    // Exibir o texto "Ola, Mundo!" na posição (4, 2)
    drawText(4, 10, "Olá, Mundo! /nenfrentarão os Gêmeos /nCAÇA,Pivô, Pavê, /nRústico, Poço, Anã, /nVânia ");  // Aqui você pode mudar o texto para o que quiser
}

int main() {
    // Inicializa a tela
    VDP_setScreenWidth320();
    VDP_setScreenHeight224();

    PAL_setPalette(PAL0, customFont_PAL.data, DMA); // Carrega a paleta associada

    // Chamar a função para exibir a mensagem
    showMessage();

    while (1) {
        // Sincroniza com o VBlank
        SYS_doVBlankProcess(); // Atualiza a tela de forma eficiente
    }

    return 0;
}
