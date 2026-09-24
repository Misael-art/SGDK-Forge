/* mg_fight.c -- luta 1x1: ordem do tick, colisao Clsn1 x Clsn2, acerto/defesa, projeteis,
 * explods, empurrao, camera, render, rounds, HUD transitorio e CPU. */
#include "mg_runtime.h"
#include "mg_ops.h"

#define FXI(v) ((mgfx)(v) << MG_FX_SHIFT)
#define FX2I(v) ((s16)((v) >> MG_FX_SHIFT))

MgFight mg_fight;
#ifdef MG_TEST_BREADCRUMB
char mg_crumbs[25];
u8 mg_crumb_i;
#endif
/* VRAM fixa por jogador (sem realocacao a cada troca de sheet); 0 = alocacao automatica */
static u16 s_vram[2];
/* efeitos de fundo: tiles pre-carregados apos os corpos; base por jogador/efeito (0 = sem espaco) */
#define MG_MAX_BGFX 4
static u16 s_bgfx_base[2][MG_MAX_BGFX];
static u16 s_pal0_saved[16];
static s8 s_bgfx_owner = -1;
#ifdef MG_PROFILE
u32 mg_prof[16];
#endif

#define STAGE_W        640      /* palco sem cenario convertido (E4): so limites */
#define FLOOR_Y        200      /* linha do chao na tela (px) */
#define ROUND_TIME     99
#define SPR_VRAM_TILES 900

/* ------------------------------------------------------------------ som / explod */
void MG_playSound(const MgPlayer *p, s16 idx)
{
    if (idx < 0 || idx >= (s16)p->def->nsounds) return;
    const MgSound *s = &p->def->sounds[idx];
    MG_CRUMB('P');
    XGM2_playPCM(s->data, s->len, SOUND_PCM_CH_AUTO);
}

void MG_spawnExplod(MgPlayer *owner, s16 anim, mgfx x, mgfx y, s16 removetime, s16 id, s8 facing)
{
    s16 idx = MG_findAnim(owner->def, anim);
    if (idx < 0) return;
    MgExplod *e = 0;
    for (u8 i = 0; i < MG_MAX_EXPLOD; i++) if (!mg_fight.explod[i].active) { e = &mg_fight.explod[i]; break; }
    if (!e) {                                   /* pool cheio: recicla o mais antigo (slot 0) */
        e = &mg_fight.explod[0];
    }
    MgDraw keep = e->dr;
    memset(e, 0, sizeof(*e));
    e->dr = keep;
    e->active = 1;
    e->id = id;
    e->anim_idx = idx;
    e->x = x;
    e->y = y;
    e->facing = facing;
    e->removetime = removetime;
    e->bind_owner = owner->side;
    e->depth = -5;
    e->bgfx = -1;
    for (u8 i = 0; i < owner->def->nbgfx && i < MG_MAX_BGFX; i++)
        if (owner->def->bgfx[i].anim_id == anim && s_bgfx_base[owner->side][i]) e->bgfx = i;
}

/* ------------------------------------------------------------------ caixas */
typedef struct { s16 x1, y1, x2, y2; } Rect;

static Rect world_box(const MgBox *b, mgfx x, mgfx y, s8 facing)
{
    Rect r;
    s16 px = FX2I(x), py = FX2I(y);
    if (facing > 0) { r.x1 = px + b->x1; r.x2 = px + b->x2; }
    else { r.x1 = px - b->x2; r.x2 = px - b->x1; }
    r.y1 = py + b->y1;
    r.y2 = py + b->y2;
    return r;
}

static u8 overlap(const Rect *a, const Rect *b)
{
    return a->x1 <= b->x2 && b->x1 <= a->x2 && a->y1 <= b->y2 && b->y1 <= a->y2;
}

/* alguma Clsn1 do quadro de ataque encosta em alguma Clsn2 do defensor?
 * Se sim, devolve em *hit a intersecao do primeiro par que colidiu (ponto de contato real). */
static u8 frames_collide(const MgCharDef *ad, const MgAnimFrame *af, mgfx ax, mgfx ay, s8 afc,
                         const MgPlayer *d, Rect *hit)
{
    const MgAnimFrame *df = &d->def->frames[d->def->anims[d->anim_idx].first + d->elem];
    if (!af->nclsn1 || !df->nclsn2) return 0;
    for (u8 i = 0; i < af->nclsn1; i++) {
        Rect r1 = world_box(&ad->boxes[af->clsn + i], ax, ay, afc);
        for (u8 j = 0; j < df->nclsn2; j++) {
            Rect r2 = world_box(&d->def->boxes[df->clsn + df->nclsn1 + j], d->x, d->y, d->facing);
            if (overlap(&r1, &r2)) {
                hit->x1 = r1.x1 > r2.x1 ? r1.x1 : r2.x1;
                hit->x2 = r1.x2 < r2.x2 ? r1.x2 : r2.x2;
                hit->y1 = r1.y1 > r2.y1 ? r1.y1 : r2.y1;
                hit->y2 = r1.y2 < r2.y2 ? r1.y2 : r2.y2;
                return 1;
            }
        }
    }
    return 0;
}

