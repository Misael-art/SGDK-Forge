/* COPIADO de tools/mugen2sgdk_forge/runtime/mg_vm.c (v0.3.0). Edite na fonte. */
/* mg_vm.c -- VM de expressoes (espelho de mugen2sgdk_forge/ir/vm.py). Ponto fixo 24.8. */
#include "mg/mg_runtime.h"
#include "mg/mg_ops.h"

#define STACK 16
#define FXI(v) ((mgfx)(v) << MG_FX_SHIFT)

static mgfx fx_mul(mgfx a, mgfx b)
{
    /* 24.8 * 24.8: separa parte inteira para nao estourar 32 bits */
    s32 ai = a >> MG_FX_SHIFT, af = a & (MG_FX - 1);
    return ai * b + ((af * b) >> MG_FX_SHIFT);
}

static mgfx fx_div(mgfx a, mgfx b)
{
    if (b == 0) return 0;
    u8 neg = (a < 0) != (b < 0);
    u32 ua = a < 0 ? -a : a, ub = b < 0 ? -b : b;
    u32 q = (ua / ub) << MG_FX_SHIFT;
    u32 r = ua % ub;
    q += (r << MG_FX_SHIFT) / ub;         /* r < ub; r<<8 cabe se ub < 2^23 */
    return neg ? -(mgfx)q : (mgfx)q;
}

static s32 elem_start(const MgPlayer *p, s16 elem1)
{
    const MgAnim *a = &p->def->anims[p->anim_idx];
    const MgAnimFrame *f = &p->def->frames[a->first];
    s32 t = 0;
    for (s16 i = 0; i < elem1 - 1 && i < a->count; i++) {
        if (f[i].time < 0) return 0x7FFF;
        t += f[i].time;
    }
    return t;
}

s16 MG_animElemTime(const MgPlayer *p, s16 elem1)
{
    const MgAnim *a = &p->def->anims[p->anim_idx];
    if (elem1 < 1 || elem1 > a->count) return -1;
    s32 d = p->anim_time - elem_start(p, elem1);
    if (d > 32767) d = 32767;
    if (d < -32768) d = -32768;
    return (s16)d;
}

s32 MG_animTime(const MgPlayer *p)
{
    const MgAnim *a = &p->def->anims[p->anim_idx];
    if (a->total < 0) return -1;             /* infinito: nunca chega a 0 */
    /* MUGEN: AnimTime = 0 no ultimo tick do ciclo (antes do loop) */
    return p->anim_time + 1 - a->total;
}

static s16 elem_at(const MgPlayer *p, s32 ahead)
{
    const MgAnim *a = &p->def->anims[p->anim_idx];
    const MgAnimFrame *f = &p->def->frames[a->first];
    s32 t = p->anim_time + ahead, acc = 0;
    for (u8 i = 0; i < a->count; i++) {
        if (f[i].time < 0) return i + 1;
        acc += f[i].time;
        if (t < acc) return i + 1;
    }
    return a->count;
}

