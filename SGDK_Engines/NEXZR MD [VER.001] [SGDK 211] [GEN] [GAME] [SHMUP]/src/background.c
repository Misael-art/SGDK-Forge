#include "background.h"
#include "game.h"
#include "resources.h"
#include "entitymanager.h"

#define STAR_COUNT 20
#define MAX_STAR_HEIGHT 5
#define WARP_DURATION 230
#define DEACELERATION_FRAMES_ANIM 7

typedef struct {
    Sprite* spr[MAX_STAR_HEIGHT];
    int x, y;
    u8 size;
    u8 speed;
    u8 colorFrame;
    bool done;
    u8 decelCounter;
    u8 blinkCounter;
    bool visible;
} Star;

static Star stars[STAR_COUNT];
static u8 warpTimer = 0;
static bool isWarping = true;
static bool isDeacelerating = false;
static u8 deAceleratedStarsCount = 0;
static Entity* backgroundTask;

void update_background(void* context);
/*
 * O background, os caracteres e o slasher tem a mesma paleta entao
 * eu fico com 3 livres pra outra coisa
 *
 */
// inicializa aleatoriamente
void Background_init() {
    Game_resetScreen();
    currentFrame = 0;

    PAL_setPalette(SLASHER_PALLETE, slasher.palette->data, DMA);

    for (int i = 0; i < STAR_COUNT; i++) {
        u8 size = (random() % MAX_STAR_HEIGHT) + 1;
        u8 speed = 3 + size * 2 + (random() % 2);
        u8 colorFrame = random() % 3;

        int x = random() % 320;
        int y = random() % 224;

        for (int j = 0; j < size; j++) {
            stars[i].spr[j] = SPR_addSprite(&star_warp, x, y + j * 8, TILE_ATTR(SLASHER_PALLETE, FALSE, FALSE, FALSE));
            SPR_setFrame(stars[i].spr[j], colorFrame);
        }

        stars[i].x = x;
        stars[i].y = y;
        stars[i].size = size;
        stars[i].speed = speed;
        stars[i].colorFrame = colorFrame;
        stars[i].done = false;
        stars[i].decelCounter = DEACELERATION_FRAMES_ANIM;
        stars[i].blinkCounter = WARP_DURATION + 20;
        stars[i].visible = true;
    }

    backgroundTask = Entity_add(NULL, update_background);
}

void Background_stop() {
    backgroundTask->active = false;
}

void Background_resume() {
    backgroundTask->active = true;
}

bool Background_isRunning() {
    return backgroundTask->active;
}

void update_background(void* context) {
    if (Game_isPaused()) return;

    // desacelera depois do warp pra deixar mais parecido com o original
    if (currentFrame % 3 != 0 && !isDeacelerating && !isWarping) return;

    for (int i = 0; i < STAR_COUNT; i++) {
        Star* s = &stars[i];

        // atualiza posição com a velocidade
        s->y += s->speed;
        // se passar do tamanho da tela atualiza y pro topo
        if (s->y > GAME_WINDOW_HEIGHT) {
            s->y = GAME_WINDOW_START_POSITION_TOP;
            s->x = random() % GAME_WINDOW_WIDTH;
        }



        s->blinkCounter--;

        if (s->blinkCounter < (s->speed + 2)) {
            SPR_setVisibility(s->spr[0], HIDDEN);
            s->blinkCounter = random() % 20 + 1;
            s->visible = false;

        } else {
            if (!s->visible) {
                SPR_setVisibility(s->spr[0], VISIBLE);
                s->visible = true;
            }

            int y = s->y;

            for (int j = 0; j < s->size; j++) {
//                if (s->spr[j]) {
                    SPR_setPosition(s->spr[j], s->x, y);
                    SPR_setZ(s->spr[j], SPR_MAX_DEPTH); //infelizmente eu tenho sempre q setar o depth senao vai pra frente da nave
//                }
                // coloca os sprites um atras do outro
                y -= 8;
            }
        }

        // fazer a animacao diminuindo e diminuir a velocidade e deixar

        /*
         * Aqui eu libero o ultimo sprite e adiciono no counter das estrelas desaceleradas
         * exite tbm uma flag pra dizer q a animacao no objeto terminou
         *
         * poderia tambem ser feito de outra forma:
         * se eu pegasse o y dos sprites e chegasse cada vez mais perto do primeiro ate eles se sobreporem
         * acredito que ficaria melhor visualmente, ate se ao inves do tile ter 8px ter 4px e eu dobrar o numero
         * de sprites, seria fixe e como eh so pra esse inicio de fase nao teria problema. Talvez faça isso no futuro
         * quem sabe
         *
         */
        if (isDeacelerating) {
            if (s->decelCounter > 0) s->decelCounter--;

            if (s->decelCounter == 0) {
                if (s->size > 1) {
                    SPR_releaseSprite(s->spr[s->size - 1]);
                    s->spr[s->size - 1] = NULL;
                    s->size--;
                    s->speed = 2 + s->size;

                } else if (!s->done) {
                    SPR_setAnimAndFrame(s->spr[0], 1, s->colorFrame);
                    s->speed = (random() % 2) + 1;
                    s->done = true;
                    deAceleratedStarsCount++;
                }

                s->decelCounter = DEACELERATION_FRAMES_ANIM; // reinicia o contador da própria estrela
            }
        }

        // fim da animação
        if (deAceleratedStarsCount >= STAR_COUNT) {
            isDeacelerating = false;
        }
    }

    if (isWarping) {
        warpTimer++;

        if (warpTimer > WARP_DURATION){
            isDeacelerating = true;
            isWarping = false;
        }
    }
}
