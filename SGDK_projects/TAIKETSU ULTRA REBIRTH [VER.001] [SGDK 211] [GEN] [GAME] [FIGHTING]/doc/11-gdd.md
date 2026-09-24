# 11 - Game Design Document - TAIKETSU ULTRA REBIRTH

## Project brief

TAIKETSU ULTRA REBIRTH e um fighting 2D round-based para Mega Drive: seis lutadores disputam um torneio em arenas industriais, e cada acerto muda espaco, ritmo e carga de especial. Jack e Ryo preservam a referencia HAMOOPIG de GameDevBoss / Daniel Moura; Kairo Vant, Mira Quell, Orion Flux e Vanta Zero sao autorais.

O projeto usa SNK 1996/SVC Chaos como eixo de geracao de linguagem, nao como fonte de copia. O destino total e D0-D6; o claim atual permanece vertical_slice ate evidencia real.

## Core loop

`ler distancia -> escolher normal/defesa/aereo -> confirmar dano ou whiff -> carregar especial e ganhar espaco -> gastar no especial e recuperar a barra ao conectar -> repetir ate vencer a rodada`.

Nos primeiros 30 segundos o jogador escolhe Jack, enfrenta Kairo Vant, testa defesa e whiff, enche a barra, conecta um especial e ve o feedback de hitstop, shake e CS-A.

## Fighting surface

- Roster: Jack, Ryo, Kairo Vant, Mira Quell, Orion Flux e Vanta Zero.
- Jack/Ryo sao mantidos como regua de escala e base de engine.
- C1 = Kairo Vant. A altura do frame idle final deve satisfazer `kairo_idle_minimum_visible_height:minimum_visible_height=ceil(1.25*max(full_body_reference_visible_height))`; nenhum numero e aceito sem leitura do model sheet e reconferencia no sprite final/VRAM.
- C2 = Mira Quell, personagem feminina de mobilidade e armadilha ritmica.
- C3 = Orion Flux, personagem com poderes, especiais e golpes aereos obrigatorios.
- C4 = Vanta Zero, chefe final desbloqueavel; nao selecionavel antes da condicao persistida.

## Sistema de especial

Cada lutador possui barra de 100 unidades. Ela carrega por dano dado, dano recebido, defesa e whiff penalizado. Um especial consome a barra inteira. Se conectar, a barra volta a cheia: esta e uma regra intencional de recompensa e nao um bug. Se falhar ou for bloqueado, a barra permanece consumida e o jogador perde a janela de vantagem.

### Regra numerica D1 da barra

| Evento | Variacao | Observacao |
|---|---:|---|
| dano causado | +1 por 10 pontos de dano, arredondado para baixo | limite em 100 |
| dano recebido | +1 por 10 pontos de dano, arredondado para baixo | limite em 100 |
| defesa confirmada | +2 por impacto defendido | nao gera refill sozinho |
| whiff de normal pesado/especial | -6 | minimo 0; whiff leve nao penaliza |
| especial declarado | -100 | custo imediato no frame de ativacao |
| especial conectado | 100 | aplicado 2 frames apos o impacto, depois do hitstop |
| especial bloqueado ou errado | 0 | sem recuperacao automatica |

O HUD exibe unidades inteiras de 0 a 100. A tabela e o contrato de balanceamento do D1; qualquer ajuste posterior exige nova medicao e trace de dano, defesa, whiff e refill.

## Scope map

### Entra no D1

- Jack contra Kairo Vant; uma arena Cinder Circuit; round system; input 6 botoes; hit/hurt boxes; barra de especial; um especial conectado e refill.
- CS-A de Jack, CS-D de Jack e Kairo, e CS-E exclusivo do par ordenado `jack -> kairo_vant`.
- CS-E deve mover simultaneamente retrato animado, dois corpos inteiros reagindo e camera por scroll/corte.

### Entra depois

- D2 adiciona Ryo, Mira Quell e Orion Flux com movesets e aereos de Orion.
- D3 fecha CS-A/CS-B/CS-C/CS-D por personagem/stage.
- D4 escreve os 30 dialogos ordenados `speaker_a -> speaker_b`, sem texto repetido.
- D5 adiciona Vanta Zero, unlock por condicao de torneio e SRAM CRC16.
- D6 integra banco final XGM2 e fecha golden CI.

### Fora de escopo

- online, rollback, tag team, arena 3D, physics de ringout e multiplayer simultaneo.
- arte final procedurally drawn; placeholders nao podem ser promovidos.

## Kit do jogador

