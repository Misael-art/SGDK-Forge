/* mg_char.c -- personagem: estados/controladores MUGEN, animacao, fisica, comandos. */
#include "mg_runtime.h"
#include "mg_ops.h"

#define FXI(v) ((mgfx)(v) << MG_FX_SHIFT)
#define PARAM(p, c, i) ((p)->sdef->param_offs[(c)->params + (i)])
#define HAS(p, c, i) (PARAM(p, c, i) != MG_NONE)
#define PV(p, c, i) MG_eval((p), PARAM(p, c, i))
#define PIV(p, c, i, d) MG_evalInt((p), PARAM(p, c, i), (d))
#define HIST(p, t) ((p)->hist[((p)->hist_head - (t)) & (MG_INPUT_HIST - 1)])
#define SYM(p, c, i) ((p)->sdef->syms[(c)->sym + (i)])

/* ------------------------------------------------------------------ busca */
s16 MG_findAnim(const MgCharDef *d, s16 id)
{
    s16 lo = 0, hi = d->nanims - 1;
    while (lo <= hi) {
        s16 mid = (lo + hi) >> 1;
        s16 v = d->anims[mid].id;
        if (v == id) return mid;
        if (v < id) lo = mid + 1; else hi = mid - 1;
    }
    return -1;
}

s16 MG_findState(const MgCharDef *d, s16 id)
{
    s16 lo = 0, hi = d->nstates - 1;
    while (lo <= hi) {
        s16 mid = (lo + hi) >> 1;
        s16 v = d->states[mid].id;
        if (v == id) return mid;
        if (v < id) lo = mid + 1; else hi = mid - 1;
    }
    return -1;
}

/* ------------------------------------------------------------------ animacao */
void MG_changeAnim(MgPlayer *p, s16 anim, u8 elem1)
{
    s16 idx = MG_findAnim(p->def, anim);
    if (idx < 0) return;                      /* MUGEN tambem ignora anim inexistente */
    const MgAnim *a = &p->def->anims[idx];
    const MgAnimFrame *f = &p->def->frames[a->first];
    if (elem1 < 1) elem1 = 1;
    if (elem1 > a->count) elem1 = a->count;
    p->anim_idx = idx;
    p->anim_id = anim;
    p->elem = elem1 - 1;
    p->elem_time = 0;
    p->anim_time = 0;
    for (u8 i = 0; i < p->elem; i++) p->anim_time += f[i].time < 0 ? 0 : f[i].time;
}

static void anim_step(u16 *anim_idx, u8 *elem, s16 *elem_time, s32 *anim_time, const MgCharDef *d)
{
    const MgAnim *a = &d->anims[*anim_idx];
    const MgAnimFrame *f = &d->frames[a->first + *elem];
    (*elem_time)++;
    (*anim_time)++;
    if (f->time >= 0 && *elem_time >= f->time) {
        *elem_time = 0;
        (*elem)++;
        if (*elem >= a->count) {
            *elem = a->loopstart < a->count ? a->loopstart : 0;
            s32 t = 0;
            const MgAnimFrame *ff = &d->frames[a->first];
            for (u8 i = 0; i < *elem; i++) t += ff[i].time < 0 ? 0 : ff[i].time;
            *anim_time = t;
        }
    }
}

/* ------------------------------------------------------------------ estados */
void MG_changeState(MgPlayer *p, s16 no, s16 ctrl, s16 anim)
{
    s16 idx = MG_findState(p->sdef, no);
    if (idx < 0 && p->sdef != p->def) {            /* estado nao existe no dono: volta ao proprio */
        p->sdef = p->def;
        idx = MG_findState(p->def, no);
    }
    if (idx < 0) idx = MG_findState(p->sdef, 0);  /* estado inexistente: MUGEN tambem cai no 0 */
    if (idx < 0) return;
    const MgState *s = &p->sdef->states[idx];
    p->prevstateno = p->stateno;
    p->stateno = s->id;
    p->state_idx = idx;
    p->time = 0;
    p->state_changed = 1;
    if (s->statetype != 'U') p->statetype = s->statetype;
    if (s->movetype != 'U') p->movetype = s->movetype;
    if (s->physics != 'U') p->physics = s->physics;
    if (!(s->flags & 2)) p->hitdef_active = 0;
    if (!(s->flags & 4)) { p->movecontact = p->movehit = p->moveguarded = 0; }
    if (!(s->flags & 8)) p->hitcount = 0;
    if (s->p_ctrl != MG_NONE) p->ctrl = MG_evalInt(p, s->p_ctrl, p->ctrl) ? 1 : 0;
    if (ctrl >= 0) p->ctrl = ctrl ? 1 : 0;
    if (s->p_velx != MG_NONE) p->vx = MG_eval(p, s->p_velx);
    if (s->p_vely != MG_NONE) p->vy = MG_eval(p, s->p_vely);
    if (s->p_poweradd != MG_NONE) p->power += MG_evalInt(p, s->p_poweradd, 0);
    if (s->p_sprpriority != MG_NONE) p->sprpriority = MG_evalInt(p, s->p_sprpriority, 0);
    if (s->p_juggle != MG_NONE) p->juggle = MG_evalInt(p, s->p_juggle, 0);
    if (anim >= 0) MG_changeAnim(p, anim, 1);
    else if (s->p_anim != MG_NONE) MG_changeAnim(p, MG_evalInt(p, s->p_anim, p->anim_id), 1);
    if ((s->flags & 1) && p->enemy && MG_FACE(p->enemy->x - p->x, p->facing) < 0) p->facing = -p->facing;
    if (p->power < 0) p->power = 0;
    if (p->power > 3000) p->power = 3000;
}