static const MgAnimFrame *cur_frame(const MgPlayer *p)
{
    return &p->def->frames[p->def->anims[p->anim_idx].first + p->elem];
}

/* hitflag: H=pe L=agachado A=ar F=caindo D=deitado ; + so em gethit ; - so fora de gethit */
static u8 can_hit(const MgHitDef *h, const MgPlayer *d)
{
    if (d->nothitby_time > 0 && (h->attr & d->nothitby_attr & 0x7) && (h->attr & d->nothitby_attr & 0x770)) return 0;
    if ((h->hitflag & 64) && d->movetype != 'H') return 0;
    if ((h->hitflag & 128) && d->movetype == 'H') return 0;
    switch (d->statetype) {
    case 'S': return (h->hitflag & 1) != 0;
    case 'C': return (h->hitflag & 2) != 0;
    case 'A': return (h->hitflag & 4) || (d->gh_fall && (h->hitflag & 8));
    case 'L': return (h->hitflag & 16) != 0;
    }
    return 1;
}

static u8 guards(const MgHitDef *h, const MgPlayer *d, s8 attacker_side_dir)
{
    if (d->movetype == 'H' && !(d->stateno >= 150 && d->stateno <= 155)) return 0;
    u8 in_guard = d->stateno >= 120 && d->stateno <= 155;
    u8 back = d->def->cmd_holdback != MG_NONE && d->cmd_timer[d->def->cmd_holdback];
    if (!in_guard && !(d->ctrl && back)) return 0;
    if (!in_guard && attacker_side_dir != d->facing) return 0;     /* ataque vindo por tras */
    switch (d->statetype) {
    case 'S': return (h->guardflag & 1) != 0;
    case 'C': return (h->guardflag & 2) != 0;
    case 'A': return (h->guardflag & 4) != 0;
    }
    return 0;
}

/* Faisca ancorada no ponto de contato (centro da intersecao Clsn1 x Clsn2).
 * Divergencia deliberada do MUGEN (que usa borda frontal + sparkxy): leitura de onde o golpe acertou.
 * Acertos seguidos na mesma regiao (<=16 px, <=90 ticks) percorrem 4 variacoes sutis (jitter). */
#define SPARK_REGION 16
#define SPARK_WINDOW 90
static const s8 kSparkJitter[4][2] = { { 0, 0 }, { 3, -2 }, { -3, 2 }, { 2, 3 } };

static void spark(MgPlayer *owner, s16 anim, const Rect *hit, s8 afc, const MgPlayer *def)
{
    if (anim < 0) return;
    s16 cx = (hit->x1 + hit->x2) >> 1, cy = (hit->y1 + hit->y2) >> 1;
    /* regiao relativa ao corpo do defensor (o empurrao do golpe nao "muda de regiao") */
    s16 rx = cx - FX2I(def->x), ry = cy - FX2I(def->y);
    if (abs(rx - owner->spark_last_x) <= SPARK_REGION && abs(ry - owner->spark_last_y) <= SPARK_REGION &&
        mg_fight.ticks - owner->spark_last_tick <= SPARK_WINDOW)
        owner->spark_var = (owner->spark_var + 1) & 3;
    else
        owner->spark_var = 0;
    owner->spark_last_x = rx;
    owner->spark_last_y = ry;
    owner->spark_last_tick = mg_fight.ticks;
    s16 jx = kSparkJitter[owner->spark_var][0] * afc, jy = kSparkJitter[owner->spark_var][1];
    MG_spawnExplod(owner, anim, FXI(cx + jx), FXI(cy + jy), -2, -1, afc);
}

