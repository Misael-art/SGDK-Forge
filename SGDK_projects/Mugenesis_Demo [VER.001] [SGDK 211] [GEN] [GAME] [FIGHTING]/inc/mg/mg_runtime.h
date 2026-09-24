/* COPIADO de tools/mugen2sgdk_forge/runtime/mg_runtime.h (v0.3.0). Edite na fonte. */
/* mg_runtime.h -- runtime generico de luta para dados gerados pelo mugen2sgdk_forge.
 *
 * Semantica alvo: motor MUGEN (estados, triggers, HitDef, Clsn1/Clsn2), reduzida ao que
 * o Mega Drive executa a 60 fps. Tudo o que diverge esta listado em runtime/README.md.
 * Sem float, sem malloc: pools estaticos, ponto fixo 24.8.
 */
#ifndef MG_RUNTIME_H
#define MG_RUNTIME_H

#include <genesis.h>
#if defined(__has_include)
#if __has_include("mg_config.h")
#include "mg_config.h"          /* configuracao do projeto (ex.: MG_EXTERNAL_HUD) */
#endif
#endif
#include "mg_types.h"

#define MG_NUM_VARS     65      /* var(0..59) + sysvar(0..4) em 60..64 */
#define MG_NUM_FVARS    45      /* fvar(0..39) + sysfvar(0..4) */
#define MG_MAX_CMDS     160
#define MG_INPUT_HIST   64      /* potencia de 2: buffer circular */
#define MG_MAX_PROJ     4
#define MG_MAX_EXPLOD   6
#define MG_MAX_PARTS    4       /* sprites SGDK por objeto (quadros divididos) */

typedef struct { Sprite *spr[MG_MAX_PARTS]; s16 sheet[MG_MAX_PARTS]; } MgDraw;
#define MG_MAX_PROG     32      /* comandos em andamento simultaneos */
#define MG_MAX_LIVE     32      /* comandos ativos (buffer) simultaneos */

/* bits de entrada ja relativos a frente do personagem */
#define MG_IN_U 0x0001
#define MG_IN_D 0x0002
#define MG_IN_B 0x0004
#define MG_IN_F 0x0008
#define MG_IN_A 0x0010
#define MG_IN_BB 0x0020
#define MG_IN_C 0x0040
#define MG_IN_X 0x0080
#define MG_IN_Y 0x0100
#define MG_IN_Z 0x0200
#define MG_IN_S 0x0400

/* v * facing sem multiplicacao de 32 bits (68000) */
#define MG_FACE(v, f) ((f) < 0 ? -(v) : (v))

typedef struct {
    s16 damage, guard_damage;
    s16 pause_p1, pause_p2, gpause_p1, gpause_p2;
    s16 hittime, slidetime, ghittime, gslidetime, gctrltime, airhittime;
    mgfx gvel_x, gvel_y, avel_x, avel_y, guardvel_x;
    mgfx fall_yvel, fall_xvel, yaccel;
    u8  fall, airfall, fall_recover, kill, guard_kill;
    s16 spark_x, spark_y, p1stateno, p2stateno, getpower, givepower, id, chainid;
    u16 attr;
    u8  hitflag, guardflag, animtype, air_animtype, groundtype, airtype, priority;
    s16 hitsound, guardsound, sparkno, guard_sparkno;
} MgHitDef;

typedef struct {
    u8 active;
    s16 id, anim_id, hitanim, remanim;
    u16 anim_idx; u8 elem; s16 elem_time;
    mgfx x, y, vx, vy, ax, ay;
    s8 facing;
    s16 removetime, hits;
    u8 removing;
    s16 contact_time;          /* ticks desde o ultimo contato (-1 nunca) */
    MgHitDef hd;
    MgDraw dr;
} MgProj;

