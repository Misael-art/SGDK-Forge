# Especificação de cenas — BLAZE_ENGINE Beat 'em Up SGDK 2.11

## `room_8_credits`

- Papel: créditos de boot preservados da fonte.
- Planos: `BG_B` base e `BG_A` overlay.
- Owner: runtime legado em `src/main.c`.
- Evidência: boot em BlastEm e screenshot dedicada.
- Fallback: tela vazia apenas como diagnóstico; não é entrega.

## `room_9_main_screen`

- Papel: tela principal/logo.
- Planos: `BG_B`.
- Owner: runtime legado em `src/main.c`.
- Evidência: entrada por botão confirmada pela ROM.
- Fallback: boot seed documentado.

## `room_10_player_select`

- Papel: seleção de personagem e teste de sprites/PCM.
- Planos: `BG_B` e sprites.
- Owner: runtime legado em `src/main.c`.
- Evidência: navegação P1/P2 e seleção observada.
- Fallback: seleção P1 sem segundo jogador.

## `room_11_gameplay` — beat 'em up

- Papel: gameplay de beat 'em up/brawler de progressão lateral disponível na fonte.
- Planos: BGs segmentados e sprites.
- Owner: runtime legado em `src/main.c`.
- Evidência: input, movimento, colisão, animação, SFX e FPS observados.
- Fallback: smoke técnico sem claim de game feel AAA.

## Dependências externas não reproduzíveis

As URLs do Discord fornecidas pelo usuário são registradas em `rascunho/discord_references.md`. Nesta sessão os canais retornaram apenas o shell público do Discord e a API retornou `401 Unauthorized`; nenhuma correção específica desses posts é afirmada ou aplicada.