/* aplica o acerto/defesa. from_proj: atacante nao congela */
static void apply_hit(MgPlayer *a, MgPlayer *d, const MgHitDef *h, u8 from_proj, const Rect *hit, s8 afc)
{
    u8 g = guards(h, d, -afc);
    d->target = 0;
    if (!from_proj) a->target = d;
    if (g) {
        s32 dmg = h->guard_damage;
        if (!h->guard_kill && d->life - dmg <= 0) dmg = d->life - 1;
        d->life -= dmg;
        a->moveguarded = a->movecontact = 1;
        if (!from_proj) a->hitpause = h->gpause_p1;
        d->hitshake = h->gpause_p2;
        d->hittime_left = h->ghittime;
        d->gh = *h;
        d->gh_guarded = 1;
        d->gh_fall = 0;
        d->gh_vx = h->guardvel_x;
        d->gh_vy = 0;
        d->sdef = d->def;
        MG_changeState(d, d->statetype == 'C' ? 152 : (d->statetype == 'A' ? 154 : 150), 0, -1);
        MG_playSound(a, h->guardsound);
        spark(a, h->guard_sparkno, hit, afc, d);
        return;
    }
    s32 dmg = h->damage;
    if (!h->kill && d->life - dmg <= 0) dmg = d->life - 1;
    d->life -= dmg;
    if (d->life < 0) d->life = 0;
    a->movehit = a->movecontact = 1;
    a->hitcount++;
    if (!from_proj) a->hitpause = h->pause_p1;
    a->power += h->getpower;
    d->power += h->givepower;
    if (a->power > 3000) a->power = 3000;
    if (d->power > 3000) d->power = 3000;
    /* combo: continua se o defensor ja estava em atordoamento (movetype H) */
    if (d->movetype == 'H' && mg_fight.combo[a->side]) mg_fight.combo[a->side]++;
    else mg_fight.combo[a->side] = 1;
    mg_fight.combo_tick[a->side] = mg_fight.ticks;
    d->gh = *h;
    d->gh_guarded = 0;
    d->hitshake = h->pause_p2;
    u8 air = d->y < 0 || d->statetype == 'A' || h->gvel_y != 0;
    if (air) {
        d->gh_vx = h->avel_x;
        d->gh_vy = h->avel_y;
        d->hittime_left = h->airhittime;
        d->gh_fall = h->airfall;
    } else {
        d->gh_vx = h->gvel_x;
        d->gh_vy = h->gvel_y;
        d->hittime_left = h->hittime;
        d->gh_fall = h->fall;
    }
    if (d->life <= 0) {                        /* KO: sempre cai */
        d->gh_fall = 1;
        if (d->gh_vy >= 0) d->gh_vy = h->fall_yvel;
        if (d->gh_vx == 0) d->gh_vx = -FXI(3);
    }
    if (d->facing == afc) { d->facing = -afc; }           /* vira para o atacante */
    MG_playSound(a, h->hitsound);
    spark(a, h->sparkno, hit, afc, d);
    if (h->p2stateno >= 0 && !from_proj) {
        d->sdef = a->sdef;                                 /* custom state do atacante */
        MG_changeState(d, h->p2stateno, 0, -1);
        a->target = d;
    } else {
        d->sdef = d->def;
        s16 st = (air || d->gh_fall) ? 5020 : (d->statetype == 'C' ? 5010 : 5000);
        MG_changeState(d, st, 0, -1);
    }
    if (h->p1stateno >= 0 && !from_proj) MG_changeState(a, h->p1stateno, -1, -1);
}

static void resolve_hits(void)
{
    for (u8 s = 0; s < 2; s++) {
        MgPlayer *a = &mg_fight.p[s], *d = a->enemy;
        /* golpe corpo a corpo */
        Rect hit;
        if (a->hitdef_active && a->movetype == 'A' && a->hitpause == 0 && can_hit(&a->hd, d) &&
            frames_collide(a->def, cur_frame(a), a->x, a->y, a->facing, d, &hit)) {
            a->hitdef_active = 0;              /* um HitDef = um acerto */
            apply_hit(a, d, &a->hd, 0, &hit, a->facing);
        }
        /* projeteis */
        for (u8 i = 0; i < MG_MAX_PROJ; i++) {
            MgProj *pr = &a->proj[i];
            if (!pr->active || pr->removing) continue;
            const MgAnimFrame *pf = &a->def->frames[a->def->anims[pr->anim_idx].first + pr->elem];
            if (!can_hit(&pr->hd, d) || !frames_collide(a->def, pf, pr->x, pr->y, pr->facing, d, &hit)) continue;
            apply_hit(a, d, &pr->hd, 1, &hit, pr->facing);
            pr->contact_time = 0;
            if (--pr->hits <= 0) {
                s16 idx = pr->hitanim >= 0 ? MG_findAnim(a->def, pr->hitanim) : -1;
                if (idx >= 0) {
                    pr->anim_idx = idx; pr->elem = 0; pr->elem_time = 0;
                    pr->vx = pr->vy = pr->ax = pr->ay = 0;
                    pr->removing = 1;
                    pr->removetime = 0x7FFF;
                } else pr->active = 0;
            }
        }
    }
    /* projetil x projetil: se anulam */
    for (u8 i = 0; i < MG_MAX_PROJ; i++) {
        MgProj *p1 = &mg_fight.p[0].proj[i];
        if (!p1->active || p1->removing) continue;
        for (u8 j = 0; j < MG_MAX_PROJ; j++) {
            MgProj *p2 = &mg_fight.p[1].proj[j];
            if (!p2->active || p2->removing) continue;
            s16 dx = FX2I(p1->x - p2->x), dy = FX2I(p1->y - p2->y);
            if (abs(dx) < 24 && abs(dy) < 24) { p1->active = 0; p2->active = 0; }
        }
    }
}

