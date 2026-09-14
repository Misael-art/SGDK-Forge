# 13 - Especificacao Tecnica por Cena - HAMOOPIG [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]

> Documento canonico para budgets por cena, contrato de evidencia e papel formal de cada surface.
> Menu, title screen e outras telas de front-end contam como cenas formais.

## Contexto de escala

Contexto do projeto: `technical_demo` (porta direta da engine HAMOOPIG). Teto de claim: `prototype`.
Os budgets abaixo sao os observados na engine upstream, NAO metas de producao AAA deste workspace.
Porta estendida: inclui seletor, HUD de atlas, Musgo e novo ciclo de round.

## scene_roadmap

### Cena 0 - `room_tela_hamoopig` (abertura/logo)

- origem: engine upstream (FSM de salas em `src/fsm.c`)
- conteudo observado: fundo em grade azul com onda/logo HAMOOPI, transicao por fade de paleta
- evidencia: `out/emulator_evidence/blastem-linux-20260910T192043Z-1434440/screenshot.png`

Contrato de round (2026-09-11):

- formato: melhor de tres (`ROUNDS_TO_WIN=2`)
- KO: vida chega e permanece em zero; vencedor recebe uma vitoria
- time over: maior vida vence; empate nao concede vitoria
- reset: `FUNCAO_ROUND_RESTART` reinicializa estado transitorio simetricamente e preserva IDs, paletas e placar
- relogio: `ROUND_CLOCK_TICKS=38` preserva o tick arcade legado; nao e declarado como segundo real
- evidencia exigida: KO de P1 e P2, empate/time over, round seguinte restaurado e especial/projetil apos transicao
- estado da arte 2026-09-12: Showdown usa o preview local solicitado, 14 cores opacas nos indices 1..14 e 768 tiles representantes, sem ampliacao 4x4. Indice zero reservado ao transparente. HUD de energia usa 16 colunas e zera integralmente; vida positiva conserva uma coluna.

### Cena 1 - `room_title_menu` (tela de titulo)

- owner: `src/title.c` via `gRoom==1`
- entrada: boot deterministico, fundo `room_0_bgb/room_0_bga` e fonte atlas 16x16
- abertura: splash HAMOOPIG permanece íntegro por 120 frames após a carga; o
  primeiro botão apenas revela o menu (não é reutilizado como confirmação)
- menu principal: `START` e `OPTION`; confirmação só ocorre depois do splash
- `START`: fade curto, limpeza do plano e saída para `gRoom==2` (seletor)
- `OPTION`: `SFX ON/OFF`, `MUSIC ON/OFF` e `BACK`; valores valem durante a sessão
- controles: P1 D-pad navega, A/START confirma, B retorna; P2 ignorado
- composição: painel estreito no plano A, sem faixa preta de tela inteira; cursor de um tile; o painel é aplicado somente após restaurar o mapa original, sem DMA concorrente
- budget: fonte atlas residente em tiles 620..763, cursor/painel em 764..765; DMA somente ao entrar ou redesenhar o menu
- evidência exigida: boot, navegação, toggles, retorno e entrada única no seletor

### Cena 2 - `room_character_select` (seletor)

- owner: `src/select.c`
- entrada: LEFT/RIGHT alterna Ryo, Ken e Musgo; A/START confirma
- saida: `CLEAR_VDP` entrega a cena a `gRoom=10`
- evidencia exigida: selecao visivel e retorno a partir da tela pos-partida

### Cena 3 - `room_after_match` (pos-partida)

- owner: ramo `gRoom==11` de `src/main.c`
- entrada: duas vitorias, tempo minimo de resultado e derrotado em 570; a duracao da animacao vencedora nao pode antecipar o pouso
- opcoes: A = revanche com mesmos lutadores; START = seletor
- proibicao: nenhum FSM/fisica da luta anterior roda depois da troca de owner
- evidencia exigida: tela do vencedor + uma captura de cada rota de saida
- tipografia: celulas 16x16 extraidas do atlas solicitado, PAL1/prioridade alta, painel BG_A nas linhas 5..10. Mapa em RAM enviado por DMA_QUEUE_COPY; PAL2/PAL3 pertencem aos lutadores.

### Cena 1 - `room_fight_arena` (combate 1v1)

- origem: engine upstream (`src/fsm.c`, `src/player.c`, `src/physics.c`, `src/collision.c`, `src/hud.c`)
- conteudo: arena Showdown com Ryo/Ken/Musgo selecionaveis, HUD WINDOW, mensagens BG_A e logica FSM de golpes
- sprites por scanline: governados pelo sprite engine do SGDK 2.11 (SPR_initEx); medicao dedicada de scanline NAO foi feita nesta porta (fora do escopo; `validado_budget: nao`)
- evidencia: `out/emulator_evidence/blastem-linux-20260910T192043Z-1434440/screenshot.png`

## Contrato de evidencia desta porta

- build: `out/logs/linux_wine_build_report.json` (wine_bridge_status=buildado)
- boot: sessoes BlastEm em `out/emulator_evidence/` com screenshot + save.sram + log
- audio: SFX GPL importados e `FUNCAO_PLAY_SND` ligado; prova de captura/escuta permanece separada
- hud: barras P1/P2 e relogio usam WINDOW; KO e sombra permanecem sprites

## Residencia estatica da revisao visual

- Stage 768 + HUD 249 + tile inicial 1 = primeiro livre 1018.
- Regiao automatica de sprites: 420 tiles, inicio 1020 no layout observado.
- Sobra entre recursos estaticos e sprites: 2 tiles. Nao e folga de DMA/SAT.
- Degrau seguinte: stage 832 leva a 1082, sobrepoe 62 tiles e foi rejeitado.
- `FUNCAO_INIT` consulta `TILE_SPRITE_INDEX` antes da carga e falha explicitamente se houver sobreposicao.
- Queda Musgo 120x120 (2 frames), derrota 128x64 (1), vitoria 88x128 (1); poses de estado, nao ciclo de vitoria multiframes.
- Proximos testes obrigatorios: pior DMA, uso dinamico/fragmentacao de sprites, SAT/scanline e PAL. Build/contagem nao os substituem.

## Provas adicionais — 2026-09-13

PAL basico exercitado na mesma ROM 532d4453: P2 vencedor e START, em
`visual_ko_20260913T114702Z`. NTSC simetrico em `visual_ko_20260913T114321Z`.
DRAW e vencedor por tempo com vida desigual vistos, com reset; contrato C
coberto por 9.216 pares. Referencia `doc/curation/2026_09_13/qa_continuation_closeout.md`.
Isto nao promove residencia estatica a pior budget nem titulo do emulador a FPS do loop.
