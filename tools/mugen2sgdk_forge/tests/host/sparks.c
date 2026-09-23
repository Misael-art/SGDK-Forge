/* P1: faiscas ancoradas no contato. Aproxima o P1 do P2 (parado), aplica uma serie de socos em pe
 * (X) e depois de chutes agachado (baixo+A); imprime cada faisca criada como JSON. */
#include "mg/mg_runtime.h"
#include "mg_gen/mg_ken.h"
u32 host_sound_plays, host_def_switches;
static u8 seen[MG_MAX_EXPLOD];
static void scan(const char *tag, int *first)
{
    for (int k = 0; k < MG_MAX_EXPLOD; k++) {
        MgExplod *e = &mg_fight.explod[k];
        u8 fresh = e->active && e->anim_time == 0 && e->elem == 0 && e->elem_time == 0;
        if (fresh && !seen[k]) {
            s16 id = mg_char_ken.anims[e->anim_idx].id;
            if (id >= 700 && id < 800) {
                printf("%s{\"tag\":\"%s\",\"x\":%d,\"y\":%d,\"p2x\":%d,\"var\":%d}", *first ? "" : ",", tag,
                       (int)(e->x >> 8), (int)(e->y >> 8), (int)(mg_fight.p[1].x >> 8), mg_fight.p[0].spark_var);
                *first = 0;
            }
        }
        seen[k] = fresh;
    }
}
static void run(u16 pad, int n, const char *tag, int *first)
{
    for (int i = 0; i < n; i++) { MG_fightUpdate(pad, 0); MG_fightRender(); scan(tag, first); }
}
int main(void)
{
    MG_fightInit(&mg_char_ken, 0, &mg_char_ken, 0, 0);
    while (mg_fight.round_state != 1) { MG_fightUpdate(0, 0); MG_fightRender(); }
    int first = 1;
    printf("[");
    run(BUTTON_RIGHT, 45, "walk", &first);
    for (int r = 0; r < 5; r++) {
        run(BUTTON_X, 2, "high", &first); run(0, 12, "high", &first); run(BUTTON_RIGHT, 6, "high", &first);
    }
    run(0, 40, "gap", &first);
    for (int r = 0; r < 5; r++) {
        run(BUTTON_RIGHT, 8, "low", &first); run(BUTTON_DOWN, 6, "low", &first);
        run(BUTTON_DOWN | BUTTON_A, 2, "low", &first); run(BUTTON_DOWN, 10, "low", &first);
    }
    printf("]\n");
    return 0;
}