/* ------------------------------------------------------------------ empurrao / limites / camera */
static void push_and_bounds(void)
{
    MgPlayer *a = &mg_fight.p[0], *b = &mg_fight.p[1];
    if (a->y > -FXI(8) && b->y > -FXI(8) && a->sdef == a->def && b->sdef == b->def) {
        mgfx wa = a->def->consts->ground_front, wb = b->def->consts->ground_front;
        mgfx dx = b->x - a->x;
        mgfx need = wa + wb;
        mgfx adx = dx < 0 ? -dx : dx;
        if (adx < need) {
            mgfx push = (need - adx) >> 1;
            if (dx >= 0) { a->x -= push; b->x += push; }
            else { a->x += push; b->x -= push; }
        }
    }
    for (u8 s = 0; s < 2; s++) {
        MgPlayer *p = &mg_fight.p[s];
        mgfx lo = FXI(mg_fight.camx) + p->def->consts->ground_back;
        mgfx hi = FXI(mg_fight.camx + 320) - p->def->consts->ground_back;
        if (p->x < lo) p->x = lo;
        if (p->x > hi) p->x = hi;
    }
    s32 mid = (FX2I(a->x) + FX2I(b->x)) / 2 - 160;
    if (mid < mg_fight.stage_left) mid = mg_fight.stage_left;
    if (mid > mg_fight.stage_right - 320) mid = mg_fight.stage_right - 320;
    s32 d = mid - mg_fight.camx;
    if (d > 4) d = 4;
    if (d < -4) d = -4;
    mg_fight.camx += d;
}

/* ------------------------------------------------------------------ render */
void MG_drawInit(MgDraw *d)
{
    for (u8 i = 0; i < MG_MAX_PARTS; i++) { d->spr[i] = 0; d->sheet[i] = -1; }
}

void MG_drawRelease(MgDraw *d)
{
    for (u8 i = 0; i < MG_MAX_PARTS; i++)
        if (d->spr[i]) { SPR_releaseSprite(d->spr[i]); d->spr[i] = 0; d->sheet[i] = -1; }
}

/* desenha uma parte (sheet/frame) no slot k do objeto */
static void draw_part(const MgCharDef *d, MgDraw *dr, u8 k, s16 sheet, u8 frame, u8 fflags, s16 ox, s16 oy,
                      mgfx x, mgfx y, s8 facing, u16 body_pal, s16 depth, u16 vram)
{
    MG_CRUMB('D');
    const MgSheet *sh = &d->sheets[sheet];
    u16 pal = sh->pal ? PAL3 : body_pal;
    Sprite **spr = &dr->spr[k];
    if (!*spr) {
        *spr = (vram && k == 0) ? SPR_addSpriteEx(sh->def, 0, 0, TILE_ATTR_FULL(pal, TRUE, FALSE, FALSE, vram),
                                                   SPR_FLAG_AUTO_TILE_UPLOAD)
                                : SPR_addSpriteEx(sh->def, 0, 0, TILE_ATTR(pal, TRUE, FALSE, FALSE),
                                                   SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD);
        if (!*spr) return;                     /* VRAM de sprite esgotada: parte pulada */
        dr->sheet[k] = sheet;
    } else if (dr->sheet[k] != sheet) {
        if (!SPR_setDefinition(*spr, sh->def)) { SPR_setVisibility(*spr, HIDDEN); return; }
        dr->sheet[k] = sheet;
    }
    SPR_setAnimAndFrame(*spr, 0, frame);
    u8 flip = (facing < 0) ^ ((fflags & MG_FRAME_HFLIP) != 0);
    SPR_setHFlip(*spr, flip);
    SPR_setVFlip(*spr, (fflags & MG_FRAME_VFLIP) != 0);
    SPR_setPalette(*spr, pal);
    s16 px = FX2I(x) - mg_fight.camx + (mg_fight.screen_shake & 1 ? 2 : 0);
    s16 py = mg_fight.floor_y + FX2I(y);
    s16 sx = px + MG_FACE(ox, facing) - (flip ? (s16)(sh->cell_w - sh->axis_x) : sh->axis_x);
    s16 sy = py + oy - sh->axis_y;
    SPR_setPosition(*spr, sx, sy);
    SPR_setDepth(*spr, depth);
    SPR_setVisibility(*spr, VISIBLE);
}

static void draw(const MgCharDef *d, MgDraw *dr, u16 anim_idx, u8 elem,
                 mgfx x, mgfx y, s8 facing, u16 body_pal, s16 depth, u8 visible, u16 vram)
{
    const MgAnimFrame *f = &d->frames[d->anims[anim_idx].first + elem];
    u8 n = (!visible || f->sheet < 0) ? 0 : (f->nparts ? f->nparts : 1);
    if (n > MG_MAX_PARTS) n = MG_MAX_PARTS;
    if (n) draw_part(d, dr, 0, f->sheet, f->frame, f->flags, f->ox, f->oy, x, y, facing, body_pal, depth, vram);
    for (u8 k = 1; k < n; k++) {
        const MgFramePart *pt = &d->parts[f->part + k - 1];
        draw_part(d, dr, k, pt->sheet, pt->frame, f->flags, f->ox, f->oy, x, y, facing, body_pal, depth, 0);
    }
    for (u8 k = n; k < MG_MAX_PARTS; k++)
        if (dr->spr[k]) SPR_setVisibility(dr->spr[k], HIDDEN);
}