/* ------------------------------------------------------------------ hitdef */
static void read_hitdef(MgPlayer *p, const MgCtrl *c, u8 base, MgHitDef *h)
{
    #define HP(n, d) PIV(p, c, base + MG_P_HITDEF_##n, d)
    #define HF(n, d) (HAS(p, c, base + MG_P_HITDEF_##n) ? PV(p, c, base + MG_P_HITDEF_##n) : (d))
    h->damage = HP(DAMAGE_X, 0);
    h->guard_damage = HP(DAMAGE_Y, 0);
    h->pause_p1 = HP(PAUSETIME_X, 0);
    h->pause_p2 = HP(PAUSETIME_Y, 0);
    h->gpause_p1 = HP(GUARD_PAUSETIME_X, h->pause_p1);
    h->gpause_p2 = HP(GUARD_PAUSETIME_Y, h->pause_p2);
    h->hittime = HP(GROUND_HITTIME, 0);
    h->slidetime = HP(GROUND_SLIDETIME, 0);
    h->ghittime = HP(GUARD_HITTIME, h->slidetime);
    h->gslidetime = HP(GUARD_SLIDETIME, h->ghittime);
    h->gctrltime = HP(GUARD_CTRLTIME, h->gslidetime);
    h->airhittime = HP(AIR_HITTIME, 20);
    h->gvel_x = HF(GROUND_VELOCITY_X, 0);
    h->gvel_y = HF(GROUND_VELOCITY_Y, 0);
    h->avel_x = HF(AIR_VELOCITY_X, 0);
    h->avel_y = HF(AIR_VELOCITY_Y, 0);
    h->guardvel_x = HF(GUARD_VELOCITY, h->gvel_x);
    h->fall = HP(FALL, 0) != 0;
    h->airfall = HP(AIR_FALL, h->fall) != 0;
    h->fall_recover = HP(FALL_RECOVER, 1) != 0;
    h->fall_yvel = HF(FALL_YVELOCITY, -(9 * MG_FX) / 2);
    h->fall_xvel = HF(FALL_XVELOCITY, h->avel_x);
    h->spark_x = HP(SPARKXY_X, 0);
    h->spark_y = HP(SPARKXY_Y, 0);
    h->p1stateno = HP(P1STATENO, -1);
    h->p2stateno = HP(P2STATENO, -1);
    h->getpower = HP(GETPOWER, h->damage);
    h->givepower = HP(GIVEPOWER, h->damage / 2);
    h->yaccel = HF(YACCEL, (35 * MG_FX) / 100);
    h->id = HP(ID, 0);
    h->chainid = HP(CHAINID, -1);
    h->kill = HP(KILL, 1) != 0;
    h->guard_kill = HP(GUARD_KILL, 1) != 0;
    #undef HP
    #undef HF
    h->attr = SYM(p, c, MG_S_HITDEF_ATTR);
    h->hitflag = SYM(p, c, MG_S_HITDEF_HITFLAG);
    h->guardflag = SYM(p, c, MG_S_HITDEF_GUARDFLAG);
    h->animtype = SYM(p, c, MG_S_HITDEF_ANIMTYPE);
    h->air_animtype = SYM(p, c, MG_S_HITDEF_AIR_ANIMTYPE);
    h->groundtype = SYM(p, c, MG_S_HITDEF_GROUND_TYPE);
    h->airtype = SYM(p, c, MG_S_HITDEF_AIR_TYPE);
    h->priority = SYM(p, c, MG_S_HITDEF_PRIORITY);
    h->hitsound = SYM(p, c, MG_S_HITDEF_HITSOUND);
    h->guardsound = SYM(p, c, MG_S_HITDEF_GUARDSOUND);
    h->sparkno = SYM(p, c, MG_S_HITDEF_SPARKNO);
    h->guard_sparkno = SYM(p, c, MG_S_HITDEF_GUARD_SPARKNO);
    if (h->sparkno == -2) h->sparkno = p->def->consts->sparkno;
    if (h->guard_sparkno == -2) h->guard_sparkno = p->def->consts->guard_sparkno;
}

#define PROJ_HD_BASE (MG_P_PROJECTILE_DAMAGE_X - MG_P_HITDEF_DAMAGE_X)

static void spawn_projectile(MgPlayer *p, const MgCtrl *c)
{
    MgProj *pr = 0;
    for (u8 i = 0; i < MG_MAX_PROJ; i++) if (!p->proj[i].active) { pr = &p->proj[i]; break; }
    if (!pr) return;                              /* limite do pool: registrado no README */
    MgDraw keep = pr->dr;                         /* preserva sprites SGDK (evita vazamento do pool) */
    memset(pr, 0, sizeof(*pr));
    pr->dr = keep;
    pr->id = PIV(p, c, MG_P_PROJECTILE_PROJID, 0);
    pr->anim_id = PIV(p, c, MG_P_PROJECTILE_PROJANIM, 0);
    pr->hitanim = PIV(p, c, MG_P_PROJECTILE_PROJHITANIM, -1);
    pr->remanim = PIV(p, c, MG_P_PROJECTILE_PROJREMANIM, pr->hitanim);
    s16 idx = MG_findAnim(p->def, pr->anim_id);
    if (idx < 0) return;
    pr->anim_idx = idx;
    pr->facing = p->facing;
    pr->x = p->x + MG_FACE(PV(p, c, MG_P_PROJECTILE_OFFSET_X), p->facing);
    pr->y = p->y + PV(p, c, MG_P_PROJECTILE_OFFSET_Y);
    pr->vx = PV(p, c, MG_P_PROJECTILE_VELOCITY_X);
    pr->vy = PV(p, c, MG_P_PROJECTILE_VELOCITY_Y);
    pr->ax = PV(p, c, MG_P_PROJECTILE_ACCEL_X);
    pr->ay = PV(p, c, MG_P_PROJECTILE_ACCEL_Y);
    pr->removetime = PIV(p, c, MG_P_PROJECTILE_PROJREMOVETIME, -1);
    pr->hits = PIV(p, c, MG_P_PROJECTILE_PROJHITS, 1);
    pr->contact_time = -1;
    read_hitdef(p, c, PROJ_HD_BASE, &pr->hd);
    pr->active = 1;
}

