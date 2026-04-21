#ifndef SGDK_RUNTIME_PROBE_H
#define SGDK_RUNTIME_PROBE_H

#include <genesis.h>

#define MD_RT_SCHEMA_VERSION 1
#define MD_RT_MAGIC_HI 0x4D44
#define MD_RT_MAGIC_LO 0x5254
#define MD_RT_MAX_SAMPLES 1800
#define MD_RT_SAMPLE_DATA_OFFSET 32

/*
 * Heartbeat: marcador ASCII "READY" (5 bytes) gravado em SRAM para que o host
 * detecte que a ROM chegou a um estado navegavel SEM precisar esperar o
 * payload MDRT completo (que so aparece apos ~90 frames de warmup + 1 export).
 * O host polla este offset durante press_until_ready para saber quando parar
 * de bombardear o START/A e prosseguir com a proxima acao.
 *
 * Layout em SRAM:
 *   0x0100 .. 0x0104 : "READY" (5 bytes ASCII, sem terminador)
 *   0x0105 .. 0x0107 : reservado (zerado)
 *   0x0108 .. 0x010B : u32 BE contendo o numero do frame em que foi emitido
 *   0x0200 ..        : assinatura MDRT + payload normal
 */
#define MD_RT_HEARTBEAT_SRAM_OFFSET 0x100
#define MD_RT_HEARTBEAT_MAGIC_LEN   5

enum
{
    MD_RT_WORD_MAGIC_HI = 0,
    MD_RT_WORD_MAGIC_LO,
    MD_RT_WORD_VERSION,
    MD_RT_WORD_FLAGS,
    MD_RT_WORD_TARGET_FPS,
    MD_RT_WORD_SCENE_ID,
    MD_RT_WORD_FRAME_WINDOW_TARGET,
    MD_RT_WORD_FRAME_WINDOW_COMPLETE,
    MD_RT_WORD_FRAMES_SEEN,
    MD_RT_WORD_SAMPLES_RECORDED,
    MD_RT_WORD_OVER_BUDGET_FRAMES,
    MD_RT_WORD_CPU_LOAD_MAX,
    MD_RT_WORD_CPU_LOAD_PREV,
    MD_RT_WORD_CPU_LOAD_JITTER_MAX,
    MD_RT_WORD_MAX_SCANLINE_SPRITES,
    MD_RT_WORD_FX_PEAK_CONCURRENCY,
    MD_RT_WORD_SPRITE_ENGINE_PEAK,
    MD_RT_WORD_ACTIVE_FX,
    MD_RT_WORD_PERCEPTUAL_FLUIDEZ,
    MD_RT_WORD_PERCEPTUAL_LEITURA,
    MD_RT_WORD_PERCEPTUAL_NATURALIDADE,
    MD_RT_WORD_PERCEPTUAL_IMPACTO,
    MD_RT_WORD_SAMPLE_CAPACITY,
    MD_RT_WORD_BUDGET_THRESHOLD,
    MD_RT_WORD_CPU_LOAD_SUM_HI,
    MD_RT_WORD_CPU_LOAD_SUM_LO,
    MD_RT_WORD_RUNTIME_FLAGS,
    MD_RT_WORD_RESERVED_0,
    MD_RT_WORD_RESERVED_1,
    MD_RT_WORD_RESERVED_2,
    MD_RT_WORD_RESERVED_3,
    MD_RT_WORD_RESERVED_4
};

extern volatile u16 g_mdRuntimeProbe[MD_RT_SAMPLE_DATA_OFFSET + MD_RT_MAX_SAMPLES];

void MD_RT_Init(void);
void MD_RT_SetScene(u16 sceneId);
void MD_RT_FrameBegin(void);
void MD_RT_FrameEnd(void);
void MD_RT_RecordSpriteSpan(s16 y, u16 height);
void MD_RT_MarkFXStart(u16 fxId);
void MD_RT_MarkFXEnd(u16 fxId);
void MD_RT_SetPerceptualScores(u16 fluidez, u16 leitura, u16 naturalidade, u16 impacto);

/*
 * Emite o marcador ASCII "READY" em SRAM[0x100] + frame corrente em BE u32
 * em SRAM[0x108]. Idempotente: pode ser chamado mais de uma vez sem efeito
 * colateral (grava sempre os mesmos 5 bytes). Projetos devem chamar apos a
 * primeira cena interativa estar pronta (normalmente ao fim do warmup,
 * antes do primeiro export MDRT completo). NAO chame em ISR: usa SRAM_enable
 * que manipula $A130F1.
 */
void MD_RT_ExportHeartbeat(u32 currentFrame);

#endif