static u16 s_vram_next;

u16 MG_fightVramNext(void) { return s_vram_next; }

static void hud(void)
{
#ifdef MG_EXTERNAL_HUD
    return;                                  /* HUD do jogo (arte convertida) substitui o texto */
#endif
    /* UI transitoria (texto): substituida por lifebar convertida na etapa de screenpack.
     * Redesenha so quando algum valor muda (VDP_drawText e caro no 68000). */
    static s16 last[5] = { -1, -1, -1, -1, -1 };
    s16 cur[5];
    for (u8 s = 0; s < 2; s++) {
        const MgPlayer *p = &mg_fight.p[s];
        s32 maxl = p->def->consts->life >> MG_FX_SHIFT;
        s16 n = maxl ? (s16)((p->life * 14) / maxl) : 0;
        cur[s * 2] = n < 0 ? 0 : n;
        cur[s * 2 + 1] = (s16)(p->power / 1000);
    }
    cur[4] = mg_fight.round_timer / 60;
    if (mg_fight.round_state != 1) cur[4] = -2 - mg_fight.round_state;
    char line[20];
    for (u8 s = 0; s < 2; s++) {
        if (cur[s * 2] == last[s * 2] && cur[s * 2 + 1] == last[s * 2 + 1]) continue;
        for (u8 i = 0; i < 14; i++) line[i] = i < cur[s * 2] ? '=' : '.';
        line[14] = '0' + cur[s * 2 + 1];
        line[15] = 0;
        VDP_drawText(line, s ? 24 : 1, 1);
    }
    if (cur[4] != last[4]) {
        s16 t = mg_fight.round_state == 1 ? mg_fight.round_timer / 60 : ROUND_TIME;
        line[0] = '0' + (t / 10) % 10;
        line[1] = '0' + t % 10;
        line[2] = 0;
        VDP_drawText(line, 19, 1);
        VDP_drawText(mg_fight.round_state == 0 ? "ROUND" : "     ", 17, 10);
    }
    for (u8 i = 0; i < 5; i++) last[i] = cur[i];
}

/* efeito de fundo: tilemap em BG_B (baixa prioridade) + PAL0 1..14 trocada a cada elemento */
static void bgfx_render(MgExplod *e, const MgPlayer *o)
{
    const MgBgFx *fx = &o->def->bgfx[(u8)e->bgfx];
    MG_CRUMB('m');
    if (!e->bgfx_shown) {
        PAL_getColors(0, s_pal0_saved, 16);
        MG_CRUMB('n');
        VDP_setTileMapEx(BG_B, fx->img->tilemap, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, s_bgfx_base[o->side][(u8)e->bgfx]),
                         0, 0, 0, 0, 40, 28, DMA_QUEUE);
        MG_CRUMB('o');
        e->bgfx_shown = 1;
        s_bgfx_owner = e - mg_fight.explod;
        mg_fight.bgfx_active = 1;
    }
    u8 k = e->elem < fx->nelem ? fx->elem_pal[e->elem] : 255;
    if (k < fx->npals) PAL_setColors(1, &fx->pals[k][1], 14, DMA_QUEUE);
}

static void bgfx_end(void)
{
    VDP_clearTileMapRect(BG_B, 0, 0, 40, 28);
    PAL_setColors(1, &s_pal0_saved[1], 14, DMA_QUEUE);
    s_bgfx_owner = -1;
    mg_fight.bgfx_active = 0;
}

void MG_fightRender(void)
{
    MG_PROF_BEGIN();
    MG_CRUMB('k');
    for (u8 s = 0; s < 2; s++) {
        MgPlayer *p = &mg_fight.p[s];
        s16 depth = -(p->sprpriority * 4) - (s ? 1 : 0);
        draw(p->def, &p->dr, p->anim_idx, p->elem, p->x, p->y, p->facing, p->pal, depth, 1, s_vram[s]);
        for (u8 i = 0; i < MG_MAX_PROJ; i++) {
            MgProj *pr = &p->proj[i];
            if (!pr->active) { if (pr->dr.spr[0]) MG_drawRelease(&pr->dr); continue; }
            draw(p->def, &pr->dr, pr->anim_idx, pr->elem, pr->x, pr->y,
                                 pr->facing, p->pal, -20, 1, 0);
        }
    }
    /* sombras: no chao sob cada lutador, profundidade maxima (atras de tudo e descartadas primeiro) */
    for (u8 s = 0; s < 2; s++) {
        MgPlayer *p = &mg_fight.p[s];
        if (!p->def->shadow) continue;
        if (!p->shadow_spr) {
            p->shadow_spr = SPR_addSpriteEx(p->def->shadow, 0, 0, TILE_ATTR(p->pal, FALSE, FALSE, FALSE),
                                            SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD);
            if (!p->shadow_spr) continue;
            SPR_setDepth(p->shadow_spr, SPR_MAX_DEPTH);
        }
        SPR_setPosition(p->shadow_spr, FX2I(p->x) - mg_fight.camx - 16, mg_fight.floor_y - 4);
        SPR_setVisibility(p->shadow_spr, mg_fight.bgfx_active ? HIDDEN : VISIBLE);
    }
    for (u8 s = 0; s < 2; s++) {
        MgPlayer *h = &mg_fight.helper[s];
        if (mg_fight.helper_active[s])
            draw(h->def, &h->dr, h->anim_idx, h->elem, h->x, h->y, h->facing, h->pal, -25, 1, 0);
        else if (h->dr.spr[0]) MG_drawRelease(&h->dr);
    }
    for (u8 i = 0; i < MG_MAX_EXPLOD; i++) {
        MgExplod *e = &mg_fight.explod[i];
        const MgPlayer *o = &mg_fight.p[e->bind_owner];
        if (!e->active) {
            if (e->dr.spr[0]) MG_drawRelease(&e->dr);
            if (s_bgfx_owner == i) bgfx_end();
            continue;
        }
        if (e->bgfx >= 0) { bgfx_render(e, o); continue; }
        draw(o->def, &e->dr, e->anim_idx, e->elem, e->x, e->y, e->facing, o->pal, -30, 1, 0);
    }
    if (mg_fight.screen_shake > 0) mg_fight.screen_shake--;
    MG_CRUMB('p');
    hud();
    MG_CRUMB('q');
    MG_PROF_MARK(6);
}

