#include <genesis.h>
#include <string.h>
#include "sprites.h"

#define ANIM_RUN     0
#define ANIM_STAND   1
#define ANIM_JUMP    2
#define ANIM_DOWN    3
#define ANIM_ATTACK  4
#define ANIM_DASH    5
#define ANIM_CROUCH  6
#define ANIM_DEAD    7

#define ANIM_IDLE    0
#define ANIM_DANO    1
#define ANIM_MORTE   2
#define ANIM_ANDA    3
#define ANIM_ATAQUE  4

//ponteiros dos sprites
Sprite* player;
Sprite* inimigo;

//struct para as caixas de colisões
typedef struct {
    int x;
    int y;
    int w;
    int h;
} BoxCollider;

//strings para o texto na tela
int sign(int x)
{
    return (x > 0) - (x < 0);
}
//posição do player na tela
int playerPosition_x = 20;
int playerPosition_y = 168;
//posição do inimigo na tela
int inimigo_x = 160;
int inimigo_y = 160;
//variavel do tempo
u16 timer;
//variavel que ajuda na morte do player
bool isDead = FALSE;

int attack_timer = 0; // contador da animação do ataque
int attack_duration = 40; //tempo de duração em frames do ataque
bool ataque = FALSE; // variavel para verificar o ataque
bool ataqueLimite = TRUE; // variavel para verificar o ataque novamente
bool tomaDano = FALSE;//verifica que o player e o inimigo tomaram dano
bool inimigoMorto = FALSE;//variavel que identifica se o inimigo morreu ou não
bool moveLeft = FALSE; // mover o player para a esquerda
bool moveRight = FALSE; // mover o player para a direita
bool invulneravel = FALSE; // estado de invulnerável
int invulneravel_timer = 0; // contador do tempo de invencibilidade
int invulneravel_duration = 90; // Duração de 60 frames (1 segundo, considerando 60 FPS)

int inimigoLife = 5; // pontos de vida do inimigo
int playerLife = 4; // pontos de vida do player
char life_string[6] = "LIFE:"; // string do texto para o life do inimigo
char str_life[4] = "5"; // texto que aparece na tela do life do inimigo
char player_string[6] = "LIFE:"; //string do texto para o life do player
char str_lifePlayer[4] = "3"; // texto que aparece na tela do life do player

void colisao(); // função que verifica a colisao
void morteInimigo(); // função que é executada quando o inimigo morre
void mortePlayer(); // função que é executada quando o player morre
void invencivel(); // função da invencibilidade
void iniciarInvencibilidade(); // função que auxilia na invencibilidade

//função que atualiza os pontos de vida do inimigo na tela
void updateLifeInimigo()
{
    VDP_drawText(str_life, 32, 18);
    sprintf(str_life, "%d", inimigoLife);
    VDP_clearText(32, 18, 3);
    VDP_drawText(str_life, 32, 18);
}

//função que atualiza os pontos de vida do player na tela
void updateLifePlayer()
{
    VDP_drawText(str_lifePlayer, 16, 18);
    sprintf(str_lifePlayer, "%d", playerLife);
    VDP_clearText(16, 18, 3);
    VDP_drawText(str_lifePlayer, 16, 18);
}

//controlador do player na tela
static void handleInput()
{

    u16 value = JOY_readJoypad(JOY_1);

if(playerLife > 0) // a movimentação só irá funcionar se o player tiver mais do que 0 pontos de vida
{
    if (value & BUTTON_LEFT)
    {
        moveLeft = TRUE;
        moveRight = FALSE;
        playerPosition_x -= 2;
        SPR_setAnim(player, ANIM_RUN);
        SPR_setHFlip(player, TRUE);
    }
    else if (value & BUTTON_RIGHT)
    {
        moveLeft = FALSE;
        moveRight = TRUE;
        playerPosition_x += 2;
        SPR_setAnim(player, ANIM_RUN);
        SPR_setHFlip(player, FALSE);
    }
    else
    {
        moveLeft = FALSE;
        moveRight = FALSE;
    }

    if(!(value & BUTTON_LEFT) && !(value & BUTTON_RIGHT))
    {
       SPR_setAnim(player, ANIM_STAND);
    }
}

     SPR_setPosition(player, playerPosition_x, playerPosition_y);
}

//controlador do ataque do player
static void joyEvent(u16 joy, u16 changed, u16 state)
{
  if(playerLife > 0) // o ataque só é ativado se o player tiver mais que 0 pontos de vida
  {

    if ((changed & state & BUTTON_B) && attack_timer == 0)
    {
        SPR_setAnim(player, ANIM_ATTACK);
        attack_timer = 1;  // Inicia o temporizador de ataque
        ataque = TRUE;
        ataqueLimite = TRUE;  // Permite o ataque
    }

  }


}

