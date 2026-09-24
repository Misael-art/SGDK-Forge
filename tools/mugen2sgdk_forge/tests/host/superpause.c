/* Regressao focal do SuperPause no personagem SINTETICO (tests/test_host_runtime.py).
 *
 * Cada parametro tem valor distinto (time 31, movetime 5, poweradd 250, pos 17,-23,
 * anim S700, sound S2,0): trocar dois indices MG_P_* no gerador muda algum numero
 * abaixo. pos nao zero com facing -1 prova o espelhamento do X (o bug do Ken era o
 * anel nascendo 250 px abaixo do chao por indice deslocado). */
#include "mg/mg_runtime.h"
#include "mg_gen/mg_fixture.h"
#include "mgres_fixture.h"
u32 host_sound_plays, host_def_switches;
extern const u8 *host_last_pcm;

#define FX(v) ((mgfx)(v) << MG_FX_SHIFT)

int main(void)
{
    MG_fightInit(&mg_char_fixture, 0, &mg_char_fixture, 0, 0);
    mg_fight.round_state = 1;
    MgPlayer *p = &mg_fight.p[0], *o = &mg_fight.p[1];
    p->x = FX(100); p->y = 0; p->facing = -1; p->power = 0;
    o->x = FX(40);
    MG_changeState(p, 3000, -1, -1);
    u32 snd0 = host_sound_plays;
    MG_fightUpdate(0, 0);

    int ex = -1;
    for (int i = 0; i < MG_MAX_EXPLOD; i++)
        if (mg_fight.explod[i].active && mg_char_fixture.anims[mg_fight.explod[i].anim_idx].id == 700) ex = i;

    /* ticks: o dono anda so durante movetime; o oponente fica congelado ate o fim */
    const int pause_first = mg_fight.pause_time, movetime_first = mg_fight.pause_movetime;
    s32 p_t0 = p->time, o_t0 = o->time;
    int pause_ticks = 0;
    while (mg_fight.pause_time > 0 && pause_ticks < 200) { MG_fightUpdate(0, 0); pause_ticks++; }

    printf("{\"pause_time_first\": %d, \"pause_ticks\": %d, \"movetime_first\": %d, \"owner\": %d, \"power\": %d, "
           "\"sound_plays\": %u, \"sound_is_2_0\": %d, \"explod\": %d, \"ex_x\": %ld, \"ex_y\": %ld, \"ex_facing\": %d, "
           "\"owner_moved\": %ld, \"other_moved\": %ld}\n",
           pause_first, pause_ticks, movetime_first, mg_fight.pause_owner, (int)p->power,
           host_sound_plays - snd0, host_last_pcm == mg_fixture_snd_2_0, ex,
           ex >= 0 ? (long)(mg_fight.explod[ex].x >> MG_FX_SHIFT) : -9999,
           ex >= 0 ? (long)(mg_fight.explod[ex].y >> MG_FX_SHIFT) : -9999,
           ex >= 0 ? mg_fight.explod[ex].facing : 0,
           (long)(p->time - p_t0), (long)(o->time - o_t0));
    return 0;
}