/* ------------------------------------------------------------------ CPU */
/* IA reimplementada (o personagem nao traz IA propria). Como a IA do MUGEN, ela ATIVA
 * comandos declarados no .cmd (p->ai_cmd) em vez de digitar sequencias; so as direcoes do
 * ultimo passo sao seguradas, para os comandos de segurar e o tipo de estado baterem. */
static s16 ai_cool[2];
static u16 ai_hold[2];
static u8 ai_hold_t[2];

static u16 key_bits(u8 k)
{
    static const u16 m[] = { 0, MG_IN_F, MG_IN_B, MG_IN_U, MG_IN_D, MG_IN_D | MG_IN_F, MG_IN_D | MG_IN_B,
                             MG_IN_U | MG_IN_F, MG_IN_U | MG_IN_B, MG_IN_A, MG_IN_BB, MG_IN_C,
                             MG_IN_X, MG_IN_Y, MG_IN_Z, MG_IN_S };
    return k < 16 ? m[k] : 0;
}

u16 MG_cpuInput(MgPlayer *p)
{
    u8 s = p->side;
    p->ai_cmd = -1;
    if (ai_hold_t[s]) { ai_hold_t[s]--; return ai_hold[s]; }
    if (mg_fight.round_state != 1) return 0;
    const MgPlayer *e = p->enemy;
    s16 dist = FX2I(MG_FACE(e->x - p->x, p->facing));
    if (e->movetype == 'A' && dist < 90 && (random() & 3)) return MG_IN_B | ((e->statetype == 'C') ? MG_IN_D : 0);
    if (ai_cool[s] > 0) { ai_cool[s]--; return dist > 70 ? MG_IN_F : 0; }
    ai_cool[s] = 6 + (random() % 20);
    if (!p->ctrl) return 0;
    const MgCharDef *d = p->def;
    for (u8 tries = 0; tries < 6; tries++) {
        u16 ci = random() % d->ncmds;
        const MgCommand *cm = &d->cmds[ci];
        if (ci == d->cmd_holdfwd || ci == d->cmd_holdback || ci == d->cmd_holdup || ci == d->cmd_holddown) continue;
        if (!cm->nsteps) continue;
        const MgCmdStep *last = &d->steps[cm->first_step + cm->nsteps - 1];
        u8 has_button = 0;
        u16 dirs = 0;
        for (u8 k = 0; k < last->nkeys; k++) {
            u8 key = d->keys[last->first_key + k].key;
            if (key >= MG_K_A && key != MG_K_S) has_button = 1;
            else if (key < MG_K_A) dirs |= key_bits(key);
        }
        if (!has_button) continue;
        if (cm->nsteps == 1 && dist > 70) continue;     /* normais so de perto */
        p->ai_cmd = ci;
        ai_hold[s] = dirs;
        ai_hold_t[s] = dirs ? 4 : 0;
        return dirs;
    }
    return dist > 60 ? MG_IN_F : 0;
}

/* ------------------------------------------------------------------ rounds */
static void reset_player(MgPlayer *p, s16 x, s8 facing)
{
    for (u8 i = 0; i < MG_MAX_PROJ; i++) p->proj[i].active = 0;
    p->x = FXI(x); p->y = 0; p->vx = p->vy = 0;
    p->facing = facing;
    p->life = p->def->consts->life >> MG_FX_SHIFT;
#ifdef MG_TEST_FULL_POWER
    p->power = 3000;                           /* so ROM de teste: supers disponiveis para evidencia */
#endif
#ifdef MG_TEST_LOW_LIFE
    if (p->side == 1) p->life = 150;           /* so ROM de teste: KO por super (fundo de vitoria) */
#endif
    p->hitpause = p->hitshake = p->hittime_left = 0;
    p->hitdef_active = 0;
    p->target = 0; p->bind_time = 0;
    p->sdef = p->def;
    p->ctrl = 0;
    p->statetype = 'S'; p->movetype = 'I'; p->physics = 'S';
    MG_changeState(p, 5900, 0, -1);
    MG_changeAnim(p, 0, 1);
    p->ctrl = 0;
}

