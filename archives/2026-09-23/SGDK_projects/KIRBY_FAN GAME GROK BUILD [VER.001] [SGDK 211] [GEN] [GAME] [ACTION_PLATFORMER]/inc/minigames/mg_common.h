#ifndef MINIGAMES_MG_COMMON_H
#define MINIGAMES_MG_COMMON_H

#include <genesis.h>

/*
 * MISSAO 2026-08-24: infra compartilhada dos 7 minigames.
 *
 * Contrato de uso em cada jogo (update):
 *   MG_tickCommon();                 // trata saida (B) e input da tela de resultado
 *   if (MG_shouldReturn()) return;   // cena mudou: saia imediatamente
 *   if (!MG_resultActive()) { ...logica do jogo... }
 *
 * Audio: MG_begin para a musica, liberando o PSG para AUDIO_playUiTone
 * (contrato do router: tom de UI so com musica parada).
 */

void MG_begin(const char* title);

/*
 * MISSAO 2026-08-24: fundo visual dos minigames. Estrelas em BG_B sempre;
 * colina silhueta em BG_A (linhas 23+) quando comHill. Chamar DEPOIS de
 * MG_begin e ANTES do texto do jogo (mesmo plano: ultima escrita vence).
 * Jogos com campo de borracha (starfall/dodge) usam comHill=FALSE para nao
 * serem comidos pelo erase de texto.
 */
void MG_drawBackdrop(bool withHill);

/* Chamar 1x por frame antes da logica. */
void MG_tickCommon(void);

/* TRUE quando o chamador deve retornar imediatamente (cena mudou). */
bool MG_shouldReturn(void);

/* TRUE enquanto o painel de resultado esta na tela. */
bool MG_resultActive(void);

/* Encerra a partida e desenha o painel de resultado. */
void MG_finish(bool win, s16 score, const char* msg);

/* Contador de frames da partida (0 no begin). */
u16 MG_frames(void);

/* Hub dos minigames (cena propria, tambem usada como retorno). */
void SCENE_mgHubEnter(void);
void SCENE_mgHubUpdate(void);

/* Os sete jogos. */
void SCENE_mgQuickdrawEnter(void);  void SCENE_mgQuickdrawUpdate(void);
void SCENE_mgStarfallEnter(void);   void SCENE_mgStarfallUpdate(void);
void SCENE_mgPunchEnter(void);      void SCENE_mgPunchUpdate(void);
void SCENE_mgDodgeEnter(void);      void SCENE_mgDodgeUpdate(void);
void SCENE_mgSimonEnter(void);      void SCENE_mgSimonUpdate(void);
void SCENE_mgHighjumpEnter(void);   void SCENE_mgHighjumpUpdate(void);
void SCENE_mgRhythmEnter(void);     void SCENE_mgRhythmUpdate(void);

#endif