/* ------------------------------------------------------------------ controladores */
static void exec(MgPlayer *p, const MgCtrl *c)
{
    MG_CRUMB('0' + (c->type % 40));
    switch (c->type) {
    case MG_CT_CHANGESTATE:
        MG_changeState(p, PIV(p, c, MG_P_CHANGESTATE_VALUE, p->stateno),
                       HAS(p, c, MG_P_CHANGESTATE_CTRL) ? PIV(p, c, MG_P_CHANGESTATE_CTRL, 0) : -1,
                       HAS(p, c, MG_P_CHANGESTATE_ANIM) ? PIV(p, c, MG_P_CHANGESTATE_ANIM, -1) : -1);
        break;
    case MG_CT_SELFSTATE:
        p->sdef = p->def;
        MG_changeState(p, PIV(p, c, MG_P_SELFSTATE_VALUE, p->stateno),
                       HAS(p, c, MG_P_SELFSTATE_CTRL) ? PIV(p, c, MG_P_SELFSTATE_CTRL, 0) : -1,
                       HAS(p, c, MG_P_SELFSTATE_ANIM) ? PIV(p, c, MG_P_SELFSTATE_ANIM, -1) : -1);
        break;
    case MG_CT_CHANGEANIM:
        MG_changeAnim(p, PIV(p, c, MG_P_CHANGEANIM_VALUE, p->anim_id), PIV(p, c, MG_P_CHANGEANIM_ELEM, 1));
        break;
    case MG_CT_VELSET:
        if (HAS(p, c, MG_P_VELSET_X)) p->vx = PV(p, c, MG_P_VELSET_X);
        if (HAS(p, c, MG_P_VELSET_Y)) p->vy = PV(p, c, MG_P_VELSET_Y);
        break;
    case MG_CT_VELADD:
        if (HAS(p, c, MG_P_VELADD_X)) p->vx += PV(p, c, MG_P_VELADD_X);
        if (HAS(p, c, MG_P_VELADD_Y)) p->vy += PV(p, c, MG_P_VELADD_Y);
        break;
    case MG_CT_VELMUL:
        if (HAS(p, c, MG_P_VELMUL_X)) p->vx = (p->vx * (PV(p, c, MG_P_VELMUL_X) >> 2)) >> (MG_FX_SHIFT - 2);
        if (HAS(p, c, MG_P_VELMUL_Y)) p->vy = (p->vy * (PV(p, c, MG_P_VELMUL_Y) >> 2)) >> (MG_FX_SHIFT - 2);
        break;
    case MG_CT_POSADD:
        if (HAS(p, c, MG_P_POSADD_X)) p->x += MG_FACE(PV(p, c, MG_P_POSADD_X), p->facing);
        if (HAS(p, c, MG_P_POSADD_Y)) p->y += PV(p, c, MG_P_POSADD_Y);
        break;
    case MG_CT_POSSET:
        if (HAS(p, c, MG_P_POSSET_X)) p->x = FXI(mg_fight.camx + 160) + PV(p, c, MG_P_POSSET_X);
        if (HAS(p, c, MG_P_POSSET_Y)) p->y = PV(p, c, MG_P_POSSET_Y);
        break;
    case MG_CT_CTRLSET: p->ctrl = PIV(p, c, MG_P_CTRLSET_VALUE, 0) != 0; break;
    case MG_CT_TURN: p->facing = -p->facing; break;
    case MG_CT_GRAVITY: p->vy += p->def->consts->yaccel; break;
    case MG_CT_SPRPRIORITY: p->sprpriority = PIV(p, c, MG_P_SPRPRIORITY_VALUE, 0); break;
    case MG_CT_POWERADD:
        p->power += PIV(p, c, MG_P_POWERADD_VALUE, 0);
        if (p->power < 0) p->power = 0;
        if (p->power > 3000) p->power = 3000;
        break;
    case MG_CT_LIFEADD: p->life += PIV(p, c, MG_P_LIFEADD_VALUE, 0); break;
    case MG_CT_POSFREEZE: p->posfreeze = PIV(p, c, MG_P_POSFREEZE_VALUE, 1) != 0; break;
    case MG_CT_VARSET:
    case MG_CT_VARADD:
    case MG_CT_VARRANDOM: {
        s16 idx = SYM(p, c, MG_S_VARSET_INDEX);
        u8 isf = SYM(p, c, MG_S_VARSET_FVAR);
        mgfx v = MG_eval(p, PARAM(p, c, 0));
        if (c->type == MG_CT_VARRANDOM) {
            s32 lo = SYM(p, c, MG_S_VARSET_MIN), hi = v >> MG_FX_SHIFT;
            v = FXI(lo + (hi > lo ? (s32)(random() % (u16)(hi - lo + 1)) : 0));
        }
        if (isf) {
            if (idx >= 0 && idx < MG_NUM_FVARS) p->fvars[idx] = (c->type == MG_CT_VARADD) ? p->fvars[idx] + v : v;
        } else if (idx >= 0 && idx < MG_NUM_VARS) {
            s32 iv = v >> MG_FX_SHIFT;
            p->vars[idx] = (c->type == MG_CT_VARADD) ? p->vars[idx] + iv : iv;
        }
        break;
    }
    case MG_CT_PLAYSND: MG_playSound(p, SYM(p, c, MG_S_PLAYSND_SOUND)); break;
    case MG_CT_STOPSND: XGM2_stopPCM(SOUND_PCM_CH_AUTO); break;
    case MG_CT_STATETYPESET: {
        u8 st = SYM(p, c, MG_S_STATETYPESET_STATETYPE), mt = SYM(p, c, MG_S_STATETYPESET_MOVETYPE),
           ph = SYM(p, c, MG_S_STATETYPESET_PHYSICS);
        if (st != 'U') p->statetype = st;
        if (mt != 'U') p->movetype = mt;
        if (ph != 'U') p->physics = ph;
        break;
    }
    case MG_CT_NOTHITBY:
        p->nothitby_attr = SYM(p, c, MG_S_NOTHITBY_ATTR);
        p->nothitby_time = PIV(p, c, MG_P_NOTHITBY_TIME, 1);
        break;
    case MG_CT_HITBY:
        p->nothitby_attr = (u16)~SYM(p, c, MG_S_HITBY_ATTR) & 0x0777;
        p->nothitby_time = PIV(p, c, MG_P_HITBY_TIME, 1);
        break;
    case MG_CT_HITDEF:
        read_hitdef(p, c, 0, &p->hd);
        p->hitdef_active = 1;
        break;
    case MG_CT_PROJECTILE: spawn_projectile(p, c); break;
    case MG_CT_SUPERPAUSE:
        mg_fight.pause_time = PIV(p, c, MG_P_SUPERPAUSE_TIME, 30);
        mg_fight.pause_movetime = PIV(p, c, MG_P_SUPERPAUSE_MOVETIME, 0);
        mg_fight.pause_owner = p->side;
        p->power += PIV(p, c, MG_P_SUPERPAUSE_POWERADD, 0);
        if (SYM(p, c, MG_S_SUPERPAUSE_SOUND) >= 0) MG_playSound(p, SYM(p, c, MG_S_SUPERPAUSE_SOUND));
        if (SYM(p, c, MG_S_SUPERPAUSE_ANIM) >= 0)
            MG_spawnExplod(p, SYM(p, c, MG_S_SUPERPAUSE_ANIM),
                           p->x + MG_FACE(PV(p, c, MG_P_SUPERPAUSE_POS_X), p->facing),
                           p->y + PV(p, c, MG_P_SUPERPAUSE_POS_Y), -2, -1, p->facing);
        break;
    case MG_CT_TARGETBIND:
        if (p->target) {
            p->bind_time = PIV(p, c, MG_P_TARGETBIND_TIME, 1);
            p->bind_x = PV(p, c, MG_P_TARGETBIND_POS_X);
            p->bind_y = PV(p, c, MG_P_TARGETBIND_POS_Y);
        }
        break;
    case MG_CT_TARGETSTATE:
        if (p->target) {
            p->target->sdef = p->sdef;            /* alvo passa a rodar estados do atacante */
            MG_changeState(p->target, PIV(p, c, MG_P_TARGETSTATE_VALUE, 0), -1, -1);
        }
        break;
    case MG_CT_TARGETVELSET:
        if (p->target) {
            if (HAS(p, c, MG_P_TARGETVELSET_X)) p->target->vx = PV(p, c, MG_P_TARGETVELSET_X);
            if (HAS(p, c, MG_P_TARGETVELSET_Y)) p->target->vy = PV(p, c, MG_P_TARGETVELSET_Y);
        }
        break;
    case MG_CT_TARGETLIFEADD:
        if (p->target) p->target->life += PIV(p, c, MG_P_TARGETLIFEADD_VALUE, 0);
        break;
    case MG_CT_TARGETDROP: p->target = 0; p->bind_time = 0; break;
    case MG_CT_HITVELSET:
        if (PIV(p, c, MG_P_HITVELSET_X, 1)) p->vx = p->gh_vx;
        if (PIV(p, c, MG_P_HITVELSET_Y, 1)) p->vy = p->gh_vy;
        break;
    case MG_CT_HITFALLVEL:
        if (p->gh_fall) { p->vx = p->gh.fall_xvel; p->vy = p->gh.fall_yvel; }
        break;
    case MG_CT_HITFALLDAMAGE: break;              /* fall.damage nao modelado (README) */
    case MG_CT_HITFALLSET: {
        s16 v = PIV(p, c, MG_P_HITFALLSET_VALUE, -1);
        if (v >= 0) p->gh_fall = v;
        break;
    }
    case MG_CT_ENVSHAKE: mg_fight.screen_shake = PIV(p, c, MG_P_ENVSHAKE_TIME, 10); break;
    case MG_CT_EXPLOD: {
        s16 anim = PIV(p, c, MG_P_EXPLOD_ANIM, -1);
        if (anim >= 0)
            MG_spawnExplod(p, anim, p->x + MG_FACE(PV(p, c, MG_P_EXPLOD_POS_X), p->facing),
                           p->y + PV(p, c, MG_P_EXPLOD_POS_Y), PIV(p, c, MG_P_EXPLOD_REMOVETIME, -2),
                           PIV(p, c, MG_P_EXPLOD_ID, -1), p->facing);
        break;
    }
    case MG_CT_REMOVEEXPLOD: {
        s16 id = PIV(p, c, MG_P_REMOVEEXPLOD_ID, -1);
        for (u8 i = 0; i < MG_MAX_EXPLOD; i++)
            if (mg_fight.explod[i].active && mg_fight.explod[i].bind_owner == p->side &&
                (id < 0 || mg_fight.explod[i].id == id)) mg_fight.explod[i].removetime = 0;
        break;
    }
    case MG_CT_HELPER: {
        if (p->is_helper) break;                  /* helpers nao criam helpers (limite do runtime) */
        MgPlayer *h = &mg_fight.helper[p->side];
        MgDraw keep = h->dr;
        memset(h, 0, sizeof(*h));
        h->dr = keep;
        h->def = h->sdef = p->def;
        h->enemy = p->enemy;
        h->side = p->side;
        h->pal = p->pal;
        h->is_helper = 1;
        h->parent = p;
        h->helper_id = PIV(p, c, MG_P_HELPER_ID, 0);
        h->facing = p->facing;
        mgfx px = PV(p, c, MG_P_HELPER_POS_X), py = PV(p, c, MG_P_HELPER_POS_Y);
        switch (SYM(p, c, MG_S_HELPER_POSTYPE)) {
        case 1: h->x = p->enemy->x + MG_FACE(px, p->facing); h->y = p->enemy->y + py; break;
        case 4: h->x = FXI(mg_fight.camx) + px; h->y = py; break;
        case 5: h->x = FXI(mg_fight.camx + 320) + px; h->y = py; break;
        default: h->x = p->x + MG_FACE(px, p->facing); h->y = p->y + py; break;
        }
        h->life = p->def->consts->life >> MG_FX_SHIFT;
        h->statetype = 'S'; h->movetype = 'I'; h->physics = 'N';
        h->stateno = -1;
        mg_fight.helper_active[p->side] = 1;
        MG_changeState(h, PIV(p, c, MG_P_HELPER_STATENO, 0), 0, -1);
        break;
    }
    case MG_CT_DESTROYSELF:
        if (p->is_helper) mg_fight.helper_active[p->side] = 0;
        break;
    default: break;                                /* null, width, assertspecial */
    }
}