static mgfx trg(const MgPlayer *p, u8 id)
{
    const MgPlayer *e = p->enemy;
    switch (id) {
    case MG_TRG_TIME: return FXI(p->time);
    case MG_TRG_ANIMTIME: return FXI(MG_animTime(p));
    case MG_TRG_STATENO: return FXI(p->stateno);
    case MG_TRG_PREVSTATENO: return FXI(p->prevstateno);
    case MG_TRG_STATETYPE: return FXI(p->statetype);
    case MG_TRG_MOVETYPE: return FXI(p->movetype);
    case MG_TRG_CTRL: return FXI(p->ctrl);
    case MG_TRG_ANIM: return FXI(p->anim_id);
    case MG_TRG_MOVECONTACT: return FXI(p->movecontact);
    case MG_TRG_MOVEHIT: return FXI(p->movehit);
    case MG_TRG_MOVEGUARDED: return FXI(p->moveguarded);
    case MG_TRG_MOVEREVERSED: return 0;
    case MG_TRG_HITCOUNT: return FXI(p->hitcount);
    case MG_TRG_POWER: return FXI(p->power);
    case MG_TRG_POWERMAX: return FXI(3000);
    case MG_TRG_LIFE: return FXI(p->life);
    case MG_TRG_LIFEMAX: return p->def->consts->life;
    case MG_TRG_ALIVE: return FXI(p->life > 0);
    case MG_TRG_VEL_X: return p->vx;
    case MG_TRG_VEL_Y: return p->vy;
    case MG_TRG_POS_X: return p->x - FXI(mg_fight.camx + 160);
    case MG_TRG_POS_Y: return p->y;
    case MG_TRG_P2BODYDIST_X: {
        mgfx d = MG_FACE(e->x - p->x, p->facing);
        mgfx w = p->def->consts->ground_front + e->def->consts->ground_front;
        return d - w;
    }
    case MG_TRG_P2BODYDIST_Y: return e->y - p->y;
    case MG_TRG_P2DIST_X: return MG_FACE(e->x - p->x, p->facing);
    case MG_TRG_P2DIST_Y: return e->y - p->y;
    case MG_TRG_P2LIFE: return FXI(e->life);
    case MG_TRG_P2STATENO: return FXI(e->stateno);
    case MG_TRG_P2STATETYPE: return FXI(e->statetype);
    case MG_TRG_P2MOVETYPE: return FXI(e->movetype);
    case MG_TRG_P2CTRL: return FXI(e->ctrl);
    case MG_TRG_FACING: return FXI(p->facing);
    case MG_TRG_RANDOM: return FXI(random() % 1000);
    case MG_TRG_ROUNDSTATE: return FXI(mg_fight.round_state + 1);
    case MG_TRG_MATCHOVER: return FXI(mg_fight.round_state == 3);
    case MG_TRG_WIN: return FXI(mg_fight.round_state >= 2 && e->life <= 0 && p->life > 0);
    case MG_TRG_WINKO: return FXI(mg_fight.round_state >= 2 && e->life <= 0 && p->life > 0);
    case MG_TRG_LOSE: return FXI(mg_fight.round_state >= 2 && p->life <= 0);
    case MG_TRG_FRONTEDGEBODYDIST:
    case MG_TRG_FRONTEDGEDIST: {
        s32 edge = p->facing > 0 ? (mg_fight.camx + 320) : mg_fight.camx;
        return MG_FACE(FXI(edge) - p->x, p->facing);
    }
    case MG_TRG_BACKEDGEBODYDIST:
    case MG_TRG_BACKEDGEDIST: {
        s32 edge = p->facing > 0 ? mg_fight.camx : (mg_fight.camx + 320);
        return MG_FACE(p->x - FXI(edge), p->facing);
    }
    case MG_TRG_HITSHAKEOVER: return FXI(p->hitshake <= 0);
    case MG_TRG_HITOVER: return FXI(p->hitshake <= 0 && p->hittime_left <= 0);
    case MG_TRG_HITFALL: return FXI(p->gh_fall);
    case MG_TRG_CANRECOVER: return FXI(p->gh.fall_recover);
    case MG_TRG_INGUARDDIST: {
        if (e->movetype != 'A') {
            for (u8 i = 0; i < MG_MAX_PROJ; i++) if (e->proj[i].active) return FXI(1);
            return 0;
        }
        mgfx d = MG_FACE(e->x - p->x, p->facing);
        return FXI(d >= 0 && d < FXI(160));
    }
    case MG_TRG_ANIMELEMNO_CUR: return FXI(p->elem + 1);
    case MG_TRG_GAMETIME: return FXI(mg_fight.ticks);
    case MG_TRG_ROUNDNO: return FXI(mg_fight.round_no);
    case MG_TRG_NUMENEMY: return FXI(1);
    case MG_TRG_AILEVEL: return FXI(p->is_cpu ? 4 : 0);
    case MG_TRG_ISHELPER: return FXI(p->is_helper);
    case MG_TRG_NUMHELPER: return FXI(mg_fight.helper_active[p->side]);
    default: return 0;   /* numhelper, numexplod, ishelper: sem helpers -> 0 */
    }
}

