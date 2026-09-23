/* Teste de golpes por script: injeta entradas de controle reais (SGDK) no P1 e registra os
 * estados alcancados. Uso: moves "<seq>" onde seq = passos "BOTOES:ticks" separados por espaco,
 * BOTOES em {U,D,L,R,A,B,C,X,Y,Z,0} combinados (ex.: "D:3 DR:3 R:3 RX:2"). P1 olha para a direita. */
#include "mg/mg_runtime.h"
#include "mg_gen/mg_ken.h"
u32 host_sound_plays, host_def_switches;

static u16 pad_of(const char *s)
{
    u16 m = 0;
    for (; *s && *s != ':'; s++) switch (*s) {
        case 'U': m |= BUTTON_UP; break; case 'D': m |= BUTTON_DOWN; break;
        case 'L': m |= BUTTON_LEFT; break; case 'R': m |= BUTTON_RIGHT; break;
        case 'A': m |= BUTTON_A; break; case 'B': m |= BUTTON_B; break; case 'C': m |= BUTTON_C; break;
        case 'X': m |= BUTTON_X; break; case 'Y': m |= BUTTON_Y; break; case 'Z': m |= BUTTON_Z; break;
    }
    return m;
}

int main(int argc, char **argv)
{
    MG_fightInit(&mg_char_ken, 0, &mg_char_ken, 0, 0);
    while (mg_fight.round_state != 1) MG_fightUpdate(0, 0);
    for (int i = 0; i < 20; i++) MG_fightUpdate(0, 0);
    s16 seen[64]; int ns = 0;
    char buf[512];
    strncpy(buf, argc > 1 ? argv[1] : "", sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = 0;
    for (char *tok = strtok(buf, " "); tok; tok = strtok(0, " ")) {
        u16 pad = pad_of(tok);
        char *c = strchr(tok, ':');
        int n = c ? atoi(c + 1) : 1;
        for (int i = 0; i < n; i++) {
            MG_fightUpdate(pad, 0);
            s16 st = mg_fight.p[0].stateno;
            if (getenv("MG_CMDDBG")) {
                int ci = atoi(getenv("MG_CMDDBG"));
                MgPlayer *q = &mg_fight.p[0];
                printf("pad=%04x in=%04x pos=%d age=%d timer=%d st=%d ctrl=%d\n", pad, q->hist[q->hist_head],
                       q->cmd_pos[ci], q->cmd_age[ci], q->cmd_timer[ci], st, q->ctrl);
            }
            if (!ns || seen[ns - 1] != st) if (ns < 64) seen[ns++] = st;
        }
    }
    for (int i = 0; i < 90; i++) {
        MG_fightUpdate(0, 0);
        MG_fightRender();
        if (getenv("MG_FXDBG"))
            for (int k = 0; k < MG_MAX_EXPLOD; k++) if (mg_fight.explod[k].active) {
                const MgAnim *a = &mg_char_ken.anims[mg_fight.explod[k].anim_idx];
                const MgAnimFrame *f = &mg_char_ken.frames[a->first + mg_fight.explod[k].elem];
                printf("explod anim=%d elem=%d partes=%d\n", a->id, mg_fight.explod[k].elem, f->nparts);
            }
        s16 st = mg_fight.p[0].stateno;
        if (seen[ns - 1] != st && ns < 64) seen[ns++] = st;
    }
    printf("[");
    for (int i = 0; i < ns; i++) printf("%s%d", i ? ", " : "", seen[i]);
    printf("]\n");
    return 0;
}