O kit do jogador de D1 e pequeno, legivel e suficiente para ensinar neutral sem
depender de texto: andar e virar, salto com gravidade fixa, defesa em pe,
ataque leve/medio/pesado, especial, pausa e reinicio de round. Cada golpe tem
startup, active e recovery declarados; cada ataque usa hitbox, hurtbox e pushbox
separadas. O jogador escolhe entre aproximar, confirmar um normal, recuar,
defender ou arriscar o especial quando a barra chega a 100. Jack e Kairo
compartilham o contrato de controle, mas nao compartilham silhueta, alcance ou
frame data de golpe.

## Regras sistemicas e estado do jogo

O fluxo global e `BOOT -> BRANDING -> MENU -> SELECT -> STAGE_INTRO -> ROUND_START
-> FIGHT -> ROUND_RESULT -> MATCH_RESULT`. Durante `FIGHT`, somente um owner
possui input, camera, sprites, audio e filas DMA; a troca de cena desmonta os
recursos temporarios antes de entregar ownership ao estado seguinte. Um round
termina por vida zero ou relogio zerado; a partida e melhor de tres. Hitstop,
camera shake e feedback de impacto congelam a leitura sem congelar o relogio de
round de forma ambigua. A barra segue a tabela numerica deste documento, e um
especial conectado agenda o refill dois frames depois do impacto, apos o
hitstop. Nenhuma regra usa ringout, online, tag team ou alocacao dinamica.

## Progressao da fase e mapa de secoes

O mapa jogavel de D1 e deliberadamente linear: menu, selecao de Jack/Kairo,
intro de Cinder Circuit, revelacao dos dois corpos, primeiro round, confirmacao
de especial, retorno ao combate e resultado. O palco tem uma lane horizontal
com limites de camera, uma arena central de leitura e o reator como landmark;
nao existe terceiro plano BG. Em D2 a progressao acrescenta Ryo, Mira e Orion
sem alterar a regra de dois lutadores ativos residentes. D3 expande cenas e
variacoes de arena; D4 expande dialogos; D5 libera Vanta Zero por condicao
persistida; D6 fecha audio, P2 e a matriz golden. Cada degrau exige nova
medicao de VRAM, scanline e evidencia antes de promover o conteudo.

## Inimigos, riscos e ritmo

Em D1 Kairo e o oponente controlado por regras simples de distancia: aproxima
quando fora do alcance, defende depois de um ataque bloqueado e escolhe normal
ou especial apenas quando a janela e legal. Ele nao simula uma IA completa e nao
cria comportamento invisivel ao jogador. As ameacas do combate sao whiff,
overcommit, defesa tardia, hitstun e gasto errado da barra; o risco da arena e
espacial, nao dano procedural do cenario. O ritmo alvo e: 0–5 s entrada e
leitura da arena, 5–15 s neutral e primeiro contato, 15–30 s carga e defesa,
30–45 s confirmacao do especial e payoff, depois rounds curtos ate o resultado.
O relogio de round impede espera passiva e o hitstop curto preserva impacto.

## Tutorial invisivel, assinatura e climax

O onboarding diegetico ensina sem painel textual: a entrada de Cinder Circuit
coloca os dois lutadores em silhuetas separadas; o primeiro ataque de Kairo
mostra a janela de defesa; a barra vazia e o brilho de carga ensinam custo e
recompensa; o primeiro especial confirmado exibe hitstop, shake, stinger e
refill. CS-E e o climax de D1: a camera abre para os dois corpos inteiros,
retratos reagem e a arena responde ao impacto antes de devolver controle ao
jogador. O climax nao pode ser substituido por card estatico nem por texto que
descreva uma acao nao observada.

## Criterios de qualidade visual

A barra visual exige 320x224 legivel em 4:3, silhueta dos dois lutadores sem
confusao com o fundo, tres planos funcionais no maximo (BG_B, BG_A e
foreground/WINDOW), grid 8x8, indice 0 transparente quando aplicavel, no
maximo 15 cores visiveis por tile e contraste suficiente para leitura CRT. A
identidade de Cinder Circuit e reactor/arena circular, metal frio e calor
laranja; nenhum probe, logo HAMOOPIG ou asset de laboratorio pode ser
promovido como arte final. A aprovacao exige screenshot BlastEm, SRAM,
`visual_vdp_dump.bin` quando a cena viva estiver sob suspeita, revisao humana e
motion evidence para claims de animacao.

## Ambicao tecnica e direcao sonora

A ambicao tecnica de D1 e 60 fps NTSC na cena pesada com dois lutadores grandes,
HUD, hitstop, shake, especial e audio ativo. O teto do hardware e medido, nao
estimado: H40 deve respeitar simultaneamente 20 sprites e 320 pixels por
scanline; DMA ocorre somente no VBlank; residency deve registrar tiles de
codigo, mapas, fontes, SAT, reservas e janelas de animacao. O fallback explicito
em caso de estouro e reduzir efeitos ou roster residente, nunca flicker para
mascarar overflow.

