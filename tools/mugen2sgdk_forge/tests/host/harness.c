/* Harness nativo: CPU x CPU por N ticks; imprime estatisticas em JSON. */
#include "mg/mg_runtime.h"
#include "mg_gen/mg_ken.h"
u32 host_sound_plays, host_def_switches;
int main(int argc, char **argv)
{
    long ticks = argc > 1 ? atol(argv[1]) : 3600;
    MG_fightInit(&mg_char_ken, mg_char_ken.default_pal, &mg_char_ken, mg_char_ken.default_pal, 1);
    mg_fight.p[0].is_cpu = 1;
    long hits = 0, rounds = 0, ko = 0, states_seen = 0;
    static u8 seen[2][32768];
    s32 prev_life[2] = { mg_fight.p[0].life, mg_fight.p[1].life };
    s16 prev_round = mg_fight.round_no;
    for (long t = 0; t < ticks; t++) {
        MG_fightUpdate(0, 0);
        MG_fightRender();
        if (getenv("MG_TRACE") && t % atol(getenv("MG_TRACE")) == 0)
            printf("t=%ld rs=%d rt=%d | P1 at=%d el=%d hp=%d sh=%d st=%d an=%d ctrl=%d mt=%c x=%d y=%d life=%d | P2 st=%d an=%d ctrl=%d mt=%c x=%d life=%d\n",
                   t, mg_fight.round_state, mg_fight.round_timer,
                   (int)mg_fight.p[0].anim_time, mg_fight.p[0].elem, mg_fight.p[0].hitpause, mg_fight.p[0].hitshake,
                   mg_fight.p[0].stateno, mg_fight.p[0].anim_id, mg_fight.p[0].ctrl, mg_fight.p[0].movetype,
                   (int)(mg_fight.p[0].x >> 8), (int)(mg_fight.p[0].y >> 8), (int)mg_fight.p[0].life,
                   mg_fight.p[1].stateno, mg_fight.p[1].anim_id, mg_fight.p[1].ctrl, mg_fight.p[1].movetype,
                   (int)(mg_fight.p[1].x >> 8), (int)mg_fight.p[1].life);
        for (int s = 0; s < 2; s++) {
            MgPlayer *p = &mg_fight.p[s];
            if (p->life < prev_life[s]) hits++;
            if (p->life <= 0 && prev_life[s] > 0) ko++;
            prev_life[s] = p->life;
            if (p->stateno >= 0 && !seen[s][p->stateno]) { seen[s][p->stateno] = 1; states_seen++; }
        }
        if (mg_fight.round_no != prev_round) { rounds++; prev_round = mg_fight.round_no;
            prev_life[0] = mg_fight.p[0].life; prev_life[1] = mg_fight.p[1].life; }
    }
    printf("{\"ticks\": %ld, \"damage_events\": %ld, \"kos\": %ld, \"round_changes\": %ld, "
           "\"distinct_states\": %ld, \"sound_plays\": %u, \"sheet_switches\": %u, \"p1_life\": %d, \"p2_life\": %d}\n",
           ticks, hits, ko, rounds, states_seen, host_sound_plays, host_def_switches,
           (int)mg_fight.p[0].life, (int)mg_fight.p[1].life);
    return 0;
}
