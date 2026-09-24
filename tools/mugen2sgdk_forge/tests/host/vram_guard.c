/* Reserva de VRAM do corpo = maior sheet de CORPO. Um sheet de efeito maior forcado na parte 0
 * do lutador vai ao pool (nao transborda a regiao vizinha) e volta ao slot fixo depois. */
#include "mg/mg_runtime.h"
#include "mg_gen/mg_ken.h"
u32 host_sound_plays, host_def_switches;
static int find_anim(const MgCharDef *d, int want_fx, u16 min_tiles)
{
    for (int a = 0; a < d->nanims; a++) {
        const MgAnimFrame *f = &d->frames[d->anims[a].first];
        if (f->sheet < 0) continue;
        const MgSheet *sh = &d->sheets[f->sheet];
        if ((sh->pal != 0) == want_fx && sh->def->maxNumTile >= min_tiles) return a;
    }
    return -1;
}
int main(void)
{
    const MgCharDef *d = &mg_char_ken;
    u16 body = 0, any = 0;
    for (int i = 0; i < d->nsheets; i++) {
        u16 n = d->sheets[i].def->maxNumTile;
        if (n > any) any = n;
        if (!d->sheets[i].pal && n > body) body = n;
    }
    MG_fightInit(d, 0, d, 1, 1);
    MgPlayer *p = &mg_fight.p[0];
    int fx = find_anim(d, 1, body + 1), bd = find_anim(d, 0, 1);
    int ok_fixed_before, ok_pool, ok_back, slot_ok;
    p->anim_idx = bd; p->elem = 0; MG_fightRender();
    ok_fixed_before = p->dr.fixed0 == 1 && !(p->dr.spr[0]->flags & SPR_FLAG_AUTO_VRAM_ALLOC);
    u16 slot = p->dr.spr[0]->attr & TILE_INDEX_MASK;
    slot_ok = slot == TILE_USER_INDEX && MG_fightVramNext() >= TILE_USER_INDEX + 2 * body;
    p->anim_idx = fx; p->elem = 0; MG_fightRender();
    ok_pool = p->dr.fixed0 == 0 && (p->dr.spr[0]->flags & SPR_FLAG_AUTO_VRAM_ALLOC);
    p->anim_idx = bd; p->elem = 0; MG_fightRender();
    ok_back = p->dr.fixed0 == 1 && (p->dr.spr[0]->attr & TILE_INDEX_MASK) == slot;
    printf("{\"body_max\": %u, \"any_max\": %u, \"fx_anim\": %d, \"vram_next\": %u, \"fixed_before\": %d, "
           "\"pool\": %d, \"back\": %d, \"slot_ok\": %d}\n", body, any, fx, MG_fightVramNext(),
           ok_fixed_before, !!ok_pool, ok_back, slot_ok);
    return 0;
}