static void start_round(void)
{
    mg_fight.camx = (STAGE_W - 320) / 2;
    reset_player(&mg_fight.p[0], STAGE_W / 2 - 70, 1);
    reset_player(&mg_fight.p[1], STAGE_W / 2 + 70, -1);
    for (u8 i = 0; i < MG_MAX_EXPLOD; i++) mg_fight.explod[i].active = 0;
    mg_fight.helper_active[0] = mg_fight.helper_active[1] = 0;
    mg_fight.round_state = 0;
    mg_fight.round_timer = 90;                 /* intro */
    mg_fight.round_no++;
    mg_fight.pause_time = 0;
    mg_fight.combo[0] = mg_fight.combo[1] = 0;
#ifndef MG_EXTERNAL_HUD
    VDP_clearTextArea(0, 8, 40, 4);
#endif
}

static void round_flow(void)
{
    MgPlayer *a = &mg_fight.p[0], *b = &mg_fight.p[1];
    switch (mg_fight.round_state) {
    case 0:
        if (--mg_fight.round_timer <= 0) {
            mg_fight.round_state = 1;
            mg_fight.round_timer = ROUND_TIME * 60;
            a->ctrl = b->ctrl = 1;
#ifndef MG_EXTERNAL_HUD
            VDP_clearTextArea(0, 8, 40, 4);
#endif
        }
        break;
    case 1:
        if (a->life <= 0 || b->life <= 0 || --mg_fight.round_timer <= 0) {
            mg_fight.round_state = 2;
            if (mg_fight.round_timer <= 0) {           /* tempo: menor vida perde */
                if (a->life != b->life) MG_selfState(a->life < b->life ? a : b, 170);
            }
            mg_fight.round_timer = 150;
#ifndef MG_EXTERNAL_HUD
            VDP_drawText(a->life <= 0 || b->life <= 0 ? "K.O." : "TIME", 18, 10);
#endif
        }
        break;
    case 2:
        if (--mg_fight.round_timer == 60) {
            MgPlayer *w = a->life > b->life ? a : (b->life > a->life ? b : 0);
            if (w && w->statetype != 'A' && w->movetype != 'H') MG_selfState(w, 180);
        }
        if (mg_fight.round_timer <= 0) {
            if (a->life > b->life) mg_fight.wins[0]++;
            else if (b->life > a->life) mg_fight.wins[1]++;
            if (mg_fight.wins[0] >= 2 || mg_fight.wins[1] >= 2) {
                mg_fight.wins[0] = mg_fight.wins[1] = 0;
                mg_fight.round_no = 0;
            }
            start_round();
        }
        break;
    }
}

/* ------------------------------------------------------------------ API */
void MG_fightInit(const MgCharDef *p1, u8 p1pal, const MgCharDef *p2, u8 p2pal, u8 p2_cpu)
{
    memset(&mg_fight, 0, sizeof(mg_fight));
    mg_fight.stage_left = 0;
    mg_fight.stage_right = STAGE_W;
    mg_fight.floor_y = FLOOR_Y;
    const MgCharDef *defs[2] = { p1, p2 };
    u8 pals[2] = { p1pal, p2pal };
    if (p1 == p2 && p1pal == p2pal) pals[1] = (p1pal + 1) % p2->npals;     /* espelho: cor diferente */
    for (u8 s = 0; s < 2; s++) {
        MgPlayer *p = &mg_fight.p[s];
        p->def = p->sdef = defs[s];
        p->side = s;
        p->enemy = &mg_fight.p[s ^ 1];
        p->pal = s ? PAL2 : PAL1;
        p->is_cpu = s == 1 && p2_cpu;
        MG_drawInit(&p->dr);
        MG_drawInit(&mg_fight.helper[s].dr);
        for (u8 i = 0; i < MG_MAX_PROJ; i++) MG_drawInit(&p->proj[i].dr);
        PAL_setColors(s ? 32 : 16, defs[s]->pals[pals[s] % defs[s]->npals], 16, DMA);
    }
    PAL_setColors(48, p1->fxpal, 16, DMA);
    s_bgfx_owner = -1;
    /* reserva VRAM fixa para os corpos: maior quadro de qualquer sheet do personagem */
    u16 need[2] = { 0, 0 };
    for (u8 s = 0; s < 2; s++)
        for (u16 i = 0; i < defs[s]->nsheets; i++)
            if (defs[s]->sheets[i].def->maxNumTile > need[s]) need[s] = defs[s]->sheets[i].def->maxNumTile;
    if (TILE_USER_INDEX + need[0] + need[1] <= TILE_SPRITE_INDEX) {
        s_vram[0] = TILE_USER_INDEX;
        s_vram[1] = TILE_USER_INDEX + need[0];
    } else {
        s_vram[0] = s_vram[1] = 0;            /* nao cabe: volta a alocacao automatica */
    }
    /* tiles dos efeitos de fundo logo apos os corpos, se couberem antes do pool de sprites */
    u16 next = TILE_USER_INDEX + need[0] + need[1];
    for (u8 s = 0; s < 2; s++)
        for (u8 i = 0; i < MG_MAX_BGFX; i++) {
            s_bgfx_base[s][i] = 0;
            if (i >= defs[s]->nbgfx) continue;
            const MgBgFx *fx = &defs[s]->bgfx[i];
            u16 n = fx->img->tileset->numTile;
            u16 dup = 0;                          /* mesmo efeito ja carregado (espelho P1=P2) */
            for (u8 t = 0; t < s; t++)
                for (u8 j = 0; j < MG_MAX_BGFX && j < defs[t]->nbgfx; j++)
                    if (defs[t]->bgfx[j].img == fx->img && s_bgfx_base[t][j]) dup = s_bgfx_base[t][j];
            if (dup) { s_bgfx_base[s][i] = dup; continue; }
            if (next + n > TILE_SPRITE_INDEX) continue;   /* sem espaco: efeito omitido */
            VDP_loadTileSet(fx->img->tileset, next, DMA_QUEUE);
            s_bgfx_base[s][i] = next;
            next += n;
        }
    s_vram_next = next;
    for (u8 i = 0; i < MG_MAX_EXPLOD; i++) MG_drawInit(&mg_fight.explod[i].dr);
    ai_hold_t[0] = ai_hold_t[1] = 0;
    start_round();
}

