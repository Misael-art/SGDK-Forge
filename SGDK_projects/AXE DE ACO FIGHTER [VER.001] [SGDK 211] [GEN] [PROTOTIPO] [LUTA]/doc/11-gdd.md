# 11 - Game Design Document - AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]

## Project Brief

AXE DE ACO FIGHTER e um jogo de luta 1v1 autoral para Mega Drive/SGDK 2.11. O slice atual abre direto na luta, sem landing page e sem menu textual de debug. A promessa e uma luta curta e legivel entre Marina "Raio de Roda" Santana e Bento "Martelo" Duarte no Terreiro Neon da Ladeira.

O projeto nao esta em status AAA: o loop jogavel existe em ROM real, mas a entrega visual final permanece bloqueada porque os sprites finais de personagem sao strips locais/procedurais e nao strips premium por estado.

## Core Loop

- Jogador controla Marina, aproxima ou recua, le o posicionamento de Bento e escolhe entre ataque leve, ataque medio, rasteira/especial curto, guarda, esquiva baixa, hop e dash.
- Golpes aplicam hit stun, pushback, dano e spark separado.
- Bento usa IA simples para manter pressao e criar risco basico.
- O round termina por HP ou timer; o slice atual foca em provar combate, leitura e runtime.

## Feature Scope Map

### Entra no slice atual

- Cena direta de luta 1v1.
- Marina jogavel por controle P1.
- Bento como rival controlado por IA simples.
- HP P1/P2, round timer e HUD formal.
- Estados minimos: idle/ginga, walk_forward, walk_back, dash, crouch/esquiva, hop, guard, light_attack, medium_attack, sweep_or_throw, hurt, knockdown, getup.
- Spark de impacto e dust como sprites FX separados.
- Camera shake leve em golpes mais fortes.
- Build SGDK 2.11, BlastEm e relatorios canonicos.

### Entra depois

- Sprites premium por acao gerados/curados com continuidade real.
- Audio validado com captura/criterio de QA.
- VDP visual dump quando o fluxo VLAB estiver habilitado.
- IA com mais contexto de distancia, whiff punish e defesa temporal.
- Rounds, tela de versus e polimento de front-end apos o primeiro slice jogavel.

### Fora de escopo desta entrega

- Declarar AAA ou Stable.
- Usar ROM fake, screenshot fake ou tempdir descartado como evidencia final.
- Copiar personagens, silhuetas, cenarios, poses ou timing de referencias comerciais.

## Identidade Visual

- Marina: mulher adulta brasileira, atletica, cabelo cacheado preso por faixa vermelha, top verde escuro, calca branca de capoeira com detalhe amarelo e faixa vermelha.
- Bento: homem adulto mais pesado, camisa azul petroleo, calca creme, faixa laranja e bandagens/luvas leves.
- Cenario: Terreiro Neon da Ladeira, ladeira urbana ficticia inspirada por Salvador noturna, mar distante, arcos, postes, fitas e roda de capoeira.
- Paleta: arcade viva, outlines firmes, sombras frias para branco da roupa, separacao forte entre BG e lutadores.

## Estado de Entrega

- Classificacao final: prototype_playable.
- Status visual: visual_gate_blocked.
- Evidencia principal: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\FINAL_DELIVERY_REPORT.md.
