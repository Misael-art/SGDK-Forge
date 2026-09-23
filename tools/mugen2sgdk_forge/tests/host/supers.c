/* Luta CPU x CPU com energia cheia (-DMG_TEST_FULL_POWER): mede efeitos de super (fundo 730, anel 30100). */
#include "mg/mg_runtime.h"
#include "mg_gen/mg_ken.h"
u32 host_sound_plays, host_def_switches;
int main(void){
    MG_fightInit(&mg_char_ken, 0, &mg_char_ken, 0, 1);
    mg_fight.p[0].is_cpu = 1;
    long first[3]={-1,-1,-1}; int bg=0, ring=0, big=0;
    for (long t=0;t<36000;t++){
        MG_fightUpdate(0,0); MG_fightRender();
        for(int s=0;s<2;s++){ int st=mg_fight.p[s].stateno; (void)st; }
        for(int i=0;i<MG_MAX_EXPLOD;i++){ MgExplod *e=&mg_fight.explod[i]; if(!e->active) continue;
            s16 id=mg_char_ken.anims[e->anim_idx].id;
            if(id==730){ bg++; if(first[1]<0) first[1]=t; }
            if(id==30100){ ring++; if(first[2]<0) first[2]=t;
                const MgAnimFrame *f=&mg_char_ken.frames[mg_char_ken.anims[e->anim_idx].first+e->elem]; if(f->nparts>1) big++; } }
    }
    printf("{\"bg730_ticks\": %d, \"ring_ticks\": %d}\n", bg, ring);
}