/* Estado -1: visita so os controladores liberados pelos comandos ativos (bitmap gerado pelo
 * compilador) + os sem portao, na ordem original. Equivalente a varrer todos com o portao. */
static void run_minus1(MgPlayer *p)
{
    const MgCharDef *d = p->def;
    const MgState *s = &d->states[d->st_minus1];
    u8 words = d->neg1_words;
    u32 m[8];
    if (words > 8) words = 8;
    const u32 *ung = d->neg1_masks + (u16)d->ncmds * d->neg1_words;
    for (u8 k = 0; k < words; k++) m[k] = ung[k];
    for (u8 j = 0; j < p->nlive; j++) {
        const u32 *r = d->neg1_masks + (u16)p->live[j] * d->neg1_words;
        for (u8 k = 0; k < words; k++) m[k] |= r[k];
    }
    /* visita so os bits ligados, em ordem crescente (= ordem original dos controladores) */
    const MgCtrl *base = &d->ctrls[s->first_ctrl];
    for (u8 k = 0; k < words; k++) {
        u32 bits = m[k];
        while (bits) {
            u32 t = bits;
            u8 bi = 0;
            if (!(t & 0xFFFF)) { t >>= 16; bi += 16; }
            if (!(t & 0xFF)) { t >>= 8; bi += 8; }
            if (!(t & 0xF)) { t >>= 4; bi += 4; }
            if (!(t & 0x3)) { t >>= 2; bi += 2; }
            if (!(t & 0x1)) bi += 1;
            bits &= bits - 1;
            u16 i = (u16)k * 32 + bi;
            if (i >= s->nctrl) return;
            const MgCtrl *c = base + i;
            if (!MG_eval(p, c->cond)) continue;
            exec(p, c);
            if (p->state_changed) return;
        }
    }
}