static mgfx trga(const MgPlayer *p, u8 id, mgfx arg)
{
    s32 n = arg >> MG_FX_SHIFT;
    switch (id) {
    case MG_TRGA_VAR: return (n >= 0 && n < 60) ? FXI(p->vars[n]) : 0;
    case MG_TRGA_SYSVAR: return (n >= 0 && n < 5) ? FXI(p->vars[60 + n]) : 0;
    case MG_TRGA_FVAR: return (n >= 0 && n < 40) ? p->fvars[n] : 0;
    case MG_TRGA_SYSFVAR: return (n >= 0 && n < 5) ? p->fvars[40 + n] : 0;
    case MG_TRGA_ANIMELEMNO: return FXI(elem_at(p, n));
    case MG_TRGA_NUMPROJID: {
        s16 c = 0;
        for (u8 i = 0; i < MG_MAX_PROJ; i++) if (p->proj[i].active && (n <= 0 || p->proj[i].id == n)) c++;
        return FXI(c);
    }
    case MG_TRGA_PROJCONTACTTIME:
    case MG_TRGA_PROJHITTIME:
    case MG_TRGA_PROJGUARDEDTIME: {
        for (u8 i = 0; i < MG_MAX_PROJ; i++)
            if ((n <= 0 || p->proj[i].id == n) && p->proj[i].contact_time >= 0) return FXI(p->proj[i].contact_time);
        return FXI(-1);
    }
    case MG_TRGA_GETHITVAR:
        switch (n) {
        case MG_GHV_XVEL: return p->gh_vx;
        case MG_GHV_YVEL: return p->gh_vy;
        case MG_GHV_FALL_YVEL: return p->gh.fall_yvel;
        case MG_GHV_FALL: return FXI(p->gh_fall);
        case MG_GHV_HITTIME: return FXI(p->hittime_left);
        case MG_GHV_SLIDETIME: return FXI(p->gh.slidetime);
        case MG_GHV_CTRLTIME: return FXI(p->gh.gctrltime);
        case MG_GHV_ANIMTYPE: return FXI(p->y < 0 ? p->gh.air_animtype : p->gh.animtype);
        case MG_GHV_GROUNDTYPE: return FXI(p->gh.groundtype);
        case MG_GHV_AIRTYPE: return FXI(p->gh.airtype);
        case MG_GHV_DAMAGE: return FXI(p->gh.damage);
        case MG_GHV_HITSHAKETIME: return FXI(p->hitshake);
        case MG_GHV_YACCEL: return p->gh.yaccel;
        case MG_GHV_FALL_RECOVER: return FXI(p->gh.fall_recover);
        case MG_GHV_FALL_XVEL: return p->gh.fall_xvel;
        default: return 0;
        }
    case MG_TRGA_ANIMEXIST: return FXI(MG_findAnim(p->def, n) >= 0);
    case MG_TRGA_NUMHELPER: {
        const MgPlayer *o = p->is_helper ? p->parent : p;
        return FXI(mg_fight.helper_active[o->side] && (n <= 0 || mg_fight.helper[o->side].helper_id == n));
    }
    default: return 0;
    }
}

static mgfx eval_full(const MgPlayer *p, const u8 *c) __attribute__((noinline));

/* Frente leve do VM: constantes e var(n) sem pagar o prologo do interpretador.
 *
 * PORQUE: amostragem de PC no BlastEm (H-Int a cada 8 linhas) mediu MG_eval em
 * 13,9% do quadro com so ~15 chamadas por quadro: ~1100 ciclos cada, a maior
 * parte no prologo/epilogo (movem de 11 registros) e no despacho. Um terco das
 * chamadas era programa constante ("PUSH8 0; END" = trigger sempre falso, 3,4
 * por tick) que pagava o prologo inteiro para devolver um literal. */
mgfx MG_eval(const MgPlayer *p, u16 off)
{
    if (off == MG_NONE) return 0;
    const u8 *c = p->sdef->code + off;
    switch (c[0]) {
    case MG_OP_PUSH8:
        if (c[2] == MG_OP_END) return FXI((s8)c[1]);
        /* var(n) com n constante: PUSH8 n; TRGA VAR; END */
        if (c[2] == MG_OP_TRGA && c[3] == MG_TRGA_VAR && c[4] == MG_OP_END) {
            s8 n = (s8)c[1];
            return (n >= 0 && n < 60) ? FXI(p->vars[(u8)n]) : 0;
        }
        break;
    case MG_OP_PUSH16: if (c[3] == MG_OP_END) return FXI((s16)((c[1] << 8) | c[2])); break;
    case MG_OP_PUSHFX:
        if (c[5] == MG_OP_END)
            return (mgfx)(((u32)c[1] << 24) | ((u32)c[2] << 16) | ((u32)c[3] << 8) | c[4]);
        break;
    }
    return eval_full(p, c);
}

/* Pilha por ponteiro (s aponta para a proxima posicao livre; topo = s[-1]).
 *
 * PORQUE: com indice (st[sp - 1]) o gcc do 68000 recalculava endereco a cada
 * acesso (extensao de sinal + duas somas + modo indexado). A amostragem de PC
 * mostrou o interpretador como maior custo dos quadros acima do orcamento
 * (16% das amostras nesses quadros). Mesma semantica, byte a byte. */
