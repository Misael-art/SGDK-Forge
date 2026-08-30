# 11 - Game Design Document — MARE_BRAVA [VER.001] [SGDK 211] [GEN] [GAME] [BRAWLER]

## Project Brief

- Promessa central: belt scroller brasileiro onde cada golpe tem peso de maré — combos que empurram, ondas de inimigos que reorganizam o espaço, e o próprio cais (beirada d'água) como arma via ring-out.
- O que o jogador faz: avança pelo cais de Porto Bravo quebrando ondas de capangas do Sindicato da Maré com combos corpo-a-corpo, joelhadas e o contra-ataque assinatura "Empurrão de Maré".
- Por que é digno do Mega Drive: benchmark direto Streets of Rage 2 em game feel (hitstop, knockback, crowd control) com identidade que SOR2 não tem — luta brasileira (muay thai de vila, capoeira futura), calor litorâneo e ring-out costeiro como mecânica espacial.
- O que o projeto NÃO é: não é jogo de luta 1v1, não é run-and-gun, não copia personagens/cenários/música de IP protegida; SOR2 é barra de qualidade, não fonte de conteúdo.

## Visao

Porto Bravo, anos 90: cidade portuária fictícia do litoral brasileiro tomada pelo Sindicato da Maré, milícia que controla o cais e sufoca a vila dos pescadores. TAÍNA, ex-instrutora de muay thai da vila, decide varrer o cais no braço. O jogo é um belt scroller de combate físico expressivo: cada acerto tem hitstop, cada derrubada empurra, e a geografia (beirada do cais, água) participa do combate. A fantasia dos primeiros 10 segundos: calor, mar ao fundo em parallax, e o primeiro jab estalando com peso.

O jogo não é um beat'em up genérico com skin brasileira: a leitura de espaço (profundidade + beirada d'água) e o groove percussivo são pilares, não decoração.

## Core Loop

- Andar pelo cais → onda trava a câmera → combo com hitstop/knockback → gerenciar espaço entre rusher e grappler → derrubar a onda (bônus: ring-out na água) → pickup → avançar.
- Primeiros 30 segundos: andar, encarar a primeira dupla de Crias, acertar combo A-A-A com knockback, ver um inimigo cair na água com splash e shake, pegar espetinho, seguir.

## Feature Scope Map

### Entra no slice

- Movimento 8 direções com profundidade (y-depth ordering)
- Combo terrestre A-A-A (jab → cruzado → chute baixo) com hitstop
- Joelhada aérea (pulo + A)
- Especial defensivo (A+B, custa vida, limpa espaço)
- "Empurrão de Maré": knockback direcional; inimigo arremessado sobre a beirada = ring-out com splash + camera shake + bônus de score
- 2 arquétipos de inimigo: CRIA (rusher) e ESTIVADOR (grappler)
- Wave manager: 1 onda com 3 grupos, câmera com wave-lock
- Pickup de vida (espetinho)
- HUD em WINDOW: health bar, score
- FSM de cena: branding → title → gameplay → game over/clear → title
- Música tema XGM2 + SFX de golpe/acerto/splash

### Entra depois

- Segundo herói (capoeirista) e co-op 2P
- Throw/agarrão completo do herói
- Armas de chão (remo, caixote)
- Boss de fim de fase (Capataz do Sindicato)
- Painel de abertura (cutscene panel_sequence)
- Fases 2+ (mercado, conveses, vila)
- Palette cycling da água e shadow/highlight do entardecer (aguardando promoção de laboratório)
- Música adaptativa por estado de onda

### Fora de escopo

- Modo versus, seleção de rota, RPG elements, lojas
- Qualquer conteúdo de IP protegida
- Scroll vertical de fase, pseudo-3D

## Identidade de Front-End