void MG_fightUpdate(u16 pad1, u16 pad2)
{
    MG_PROF_BEGIN();
    MG_CRUMB('a');
    mg_fight.ticks++;
    MgPlayer *p0 = &mg_fight.p[0], *p1 = &mg_fight.p[1];
    MG_playerInput(p0, pad1);
    MG_playerInput(p1, pad2);
    MG_PROF_MARK(0);
    if (mg_fight.round_state == 0) { p0->ctrl = p1->ctrl = 0; }

    if (mg_fight.pause_time > 0) {             /* SuperPause: so o dono anda durante movetime */
        mg_fight.pause_time--;
        MgPlayer *o = &mg_fight.p[mg_fight.pause_owner];
        if (mg_fight.pause_movetime > 0) {
            mg_fight.pause_movetime--;
            MG_playerLogic(o);
            MG_playerPhysics(o);
        }
        for (u8 i = 0; i < MG_MAX_EXPLOD; i++)
            if (mg_fight.explod[i].active) MG_explodStep(&mg_fight.explod[i], &mg_fight.p[mg_fight.explod[i].bind_owner]);
        return;
    }
    MG_CRUMB('b');
    MG_playerLogic(p0);
    MG_CRUMB('c');
    MG_playerLogic(p1);
    MG_CRUMB('d');
    MG_PROF_MARK(1);
    MG_playerPhysics(p0);
    MG_playerPhysics(p1);
    MG_PROF_MARK(2);
    MG_CRUMB('e');
    for (u8 s = 0; s < 2; s++)
        if (mg_fight.helper_active[s]) { MG_playerLogic(&mg_fight.helper[s]); MG_playerPhysics(&mg_fight.helper[s]); }
    MG_CRUMB('f');
    for (u8 s = 0; s < 2; s++)
        for (u8 i = 0; i < MG_MAX_PROJ; i++) MG_projStep(&mg_fight.p[s], &mg_fight.p[s].proj[i]);
    for (u8 i = 0; i < MG_MAX_EXPLOD; i++)
        if (mg_fight.explod[i].active) MG_explodStep(&mg_fight.explod[i], &mg_fight.p[mg_fight.explod[i].bind_owner]);
    MG_PROF_MARK(3);
    MG_CRUMB('g');
    if (mg_fight.round_state == 1 || mg_fight.round_state == 2) resolve_hits();
    MG_CRUMB('h');
    MG_PROF_MARK(4);
    push_and_bounds();
    MG_CRUMB('i');
    round_flow();
    MG_CRUMB('j');
    MG_PROF_MARK(5);
}

void MG_fightEnd(void)
{
    for (u8 s = 0; s < 2; s++) {
        MgPlayer *p = &mg_fight.p[s];
        MG_drawRelease(&p->dr);
        if (p->shadow_spr) SPR_releaseSprite(p->shadow_spr);
        MG_drawRelease(&mg_fight.helper[s].dr);
        for (u8 i = 0; i < MG_MAX_PROJ; i++) MG_drawRelease(&p->proj[i].dr);
    }
    for (u8 i = 0; i < MG_MAX_EXPLOD; i++) MG_drawRelease(&mg_fight.explod[i].dr);
    memset(&mg_fight, 0, sizeof(mg_fight));
}
