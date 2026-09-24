/* Etapa 3: camera shake (impacto pesado) + palette flash (acerto), conferidos evento a evento
 * numa luta CPU x CPU. Cada violacao conta; o teste Python exige zero. */
#include "mg/mg_runtime.h"
#include "mg_gen/mg_ken.h"
u32 host_sound_plays, host_def_switches;
/* oraculo INDEPENDENTE do runtime: canal de 3 bits clareado para o branco em nivel/4 */
static const u8 kExp[5][8] = {
    { 0, 1, 2, 3, 4, 5, 6, 7 }, { 2, 3, 3, 4, 5, 6, 6, 7 }, { 4, 4, 5, 5, 6, 6, 7, 7 },
    { 5, 6, 6, 6, 7, 7, 7, 7 }, { 7, 7, 7, 7, 7, 7, 7, 7 },
};
static u16 blend(u16 v, u8 l)
{
    return ((u16)kExp[l][(v >> 9) & 7] << 9) | ((u16)kExp[l][(v >> 5) & 7] << 5) | ((u16)kExp[l][(v >> 1) & 7] << 1);
}
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
    /* contrato: o flash so escreve na linha do lutador; PAL0/PAL3 intocadas (fora do emprestimo do super) */
    u16 iso0[16], iso3[16];
    memcpy(iso0, &host_cram[0], 32); memcpy(iso3, &host_cram[48], 32);
    long bad_iso = 0, bad_stuck = 0, bad_round = 0, retriggers = 0, proj_hits = 0, round_checks = 0;
    long hitstop_checked = 0, superpause_checked = 0, iso_frames = 0;
    u8 prev_bgfx = 0; int round_watch = 0; s16 prev_round = mg_fight.round_no, prev_rs = mg_fight.round_state;
    long bad_guard = 0, bad_flash = 0, bad_dir = 0, bad_restore = 0, bad_shake_end = 0, bad_scroll = 0;
    s16 prev_hs[2] = { 0, 0 };
    s32 prev_life[2] = { mg_fight.p[0].life, mg_fight.p[1].life };
    int hit_now[2];
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
            /* acerto neste tick = vida caiu sem defesa (pega o 2o golpe ainda dentro do hitshake) */
            hit_now[s] = d->life < prev_life[s] && !d->gh_guarded;
            prev_life[s] = d->life;
        }
        MG_fightRender(); host_vblank();
        for (int s = 0; s < 2; s++) {                   /* nunca trava: sem novo acerto, desce 1 por quadro */
            int retrig = (ev == s && !ev_guard) || hit_now[s];
            if (retrig && before[s]) retriggers++;
            if (hit_now[s] && !(ev == s && !ev_guard)) {       /* 2o golpe dentro do hitshake: cor exata tambem */
                MgPlayer *d = &mg_fight.p[s];
                u8 L = (d->gh_fall || d->life <= 0 || d->gh.damage >= 100) ? 4 : 3;
                for (int k = 1; k < 16; k++)
                    if (host_cram[(s ? 32 : 16) + k] != blend(base[s][k], L)) { bad_flash++; break; }
            }
            if (!retrig && before[s]) {
                if (mg_fight.flash_lvl[s] != before[s] - 1) bad_stuck++;
                if (mg_fight.p[0].hitpause > 0 || mg_fight.p[1].hitpause > 0) hitstop_checked++;
                if (mg_fight.pause_time > 0) superpause_checked++;
            }
        }
        if (ev >= 0 && !ev_guard) {                     /* acerto por projetil distante (> 120 px) */
            MgPlayer *a = &mg_fight.p[ev ^ 1];
            s32 dx = (a->x - mg_fight.p[ev].x) >> 8; if (dx < 0) dx = -dx;
            for (int i = 0; i < MG_MAX_PROJ; i++) if (a->proj[i].active && dx > 120) { proj_hits++; break; }
        }
        if (!mg_fight.bgfx_active && !prev_bgfx) {
            iso_frames++;
            if (memcmp(&host_cram[0], iso0, 32) || memcmp(&host_cram[48], iso3, 32)) bad_iso++;
        } else memcpy(iso0, &host_cram[0], 32);      /* emprestimo declarado do super: PAL0 muda; re-snapshot */
        prev_bgfx = mg_fight.bgfx_active;
        if (mg_fight.round_no != prev_round || mg_fight.round_state != prev_rs) round_watch = 5;
        prev_round = mg_fight.round_no; prev_rs = mg_fight.round_state;
        if (round_watch && --round_watch == 0) {        /* troca de round/KO: linhas devolvidas exatas */
            round_checks++;
            for (int s = 0; s < 2; s++)
                if (mg_fight.flash_lvl[s] == 0 && memcmp(&host_cram[(s ? 32 : 16) + 1], &base[s][1], 30)) bad_round++;
        }
        if (ev >= 0 && ev_guard) {
            guards++;
            if (mg_fight.flash_lvl[ev] > before[ev] - (before[ev] ? 1 : 0)) bad_guard++;   /* defesa nao acende */
        } else if (ev >= 0) {
            hits++;
            /* ja passou 1 render: heavy 4->3, normal 3->2; a cor 1 da linha ficou mais clara */
            if (mg_fight.flash_lvl[ev] != (ev_heavy ? 3 : 2)) bad_flash++;
            /* no quadro do acerto a linha inteira (15 cores) e EXATAMENTE a mistura do nivel inicial */
            for (int k = 1; k < 16; k++)
                if (host_cram[(ev ? 32 : 16) + k] != blend(base[ev][k], ev_heavy ? 4 : 3)) { bad_flash++; break; }
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
    /* cenario DIRIGIDO: flash armado + superpause forcada. O flash e de render e tem de devolver a
     * linha exata em 4 quadros mesmo com o jogo congelado (nao ocorre naturalmente no CPU x CPU). */
    long superpause_directed_ok;
    {
        mg_fight.flash_lvl[0] = 4;
        mg_fight.pause_time = 60;
        for (int f = 0; f < 4; f++) { MG_fightUpdate(0, 0); MG_fightRender(); host_vblank(); }
        superpause_directed_ok = mg_fight.flash_lvl[0] == 0 && mg_fight.pause_time > 0 &&
                                 !memcmp(&host_cram[17], &base[0][1], 30);
        mg_fight.pause_time = 0;
    }
    bad = bad_guard + bad_flash + bad_dir + bad_restore + bad_shake_end + bad_scroll + bad_iso + bad_stuck + bad_round;
    printf("{\"hits\": %ld, \"heavy\": %ld, \"guards\": %ld, \"flash_restored\": %ld, \"shake_done\": %ld, "
           "\"shake_varied\": %ld, \"bad_guard\": %ld, \"bad_flash\": %ld, \"bad_dir\": %ld, \"bad_restore\": %ld, "
           "\"bad_shake_end\": %ld, \"bad_scroll\": %ld, \"bad_iso\": %ld, \"bad_stuck\": %ld, \"bad_round\": %ld, "
           "\"retriggers\": %ld, \"proj_hits\": %ld, \"round_checks\": %ld, \"hitstop_checked\": %ld, "
           "\"superpause_checked\": %ld, \"iso_frames\": %ld, \"superpause_directed_ok\": %ld, \"bad\": %ld}\n",
           hits, heavy, guards, flash_restored, shake_done, shake_varied, bad_guard, bad_flash, bad_dir,
           bad_restore, bad_shake_end, bad_scroll, bad_iso, bad_stuck, bad_round, retriggers, proj_hits,
           round_checks, hitstop_checked, superpause_checked, iso_frames, superpause_directed_ok, bad);
    return 0;
}