static void run_state(MgPlayer *p, s16 idx)
{
    const MgState *s = &p->sdef->states[idx];
    const MgCtrl *c = &p->sdef->ctrls[s->first_ctrl];
    u8 own = p->sdef == p->def;
    for (u16 i = 0; i < s->nctrl; i++, c++) {
        /* portoes exatos gerados pelo compilador (condicoes necessarias baratas) */
        if (c->tkind == 1 && p->time != c->tval) continue;
        if (c->tkind == 2 && (p->elem + 1 != c->tval || p->elem_time != 0)) continue;
        if (c->gate != MG_NONE) {
            const u8 *g = p->sdef->gates + c->gate;
            u8 n = *g++, any = 0;
            if (own) while (n--) if (p->cmd_timer[*g++]) { any = 1; break; }
            if (!any) continue;
        }
        if (!MG_eval(p, c->cond)) continue;
        exec(p, c);
        if (p->state_changed) return;          /* ChangeState aborta o resto do estado antigo */
    }
}

/* ------------------------------------------------------------------ comandos */
static const u16 KEY_MASK[16] = {
    0, MG_IN_F, MG_IN_B, MG_IN_U, MG_IN_D, MG_IN_D | MG_IN_F, MG_IN_D | MG_IN_B, MG_IN_U | MG_IN_F,
    MG_IN_U | MG_IN_B, MG_IN_A, MG_IN_BB, MG_IN_C, MG_IN_X, MG_IN_Y, MG_IN_Z, MG_IN_S };
#define key_mask(k) KEY_MASK[(k) & 15]

#define DIRS (MG_IN_U | MG_IN_D | MG_IN_B | MG_IN_F)

static u8 key_down(u16 in, const MgCmdKey *k)
{
    u16 m = key_mask(k->key);
    if (k->key >= MG_K_A) return (in & m) == m;
    if (k->mods & MG_KEY_4WAY) return (in & m) == m;          /* $F aceita DF/UF */
    return (in & DIRS) == m;                                   /* direcao exata */
}

/* evento de um passo no tick t do historico (hist[0] = agora):
 *   /tecla  = segurada em t;  ~tecla = soltou em t (carga: segurou reltime ticks antes);
 *   tecla   = pressionou em t (todas as teclas do passo seguras, ao menos uma com borda). */
static u8 step_at(const MgPlayer *p, const MgCmdStep *st, s16 t)
{
    const MgCharDef *d = p->def;
    u16 now = HIST(p, t), before = (t + 1 < p->hist_len) ? HIST(p, t + 1) : 0;
    u8 edge = 0, need_edge = 0;
    for (u8 ki = 0; ki < st->nkeys; ki++) {
        const MgCmdKey *k = &d->keys[st->first_key + ki];
        u8 dn = key_down(now, k), was = key_down(before, k);
        if (k->mods & MG_KEY_HOLD) {
            if (!dn) return 0;
        } else if (k->mods & MG_KEY_REL) {
            if (!was || dn) return 0;
            if (k->reltime) {
                u16 held = 0;
                for (s16 j = t + 1; j < p->hist_len && key_down(HIST(p, j), k); j++) held++;
                if (held < k->reltime) return 0;
            }
        } else {
            if (!dn) return 0;
            need_edge = 1;
            if (!was) edge = 1;
        }
    }
    return !need_edge || edge;
}

/* Reconhecedor incremental guiado por eventos (como os motores de luta).
 * Cada comando guarda o proximo passo e a idade da sequencia. Por tick so sao visitados:
 * comandos em andamento, comandos cujo 1o passo reage a uma tecla que teve evento (indice
 * cmd_bucket gerado pelo compilador) e comandos de "segurar". Passos consecutivos podem
 * ocorrer no mesmo tick se as teclas diferem. Divergencia declarada: casamento guloso. */