- Fantasia no primeiro frame: entardecer no cais — logo MARÉ BRAVA pesado com respingo de espuma, mar em movimento atrás.
- Linguagem visual: urbano-litorâneo brasileiro anos 90 (azulejo, ferrugem, rede de pesca, néon de bar).
- Eixo vivo em idle: line_scroll do mar ao fundo (2 velocidades) + press-start pulsante.
- Feedback de seleção: flash de paleta no item + SFX percussivo seco.
- Fora de tom: fonte default/genérica como identidade final, neon cyberpunk, interface corporativa fria, qualquer trade dress de SOR/Capcom.
- `brand_identity_seed`: logo custom com fonte display própria (traço grosso + quebra de onda), teste de leitura em 320x224, fallback = fonte display simplificada sem respingo; press-start com pulso de 30 frames; estratégia runtime: IMAGE em BG_A + texto em WINDOW apenas para debug.

## Ambicao Tecnica, Visual e Sonora

- `quality_promise`: game feel de combate no nível de Streets of Rage 2 — resposta imediata ao input, hitstop consistente, leitura de crowd impecável; percebido no primeiro combo conectado.
- `visual_direction` (criterios de qualidade visual): sprites 44–56px com silhuetas fortes e 3-4 heads; cais em 2 planos (BG_B mar/céu com line_scroll, BG_A cais jogável); paleta quente de entardecer; index 0 transparente; zero alpha blending.
- `sound_direction` (direcao sonora / identidade musical): XGM2; groove de baixo + percussão brasileira (surdo/agogô sintetizados via FM), SFX de impacto secos e altos; splash de ring-out como payoff sonoro.
- `gameplay_quality_bar`: 60fps constantes com 6 sprites ativos (1 herói + 4 inimigos + 1 pickup/FX); colisão multi-ponto justa; sem slowdown fora de hitstop intencional.
- `hardware_strategy`: técnicas do registry com status apto; DMA apenas em VBlank; budget VDP validado antes do runtime; WINDOW para HUD; sem prometer terceiro plano nem efeitos inexistentes.

## Tecnicas Escolhidas

Toda tecnica precisa existir no registry canonico e servir a gameplay, narrativa, leitura, direcao visual ou sonora. Quantidade de efeitos nao substitui coerencia.

| Cena/sistema | Registry id | Tags | Funcao no jogo | Papel visual/sonoro | Owner skills | Budget/evidencia esperada | Fallback |
|---|---|---|---|---|---|---|---|
| CAIS_01 fundo | `line_scrolling` | `LINE_SCROLL`, `PARALLAX`, `VBLANK_BUDGET_AUDIT` | profundidade e direção de avanço | mar/céu em 2 velocidades atrás do cais | hardware/shadow-highlight-scroll-fx, code/sgdk-runtime-coder | tabela HScroll medida em runtime_metrics + screenshot BlastEm | scroll de plano único (HSCROLL_PLANE) |
| CAIS_01 câmera | `camera_scroll_management` | `CAMERA_MANAGEMENT`, `CAMERA_DEADZONE`, `FIXED_POINT_MATH` | wave-lock e leitura do espaço de luta | câmera estável sem jitter, trava por onda | code/camera-system-sgdk | scene_regression com wave-lock capturado | câmera fixa por segmento |
| Combate | `hitstop_camera_shake_feedback` | `HITSTOP`, `CAMERA_SHAKE`, `GAMEPLAY_FEEDBACK` | peso do golpe e payoff do ring-out | freeze 2-5 frames no acerto; shake no splash | code/sgdk-runtime-coder, planning/brawler-game-design | frame data no design contract + captura de combo | knockback sem shake |

### Tecnicas rejeitadas ou adiadas

| Registry id | Decisao | Motivo | Condicao para reconsiderar |
|---|---|---|---|
| `palette_cycling` | adiada | status `LABORATORIO` no registry; bloqueada fora de lab/techdemo | promoção do registry + budget CRAM medido |
| `shadow_highlight_mode` | adiada | status `LABORATORIO`; entardecer via paleta estática resolve o slice | promoção do registry + slot audit |
| `pseudo3d_road_stack` | rejeitada | sem função em belt scroller | nunca neste projeto |

## Kit do jogador e mecanicas core

Kit do jogador (acoes e movimentos): andar 8 direcoes, combo A-A-A, joelhada aerea, especial defensivo A+B, Empurrao de Mare (knockback direcional).

