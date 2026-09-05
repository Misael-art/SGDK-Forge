#include <genesis.h>
#include <string.h>
#include "opening_cutscene.h"
#include "scene_manager.h"
#include "input_abstraction.h"

typedef struct {
    u16 frame_start;
    u16 frame_end;
    const char* text;
    u16 text_y;
    void (*on_enter)(void);
    void (*on_exit)(void);
} CutsceneStep;

static u16 cutscene_frame = 0;
static s16 active_step_idx = -1;

static const u16 cutscene_palette[64] = {
    /* PAL0: UI */
    RGB24_TO_VDPCOLOR(0x000000), /* transparente/preto */
    RGB24_TO_VDPCOLOR(0xF0F8FF), /* branco */
    RGB24_TO_VDPCOLOR(0x50C8FF), /* ciano */
    RGB24_TO_VDPCOLOR(0x102850), /* azul escuro */
    /* cor 15 reservada para o font padrao do SGDK */
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, RGB24_TO_VDPCOLOR(0xF0F8FF),
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

static void op0_enter(void) { PAL_setColor(0, RGB24_TO_VDPCOLOR(0x000000)); }
static void op1_enter(void) { PAL_setColor(0, RGB24_TO_VDPCOLOR(0x000020)); }
static void op2_enter(void) { PAL_setColor(0, RGB24_TO_VDPCOLOR(0x102040)); }
static void op3_enter(void) { PAL_setColor(0, RGB24_TO_VDPCOLOR(0x603000)); }
static void op4_enter(void) { PAL_setColor(0, RGB24_TO_VDPCOLOR(0x200000)); }
static void op5_enter(void) { PAL_setColor(0, RGB24_TO_VDPCOLOR(0x101010)); }
static void op6_enter(void) { VDP_clearPlane(BG_A, TRUE); }

static const CutsceneStep cutscene_steps[] = {
    { 0,   60,  "THE SKY ROAD SLEPT.",               12, op0_enter, NULL },
    { 60,  210, "UNTIL THE LAST BEACON CRACKED.",     12, op1_enter, NULL },
    { 210, 330, "LIO, RUN.",                         12, op2_enter, NULL },
    { 330, 420, "CARRY THE LUMEN.",                  12, op3_enter, NULL },
    { 420, 570, "DO NOT LET IT REMEMBER YOUR NAME.", 12, op4_enter, NULL },
    { 570, 690, "THE ROAD AWAKENS.",                 12, op5_enter, NULL },
    { 690, 750, "",                                  12, op6_enter, NULL }
};

#define CUTSCENE_STEPS_COUNT 7

static void clear_text_line(u16 y)
{
    VDP_drawText("                                        ", 0, y);
}

static void draw_typewriter(const char* text, u16 current_char_count, u16 x, u16 y)
{
    char temp[40];
    if (current_char_count >= 39)
    {
        current_char_count = 39;
    }

    strncpy(temp, text, current_char_count);
    temp[current_char_count] = '\0';
    VDP_drawText(temp, x, y);
}

static void enter(void)
{
    cutscene_frame = 0;
    active_step_idx = -1;
}

static void update(void)
{
    /* Encontra o step correspondente ao frame atual */
    s16 current_step_idx = -1;
    for (s16 i = 0; i < CUTSCENE_STEPS_COUNT; i++)
    {
        if (cutscene_frame >= cutscene_steps[i].frame_start && cutscene_frame < cutscene_steps[i].frame_end)
        {
            current_step_idx = i;
            break;
        }
    }

    /* Trata a transicao de step */
    if (current_step_idx != active_step_idx)
    {
        if (active_step_idx != -1)
        {
            if (cutscene_steps[active_step_idx].on_exit != NULL)
            {
                cutscene_steps[active_step_idx].on_exit();
            }
            clear_text_line(cutscene_steps[active_step_idx].text_y);
        }

        if (current_step_idx != -1)
        {
            if (cutscene_steps[current_step_idx].on_enter != NULL)
            {
                cutscene_steps[current_step_idx].on_enter();
            }
        }
        active_step_idx = current_step_idx;
    }

    /* Se ja passamos do final de todos os steps, transiciona para a corrida */
    if (cutscene_frame >= 750 || current_step_idx == -1)
    {
        SM_requestTransition(APP_SCENE_RACE);
        return;
    }

    const CutsceneStep* step = &cutscene_steps[current_step_idx];
    u16 step_frame = cutscene_frame - step->frame_start;
    u16 text_len = strlen(step->text);

    /* Typewriter: 2 frames por caractere */
    u16 typewriter_done_frame = text_len * 2;
    u16 char_show = step_frame / 2;

    /* Desenha o texto */
    if (text_len > 0)
    {
        u16 x = (40 - text_len) / 2;
        draw_typewriter(step->text, char_show, x, step->text_y);
    }

    /* Verifica interrupcao por botao */
    if (IO_getState(INPUT_ACTION_START).pressed || IO_getState(INPUT_ACTION_A).pressed)
    {
        if (step_frame < typewriter_done_frame)
        {
            /* Completa o typewriter instantaneamente */
            cutscene_frame = step->frame_start + typewriter_done_frame;
        }
        else
        {
            /* Pula para o proximo step (um frame antes do final do atual) */
            cutscene_frame = step->frame_end - 1;
        }
    }

    cutscene_frame++;
}

static void exit(void)
{
    VDP_clearPlane(BG_A, TRUE);
}

const Scene opening_cutscene = {
    .enter = enter,
    .update = update,
    .exit = exit,
    .palette = cutscene_palette,
    .enterFade = true,
    .exitFade = true
};