static u8 s_fired;

static void cmd_fire(MgPlayer *p, u8 i)
{
    s_fired = 1;
    const MgCommand *cm = &p->def->cmds[i];
    if (!p->cmd_timer[i] && p->nlive < MG_MAX_LIVE) p->live[p->nlive++] = i;
    p->cmd_timer[i] = cm->buffer_time ? cm->buffer_time : 1;
}

static u8 dir_code(u16 in)
{
    switch (in & DIRS) {
    case MG_IN_F: return MG_K_F; case MG_IN_B: return MG_K_B; case MG_IN_U: return MG_K_U; case MG_IN_D: return MG_K_D;
    case MG_IN_D | MG_IN_F: return MG_K_DF; case MG_IN_D | MG_IN_B: return MG_K_DB;
    case MG_IN_U | MG_IN_F: return MG_K_UF; case MG_IN_U | MG_IN_B: return MG_K_UB;
    }
    return 0;
}

/* contexto do tick para o teste rapido de passos de uma tecla */
static u8 s_dir_now, s_dir_prev;
static u16 s_in_now, s_in_prev;

/* passo com uma tecla sem modificador especial: teste inline (sem step_at) */
static u8 step_fast(const MgPlayer *p, const MgCmdStep *st)
{
    if (st->nkeys != 1) return step_at(p, st, 0);
    const MgCmdKey *k = &p->def->keys[st->first_key];
    if (k->mods & (MG_KEY_4WAY | MG_KEY_REL | MG_KEY_HOLD)) return step_at(p, st, 0);
    if (k->key >= MG_K_A) {
        u16 m = key_mask(k->key);
        return (s_in_now & m) && !(s_in_prev & m);
    }
    return s_dir_now == k->key && s_dir_prev != k->key;
}

/* tenta avancar o comando i neste tick; devolve a nova posicao */
static u8 cmd_advance(MgPlayer *p, u8 i, u16 ev)
{
    const MgCharDef *d = p->def;
    const MgCommand *cm = &d->cmds[i];
    u8 pos = p->cmd_pos[i];
    const MgCmdStep *st = &d->steps[cm->first_step + pos];
    if (((st->kmask & ev) || (st->strict & MG_STEP_HOLD_ONLY)) && step_fast(p, st)) {
        if (pos == 0) p->cmd_age[i] = 0;
        pos++;
        while (pos < cm->nsteps) {
            const MgCmdStep *nx = &d->steps[cm->first_step + pos];
            const MgCmdStep *pv = nx - 1;
            if (nx->nkeys == pv->nkeys && d->keys[nx->first_key].key == d->keys[pv->first_key].key) break;
            if (!((nx->kmask & ev) || (nx->strict & MG_STEP_HOLD_ONLY)) || !step_fast(p, nx)) break;
            pos++;
        }
    } else if (pos) {
        const MgCmdStep *s0 = &d->steps[cm->first_step];
        if (((s0->kmask & ev) || (s0->strict & MG_STEP_HOLD_ONLY)) && step_fast(p, s0)) { pos = 1; p->cmd_age[i] = 0; }
    }
    if (pos >= cm->nsteps) { cmd_fire(p, i); pos = 0; }
    return pos;
}

static void track(MgPlayer *p, u8 i, u8 old, u8 pos)
{
    p->cmd_pos[i] = pos;
    if (!old && pos && p->nprog < MG_MAX_PROG) p->prog[p->nprog++] = i;
}

static void update_hold_only(MgPlayer *p, u16 in)
{
    p->hist_head = (p->hist_head + 1) & (MG_INPUT_HIST - 1);
    p->hist[p->hist_head] = in;
    if (p->hist_len < MG_INPUT_HIST) p->hist_len++;
    const MgCharDef *d = p->def;
    u8 w = 0;
    for (u8 j = 0; j < p->nlive; j++) {
        u8 i = p->live[j];
        if (--p->cmd_timer[i]) p->live[w++] = i;
    }
    p->nlive = w;
    u16 prev = p->hist_len > 1 ? HIST(p, 1) : 0;
    s_in_now = in; s_in_prev = prev;
    s_dir_now = dir_code(in); s_dir_prev = dir_code(prev);
    u8 nh = d->nhold_cmds < 32 ? d->nhold_cmds : 32;
    if (in != prev || p->hist_len < 2) {
        u32 ok = 0;
        for (u8 j = 0; j < nh; j++) {
            u8 i = d->hold_cmds[j];
            const MgCommand *cm = &d->cmds[i];
            if (cm->nsteps != 1) continue;             /* so comandos de um passo de segurar */
            s_fired = 0;
            if (step_at(p, &d->steps[cm->first_step], 0)) cmd_fire(p, i);
            if (s_fired) ok |= 1UL << j;
        }
        p->hold_ok = ok;
    } else {
        for (u8 j = 0; j < nh; j++)
            if (p->hold_ok & (1UL << j)) cmd_fire(p, d->hold_cmds[j]);
    }
}