//função que congela a animação do player morto na tela
static void playerFrameChanged2(Sprite* sprite)
{
    if (sprite->animInd == ANIM_DEAD)
    {
        // Quando a animação de morte terminar, "congelar" no último quadro
        if (sprite->frameInd == 8) {  // Último quadro da animação de morte
            isDead = TRUE;  // Marcar que o jogador morreu
            sprite->animInd = -1;  // Desativar animação, deixando o último quadro congelado
        }
    }
}

int main()
{
    //inicializa o motor de sprites
    SPR_init();
    JOY_setEventHandler(joyEvent); // inicializa o controlador
    //importação do player
    player = SPR_addSprite(&spr_player, playerPosition_x, playerPosition_y, TILE_ATTR(PAL2, 0, FALSE, FALSE));
    PAL_setPalette(PAL2, spr_player.palette->data, DMA);
    //importação do inimigo
    inimigo = SPR_addSprite(&spr_inimigo, inimigo_x, inimigo_y, TILE_ATTR(PAL3, 0, FALSE, TRUE));
    PAL_setPalette(PAL3, spr_inimigo.palette->data, DMA);
    //retorno de chamada da função anterior
    SPR_setFrameChangeCallback(player, playerFrameChanged2);

    VDP_setTextPlane(BG_A); // os textos serão exibidos no plano A
    VDP_drawText(life_string, 26, 18); // localização do texto na tela
    VDP_drawText(str_life, 32, 18); // localização do texto na tela
    VDP_drawText(player_string, 10, 18); // localização do texto na tela
    VDP_drawText(str_lifePlayer, 16, 18); // localização do texto na tela

    while(1)
    {
        if (attack_timer == 0)
            handleInput();
        else if (attack_timer > 0 && attack_timer < attack_duration)
            attack_timer++;
        else if (attack_timer == attack_duration)
        {
            attack_timer = 0;  // Reseta o temporizador de ataque
            ataque = FALSE;  // O ataque termina
        }

        if (playerPosition_x > inimigo_x && playerLife > 0) // toda vez que a posição do player foi maior que a posição do inimigo, o inimigo vira
            SPR_setHFlip(inimigo, FALSE);
        else
            SPR_setHFlip(inimigo, TRUE);

        SPR_update();
        colisao();
        morteInimigo();
        mortePlayer();
        invencivel();
        SYS_doVBlankProcess();
    }

    return 0;
}

//função que executa a invencibilidade do player
void invencivel()
{
    // Se o jogador estiver invulnerável, começa a lógica de invencibilidade
    if (invulneravel)
    {
        invulneravel_timer++;

        // Alterna a visibilidade do sprite para dar o efeito de piscar
        if (invulneravel_timer % 10 < 5)  // Pisca a cada 5 frames
        {
            SPR_setVisibility(player, HIDDEN);
        }
        else
        {
            SPR_setVisibility(player, VISIBLE);
        }

        // Desativa a invulnerabilidade quando o timer atinge a duração máxima
        if (invulneravel_timer >= invulneravel_duration)
        {
            invulneravel = FALSE;  // Fim da invulnerabilidade
            invulneravel_timer = 0; // Reseta o timer
            ataqueLimite = TRUE;
            tomaDano = FALSE;
            SPR_setVisibility(player, VISIBLE);  // Garante que o jogador fique visível
        }

        if(playerLife <= 0)
        {
            invulneravel = FALSE;
            SPR_setVisibility(player, VISIBLE);
        }
    }
}


void iniciarInvencibilidade()
{
    invulneravel = TRUE;
    invulneravel_timer = 0;  // Reinicia o timer quando a invulnerabilidade é ativada
    ataqueLimite = TRUE; // faz-se necessário para poder atacar enquanto estiver no modo invencível
}