typedef struct {
    u8 active;
    s16 id;
    u16 anim_idx; u8 elem; s16 elem_time; s32 anim_time;
    mgfx x, y, vx, vy;
    s8 facing;
    s16 removetime, bindtime;
    u8 bind_owner;             /* segue o dono enquanto bindtime */
    mgfx bx, by;
    s16 depth;
    s8 bgfx;                   /* >=0: efeito de fundo (indice em def->bgfx) em vez de sprite */
    u8 bgfx_shown;
    MgDraw dr;
} MgExplod;

typedef struct MgPlayer MgPlayer;
struct MgPlayer {
    const MgCharDef *def;      /* dono das animacoes/sprites/sons/comandos */
    const MgCharDef *sdef;     /* dono dos estados em execucao (custom state = def do atacante) */
    MgPlayer *enemy;
    u8 side;
    u8 pal;                    /* PAL1/PAL2 do corpo */
    u8 is_cpu;

    /* posicao em pixels do mundo (fx), y=0 chao, y<0 no ar; vel local (x relativo a facing) */
    mgfx x, y, vx, vy;
    s8 facing;

    s16 stateno, prevstateno;
    s16 state_idx;
    s32 time;
    u8 statetype, movetype, physics, ctrl;
    u8 state_changed;

    u16 anim_idx; s16 anim_id;
    u8 elem;                   /* 0-based */
    s16 elem_time;
    s32 anim_time;             /* ticks desde o inicio do ciclo */

    s32 life, power;
    s32 vars[MG_NUM_VARS];
    mgfx fvars[MG_NUM_FVARS];

    /* ataque */
    u8 hitdef_active;
    MgHitDef hd;
    s16 movecontact, movehit, moveguarded;   /* ticks desde o contato (0 = nao) */
    s16 hitcount;
    s16 hitpause;              /* congelado (pausetime) */
    u8 posfreeze;

    /* dano recebido */
    MgHitDef gh;               /* hitdef que me atingiu */
    mgfx gh_vx, gh_vy;
    s16 hitshake;              /* ticks de tremida restantes */
    s16 hittime_left;
    u8 gh_fall, gh_guarded;
    u16 nothitby_attr; s16 nothitby_time;
    s16 juggle;

    /* entrada */
    u16 in_raw, in_prev;
    u16 hist[MG_INPUT_HIST]; u8 hist_len; u8 hist_head;
    u8 cmd_timer[MG_MAX_CMDS];
    u8 cmd_pos[MG_MAX_CMDS];      /* proximo passo esperado */
    u8 cmd_age[MG_MAX_CMDS];      /* ticks desde o primeiro passo */
    u8 prog[MG_MAX_PROG]; u8 nprog;      /* comandos em andamento (pos > 0) */
    u8 live[MG_MAX_LIVE]; u8 nlive;      /* comandos com cmd_timer > 0 */
    u32 hold_ok;                         /* resultado dos comandos de segurar no ultimo tick com mudanca */
    s16 ai_cmd;                          /* CPU: comando a ativar neste tick (-1 nenhum) */

    /* agarrao */
    MgPlayer *target; s16 bind_time; mgfx bind_x, bind_y;

    s16 sprpriority;
    MgProj proj[MG_MAX_PROJ];
    MgDraw dr;
    Sprite *shadow_spr;        /* sombra (P5): ultimo na lista, descartada primeiro em estouro de linha */
    s16 shake_screen;
    /* faisca: ultimo ponto de contato e indice de variacao (combos na mesma regiao) */
    s16 spark_last_x, spark_last_y; u32 spark_last_tick; u8 spark_var;
    /* helper reduzido (MUGEN Helper): roda estados do dono, invisivel a colisoes */
    u8 is_helper;
    s16 helper_id;
    MgPlayer *parent;
};

typedef struct {
    MgPlayer p[2];
    MgPlayer helper[2];        /* um helper por jogador */
    u8 helper_active[2];
    MgExplod explod[MG_MAX_EXPLOD];
    s32 camx;                  /* pixels do mundo na borda esquerda da tela */
    s16 stage_left, stage_right, floor_y;
    s16 pause_time; u8 pause_owner; s16 pause_movetime;
    s16 round_state;           /* 0 intro, 1 luta, 2 KO, 3 fim */
    s16 round_timer, round_no;
    u8 wins[2];
    u32 ticks;
    s16 screen_shake;
    u8 combo[2];               /* acertos consecutivos do atacante (lado) no combo atual */
    u32 combo_tick[2];         /* tick do ultimo acerto do combo */
    u8 bgfx_active;            /* fundo de super em tela cheia ativo (HUD deve se esconder) */
} MgFight;