static void update_commands(MgPlayer *p, u16 in)
{
    MG_PROF_BEGIN();
    p->hist_head = (p->hist_head + 1) & (MG_INPUT_HIST - 1);
    p->hist[p->hist_head] = in;
    if (p->hist_len < MG_INPUT_HIST) p->hist_len++;
    const MgCharDef *d = p->def;

    /* buffers ativos */
    u8 w = 0;
    for (u8 j = 0; j < p->nlive; j++) {
        u8 i = p->live[j];
        if (--p->cmd_timer[i]) p->live[w++] = i;
    }
    p->nlive = w;

    /* eventos deste tick: codigos MG_K_* de direcao (saida/entrada) e botoes que mudaram */
    u16 prev = p->hist_len > 1 ? HIST(p, 1) : 0;
    s_in_now = in; s_in_prev = prev;
    s_dir_now = dir_code(in); s_dir_prev = dir_code(prev);
    u16 ev = 0;
    if ((prev ^ in) & DIRS) ev |= (1 << dir_code(prev)) | (1 << dir_code(in));
    u16 bchg = (prev ^ in) & ~DIRS;
    if (bchg & MG_IN_A) ev |= 1 << MG_K_A;
    if (bchg & MG_IN_BB) ev |= 1 << MG_K_B_BTN;
    if (bchg & MG_IN_C) ev |= 1 << MG_K_C;
    if (bchg & MG_IN_X) ev |= 1 << MG_K_X;
    if (bchg & MG_IN_Y) ev |= 1 << MG_K_Y;
    if (bchg & MG_IN_Z) ev |= 1 << MG_K_Z;
    if (bchg & MG_IN_S) ev |= 1 << MG_K_S;
    ev &= ~1;
    MG_PROF_MARK(8);

    /* 1) em andamento: timeout, proximo passo ou recomeco */
    w = 0;
    u8 n = p->nprog;
    for (u8 j = 0; j < n; j++) {
        u8 i = p->prog[j];
        u8 pos = p->cmd_pos[i];
        if (!pos) continue;
        if (++p->cmd_age[i] > d->cmds[i].time) pos = 0;
        if (pos && !ev) {                  /* sem evento: so passo de segurar pode avancar */
            const MgCmdStep *nx = &d->steps[d->cmds[i].first_step + pos];
            if (!(nx->strict & MG_STEP_HOLD_ONLY)) { p->prog[w++] = i; continue; }
        }
        p->cmd_pos[i] = pos;
        pos = cmd_advance(p, i, ev);
        p->cmd_pos[i] = pos;
        if (pos) p->prog[w++] = i;
    }
    p->nprog = w;

    /* 2) comecos: comandos cujo 1o passo reage aos eventos deste tick */
    if (ev) {
        for (u8 code = 1; code < 16; code++) {
            if (!(ev & (1 << code))) continue;
            for (u16 j = d->cmd_bucket_first[code]; j < d->cmd_bucket_first[code + 1]; j++) {
                u8 i = d->cmd_bucket[j];
                if (p->cmd_pos[i] || p->cmd_timer[i] == d->cmds[i].buffer_time) continue;   /* ja tratado */
                track(p, i, 0, cmd_advance(p, i, ev));
            }
        }
    }
    /* 3) comandos de segurar (ex.: holdfwd = /$F): so muda quando a entrada muda */
    u8 nh = d->nhold_cmds < 32 ? d->nhold_cmds : 32;
    if (in != prev || p->hist_len < 2) {
        u32 ok = 0;
        for (u8 j = 0; j < nh; j++) {
            u8 i = d->hold_cmds[j];
            if (p->cmd_pos[i]) continue;
            s_fired = 0;
            track(p, i, 0, cmd_advance(p, i, ev));
            if (s_fired) ok |= 1UL << j;
        }
        p->hold_ok = ok;
    } else {
        for (u8 j = 0; j < nh; j++)
            if (p->hold_ok & (1UL << j)) cmd_fire(p, d->hold_cmds[j]);
    }
    MG_PROF_MARK(9);
}

/* pad (SGDK) -> bits relativos a frente */
static u16 pad_to_rel(u16 pad, s8 facing)
{
    u16 r = 0;
    if (pad & BUTTON_UP) r |= MG_IN_U;
    if (pad & BUTTON_DOWN) r |= MG_IN_D;
    if (pad & BUTTON_RIGHT) r |= facing > 0 ? MG_IN_F : MG_IN_B;
    if (pad & BUTTON_LEFT) r |= facing > 0 ? MG_IN_B : MG_IN_F;
    /* layout 6 botoes: A B C = chutes (a b c), X Y Z = socos (x y z), START = s */
    if (pad & BUTTON_A) r |= MG_IN_A;
    if (pad & BUTTON_B) r |= MG_IN_BB;
    if (pad & BUTTON_C) r |= MG_IN_C;
    if (pad & BUTTON_X) r |= MG_IN_X;
    if (pad & BUTTON_Y) r |= MG_IN_Y;
    if (pad & BUTTON_Z) r |= MG_IN_Z;
    if (pad & BUTTON_START) r |= MG_IN_S;
    return r;
}

/* ------------------------------------------------------------------ transicoes do motor */
static u8 cmd(const MgPlayer *p, u16 idx) { return idx != MG_NONE && p->cmd_timer[idx]; }

static void engine_auto_transitions(MgPlayer *p)
{
    if (!p->ctrl || p->movetype != 'I') return;
    const MgCharDef *d = p->def;
    u8 up = cmd(p, d->cmd_holdup), down = cmd(p, d->cmd_holddown);
    u8 fwd = cmd(p, d->cmd_holdfwd), back = cmd(p, d->cmd_holdback);
    MgPlayer *e = p->enemy;
    u8 threat = e->movetype == 'A';
    for (u8 i = 0; i < MG_MAX_PROJ && !threat; i++) threat = e->proj[i].active;
    if (p->statetype == 'S') {
        if (back && threat && p->stateno != 130) { MG_changeState(p, 120, -1, -1); return; }
        if (p->stateno != 0 && p->stateno != 20) return;
        if (up) MG_changeState(p, 40, -1, -1);
        else if (down) MG_changeState(p, 10, -1, -1);
        else if ((fwd || back) && p->stateno != 20) MG_changeState(p, 20, -1, -1);
    } else if (p->statetype == 'C') {
        if (back && threat && p->stateno != 131) { MG_changeState(p, 120, -1, -1); return; }
        if (p->stateno != 11 && p->stateno != 10) return;   /* soltar baixo tambem interrompe o agachar */
        if (up) MG_changeState(p, 40, -1, -1);
        else if (!down) MG_changeState(p, 12, -1, -1);
    } else if (p->statetype == 'A') {
        if (back && threat && p->stateno != 132 && (p->stateno == 50)) MG_changeState(p, 120, -1, -1);
    }
}