A direcao sonora separa identidade e feedback. XGM2 sustenta o loop de arena;
PSG cobre confirmacao, defesa, hitstop e resultado; PCM fica reservado a
stingers de maior impacto quando a arbitragem de canal permitir. Todo cue tem
owner, prioridade, duracao e regra de teardown. Ataque conectado deve soar
diferente de whiff e bloqueio, e a troca de cena deve zerar cues pendentes sem
cortar a musica por acidente. O validator de recursos mede declaracoes e
orcamento; a aprovacao final ainda exige reproducao observada na cena pesada.

## Front-end

O primeiro frame e uma tela de titulo com o wordmark quebrado por uma linha de impacto: a fantasia e um torneio que reescreve o destino dos lutadores. Menu, select, intro de stage e fight usam fonte pixel autoral ou fallback apenas durante debug. A selecao pulsa a silhueta do lutador e mostra a barra de especial como promessa de risco; nenhum card estatico e aceito como identidade final.

## Ambicao

- `quality_promise`: game feel arcade legivel em 320x224, com corpos grandes, hitstop curto, especiais com payoff e cutscenes vivas.
- `visual_direction`: pixel art indexada em grid 8x8, contraste separado por plano, paleta limitada e retratos expressivos; idioma SNK 1996/SVC apenas como benchmark de funcao.
- `sound_direction`: XGM2 para musica, stingers e SFX; audio de impacto deve mudar a decisao perceptiva e sera escutado em P2.
- `gameplay_quality_bar`: input <= 1 frame alvo, hitboxes explicitas, sem flicker como fallback, 60fps NTSC na cena pesada.
- `hardware_strategy`: somente dois lutadores ativos residentes, efeitos e retratos em janelas de VRAM, DMA exclusivamente no VBlank e dois limites de scanline medidos.

## Tecnicas escolhidas

| Sistema | Registry id | Funcao | Owner | Budget/evidencia | Fallback |
|---|---|---|---|---|---|
| camera de luta | camera_scroll_management | manter os dois corpos na arena sem perder neutral | code/camera-system-sgdk | camera contract + BlastEm | camera fixa por room |
| impacto | hitstop_camera_shake_feedback | tornar confirmacao e especial legiveis | code/sgdk-runtime-coder | runtime metrics + captura | hitstop sem shake |
| roster | tile_cache_streaming_refcount | trocar sheets sem manter seis na VRAM | hardware/vram-streaming-dma-queue | audit_tile_residency + DMA report | roster parcial do D1 |

Adiadas: H-Int/palette blending, Shadow/Highlight e multiplexacao temporal. O gap 17/18 e a necessidade de preservar leitura bloqueiam essas tecnicas ate nova medicao.

## Route decision record

- `context_type`: projeto_novo -> aaa_game
- `dominant_route`: planning -> fighting specialization -> scene architecture -> budget -> runtime -> validation
- `first_skill`: planning/game-design-planning; depois planning/fighting-game-design
- `first_tool`: `tools/sgdk_wrapper/validate_project_context.ps1`, `validate_fighting_specialization.ps1`, `vdp_scanline_simulator.py`
- `resource_loading_model`: tilemap_streaming + animation_window_streaming; dois lutadores ativos residentes
- `asset_strategy`: source translation para Jack/Ryo e autoria nativa para os quatro originais; toda saida nasce technical_candidate
- `evidence_required`: reports JSON, ROM hash, screenshot BlastEm, save.sram, visual_vdp_dump.bin quando a cena viva for fechada
- `forbidden_shortcuts_until_evidence`: arte antes de medicao, seis lutadores residentes, flicker, PNG procedural promovido e DMA fora do VBlank

## Roadmap D0-D6

| Degrau | Fechamento |
|---|---|
| D0 | Fase -1, GDD/TDD, opt-in, cobertura, Q1 |
| D1 | Jack + Kairo, Cinder Circuit, especial, CS-A/CS-D/CS-E; P1 + Q3 |
| D2 | Jack/Ryo/Kairo/Mira/Orion jogaveis; Q3 de roster |
| D3 | CS-A/B/C/D completos por personagem/stage |
| D4 | 30 CS-E unicos e auditados |
| D5 | Vanta Zero, unlock e persistencia provados |
| D6 | audio final, P2, golden CI e P3 |

## First playable slice

Cena `combat_cinder_circuit`: boot -> select Jack/Kairo -> CS-C stage-only -> revelacao/entrada dos dois lutadores -> CS-D de Jack e Kairo -> CS-E -> luta -> barra de especial -> CS-A ao conectar -> retorno ao combate -> resultado. O slice so existe depois de build, validacao, evidencia BlastEm e laudo live_scene_bar; antes disso e documentado/implementado no maximo.
