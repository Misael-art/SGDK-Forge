/* Etapa 3: camera shake (impacto pesado) + palette flash (acerto), conferidos evento a evento
 * numa luta CPU x CPU. Cada violacao conta; o teste Python exige zero. */
#include "mg/mg_runtime.h"
#include "mg_gen/mg_ken.h"
u32 host_sound_plays, host_def_switches;
extern u16 host_cram[64];
extern s16 host_scroll_b[2];
int main(int argc, char **argv)
{
    long ticks = argc > 1 ? atol(argv[1]) : 36000;
    MG_fightInit(&mg_char_ken, mg_char_ken.default_pal, &mg_char_ken, mg_char_ken.default_pal, 1);
    mg_fight.p[0].is_cpu = 1;
    u16 base[2][16];
    for (int s = 0; s < 2; s++) memcpy(base[s], &host_cram[s ? 32 : 16], 32);
    long hits = 0, heavy = 0, guards = 0, bad = 0, flash_restored = 0, shake_done = 0, shake_varied = 0;
    long bad_guard = 0, bad_flash = 0, bad_dir = 0, bad_restore = 0, bad_shake_end = 0, bad_scroll = 0;
    s16 prev_hs[2] = { 0, 0 };
    int watch = -1, watch_age = 0, shake_age = -1, distinct = 0; s8 last_x = 0;
    for (long t = 0; t < ticks; t++) {
        u8 before[2] = { mg_fight.flash_lvl[0], mg_fight.flash_lvl[1] };
        u8 shake_before = mg_fight.shake_t;
        MG_fightUpdate(0, 0);
        int ev = -1, ev_heavy = 0, ev_guard = 0; s8 ev_dir = 0;
        for (int s = 0; s < 2; s++) {
            MgPlayer *d = &mg_fight.p[s];
            if (d->hitshake > 0 && prev_hs[s] == 0) {
                ev = s; ev_guard = d->gh_guarded;
                ev_heavy = !ev_guard && (d->gh_fall || d->life <= 0 || d->gh.damage >= 100);
                ev_dir = mg_fight.p[s ^ 1].facing;
            }
            prev_hs[s] = d->hitshake;
        }
        MG_fightRender();
        if (ev >= 0 && ev_guard) {
            guards++;
            if (mg_fight.flash_lvl[ev] > before[ev] - (before[ev] ? 1 : 0)) bad_guard++;   /* defesa nao acende */
        } else if (ev >= 0) {
            hits++;
            /* ja passou 1 render: heavy 4->3, normal 3->2; a cor 1 da linha ficou mais clara */
            if (mg_fight.flash_lvl[ev] != (ev_heavy ? 3 : 2)) bad_flash++;
            u16 c = host_cram[(ev ? 32 : 16) + 1], b = base[ev][1];
            if (((c >> 1) & 7) < ((b >> 1) & 7) || ((c >> 5) & 7) < ((b >> 5) & 7) || c == b) bad_flash++;
            watch = ev; watch_age = 0;
            if (ev_heavy) {
                heavy++;
                if (mg_fight.shake_t != 1 || mg_fight.shake_x == 0 || (mg_fight.shake_x > 0) != (ev_dir > 0)) bad_dir++;
                shake_age = 0; distinct = 0; last_x = 127;
            } else if (mg_fight.shake_t == 0 && shake_before >= 12) bad_dir++;    /* leve nao treme */
        }
        if (watch >= 0 && ++watch_age == 4) {           /* 4 renders depois: paleta original exata */
            if (!mg_fight.flash_lvl[watch] && memcmp(&host_cram[(watch ? 32 : 16) + 1], &base[watch][1], 30)) bad_restore++;
            else if (!mg_fight.flash_lvl[watch]) flash_restored++;
            watch = -1;
        }
        if (host_scroll_b[0] != mg_fight.shake_x || host_scroll_b[1] != -mg_fight.shake_y) bad_scroll++;
        if (shake_age >= 0) {
            if (mg_fight.shake_x != last_x) { distinct++; last_x = mg_fight.shake_x; }
            if (++shake_age == 12) {
                if (mg_fight.shake_t >= 12 && mg_fight.shake_x != 0) bad_shake_end++;
                if (mg_fight.shake_t >= 12) { shake_done++; if (distinct >= 5) shake_varied++; }
                shake_age = -1;
            }
        }
    }
    bad = bad_guard + bad_flash + bad_dir + bad_restore + bad_shake_end + bad_scroll;
    printf("{\"hits\": %ld, \"heavy\": %ld, \"guards\": %ld, \"flash_restored\": %ld, \"shake_done\": %ld, "
           "\"shake_varied\": %ld, \"bad_guard\": %ld, \"bad_flash\": %ld, \"bad_dir\": %ld, \"bad_restore\": %ld, "
           "\"bad_shake_end\": %ld, \"bad_scroll\": %ld, \"bad\": %ld}\n",
           hits, heavy, guards, flash_restored, shake_done, shake_varied, bad_guard, bad_flash, bad_dir,
           bad_restore, bad_shake_end, bad_scroll, bad);
    return 0;
}