- Combo terrestre 3 hits com cancel window e hitstop crescente (2/3/5 frames)
- Knockback direcional com física fix16 e ring-out na beirada d'água
- Crowd control: rusher força ritmo, grappler pune posicionamento estático
- Especial defensivo com custo de vida (válvula de escape clássica do gênero)
- Profundidade por y-sort com faixa de luta de 64px

## Progressao

- Slice: cena única CAIS_01 com 3 grupos de onda; vitória = painel "DEMO CLEAR" e retorno ao title.
- Ensino invisivel (tutorial invisivel, sem texto): arena 1 convida o combo com 2 CRIAs fracos; arena 2 ensina controle de espaço com o ESTIVADOR; arena 3 sugere o ring-out pelo layout da beirada.
- Jogo completo (contrato v1): 3 atos com boss por ato — cais (CAPATAZ), mercado da madrugada (RAINHA DO MERCADO), sede do sindicato (MARÉ ALTA); expansível a 5 fases em revisão futura do design contract.

## Regras e limites

- Nenhum inimigo spawna fora de tela sem telegraph (entra andando visível)
- Hitstop nunca acumula acima de 6 frames (trava de responsividade)
- Máximo 4 inimigos ativos simultâneos no slice (budget sprite/scanline)
- NÃO é escopo: dano ambiental além do ring-out, plataformas, água jogável

## Character Scale Seed

- TAÍNA: 48px altura (~3.5 heads), frame 48x48; inimigos 44px (CRIA) e 56px (ESTIVADOR)
- Impacto: FOV 320x224 comporta 4 inimigos + herói com folga de leitura; hitbox dupla (corpo 16x40, golpe 24x16 na ponta do membro)
- Carga de animação alvo: herói 8 estados (idle, walk, jab, cross, lowkick, knee, special, hit/down) × 4-8 frames; inimigos 5 estados × 4-6 frames
- Travamento: escala congela no `visual_dna_manifest.scale_contract` antes de key poses

## Camera Behavior Seed

- Modo: scroll horizontal com deadzone estreita (16px), wave-lock nas ondas, clamp nos limites da cena
- Problema que resolve: manter a arena de luta legível e impedir fuga da onda
- Sem look-ahead vertical; shake apenas por evento de impacto (registry `hitstop_camera_shake_feedback`)

## UI Pixel Surface Seed

- Health bar 40x8 em grid inteiro no WINDOW, com buffer de dano (chip delay de 20 frames)
- Fonte HUD 8x8 custom (derivada da fonte display do logo, versão simplificada)
- Score 6 dígitos; retrato 16x16 ao lado da barra
- Evidência esperada: screenshot BlastEm com HUD legível sobre gameplay carregado

## Creative Director Radar Seed

- `project_promise`: "cada golpe tem peso de maré" — sentimento alvo: calor + groove + impacto físico; teste dos 10 segundos: parallax do mar + primeiro jab com hitstop devem comunicar o jogo inteiro sem texto.
- `benchmark_axis_matrix`:
  - game feel de combate → Streets of Rage 2 (herdável: hitstop/knockback/crowd; tradução autoral: ring-out costeiro; fronteira: zero conteúdo SOR; métrica: captura de combo com frame data)
  - leitura de crowd → Final Fight (herdável: silhuetas e telegraphs; tradução: arquétipos autorais; métrica: screenshot com 4 inimigos legíveis)
  - identidade sonora → Thunder Force IV / SOR2 (herdável: FM agressivo; tradução: percussão brasileira em FM; métrica: audio_validation_report)
- `signature_pillars`: (1) peso de maré no combate, (2) cais como arma (ring-out), (3) groove percussivo brasileiro, (4) calor litorâneo na paleta, (5) crowd sempre legível
- `proactive_gap_radar`: risco de "skin brasileira genérica" → mitigar com ring-out mecânico e percussão FM já no slice (owner: planning/brawler-game-design + code/xgm2-audio-director; prioridade alta; docs alvo: doc/11-gdd.md, doc/17-audio-design.md; fallback: slice sem ring-out ainda é brawler competente)
- `signature_scene_candidates`: primeiro ring-out — Estivador arremessado da beirada, splash grande, shake, respingo na espuma do BG (payoff jogável + visual + sonoro + técnico em um evento)

