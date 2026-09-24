# Success Patterns

Registre aqui apenas padroes que funcionaram neste projeto com evidencia rastreavel.

| Data | Classificacao | Contexto | Padrao observado | Evidencia | Limite de uso |
|---|---|---|---|---|---|
| 2026-08-18 | `promotion_candidate` | IMAGE BEST no display | unpackTileMap em buffer estatico no warmup + TILE_ATTR assado + DataRect/DMA_QUEUE. Serie cpu 160→92→83, ob 9→0 | ROM e6437530 / ceaa7028 / 661e4086; d3/d4/d5 | Dest sem malloc. Fatiar so depois de unpack. Owner: sgdk-runtime-coder |
| 2026-08-18 | `promotion_candidate` | evidencia VLAB | Screenshot e o beat; frame_counter VLAB anda de 60 em 60 e atrasa o SRAM. Dois F151 podem ser atos diferentes | d2_reveal vs d2_lock; probe export 60 / warmup 90 | Nao e relogio fino. Owner: emulator-vdp-evidence-curator |
| 2026-08-18 | `local_note` | The Forge fio | 12 fagulhas do preludio ao nome no lugar de 56 estilhacos: spr 51→13, climax sem +ob | ROM e79a9de4…; d2_hit1 spr=13 | Nao reabrir enxame sem resim de scanline |
| 2026-08-18 | `local_note` | The Forge martelo | Prefetch quadro 4 no slot livre (lock t==21) e 1/2 em F12–13 com sprite oculto | ROM ceaa7028…; d4_hit1 | Nao evictar o quadro que esta na tela |
| 2026-08-18 | `local_note` | The Forge ceu | Conceito IA so para composicao; placa VDP reconstruida em 16 cores 9-bit. Unique 125→26. Ato I fica navy+estrelas | ROM 661e4086…; d5_sky | Ainda placeholder. Selo BlastEm recusa void |
| 2026-08-18 | `local_note` | The Forge nametable | Assar TILE_ATTR no preludio e escrever metades com DataRect+DMA_QUEUE. cpu 92→83, ob=0 | ROM ceaa7028…; d4_hit1/d4_forge | Pico 83 residual. Nao e validado_budget |
| 2026-08-18 | `local_note` | The Forge parede | Unpack APLIB 40x28 no preludio (probe warmup) e nametable no reveal. ob 9→0, cpu 160→92 | ROM e6437530…; d3_hit1/d3_forge | Pico 92 residual. Dest estatico, sem malloc |
| 2026-08-18 | `local_note` | The Forge descida | Paleta da forja so depois do tilemap da parede: emerge escura, nao muro fantasma no ceu. 12 fagulhas no lugar de 56 estilhacos: spr 51→13 | ROM e79a9de4…; d2_reveal/d2_lock/d2_hit1/d2_forge | Golpes ainda cpu 160 / ob 9. Nao e validado_budget |
| 2026-08-18 | `local_note` | branding_sequence_v2 ato 3 | Forja travada + restore unico de props + nomes na parede (y<64) + PRESENTS no fogo. over_budget 0 em F271/331/451/511 | ROM 40fec78b…; fin2/fin4/fin6/fin72 | Nao e licenca para arte final nem ready_for_aaa |
| 2026-09-11 | `promotion_candidate` | lutador arcade nativo | Recortar a sheet por faixa (`is_sheet_bg` so no layout) e tratar ciano residual so no matte/quantize. Paleta unica + remap global. Sem shrink 32x64. | ROM 62befee3…; `02_after_mode2.png`; `rascunho/ken_arcade_convert_report.json` | Nao e licenca Capcom. Owner: art-conversion-pipeline |
| 2026-09-11 | `promotion_candidate` | BGM MD barato | MIDI de referencia vira VGM FM+PSG (3 ch YM2612 + noise), loop 8–16 compassos, sem PCM. 30751 B MIDI -> 9333 B VGM. Manter XGM1 se o projeto ja tem SFX PCM nele. | `rascunho/ken_stage_vgm_report.json`; sound.res 162 KB; audio.raw RMS nao-zero | Nao trocar HAMOOPIG para XGM2. Owner: megadrive-music-composition |
| 2026-09-11 | `local_note` | input MODE | No Mega Drive, SELECT e `BUTTON_MODE`. MODE sozinho cicla id; MODE+START fica debug. BlastEm `f` = pad1 MODE. | `src/input.c`; `02_after_mode2.png` | Nao inferir 6-button. Owner: input-system-sgdk |
| 2026-09-11 | `promotion_candidate` | sprite CPS vs SNK | Sheet CPS/SF olha para a esquerda; HAMOOPIG/Ryo olha para a direita. Espelhar os frames na conversao, nao inverter HFlip no runtime (FUNCAO_SPR_POSITION assume arte para a direita). | ken/100.png apos FLIP_LEFT_RIGHT; 00_select.png | Owner: sprite-animation |
| 2026-09-11 | `local_note` | HUD luta | Barra SF cabe em sprite 128x16 / 13 frames + KO. Amarelo=energiaBase, vermelho=energia atrasada. VRAM pinada. P2 = HFlip. | 03_fight_hud.png; hud_gfx.res 3 KB packed | Nao e WINDOW plane. FPS cai com 4 barras. Owner: sgdk-runtime-coder |
| 2026-09-11 | `promotion_candidate` | soft reset SGDK | `int main(bool hardReset)` e `if (!hardReset) SYS_hardReset();` forcam boot limpo. Title fade apos Tab prova RAM zerada. | ROM c0a084e4…; 07_after_soft_reset.png; 11_fight_after_reset.png | Nao usar para persistir SRAM de jogo. Owner: sgdk-runtime-coder |
| 2026-09-11 | `local_note` | hitbox Ken | Hurt/hit do Ken no ultimo ou unico quadro do strip (`ken_anim_for`), nao copiar frames 2–5 do Ryo. | 05_ken_attack.png; 12_post_reset_attack.png | Prototype; boxes nao sao CPS. Owner: collision-system-architect |
| 2026-09-11 | `local_note` | sombra PAL1 | Com HUD na PAL1, a sombra so funciona se os pixels opacos usarem um index escuro dessa paleta. | sombra.png index 11; 00_hud_both.png | Nao reusar paleta de personagem na PAL1. |
| 2026-09-11 | `promotion_candidate` | HUD WINDOW | Barra 128px de sprite some no H40; a mesma arte em TILESET no WINDOW (depois do BG, prio FALSE, index 0→11) aparece. | ROM 21f1654d…; `00_hud_both.png` P2 amarela a direita | Nao e terceiro plano. Off no teardown. Owner: sgdk-runtime-coder |
| 2026-09-11 | `promotion_candidate` | roster lutador | Checklist Ken generaliza para id=3: tabela, PLAYER_STATE, paleta, hitbox no ultimo quadro, gravidade 550, MODE, seletor, SFX, especiais sem fireball. | ROM c81fee9f9f7b799f30514418f01ceeb8d293788c51b5b6c89fb4376964e98589; src/player_musgo.c; fsm.c case 3; screenshot seletor | Prototype. Owner: sgdk-runtime-coder. Nao e fighting_2d_traditional opt-in. |
| 2026-09-11 | `promotion_candidate` | palco luta CPS | Medir unique tiles, aplanar para IMAGE 512x256 com bloco 4px / 10 cores quando 4 paletas e ~3191 tiles bloqueiam. Camera H medio + V follow 0.5, rest vscroll=height-224. | ROM 1eb99f6c…; interactive-showdown-20260911T225648Z; convert_showdown.py | Placeholder / IP estudo. Sem parallax. Owner: multi-plane-composition + camera-system-sgdk |
| 2026-09-11 | `local_note` | facing original | Grappler autoral desenhado a direita encaixa no HFlip do P2; P2 Musgo olha para o Ryo no seletor. | out/emulator_evidence/blastem-linux-20260911T212135Z-1769103/screenshot.png | Nao comecar arte original olhando esquerda. Confirma CPS vs SNK. Owner: sprite-animation |
| 2026-09-11 | `local_note` | prova no boot | Default P2=Musgo faz o primeiro BlastEm mostrar o lutador novo no seletor sem input. | screenshot.png P1 RYO P2 MUSGO; src/select.c cursorP2_ID=3 | So para fatia de prova. Nao e roster de produto. |
| 2026-09-11 | `local_note` | video-first | Idle e walk em camera travada no lugar colhem ciclo; soco so no hibrido. | data/source_art/musgo/video_frames/; res/sprite/musgo/420.png | Path de harvest sem `%`. Owner: sprite-animation |
| 2026-09-11 | `local_note` | IP ancora | Sheet CPS2 de grappler como escala/timing/cell, paleta e silhueta autorais, nenhum pixel da sheet no .res. | doc/art/musgo/character_identity.md; convert_musgo.py | Nao img2img da sheet. Owner: character-design |
| [DATA] | `local_note` | [cena/sistema] | [o que funcionou] | [build/log/screenshot/hash] | [onde nao aplicar] |

## Regras

- Nao transforme sucesso local em regra global.
- Nao registre preferencia estetica como skill tecnica.
- Nao use este arquivo para alterar `.agent`, registry ou `lib_case`.