//função da colisão
void colisao()
{
    BoxCollider sprt1Collider;
    sprt1Collider.x = player->x + 8;
    sprt1Collider.y = player->y + 4;
    sprt1Collider.w = 16;
    sprt1Collider.h = 16;

    BoxCollider sprt2Collider;
    sprt2Collider.x = inimigo->x + 8;
    sprt2Collider.y = inimigo->y + 4;
    sprt2Collider.w = 32;
    sprt2Collider.h = 32;

    s8 box1_x1 = sprt1Collider.x;
    s8 box1_y1 = sprt1Collider.y;
    s8 box1_x2 = sprt1Collider.x + sprt1Collider.w;
    s8 box1_y2 = sprt1Collider.y + sprt1Collider.h;

    s8 box2_x1 = sprt2Collider.x;
    s8 box2_y1 = sprt2Collider.y;
    s8 box2_x2 = sprt2Collider.x + sprt2Collider.w;
    s8 box2_y2 = sprt2Collider.y + sprt2Collider.h;

    // Verifica colisão entre o jogador e o inimigo
    if ((box1_x1 <= box2_x2) && (box1_x2 >= box2_x1) && (box1_y1 <= box2_y2) && (box1_y2 >= box2_y1))
    {
        if(invulneravel)
        {
             // O jogador está invulnerável, mas verificamos o ataque abaixo
        }

        else{

        if (!tomaDano && inimigoMorto == FALSE)
        {

            if(playerLife > 0)
            {
                playerLife--; // se tomar dano, perde ponto de vida
            }

            updateLifePlayer(); // atualiza os pontos de vida do player na tela
            iniciarInvencibilidade(); // inicia a invencibilidade
            tomaDano = TRUE; // o player tomou dano
        }


        }

    }
        // Verifica o ataque e muda as cores do esqueleto para um cinza claro
        if((box1_x1 + 8 <= box2_x2 + 16) && (box1_x2 + 8 >= box2_x1) && (box1_y1 <= box2_y2) && (box1_y2 >= box2_y1) && ataque && ataqueLimite)
        {
            SPR_setAnimAndFrame(player, ANIM_ATTACK, 4);
            PAL_setColor(48,RGB24_TO_VDPCOLOR(0xb1b1b1));
            PAL_setColor(49,RGB24_TO_VDPCOLOR(0xb1b1b1));
            PAL_setColor(50,RGB24_TO_VDPCOLOR(0xb1b1b1));
            PAL_setColor(51,RGB24_TO_VDPCOLOR(0xb1b1b1));
            PAL_setColor(52,RGB24_TO_VDPCOLOR(0xb1b1b1));
            PAL_setColor(53,RGB24_TO_VDPCOLOR(0xb1b1b1));
            PAL_setColor(54,RGB24_TO_VDPCOLOR(0xb1b1b1));
            PAL_setColor(55,RGB24_TO_VDPCOLOR(0xb1b1b1));

          if(inimigoLife > 0)
          {
             inimigoLife--; // se tomar dano perde pontos de vida

          }

            updateLifeInimigo(); // atualiza os pontos de vida do inimigo na tela
            ataqueLimite = FALSE;  // Impede ataques consecutivos


        }

    else
       {
            PAL_setColor(48,RGB24_TO_VDPCOLOR(0xff00ff));
            PAL_setColor(49,RGB24_TO_VDPCOLOR(0x472304));
            PAL_setColor(50,RGB24_TO_VDPCOLOR(0x403c25));
            PAL_setColor(51,RGB24_TO_VDPCOLOR(0x181407));
            PAL_setColor(52,RGB24_TO_VDPCOLOR(0x706a44));
            PAL_setColor(53,RGB24_TO_VDPCOLOR(0x6a6a67));
            PAL_setColor(54,RGB24_TO_VDPCOLOR(0x9a9a9a));
            PAL_setColor(55,RGB24_TO_VDPCOLOR(0xb1b1b1));
            tomaDano = FALSE;
       }
}

void morteInimigo()
{

  if(inimigoLife <= 0)
{
    timer++; // inicia a contagem
    inimigoLife = 0; // zera os pontos de vida
    tomaDano = FALSE; // não toma mais dano depois que os pontos de vida chega a zero
    inimigoMorto = TRUE; // confirma a morte

    //rotina da execução da animação de morte
    if(timer > 50) timer = 0;

    if(timer < 40)
    {
       SPR_setAnim(inimigo, ANIM_MORTE); // executa a animação de morte
    }

    if(timer > 20)
    {
        SPR_releaseSprite(inimigo); // desaparece com o sprite da tela
    }
}
}


void mortePlayer()
{
    if (playerLife <= 0)
    {
        SPR_setAnim(player, ANIM_DEAD); // executa a animação de morte
        playerLife = 0; // zera os pontos de vida
        tomaDano = FALSE; // impede que continue tomando dano depois de morto
        moveLeft = FALSE; // impede a movimentação para a esquerda
        moveRight = FALSE; //impede a movimentação para a direita


    if (isDead)
    {
        // Não reiniciar a animação, manter o último quadro congelado
        SPR_setAnimAndFrame(player, ANIM_DEAD, 8);  // Congelar no último quadro
    }
    }
}
