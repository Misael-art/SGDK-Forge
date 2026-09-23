/* mg_types.h -- contrato de dados entre o gerador mugen2sgdk_forge e o runtime.
 * Fonte canonica: tools/mugen2sgdk_forge/runtime/. Copiado para projetos por `install-runtime`.
 * Numeros em ponto fixo 24.8 (MG_FX). Sem float, sem malloc.
 */
#ifndef MG_TYPES_H
#define MG_TYPES_H

#include <genesis.h>

#define MG_FX_SHIFT 8
#define MG_FX       (1 << MG_FX_SHIFT)
#define MG_NONE     0xFFFF

typedef s32 mgfx;

typedef struct { s16 x1, y1, x2, y2; } MgBox;

typedef struct {
    const SpriteDefinition *def;
    s16 axis_x, axis_y;          /* eixo MUGEN dentro da celula */
    u16 cell_w, cell_h;
    u8  pal;                     /* 0 = corpo, 1 = efeitos */
    u8  pad;
} MgSheet;

#define MG_FRAME_HFLIP 1
#define MG_FRAME_VFLIP 2
#define MG_FRAME_BLEND 4         /* blend MUGEN: sem equivalente no VDP (desenhado opaco) */

typedef struct {
    s16 sheet;                   /* -1 = frame vazio */
    u8  frame;
    u8  flags;
    s16 ox, oy;                  /* offset do .air */
    s16 time;                    /* -1 = infinito */
    u8  nclsn1, nclsn2;          /* caixas de ataque / corpo */
    u16 clsn;                    /* indice em boxes[]: clsn1 depois clsn2 */
} MgAnimFrame;

typedef struct {
    s16 id;
    u16 first;                   /* indice em frames[] */
    u8  count;
    u8  loopstart;
    s16 total;                   /* soma dos tempos; -1 se algum frame e infinito */
} MgAnim;

typedef struct {
    u8  type;                    /* MG_CT_* (mg_ops.h) */
    u8  nparams;
    u8  nsym;
    u8  pad;
    u16 cond;                    /* offset em code[] */
    u16 params;                  /* indice em param_offs[] (MG_NONE por parametro ausente) */
    u16 sym;                     /* indice em syms[] */
    u16 gate;                    /* offset em gates[] ([n, cmd...]); MG_NONE = sem portao */
    u8  tkind;                   /* portao de tempo: 0 nenhum, 1 time == tval, 2 inicio do elemento tval */
    s16 tval;
} MgCtrl;

typedef struct {
    s16 id;
    u8  statetype, movetype, physics;
    u8  flags;                   /* bit0 facep2, bit1 hitdefpersist, bit2 movehitpersist, bit3 hitcountpersist */
    u16 p_anim, p_ctrl, p_poweradd, p_sprpriority, p_juggle, p_velx, p_vely;   /* offsets em code[] */
    u16 first_ctrl;
    u16 nctrl;
} MgState;

#define MG_KEY_REL   1           /* ~ */
#define MG_KEY_HOLD  2           /* / */
#define MG_KEY_4WAY  4           /* $ */
typedef struct { u8 key; u8 mods; u8 reltime; u8 pad; } MgCmdKey;
typedef struct { u16 first_key; u8 nkeys; u8 strict; u16 kmask; } MgCmdStep;   /* strict: bit0 ">", bit1 so "/segurar"; kmask: bits MG_K_* cujo evento pode satisfazer o passo */
#define MG_STEP_STRICT    1
#define MG_STEP_HOLD_ONLY 2
typedef struct { u16 first_step; u8 nsteps; u8 time; u8 buffer_time; u8 hold_only; } MgCommand;  /* hold_only: ultimo passo so /teclas */

/* teclas: direcoes relativas a frente do personagem, botoes MUGEN */
enum { MG_K_NONE, MG_K_F, MG_K_B, MG_K_U, MG_K_D, MG_K_DF, MG_K_DB, MG_K_UF, MG_K_UB,
       MG_K_A, MG_K_B_BTN, MG_K_C, MG_K_X, MG_K_Y, MG_K_Z, MG_K_S };

typedef struct { const u8 *data; u32 len; } MgSound;

typedef struct {
    mgfx life, attack, defence, liedown_time, airjuggle;
    mgfx ground_back, ground_front, air_back, air_front, height;
    mgfx walk_fwd, walk_back, run_fwd_x, run_fwd_y, run_back_x, run_back_y;
    mgfx jump_neu_x, jump_neu_y, jump_back_x, jump_fwd_x;
    mgfx yaccel, stand_friction, crouch_friction;
    s16  sparkno, guard_sparkno;           /* anim propria; -1 nenhuma */
} MgConsts;

typedef struct {
    const char *name;
    const MgSheet *sheets;         u16 nsheets;
    const MgAnim *anims;           u16 nanims;       /* ordenado por id */
    const MgAnimFrame *frames;
    const MgBox *boxes;
    const u8 *code;
    const u16 *param_offs;
    const s16 *syms;
    const MgCtrl *ctrls;
    const MgState *states;         u16 nstates;      /* ordenado por id */
    const MgCommand *cmds;         u16 ncmds;
    const MgCmdStep *steps;
    const MgCmdKey *keys;
    const u8 *gates;               /* portoes de comando por controlador */
    const u16 *cmd_bucket_first;   /* [17]: comandos cujo 1o passo reage a evento da tecla k em cmd_bucket[first[k]..first[k+1]) */
    const u8 *cmd_bucket;
    const u8 *hold_cmds; u8 nhold_cmds;   /* comandos cujo 1o passo e so "/segurar" (testados todo tick) */
    const u32 *neg1_masks; u8 neg1_words; /* estado -1: [ncmds+1][words] controladores liberados por comando; ultima linha = sem portao */
    const u16 (*pals)[16];         u8 npals;
    u8 default_pal;
    const u16 *fxpal;
    const MgSound *sounds;         u16 nsounds;      /* indice = posicao no .snd original */
    const MgConsts *consts;
    s16 st_minus1, st_minus2, st_minus3;             /* indices em states[] ou -1 */
    u16 cmd_holdfwd, cmd_holdback, cmd_holdup, cmd_holddown;  /* MG_NONE se ausente */
} MgCharDef;

#endif