## First Playable Slice

- Primeira entrega jogável: CAIS_01 completo — branding → title → gameplay (3 grupos de onda, 2 arquétipos, ring-out, pickup, HUD) → game over/clear → title.
- Sistemas que prova: FSM de cenas, input abstraction, combate com hitstop/knockback, wave manager, y-sort, colisão multi-ponto, câmera wave-lock, parallax line_scroll, HUD WINDOW, XGM2 música+SFX, heartbeat SRAM de evidência.
- Critério mínimo do loop: completar a onda usando combo + gerenciamento de espaço, com ring-out possível e legível, a 60fps no BlastEm.

## Route Decision Record

- `context_type`: `projeto_novo`
- `dominant_route`: `art_diagnostic`
- `first_skill`: `art/art-direction-selector` (emitir `art_direction_decision_record` + `master_style_manifest`), seguida de `art/art-creation-sourcing` (rota `3_no_art`)
- `first_tool`: `tools/ai_imagegen/` para premium source; conversão via `art-translation-to-vdp`
- `resource_loading_model`: `tilemap_streaming` (BG_A do cais 1344px; contrato `doc/contracts/tilemap_streaming_contract.json`) + `scene_local_preload` apenas para sprites/HUD/BG_B
- `asset_strategy`: geração IA → `data/source_art/` com `premium_source_manifest` → aprovação humana → conversão VDP (spritesheet strips + tilemap IMAGE/MAP)
- `evidence_required`: `art_direction_decision_record`, `premium_source_manifest`, laudo `megadrive-vdp-budget-analyst`, build ok, screenshot BlastEm + `save.sram` MDRT
- `forbidden_shortcuts_until_evidence`: sem arte placeholder promovida a final; sem runtime de gameplay antes do laudo de budget VDP; sem `.res` de sprite antes do scale_contract travado

## Escopo atual

- Fase em produção: FASE 1 concluída (GDD) → próxima: FASE 2 (tdd_contract.json) e FASE 3 (arte CAIS_01)
- Fora do escopo desta fase: tudo listado em "Entra depois" e "Fora de escopo"

## Cenas de Front-End

- Title screen: logo + mar em line_scroll + press start (identidade acima)
- Menu principal: START apenas no slice (opções/sound test = entra depois)
- Game over / Demo clear: painéis estáticos com paleta própria

## Production Runtime Contract (seed)

- `scene_manager_scope`: FSM determinístico branding → title → gameplay → gameover/clear, enter/update/exit/cleanup por cena
- `input_abstraction_scope`: leitura centralizada 3/6 botões via camada única (JOY), sem leitura direta em cena
- `persistence_scope`: `none` para gameplay → `save_system_contract_not_applicable`; SRAM usada apenas para heartbeat de evidência MDRT
- `region_timing_scope`: NTSC-first (60fps); PAL declarado como ajuste de timing por flag, validação futura
- `rom_mastering_scope`: header autoral, checksum via sizebnd, sem SRAM de jogo
- `code_review_scope`: review formal por skill governance antes de closeout de cena
- `ci_gate_scope`: `tools/sgdk_wrapper/ci/run_golden_validate.ps1` como gate local
- `asset_optimization_scope`: dedup de tiles + compressão padrão rescomp; medição no res_graph_report

## Roteiro Scope

Ver `doc/12-roteiro.md`: slice sem diálogo em gameplay; texto apenas em title (logo/press start), painel DEMO CLEAR e game over. Tom: seco, direto, regional sem caricatura.

## Vibe Playable Birth Route

Projeto nascido pela rota Vibe Playable, bloqueada em `blocked_no_premium_source`.

Pedido natural de jogo/fase/personagem/FX aciona o roteador visual antes de runtime definitivo.

Nenhum asset, aprovação humana ou evidência BlastEm existe ainda; gates visuais: premium source → aprovação humana → conversão VDP → build → evidência BlastEm.