static mgfx eval_full(const MgPlayer *p, const u8 *c)
{
    mgfx st[STACK];
    mgfx *s = st;
    mgfx *const lim = st + STACK;
    for (;;) {
        u8 op = *c++;
        mgfx a, b;
        switch (op) {
        case MG_OP_END: return s > st ? s[-1] : 0;
        case MG_OP_PUSH8: *s++ = FXI((s8)*c); c++; break;
        case MG_OP_PUSH16: *s++ = FXI((s16)((c[0] << 8) | c[1])); c += 2; break;
        case MG_OP_PUSHFX: *s++ = (mgfx)(((u32)c[0] << 24) | ((u32)c[1] << 16) | ((u32)c[2] << 8) | c[3]); c += 4; break;
        case MG_OP_TRG: *s++ = trg(p, *c++); break;
        case MG_OP_TRGA: s[-1] = trga(p, *c, s[-1]); c++; break;
        case MG_OP_CMD: *s++ = FXI(p->sdef == p->def && p->cmd_timer[*c] != 0); c++; break;
        case MG_OP_ANIMELEMTIME: s[-1] = FXI(MG_animElemTime(p, s[-1] >> MG_FX_SHIFT)); break;
        case MG_OP_UNSUPPORTED: *s++ = 0; c++; break;
        case MG_OP_ANDJ: {
            u16 rel = (c[0] << 8) | c[1];
            c += 2;
            if (s[-1] == 0) c += rel; else s--;
            break;
        }
        case MG_OP_ORJ: {
            u16 rel = (c[0] << 8) | c[1];
            c += 2;
            if (s[-1] != 0) { s[-1] = MG_FX; c += rel; } else s--;
            break;
        }
        case MG_OP_BOOL: s[-1] = s[-1] ? MG_FX : 0; break;
        case MG_OP_NEG: s[-1] = -s[-1]; break;
        case MG_OP_NOT: s[-1] = s[-1] ? 0 : MG_FX; break;
        case MG_OP_BNOT: s[-1] = FXI(~(s[-1] >> MG_FX_SHIFT)); break;
        case MG_OP_ABS: if (s[-1] < 0) s[-1] = -s[-1]; break;
        case MG_OP_FLOOR: s[-1] &= ~(MG_FX - 1); break;
        case MG_OP_INRANGE: {
            u8 fl = *c++;
            mgfx hi = *--s, lo = *--s, v = s[-1];
            u8 ok = ((fl & 1) ? v >= lo : v > lo) && ((fl & 2) ? v <= hi : v < hi);
            s[-1] = ok ? MG_FX : 0;
            break;
        }
        case MG_OP_IFELSE: {
            mgfx bb = *--s, aa = *--s, cc = s[-1];
            s[-1] = cc ? aa : bb;
            break;
        }
        default:
            b = *--s;
            a = s[-1];
            switch (op) {
            case MG_OP_ADD: a = a + b; break;
            case MG_OP_SUB: a = a - b; break;
            case MG_OP_MUL: a = fx_mul(a, b); break;
            case MG_OP_DIV: a = fx_div(a, b); break;
            case MG_OP_MOD: { s32 ia = a >> MG_FX_SHIFT, ib = b >> MG_FX_SHIFT; a = ib ? FXI(ia % ib) : 0; break; }
            case MG_OP_POW: { s32 n = b >> MG_FX_SHIFT; mgfx r = MG_FX; while (n-- > 0) r = fx_mul(r, a); a = r; break; }
            case MG_OP_EQ: a = (a == b) ? MG_FX : 0; break;
            case MG_OP_NE: a = (a != b) ? MG_FX : 0; break;
            case MG_OP_LT: a = (a < b) ? MG_FX : 0; break;
            case MG_OP_LE: a = (a <= b) ? MG_FX : 0; break;
            case MG_OP_GT: a = (a > b) ? MG_FX : 0; break;
            case MG_OP_GE: a = (a >= b) ? MG_FX : 0; break;
            case MG_OP_BAND: a = FXI((a >> MG_FX_SHIFT) & (b >> MG_FX_SHIFT)); break;
            case MG_OP_BOR: a = FXI((a >> MG_FX_SHIFT) | (b >> MG_FX_SHIFT)); break;
            case MG_OP_BXOR: a = FXI((a >> MG_FX_SHIFT) ^ (b >> MG_FX_SHIFT)); break;
            case MG_OP_LAND: a = (a && b) ? MG_FX : 0; break;
            case MG_OP_LOR: a = (a || b) ? MG_FX : 0; break;
            case MG_OP_LXOR: a = ((a != 0) != (b != 0)) ? MG_FX : 0; break;
            default: return 0;   /* opcode invalido: programa corrompido */
            }
            s[-1] = a;
            break;
        }
        if (s >= lim) return 0;
    }
}

s32 MG_evalInt(const MgPlayer *p, u16 off, s32 dflt)
{
    if (off == MG_NONE) return dflt;
    return MG_eval(p, off) >> MG_FX_SHIFT;
}