extern MgFight mg_fight;

/* Perfil opcional no hardware (compilar com -DMG_PROFILE): subticks (1280 por quadro NTSC)
 * acumulados por etapa: 0 entrada/comandos, 1 estados, 2 fisica, 3 projeteis/explods,
 * 4 colisoes, 5 empurrao/rounds, 6 render, 7 SPR_update (medido pelo host da cena). */
/* marcador de diagnostico (so ROM de teste): escreve o passo atual na linha 4 da tela */
#ifdef MG_TEST_BREADCRUMB
extern char mg_crumbs[25];
extern u8 mg_crumb_i;
/* anel de 24 marcadores gravado na SRAM (offset 0x1000; 0x1018 = proxima posicao): sobrevive ao crash */
#define MG_CRUMB(ch) do { SRAM_enable(); SRAM_writeByte(0x1000 + mg_crumb_i, (ch)); \
    mg_crumb_i = (mg_crumb_i + 1) % 24; SRAM_writeByte(0x1018, mg_crumb_i); SRAM_disable(); } while (0)
#else
#define MG_CRUMB(ch) do { } while (0)
#endif

#ifdef MG_PROFILE
extern u32 mg_prof[16];   /* 8..: detalhe (8 hist, 9 laco comandos, 10 negativos, 11 estado atual, 12 auto) */
#define MG_PROF_BEGIN() u32 mg_prof_t = getSubTick()
#define MG_PROF_MARK(i) do { u32 mg_prof_n = getSubTick(); mg_prof[i] += mg_prof_n - mg_prof_t; mg_prof_t = mg_prof_n; } while (0)
#else
#define MG_PROF_BEGIN() do { } while (0)
#define MG_PROF_MARK(i) do { } while (0)
#endif

/* API */
void MG_fightInit(const MgCharDef *p1, u8 p1pal, const MgCharDef *p2, u8 p2pal, u8 p2_cpu);
void MG_fightUpdate(u16 pad1, u16 pad2);     /* 1 tick de logica (sem DMA fora do VBlank) */
void MG_fightRender(void);                   /* posiciona sprites; o upload ocorre em SPR_update */
void MG_fightEnd(void);
u16  MG_fightVramNext(void);                 /* primeiro tile livre apos corpos e fundos (para o HUD) */

/* internos compartilhados */
mgfx MG_eval(const MgPlayer *p, u16 off);
s32  MG_evalInt(const MgPlayer *p, u16 off, s32 dflt);
void MG_changeState(MgPlayer *p, s16 no, s16 ctrl, s16 anim);
void MG_changeAnim(MgPlayer *p, s16 anim, u8 elem1);
s16  MG_findAnim(const MgCharDef *d, s16 id);
s16  MG_findState(const MgCharDef *d, s16 id);
s16  MG_animElemTime(const MgPlayer *p, s16 elem1);
s32  MG_animTime(const MgPlayer *p);
void MG_playSound(const MgPlayer *p, s16 idx);
void MG_spawnExplod(MgPlayer *owner, s16 anim, mgfx x, mgfx y, s16 removetime, s16 id, s8 facing);
u16  MG_cpuInput(MgPlayer *p);
void MG_playerInput(MgPlayer *p, u16 pad);
void MG_playerLogic(MgPlayer *p);
void MG_playerPhysics(MgPlayer *p);
void MG_projStep(MgPlayer *p, MgProj *pr);
void MG_explodStep(MgExplod *e, const MgPlayer *owner);
void MG_selfState(MgPlayer *p, s16 no);
void MG_drawInit(MgDraw *d);
void MG_drawRelease(MgDraw *d);

#endif