/* ------------------------------------------------------------------ tick */
void MG_playerInput(MgPlayer *p, u16 pad)
{
    if (p->is_helper) return;
    u16 in = p->is_cpu ? MG_cpuInput(p) : pad_to_rel(pad, p->facing);
    p->in_prev = p->in_raw;
    p->in_raw = in;
    if (!p->is_cpu) { update_commands(p, in); return; }
    /* CPU: sem reconhecimento de sequencias; ativa o comando escolhido pela IA */
    update_hold_only(p, in);
    if (p->ai_cmd >= 0 && p->ai_cmd < (s16)p->def->ncmds) cmd_fire(p, (u8)p->ai_cmd);
}

void MG_playerLogic(MgPlayer *p)
{
    if (p->hitpause > 0) { p->hitpause--; return; }
    if (p->hitshake > 0) { p->hitshake--; }
    else if (p->hittime_left > 0) p->hittime_left--;
    if (p->nothitby_time > 0) p->nothitby_time--;
    if (p->movecontact) p->movecontact++;
    if (p->movehit) p->movehit++;
    if (p->moveguarded) p->moveguarded++;

    /* auto-turn (MUGEN: parado/agachado com ctrl vira para o oponente) */
    if (p->ctrl && p->statetype != 'A' && p->movetype == 'I' && MG_FACE(p->enemy->x - p->x, p->facing) < 0)
        p->facing = -p->facing;

    /* regra do motor MUGEN: deitado (5110) e vivo por liedown.time ticks -> levantar (5120) */
    if (p->stateno == 5110 && p->life > 0 && p->time >= (p->def->consts->liedown_time >> MG_FX_SHIFT))
        MG_selfState(p, 5120);

    /* ordem MUGEN: -3, -2, -1 (comandos) sempre; so entao as transicoes automaticas do motor */
    MG_PROF_BEGIN();
    p->state_changed = 0;
    if (p->sdef == p->def && !p->is_helper) {    /* negativos: nao em custom state nem em helper */
        if (p->def->st_minus3 >= 0) run_state(p, p->def->st_minus3);
        if (p->def->st_minus2 >= 0 && !p->state_changed) run_state(p, p->def->st_minus2);
        if (p->def->st_minus1 >= 0 && !p->state_changed) run_minus1(p);
        MG_PROF_MARK(10);
        if (!p->state_changed) engine_auto_transitions(p);
        MG_PROF_MARK(12);
    }
    /* estado atual; se mudou, o novo roda no mesmo tick (limite anti-loop) */
    for (u8 guard = 0; guard < 6; guard++) {
        p->state_changed = 0;
        run_state(p, p->state_idx);
        if (!p->state_changed) break;
    }
    MG_PROF_MARK(11);
}

void MG_playerPhysics(MgPlayer *p)
{
    const MgConsts *k = p->def->consts;
    if (p->hitpause > 0) return;
    if (p->bind_time > 0 && p->target) {
        MgPlayer *t = p->target;
        t->x = p->x + MG_FACE(p->bind_x, p->facing);
        t->y = p->y + p->bind_y;
        p->bind_time--;
    }
    if (!p->posfreeze && p->hitshake <= 0) {
        p->x += MG_FACE(p->vx, p->facing);
        p->y += p->vy;
    }
    p->posfreeze = 0;
    switch (p->physics) {
    case 'S': p->vx = (p->vx * (k->stand_friction >> 2)) >> (MG_FX_SHIFT - 2); break;
    case 'C': p->vx = (p->vx * (k->crouch_friction >> 2)) >> (MG_FX_SHIFT - 2); break;
    case 'A':
        p->vy += k->yaccel;
        if (p->y >= 0 && p->vy > 0) {       /* pouso automatico do motor */
            p->y = 0;
            p->vy = 0;
            MG_changeState(p, 52, -1, -1);
        }
        break;
    default: break;
    }
    /* so fisica S/C prende ao chao; N (quedas, deitado) e livre como no MUGEN */
    if ((p->physics == 'S' || p->physics == 'C') && p->statetype != 'A') {
        if (p->y > 0 || (p->y < 0 && p->vy >= 0)) {
            p->y = 0;
            if (p->vy > 0) p->vy = 0;
        }
    }
    anim_step(&p->anim_idx, &p->elem, &p->elem_time, &p->anim_time, p->def);
    p->time++;
}

void MG_projStep(MgPlayer *p, MgProj *pr)
{
    if (!pr->active) return;
    if (pr->contact_time >= 0) pr->contact_time++;
    pr->x += MG_FACE(pr->vx, pr->facing);
    pr->y += pr->vy;
    pr->vx += pr->ax;
    pr->vy += pr->ay;
    s32 at = 0;
    anim_step(&pr->anim_idx, &pr->elem, &pr->elem_time, &at, p->def);
    if (pr->removetime > 0) pr->removetime--;
    const MgAnim *a = &p->def->anims[pr->anim_idx];
    u8 anim_over = pr->elem == 0 && pr->elem_time == 0 && a->count > 0 && a->loopstart == 0 && pr->removing;
    if (pr->removetime == 0 || anim_over) pr->active = 0;
    s32 sx = (pr->x >> MG_FX_SHIFT) - mg_fight.camx;
    if (sx < -160 || sx > 480) pr->active = 0;
}

void MG_explodStep(MgExplod *e, const MgPlayer *owner)
{
    if (!e->active) return;
    const MgAnim *a = &owner->def->anims[e->anim_idx];
    u8 last = e->elem == a->count - 1;
    const MgAnimFrame *f = &owner->def->frames[a->first + e->elem];
    anim_step(&e->anim_idx, &e->elem, &e->elem_time, &e->anim_time, owner->def);
    e->x += MG_FACE(e->vx, e->facing);
    e->y += e->vy;
    if (e->removetime == -2) {              /* ate o fim da animacao */
        if (last && f->time >= 0 && e->elem_time == 0) e->active = 0;
    } else if (e->removetime > 0) {
        if (--e->removetime == 0) e->active = 0;
    } else if (e->removetime == 0) e->active = 0;
}

void MG_selfState(MgPlayer *p, s16 no)
{
    p->sdef = p->def;
    MG_changeState(p, no, -1, -1);
}
